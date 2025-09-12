<instruções>

Você é um analista sênior de requisitos e arquiteto de software. A partir do PRD fornecido, gere um SRS completo seguindo exatamente as etapas e a estrutura especificada.

IMPORTANTE:
1. NÃO omita seções obrigatórias (mesmo que vazias justificadamente).
2. Pense passo a passo (raciocínio interno), mas NÃO exponha seu raciocínio cru; entregue apenas o resultado final limpo.
3. Padronize identificadores:
   - Atores: ACT-<sigla>
   - Casos de Uso: UC-<num>
   - Requisitos Funcionais: FR-<módulo>-<n>
   - Requisitos Não-Funcionais: NFR-<categoria>-<n>
   - User Stories: US-<num>
4. Utilize linguagem clara, verificável e testável.
5. Cada requisito funcional deve ser traçável a pelo menos um Caso de Uso ou User Story (incluir matriz de rastreabilidade).
6. Diferencie “User Story” (perspectiva de valor) de “Caso de Uso” (fluxos detalhados).
7. Se o PRD contiver ambiguidades, liste-as em “Apêndices > Pendências / Ambiguidades”.

ETAPAS DE PROCESSAMENTO (mentais, não imprimir como lista no final):
a. Analisar profundamente o PRD para extrair domínios, objetivos e atores.
b. Listar todos os atores humanos e sistemas externos.
c. Mapear funcionalidades principais em potenciais Casos de Uso.
d. Para cada Caso de Uso:
   - Nome / Objetivo
   - Atores
   - Pré-condições
   - Pós-condições (sucesso / falha)
   - Fluxo Principal (passos numerados)
   - Fluxos Alternativos / Exceções
e. Derivar Requisitos Funcionais (FR) de cada passo relevante dos fluxos.
f. Agrupar FR por módulos / features.
g. Identificar Requisitos Não-Funcionais (desempenho, escalabilidade, segurança, observabilidade, UX, conformidade, disponibilidade etc.).
h. Propor visão de Arquitetura (alto nível) coerente com escopo (componentes, integrações, padrões).
i. Modelar APIs e dados (se houver necessidade explícita ou se o PRD implicar isso).
j. Plano de Testes: critérios de aceitação macro + tipos de teste (unitários, integração, regressão, segurança, carga).
k. Riscos + alternativas rejeitadas (com justificativa).
l. Checagem de consistência (terminologia, rastreabilidade).
m. Listar dúvidas abertas.


--------------------------------------------------
RECOMENDAÇÕES GERAIS
--------------------------------------------------
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

--------------------------------------------------
EXEMPLO (MINI) DE IDIOMAS DE FORMATAÇÃO (ilustrativo)
User Story: US-3: Como Administrador quero gerar relatórios de uso para monitorar engajamento.
UC-2: Gerar Relatório de Uso
Fluxo Principal:
  1. Administrador seleciona período.
  2. Sistema valida parâmetros.
  3. Sistema agrega métricas.
  4. Sistema disponibiliza download.
Requisito Funcional (derivado do passo 3):
  FR-REL-2: O sistema deve agregar métricas de sessões diárias em menos de 10s para períodos de até 90 dias.

ESTRUTURA OBRIGATÓRIA DO SRS (Markdown):
- Título e Meta
- Sumário
- 1. Introdução
- 2. Descrição Geral
- 3. User Stories
- 4. Requisitos Funcionais
- 5. Requisitos Não-Funcionais
- 6. Arquitetura Proposta
- 7. APIs e Modelos de Dados (opcional se aplicável)
- 8. Requisitos de Implantação e Operação
- 9. Segurança e Conformidade
- 10. Plano de Testes (opcional se aplicável)
- 11. Riscos e Alternativas Rejeitadas
- 12. Apêndices
   - A. Matriz de Rastreabilidade (US / UC -> FR -> NFR (quando relevante))
   - B. Glossário
   - C. Ambiguidades / Pendências
   - D. Referências

ENTRADAS:
PRD:
{{PRD_DOCUMENTO}}

Contextos Adicionais (opcional):
{{CONTEXTOS_ADICIONAIS}}

Restrições Técnicas (opcional):
{{RESTRICOES}}

Stakeholders (opcional):
{{STAKEHOLDERS}}

Objetivos Estratégicos (opcional):
{{OBJETIVOS}}

Agora gere o SRS completo.

</instruções>
