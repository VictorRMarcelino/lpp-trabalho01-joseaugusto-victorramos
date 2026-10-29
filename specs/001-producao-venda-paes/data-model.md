# Data Model: Produção e venda de pães

## Estado compartilhado da vila

O estado permanece no dicionário existente do servidor e é serializado em fatos.
Campos atuais continuam com seu significado; novos campos refletem a feature.

| Campo | Tipo | Descrição e validação |
|---|---|---|
| `fase` | string | `aguardando`, `aberta` ou `encerrada`; produzir e vender só em `aberta`. |
| `farinhas` | inteiro | Estoque compartilhado; produção válida debita 10; cancelamento ao encerrar restitui 10. |
| `moedas` | número | Saldo compartilhado apresentado em reais com duas casas; cálculo interno em centavos inteiros. |
| `paes` | inteiro | Quantidade de pães concluídos e prontos, preservando o campo numérico atual. |
| `paes_em_producao` | inteiro | Quantidade de vagas reservadas em produções ainda não concluídas. |
| `paes_itens` | lista | Representação serializável de pães prontos com estado, valor e idade derivados. |
| `producoes_paes` | lista | Identificadores das produções pendentes para sincronizar clientes que conectam durante uma produção. |
| `padeiros` | inteiro | Trabalhadores ocupados, incluindo construções e produção de pães. |
| `limite` | inteiro | Capacidade existente de dois padeiros simultaneamente. |
| `concluidas` | inteiro | Fornos concluídos; uma produção ocupa um forno até terminar ou ser cancelada. |
| `fornos_ocupados` | inteiro | Fornos reservados por produções de pão; não pode exceder `concluidas`. |
| `paes_maximos` | inteiro | Limite de seis itens considerando `paes` + `paes_em_producao`. |

O estado serializado não inclui referências monotônicas de relógio nem objetos de
tarefa. O snapshot inclui pães prontos e reservas de produção, com valores derivados
e reproduzíveis no cliente.

## Pão

Cada pão é identificado individualmente e possui:

| Campo | Tipo | Descrição e validação |
|---|---|---|
| `id` | string/inteiro | Identificador único no processo servidor. |
| `estado` | enum | `em_producao`, `fresco` ou `amanhecido`. Pães em produção não são vendáveis. |
| `valor_centavos` | inteiro | Valor mínimo zero; inicializa em 500 ao concluir; perde 50 centavos por cada intervalo completo de 10 segundos depois dos primeiros 60 segundos. |
| `idade_segundos` | inteiro | Idade calculada pelo servidor a partir da conclusão; não define preço por contagem regressiva no cliente. |

O servidor mantém o instante monotônico da conclusão internamente e não o envia ao
cliente. Ao atingir 60 segundos, o estado muda para `amanhecido`; a primeira redução
de 50 centavos acontece aos 70 segundos e repete a cada 10 segundos, até zero.

## Produção pendente

Uma produção aceita reserva uma vaga de pão, um padeiro, um forno e 10 sacas de
farinha. A reserva existe por quatro segundos ou até o encerramento da temporada.
Ao concluir, a reserva se transforma em um pão fresco de 500 centavos e libera
padeiro e forno. Ao ser cancelada por encerramento, libera também a vaga e restitui a
farinha, sem criar um pão.

## Regras de integridade

- `0 <= paes + paes_em_producao <= 6`.
- `0 <= padeiros <= limite`, incluindo trabalhadores ocupados por construções.
- `0 <= fornos_ocupados <= concluidas`.
- O tamanho de `producoes_paes` corresponde a `paes_em_producao`.
- Cada produção em curso corresponde a uma vaga reservada, um padeiro e um forno.
- Uma ação inválida não modifica o estado compartilhado.
- Venda remove atomicamente todos os pães prontos e soma seus valores atuais às moedas;
  produções pendentes permanecem intocadas.
- Pães e saldo são compartilhados entre jogadores e existem apenas enquanto o
  processo mantém o estado atual.
