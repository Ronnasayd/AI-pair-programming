import sys
import os
import tiktoken


def split_by_tokens(caminho_arquivo, tamanho=100000, modelo="gpt-4"):
    if not os.path.isfile(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    # Leitura do conteúdo do arquivo
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Seleção do codificador com base no modelo
    try:
        encoding = tiktoken.encoding_for_model(modelo)
    except KeyError:
        print(
            f"Modelo '{modelo}' não reconhecido, usando codificação padrão (cl100k_base)."
        )
        encoding = tiktoken.get_encoding("cl100k_base")

    parts = conteudo.split("###")
    size = 0
    content = ""
    chunk_count = 1

    # Pasta de saída: mesma do arquivo de entrada
    dir_arquivo = os.path.dirname(os.path.abspath(caminho_arquivo))
    pasta_saida = os.path.join(dir_arquivo, "chunks")
    os.makedirs(pasta_saida, exist_ok=True)
    total_size = 0
    for part in parts:
        tokens = encoding.encode(part)
        token_count = len(tokens)

        if size + token_count > tamanho:
            nome_arquivo = os.path.join(pasta_saida, f"chunk_{chunk_count:03d}.md")
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Chunk {chunk_count} salvo com {size} tokens.")
            total_size += size
            chunk_count += 1
            size = 0
            content = ""

        content += part + "###"
        size += token_count

    if content.strip():
        nome_arquivo = os.path.join(pasta_saida, f"chunk_{chunk_count:03d}.md")
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(content)
        total_size += size
        print(f"Chunk {chunk_count} salvo com {size} tokens.")

    print(f"Tamanho total dos chunks: {total_size} tokens.")


# Exemplo de uso
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python contar_tokens.py <caminho_arquivo> [tamanho] [modelo]")
        sys.exit(1)

    caminho = sys.argv[1]
    try:
        tamanho = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
    except ValueError:
        print("Erro: o tamanho deve ser um número inteiro.")
        sys.exit(1)

    modelo = sys.argv[3] if len(sys.argv) > 3 else "gpt-4"

    split_by_tokens(caminho, tamanho, modelo)
