Existem diversos tipos/estratégias de prompts para LLMs (Large Language Models) que ajudam a estruturar o raciocínio e melhorar os resultados, especialmente em tarefas complexas de resolução de problemas ou tomada de decisão. Veja os principais, exemplos e quando usá-los:

---

### 1. **Tree of Thoughts (Árvore de Pensamentos)**
- **O que é:** O modelo explora múltiplas linhas de raciocínio simultaneamente, ramificando caminhos possíveis como em uma árvore de decisões.
- **Exemplo de prompt:**
  ```
  Resolva o problema abaixo explorando diferentes caminhos de raciocínio. Para cada etapa, liste múltiplas opções e avalie cada uma, escolhendo a melhor para seguir adiante.
  Problema: Como posso otimizar custos em uma empresa de tecnologia?
  ```
- **Quando usar:**
  - Tarefas de planejamento complexo
  - Problemas que envolvem múltiplas soluções potenciais
  - Quando queremos que o modelo avalie alternativas antes de decidir

---

### 2. **Sequential Thoughts (Pensamento Sequencial)**
- **O que é:** O modelo segue uma cadeia linear de raciocínio, resolvendo um passo de cada vez de forma ordenada.
- **Exemplo de prompt:**
  ```
  Resolva o seguinte problema passo a passo, explicando cada decisão antes de prosseguir para a próxima etapa.
  Problema: Calcule o valor final após aplicar 10% de desconto em R$ 200.
  ```
- **Quando usar:**
  - Problemas matemáticos e lógicos
  - Tarefas que exigem etapas claras e sequência definida
  - Situações em que o processo é tão importante quanto a resposta

---

### 3. **Chain of Thought (Cadeia de Pensamentos)**
- **O que é:** Similar ao sequencial, mas o foco é o modelo explicar seu raciocínio em linguagem natural entre os passos.
- **Exemplo de prompt:**
  ```
  Explique seu raciocínio ao resolver o seguinte problema:
  Problema: Se João tem 3 maçãs e ganha mais 2, quantas maçãs ele terá?
  ```
- **Quando usar:**
  - Questões de lógica
  - Perguntas abertas ou de múltipla escolha
  - Quando queremos transparência no processo de raciocínio

---

### 4. **Self-Consistency (Autoconsistência)**
- **O que é:** O modelo gera múltiplas cadeias de pensamento para a mesma questão e escolhe a resposta mais frequente ou plausível.
- **Exemplo de prompt:**
  ```
  Gere três explicações diferentes para a resposta deste problema e escolha a mais convincente.
  Problema: Qual é a raiz quadrada de 16?
  ```
- **Quando usar:**
  - Tarefas onde a resposta correta pode variar
  - Quando há ambiguidade ou múltiplas interpretações possíveis

---

### 5. **Scratchpad Prompting**
- **O que é:** O modelo utiliza um "rascunho" ou bloco de anotações para trabalhar com cálculos intermediários antes de dar a resposta final.
- **Exemplo de prompt:**
  ```
  Use o bloco de rascunho abaixo para calcular e depois forneça a resposta final.
  Problema: Qual é 12 x 15?
  Rascunho: ...
  ```
- **Quando usar:**
  - Problemas matemáticos complexos
  - Situações que exigem vários cálculos intermediários

---

### 6. **Reflexion Prompting**
- **O que é:** O modelo reflete sobre a resposta, revisando e corrigindo possíveis erros.
- **Exemplo de prompt:**
  ```
  Resolva o problema abaixo, depois revise sua resposta e corrija se encontrar erros.
  Problema: Se um trem parte às 8h e viaja por 3 horas, que horas ele chega?
  ```
- **Quando usar:**
  - Ao buscar minimizar erros
  - Para tarefas críticas onde revisão é importante

---

### Resumindo:
- **Tree of Thoughts:** Para explorar múltiplos caminhos e avaliar opções.
- **Sequential/Chain of Thought:** Para raciocínio passo a passo linear.
- **Self-Consistency:** Para validação e robustez da resposta.
- **Scratchpad:** Para cálculos detalhados.
- **Reflexion:** Para revisão e autocorreção.

Se quiser exemplos práticos para um tipo específico, só pedir!
