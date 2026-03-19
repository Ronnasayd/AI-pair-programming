#!/usr/bin/env python3
# protect-files.py

import sys
import json
import fnmatch
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

PROTECTED_PATTERNS = [
    ".env",
    ".env.*",
    ".git/*",
    "secrets/*",
    "**/*.pem",
    "**/*.key",
    "**/id_rsa*",
]

def is_protected(file_path: str) -> tuple[bool, str]:
    for pattern in PROTECTED_PATTERNS:
        if fnmatch.fnmatch(file_path, pattern):
            return True, pattern
        # checa também se o padrão aparece como substring
        if pattern.strip("*./") in file_path:
            return True, pattern
    return False, ""

def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        logging.error(f"JSON inválido: {e}")
        sys.exit(1)

    file_path = (
        payload.get("tool_input", {}).get("filePath")
        or payload.get("tool_input", {}).get("file_path")  # normaliza variações
        or ""
    )

    if not file_path:
        sys.exit(0)

    blocked, pattern = is_protected(file_path)

    if blocked:
        print(
            json.dumps({    
                "decision": "deny",       # saída estruturada, fácil de logar/auditar
                "file": file_path,
                "reason": f"matches protected pattern '{pattern}'",
            }),
            file=sys.stderr,
        )
        sys.exit(2)  # código específico para bloqueio

    sys.exit(0)

if __name__ == "__main__":
    main()
