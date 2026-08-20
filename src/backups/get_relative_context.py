from pathlib import Path
import re
import os
from glob import glob
import sys

# Padrões de import para cada linguagem
PADROES_IMPORT = {
    ".py": [r"^\s*import\s+([\w\.]+)", r"^\s*from\s+([\w\.]+)\s+import"],
    ".go": [
        r'^\s*import\s+"([^"]+)"',
        r"^\s*import\s+\((.*?)\)",  # Suporta múltiplos imports entre parênteses
    ],
    ".js": [
        r'^\s*import\s+.*?["\']([^"\']+)["\']',
        r'^\s*const\s+\w+\s*=\s*require\(["\']([^"\']+)["\']\)',
    ],
    ".ts": [
        r'^\s*import\s+.*?["\']([^"\']+)["\']',
        r'^\s*const\s+\w+\s*=\s*require\(["\']([^"\']+)["\']\)',
    ],
}


def encontrar_imports(caminho_arquivo, workspace, visitados=None):
    """
    Retorna lista (ordenada, sem repetições) dos arquivos encontrados
    a partir de caminho_arquivo, seguindo imports recursivamente.
    """
    if caminho_arquivo is None or workspace is None:
        return
    if visitados is None:
        visitados = set()
    visitados.add(caminho_arquivo)

    print(caminho_arquivo)

    ext = Path(caminho_arquivo).suffix
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        conteudo = f.read()

    padroes = PADROES_IMPORT[ext]
    imports_encontrados = get_imports(ext, conteudo, padroes)

    patterns = []
    for inp in imports_encontrados:
        if "/" in inp:
            p = inp.split("/")
            while len(p) >= 2:
                patterns += [os.path.join(workspace, "/".join(p)) + ext]
                patterns += [os.path.join(workspace, "/".join(p), "index") + ext]
                patterns += [os.path.join(workspace, "**", "/".join(p)) + ext]
                patterns += [os.path.join(workspace, "**", "/".join(p), "index") + ext]
                p.pop(0)
    for pattern in patterns:
        candidatos = glob(pattern, recursive=True)
        for candidato in candidatos:
            if candidato not in visitados:
                encontrar_imports(candidato, workspace, visitados)


def get_imports(ext, conteudo, padroes):
    imports_encontrados = []
    for padrao in padroes:
        if ext == ".go" and "import" in padrao and "(" in padrao:
            # Captura múltiplos imports em bloco
            matches = re.findall(padrao, conteudo, re.MULTILINE | re.DOTALL)
            for bloco in matches:
                imports_encontrados.extend(re.findall(r'"([^"]+)"', bloco))
        else:
            matches = re.findall(padrao, conteudo, re.MULTILINE)
            imports_encontrados.extend(matches)
    return imports_encontrados


if __name__ == "__main__":
    arquivo_inicial = sys.argv[1] if len(sys.argv) > 1 else None
    workspace = sys.argv[2] if len(sys.argv) > 2 else None
    encontrar_imports(arquivo_inicial, workspace)
