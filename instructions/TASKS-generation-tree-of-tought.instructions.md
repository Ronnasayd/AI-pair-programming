ATUE NO MODO TREE OF THOUGHTS.

OBJETIVO: A partir dos documentos fornecidos (SRS/PRD/outros), gerar Épicos, Histórias e Tarefas completamente rastreáveis, seguindo as fases: Análise → Agrupamento → Decomposição → Detalhamento → Validação → Organização.

INSTRUÇÕES DE RACIOCÍNIO (ÁRVORES):
1. Extraia TODOS os requisitos: atribua IDs (R-001...), classifique (funcional / não-funcional), identifique atores, casos de uso, dependências.
2. Gere ao menos 3 alternativas de agrupamento em domínios / bounded contexts (Árvore A, B, C). Liste prós/contras de cada.
3. Para cada agrupamento, proponha 2–3 opções de épicos por cluster. Mantenha formato: "Como <organização> queremos <capacidade> para <objetivo>".
4. Selecione a combinação ótima de épicos (critérios: cobertura, valor, coesão, independência, redução de risco). Justifique exclusões.
5. Para cada épico, gere histórias INVEST. Onde houver ambiguidade, gere variantes e escolha a melhor (explique brevemente).
6. Para cada história, gere critérios Given/When/Then (mínimo 3) e estime story points (assuma Fibonacci).
7. Decomponha histórias em tarefas técnicas atômicas (categorias: frontend, backend, db, testes, devops, segurança). Defina Definition of Done por tarefa.
8. Monte matriz de rastreabilidade: Requisito → Épico → Histórias → Tarefas.
9. Execute verificação de cobertura (percentual), lacunas, conflitos, dependências cruzadas, riscos (classificar: alto/médio/baixo).
10. Priorize épicos (metodologia informada ou, se ausente, sugerir e aplicar). Considere valor vs esforço vs risco vs dependências.
11. Proponha plano inicial de releases/sprints (ordem lógica).
12. Liste recomendações e pontos a validar com stakeholders.

PADRÕES:
- Épicos: SMART + valor de negócio + esforço relativo (T-Shirt).
- Histórias: INVEST + clara persona + benefício explícito.
- Tarefas: claras, estimáveis (< 16h), com DoD objetivo.
- Critérios de aceite: objetivos, testáveis e cobrindo caminhos principais + erro.

SAÍDA (MARKDOWN):
{{ TEMPLATE A SER FORNECIDO }}

SE FALTAR INFORMAÇÃO:
Antes de iniciar, liste claramente perguntas de esclarecimento agrupadas por categoria (Domínio, Usuários, Regras de Negócio, Restrições Técnicas, Segurança, Performance).

INÍCIO DOS DADOS:
[INSERIR AQUI OS DOCUMENTOS E CONTEXTO]
