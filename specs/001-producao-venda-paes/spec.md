# Feature Specification: Produção e venda de pães

**Feature Branch**: `001-producao-venda-paes`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "Adicione o sistema de produção de pães. Os pães são produzidos a partir das construções (Fornos). Para isso, deve adicionar o botão 'Produzir pão'. Ao clicar, verifica se há um padeiro e um forno livre. Se houver, debita da quantidade de farinha e realiza a produção do pão. Todo pão inicia com o valor de 5 reais. Pode se ter até 6 pães no total. Além disso, deve-se ter a opção de vender os pães. Ao clicar, debita todos os pães disponíveis e adiciona os valores dos pães na quantidade de moedas. Caso passe até 1 minuto sem que o pão seja vendido, ele se torna 'amanhecido'. No estado amanhecido, o pão passa a perder 0.5 de valor a cada 10 segundos."

## Clarifications

### Session 2026-10-28

- Q: Em que momento o pão deve se tornar amanhecido e começar a perder valor? → A: Fica amanhecido ao completar 60 segundos; o primeiro desconto de R$ 0,50 ocorre após mais 10 segundos completos.
- Q: Os jogadores podem vender pães prontos depois que o Mestre encerrar a temporada? → A: Não; encerrar a temporada bloqueia também a venda.
- Q: O que deve acontecer com um pão cuja produção já começou quando o Mestre encerra a temporada? → A: Cancelar a produção, liberar padeiro e forno e devolver as 10 sacas de farinha.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Produzir pão (Priority: P1)

Como jogador da padaria, quero iniciar a produção de um pão usando um padeiro e um
forno disponíveis, para transformar farinha em um produto que possa ser vendido.

**Why this priority**: A produção cria os pães necessários para a atividade de venda.

**Independent Test**: Com a temporada aberta, farinha suficiente, um padeiro livre e
um forno concluído e livre, iniciar a produção e confirmar o débito da farinha e que
um pão novo aparece após 4 segundos.

**Acceptance Scenarios**:

1. **Given** a temporada aberta, farinha suficiente, um padeiro livre, um forno livre
   e espaço para mais um pão, **When** o jogador escolhe "Produzir pão", **Then** o
   custo de 10 sacas de farinha é debitado, o padeiro e o forno ficam ocupados durante
   a produção e um pão de R$ 5,00 é adicionado após 4 segundos.
2. **Given** que não há farinha suficiente, **When** o jogador tenta produzir um pão,
   **Then** a solicitação é recusada, nenhum recurso é debitado e nenhum padeiro ou
   forno fica ocupado.
3. **Given** que não há padeiro livre ou forno livre, **When** o jogador tenta
   produzir um pão, **Then** a solicitação é recusada sem debitar farinha nem ocupar
   recursos.
4. **Given** que já existem 6 pães entre os disponíveis e os em produção, **When** o
   jogador tenta iniciar outra produção, **Then** a solicitação é recusada e o total
   não ultrapassa 6.
5. **Given** farinha e espaço para apenas uma nova produção, **When** dois jogadores
   solicitam produção simultaneamente, **Then** no máximo uma produção é aceita e a
   outra é recusada se os recursos disponíveis já tiverem sido reservados.

---

### User Story 2 - Vender pães disponíveis (Priority: P1)

Como jogador, quero vender todos os pães prontos de uma vez, para receber moedas pelo
valor atual de cada pão.

**Why this priority**: A venda converte a produção em moedas e permite que os
jogadores vejam o efeito da qualidade e do tempo de armazenamento no retorno.

**Independent Test**: Com pães prontos de diferentes idades, vender e verificar que
todos deixam o estoque e que as moedas aumentam pela soma de seus valores atuais.

**Acceptance Scenarios**:

1. **Given** uma temporada aberta e um ou mais pães prontos, **When** o jogador escolhe "Vender pães",
   **Then** todos os pães prontos são removidos do estoque e o saldo de moedas
   aumenta pela soma dos valores atuais desses pães.
