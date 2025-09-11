#!/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import base64
import fnmatch
import hashlib
import math
import os
import re  # Usar re padrão do Python
import subprocess
from collections import Counter

import enchant
from dotenv import load_dotenv

home_directory = os.path.expanduser("~")
load_dotenv(dotenv_path=os.path.join(home_directory, ".secrets", "gcia.env"))

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
]

DEFAULT_CONTENT_EXCLUDE = os.getenv("DEFAULT_CONTENT_EXCLUDE", "").split(",")


def remove_comments_from_code(code: str, filetype: str) -> str:
    """
    Remove comentários do código com base na extensão do arquivo,
    mas mantém aqueles que contêm 'TODO:'.
    """

    def replacer(match: re.Match) -> str:
        comment = match.group(0)
        return comment if "TODO:" in comment else ""

    if filetype in {".js", ".ts", ".go"}:
        code = re.sub(
            r"//.*?$|/\*.*?\*/", replacer, code, flags=re.DOTALL | re.MULTILINE
        )
    elif filetype == ".py":
        code = re.sub(r"#.*$", replacer, code, flags=re.MULTILINE)
        code = re.sub(r'("""|\'\'\')(.*?)\1', replacer, code, flags=re.DOTALL)
    elif filetype in {".html", ".css"}:
        code = re.sub(r"<!--.*?-->", replacer, code, flags=re.DOTALL)
        code = re.sub(r"/\*.*?\*/", replacer, code, flags=re.DOTALL)

    return code


def run_tree_command(path=".", exclude_dirs=[], exclude_files=[]):
    command = ["tree", path]
    for item in exclude_dirs:
        command.extend(["-I", item.replace("/", "")])
    for item in exclude_files:
        command.extend(["-I", f"'*{item}'"])
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stdout:
        return result.stdout
    else:
        return "Erro ao executar o comando tree: " + result.stderr


def run_text_command(texts=[], exclude_dirs=[], exclude_files=[], directories=[]):
    command_results = []
    data = {}
    for directory in directories:
        command = ["ag", "--nocolor", "--numbers", "--filename"]
        for item in exclude_dirs:
            command.append(f'--ignore="{item.replace("/", "")}"')
        for item in exclude_files:
            command.append(f'--ignore="*{item}"')
        for text in texts:
            command.append(text)
        command.append(directory)
        command.extend(
            "| awk '{ print substr($0, 1, length($0) < 250 ? length($0) : 250) }'".split(
                " "
            )
        )
        # print(" ".join(command))

        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            # print(result.stdout)
            command_results.extend(result.stdout.split("\n"))
    for line in command_results:
        s = line.split(":")
        if len(s) > 1:
            limit = 5
            file = s[0]
            number = int(s[1])
            data[file] = list(
                set(
                    data.get(file, [])
                    + list(range(max(number - limit, 1), number + limit))
                )
            )
    return data


# Dicionários para ignorar identificadores válidos
english_dict = enchant.Dict("en_US")
portuguese_dict = enchant.Dict("pt_BR")


def shannon_entropy(s):
    if not s:
        return 0
    freq = Counter(s)
    length = len(s)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


def is_high_entropy_string(s, threshold=2.0):
    return shannon_entropy(s) >= threshold


def has_meaningful_words(s):
    parts = re.findall(r"[A-Za-z][a-z]+|[A-Z]{2,}(?=[A-Z][a-z])|[A-Z][a-z]*", s)
    meaningful1 = [
        p
        for p in parts
        if english_dict.check(p.lower()) or portuguese_dict.check(p.lower())
    ]
    parts = s.split("/")
    meaningful2 = [
        p
        for p in parts
        if english_dict.check(p.lower()) or portuguese_dict.check(p.lower())
    ]
    return len(meaningful1) >= 2 or len(meaningful2) >= 2


def is_base64_string(s):
    try:
        if len(s) % 4 != 0 or len(s) < 20:
            return False
        if has_meaningful_words(s):
            return False
        base64.b64decode(s, validate=True)
        return is_high_entropy_string(s)
    except Exception:
        return False


