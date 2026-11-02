# Implementation Plan: Limite de construções

**Branch**: `003-limite-construcoes` | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-limite-construcoes/spec.md`

## Summary

Limitar a seis o total de construções concluídas e obras em andamento. O servidor
deve recusar novos pedidos ao atingir esse total, sem alterar recursos, e avisar
somente o solicitante pelo evento de recusa existente. O cliente já apresenta
essa recusa e o mapa já limita a posição visual por meio dos lotes existentes;
portanto, não é necessário criar outro fluxo ou alterar o protocolo.

## Technical Context

**Language/Version**: Python existente (versão mínima não declarada); JavaScript/Vue existente no cliente.

**Primary Dependencies**: `python-socketio`, ASGI/Uvicorn; Phaser 3 e Vue já carregados no cliente.

**Storage**: Estado compartilhado em memória no dicionário `estado` do servidor.

**Testing**: `unittest` com `IsolatedAsyncioTestCase`; adicionar cobertura em `tests/`.

**Target Platform**: Servidor Python ASGI e clientes de navegador conectados por Socket.IO.

**Project Type**: Aplicação web em tempo real com servidor e cliente.

**Performance Goals**: A checagem do limite ocorre durante o tratamento existente do pedido, sem espera adicional ou novo ciclo de rede.

**Constraints**: O servidor continua autoritativo; manter o limite de seis, os eventos existentes e recusas direcionadas somente ao solicitante. O total conta `concluidas + em_obra`.

**Scale/Scope**: Uma vila compartilhada e até seis construções somando concluídas e em andamento; mudanças limitadas à validação do pedido e seus testes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Specification Fidelity**: PASS — aplicar o máximo de seis construções e o aviso ao solicitante descritos na especificação da feature e em `docs/especificacao.md`.
- **Architectural Continuity**: PASS — reutilizar o estado em memória, o handler Socket.IO, `operacao.recusada`, os listeners do cliente e a suíte `unittest` existentes.
- **Approved Technology Stack**: PASS — nenhuma linguagem, dependência ou serviço novo.
- **Server-Authoritative Event Model**: PASS — o servidor valida e atualiza o estado; recusas são enviadas somente ao solicitante.
- **Verifiable Business Rules**: PASS — cobrir estados de limite, preservação de recursos e concorrência por testes reproduzíveis.
- **Gate result**: PASS. Nenhuma violação requer exceção.

## Phase 0: Research

Concluído em [research.md](research.md). Não há decisões de tecnologia ou
requisitos funcionais pendentes de esclarecimento.

## Phase 1: Design & Contracts

- Modelo de estado e invariantes: [data-model.md](data-model.md).
- Contrato de eventos Socket.IO existente e comportamento da recusa:
  [contracts/socketio-events.md](contracts/socketio-events.md).
- Verificação manual e automatizada: [quickstart.md](quickstart.md).
- Gate após desenho: PASS — o desenho preserva a autoridade do servidor, o
  protocolo vigente e as responsabilidades existentes do cliente.

## Project Structure

### Documentation (this feature)

```text
specs/003-limite-construcoes/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── socketio-events.md
└── tasks.md
```

### Source Code (repository root)

```text
server.py                 # validação autoritativa de construção
client/
└── index.html            # listener e exibição de operacao.recusada existentes
tests/
└── test_server_construction_limit.py
```

**Structure Decision**: Manter a estrutura atual de aplicação web. A regra fica
no handler de construção em `server.py`; os testes focados ficam em `tests/`.
O listener existente em `client/index.html` já mostra o motivo recebido e não
precisa de um novo evento ou controle visual.

## Complexity Tracking

Sem violações da Constituição; não se aplica.
