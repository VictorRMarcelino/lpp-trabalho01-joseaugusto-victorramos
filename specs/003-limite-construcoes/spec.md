# Feature Specification: Limite de construções

**Feature Branch**: `003-limite-construcoes`

**Created**: 2026-11-02

**Status**: Draft

**Input**: User description: "Adicionar limite de construções. Hoje, o visual tem slot para até 6 construções. No entanto, se eu clicar para construir uma sétima, ele constrói outra em cima da primeira. Vamos limitar para que o máximo seja 6 construções no total e, se tentar construir outra, aparece um aviso que já atingiu o limite de construções."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Construir sem ultrapassar o limite (Priority: P1)

Como jogador, quero construir até seis construções na vila e receber um aviso ao
tentar construir outra, para que nenhuma construção existente seja substituída ou
se sobreponha.

**Why this priority**: Impedir a perda visual de uma construção existente é
necessário para que a vila permaneça legível e o limite de seis posições seja
respeitado.

**Independent Test**: Com a temporada aberta, concluir ou iniciar construções até
ocupar as seis posições e tentar iniciar mais uma; confirmar que as seis continuam
visíveis e que o jogador recebe o aviso de limite atingido.

**Acceptance Scenarios**:

1. **Given** uma temporada aberta e menos de seis construções entre concluídas e
   em andamento, **When** o jogador solicita uma construção, **Then** a solicitação
   pode ser aceita conforme as demais regras e o total não ultrapassa seis.
2. **Given** seis construções entre concluídas e em andamento, **When** o jogador
   solicita outra construção, **Then** a solicitação é recusada, as seis
   construções permanecem inalteradas e o jogador solicitante vê um aviso de que
   o limite de construções foi atingido.
3. **Given** cinco construções e duas solicitações simultâneas para a última vaga,
   **When** o servidor processa os pedidos, **Then** no máximo uma construção é
   iniciada e o outro solicitante recebe o aviso de limite atingido.
4. **Given** seis construções existentes, **When** uma nova solicitação é
   recusada por limite, **Then** nenhuma construção existente é removida,
   substituída ou sobreposta.

### Edge Cases

- O total inclui construções concluídas e obras ainda em andamento.
- Com exatamente cinco construções, uma nova construção pode ocupar a sexta vaga;
  com seis, qualquer solicitação adicional deve ser recusada.
- Solicitações concorrentes pela última vaga não podem fazer o total ultrapassar
  seis.
- Uma recusa por limite não altera construções existentes nem outros recursos da
  vila.
- Fora de uma temporada aberta, as regras existentes de encerramento continuam
  bloqueando novas construções.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST permitir no máximo seis construções no total na vila.
- **FR-002**: O total MUST incluir construções concluídas e obras em andamento.
- **FR-003**: O sistema MUST recusar uma solicitação de construção quando o total
  já for seis.
- **FR-004**: Ao recusar uma solicitação por limite, o sistema MUST avisar o
  jogador solicitante de que o limite de construções foi atingido.
- **FR-005**: Uma solicitação recusada por limite MUST NOT remover, substituir
  nem sobrepor construções existentes e MUST NOT alterar os recursos da vila.
- **FR-006**: O sistema MUST processar solicitações concorrentes de forma que
  apenas uma possa ocupar a última vaga e o total nunca ultrapasse seis.
- **FR-007**: A recusa por limite MUST deixar a vila em estado consistente para
  todos os jogadores.

### Key Entities *(include if feature involves data)*

- **Construção da vila**: Uma construção concluída ou uma obra em andamento que
  ocupa uma das seis vagas disponíveis.
- **Vaga de construção**: Uma das seis posições disponíveis para construções da
  vila; não pode ser ocupada por mais de uma construção.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% das tentativas válidas enquanto houver menos de seis
  construções, a vila aceita no máximo uma nova construção e permanece com até
  seis no total.
- **SC-002**: Em 100% das tentativas feitas com seis construções, nenhuma nova
  construção é iniciada e o solicitante recebe o aviso de limite atingido.
- **SC-003**: Em 100% das tentativas recusadas por limite, as seis construções
  existentes e os recursos da vila permanecem inalterados.
- **SC-004**: Em 100% das disputas simultâneas pela última vaga, no máximo uma
  solicitação é aceita e todos os jogadores observam um total de até seis
  construções.

## Assumptions

- O limite aplica-se ao total combinado de obras em andamento e construções
  concluídas, conforme a capacidade visual de seis posições e a regra de limite
  de obras já registrada em `docs/especificacao.md`.
- A mensagem de recusa é apresentada ao jogador que solicitou a construção; as
  demais regras de validação e de encerramento da temporada permanecem vigentes.
- Este escopo não altera os tipos, custos, tempos ou demais regras de construção.