2. **Given** uma temporada aberta sem pães prontos, **When** o jogador tenta vender pães,
   **Then** nenhuma moeda é adicionada e nenhuma produção em andamento é cancelada.
3. **Given** uma temporada aberta e uma produção em andamento, **When** o jogador escolhe
   "Vender pães", **Then** somente os pães já concluídos são vendidos.
4. **Given** uma temporada encerrada com pães prontos, **When** um jogador tenta
   vendê-los, **Then** a venda é recusada e os pães e o saldo de moedas permanecem
   inalterados.
5. **Given** uma ou mais produções de pão em andamento, **When** o Mestre encerra a
   temporada, **Then** cada produção é cancelada, o padeiro e o forno são liberados,
   a vaga de pão em produção é liberada e as 10 sacas de farinha de cada produção
   cancelada são devolvidas; nenhum pão dessas produções é concluído.

---

### User Story 3 - Acompanhar o frescor e o valor (Priority: P2)

Como jogador, quero acompanhar a idade e o valor atual de cada pão, para decidir
quando vender e entender o retorno recebido.

**Why this priority**: O envelhecimento cria urgência para vender sem impedir o uso
independente da produção e da venda.

**Independent Test**: Produzir um pão e observar seu estado e valor antes e depois
de 60 segundos e em intervalos subsequentes de 10 segundos.

**Acceptance Scenarios**:

1. **Given** um pão produzido há menos de 60 segundos, **When** seu estado e valor
   são consultados, **Then** ele é exibido como fresco e vale R$ 5,00.
2. **Given** um pão que não foi vendido ao completar 60 segundos desde sua produção,
   **When** esse prazo é atingido, **Then** ele passa a ser exibido como amanhecido.
3. **Given** um pão amanhecido, **When** passam 10 segundos, **Then** seu valor
   diminui R$ 0,50, sem ficar abaixo de R$ 0,00.
4. **Given** pães com idades diferentes, **When** um deles é vendido, **Then** cada
   pão vendido contribui com seu próprio valor atual, sem alterar o valor dos demais
   antes da venda.

### Edge Cases

- Uma produção não pode começar quando a temporada não está aberta.
- Produções simultâneas não podem reservar o mesmo padeiro ou forno, gastar a mesma
  farinha, nem ultrapassar o limite total de 6 pães.
- O limite de 6 considera tanto pães prontos quanto produções em andamento.
- Uma venda que ocorra antes de uma produção terminar não inclui aquele pão.
- Uma venda não pode ser realizada antes da abertura ou depois do encerramento da
  temporada; uma tentativa recusada não altera pães nem moedas.
- Ao encerrar a temporada, produções de pão em andamento são canceladas, seus padeiros
  e fornos são liberados e o custo de farinha é reembolsado.
- O envelhecimento e a perda de valor são controlados individualmente para cada pão;
  vender ou envelhecer um pão não reinicia o prazo dos outros.
- O valor de um pão pode chegar a R$ 0,00, mas nunca se torna negativo.
- Se não houver pão pronto, uma tentativa de venda não altera o saldo de moedas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST oferecer ao jogador a ação "Produzir pão".
- **FR-002**: O sistema MUST aceitar produção somente durante uma temporada aberta.
- **FR-003**: O sistema MUST permitir iniciar uma produção somente quando houver
  farinha suficiente, um padeiro livre, um forno concluído e livre, e espaço para o
  novo pão dentro do limite total.
- **FR-004**: Cada produção aceita MUST debitar 10 sacas de farinha e ocupar um
  padeiro e um forno até sua conclusão, sem permitir que outra solicitação reserve
  os mesmos recursos.
- **FR-005**: Cada produção aceita MUST concluir após 4 segundos e adicionar
  exatamente um pão ao estoque, com valor inicial de R$ 5,00.
- **FR-006**: O sistema MUST limitar a seis o número combinado de pães prontos e
  pães em produção.
- **FR-007**: Uma produção recusada MUST deixar inalterados farinha, estoque de
  pães, moedas, padeiros e fornos.
