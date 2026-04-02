# arquivo: copilot_ollama.py
# Ollama API proxy server using GitHub Copilot as backend
# Similar to ollama_local_proxy.py but routes requests to GitHub Copilot instead of Gemini
import asyncio
import json
import logging
import os
import re
import sys
import time
import uuid
from datetime import datetime, timedelta

import uvicorn
import yaml
from copilot_api import CopilotAPI
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

LOG_SIZE = (
    200000  # Max characters to log for prompts and responses to prevent log flooding
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/copilot_ollama_proxy.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model configuration — populated at startup by load_model_config()
# ---------------------------------------------------------------------------
ALLOWED_MODELS: set[str] = set()
DEFAULT_MODEL: str = ""
VERSION = "0.18.2"


def load_model_config() -> None:
    """Load allowed models and default model from config.models.yaml.

    Reads the YAML file located next to this module.  Aborts server startup
    with a clear error message when the file is missing, malformed, or fails
    schema validation.
    """
    global ALLOWED_MODELS, DEFAULT_MODEL

    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "config.models.yaml"
    )

    try:
        with open(config_path, "r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh)
    except FileNotFoundError:
        logging.critical(f"❌ Model config file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as exc:
        logging.critical(f"❌ Invalid YAML in model config: {exc}")
        sys.exit(1)

    if not isinstance(config, dict):
        logging.critical("❌ Model config must be a YAML mapping")
        sys.exit(1)

    models = config.get("models")
    default_model = config.get("default_model")

    if not models or not isinstance(models, list) or len(models) == 0:
        logging.critical("❌ Model config 'models' must be a non-empty list")
        sys.exit(1)

    # Guard against non-string entries
    for entry in models:
        if not isinstance(entry, str):
            logging.critical(
                f"❌ Model config 'models' contains non-string entry: {entry!r}"
            )
            sys.exit(1)

    if not default_model or not isinstance(default_model, str):
        logging.critical("❌ Model config 'default_model' must be a non-empty string")
        sys.exit(1)

    if default_model not in models:
        logging.critical(
            f"❌ Model config 'default_model' ({default_model!r}) must be listed in 'models'"
        )
        sys.exit(1)

    ALLOWED_MODELS = set(models)
    DEFAULT_MODEL = default_model
    logging.info(
        f"✅ Model config loaded: {len(ALLOWED_MODELS)} model(s), default: {DEFAULT_MODEL}"
    )


# Load configuration immediately so globals are populated before routes are registered.
load_model_config()


def get_validated_model(model: str | None) -> str:
    """Return model as-is when valid; otherwise log and return the default."""
    if not model:
        return DEFAULT_MODEL
    if model not in ALLOWED_MODELS:
        logging.info(f"Unknown model {model!r}, using default {DEFAULT_MODEL!r}")
        return DEFAULT_MODEL
    return model


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


def extrair_attachments(texto: str) -> str:
    """
    Extrai todos os caminhos de arquivo a partir do padrão '// filepath: ...'
    e retorna uma string no formato:
    <attachments><attachment id="ARQUIVO_1"/><attachment id="ARQUIVO_2"/>...</attachments>
    """
    # Regex matches both: <attachment filePath="..."> content </attachment> and <attachment filePath="..."/>
    regex1 = r'<attachment\s+filePath=\"([^"]+)\"(?:\s*>[\s\S]*?<\/attachment>|\s*/>)'
    match1 = re.findall(regex1, texto)
    paths1 = [p for p in match1 if os.path.exists(p)]

    if paths1:
        # Remove all attachment tags (both formats)
        new_prompt = re.sub(
            r'<attachment\s+filePath=\"([^"]+)\"(?:\s*>[\s\S]*?<\/attachment>|\s*/>)',
            "",
            texto,
            count=0,
            flags=re.DOTALL,
        )
        return [new_prompt, paths1]

    match2 = re.search(r"<attachments>(.*)<\/attachments>", texto, re.DOTALL)
    if not match2:
        return []
    attachments_text = match2.group(1).strip()
    paths = re.findall(r"(#|#\s+)?filepath:\s*(.+)", attachments_text)
    paths = [path[1] for path in paths if path[0] == "" and os.path.exists(path[1])]
    if not paths:
        return []
    paths = [path for path in paths if os.path.exists(path)]
    attachments = "".join(
        f'<attachment id="{caminho.strip().split("/")[-1]}"/>' for caminho in paths
    )

    attachments_new_text = f"<attachments>{attachments}\n</attachments>"
    new_prompt = re.sub(
        r"<attachments>.*<\/attachments>",
        attachments_new_text,
        texto,
        count=0,
        flags=re.DOTALL,
    )
    return [new_prompt, paths]


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
        f"📝 Corpo da requisição: {request_body.decode('utf-8', errors='ignore')[:LOG_SIZE]}"
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
        f"📝 Corpo da resposta: {response_body[:100]}{'...' if len(response_body) > 100 else ''}"
    )

    return response


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


async def call_copilot(prompt: str, references: list = None, stream: bool = False):
    """Call the Copilot API and return the response."""
    start_time = time.time()
    logger.info("🤖 Iniciando chamada para Copilot")
    logger.debug(
        f"📝 Prompt enviado: {prompt[:200]}{'...' if len(prompt) > 200 else ''}"
    )

    try:
        client = initialize_copilot()
        if client is None:
            logger.error("CopilotAPI não inicializado.")
            return {"error": "CopilotAPI não inicializado."}

        refs = references or []

        # Chamada Copilot API
        result = await client.chat(prompt, refs, streaming=stream)
        execution_time = time.time() - start_time
        logger.info(f"✅ Copilot respondeu em {execution_time:.2f}s")

        if stream:

            async def openapi_generator():
                # Processa resposta streaming
                idref = f"{uuid.uuid4()}"
                for chunk in result:
                    data = {
                        "id": idref,
                        "object": "chat.completion",
                        "created": int(time.time()),
                        "model": DEFAULT_MODEL,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {
                                    "role": "assistant",
                                    "content": chunk.get("content", ""),
                                },
                                "finish_reason": None,
                            }
                        ],
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                yield f"data: {
                    json.dumps(
                        {
                            'id': idref,
                            'object': 'chat.completion',
                            'created': int(time.time()),
                            'model': DEFAULT_MODEL,
                            'choices': [
                                {
                                    'index': 0,
                                    'delta': {},
                                    'finish_reason': 'stop',
                                }
                            ],
                        },
                        ensure_ascii=False,
                    )
                }\n\n"

            return openapi_generator
        else:
            # Resposta não streaming
            if isinstance(result, dict):
                return {"text": result.get("message").get("content", "")}
            else:
                return {"text": str(result)}

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        logger.error(
            f"❌ Erro na chamada Copilot após {execution_time:.2f}s: {error_msg}"
        )
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            fallback_msg = (
                "Erro de autenticação: verifique suas credenciais do Copilot."
            )
        elif "400" in error_msg:
            fallback_msg = "Requisição inválida para Copilot."
        elif "timeout" in error_msg.lower():
            fallback_msg = "Timeout na chamada Copilot."
        else:
            fallback_msg = f"Erro inesperado: {error_msg}"
        return {"error": fallback_msg}


