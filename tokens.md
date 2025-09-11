Aqui está uma tabela com o **limite de tokens na janela de contexto** das principais **LLMs (Large Language Models)** até agosto de 2025, com base nas versões mais conhecidas:

| **Modelo**                      | **Janela de Contexto (tokens)** | **Observações**                                                              |
| ------------------------------- | ------------------------------- | ---------------------------------------------------------------------------- |
| **GPT-4o (OpenAI)**             | 128k (128.000 tokens)           | Modelo mais recente, disponível via ChatGPT e API                            |
| **GPT-4-turbo (OpenAI)**        | 128k                            | Versão mais barata e rápida do GPT-4, com janela estendida                   |
| **GPT-4 (original)**            | 8k / 32k                        | Versões distintas para uso geral ou com janela estendida                     |
| **GPT-3.5-turbo (OpenAI)**      | 16k                             | Modelo gratuito no ChatGPT; janela aumentada comparada ao GPT-3.5 inicial    |
| **Claude 3 Opus (Anthropic)**   | 200k                            | Janela de contexto mais ampla disponível atualmente                          |
| **Claude 3 Sonnet (Anthropic)** | 200k                            | Versão intermediária, também com 200k tokens                                 |
| **Claude 3 Haiku (Anthropic)**  | 200k                            | Versão mais leve, mas com mesmo contexto                                     |
| **Gemini 1.5 Pro (Google)**     | 1M (1.000.000 tokens)           | Janela de contexto mais longa entre modelos atuais                           |
| **Gemini 1.5 Flash (Google)**   | 1M                              | Versão otimizada para velocidade e custo                                     |
| **Command R+ (Cohere)**         | 128k                            | Otimizado para tarefas de RAG e contexto longo                               |
| **Mistral (variações)**         | 32k                             | Modelos open-source como Mixtral suportam até 32k, dependendo da arquitetura |
| **LLaMA 2 (Meta)**              | 4k–32k                          | Varia conforme o fine-tuning e integração                                    |
| **LLaMA 3 (Meta)**              | 8k–128k                         | Dependendo da versão e configuração da API                                   |
| **Yi-34B (01.AI)**              | 32k                             | Modelo open-source com janela estendida                                      |

### Observações:

- **Token** ≠ palavra. Em média, 1.000 tokens = 750 palavras.
- Janela de contexto maior permite lidar com documentos longos, múltiplos turnos de conversa e RAG (retrieval-augmented generation).
- Modelos open-source (como LLaMA, Mistral, Yi, etc.) podem ter janelas configuráveis conforme o treinamento/inferência.
