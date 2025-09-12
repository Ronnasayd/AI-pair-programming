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


ENTREGA FINAL:
- Apenas a versão revisada do SRS (sem mostrar a crítica e sem o draft bruto).

Padronização:
- UC-<n>, FR-<módulo>-<n>, NFR-<categoria>-<n>, US-<n>
- Matriz: tabela (US / UC / FR / NFR (se aplicável))

ENTRADAS:
PRD:
{{PRD_DOCUMENTO}}

ESTRUTURA:
{{ESTRUTURA_SRS}}

Contextos Adicionais (opcional):
{{CONTEXTOS_ADICIONAIS}}

Restrições Técnicas (opcional):
{{RESTRICOES}}

Stakeholders (opcional):
{{STAKEHOLDERS}}

Objetivos Estratégicos (opcional):
{{OBJETIVOS}}

Agora execute internamente os 3 ciclos e entregue apenas o SRS final revisado.

</instruções>
