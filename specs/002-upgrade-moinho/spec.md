# Feature Specification: Upgrade do moinho

**Feature Branch**: `002-upgrade-moinho`

**Created**: 2026-10-30

**Status**: Draft

**Input**: User description: "Alterar o sistema de aumento da produção da farinha. Atualmente, após terminar uma obra/forno, a quantidade de farinha produzida por vez aumenta. No entanto, vamos alterar para que esse aumento seja feito em um nível de sistema de moinho. Ou seja, o moinho começa no nível 1 e vai até o 5 e, em cada nível, a produção de farinha aumenta. Apenas o mestre pode upar o moinho e, para isso, precisa gastar das moedas. O custo para subir o nível de moinho é o nível do moinho * 10. Os valores estão dispostos em docs/especificacao.md"

## Clarifications

### Session 2026-10-30

- Q: Quando uma temporada termina e outra começa, o nível do moinho deve voltar a 1 ou permanecer no nível alcançado? → A: O moinho volta ao nível 1 a cada nova temporada.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Aprimorar o moinho (Priority: P1)

Como Mestre, quero gastar moedas para aumentar o nível do moinho, para elevar a
produção automática de farinha da vila.

**Why this priority**: O aprimoramento passa a ser a forma controlada de aumentar
a produção de farinha, substituindo o aumento associado à conclusão de obras.

**Independent Test**: Com a temporada aberta, o moinho no nível 1 e pelo menos
10 moedas disponíveis, aprimorar o moinho e verificar o novo nível, o débito e
a produção do próximo ciclo.

**Acceptance Scenarios**:

1. **Given** uma vila recém-iniciada, temporada aberta, moinho no nível 1 e pelo
   menos 10 moedas, **When** o Mestre aprimora o moinho, **Then** o nível passa
   a 2, exatamente 10 moedas são debitadas, os próximos ciclos produzem 15 sacas
   de farinha a cada 5 segundos e todos os jogadores veem o nível e a produção
   atualizados, sem alteração dos ciclos já concluídos.
2. **Given** o moinho em um nível entre 1 e 4 e moedas suficientes,
   **When** o Mestre solicita um aprimoramento, **Then** o moinho sobe exatamente
   um nível, o custo debitado é o nível anterior multiplicado por 10 e a produção
   dos próximos ciclos corresponde a 5 + (5 × nível atual) sacas a cada 5 segundos.
3. **Given** uma construção concluída enquanto o moinho está em qualquer nível,
   **When** a obra termina, **Then** o nível do moinho e a quantidade de farinha
   produzida por ciclo permanecem inalterados.
4. **Given** uma temporada encerrada, um pedido feito por alguém que não é o
   Mestre, um saldo inferior ao custo do próximo nível, ou um moinho já no nível
   5, **When** o aprimoramento é solicitado, **Then** o pedido é recusado sem
   alterar o nível, as moedas ou a produção.
5. **Given** pedidos de aprimoramento simultâneos quando resta apenas um nível
   disponível, **When** ambos são processados, **Then** no máximo um é aceito e
   o moinho não ultrapassa o nível 5 nem sofre débito indevido.

### Edge Cases

- O moinho começa no nível 1; não é possível reduzi-lo abaixo desse nível.
- O nível do moinho é reiniciado para 1 quando uma nova temporada começa.
- O nível máximo é 5; pedidos adicionais são recusados sem débito.
- O custo usa o nível atual antes do aprimoramento: nível 1 para 2 custa 10
  moedas, nível 2 para 3 custa 20, nível 3 para 4 custa 30 e nível 4 para 5
  custa 40.
- Um saldo exatamente igual ao custo permite o aprimoramento e resulta em saldo
  zero; saldo inferior resulta em recusa sem alteração.
- A produção continua ocorrendo a cada 5 segundos; somente a quantidade por
  ciclo muda com o nível do moinho.
- A conclusão de uma obra não concede mais aumento de produção de farinha.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST iniciar cada vila com o moinho no nível 1.
- **FR-002**: O sistema MUST permitir níveis inteiros do moinho de 1 a 5,
  inclusive, e MUST recusar qualquer tentativa de ultrapassar esse intervalo.
- **FR-003**: Somente o Mestre MUST poder solicitar o aprimoramento do moinho.
- **FR-004**: Cada aprimoramento aceito MUST elevar o nível do moinho em
  exatamente um e debitar do saldo compartilhado de moedas o nível atual
  multiplicado por 10.
- **FR-005**: O sistema MUST aceitar o aprimoramento somente quando a temporada
  estiver aberta e o saldo disponível for suficiente para seu custo.
- **FR-006**: O sistema MUST produzir farinha automaticamente a cada 5 segundos,
  em quantidade de 5 + (5 × nível atual do moinho) sacas por ciclo.
- **FR-007**: Os ciclos de produção posteriores a um aprimoramento MUST usar a
  quantidade correspondente ao novo nível; ciclos já concluídos MUST permanecer
  inalterados.
- **FR-008**: A conclusão de uma obra MUST NOT alterar o nível do moinho nem
  bonificar a quantidade produzida por ciclo.
- **FR-009**: Um pedido recusado MUST deixar inalterados o nível do moinho, o
  saldo de moedas e a produção de farinha.
- **FR-010**: O sistema MUST manter o nível e a produção atualizados para os
  jogadores da vila após um aprimoramento aceito.
- **FR-011**: Ao iniciar uma nova temporada, o sistema MUST reiniciar o moinho
  no nível 1.

### Key Entities *(include if feature involves data)*

- **Moinho**: Nível atual, limitado de 1 a 5, que determina a produção automática
  de farinha.
- **Saldo de moedas da vila**: Moedas compartilhadas disponíveis para pagar o
  custo de um aprimoramento.
- **Ciclo de produção de farinha**: Ciclo automático de 5 segundos cuja
  quantidade depende do nível atual do moinho.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos níveis de 1 a 5, a quantidade por ciclo corresponde a
  5 + (5 × nível): 10, 15, 20, 25 e 30 sacas, respectivamente.
- **SC-002**: Em 100% dos aprimoramentos válidos, o moinho avança exatamente um
  nível e o saldo diminui exatamente pelo nível anterior multiplicado por 10.
- **SC-003**: Em 100% das tentativas de não Mestres, com moedas insuficientes ou
  no nível máximo, o pedido é recusado sem alteração do estado da vila.
- **SC-004**: Concluir uma obra não altera a quantidade de farinha produzida por
  ciclo em nenhum dos níveis do moinho.

## Assumptions

- Os aprimoramentos são permitidos somente durante uma temporada aberta, de
  acordo com as regras existentes para ações da vila.
- O pagamento usa o saldo compartilhado de moedas da vila.
- Cada temporada começa com o moinho no nível 1; aprimoramentos não persistem
  entre temporadas.
- O custo é calculado com base no nível atual antes do aprimoramento, conforme
  a regra “nível do moinho × 10” de `docs/especificacao.md`.
- A fórmula e o intervalo de produção definidos em `docs/especificacao.md`
  permanecem válidos; o nível atual determina a quantidade dos ciclos
  subsequentes.
