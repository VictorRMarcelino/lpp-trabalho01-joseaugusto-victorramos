# Tasks: Produção e venda de pães

**Input**: Design documents from
`/specs/001-producao-venda-paes/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/socketio-events.md`, `quickstart.md`

**Tests**: Não foram solicitados testes automatizados. As histórias incluem critérios
de teste independente e a fase final executa o roteiro manual reproduzível existente.

## Phase 1: Setup

**Purpose**: Sincronizar a especificação oficial do projeto com as decisões aprovadas
antes de alterar seu comportamento.

- [X] T001 Atualizar `docs/especificacao.md` com custo de 10 sacas, produção individual em 4 segundos, limite de seis pães, valor inicial de R$ 5,00, envelhecimento aos 60 segundos e primeira redução aos 70 segundos; documentar venda somente durante a temporada aberta, cancelamento e reembolso de produções ao encerrar e eventos/públicos definidos em `specs/001-producao-venda-paes/contracts/socketio-events.md`.

---

## Phase 2: Foundational

**Purpose**: Preparar o estado serializável e os dados por pão usados pelas três
histórias sem alterar a arquitetura servidor-autoritativo existente.

**⚠️ CRITICAL**: Concluir esta fase antes das histórias de usuário.

- [X] T002 Ampliar o estado e implementar registros individuais de pães e reservas de produção em `server.py`; manter `estado["paes"]` como contagem de prontos e aplicar as restrições do modelo literalmente: "`0 <= paes + paes_em_producao <= 6`", "`0 <= padeiros <= limite`", "`0 <= fornos_ocupados <= concluidas`", "o tamanho de `producoes_paes` corresponde a `paes_em_producao`" e "`valor_centavos` é inteiro, mínimo zero, inicializa em 500 ao concluir e perde 50 por cada intervalo completo de 10 segundos depois dos primeiros 60 segundos"; reservar padeiro/forno/farinha por produção, usar tempo monotônico interno e manter relógios e tarefas fora do snapshot cliente em `server.py`.
- [X] T003 Incluir cópias serializáveis de pães prontos e produções pendentes nos snapshots de `fato()` e `estado.sincronizado`, expondo moedas em reais, valores em centavos por pão e contagens consistentes sem compartilhar listas mutáveis entre snapshots em `server.py`.

**Checkpoint**: Modelo e snapshots compartilhados prontos; as histórias podem ser
implementadas pela sequência de dependências descrita abaixo.

---

## Phase 3: User Story 1 - Produzir pão (Priority: P1) 🎯 MVP

**Goal**: Permitir iniciar uma produção válida com farinha, padeiro, forno e vaga
disponíveis, concluí-la em quatro segundos e cancelar corretamente ao encerrar.

**Independent Test**: Com a temporada aberta, um forno concluído e recursos livres,
produzir um pão: 10 sacas são reservadas/debitadas, padeiro e forno ficam ocupados,
e um pão fresco de R$ 5,00 aparece após quatro segundos. Confirme também recusas sem
alteração de estado e o cancelamento com reembolso se a temporada encerrar antes do
término.

### Implementation for User Story 1

- [X] T004 [US1] Implement o pedido `pao.produzir` em `server.py`, validando temporada aberta, pelo menos 10 sacas, um padeiro livre, um forno concluído e livre e menos de seis itens entre prontos e em produção; validar e reservar antes do primeiro `await`, emitir `pao.producao_iniciada`, concluir após 4 segundos com pão fresco de 500 centavos e liberar padeiro/forno, ou enviar `operacao.recusada` só ao solicitante sem alterar estado.
- [X] T005 [US1] Integrar o encerramento em `server.py` com as reservas de produção de pães: cancelar cada tarefa pendente, liberar padeiro, forno e vaga, devolver 10 sacas por produção, impedir conclusão posterior e emitir fatos atualizados `paes.producao_cancelada` antes de `vila.encerrada`.
- [X] T006 [P] [US1] Adicionar o botão "Produzir pão", seu pedido `pao.produzir` e listeners dos fatos de início, conclusão, cancelamento e recusa em `client/index.html`; atualizar o painel usando o estado recebido do servidor e exibir os avisos no padrão existente.

**Checkpoint**: Produção individual concluída após quatro segundos; limites, recursos
e cancelamento no encerramento são visíveis e coerentes em clientes conectados.

---

## Phase 4: User Story 2 - Vender pães disponíveis (Priority: P1)

**Goal**: Vender todos os pães prontos durante uma temporada aberta e creditar a soma
dos valores atuais sem incluir produções pendentes.

**Independent Test**: Com pelo menos um pão pronto e a temporada aberta, vender e
confirmar que todos os prontos são removidos e o valor atual total é adicionado às
moedas em ambas as abas; confirmar recusas sem pão pronto ou fora da temporada.

### Implementation for User Story 2

