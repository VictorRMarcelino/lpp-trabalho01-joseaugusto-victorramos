# Research: Limite de construções

## Contexto encontrado

- `server.py` guarda `concluidas` e `em_obra` no estado compartilhado. O handler
  de `construcao.solicitada` valida a temporada, o saldo e trabalhadores antes
  de debitar moedas e incrementar `em_obra`.
- O handler faz as validações e mutações sem um `await` intermediário, mantendo
  decisões concorrentes sequenciais no event loop assíncrono.
- `operacao.recusada` já envia `motivo` e `causa` somente ao socket solicitante.
- `client/index.html` já apresenta o motivo de `operacao.recusada` em um aviso e
  faz a cena tremer. As posições de obra são consumidas sequencialmente nos
  lotes visuais existentes.
- `tests/test_server_bread.py` demonstra o padrão de testes assíncronos, mocks de
  emissão Socket.IO e isolamento/reset do estado global.
- `docs/especificacao.md` já registra limite de seis obras. A especificação
  desta feature confirma que o total deve incluir obras em andamento e
  construções concluídas.

## Decisões

### Contar construções concluídas e obras em andamento

- **Decision**: Verificar `concluidas + em_obra` contra o limite 6 antes de
  debitar moedas, ocupar um padeiro ou iniciar uma nova obra.
- **Rationale**: Uma obra iniciada já ocupa uma das seis posições visuais; contar
  somente construções concluídas permitiria iniciar obras além da capacidade.
- **Alternatives considered**: Contar apenas `concluidas` ou depender da
  quantidade de lotes do cliente. A primeira ignora reservas em andamento; a
  segunda não protege o estado compartilhado e não cobre pedidos concorrentes.

### Reutilizar a recusa individual existente

- **Decision**: Recusar com `operacao.recusada`, causa
  `construcao.solicitada` e motivo legível que informa que o limite de
  construções foi atingido.
- **Rationale**: O evento já é destinado apenas ao solicitante e o cliente já
  mostra seu motivo; não é necessário introduzir protocolo nem UI paralelos.
- **Alternatives considered**: Criar evento ou notificação específica. Seria
  redundante e exigiria mudanças em clientes sem benefício funcional.

### Preservar a atomicidade do handler atual

- **Decision**: Incluir a checagem do limite no mesmo bloco de validação, antes
  de qualquer mutação e sem inserir espera assíncrona entre validação e reserva.
- **Rationale**: O handler existente já serializa naturalmente essas transições
  no event loop; depois que o primeiro pedido reserva a sexta vaga, o seguinte
  observará o total 6 e será recusado.
- **Alternatives considered**: Introduzir lock ou sincronização adicional. Não é
  necessário para o padrão atual de handler em processo único e aumentaria a
  complexidade sem alterar a garantia no escopo presente.

### Validar com testes de servidor e cliente existente

- **Decision**: Adicionar testes `unittest` cobrindo limite cheio, mistura de
  obras e construções concluídas, preservação de recursos e disputa concorrente
  pela última vaga; validar manualmente que o aviso aparece no navegador.
- **Rationale**: O projeto já usa `unittest`, e o cliente já processa o evento de
  recusa sem adaptação.
- **Alternatives considered**: Adicionar framework de teste novo ou mudar os
  listeners do cliente. Nenhuma necessidade foi identificada.

## Decisões não necessárias

- Não há persistência, serviço externo, novo campo de estado, novo evento ou
  mudança de custo/tempo envolvida.
- A ordem de prioridade entre a recusa por limite e outras validações não é
  requisito adicional da feature; os testes de recusa por limite devem usar
  estado de temporada, saldo e trabalhadores que de outra forma permitiriam a
  construção.
