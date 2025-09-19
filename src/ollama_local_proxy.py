# arquivo: ollama_local_proxy.py
import asyncio
import json
import subprocess
import time
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI()

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "gemini-proxy"  # Simplified name without tag
MODEL_TAG = "latest"
MODEL_FULL_NAME = f"{MODEL_NAME}:{MODEL_TAG}"
DIGEST = "sha256:fake-digest-123456789abcdef"
MODIFIED_AT = "2024-09-01T00:00:00Z"
SIZE = 12345678
PARAMETER_SIZE = "3B"
QUANTIZATION_LEVEL = "Q4_0"


def now_timestamp():
    return datetime.utcnow().isoformat() + "Z"


def call_gemini(prompt: str):
    """Call the external Gemini CLI tool and return the response."""
    try:
        cmd = ["gemini", "chat", "--prompt", prompt, "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"text": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr or str(e)}


def get_model_details():
    """Return standardized model details structure."""
    return {
        "parent_model": "",
        "format": "gguf",
        "family": "llama",  # Use "llama" as it's widely supported
        "families": ["llama"],  # Many clients expect "llama" family
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
        "expires_at": "2025-12-31T23:59:59Z",
        "size_vram": SIZE,
    }


def is_valid_model(model_name: str) -> bool:
    """Check if the model name is valid/supported."""
    if not model_name:
        return False

    # Support various formats
    valid_names = [
        MODEL_NAME,  # "gemini-proxy"
        MODEL_FULL_NAME,  # "gemini-proxy:latest"
        f"{MODEL_NAME}:latest",
        "gemini-proxy",
        "gemini-proxy:latest",
    ]

    return model_name in valid_names


def normalize_model_name(model_name: str) -> str:
    """Normalize model name to the canonical form."""
    if model_name in [MODEL_NAME, "gemini-proxy"]:
        return MODEL_FULL_NAME
    if model_name.endswith(":latest"):
        return model_name
    return f"{model_name}:latest" if ":" not in model_name else model_name


# Root endpoint for basic server info
@app.get("/")
async def root():
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
    return JSONResponse(content={"models": [get_model_info()]})


@app.get("/api/models")
async def list_models_alias():
    """Alias for /api/tags for backward compatibility."""
    return await list_models()


@app.get("/api/show")
async def show_model_get(name: str = Query(MODEL_FULL_NAME)):
    """Show model information via GET request."""
    if not is_valid_model(name):
        raise HTTPException(status_code=404, detail=f"Model '{name}' not found")

    normalized_name = normalize_model_name(name)

    return JSONResponse(
        content={
            "modelfile": f"FROM {normalized_name}\\nSYSTEM You are a helpful assistant powered by Gemini.",
            "parameters": 'temperature 0.7\\nstop "\\n"',
            "template": "{{ .System }}\\nUSER: {{ .Prompt }}\\nASSISTANT: {{ .Response }}",
            "details": get_model_details(),
            "model_info": {
                "general.architecture": "transformer",
                "general.file_type": 2,
                "general.parameter_count": 3000000000,
                "general.quantization_version": 2,
                "gemini.attention.head_count": 32,
                "gemini.attention.head_count_kv": 8,
                "gemini.block_count": 24,
                "gemini.context_length": 8192,
                "gemini.embedding_length": 2048,
                "gemini.feed_forward_length": 8192,
                "gemini.vocab_size": 32000,
                "tokenizer.ggml.model": "gpt2",
                "tokenizer.ggml.pre": "gemini-bpe",
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
    _options = body.get("options", {})  # Reserved for future model options
    _keep_alive = body.get("keep_alive", "5m")  # Reserved for memory management

    # Validate model
    if not is_valid_model(model):
        raise HTTPException(status_code=404, detail=f"Model '{model}' not found")

    # Handle empty messages (model loading)
    if not messages:
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

    # Call Gemini
    start_time = time.time()
    gemini_resp = call_gemini(prompt)
    end_time = time.time()

    # Handle errors
    if "error" in gemini_resp:
        raise HTTPException(status_code=500, detail=gemini_resp["error"])

    response_content = gemini_resp.get("text", str(gemini_resp))

    # Calculate timing
    total_duration = int((end_time - start_time) * 1_000_000_000)  # nanoseconds

    if stream:

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

    # Validate model
    if model != MODEL_NAME:
        raise HTTPException(status_code=404, detail=f"Model '{model}' not found")

    # Handle model loading (empty prompt)
    if not prompt.strip():
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

    # Call Gemini
    start_time = time.time()
    gemini_resp = call_gemini(full_prompt)
    end_time = time.time()

    # Handle errors
    if "error" in gemini_resp:
        raise HTTPException(status_code=500, detail=gemini_resp["error"])

    response_content = gemini_resp.get("text", str(gemini_resp))

    # JSON format handling
    if format_type == "json":
        try:
            # Try to ensure response is valid JSON
            json.loads(response_content)
        except json.JSONDecodeError:
            # If not valid JSON, wrap it
            response_content = json.dumps({"response": response_content})

    # Calculate timing
    total_duration = int((end_time - start_time) * 1_000_000_000)  # nanoseconds

    if stream:

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
    return JSONResponse(
        content={
            "models": [
                {
                    "name": MODEL_NAME,
                    "model": MODEL_NAME,
                    "size": SIZE,
                    "digest": DIGEST,
                    "details": get_model_details(),
                    "expires_at": "2024-12-31T23:59:59Z",
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

    # Validate model
    if model != MODEL_NAME:
        raise HTTPException(status_code=404, detail=f"Model '{model}' not found")

    # Handle multiple inputs
    if isinstance(input_text, list):
        inputs = input_text
    else:
        inputs = [input_text]

    # Generate fake embeddings (in real implementation, you'd call Gemini for embeddings)
    embeddings = []
    for text in inputs:
        # Generate a fake embedding vector (384 dimensions for example)
        import hashlib
        import struct

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

    if source != MODEL_NAME:
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

    if model != MODEL_NAME:
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


if __name__ == "__main__":
    print("Starting Ollama API proxy server on port 11434")
    print(f"Available model: {MODEL_FULL_NAME}")
    print("Endpoints:")
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
    uvicorn.run(app, host="0.0.0.0", port=11434)
