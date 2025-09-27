from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required, but unused
)

response = client.chat.completions.create(
    model="llama2",
    stream=True,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
    ],
)
print(response)
# Processa resposta streaming corretamente
for chunk in response:
    print(chunk)
    if hasattr(chunk, "choices") and chunk.choices:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()  # Nova linha ao final
