# arquivo: copilot_ollama.py
# Ollama API proxy server using GitHub Copilot as backend
# Similar to ollama_local_proxy.py but routes requests to GitHub Copilot instead of Gemini
import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta

import uvicorn
from copilot_api import CopilotAPI
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("copilot_ollama_proxy.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Copilot API instance
copilot_api = None


# Middleware para logar todas as requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log da requisição
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"📥 {request.method} {request.url.path} - IP: {client_ip}")

    # Capturar corpo da requisição
    request_body = await request.body()
    logger.info(
        f"📝 Corpo da requisição: {request_body.decode('utf-8', errors='ignore')}"
    )

    # Processar a requisição
    response = await call_next(request)

    # Capturar corpo da resposta
    response_body = "N/A"
    content_type = response.headers.get("content-type", "")

    # Se for uma JSONResponse, tentamos capturar o conteúdo
    if "application/json" in content_type:
        response_body = "JSON Response"
    elif "text/event-stream" in content_type:
        response_body = "Stream Response"
    else:
        response_body = "Other Response"

    # Log da resposta
    process_time = time.time() - start_time
    logger.info(
        f"📤 {request.method} {request.url.path} - Status: {response.status_code} - Tempo: {process_time:.3f}s"
    )
    logger.info(
        f"📝 Corpo da resposta: {response_body[:50000]}{'...' if len(response_body) > 50000 else ''}"
    )

    return response


MODEL_NAME = "github-copilot"
MODEL_TAG = "gpt-4.1"
MODEL_FULL_NAME = f"{MODEL_NAME}:{MODEL_TAG}"
DIGEST = "copilot-" + str(uuid.uuid4()).replace("-", "")[:32]
# Set MODIFIED_AT to current UTC time in ISO format with nanoseconds
MODIFIED_AT = datetime.utcnow().isoformat() + "Z"
SIZE = 1500000000  # Approximate size for Copilot model
PARAMETER_SIZE = "175B"  # GPT-4 parameter size
QUANTIZATION_LEVEL = "FP16"


def now_timestamp():
    return datetime.utcnow().isoformat() + "Z"


def initialize_copilot():
    """Initialize the Copilot API client."""
    global copilot_api
    if copilot_api is None:
        try:
            logger.info("🤖 Inicializando cliente Copilot API")
            copilot_api = CopilotAPI()
            logger.info("✅ Cliente Copilot inicializado com sucesso")

            # Test the connection with a simple call
            logger.info("🧪 Testando conexão com Copilot...")
            test_result = copilot_api.chat("Hello", [])
            logger.info("✅ Teste de conexão Copilot bem-sucedido")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Erro ao inicializar Copilot: {error_msg}")

            if "401" in error_msg or "unauthorized" in error_msg.lower():
                logger.error(
                    "❌ Erro de autenticação do GitHub Copilot. Verifique suas credenciais."
                )
            elif "FileNotFoundError" in error_msg:
                logger.error("❌ Arquivos de configuração do Copilot não encontrados.")

            copilot_api = None
    return copilot_api


