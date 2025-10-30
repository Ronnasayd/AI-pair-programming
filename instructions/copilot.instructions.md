<rules>
Gere código que siga as melhores práticas reconhecidas pelo setor e esteja otimizado para desempenho, segurança e escalabilidade.
Garanta que o código seja limpo, bem estruturado, legível e fácil de manter.
Siga rigorosamente as convenções de codificação, padrões de nomenclatura e as diretrizes de estilo do projeto ou linguagem utilizada.
Evite métodos, APIs ou bibliotecas obsoletos ou depreciados; prefira sempre alternativas atuais e bem suportadas pela comunidade.
Inclua comentários explicativos para lógicas complexas, decisões de arquitetura, limitações conhecidas e trechos de código não triviais.
Considere o contexto da base de código existente, integrando novas implementações de modo compatível e seguindo padrões já estabelecidos.
Evite mudanças que quebrem a retrocompatibilidade, exceto quando absolutamente necessário, e nesse caso, forneça documentação detalhada sobre as alterações e instruções para migração.
Ao criar funções, métodos, classes ou módulos, utilize nomes claros, descritivos e consistentes, refletindo com precisão o seu propósito e evitando ambiguidades.
Implemente tratamento de erros robusto e validação de entrada em todos os pontos relevantes, contemplando tanto erros previstos quanto exceções inesperadas.
Garanta que o código seja testável, incluindo exemplos, testes automatizados ou instruções para validação manual sempre que possível.
Para código front-end, assegure que componentes sejam responsivos, acessíveis, compatíveis com diferentes navegadores e dispositivos, e sigam as recomendações de usabilidade e padrões modernos da web (WCAG, ARIA, etc.).
Para código back-end, priorize segurança (proteção contra injeções, autenticação, autorização, criptografia), escalabilidade e eficiência no acesso a dados e recursos.
Se o pedido for ambíguo, incompleto ou contraditório, solicite esclarecimentos ao usuário antes de gerar o código, especificando as dúvidas de forma objetiva.
Evite o uso de gírias, linguagem informal ou abreviações excessivas nos comentários, documentação e mensagens de log.
Adote princípios de programação defensiva, modularização, reutilização e separação de responsabilidades.
Inclua documentação clara e objetiva, sempre que houver alterações significativas, novos componentes, endpoints, ou interfaces públicas.
Considere requisitos de internacionalização/localização, se aplicável ao projeto.
Sempre que possível, utilize recursos nativos da linguagem ou bibliotecas amplamente utilizadas, em vez de implementar soluções do zero sem justificativa técnica.
</rules>
<avoid>
Evite nomes confusos, genéricos ou abreviados para variáveis, funções, classes ou módulos (ex.: `x`, `temp1`, `doStuff`, `data1`).
Não escreva código sem comentários em seções complexas, algoritmos não triviais ou decisões fora do padrão.
Evite duplicação de código; prefira abstração e reutilização por meio de funções, métodos ou módulos.
Não ignore o tratamento de erros ou presuma sucesso em operações críticas, como acesso a recursos externos, I/O ou manipulação de dados.
Não utilize valores mágicos (números, strings hardcoded) sem explicação ou definição em constantes nomeadas ou enums.
Evite misturar múltiplas responsabilidades em uma única função, classe ou módulo; pratique o princípio da responsabilidade única.
Não implemente código sem testes básicos, validações de comportamento ou exemplos de uso.
Não ignore o desempenho em partes críticas, como loops ineficientes, consultas pesadas ou operações síncronas bloqueantes.
Nunca confie na entrada do usuário sem validação adequada ou proteção contra vulnerabilidades (XSS, CSRF).
Não deixe código morto, comentado, funções não utilizadas ou trechos obsoletos no projeto.
Não reimplemente funcionalidades já existentes em bibliotecas estáveis e bem testadas sem justificativa técnica relevante.
Não desconsidere guias de estilo, estrutura, convenções do projeto ou recomendações da equipe.
Evite excesso de estruturas condicionais aninhadas (muitos if-elif-else), prefira alternativas como polimorfismo, dicionários ou padrões de projeto.
Nunca importe módulos fora do nível superior do arquivo, exceto quando explicitamente necessário (ex.: imports condicionais ou de plugins).
Jamais capture exceções muito gerais (ex.: `except Exception`) sem necessidade; prefira capturar exceções específicas.
Não acesse membros protegidos ou privados fora da classe ou módulo de origem.
Evite deixar variáveis, argumentos ou parâmetros não utilizados no código.
Não utilize tipagem genérica ou permissiva demais (ex.: `any`, tipos sem restrição) sem motivo claro.
Evite dependências circulares, acoplamento excessivo entre módulos e violações ao princípio da inversão de dependências.
Não utilize práticas desatualizadas de segurança, algoritmos obsoletos de criptografia ou métodos inseguros de autenticação/autorização.
Não ignore requisitos de internacionalização/localização em projetos que demandem suporte multi-idioma.
Evite inconsistências entre ambientes de desenvolvimento, teste e produção (ex.: configurações hardcoded, caminhos absolutos, permissões diferentes).
</avoid>
<run_commands>
Execute comandos de tarefas longas (que levem mais de 2 segundos) com a ferramenta mcp my_run_command. Sempre passe o argumento correto rootProject para o run_command, que deve ser o diretório raiz do projeto. Se o projeto tiver um ambiente virtual (venv/.venv), ative-o automaticamente antes de executar o comando.
</run_commands>
<update_documentation>
Sempre que for solicitado a fazer documentação de modificações feitas após uma implementação utilize o mcp my_generate_docs_update. passando o argumento correto rootProject, que deve ser o diretório raiz do projeto e um commando que descreva as modificações feitas (ex: git diff). Siga as instruções fornecidas pela ferramenta para atualização da documentação.
</update_documentation>
<add_techs>
Sempre que novas tecnologias, frameworks ou bibliotecas forem introduzidas no projeto, deve-se gerar uma documentação com referências de uso, melhores práticas e links úteis utilizando a ferramenta de pesquisa ou mcp context7. Salve essa documentação em docs/techs/<nomedatecnologia>.md
</add_techs>
<task_master>
Sempre que for solicitado a fazer a implementação de uma nova task usando o mcp task_master. Deve solicitar no mcp task_master as informações referentes a task. criar uma nova branch  task-<ID da task> e seguir o checklist abaixo:
- [ ] Analisar o escopo da task no mcp task_master
- [ ] Atualizar o status da task para "Em Progresso" no mcp task_master
- [ ] Executa uma subtask por vez seguindo o checklist abaixo para cada subtask:
  - [ ] Atualizar o status da subtask para "Em Progresso" no mcp task_master
  - [ ] Criar um plano de ação detalhado para a subtask
  - [ ] Apresentar o plano de ação para o usuário e aguardar confirmação
  - [ ] Gerar uma pré-visualização do código a ser implementado e aguardar confirmação do usuário
  - [ ] Implementar a subtask seguindo o plano de ação aprovado
  - [ ] Aguardar o "okay" do usuário e atualizar o status da subtask para "Concluída" no mcp task_master
- [ ] Realizar um commit com uma mensagem clara e descritiva
- [ ] Após aprovação, realizar o merge da branch da task na branch principal
- [ ] Fechar a branch da task após o merge
</task_master>
<preview_code>
Sempre que for fazer alguma adição, exclusão ou modificação significativa no código, mostre uma pré-visualização do código que será feito. Mostre apenas os pontos principais do código que será gerado e utilize comentários bem explicativos em cada linha. Espere pela confirmação do usuário antes de prosseguir. Se ele adicionar sugestões, considere-as cuidadosamente e ajuste o código antes de fazer a modificação em si.</preview_code>
<show_action_plan>
Sempre que for fazer alguma adição, exclusão ou modificação significativa no código, explique o que será feito e o motivo de tal alteração. Espere pela confirmação do usuário antes de prosseguir. Se ele adicionar sugestões, considere-as cuidadosamente e ajuste o plano conforme necessário.
</show_action_plan>
