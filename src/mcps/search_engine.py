"""Hybrid BM25 + semantic code-snippet search over a project tree."""

import fnmatch
import os
import re
import subprocess

# pylint: disable=import-error
from fastembed import TextEmbedding  # type: ignore[import-not-found]
import numpy as np
from rank_bm25 import BM25Okapi  # type: ignore[import-not-found]

# pylint: enable=import-error

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


def _run_ag(text: str, root_project: str) -> dict[str, list[int]]:
    """Run `ag` for `text` under `root_project`; return {file: [matched line numbers]}.

    Args:
        text: whitespace-separated terms to search for (joined as an OR regex).
        root_project: directory to search in.

    Returns:
        A map of file path to the set of line numbers (+/- a small window)
        where a match was found.
    """
    exclude_dirs = [item for item in DEFAULT_EXCLUDE if item.endswith("/")]
    exclude_files = [item for item in DEFAULT_EXCLUDE if not item.endswith("/")]
    command = ["ag", "--nocolor", "--numbers", "--filename"]
    command.extend(f'--ignore="{item.replace("/", "")}"' for item in exclude_dirs)
    command.extend(f'--ignore="*{item}"' for item in exclude_files)
    command.append("|".join(text.split()))
    command.append(root_project)
    command.extend(
        ["|", "awk", "{ print substr($0, 1, length($0) < 250 ? length($0) : 250) }"]
    )

    # args built from a fixed allowlist, not raw input
    result = subprocess.run(  # noqa: S603
        command, capture_output=True, text=True, check=False
    )

    data: dict[str, list[int]] = {}
    if result.returncode != 0:
        return data
    for line in result.stdout.split("\n"):
        parts = line.split(":")
        if len(parts) <= 1:
            continue
        limit = 5
        file, number = parts[0], int(parts[1])
        window = range(max(number - limit, 1), number + limit)
        data[file] = list(set(data.get(file, []) + list(window)))
    return data


def _blocks_from_matches(key: str, matched_lines: list[int]) -> list[dict[str, str]]:
    """Group a file's matched line numbers into contiguous code blocks."""
    blocks: list[dict[str, str]] = []
    with open(key, encoding="utf-8", errors="ignore") as f:
        file_lines = f.readlines()
    lines = sorted(matched_lines)
    start = last = lines[0]
    for line_no in lines:
        if abs(line_no - last) > 1:
            blocks.append({"path": key, "code": "".join(file_lines[start:last])})
            start = line_no
        last = line_no
    return blocks


def ag_search(
    text: str = "",
    root_project: str = "src",
    globs: list[str] | None = None,
) -> list[dict[str, str]]:
    """Run `ag` over `root_project` and return matched code blocks.

    Args:
        text: whitespace-separated terms to search for (joined as an OR regex).
        root_project: directory to search in.
        globs: filename glob patterns to keep; defaults to every file.

    Returns:
        A list of `{"path": ..., "code": ...}` blocks around each match.
    """
    if globs is None:
        globs = ["*.*"]
    matches = _run_ag(text, root_project)
    result_blocks: list[dict[str, str]] = []
    for key, matched_lines in matches.items():
        if any(fnmatch.fnmatch(key, glob) for glob in globs):
            result_blocks.extend(_blocks_from_matches(key, matched_lines))
    return result_blocks


def should_exclude(path: str) -> bool:
    """Return True if `path` matches any pattern in DEFAULT_EXCLUDE.

    Args:
        path: file or directory path to check.

    Returns:
        True if the path should be skipped.
    """
    normalized = path.replace("\\", "/")
    return any(pattern in normalized for pattern in DEFAULT_EXCLUDE)


_CODE_EXTENSIONS = (".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".md", ".prisma")


def _snippets_from_file(fpath: str, max_chars_per_chunk: int) -> list[dict[str, str]]:
    """Split one file's contents into blank-line-delimited, size-capped chunks."""
    try:
        with open(fpath, encoding="utf-8", errors="ignore") as f:
            code = f.read()
    except OSError:
        return []

    chunks = re.split(r"\n\s*\n", code)
    return [
        {"path": fpath, "code": chunk.strip()[:max_chars_per_chunk]}
        for chunk in chunks
        if chunk.strip()
    ]


def collect_code_snippets(
    base_dir: str = "src", max_chars_per_chunk: int = 600
) -> list[dict[str, str]]:
    """Walk `base_dir` and split every source file into blank-line-delimited chunks.

    Args:
        base_dir: directory to walk.
        max_chars_per_chunk: max characters kept per chunk.

    Returns:
        A list of `{"path": ..., "code": ...}` snippets.
    """
    snippets: list[dict[str, str]] = []
    for root, _, files in os.walk(base_dir):
        if should_exclude(root):
            continue
        for fname in files:
            fpath = os.path.join(root, fname)
            if should_exclude(fpath) or not fname.endswith(_CODE_EXTENSIONS):
                continue
            snippets.extend(_snippets_from_file(fpath, max_chars_per_chunk))
    return snippets


def bm25_filter(
    snippets: list[dict[str, str]], query: str, top_n: int = 50
) -> list[dict[str, str]]:
    """Keep the `top_n` snippets most relevant to `query` by BM25 score.

    Args:
        snippets: candidate `{"path": ..., "code": ...}` snippets.
        query: search query.
        top_n: max number of snippets to keep.

    Returns:
        The `top_n` highest-scoring snippets.
    """
    tokenized_corpus = [s["code"].lower().split() for s in snippets]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    ranked = sorted(
        zip(snippets, scores, strict=True), key=lambda x: x[1], reverse=True
    )
    return [s for s, _ in ranked[:top_n]]


def semantic_rerank(
    snippets: list[dict[str, str]], query: str, top_n: int = 10
) -> list[dict[str, object]]:
    """Re-rank `snippets` by cosine similarity to `query` in embedding space.

    Args:
        snippets: candidate `{"path": ..., "code": ...}` snippets.
        query: search query.
        top_n: max number of snippets to keep.

    Returns:
        The `top_n` snippets most similar to `query`, each with a `score`.
    """
    embedder = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    query_emb = np.array(list(embedder.embed([query])))[0]
    code_embs = np.array(list(embedder.embed([s["code"] for s in snippets])))

    sims = np.dot(code_embs, query_emb) / (
        np.linalg.norm(code_embs, axis=1) * np.linalg.norm(query_emb)
    )

    ranked = sorted(zip(snippets, sims, strict=True), key=lambda x: x[1], reverse=True)
    return [
        {"path": s["path"], "code": s["code"], "score": round(float(score), 4)}
        for s, score in ranked[:top_n]
    ]


def search_codebase(
    query: str, base_dir: str = "src", globs: list[str] | None = None, top_n: int = 10
) -> list[dict[str, object]]:
    """Search `base_dir` for `query`: `ag` match, BM25 filter, then semantic rerank.

    Args:
        query: search query.
        base_dir: directory to search in.
        globs: filename glob patterns to keep; defaults to every file.
        top_n: max number of results to return.

    Returns:
        The `top_n` snippets most relevant to `query`, each with a `score`.
    """
    snippets = ag_search(query, root_project=base_dir, globs=globs)
    if not snippets:
        return []

    filtered = bm25_filter(snippets, query)
    return semantic_rerank(filtered, query, top_n)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    _base_dir = "$HOME/develop/lingopass/lingospace-backend"
    logging.info(search_codebase("token image", base_dir=_base_dir))
