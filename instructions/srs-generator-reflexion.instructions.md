<instruções>

Você seguirá um processo iterativo de 3 ciclos (podendo encurtar se a qualidade já for alta):

CICLO 1 – DRAFT INICIAL:
- Gerar versão inicial do SRS (mínimo viável completo).
- Marcar incertezas com tag TODO:? no corpo.

CICLO 2 – CRÍTICA:
- Gerar uma seção interna (não incluída no SRS final) de auditoria avaliando:
  * Cobertura de funcionalidades declaradas no PRD
  * Completude dos fluxos de casos de uso
  * Clareza e testabilidade dos requisitos
  * Rastreabilidade (UC/US -> FR -> NFR)
  * Consistência terminológica
  * Gaps (itens do PRD não mapeados)
  * Riscos não tratados
- NÃO exibir o texto do SRS aqui, apenas a crítica estruturada.

CICLO 3 – REVISÃO:
- Ajustar o SRS removendo TODO:? resolvidos.
- Completar requisitos ausentes.
- Garantir que cada FR referencia pelo menos um UC ou US.
- Otimizar linguagem para testabilidade (evitar adjetivos vagos).

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

ENTREGA FINAL:
- Apenas a versão revisada do SRS (sem mostrar a crítica e sem o draft bruto).
- Manter estrutura oficial:
  # Título e Meta
  # Sumário
  # 1. Introdução
  # 2. Descrição Geral
  # 3. User Stories
  # 4. Requisitos Funcionais
  # 5. Requisitos Não-Funcionais
  # 6. Arquitetura Proposta
  # 7. APIs e Modelos de Dados (opcional se aplicável)
  # 8. Requisitos de Implantação e Operação
  # 9. Segurança e Conformidade
  # 10. Plano de Testes (opcional)
  # 11. Riscos e Alternativas Rejeitadas
  # 12. Apêndices (Matriz de Rastreabilidade, Glossário, Ambiguidades, Referências)

Padronização:
- UC-<n>, FR-<módulo>-<n>, NFR-<categoria>-<n>, US-<n>
- Matriz: tabela (US / UC / FR / NFR (se aplicável))

Entrada PRD:
{{PRD_DOCUMENTO}}

Contextos Adicionais:
{{CONTEXTOS_ADICIONAIS}}

Agora execute internamente os 3 ciclos e entregue apenas o SRS final revisado.

</instruções>