def call_copilot(prompt: str, references: list = None):
    """Call the Copilot API and return the response."""
    start_time = time.time()
    logger.info("🤖 Iniciando chamada para Copilot")
    logger.debug(
        f"📝 Prompt enviado: {prompt[:200]}{'...' if len(prompt) > 200 else ''}"
    )

    try:
        client = initialize_copilot()
        if client is None:
            logger.error("❌ Cliente Copilot não disponível")
            return {
                "text": "I'm a Copilot Ollama proxy server, but GitHub Copilot is currently not available. Please check your authentication credentials."
            }

        # Use references if provided, otherwise empty list
        refs = references or []

        # Call Copilot API
        result = client.chat(prompt, refs)
        execution_time = time.time() - start_time

        logger.info(f"✅ Copilot respondeu em {execution_time:.2f}s")

        # Extract the response text from Copilot API response
        if isinstance(result, dict):
            # Check for the correct Copilot API format: {'message': {'content': '...'}}
            if "message" in result and isinstance(result["message"], dict):
                content = result["message"].get("content", "")
                if content and isinstance(content, str) and content.strip():
                    logger.debug(
                        f"✅ Resposta recebida: {content[:200]}{'...' if len(content) > 200 else ''}"
                    )
                    return {"text": content.strip()}

            # Fallback: try other possible response fields
            response_text = (
                result.get("content")
                or result.get("text")
                or result.get("response")
                or None
            )

            # If we got a dict as response_text, convert to string
            if isinstance(response_text, dict):
                logger.debug(f"🔧 Converting dict response to string: {response_text}")
                response_text = str(response_text)
            elif response_text is None:
                logger.debug(f"🔧 No text field found, using full result: {result}")
                response_text = str(result)

            # Ensure response_text is a string before calling strip()
            if isinstance(response_text, str) and response_text.strip():
                logger.debug(
                    f"✅ Resposta recebida (fallback): {response_text[:200]}{'...' if len(response_text) > 200 else ''}"
                )
                return {"text": response_text.strip()}
            else:
                logger.warning("⚠️ Resposta vazia do Copilot")
                return {
                    "text": "I received an empty response from GitHub Copilot. Please try again."
                }
        else:
            logger.warning(f"⚠️ Formato de resposta inesperado: {type(result)}")
            return {"text": str(result) if result else "Empty response."}

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        logger.error(
            f"❌ Erro na chamada Copilot após {execution_time:.2f}s: {error_msg}"
        )

        # Provide user-friendly error messages based on the error type
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            fallback_msg = "GitHub Copilot authentication failed. Please check your credentials and try again. For now, I'm running in demo mode."
        elif "400" in error_msg:
            fallback_msg = "GitHub Copilot request was invalid. Please try rephrasing your question."
        elif "timeout" in error_msg.lower():
            fallback_msg = "GitHub Copilot request timed out. Please try again."
        else:
            fallback_msg = f"GitHub Copilot is currently unavailable: {error_msg}"

        return {"text": fallback_msg}


def get_model_details():
    """Return standardized model details structure."""
    return {
        "parent_model": "",
        "format": "transformers",
        "family": "gpt",
        "families": ["gpt"],
        "parameter_size": PARAMETER_SIZE,
        "quantization_level": QUANTIZATION_LEVEL,
    }


def get_model_info(model_name=None):
    """Return detailed model information for any model name."""
    if not model_name:
        model_name = MODEL_FULL_NAME

    return {
        "name": model_name,
        "model": model_name,
        "modified_at": MODIFIED_AT,
        "size": SIZE,
        "digest": DIGEST,
        "details": get_model_details(),
        # Additional fields that some clients might expect
        "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        "size_vram": SIZE,
    }


def is_valid_model(model_name: str) -> bool:
    """Check if the model name is valid/supported.

    For maximum compatibility, we accept any model name format.
    """
    if not model_name:
        return False

    # Accept any model name for maximum compatibility
    # This proxy will handle any model request and route it to Copilot
    return True


def normalize_model_name(model_name: str) -> str:
    """Normalize model name to a consistent form."""
    if not model_name:
        return MODEL_FULL_NAME

    # For logging and consistency, we can normalize but still accept any name
    # If no tag specified, assume latest
    if ":" not in model_name:
        normalized = f"{model_name}:latest"
    else:
        normalized = model_name

    return normalized


# Root endpoint for basic server info
@app.get("/")
async def root():
    logger.info("🏠 Acesso ao endpoint raiz")
    return JSONResponse(
        content={
            "status": "copilot ollama proxy server is running",
            "version": "0.1.0",
            "models": [MODEL_FULL_NAME],
            "backend": "github-copilot",
        }
    )


@app.get("/api/version")
async def version():
    """Get server version information."""
    return JSONResponse(
        content={"version": "0.1.9", "proxy": True, "backend": "github-copilot"}
    )


