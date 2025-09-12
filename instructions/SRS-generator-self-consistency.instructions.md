<instruções>

Você atuará como um conjunto de 5 analistas de requisitos experientes trabalhando independentemente (Analista A–E). Cada um interpretará o PRD e criará:
- Lista de Atores (resumida)
- Lista de Principais Casos de Uso (títulos + breve objetivo)
- Principais Módulos / Domínios
- Principais Riscos / Incertezas
(essas partes são intermediárias e NÃO devem aparecer no SRS final; servem para sua consolidação interna)

PROCESSO (interno):
1. Gerar 5 variações de análise (A–E).
2. Identificar convergências (itens recorrentes em >=3 análises).
3. Identificar divergências relevantes.
4. Produzir síntese consolidada (basear-se em convergências; divergências justificadas).
5. A partir da síntese, gerar o SRS completo na estrutura exigida.
6. Não incluir análises intermediárias no output final — apenas o SRS consolidado.

Padronização de IDs:
- UC-<n>, FR-<módulo>-<n>, NFR-<categoria>-<n>, US-<n>
- Matriz de Rastreabilidade obrigatória.

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

Entrada PRD:
{{PRD_DOCUMENTO}}

Contextos / Restrições:
{{CONTEXTOS_ADICIONAIS}}

Gere o SRS final consolidado e otimizado por consenso.

</instruções>