def detect_sensitive_content(text):
    patterns = [
        r"AKIA[0-9A-Z]{16}",  # AWS Access Key ID
        r"ASIA[0-9A-Z]{16}",  # AWS Temporary Access Key
        r"sk_live_[0-9a-zA-Z]{24,}",  # Stripe
        r"AIza[0-9A-Za-z-_]{35}",  # Google API
        r"(?i)-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----",
        r"(?i)-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----",
        r"(access_token|api_key|secret)[\'\"]?\s*[:=]\s*[\'\"][a-zA-Z0-9_\-]{20,}[\'\"]",
        r"\b[a-fA-F0-9]{32}\b",  # MD5
        r"\b[a-fA-F0-9]{40}\b",  # SHA1
        r"\b[a-fA-F0-9]{64}\b",  # SHA256
        r"\b[a-fA-F0-9]{128}\b",  # SHA512
        r"\$2[aby]?\$[0-9]{2}\$[./A-Za-z0-9]{53}",  # bcrypt
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",  # UUID
        r"G-[A-Z0-9]{8,20}",  # Google Analytics ID
        r"UA-[0-9]{4,10}-[0-9]{1,4}",  # Google Analytics ID (Universal)
        r"eyJ[A-Za-z0-9_=]+\.eyJ[A-Za-z0-9_=]+\.?[A-Za-z0-9_.+/=-]*",  # JWT Token
        r"r[0-9a-fA-F]{7,40}",  # Git commit hash
        r"ghp_[A-Za-z0-9_]{36,255}",  # GitHub Personal Access Token,
        r"6L[0-9A-Za-z_-]{38}",  # Google reCAPTCHA v3 keys
        r"GTM-[A-Z0-9]{6,8}",  # Google Tag Manager ID
    ]

    found = []

    # Detectar padrões fixos
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        found.extend(matches)

    # Detectar Base64s suspeitas
    base64_candidates = re.findall(r"[A-Za-z0-9+/=]{20,}", text)
    for candidate in base64_candidates:
        if is_base64_string(candidate):
            found.append(candidate)

    return found


def short_hash(texto, tamanho=8):
    hash_completo = hashlib.sha256(texto.encode()).hexdigest()
    return hash_completo[:tamanho]


def is_binary_file(file_path, blocksize=512):
    try:
        with open(file_path, "rb") as f:
            block = f.read(blocksize)
        if not block:
            return False
        if b"\0" in block:
            return True
        text_chars = bytearray(range(32, 127)) + b"\n\r\t\b"
        non_text = [byte for byte in block if byte not in text_chars]
        return len(non_text) / len(block) > 0.3
    except Exception:
        return True


def should_exclude(file_path, exclude_dirs, exclude_files, include_dirs):
    # Extrai diretórios do caminho para ver se deve incluir/excluir

    # Excluir se for arquivo e bater com padrão de arquivo a excluir
    for pattern in exclude_files:
        if fnmatch.fnmatch(file_path, f"*{pattern}"):
            return True

    # Se o caminho bate com include dirs, força a inclusão
    for pattern in include_dirs:
        if fnmatch.fnmatch(file_path, f"*{pattern}*"):
            return False  # inclui

    # Excluir se o caminho bater com algum diretório a excluir
    for pattern in exclude_dirs:
        if fnmatch.fnmatch(file_path, f"*{pattern}*"):
            return True  # exclui

    return False


def read_file(file, content_exclude, line_numbers=[]):
    filepath = file.replace(home_directory, "~")
    try:
        if is_binary_file(file):
            return None

        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                findings = detect_sensitive_content(content)
                if findings:
                    # print(f"\n[!] Conteúdo suspeito encontrado em: {filepath}")
                    for f in findings:
                        content = content.replace(f, "[PRIVATE-HASH-INFO]")
                        # print(f"  → {f}")
        except UnicodeDecodeError:
            with open(file, "r", encoding="latin-1") as f:
                content = f.read()

        if len(line_numbers) > 0:
            line_numbers = sorted(line_numbers)
            line_inc = ""
            aux_content = content.split("\n")
            last_line_number = 1
            for line_number in line_numbers:
                if line_number - last_line_number > 1:
                    line_inc += "...\n"
                line_inc += (
                    str(line_number)
                    + ":"
                    + aux_content[min(line_number - 1, len(aux_content))]
                    + "\n"
                )
                last_line_number = line_number
            if line_number < len(aux_content):
                line_inc += "...\n"
            content = line_inc

        content = re.sub(r"^\s*\n", "", content, flags=re.MULTILINE)
        content = private_values(content_exclude, content, value="[PRIVATE-INFO]")

        ext = "sh"
        if "." in filepath:
            _, ext = os.path.splitext(filepath)
            ext = ext[1:]
        # if ext == "md":
        #     content = content.replace("`", "\`")
        if ext in {"js", "ts", "go", "py", "html", "css"}:
            content = remove_comments_from_code(content, f".{ext}")
        content = remove_blank_lines(content)
        result = f"### Arquivo: {filepath}\n````{ext}\n{content}\n````\n"
        print(result)

    except Exception as e:
        return f"# ERRO ao ler arquivo {filepath}: {e}\n"