# Endpoints
@app.get("/api/tags")
async def list_models():
    """List models that are available locally."""
    logger.info("📋 GET /api/tags - Listando modelos disponíveis")
    # Return a generic model that can handle any requests
    return JSONResponse(content={"models": [get_model_info()]})


@app.get("/api/models")
async def list_models_alias():
    """Alias for /api/tags for backward compatibility."""
    return await list_models()


@app.get("/api/show")
async def show_model_get(name: str = Query(MODEL_FULL_NAME)):
    """Show model information via GET request."""
    logger.info(f"ℹ️ GET /api/show - Modelo: {name}")

    if not is_valid_model(name):
        raise HTTPException(status_code=404, detail=f"Model '{name}' not found")

    normalized_name = normalize_model_name(name)
    logger.debug(f"🔧 Nome normalizado: {normalized_name}")

    return JSONResponse(
        content={
            "license": "GitHub Copilot Terms of Service",
            "modelfile": f"""# Modelfile generated by "ollama show"
# To build a new Modelfile based on this, replace FROM with:
# FROM {normalized_name}

FROM github-copilot:gpt-4.1
TEMPLATE "{{{{ .System }}}}\\n\\n{{{{ .Prompt }}}}"
PARAMETER temperature 0.7
PARAMETER max_tokens 4096""",
            "parameters": """temperature                    0.7
max_tokens                     4096""",
            "template": "{{ .System }}\\n\\n{{ .Prompt }}",
            "details": get_model_details(),
            "model_info": {
                "general.architecture": "transformer",
                "general.parameter_count": 175000000000,
                "general.quantization_version": 2,
                "tokenizer.model": "gpt-4",
            },
        }
    )


@app.post("/api/show")
async def show_model_post(request: Request):
    """Show model information via POST request."""
    body = await request.json()
    name = body.get("name", MODEL_FULL_NAME)
    return await show_model_get(name=name)


@app.post("/api/chat")
async def chat(request: Request):
    """Generate a chat completion."""
    body = await request.json()
    model = body.get("model", MODEL_FULL_NAME)
    messages = body.get("messages", [])
    stream = body.get("stream", True)
    _options = body.get("options", {})
    _keep_alive = body.get("keep_alive", "5m")

    logger.info(
        f"💬 POST /api/chat - Modelo: {model}, Stream: {stream}, Mensagens: {len(messages)}"
    )
    logger.debug(
        f"📨 Mensagens recebidas: {json.dumps(messages, ensure_ascii=False)[:500]}{'...' if len(str(messages)) > 500 else ''}"
    )

    # Validate model
    if not is_valid_model(model):
        raise HTTPException(status_code=404, detail=f"Model '{model}' not found")

    # Normalize the model name for consistency in responses
    normalized_model = normalize_model_name(model)
    logger.debug(f"🔧 Modelo normalizado: {model} -> {normalized_model}")

    # Handle empty messages (model loading)
    if not messages:
        created_at = now_timestamp()
        response_data = {
            "model": normalized_model,
            "created_at": created_at,
            "message": {"role": "assistant", "content": ""},
            "done": True,
        }
        return JSONResponse(content=response_data)

    # Build prompt from messages
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")

    prompt = "\n\n".join(prompt_parts)
    logger.debug(
        f"🔧 Prompt construído: {prompt[:300]}{'...' if len(prompt) > 300 else ''}"
    )

    # Call Copilot
    start_time = time.time()
    copilot_resp = call_copilot(prompt)
    end_time = time.time()

    # Handle errors
    if "error" in copilot_resp:
        raise HTTPException(status_code=500, detail=copilot_resp["error"])

    response_content = copilot_resp.get("text", str(copilot_resp))
    logger.info(
        f"✅ Resposta gerada em {end_time - start_time:.2f}s, {len(response_content)} caracteres"
    )

    # Calculate timing
    total_duration = int((end_time - start_time) * 1_000_000_000)  # nanoseconds
    created_at = now_timestamp()

    if stream:

        async def generate_stream():
            # Simulate streaming by yielding chunks
            words = response_content.split()
            for i, word in enumerate(words):
                chunk_data = {
                    "model": normalized_model,
                    "created_at": created_at,
                    "message": {
                        "role": "assistant",
                        "content": word + (" " if i < len(words) - 1 else ""),
                    },
                    "done": False,
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                await asyncio.sleep(0.01)  # Small delay for realistic streaming

            # Final chunk
            final_data = {
                "model": normalized_model,
                "created_at": created_at,
                "message": {"role": "assistant", "content": ""},
                "done": True,
                "total_duration": total_duration,
                "load_duration": 0,
                "prompt_eval_count": len(prompt.split()),
                "prompt_eval_duration": total_duration // 2,
                "eval_count": len(response_content.split()),
                "eval_duration": total_duration // 2,
            }
            yield f"data: {json.dumps(final_data)}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Transfer-Encoding": "chunked"},
        )
    else:
        response_data = {
            "model": normalized_model,
            "created_at": created_at,
            "message": {"role": "assistant", "content": response_content},
            "done": True,
            "total_duration": total_duration,
            "load_duration": 0,
            "prompt_eval_count": len(prompt.split()),
            "prompt_eval_duration": total_duration // 2,
            "eval_count": len(response_content.split()),
            "eval_duration": total_duration // 2,
        }
        return JSONResponse(content=response_data)


