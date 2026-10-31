# Contrato de eventos Socket.IO

Todos os pedidos são emitidos pelo cliente e validados pelo servidor. Fatos são
emitidos pelo servidor para todos os clientes conectados, salvo
`operacao.recusada`, que é direcionado apenas ao solicitante. Fatos usam o
padrão existente: snapshot `estado` atualizado, `causa` e campos adicionais.

## Sincronização inicial

### `estado.sincronizado`

- **Direção**: servidor → cliente conectado.
- **Quando**: conexão ou reconexão.
- **Payload**: snapshot completo, incluindo `nivel_moinho` e `producao`, além do
  `causa: "conexao"`.

## Pedido do cliente

### `moinho.nivel_solicitado`

- **Direção**: cliente → servidor.
- **Dados**: sem payload obrigatório; nível e custo não são aceitos do cliente.
- **Validações**: remetente com papel `mestre`, temporada aberta, nível atual
  entre 1 e 4 e saldo de moedas maior ou igual a `nivel_moinho × 10`.
- **Aceitação**: antes de qualquer espera assíncrona, debita o custo, incrementa
  o nível e atualiza a produção para `5 + (5 × novo_nivel)`; emite
  `moinho.nivel_atualizado`.
- **Recusa**: `operacao.recusada` apenas ao solicitante, com `motivo` e
  `causa: "moinho.nivel_solicitado"`; o estado global não muda.

## Fato do servidor

### `moinho.nivel_atualizado`

- **Direção**: servidor → todos os clientes.
- **Quando**: após a validação e o débito do aprimoramento.
- **Payload**: snapshot atualizado com saldo, `nivel_moinho` e `producao`;
  `causa: "moinho.nivel_solicitado"` e dados do jogador que solicitou, conforme
  o padrão de fatos existente.
- **Efeito**: todos os clientes atualizam a interface e a cena com o snapshot.

### `recurso.produzido`

- **Direção**: servidor → todos os clientes.
- **Quando**: a cada ciclo de produção de 5 segundos durante a temporada aberta.
- **Payload**: snapshot atualizado, incluindo a quantidade produzida no ciclo,
  `nivel_moinho` e `producao`.
- **Regra**: usa o nível vigente quando o ciclo é executado.

### `operacao.recusada`

- **Direção**: servidor → somente o socket solicitante.
- **Payload**: `motivo` textual e causa do pedido; nenhuma alteração do estado
  global.

## Consistência

- Validar e efetuar o débito/avanço antes de qualquer `await` para que pedidos
  concorrentes não gastem o mesmo saldo nem ultrapassem o nível 5.
- O cliente não calcula custo nem altera o nível ou saldo localmente; atualiza
  os dados recebidos pelo listener e pelo snapshot inicial.
- A conclusão de uma obra não emite bônus de farinha nem modifica a taxa.