def convert_large_prompt_to_attachment(text: str) -> tuple[str, str | None]:
    """Convert large prompts (>100KB) to temporary file attachments.

    Args:
        text: The prompt text to potentially convert

    Returns:
        tuple of (processed_prompt, temp_file_path | None)
        - If text is <= 100KB: returns (text, None)
        - If text is > 100KB: creates file and returns ("<attachment id='filename'/>", file_path)
    """
    # Check byte size (UTF-8 encoded)
    text_bytes = text.encode("utf-8")
    byte_size = len(text_bytes)
    threshold = 102400  # 100KB in bytes

    if byte_size <= threshold:
        # Prompt is small enough, return as-is
        return (text, None)

    # Prompt is too large, convert to attachment
    try:
        # Create temp directory (idempotent)
        temp_dir = "/tmp/copilot-ollama/"
        os.makedirs(temp_dir, exist_ok=True)

        # Generate unique filename
        filename = f"copilot-{uuid.uuid4().hex[:8]}.tmp"
        temp_file_path = os.path.join(temp_dir, filename)

        # Write text to file
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(text)

        # Log conversion
        logger.info(
            f"Large prompt auto-converted to attachment: {byte_size} bytes (>{threshold}) → {filename}"
        )

        # Return attachment tag and file path
        # Use double quotes for compatibility with extrair_attachments regex
        attachment_tag = f'<attachment filePath="{temp_file_path}"/>'
        return (attachment_tag, temp_file_path)

    except Exception as e:
        logger.error(f"Failed to create attachment for large prompt: {e}")
        # Fallback: return original text if conversion fails
        return (text, None)


