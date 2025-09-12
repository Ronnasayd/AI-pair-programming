# RECOMENDAÇÕES GERAIS

1. Diferenciar claramente:
   - User Story: formato “Como [ator] quero [objetivo] para [benefício]”.
   - Caso de Uso: fluxos detalhados (principal + alternativos).
2. Requisitos Funcionais:
   - Começar com verbo no infinitivo: “O sistema deve...”
   - Evitar ambiguidade: substituir “rápido” por métrica (ex: “<2s para...”).
3. Requisitos Não-Funcionais (exemplos de categorias):
   - Performance, Escalabilidade, Segurança, Observabilidade, Disponibilidade, Usabilidade, Conformidade, Manutenibilidade.
4. Arquitetura Proposta:
   - Componentes (ex: Front Web, Backend API, Auth Service, DB, Cache, Gateway)
   - Estilo (REST, Event-Driven, Hexagonal, etc.)
   - Integradores externos (pagamentos, notificações, etc.)
5. APIs e Dados:
   - Só se o PRD implicar endpoints claros. Caso contrário, justificar ausência.
6. Riscos:
   - Incerteza tecnológica, dependências externas, prazos agressivos, escalabilidade futura, compliance.
7. Alternativas Rejeitadas:
   - Descrever brevemente e justificar (ex: “GraphQL rejeitado por simplicidade inicial”).
8. Matriz de Rastreabilidade:
   - Cada FR deve mapear a pelo menos um UC ou US.
9. Ambiguidades:
   - Listar perguntas abertas para stakeholders.

