# arquivo: ollama_local_proxy.py
import asyncio
import hashlib
import json
import logging
import struct
import subprocess
import time
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.responses import Response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ollama_proxy.log"), logging.StreamHandler()],
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
        try:
            # Para FastAPI/Starlette, o corpo está no body_iterator
            if hasattr(response, "body_iterator"):
                # Coletar todos os chunks do body_iterator
                chunks = []
                async for chunk in response.body_iterator:
                    chunks.append(chunk)

                # Decodificar o conteúdo
                full_content = b"".join(chunks)
                response_body = full_content.decode("utf-8", errors="ignore")

                # Recriar o response com o mesmo conteúdo
                new_response = Response(
                    content=full_content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
                response = new_response
            elif hasattr(response, "body"):
                response_body = (
                    response.body.decode("utf-8", errors="ignore")
                    if isinstance(response.body, bytes)
                    else str(response.body)
                )
        except Exception as e:
            response_body = f"N/A (erro ao capturar: {str(e)})"
    elif "text/event-stream" in content_type:
        response_body = "N/A (streaming response)"
    else:
        response_body = "N/A (tipo não suportado)"

    # Log da resposta
    process_time = time.time() - start_time
    logger.info(
        f"📤 {request.method} {request.url.path} - Status: {response.status_code} - Tempo: {process_time:.3f}s"
    )
    logger.info(
        f"📝 Corpo da resposta: {response_body[:50000]}{'...' if len(response_body) > 50000 else ''}"
    )

    return response


MODEL_NAME = "codellama"  # Use codellama for better compatibility
MODEL_TAG = "7b-instruct-q2_K"
MODEL_FULL_NAME = f"{MODEL_NAME}:{MODEL_TAG}"
DIGEST = "28ee56afb6a5dada9cd8d09d89b5217499ffe9364658aa2d1eaf9f97bdfa0cba"
# Set MODIFIED_AT to current UTC time in ISO format with nanoseconds
MODIFIED_AT = datetime.utcnow().isoformat() + "Z"
SIZE = 2826028934
PARAMETER_SIZE = "7B"
QUANTIZATION_LEVEL = "Q2_K"


def now_timestamp():
    return datetime.utcnow().isoformat() + "Z"


def call_gemini(prompt: str):
    """Call the external Gemini CLI tool and return the response."""
    start_time = time.time()
    logger.info("🤖 Iniciando chamada para Gemini")
    logger.debug(
        f"📝 Prompt enviado: {prompt[:200]}{'...' if len(prompt) > 200 else ''}"
    )

    try:
        # Use the correct gemini CLI syntax without --json flag
        cmd = ["gemini", "--prompt", prompt]
        logger.debug(f"🔧 Comando executado: {' '.join(cmd[:2])} [prompt truncado]")

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        execution_time = time.time() - start_time

        logger.info(f"✅ Gemini respondeu em {execution_time:.2f}s")

        # Since gemini CLI returns plain text, not JSON, return as text
        response_text = result.stdout.strip()
        if response_text:
            logger.debug("📤 Resposta recebida com sucesso")
            return {"text": response_text}
        else:
            logger.warning("⚠️ Resposta vazia do Gemini")
            return {"text": "Desculpe, não consegui gerar uma resposta."}

    except subprocess.CalledProcessError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Erro na chamada Gemini após {execution_time:.2f}s: {e}")
        logger.error(f"🔍 Stderr: {e.stderr}")
        return {"error": e.stderr or str(e)}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            f"❌ Erro inesperado na chamada Gemini após {execution_time:.2f}s: {e}"
        )
        return {"error": str(e)}


def get_model_details():
    """Return standardized model details structure."""
    return {
        "parent_model": "",
        "format": "gguf",
        "family": "llama",
        "families": None,  # Match the log format exactly
        "parameter_size": PARAMETER_SIZE,
        "quantization_level": QUANTIZATION_LEVEL,
    }


def get_model_info():
    """Return detailed model information."""
    return {
        "name": MODEL_FULL_NAME,  # Use full name with tag
        "model": MODEL_FULL_NAME,  # Some clients expect both 'name' and 'model'
        "modified_at": MODIFIED_AT,
        "size": SIZE,
        "digest": DIGEST,
        "details": get_model_details(),
        # Additional fields that some clients might expect
        "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        "size_vram": SIZE,
    }


