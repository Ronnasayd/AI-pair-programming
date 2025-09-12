ATUE NO MODO SELF-CONSISTENCY.

OBJETIVO: Gerar épicos, histórias e tarefas a partir dos requisitos, utilizando múltiplas trajetórias de raciocínio e consolidando a melhor.

PROCESSO:
1. Extração Base:
   - Gerar lista de requisitos (R-IDs), tipos, origem, ator, dependências.
2. Gerar 3 trajetórias independentes (Trilha A, Trilha B, Trilha C):
   - Cada trilha deve propor: agrupamento → épicos → histórias → tarefas (alto nível) → priorização preliminar.
   - Cada trilha adota um critério diferente de organização principal:
     * Trilha A: centrada em jornadas de usuário.
     * Trilha B: centrada em bounded contexts técnicos.
     * Trilha C: centrada em valor de negócio incremental.
3. Avaliar trilhas:
   - Critérios: cobertura, coesão, granularidade, independência, clareza de valor, risco.
   - Atribuir pontuação (0–5) por critério.
4. Escolher trilha base (ou mesclar elementos). Justificar.
5. Refinar trilha escolhida:
   - Ajustar épicos (SMART).
   - Garantir histórias INVEST.
   - Expandir tarefas com DoD.
6. Construir matriz de rastreabilidade final.
7. Validar cobertura e listar lacunas.
8. Priorizar (explicar método e parâmetros).
9. Produzir recomendações finais.

SAÍDA (MARKDOWN):
{{ TEMPLATE A SER FORNECIDO }}

PADRÕES:
- Critérios de aceite concretos (Given/When/Then).
- Estimativas: Story points (Fibonacci). Tarefas em horas.
- Categorias técnicas claras.

ANTES DE EXECUTAR:
Se faltar dado crítico (ex: personas inexistentes), solicite esclarecimentos; se continuar, declare premissas.

INSIRA OS DADOS A SEGUIR:
[DOCUMENTOS / CONTEXTO]