def remove_blank_lines(text: str) -> str:
    """
    Remove linhas que contêm apenas espaços, tabs ou quebras de linha.
    """
    return "\n".join(line for line in text.splitlines() if line.strip())


def private_values(content_exclude, content, value):
    for pattern in content_exclude:
        pattern = pattern.strip()
        if pattern:
            content = re.sub(re.escape(pattern), value, content, flags=re.IGNORECASE)

    return content


def parse_exclude_list(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def split_exclude_patterns(patterns):
    exclude_dirs = []
    exclude_files = []
    for p in patterns:
        p = p.strip()
        if p.endswith("/") or os.path.isdir(p):
            exclude_dirs.append(p)
        else:
            exclude_files.append(p)
    return exclude_dirs, exclude_files


def list_valid_files(paths, exclude_dirs, exclude_files, include_dirs):
    """
    Retorna a lista de arquivos válidos para processar, filtrando exclusões e inclusões.
    """
    valid_files = []
    directories = []
    for item in paths:
        if os.path.isfile(item):
            if not should_exclude(item, exclude_dirs, exclude_files, include_dirs):
                valid_files.append(item)
        else:
            directories.append(item)
            for root, _, files in os.walk(item):
                for file in files:
                    filepath = os.path.join(root, file)
                    if not should_exclude(
                        filepath, exclude_dirs, exclude_files, include_dirs
                    ):
                        valid_files.append(filepath)
    return valid_files, directories


def main():
    parser = argparse.ArgumentParser(description="Indexa arquivos texto paralelamente")
    parser.add_argument("paths", nargs="+", help="Diretórios ou arquivos para indexar")
    parser.add_argument(
        "--exclude",
        type=lambda v: [item.strip() for item in v.split(",") if item.strip()],
        default=[],
        help="Lista de padrões a excluir, separados por vírgula (ex: node_modules/,venv/,dist/)",
    )
    parser.add_argument(
        "--exclude-content",
        type=lambda v: [item.strip() for item in v.split(",") if item.strip()],
        default=[],
        help="Padrões para conteúdos a mascarar com [PRIVATE-INFO] (ex: node_modules/,venv/,dist/)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Número de threads simultâneas (padrão: 8)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Apenas listar arquivos",
    )
    parser.add_argument(
        "--tree",
        action="store_true",
        help="Adiciona a arvore de arquivos",
    )
    parser.add_argument(
        "--include",
        type=lambda v: [item.strip() for item in v.split(",") if item.strip()],
        default=[],
        help="Lista de padrões a incluir, separados por vírgula (ex: src/,tests/)",
    )
    parser.add_argument(
        "--text",
        type=lambda v: [item.strip() for item in v.split(",") if item.strip()],
        default=[],
        help="Lista de textos a pesquisar separados por vírgula (ex: 'import', 'from')",
    )

    parser.add_argument(
        "--text-full",
        action="store_true",
        help="Booleano que define se deve retorno todo o texto de um arquivo que tem referencia a um texto pesquisado",
    )

    args = parser.parse_args()
    combined_exclude = sorted(set(DEFAULT_EXCLUDE + (args.exclude or [])))

    exclude_dirs, exclude_files = split_exclude_patterns(combined_exclude)
    include_dirs = sorted(set(args.include or []))

    args.exclude_content = sorted(
        set(DEFAULT_CONTENT_EXCLUDE + (args.exclude_content or [])),
        key=len,
        reverse=True,
    )

    # 1) Listar arquivos válidos
    all_files, directories = list_valid_files(
        args.paths, exclude_dirs, exclude_files, include_dirs
    )
    all_files = sorted(all_files)

    if args.tree:
        print("## Arvores de arquivos")
        for directory in directories:
            print(
                f"````sh\n{run_tree_command(directory, exclude_dirs, exclude_files)}````"
            )

    # Se apenas listar, já retorna essa lista com caminho abreviado e nada mais
    if args.list:
        for file in sorted(all_files):
            print(file.replace(home_directory, "~"))
        return

    print(f"# Contexto\n")
    if args.text:
        data = run_text_command(
            texts=args.text,
            exclude_dirs=exclude_dirs,
            exclude_files=exclude_files,
            directories=directories,
        )
        if args.text_full:
            for file in data:
                read_file(file, args.exclude_content, [])
        else:
            for file in data:
                read_file(file, args.exclude_content, data[file])
    else:
        for file in all_files:
            read_file(file, args.exclude_content, [])


if __name__ == "__main__":
    main()
