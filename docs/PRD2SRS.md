
## 1. **Análise inicial**

* **Revisar o PRD**: compreender os objetivos do produto, público-alvo, casos de uso principais, limitações e métricas de sucesso.
* **Identificar lacunas**: verificar se o PRD cobre aspectos técnicos ou se há pontos vagos que precisam de detalhamento.

---

## 2. **Definir escopo do SRS**

* Extrair do PRD a **visão de alto nível** do sistema.
* Delimitar claramente **o que está dentro e fora do escopo** (ex.: features futuras que não serão implementadas agora).

---

## 3. **Organizar requisitos funcionais**

* Converter descrições de funcionalidades do PRD em **requisitos funcionais formais**, numerados e testáveis.
* Exemplo:

  * PRD: “O usuário deve poder resetar sua senha por e-mail.”
  * SRS: “RF-001: O sistema deve permitir que o usuário solicite a redefinição de senha através do envio de um link único e temporário para o e-mail cadastrado.”

---

## 4. **Organizar requisitos não funcionais**

* Traduzir expectativas do PRD em métricas técnicas:

  * Desempenho (ex.: tempo de resposta < 2s).
  * Segurança (ex.: criptografia AES-256 para dados sensíveis).
  * Confiabilidade (ex.: uptime 99,9%).
  * Usabilidade, portabilidade, escalabilidade etc.

---

## 5. **Modelagem de casos de uso / cenários**

* Transformar histórias de usuário ou fluxos descritos no PRD em:

  * **Casos de uso formais** (atores, gatilhos, pré-condições, fluxo principal, exceções).
  * **Diagramas UML** (opcional, mas ajuda muito).

---

## 6. **Detalhar interfaces externas**

* Especificar o que no PRD aparece de forma genérica (“integração com sistema de pagamento”).
* No SRS:

  * Descrever APIs, protocolos, formatos de dados (JSON, XML, gRPC).
  * Definir contratos de integração.

---

## 7. **Definir restrições e premissas**

* Listar limitações mencionadas no PRD (ex.: funcionar apenas em iOS/Android, ou restrições legais).
* Adicionar premissas técnicas não descritas mas necessárias (ex.: dependência de serviços cloud).

---

## 8. **Critérios de aceitação e testes**

* Requisitos do SRS devem ser **verificáveis**.
* Especificar critérios de aceitação (quando o requisito é considerado cumprido).
* Exemplo:

  * SRS: “RF-002 será aceito se, ao registrar um novo usuário, o sistema validar que e-mails duplicados não podem ser cadastrados.”

---

## 9. **Estruturar documento no padrão SRS**

Um SRS típico segue IEEE 29148:

1. Introdução

   * Propósito, escopo, definições
2. Visão geral do sistema
3. Requisitos funcionais
4. Requisitos não funcionais
5. Interfaces externas
6. Restrições, premissas, dependências
7. Critérios de aceitação
8. Apêndices (diagramas, glossário, referências)

---

## 10. **Validação e revisão**

* Validar com stakeholders se o SRS cobre todos os pontos do PRD.
* Validar com a equipe técnica se os requisitos são **implementáveis e testáveis**.
* Revisar linguagem: deve ser **clara, não ambígua e verificável**.

---

## 11. **Checklist de qualidade dos requisitos**

- Um requisito precisa ser necessário
- Um requisito precisa ser apropriado
- Um requisito precisa ser inequívoco
- Um requisito precisa ser completo
- Um requisito precisa ser singular
- Um requisito precisa ser exequível
- Um requisito precisa ser evidenciável
- Um requisito precisa ser correto
- Um requisito precisa ser conforme
- Um conjunto de requisitos precisa ser compreensível
- Um conjunto de requisitos precisa ser completo
- Um conjunto de requisitos precisa ser exequível
- Um conjunto de requisitos precisa ser consistente
- Um conjunto de requisitos precisa ser validável
