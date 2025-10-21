import os
import re

import numpy as np
from fastembed import TextEmbedding
from rank_bm25 import BM25Okapi

# ===============================
# 🔒 ARQUIVOS E DIRETÓRIOS A IGNORAR
# ===============================
DEFAULT_EXCLUDE = [
    "/node_modules/",
    "/vendor/",
    ".env",
    "/.git/",
    "venv/",
    ".png",
    ".jpeg",
    ".token.json",
    ".svg",
    ".pytest_cache",
    ".vscode-test",
    "/.nuxt/",
    "/dist/",
    "/build/",
    "__init__.py",
    "/.pytest_cache/",
    ".eslintcache",
    "yarn.lock",
    "package-lock.json",
    ".gitignore",
    ".log",
    ".editorconfig",
    ".eslintignore",
    ".eslintrc.js",
    ".tool-versions",
    ".prettierrc",
    "/coverage/",
    "go.mod",
    "go.sum",
    ".ttf",
    "/.husky/",
    ".dockerignore",
    ".nvmrc",
    "__pycache__/",
    ".pdf",
]


# ===================================
# 🔍 COLETA DE TRECHOS DE CÓDIGO
# ===================================
def should_exclude(path: str) -> bool:
    """
    Retorna True se o caminho deve ser ignorado com base no DEFAULT_EXCLUDE.
    Verifica substrings tanto em arquivos quanto em diretórios.
    """
    path = path.replace("\\", "/")  # normaliza para comparação
    for pattern in DEFAULT_EXCLUDE:
        if pattern in path:
            return True
    return False


def collect_code_snippets(base_dir="src", max_chars_per_chunk=600):
    snippets = []
    for root, _, files in os.walk(base_dir):
        if should_exclude(root):
            continue

        for fname in files:
            fpath = os.path.join(root, fname)
            if should_exclude(fpath):
                continue

            # filtrar extensões de código
            if not fname.endswith(
                (".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".md", ".prisma")
            ):
                continue

            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
            except Exception:
                continue

            # quebrar em blocos
            chunks = re.split(r"\n\s*\n", code)
            for chunk in chunks:
                chunk = chunk.strip()
                if len(chunk) > 0:
                    snippets.append(
                        {"path": fpath, "code": chunk[:max_chars_per_chunk]}
                    )
    return snippets


# ===================================
# 🔢 FILTRAGEM E RERANQUEAMENTO
# ===================================
def bm25_filter(snippets, query, top_n=50):
    tokenized_corpus = [s["code"].lower().split() for s in snippets]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    ranked = sorted(zip(snippets, scores), key=lambda x: x[1], reverse=True)
    return [s for s, _ in ranked[:top_n]]


def semantic_rerank(snippets, query, top_n=10):
    embedder = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    query_emb = np.array(list(embedder.embed([query])))[0]
    code_embs = np.array(list(embedder.embed([s["code"] for s in snippets])))

    sims = np.dot(code_embs, query_emb) / (
        np.linalg.norm(code_embs, axis=1) * np.linalg.norm(query_emb)
    )

    ranked = sorted(zip(snippets, sims), key=lambda x: x[1], reverse=True)
    return [
        {"path": s["path"], "code": s["code"], "score": round(float(score), 4)}
        for s, score in ranked[:top_n]
    ]


def search_codebase(query: str, base_dir="src"):
    snippets = collect_code_snippets(base_dir)
    if not snippets:
        return []

    filtered = bm25_filter(snippets, query)
    ranked = semantic_rerank(filtered, query)
    return ranked


if __name__ == "__main__":
    from pprint import pprint

    ranked = search_codebase(
        "token image", base_dir="/home/ronnas/develop/lingopass/lingospace-backend"
    )
    pprint(ranked)