@app.post("/api/generate")
async def generate(request: Request):
    """Generate a completion."""
    body = await request.json()
    model = body.get("model", MODEL_FULL_NAME)
    prompt = body.get("prompt", "")
    stream = body.get("stream", True)
    suffix = body.get("suffix", "")
    format_type = body.get("format", None)
    _options = body.get("options", {})
    system = body.get("system", "")
    _template = body.get("template", "")
    context = body.get("context", [])
    raw = body.get("raw", False)
    _keep_alive = body.get("keep_alive", "5m")
    _images = body.get("images", [])

    logger.info(
        f"🤖 POST /api/generate - Modelo: {model}, Stream: {stream}, Formato: {format_type}"
    )
    logger.debug(f"📝 Prompt: {prompt[:200]}{'...' if len(prompt) > 200 else ''}")
    logger.debug(f"🔧 Sistema: {system[:100]}{'...' if len(system) > 100 else ''}")

    # Validate model
    if not is_valid_model(model):
        raise HTTPException(status_code=404, detail=f"Model '{model}' not found")

    # Handle model loading (empty prompt)
    if not prompt.strip():
        created_at = now_timestamp()
        response_data = {
            "model": model,
            "created_at": created_at,
            "response": "",
            "done": True,
        }
        return JSONResponse(content=response_data)

    # Build complete prompt
    full_prompt = prompt
    if system and not raw:
        full_prompt = f"System: {system}\n\nUser: {prompt}"
    if suffix:
        full_prompt += f"\n\n{suffix}"

    logger.debug(
        f"🔧 Prompt completo: {full_prompt[:300]}{'...' if len(full_prompt) > 300 else ''}"
    )

    # Call Copilot
    start_time = time.time()
    copilot_resp = call_copilot(full_prompt)
    end_time = time.time()

    # Handle errors
    if "error" in copilot_resp:
        raise HTTPException(status_code=500, detail=copilot_resp["error"])

    response_content = copilot_resp.get("text", str(copilot_resp))
    logger.info(
        f"✅ Resposta gerada em {end_time - start_time:.2f}s, {len(response_content)} caracteres"
    )

    # JSON format handling
    if format_type == "json":
        try:
            # Try to parse as JSON to validate
            json.loads(response_content)
        except json.JSONDecodeError:
            # If not valid JSON, wrap in JSON structure
            response_content = json.dumps({"response": response_content})

    # Calculate timing
    total_duration = int((end_time - start_time) * 1_000_000_000)  # nanoseconds
    created_at = now_timestamp()

    if stream:

        async def generate_stream():
            # Simulate streaming by yielding chunks
            words = response_content.split()
            for i, word in enumerate(words):
                chunk_data = {
                    "model": model,
                    "created_at": created_at,
                    "response": word + (" " if i < len(words) - 1 else ""),
                    "done": False,
                }
                yield f"{json.dumps(chunk_data)}\n"
                await asyncio.sleep(0.01)

            # Final chunk
            final_data = {
                "model": model,
                "created_at": created_at,
                "response": "",
                "done": True,
                "context": context,
                "total_duration": total_duration,
                "load_duration": 0,
                "prompt_eval_count": len(full_prompt.split()),
                "prompt_eval_duration": total_duration // 2,
                "eval_count": len(response_content.split()),
                "eval_duration": total_duration // 2,
            }
            yield f"{json.dumps(final_data)}\n"

        return StreamingResponse(
            generate_stream(),
            media_type="application/x-ndjson",
            headers={"Transfer-Encoding": "chunked"},
        )
    else:
        response_data = {
            "model": model,
            "created_at": created_at,
            "response": response_content,
            "done": True,
            "context": context,
            "total_duration": total_duration,
            "load_duration": 0,
            "prompt_eval_count": len(full_prompt.split()),
            "prompt_eval_duration": total_duration // 2,
            "eval_count": len(response_content.split()),
            "eval_duration": total_duration // 2,
        }
        return JSONResponse(content=response_data)


