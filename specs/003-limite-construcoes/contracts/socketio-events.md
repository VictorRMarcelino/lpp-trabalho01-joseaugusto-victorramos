# Contrato de eventos Socket.IO

O fluxo reutiliza os eventos existentes de solicitação, início de construção e
recusa. Os fatos aceitos seguem o padrão do projeto: snapshot `estado`,
`causa` e informações adicionais. A recusa é enviada apenas ao socket
solicitante.

## Pedido

### `construcao.solicitada`

- **Direção**: cliente → servidor.
- **Dados**: nenhum payload obrigatório para esta regra.
- **Validação de limite**: contar `estado.concluidas + estado.em_obra`; aceitar
  somente se o total for menor que 6.
- **Recusa por limite**: não debitar moedas, não ocupar trabalhador e não
  incrementar `em_obra`; emitir `operacao.recusada` com
  `causa: "construcao.solicitada"` e motivo que informa que o limite de
  construções foi atingido.
- **Aceitação**: manter o fluxo vigente de débito e reserva; emitir
  `construcao.iniciada` para todos os jogadores.
- **Concorrência**: validar e reservar a vaga sem espera assíncrona entre as
  operações; apenas um pedido pode ocupar a última vaga.

## Recusa

### `operacao.recusada`

- **Direção**: servidor → somente o solicitante.
- **Payload**:

  ```json
  {
    "motivo": "Limite de construções atingido",
    "causa": "construcao.solicitada"
  }
  ```

- **Efeito no cliente**: utilizar o listener existente, que mostra o motivo em
  um aviso. Não requer novo evento nem alteração do estado visual.

## Fatos de construção aceitos

### `construcao.iniciada`

- **Direção**: servidor → todos os jogadores.
- **Efeito**: snapshot reflete o incremento de `em_obra`; o cliente aloca o
  próximo lote visual para o canteiro.

### `construcao.concluida`

- **Direção**: servidor → todos os jogadores.
- **Efeito**: snapshot troca uma obra por uma construção concluída. A soma
  `concluidas + em_obra` não muda.
