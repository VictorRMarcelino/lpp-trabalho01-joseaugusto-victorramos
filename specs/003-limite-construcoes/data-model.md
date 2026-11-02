# Data Model: Limite de construções

## Estado compartilhado da vila

O estado permanece no dicionário existente do servidor e nos snapshots enviados
nos fatos Socket.IO. Nenhum campo novo é necessário: o total de construções é
derivado dos contadores existentes.

| Campo | Tipo | Descrição e validação |
|---|---|---|
| `concluidas` | inteiro | Número de construções concluídas; não negativo. |
| `em_obra` | inteiro | Número de obras iniciadas ainda não concluídas; não negativo. |
| Total de construções | inteiro derivado | `concluidas + em_obra`; deve permanecer entre 0 e 6, inclusive. |
| `padeiros` | inteiro | Trabalhadores ocupados, inclusive os alocados a obras; não deve ser alterado por recusa de limite. |
| `moedas` | número | Saldo compartilhado; não deve ser debitado por recusa de limite. |

## Vaga de construção

- A vila possui seis vagas visuais, numeradas de forma implícita pela ordem de
  alocação usada pelo cliente.
- Uma obra em andamento reserva uma vaga desde `construcao.iniciada`.
- Ao concluir, a obra converte-se em construção concluída; a transição decrementa
  `em_obra` e incrementa `concluidas`, sem alterar o total.
- Uma nova solicitação só pode reservar uma vaga se o total atual for inferior
  a 6.

## Integridade e transições

- A validação da capacidade ocorre antes de qualquer débito de moedas ou reserva
  de trabalhador/obra.
- Ao aceitar uma solicitação, `em_obra` aumenta em um; o total aumenta em um.
- Ao concluir uma obra, `em_obra` diminui em um e `concluidas` aumenta em um; o
  total permanece constante.
- Ao recusar por limite, os contadores, saldo e demais recursos permanecem
  inalterados.
- As validações e a reserva da última vaga acontecem no handler do servidor sem
  espera assíncrona intermediária. Pedidos simultâneos não podem reservar a
  mesma vaga.
- O snapshot do evento de recusa mantém o formato vigente e é enviado apenas ao
  solicitante.