- **FR-008**: O sistema MUST exibir a ação "Vender pães" somente durante uma temporada
  aberta e quando houver pães prontos.
- **FR-009**: Durante uma temporada aberta, ao vender, o sistema MUST remover todos
  os pães prontos e adicionar ao saldo de moedas a soma dos valores atuais de cada
  um deles. Fora da temporada aberta, MUST recusar a venda sem alterar o estado.
- **FR-010**: Pães em produção MUST permanecer indisponíveis para venda até serem
  concluídos.
- **FR-011**: Cada pão MUST permanecer fresco pelos primeiros 60 segundos a partir da
  conclusão da produção e MUST passar ao estado amanhecido ao completar esse prazo.
- **FR-012**: Cada pão amanhecido MUST perder R$ 0,50 após cada intervalo completo de
  10 segundos nesse estado, começando 10 segundos após tornar-se amanhecido, sem que
  seu valor fique abaixo de R$ 0,00.
- **FR-013**: O sistema MUST apresentar a quantidade de farinha, moedas e pães
  prontos, além do estado e valor atual de cada pão.
- **FR-014**: Ao encerrar a temporada, o sistema MUST cancelar cada produção de pão
  em andamento, liberar o padeiro, o forno e a vaga reservada no limite de pães,
  devolver 10 sacas de farinha por produção cancelada e impedir que esses pães sejam
  concluídos.

### Key Entities

- **Pão**: Item produzido individualmente; possui estado (em produção, fresco ou
  amanhecido), valor atual e tempo desde a conclusão da produção.
- **Padeiro**: Trabalhador que pode estar livre ou ocupado em uma produção.
- **Forno**: Construção concluída que pode estar livre ou ocupada em uma produção.
- **Estoque da padaria**: Quantidades compartilhadas de farinha, pães prontos e
  moedas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos testes de produção válida, são debitadas exatamente
  10 sacas de farinha e um pão de R$ 5,00 fica disponível após 4 segundos.
- **SC-002**: Em 100% dos testes de restrição, nenhuma produção começa sem farinha,
  padeiro, forno ou espaço disponível, e nenhum estado é debitado indevidamente.
- **SC-003**: O estoque de pães prontos e em produção nunca excede 6, inclusive sob
  solicitações simultâneas.
- **SC-004**: Em 100% das vendas, todos e somente os pães prontos são removidos e o
  saldo de moedas aumenta pela soma de seus valores no momento da venda.
- **SC-005**: Cada pão não vendido fica amanhecido ao completar 60 segundos e perde
  R$ 0,50 aos 70 segundos e a cada 10 segundos completos subsequentes, até o mínimo
  de R$ 0,00.
- **SC-006**: Os jogadores conseguem identificar a quantidade de pães, seu estado e
  valor atual antes de decidir vender.
- **SC-007**: Em 100% dos encerramentos com produções em andamento, cada produção é
  cancelada, seus recursos são liberados, 10 sacas de farinha são devolvidas e nenhum
  pão cancelado aparece no estoque.

## Assumptions

- A especificação existente em `docs/especificacao.md` define o custo de 10 sacas de
  farinha e o tempo de produção de 4 segundos por pão; esses valores são mantidos.
- Cada ação produz exatamente um pão.
- Cada forno concluído processa no máximo um pão por vez; cada produção ocupa também
  um padeiro, respeitando o limite existente de dois padeiros ativos.
- O limite de seis reserva um lugar para cada produção em andamento, para que o
  resultado não exceda o máximo ao terminar.
- O minuto de frescor começa quando a produção termina. O pão torna-se amanhecido ao
  completar 60 segundos e a primeira redução de R$ 0,50 ocorre após os 10 segundos
  seguintes.
- Os valores monetários são representados em reais e centavos; o valor mínimo do pão
  é R$ 0,00.
- A venda afeta os pães prontos de todos os jogadores, por se tratar do estoque
  compartilhado da vila, e qualquer jogador conectado pode solicitar produção ou
  venda durante a temporada aberta.
- Depois que a temporada é encerrada, vendas e novas produções ficam bloqueadas.