def cleanup_temp_files(file_paths: list[str]) -> None:
    """Safely clean up temporary files.

    Args:
        file_paths: List of file paths to delete

    Note:
        Never raises exceptions; logs all errors but continues cleanup.
    """
    for path in file_paths:
        if not path:
            continue

        try:
            # os.remove(path)
            logger.debug(f"Temp file deleted: {path}")
        except FileNotFoundError:
            logger.warning(f"Temp file not found (already cleaned): {path}")
        except PermissionError:
            logger.error(f"Permission denied deleting temp file: {path}")
        except Exception as e:
            logger.error(f"Failed to delete temp file {path}: {e}")


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
        model_name = DEFAULT_MODEL

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
    """Return True only when model_name is in the configured allowed set."""
    if not model_name:
        return False
    return model_name in ALLOWED_MODELS


def normalize_model_name(model_name: str) -> str:
    """Normalize model name to a consistent form."""
    if not model_name:
        return DEFAULT_MODEL

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
            "version": VERSION,
            "models": sorted(ALLOWED_MODELS),
            "backend": "github-copilot",
        }
    )


@app.get("/api/version")
async def version():
    """Get server version information."""
    return JSONResponse(
        content={"version": VERSION, "proxy": True, "backend": "github-copilot"}
    )


# Endpoints
@app.get("/api/tags")
async def list_models():
    """List models that are available locally."""
    logger.info("📋 GET /api/tags - Listando modelos disponíveis")
    return JSONResponse(
        content={"models": [get_model_info(m) for m in sorted(ALLOWED_MODELS)]}
    )


@app.get("/api/models")
async def list_models_alias():
    """Alias for /api/tags for backward compatibility."""
    return await list_models()


@app.get("/api/show")
async def show_model_get(name: str = Query(None)):
    """Show model information via GET request."""
    name = name or DEFAULT_MODEL
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
TEMPLATE "{{{{ .System }}}}\\n\\n{{{{ if .Tools }}}}{{{{ .Tools }}}}\\n\\n{{{{ end }}}}{{{{ .Prompt }}}}"
PARAMETER temperature 0.7
PARAMETER max_tokens 4096""",
            "parameters": """temperature                    0.7