def is_valid_model(model_name: str) -> bool:
    """Check if the model name is valid/supported."""
    if not model_name:
        return False

    # Support various formats
    valid_names = [
        MODEL_NAME,  # "codellama"
        MODEL_FULL_NAME,  # "codellama:7b-instruct-q2_K"
        f"{MODEL_NAME}:latest",
        "codellama:7b-instruct-q2_K",
        "gemini-proxy",  # Legacy support
        "gemini-proxy:latest",
    ]

    return model_name in valid_names


def normalize_model_name(model_name: str) -> str:
    """Normalize model name to the canonical form."""
    if model_name in [MODEL_NAME, "codellama"]:
        return MODEL_FULL_NAME
    if model_name.endswith(f":{MODEL_TAG}"):
        return model_name
    if model_name == "gemini-proxy" or model_name == "gemini-proxy:latest":
        return MODEL_FULL_NAME  # Legacy support
    return f"{model_name}:{MODEL_TAG}" if ":" not in model_name else model_name


# Root endpoint for basic server info
@app.get("/")
async def root():
    logger.info("🏠 Acesso ao endpoint raiz")
    return JSONResponse(
        content={
            "status": "ollama proxy server is running",
            "version": "0.1.0",
            "models": [MODEL_FULL_NAME],
        }
    )


@app.get("/api/version")
async def version():
    """Get server version information."""
    return JSONResponse(
        content={"version": "0.1.9", "proxy": True, "backend": "gemini"}
    )


# Endpoints


