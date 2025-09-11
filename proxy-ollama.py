#!/usr/bin/env python3
import requests
from flask import Flask, request, Response
from urllib.parse import urljoin
import json
import time

# Configuração
REMOTE_OLLAMA = "https://nasty-knives-remain.loca.lt/"  # endereço do ollama remoto
LOCAL_HOST = "0.0.0.0"
LOCAL_PORT = 11434

EXCLUDE_PATHS = ['api/show']

app = Flask(__name__)

def log_request(path):
    print(f"\n=== [{time.strftime('%Y-%m-%d %H:%M:%S')}] Nova requisição ===")
    print(f"URL local: {request.method} /{path}")
    print(f"Headers: {dict(request.headers)}")
    try:
        body_str = request.get_data().decode("utf-8", errors="replace")
        print(f"Body:\n{body_str}")
    except Exception as e:
        print(f"Erro ao ler corpo: {e}")

def log_response(resp):
    print(f"--- Resposta do remoto ---")
    print(f"Status: {resp.status_code}")
    print(f"Headers: {dict(resp.headers)}")
    try:
        # Tentamos decodificar JSON bonito se possível
        content = resp.content.decode("utf-8", errors="replace")
        if resp.headers.get("Content-Type", "").startswith("application/json"):
            try:
                parsed = json.loads(content)
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(content)
        else:
            print(content[:1000] + ("..." if len(content) > 1000 else ""))
    except Exception as e:
        print(f"Erro ao ler resposta: {e}")
    print("=" * 50)

def proxy_request(path):
    """Encaminha requisição para o Ollama remoto com logging."""
    if path not in EXCLUDE_PATHS:
        log_request(path)

    remote_url = urljoin(REMOTE_OLLAMA + "/", path)
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}

    resp = requests.request(
        method=request.method,
        url=remote_url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        stream=True
    )
    
    if path not in EXCLUDE_PATHS:
        log_response(resp)

    return Response(
        resp.iter_content(chunk_size=8192),
        status=resp.status_code,
        headers=dict(resp.headers)
    )

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def catch_all(path):
    return proxy_request(path)

if __name__ == '__main__':
    print(f"Proxy rodando em http://{LOCAL_HOST}:{LOCAL_PORT} -> {REMOTE_OLLAMA}")
    app.run(host=LOCAL_HOST, port=LOCAL_PORT)