@app.get("/api/ps")
async def list_running_models():
    """List models that are currently loaded into memory."""
    logger.info("🏃 GET /api/ps - Listando modelos em execução")
    return JSONResponse(content={"models": [get_model_info()]})


@app.post("/api/embed")
async def generate_embeddings(request: Request):
    """Generate embeddings from a model."""
    body = await request.json()
    model = body.get("model", MODEL_FULL_NAME)
    input_text = body.get("input", "")

    logger.info(f"🔢 POST /api/embed - Modelo: {model}")

    # Copilot doesn't support embeddings, return mock data
    logger.warning("⚠️ Copilot não suporta embeddings, retornando dados simulados")

    # Generate mock embedding (768 dimensions, typical for many models)
    import random

    embedding = [random.uniform(-1, 1) for _ in range(768)]

    return JSONResponse(content={"model": model, "embeddings": [embedding]})


@app.post("/api/copy")
async def copy_model(request: Request):
    """Copy a model."""
    body = await request.json()
    source = body.get("source", "")
    destination = body.get("destination", "")

    logger.info(f"📋 POST /api/copy - De: {source} Para: {destination}")

    # Since we're using Copilot, we just acknowledge the copy
    return JSONResponse(content={"status": "success"})


@app.delete("/api/delete")
async def delete_model(request: Request):
    """Delete a model."""
    body = await request.json()
    name = body.get("name", "")

    logger.info(f"🗑️ DELETE /api/delete - Modelo: {name}")

    # Since we're using Copilot, we just acknowledge the deletion
    return JSONResponse(content={"status": "success"})


@app.post("/api/pull")
async def pull_model(request: Request):
    """Pull a model."""
    body = await request.json()
    name = body.get("name", "")
    stream = body.get("stream", True)

    logger.info(f"⬇️ POST /api/pull - Modelo: {name}, Stream: {stream}")

    if stream:

        async def pull_stream():
            # Simulate pull progress
            for progress in [0, 25, 50, 75, 100]:
                data = {
                    "status": f"pulling {name}",
                    "digest": DIGEST,
                    "total": SIZE,
                    "completed": int(SIZE * progress / 100),
                }
                yield f"{json.dumps(data)}\n"
                await asyncio.sleep(0.1)

            # Final status
            final_data = {"status": "success"}
            yield f"{json.dumps(final_data)}\n"

        return StreamingResponse(pull_stream(), media_type="application/x-ndjson")
    else:
        return JSONResponse(content={"status": "success"})