- [X] T007 [P] [US2] Implement o pedido `pao.vender` em `server.py`; aceitar somente durante a fase `aberta` e com pães prontos, atualizar valores vencidos antes da venda, remover todos os pães prontos atomicamente, creditar a soma em centavos e emitir `paes.vendidos`; recusar sem alterar estado se não houver pão pronto ou a temporada não estiver aberta.
- [X] T008 [P] [US2] Adicionar o botão "Vender pães", habilitação conforme temporada aberta e existência de pão pronto, pedido `pao.vender` e listener de `paes.vendidos` em `client/index.html`; exibir saldo de moedas e atualizar o estoque somente por fatos do servidor.

**Checkpoint**: Venda converte todos e somente os pães prontos em moedas no estado
compartilhado; produções em andamento continuam reservadas.

---

## Phase 5: User Story 3 - Acompanhar frescor e valor (Priority: P2)

**Goal**: Exibir individualmente o estado e preço dos pães e propagar envelhecimento e
perda de valor mesmo quando não há novas ações de jogadores.

**Independent Test**: Produzir um pão e observar atualização sincronizada: fresco a
R$ 5,00 até 60 segundos, amanhecido aos 60 sem redução, R$ 4,50 aos 70 e reduções de
R$ 0,50 a cada 10 segundos completos até R$ 0,00.

### Implementation for User Story 3

- [X] T009 [P] [US3] Implement em `server.py` um único agendador de envelhecimento que aguarde o próximo limite de cada pão, derive estado/valor do relógio monotônico, emita `pao.amanhecido` aos 60 segundos e `pao.valor_reduzido` a cada 10 segundos completos subsequentes, limite o valor a zero, continue atualizando pães prontos mesmo após o encerramento e pare quando não houver mais pães com valor a atualizar.
- [X] T010 [P] [US3] Apresentar em `client/index.html` cada pão pronto com estado e valor, manter a lista sincronizada com `estado.sincronizado`, `pao.produzido`, `pao.amanhecido`, `pao.valor_reduzido` e `paes.vendidos`, e formatar valores monetários em reais sem calcular preços no cliente.

**Checkpoint**: Todos os clientes conectados exibem o mesmo estado e preço por pão,
inclusive durante períodos sem ações de jogador.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validar o comportamento integrado e preservar consistência do contrato.

- [X] T011 Criar testes `unittest` para reservas, recusas, concorrência, produção, venda, envelhecimento, reembolso ao encerrar e custo de construção em `tests/test_server_bread.py`; executar esses testes e os percursos de integração de `specs/001-producao-venda-paes/quickstart.md`, corrigindo divergências em `server.py`, `client/index.html` ou `docs/especificacao.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências; atualiza a fonte oficial dos requisitos.
- **Foundational (Phase 2)**: depende de T001 e bloqueia as histórias.
- **User Story 1 (Phase 3)**: depende de T002 e T003.
- **User Story 2 (Phase 4)**: depende da produção e do modelo de pão pronto da US1.
- **User Story 3 (Phase 5)**: depende de pães individuais produzidos pela US1; a
  sequência após US2 evita alterações concorrentes ao mesmo `server.py`.
- **Polish (Phase 6)**: depende da integração das três histórias.

### User Story Dependencies

- **US1 (P1)**: começa após a fase Foundational; MVP de produção.
- **US2 (P1)**: requer pães prontos produzidos pela US1.
- **US3 (P2)**: requer pães individuais da US1; suas mudanças de agendamento no
  servidor são feitas após a venda para evitar conflito de edição em `server.py`.

### Parallel Opportunities

- Na **US1**, T004 (servidor) e T006 (cliente) podem avançar em paralelo após a
  fundação, pois o contrato Socket.IO já está documentado. T005 depende de T004.
- Na **US2**, T007 (servidor) e T008 (cliente) podem avançar em paralelo após a US1,
  seguindo os eventos definidos no contrato.
- Na **US3**, T009 (servidor) e T010 (cliente) podem avançar em paralelo após a US2,
  usando os eventos e campos definidos no contrato e modelo.
- Nenhuma tarefa da fundação é paralela: T003 depende dos registros introduzidos
  por T002.

## Parallel Examples

### User Story 1

```text
Executar em paralelo após T003:
- T004 em server.py
- T006 em client/index.html
Depois executar T005 em server.py após T004.
```

### User Story 2

```text
Executar em paralelo após concluir US1:
- T007 em server.py
- T008 em client/index.html
```

### User Story 3

```text
Executar em paralelo após concluir US2:
- T009 em server.py
- T010 em client/index.html
```

## Implementation Strategy

### MVP First (User Story 1)

1. Concluir T001–T003 para alinhar a especificação e preparar o estado serializável.
2. Concluir T004–T006 para produzir pão, impor limites e cancelar/reembolsar no
   encerramento.
3. Validar o critério independente da US1 antes de avançar.

### Incremental Delivery

1. Entregar US1 como incremento de produção utilizável.
2. Adicionar US2 para venda de todos os pães prontos e crédito do valor atual.
3. Adicionar US3 para frescor e atualização periódica do valor.
4. Executar T011 e validar o roteiro ponta a ponta com duas sessões.
