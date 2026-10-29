# Contrato de eventos Socket.IO

Todos os nomes usam o namespace padrão `/`. Pedidos são emitidos por um cliente e
recebidos somente pelo servidor. Fatos são emitidos pelo servidor para todos os
clientes conectados, salvo `operacao.recusada`, que é direcionado apenas ao solicitante.
Os payloads de fatos seguem o padrão existente `fato(causa, **extras)` e incluem
`estado` atualizado e `causa`.

## Snapshot

### `estado.sincronizado`

- **Direção**: servidor → cliente conectado.
- **Quando**: conexão ou reconexão.
- **Payload**: `estado` completo, incluindo moedas, reservas, quantidade de pães e
  detalhes atuais de todos os pães prontos e produções pendentes; `causa: "conexao"`.

## Pedidos do cliente

### `pao.produzir`

- **Direção**: cliente → servidor.
- **Dados**: sem payload obrigatório.
- **Validações**: temporada aberta; pelo menos 10 sacas; padeiro livre; forno
  concluído e livre; total de prontos e em produção menor que seis.
- **Aceitação**: debita 10 sacas e reserva vaga, padeiro e forno antes de qualquer
  `await`; emite `pao.producao_iniciada` e conclui após quatro segundos.
- **Recusa**: `operacao.recusada` somente ao solicitante, com `motivo` e
  `causa: "pao.produzir"`.

### `pao.vender`

- **Direção**: cliente → servidor.
- **Dados**: sem payload obrigatório.
- **Validações**: temporada aberta e ao menos um pão pronto.
- **Aceitação**: recalcula primeiro os limites de idade e preço já vencidos; remove
  todos os pães prontos em uma única alteração, soma seus valores atuais em moedas e
  emite `paes.vendidos`.
- **Recusa**: `operacao.recusada` somente ao solicitante, com `motivo` e
  `causa: "pao.vender"`; não altera moedas ou pães.

## Fatos do servidor

### `pao.producao_iniciada`

Broadcast após a reserva e débito de farinha. Inclui `estado`, `causa:
"pao.produzir"`, `pao_id` da vaga reservada e `por` com o nome do jogador.

### `pao.produzido`

Broadcast após quatro segundos de produção válida. Inclui `estado`, `pao_id`, o pão
concluído (`id`, estado `fresco`, `valor_centavos: 500`, `idade_segundos: 0`) e `por`.

### `pao.amanhecido`

Broadcast ao completar 60 segundos desde a conclusão. Inclui estado atualizado e o
pão que mudou para `amanhecido`; o valor permanece até a primeira redução.

### `pao.valor_reduzido`

Broadcast a cada intervalo completo de 10 segundos no estado amanhecido. Inclui estado
atualizado e o pão afetado; valor mínimo zero.

### `paes.vendidos`

Broadcast após venda válida. Inclui estado atualizado, quantidade vendida e
`valor_total_centavos` creditado.

### `paes.producao_cancelada`

Broadcast quando o encerramento cancela uma ou mais produções. Inclui estado
atualizado, identificadores cancelados e `farinhas_devolvidas`; cada produção devolve
10 sacas e libera sua vaga, padeiro e forno.

### `operacao.recusada`

Servidor → somente o socket solicitante. Inclui `motivo` textual e nome do pedido em
`causa`; o estado global não muda.

## Ordem e consistência

- O servidor valida e reserva antes de ceder o controle assíncrono; nenhum pedido
  simultâneo pode gastar o mesmo saldo ou reservar o mesmo recurso.
- Cada snapshot é serializado com cópias dos registros de pão e produção; listas
  aninhadas não devem compartilhar objetos mutáveis com estados já emitidos.
- Ao encerrar, cancela todas as produções e aplica os reembolsos antes de emitir
  `paes.producao_cancelada` e `vila.encerrada`.
- O cliente atualiza o snapshot recebido pelo helper de escuta existente. Não calcula
  preço, aceita produções ou decide vendas localmente.
- A conexão recebe o snapshot completo porque fatos emitidos durante desconexão não
  são assumidos como reproduzidos.