@app.post("/api/push")
async def push_model(request: Request):
    """Push a model."""
    body = await request.json()
    name = body.get("name", "")
    stream = body.get("stream", True)

    logger.info(f"⬆️ POST /api/push - Modelo: {name}, Stream: {stream}")

    if stream:

        async def push_stream():
            # Simulate push progress
            for progress in [0, 25, 50, 75, 100]:
                data = {
                    "status": f"pushing {name}",
                    "digest": DIGEST,
                    "total": SIZE,
                    "completed": int(SIZE * progress / 100),
                }
                yield f"{json.dumps(data)}\n"
                await asyncio.sleep(0.1)

            # Final status
            final_data = {"status": "success"}
            yield f"{json.dumps(final_data)}\n"

        return StreamingResponse(push_stream(), media_type="application/x-ndjson")
    else:
        return JSONResponse(content={"status": "success"})


# Legacy embedding endpoint for backward compatibility
@app.post("/api/embeddings")
async def generate_embedding_legacy(request: Request):
    """Generate embedding (legacy endpoint)."""
    return await generate_embeddings(request)


@app.post("/v1/chat/completions")
async def openai_chat_completions(request: Request):
    """OpenAI-compatible chat completions endpoint."""
    body = await request.json()
    model = body.get("model", MODEL_FULL_NAME)
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    temperature = body.get("temperature", 0.7)
    max_tokens = body.get("max_tokens", 4096)

    logger.info(f"🔗 POST /v1/chat/completions - Modelo: {model}, OpenAI compatible")

    # Build prompt from messages
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")

    prompt = "\n\n".join(prompt_parts)

    # Call Copilot
    start_time = time.time()
    copilot_resp = call_copilot(prompt)
    end_time = time.time()

    if "error" in copilot_resp:
        raise HTTPException(status_code=500, detail=copilot_resp["error"])

    response_content = copilot_resp.get("text", str(copilot_resp))

    # OpenAI format response
    response_data = {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response_content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(response_content.split()),
            "total_tokens": len(prompt.split()) + len(response_content.split()),
        },
    }

    return JSONResponse(content=response_data)


@app.get("/v1/models")
async def openai_list_models():
    """OpenAI-compatible models list."""
    logger.info("📋 GET /v1/models - OpenAI compatible")

    return JSONResponse(
        content={
            "object": "list",
            "data": [
                {
                    "id": MODEL_FULL_NAME,
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "github-copilot",
                    "permission": [],
                    "root": MODEL_FULL_NAME,
                    "parent": None,
                }
            ],
        }
    )


if __name__ == "__main__":
    print("🚀 Starting Copilot Ollama API proxy server on port 11435")
    print(f"📦 Available model: {MODEL_FULL_NAME}")
    print("🔗 Endpoints:")
    print("  - GET  /api/tags          - List available models")
    print("  - POST /api/show          - Show model information")
    print("  - POST /api/generate      - Generate completion")
    print("  - POST /api/chat          - Generate chat completion")
    print("  - GET  /api/ps            - List running models")
    print("  - POST /api/embed         - Generate embeddings")
    print("  - POST /api/copy          - Copy model")
    print("  - DELETE /api/delete      - Delete model")
    print("  - POST /api/pull          - Pull model")
    print("  - POST /api/push          - Push model")
    print("  - POST /api/embeddings    - Generate embedding (legacy)")
    print("  - POST /v1/chat/completions - OpenAI-compatible chat completions")
    print("  - GET  /v1/models         - OpenAI-compatible models list")
    print("📝 Logs serão salvos em: copilot_ollama_proxy.log")
    print("🔧 Backend: GitHub Copilot API")

    logger.info("🚀 Iniciando servidor Copilot Ollama API proxy na porta 11435")
    logger.info(f"📦 Modelo disponível: {MODEL_FULL_NAME}")
    logger.info("🔧 Backend: GitHub Copilot API")

    # Initialize Copilot client on startup
    initialize_copilot()

    uvicorn.run(app, host="0.0.0.0", port=11435)
