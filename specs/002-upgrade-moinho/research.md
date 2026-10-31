# Research: Upgrade do moinho

## Decisões

### Manter o fluxo de eventos do projeto

- **Decision**: A interface envia `moinho.nivel_solicitado`; o servidor valida e
  altera o estado; o fato `moinho.nivel_atualizado` é transmitido a todos os
  jogadores. Recusas reutilizam `operacao.recusada` apenas para quem solicitou.
- **Rationale**: Este é o padrão Socket.IO já utilizado para abertura da vila,
  construções, produção de recursos e recusas. O servidor permanece como
  autoridade do estado compartilhado.
- **Alternatives considered**: Alterar nível ou saldo diretamente no cliente;
  criar uma API HTTP paralela. Ambas divergem dos padrões existentes e
  possibilitam estados inconsistentes entre clientes.

### Calcular produção pelo nível atual do moinho

- **Decision**: Manter o ciclo de 5 segundos e calcular a quantidade por ciclo
  como `5 + (5 × nível do moinho)`. Inicializar no nível 1 e recalcular para os
  ciclos seguintes após um aprimoramento.
- **Rationale**: A fórmula, o intervalo e o intervalo de níveis estão definidos
  em `docs/especificacao.md`; a taxa inicial é 10 sacas por ciclo.
- **Alternatives considered**: Manter a taxa fixa de 10 ou aumentá-la quando
  uma construção termina. A primeira ignora os níveis; a segunda mantém o
  comportamento que a feature substitui.

### Validar e cobrar no servidor

- **Decision**: Usar o papel Mestre já mantido para a conexão, a fase da vila,
  o nível atual e o saldo compartilhado no momento do pedido. Calcular o custo
  como `nível atual × 10`, debitar e incrementar antes de qualquer espera
  assíncrona.
- **Rationale**: O servidor já trata os comandos de jogo com validação e
  mutação do estado em memória; a operação sem espera entre verificação e débito
  preserva o processamento sequencial dos pedidos concorrentes.
- **Alternatives considered**: Confiar em valores de nível ou custo enviados
  pelo cliente, ou cobrar o nível de destino. Não são necessários e permitiriam
  estado incorreto; a regra especifica o nível atual como base do custo.

### Integrar a interface existente

- **Decision**: Mostrar nível e produção na tela Vue e oferecer ação de
  aprimoramento ao Mestre; todos os clientes atualizam o estado e a cena pelo
  snapshot dos fatos recebidos. Manter Phaser 3/Tiled para a cena existente.
- **Rationale**: O cliente já mantém estado reativo sincronizado pelo payload
  `estado` e registra envios/recebimentos pelo helper de eventos.
- **Alternatives considered**: Criar outro cliente, painel ou sistema de
  renderização. Não há necessidade funcional e isso alteraria a arquitetura.

### Testar com `unittest` e fluxo de duas conexões

- **Decision**: Cobrir as regras do servidor por testes `unittest`, incluindo
  limites, cobrança, recusa e concorrência; validar a atualização visual em
  duas abas do navegador.
- **Rationale**: A suíte Python existente usa `unittest`, isola o estado do
  servidor e simula emissões e temporizadores. O repositório não declara testes
  de frontend ou scripts de build.
- **Alternatives considered**: Adicionar uma nova dependência ou framework de
  teste frontend. Não é necessário para verificar esta mudança.

## Contexto do projeto

- O estado compartilhado está em um dicionário global do processo servidor e
  seus snapshots são cópias do estado mais a causa do evento.
- A produção automática espera 5 segundos por ciclo e lê a taxa atual do
  estado; a conclusão de cada construção atualmente acrescenta 5 à taxa.
- O cliente atualiza o estado Vue ao receber fatos e envia pedidos pelo padrão
  `socket.emit`; a sincronização inicial usa `estado.sincronizado`.
- Não há persistência, manifesto de frontend ou versão mínima Python
  declarados no repositório.