@app.get("/api/tags")
async def list_models():
    """List models that are available locally."""
    logger.info("📋 GET /api/tags - Listando modelos disponíveis")
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
        logger.warning(f"⚠️ Modelo não encontrado: {name}")
        raise HTTPException(status_code=404, detail=f"Model '{name}' not found")

    normalized_name = normalize_model_name(name)
    logger.debug(f"🔧 Nome normalizado: {normalized_name}")

    return JSONResponse(
        content={
            "license": """LLAMA 2 COMMUNITY LICENSE AGREEMENT\t
Llama 2 Version Release Date: July 18, 2023

"Agreement" means the terms and conditions for use, reproduction, distribution and 
modification of the Llama Materials set forth herein.

"Documentation" means the specifications, manuals and documentation 
accompanying Llama 2 distributed by Meta at ai.meta.com/resources/models-and-
libraries/llama-downloads/.

"Licensee" or "you" means you, or your employer or any other person or entity (if 
you are entering into this Agreement on such person or entity's behalf), of the age 
required under applicable laws, rules or regulations to provide legal consent and that 
has legal authority to bind your employer or such other person or entity if you are 
entering in this Agreement on their behalf.

"Llama 2" means the foundational large language models and software and 
algorithms, including machine-learning model code, trained model weights, 
inference-enabling code, training-enabling code, fine-tuning enabling code and other 
elements of the foregoing distributed by Meta at ai.meta.com/resources/models-and-
libraries/llama-downloads/.

"Llama Materials" means, collectively, Meta's proprietary Llama 2 and 
Documentation (and any portion thereof) made available under this Agreement.

"Meta" or "we" means Meta Platforms Ireland Limited (if you are located in or, if you 
are an entity, your principal place of business is in the EEA or Switzerland) and Meta 
Platforms, Inc. (if you are located outside of the EEA or Switzerland). 

By clicking "I Accept" below or by using or distributing any portion or element of the 
Llama Materials, you agree to be bound by this Agreement.""",
            "modelfile": f"""# Modelfile generated by "ollama show"
# To build a new Modelfile based on this, replace FROM with:
# FROM {normalized_name}

FROM /root/.ollama/models/blobs/sha256-28ee56afb6a5dada9cd8d09d89b5217499ffe9364658aa2d1eaf9f97bdfa0cba
TEMPLATE "[INST] <<SYS>>{{{{ .System }}}}<</SYS>>\\n\\n{{{{ .Prompt }}}} [/INST]\\n"
PARAMETER stop [INST]
PARAMETER stop [/INST]
PARAMETER stop <<SYS>>
PARAMETER stop <</SYS>>
PARAMETER rope_frequency_base 1e+06""",
            "parameters": """rope_frequency_base            1e+06
stop                           "[INST]"
stop                           "[/INST]"
stop                           "<<SYS>>"
stop                           "<</SYS>>\"""",
            "template": "[INST] <<SYS>>{{ .System }}<</SYS>>\\n\\n{{ .Prompt }} [/INST]\\n",
            "details": get_model_details(),
            "model_info": {
                "general.architecture": "llama",
                "general.file_type": 10,
                "general.parameter_count": 6738546688,
                "general.quantization_version": 2,
                "llama.attention.head_count": 32,
                "llama.attention.head_count_kv": 32,
                "llama.attention.layer_norm_rms_epsilon": 1e-05,
                "llama.block_count": 32,
                "llama.context_length": 16384,
                "llama.embedding_length": 4096,
                "llama.feed_forward_length": 11008,
                "llama.rope.dimension_count": 128,
                "llama.rope.freq_base": 1000000,
                "tokenizer.ggml.bos_token_id": 1,
                "tokenizer.ggml.eos_token_id": 2,
                "tokenizer.ggml.model": "llama",
                "tokenizer.ggml.scores": None,
                "tokenizer.ggml.token_type": None,
                "tokenizer.ggml.tokens": None,
                "tokenizer.ggml.unknown_token_id": 0,
            },
            "tensors": [
                {"name": "token_embd.weight", "type": "Q2_K", "shape": [4096, 32016]},
                {"name": "blk.0.attn_norm.weight", "type": "F32", "shape": [4096]},
                {"name": "output_norm.weight", "type": "F32", "shape": [4096]},
            ],
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
    _options = body.get("options", {})  # Reserved for future model options
    _keep_alive = body.get("keep_alive", "5m")  # Reserved for memory management

    logger.info(
        f"💬 POST /api/chat - Modelo: {model}, Stream: {stream}, Mensagens: {len(messages)}"
    )
    logger.debug(
        f"📨 Mensagens recebidas: {json.dumps(messages, ensure_ascii=False)[:500]}{'...' if len(str(messages)) > 500 else ''}"
    )

    # Validate model
    if not is_valid_model(model):
        logger.warning(f"⚠️ Modelo inválido solicitado: {model}")
        raise HTTPException(status_code=404, detail=f"Model '{model}' not found")

    # Handle empty messages (model loading)
    if not messages:
        logger.info("📭 Mensagens vazias - retornando resposta de carregamento")
        return JSONResponse(
            content={
                "model": model,
                "created_at": now_timestamp(),
                "message": {"role": "assistant", "content": ""},
                "done_reason": "load",
                "done": True,
            }
        )

    # Build prompt from messages
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        prompt_parts.append(f"{role}: {content}")

    prompt = "\n\n".join(prompt_parts)
    logger.debug(
        f"🔧 Prompt construído: {prompt[:300]}{'...' if len(prompt) > 300 else ''}"
    )

    # Call Gemini
    start_time = time.time()
    gemini_resp = call_gemini(prompt)
    end_time = time.time()

    # Handle errors
    if "error" in gemini_resp:
        logger.error(f"❌ Erro no Gemini: {gemini_resp['error']}")
        raise HTTPException(status_code=500, detail=gemini_resp["error"])

    response_content = gemini_resp.get("text", str(gemini_resp))
    logger.info(
        f"✅ Resposta gerada em {end_time - start_time:.2f}s, {len(response_content)} caracteres"
    )

    # Calculate timing
    total_duration = int((end_time - start_time) * 1_000_000_000)  # nanoseconds

    if stream:
        logger.info("🌊 Iniciando resposta em streaming")

        async def generate_stream():
            # First chunk with partial content
            yield f'data: {json.dumps({
                "model": model,
                "created_at": now_timestamp(),
                "message": {
                    "role": "assistant",
                    "content": response_content[:10] if len(response_content) > 10 else response_content
                },
                "done": False
            })}\n\n'

            # Final chunk with complete response
            yield f'data: {json.dumps({
                "model": model,
                "created_at": now_timestamp(),
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "done": True,
                "total_duration": total_duration,
                "load_duration": 1000000,  # 1ms
                "prompt_eval_count": len(prompt.split()),
                "prompt_eval_duration": int(total_duration * 0.1),
                "eval_count": len(response_content.split()),
                "eval_duration": int(total_duration * 0.9)
            })}\n\n'

        return StreamingResponse(generate_stream(), media_type="text/plain")
    else:
        logger.info("📝 Enviando resposta não-streaming")
        # Non-streaming response
        return JSONResponse(
            content={
                "model": model,
                "created_at": now_timestamp(),
                "message": {"role": "assistant", "content": response_content},
                "done": True,
                "total_duration": total_duration,
                "load_duration": 1000000,  # 1ms
                "prompt_eval_count": len(prompt.split()),
                "prompt_eval_duration": int(total_duration * 0.1),
                "eval_count": len(response_content.split()),
                "eval_duration": int(total_duration * 0.9),
            }
        )


