# Data Model: Upgrade do moinho

## Estado compartilhado da vila

O estado permanece no dicionário global existente no servidor e é enviado nos
fatos Socket.IO. O nível do moinho é autoritativo; a taxa de produção é derivada
dele e precisa permanecer sincronizada para alimentar o temporizador existente.

| Campo | Tipo | Descrição e validação |
|---|---|---|
| `fase` | string | `aguardando`, `aberta` ou `encerrada`; aprimorar somente em `aberta`. |
| `nivel_moinho` | inteiro | Nível atual, entre 1 e 5; inicia em 1 em cada temporada. |
| `producao` | inteiro | Taxa atual derivada: `5 + (5 × nivel_moinho)` sacas por ciclo de 5 segundos. |
| `moedas` | número | Saldo compartilhado. O custo é o nível atual antes do avanço multiplicado por 10. |
| `farinhas` | inteiro | Estoque compartilhado incrementado pela quantidade `producao` a cada ciclo. |
| `concluidas` | inteiro | Fornos concluídos; conclusão não altera `nivel_moinho` nem `producao`. |

## Aprimoramento

Um pedido válido do Mestre, durante a temporada aberta, avança exatamente um
nível. Os custos para os avanços 1→2, 2→3, 3→4 e 4→5 são, respectivamente,
10, 20, 30 e 40 moedas.

| Estado anterior | Custo | Estado posterior | Produção por ciclo |
|---|---:|---|---:|
| Nível 1 | 10 | Nível 2 | 15 |
| Nível 2 | 20 | Nível 3 | 20 |
| Nível 3 | 30 | Nível 4 | 25 |
| Nível 4 | 40 | Nível 5 | 30 |

## Regras de integridade e transições

- `1 <= nivel_moinho <= 5`.
- `producao = 5 + (5 × nivel_moinho)`; produção inicial no nível 1 é 10 sacas.
- O custo do próximo avanço, quando o nível é inferior a 5, é
  `nivel_moinho × 10`.
- Só o papel Mestre pode aprimorar; o saldo precisa ser maior ou igual ao custo
  e a fase precisa ser `aberta`.
- Uma operação aceita debita o saldo e atualiza nível e taxa como uma transição
  indivisível antes de transmitir o fato.
- Uma recusa não altera nível, saldo, estoque de farinha ou taxa.
- No início de cada temporada, o nível volta a 1 e a taxa corresponde a 10.
- Concluir uma obra libera o trabalhador e atualiza a construção, sem mudar o
  nível nem a taxa do moinho.
- O snapshot do servidor inclui `nivel_moinho` e `producao`, para que conexões
  existentes e reconectadas exibam a mesma produção atual.
