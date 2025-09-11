import tiktoken
import sys
import os

def contar_tokens_arquivo(caminho_arquivo, modelo="gpt-4"):
    if not os.path.isfile(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Escolhe o codificador com base no modelo
    try:
        encoding = tiktoken.encoding_for_model(modelo)
    except KeyError:
        print(f"Modelo '{modelo}' não reconhecido, usando codificação padrão (cl100k_base).")
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(conteudo)
    print(f"Arquivo: {caminho_arquivo}")
    print(f"Modelo: {modelo}")
    print(f"Tokens: {len(tokens)}")

    return len(tokens)

# Exemplo de uso
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python contar_tokens.py <caminho_arquivo> [modelo]")
        sys.exit(1)

    caminho = sys.argv[1]
    modelo = sys.argv[2] if len(sys.argv) > 2 else "gpt-4"

    contar_tokens_arquivo(caminho, modelo)