@app.post("/api/generate")
async def generate(request: Request):
    """Generate a completion."""
    body = await request.json()
    model = body.get("model", MODEL_FULL_NAME)
    prompt = body.get("prompt", "")
    stream = body.get("stream", True)
    suffix = body.get("suffix", "")
    format_type = body.get("format", None)
    _options = body.get("options", {})  # Reserved for future model options
    system = body.get("system", "")
    _template = body.get("template", "")  # Reserved for custom templates
    context = body.get("context", [])
    raw = body.get("raw", False)
    _keep_alive = body.get("keep_alive", "5m")  # Reserved for memory management
    _images = body.get("images", [])  # Reserved for multimodal support

    logger.info(
        f"🤖 POST /api/generate - Modelo: {model}, Stream: {stream}, Formato: {format_type}"
    )
    logger.debug(f"📝 Prompt: {prompt[:200]}{'...' if len(prompt) > 200 else ''}")
    logger.debug(f"🔧 Sistema: {system[:100]}{'...' if len(system) > 100 else ''}")

    # Validate model (be more flexible)
    if not is_valid_model(model):
        # For compatibility, accept any model name and use our default
        logger.warning(
            f"⚠️ Modelo desconhecido '{model}', usando padrão {MODEL_FULL_NAME}"
        )
        model = MODEL_FULL_NAME

    # Handle model loading (empty prompt)
    if not prompt.strip():
        logger.info("📭 Prompt vazio - retornando resposta de carregamento")
        return JSONResponse(
            content={
                "model": model,
                "created_at": now_timestamp(),
                "response": "",
                "done": True,
            }
        )

    # Build complete prompt
    full_prompt = prompt
    if system and not raw:
        full_prompt = f"System: {system}\n\n{prompt}"
    if suffix:
        full_prompt = f"{full_prompt}\n{suffix}"

    logger.debug(
        f"🔧 Prompt completo: {full_prompt[:300]}{'...' if len(full_prompt) > 300 else ''}"
    )

    # Call Gemini
    start_time = time.time()
    gemini_resp = call_gemini(full_prompt)
    end_time = time.time()

    # Handle errors
    if "error" in gemini_resp:
        logger.error(f"❌ Erro no Gemini: {gemini_resp['error']}")
        raise HTTPException(status_code=500, detail=gemini_resp["error"])

    response_content = gemini_resp.get("text", str(gemini_resp))
    logger.info(
        f"✅ Resposta gerada em {end_time - start_time:.2f}s, {len(response_content)} caracteres"
    )

    # JSON format handling
    if format_type == "json":
        logger.debug("🔧 Processando formato JSON")
        try:
            # Try to ensure response is valid JSON
            json.loads(response_content)
        except json.JSONDecodeError:
            # If not valid JSON, wrap it
            logger.warning("⚠️ Resposta não é JSON válido, encapsulando")
            response_content = json.dumps({"response": response_content})

    # Calculate timing
    total_duration = int((end_time - start_time) * 1_000_000_000)  # nanoseconds

    if stream:
        logger.info("🌊 Iniciando resposta em streaming")

        async def generate_stream():
            # Simulate streaming by chunking the response
            chunk_size = max(1, len(response_content) // 5)
            for i in range(0, len(response_content), chunk_size):
                chunk = response_content[i : i + chunk_size]
                is_done = i + chunk_size >= len(response_content)

                response_obj = {
                    "model": model,
                    "created_at": now_timestamp(),
                    "response": chunk,
                    "done": is_done,
                }

                # Add completion stats to final chunk
                if is_done:
                    response_obj.update(
                        {
                            "context": context if context else [1, 2, 3],
                            "total_duration": total_duration,
                            "load_duration": 1000000,  # 1ms
                            "prompt_eval_count": len(full_prompt.split()),
                            "prompt_eval_duration": int(total_duration * 0.1),
                            "eval_count": len(response_content.split()),
                            "eval_duration": int(total_duration * 0.9),
                        }
                    )

                yield f"{json.dumps(response_obj)}\n"

                if not is_done:
                    await asyncio.sleep(0.1)  # Small delay between chunks

        return StreamingResponse(generate_stream(), media_type="application/x-ndjson")
    else:
        logger.info("📝 Enviando resposta não-streaming")
        # Non-streaming response
        return JSONResponse(
            content={
                "model": model,
                "created_at": now_timestamp(),
                "response": response_content,
                "done": True,
                "context": context if context else [1, 2, 3],
                "total_duration": total_duration,
                "load_duration": 1000000,  # 1ms
                "prompt_eval_count": len(full_prompt.split()),
                "prompt_eval_duration": int(total_duration * 0.1),
                "eval_count": len(response_content.split()),
                "eval_duration": int(total_duration * 0.9),
            }
        )


@app.get("/api/ps")
async def list_running_models():
    """List models that are currently loaded into memory."""
    logger.info("🏃 GET /api/ps - Listando modelos em execução")
    return JSONResponse(
        content={
            "models": [
                {
                    "name": MODEL_NAME,
                    "model": MODEL_NAME,
                    "size": SIZE,
                    "digest": DIGEST,
                    "details": get_model_details(),
                    "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat()
                    + "Z",
                    "size_vram": SIZE,
                }
            ]
        }
    )


@app.post("/api/embed")
async def generate_embeddings(request: Request):
    """Generate embeddings from a model."""
    body = await request.json()
    model = body.get("model", MODEL_FULL_NAME)
    input_text = body.get("input", "")
    _truncate = body.get("truncate", True)  # Reserved for context length handling
    _options = body.get("options", {})  # Reserved for future model options
    _keep_alive = body.get("keep_alive", "5m")  # Reserved for memory management

    logger.info(f"🔗 POST /api/embed - Modelo: {model}")
    logger.debug(
        f"📝 Input: {str(input_text)[:200]}{'...' if len(str(input_text)) > 200 else ''}"
    )

    # Validate model (be flexible)
    if not is_valid_model(model):
        logger.warning(
            f"⚠️ Modelo desconhecido '{model}' para embeddings, usando padrão {MODEL_FULL_NAME}"
        )
        model = MODEL_FULL_NAME

    # Handle multiple inputs
    if isinstance(input_text, list):
        inputs = input_text
    else:
        inputs = [input_text]

    logger.debug(f"🔧 Processando {len(inputs)} entrada(s) para embedding")

    # Generate fake embeddings (in real implementation, you'd call Gemini for embeddings)
    embeddings = []
    for text in inputs:
        # Generate a fake embedding vector (384 dimensions for example)
        # Use hash of text to generate consistent fake embeddings
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to float values between -1 and 1
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            if i + 4 <= len(hash_bytes):
                val = struct.unpack("f", hash_bytes[i : i + 4])[0]
                embedding.append(val)

        # Pad or truncate to 384 dimensions
        while len(embedding) < 384:
            embedding.append(0.0)
        embedding = embedding[:384]

        embeddings.append(embedding)

    logger.info(f"✅ Embeddings gerados: {len(embeddings)} vetores de 384 dimensões")

    return JSONResponse(
        content={
            "model": model,
            "embeddings": embeddings,
            "total_duration": 1000000,  # 1ms
            "load_duration": 500000,  # 0.5ms
            "prompt_eval_count": sum(len(text.split()) for text in inputs),
        }
    )


@app.post("/api/copy")
async def copy_model(request: Request):
    """Copy a model."""
    body = await request.json()
    source = body.get("source")
    destination = body.get("destination")

    if not source or not destination:
        raise HTTPException(
            status_code=400, detail="Source and destination are required"
        )

    if not is_valid_model(source):
        raise HTTPException(
            status_code=404, detail=f"Source model '{source}' not found"
        )

    # In a real implementation, you would copy the model
    # For this proxy, we just return success
    return JSONResponse(content={"status": "success"})


@app.delete("/api/delete")
async def delete_model(request: Request):
    """Delete a model."""
    body = await request.json()
    model = body.get("model")

    if not model:
        raise HTTPException(status_code=400, detail="Model name is required")

    if not is_valid_model(model):
        raise HTTPException(status_code=404, detail=f"Model '{model}' not found")

    # In a real implementation, you would delete the model
    # For this proxy, we just return success
    return JSONResponse(content={"status": "success"})


@app.post("/api/pull")
async def pull_model(request: Request):
    """Pull a model from the library."""
    body = await request.json()
    model = body.get("model")
    _insecure = body.get("insecure", False)  # Reserved for TLS settings
    stream = body.get("stream", True)

    if not model:
        raise HTTPException(status_code=400, detail="Model name is required")

    if stream:

        async def pull_stream():
            steps = [
                {"status": "pulling manifest"},
                {
                    "status": "downloading",
                    "digest": DIGEST,
                    "total": SIZE,
                    "completed": SIZE // 4,
                },
                {
                    "status": "downloading",
                    "digest": DIGEST,
                    "total": SIZE,
                    "completed": SIZE // 2,
                },
                {
                    "status": "downloading",
                    "digest": DIGEST,
                    "total": SIZE,
                    "completed": SIZE,
                },
                {"status": "verifying sha256 digest"},
                {"status": "writing manifest"},
                {"status": "removing any unused layers"},
                {"status": "success"},
            ]

            for step in steps:
                yield f"{json.dumps(step)}\n"
                await asyncio.sleep(0.5)

        return StreamingResponse(pull_stream(), media_type="application/x-ndjson")
    else:
        return JSONResponse(content={"status": "success"})


@app.post("/api/push")
async def push_model(request: Request):
    """Push a model to the library."""
    body = await request.json()
    model = body.get("model")
    _insecure = body.get("insecure", False)  # Reserved for TLS settings
    stream = body.get("stream", True)

    if not model:
        raise HTTPException(status_code=400, detail="Model name is required")

    if stream:

        async def push_stream():
            steps = [
                {"status": "retrieving manifest"},
                {"status": "starting upload", "digest": DIGEST, "total": SIZE},
                {"status": "pushing manifest"},
                {"status": "success"},
            ]

            for step in steps:
                yield f"{json.dumps(step)}\n"
                await asyncio.sleep(0.5)

        return StreamingResponse(push_stream(), media_type="application/x-ndjson")
    else:
        return JSONResponse(content={"status": "success"})


# Legacy embedding endpoint for backward compatibility
@app.post("/api/embeddings")
async def generate_embedding_legacy(request: Request):
    """Generate embedding (legacy endpoint)."""
    body = await request.json()
    model = body.get("model", MODEL_FULL_NAME)
    prompt = body.get("prompt", "")
    options = body.get("options", {})
    keep_alive = body.get("keep_alive", "5m")

    # Convert to new format and call embed endpoint
    # Note: embed_request would be used in a more complex implementation

    # Simulate the request body for embed endpoint
    embed_body = {
        "model": model,
        "input": prompt,
        "options": options,
        "keep_alive": keep_alive,
    }

    # Mock the request
    class MockRequest:
        async def json(self):
            return embed_body

    embed_response = await generate_embeddings(MockRequest())

    # Convert response to legacy format
    response_data = json.loads(embed_response.body)
    if response_data.get("embeddings"):
        embedding = (
            response_data["embeddings"][0] if response_data["embeddings"] else []
        )
        return JSONResponse(content={"embedding": embedding})

    return JSONResponse(content={"embedding": []})


@app.post("/v1/chat/completions")
async def openai_chat_completions(request: Request):
    """OpenAI-compatible chat completions endpoint."""
    body = await request.json()
    model = body.get("model", MODEL_FULL_NAME)
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    # Extract other parameters but don't log unused warnings
    _temperature = body.get("temperature", 0.7)
    _top_p = body.get("top_p", 1.0)
    _n = body.get("n", 1)
    _max_tokens = body.get("max_tokens", None)
    _stop = body.get("stop", None)
    _presence_penalty = body.get("presence_penalty", 0)
    _frequency_penalty = body.get("frequency_penalty", 0)

    logger.info(
        f"🔌 POST /v1/chat/completions (OpenAI) - Modelo: {model}, Stream: {stream}, Mensagens: {len(messages)}"
    )
    logger.debug(
        f"📨 Mensagens OpenAI: {json.dumps(messages, ensure_ascii=False)[:500]}{'...' if len(str(messages)) > 500 else ''}"
    )

    # Validate model - accept any model name for OpenAI compatibility
    if not model:
        logger.error("❌ Modelo não especificado")
        raise HTTPException(status_code=400, detail="Model is required")

    # Handle empty messages
    if not messages:
        logger.info("📭 Mensagens vazias - retornando resposta vazia OpenAI")
        if stream:

            async def empty_stream():
                chunk_data = {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model,
                    "system_fingerprint": "fp_ollama",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"role": "assistant", "content": ""},
                            "finish_reason": "stop",
                        }
                    ],
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(empty_stream(), media_type="text/event-stream")
        else:
            return JSONResponse(
                content={
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": ""},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                    },
                }
            )

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
        f"🔧 Prompt OpenAI construído: {prompt[:300]}{'...' if len(prompt) > 300 else ''}"
    )

    # Call Gemini
    gemini_resp = call_gemini(prompt)

    # Handle errors
    if "error" in gemini_resp:
        logger.error(f"❌ Erro no Gemini (OpenAI): {gemini_resp['error']}")
        raise HTTPException(status_code=500, detail=gemini_resp["error"])

    response_content = gemini_resp.get("text", str(gemini_resp))
    logger.info(f"✅ Resposta OpenAI gerada, {len(response_content)} caracteres")

    # Calculate token usage (approximation)
    prompt_tokens = len(prompt.split())
    completion_tokens = len(response_content.split())
    total_tokens = prompt_tokens + completion_tokens

    completion_id = f"chatcmpl-{int(time.time())}"
    created_timestamp = int(time.time())

    if stream:
        logger.info("🌊 Iniciando resposta OpenAI em streaming")

        async def generate_openai_stream():
            # Split response into chunks for streaming
            words = response_content.split()
            chunk_size = max(1, len(words) // 10)  # Split into ~10 chunks

            for i in range(0, len(words), chunk_size):
                chunk_words = words[i : i + chunk_size]
                chunk_content = " ".join(chunk_words)

                # Add space at the beginning if not the first chunk
                if i > 0:
                    chunk_content = " " + chunk_content

                is_last_chunk = i + chunk_size >= len(words)

                chunk_data = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created_timestamp,
                    "model": model,
                    "system_fingerprint": "fp_ollama",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "role": "assistant" if i == 0 else None,
                                "content": chunk_content,
                            },
                            "finish_reason": "stop" if is_last_chunk else None,
                        }
                    ],
                }

                # Remove None values from delta
                if chunk_data["choices"][0]["delta"]["role"] is None:
                    del chunk_data["choices"][0]["delta"]["role"]

                yield f"data: {json.dumps(chunk_data)}\n\n"

                if not is_last_chunk:
                    await asyncio.sleep(0.05)  # Small delay between chunks

            # Send final chunk with usage info
            final_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created_timestamp,
                "model": model,
                "system_fingerprint": "fp_ollama",
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                },
            }

            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_openai_stream(), media_type="text/event-stream"
        )
    else:
        logger.info("📝 Enviando resposta OpenAI não-streaming")
        # Non-streaming response
        return JSONResponse(
            content={
                "id": completion_id,
                "object": "chat.completion",
                "created": created_timestamp,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": response_content},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                },
            }
        )


@app.get("/v1/models")
async def openai_list_models():
    """OpenAI-compatible models endpoint."""
    logger.info("🔌 GET /v1/models - Listando modelos (OpenAI)")
    return JSONResponse(
        content={
            "object": "list",
            "data": [
                {
                    "id": MODEL_FULL_NAME,
                    "object": "model",
                    "created": int(
                        time.mktime(
                            datetime.fromisoformat(
                                MODIFIED_AT.replace("Z", "+00:00")
                            ).timetuple()
                        )
                    ),
                    "owned_by": "ollama",
                    "permission": [],
                    "root": MODEL_FULL_NAME,
                    "parent": None,
                }
            ],
        }
    )


if __name__ == "__main__":
    print("🚀 Starting Ollama API proxy server on port 11434")
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
    print("📝 Logs serão salvos em: ollama_proxy.log")

    logger.info("🚀 Iniciando servidor Ollama API proxy na porta 11434")
    logger.info(f"📦 Modelo disponível: {MODEL_FULL_NAME}")

    uvicorn.run(app, host="0.0.0.0", port=11434)