max_tokens                     4096""",
            "template": "{{ .System }}\n\n{{ if .Tools }}{{ .Tools }}\n\n{{ end }}{{ .Prompt }}",
            "details": get_model_details(),
            "model_info": {
                "general.architecture": "transformer",
                "general.parameter_count": 175000000000,
                "general.quantization_version": 2,
                "tokenizer.model": "gpt-4",
                "tokenizer.ggml.merges": [],
                "tokenizer.ggml.token_type": [],
                "tokenizer.ggml.tokens": [],
            },
            "capabilities": ["completion", "tools"],
        }
    )


@app.post("/api/show")
async def show_model_post(request: Request):
    """Show model information via POST request."""
    body = await request.json()
    name = body.get("name", DEFAULT_MODEL)
    return await show_model_get(name=name)


@app.post("/api/chat")
async def chat(request: Request):
    """Generate a chat completion."""
    body = await request.json()
    model = get_validated_model(body.get("model", ""))
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

    # Initialize temp files tracking
    temp_files = []

    # Convert large prompt to attachment if necessary
    prompt, temp_file = convert_large_prompt_to_attachment(prompt)
    if temp_file:
        temp_files.append(temp_file)

    references = []
    info = extrair_attachments(prompt)
    if len(info) > 1:
        prompt = info[0]
        references = info[1]

    # Call Copilot with try-finally to ensure cleanup
    try:
        start_time = time.time()
        copilot_resp = await call_copilot(prompt, references, stream=stream)
        end_time = time.time()
    finally:
        # Always clean up temp files, even if there's an error
        cleanup_temp_files(temp_files)

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
    model = get_validated_model(body.get("model", ""))
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

    # Initialize temp files tracking
    temp_files = []

    # Convert large prompt to attachment if necessary
    full_prompt, temp_file = convert_large_prompt_to_attachment(full_prompt)
    if temp_file:
        temp_files.append(temp_file)

    # Add temp file path to references list if conversion occurred
    references = []
    if temp_file:
        references = [temp_file]

    # Call Copilot with try-finally to ensure cleanup
    try:
        start_time = time.time()
        copilot_resp = await call_copilot(
            full_prompt, references if temp_file else None, stream=stream
        )
        end_time = time.time()
    finally:
        # Always clean up temp files, even if there's an error
        cleanup_temp_files(temp_files)

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
    return JSONResponse(
        content={"models": [get_model_info(m) for m in sorted(ALLOWED_MODELS)]}
    )


@app.post("/api/embed")
async def generate_embeddings(request: Request):
    """Generate embeddings from a model."""
    body = await request.json()
    model = get_validated_model(body.get("model", ""))
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

    # Since we're usando Copilot, we just acknowledge the deletion
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
    model = get_validated_model(body.get("model", ""))
    messages = body.get("messages", [])
    stream = body.get("stream", False)

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
    info = extrair_attachments(prompt)
    references = []
    if len(info) > 1:
        prompt = info[0]
        references = info[1]
    # Call Copilot
    copilot_resp = await call_copilot(prompt, references, stream=stream)

    if stream:
        return StreamingResponse(content=copilot_resp(), media_type="text/event-stream")

    if copilot_resp.get("error"):
        raise HTTPException(status_code=500, detail=copilot_resp["error"])

    response_content = copilot_resp.get("text", str(copilot_resp))

    # OpenAI format response
    response_data = {
        "id": f"{uuid.uuid4()}",
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
                    "id": m,
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "github-copilot",
                    "permission": [],
                    "root": m,
                    "parent": None,
                }
                for m in sorted(ALLOWED_MODELS)
            ],
        }
    )


@app.post("/v1/messages")
async def anthropic_messages(request: Request):
    """Anthropic-compatible /v1/messages endpoint."""
    body = await request.json()
    model = get_validated_model(body.get("model", ""))
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    system = body.get("system", "")
    max_tokens = body.get("max_tokens", 1024)

    logger.info(f"🧠 POST /v1/messages - Model: {model}, Stream: {stream}")

    # Build prompt from Anthropic message format
    prompt_parts = []
    if system:
        prompt_parts.append(f"System: {system}")

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        # Anthropic supports content as string or list of blocks
        if isinstance(content, list):
            text_parts = [
                block.get("text", "")
                for block in content
                if block.get("type") == "text"
            ]
            content = " ".join(text_parts)

        if role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")

    prompt = "\n\n".join(prompt_parts)

    # Convert large prompts to temp file
    temp_files = []
    prompt, temp_file = convert_large_prompt_to_attachment(prompt)
    if temp_file:
        temp_files.append(temp_file)

    # Extract attachments
    references = []
    info = extrair_attachments(prompt)
    if len(info) > 1:
        prompt = info[0]
        references = info[1]

    message_id = f"msg_{uuid.uuid4().hex[:24]}"
    created_at = int(time.time())

    try:
        copilot_resp = await call_copilot(prompt, references, stream=stream)
    finally:
        cleanup_temp_files(temp_files)

    # --- Streaming ---
    if stream:

        async def anthropic_stream():
            # message_start event
            yield f"event: message_start\ndata: {
                json.dumps(
                    {
                        'type': 'message_start',
                        'message': {
                            'id': message_id,
                            'type': 'message',
                            'role': 'assistant',
                            'content': [],
                            'model': model,
                            'stop_reason': None,
                            'stop_sequence': None,
                            'usage': {
                                'input_tokens': len(prompt.split()),
                                'output_tokens': 0,
                            },
                        },
                    }
                )
            }\n\n"

            # content_block_start
            yield f"event: content_block_start\ndata: {
                json.dumps(
                    {
                        'type': 'content_block_start',
                        'index': 0,
                        'content_block': {'type': 'text', 'text': ''},
                    }
                )
            }\n\n"

            # Stream chunks from Copilot generator
            output_tokens = 0
            async for chunk in copilot_resp():
                # copilot_resp() yields SSE strings like "data: {...}\n\n"
                # parse the content out of them
                if not chunk.startswith("data: "):
                    continue
                try:
                    data = json.loads(chunk[6:])
                    delta_content = (
                        data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    )
                    if delta_content:
                        output_tokens += len(delta_content.split())
                        yield f"event: content_block_delta\ndata: {
                            json.dumps(
                                {
                                    'type': 'content_block_delta',
                                    'index': 0,
                                    'delta': {
                                        'type': 'text_delta',
                                        'text': delta_content,
                                    },
                                }
                            )
                        }\n\n"
                except (json.JSONDecodeError, IndexError):
                    continue

            yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': 0})}\n\n"

            yield f"event: message_delta\ndata: {
                json.dumps(
                    {
                        'type': 'message_delta',
                        'delta': {'stop_reason': 'end_turn', 'stop_sequence': None},
                        'usage': {'output_tokens': output_tokens},
                    }
                )
            }\n\n"

            yield f"event: message_stop\ndata: {json.dumps({'type': 'message_stop'})}\n\n"

        return StreamingResponse(anthropic_stream(), media_type="text/event-stream")

    # --- Non-streaming ---
    if copilot_resp.get("error"):
        raise HTTPException(status_code=500, detail=copilot_resp["error"])

    response_content = copilot_resp.get("text", "")

    return JSONResponse(
        content={
            "id": message_id,
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": response_content}],
            "model": model,
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": len(prompt.split()),
                "output_tokens": len(response_content.split()),
            },
        }
    )


if __name__ == "__main__":
    print("🚀 Starting Copilot Ollama API proxy server on port 11434")
    print(f"📦 Available models: {', '.join(sorted(ALLOWED_MODELS))}")
    print(f"🎯 Default model: {DEFAULT_MODEL}")
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
    print("  - POST /v1/messages           - Anthropic-compatible messages")
    print("  - GET  /v1/models         - OpenAI-compatible models list")
    print("📝 Logs serão salvos em: /tmp/copilot_ollama_proxy.log")
    print("🔧 Backend: GitHub Copilot API")

    logger.info("🚀 Iniciando servidor Copilot Ollama API proxy na porta 11434")
    logger.info(f"📦 Modelos disponíveis: {', '.join(sorted(ALLOWED_MODELS))}")
    logger.info(f"🎯 Modelo padrão: {DEFAULT_MODEL}")
    logger.info("🔧 Backend: GitHub Copilot API")

    # Initialize temporary attachment directory
    os.makedirs("/tmp/copilot-ollama/", exist_ok=True)
    logger.info("Temporary attachment directory initialized: /tmp/copilot-ollama/")

    # Initialize Copilot client on startup
    initialize_copilot()

    uvicorn.run(app, host="0.0.0.0", port=11434)
