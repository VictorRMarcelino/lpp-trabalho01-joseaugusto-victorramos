# Implementation Plan: Produção e venda de pães

**Branch**: `001-producao-venda-paes` | **Date**: 2026-10-28 | **Spec**:
[spec.md](./spec.md)

**Input**: Feature specification from
`/specs/001-producao-venda-paes/spec.md`

## Summary

Adicionar produção, acompanhamento e venda de pães no fluxo de eventos já existente.
O servidor Python continua como autoridade do estado compartilhado: valida e reserva
farinha, padeiros, fornos e vagas antes de ceder o controle, conclui produções após
quatro segundos, calcula idade e valor individualmente e transmite fatos Socket.IO.
O cliente Vue apresenta as ações e o estado recebido; a cena Phaser/Tiled permanece
integrada pelo padrão atual, sem substituição arquitetural ou nova dependência.

## Technical Context

**Language/Version**: Python 3.14.7 no ambiente local observado; o repositório não
declara versão mínima. JavaScript no navegador.

**Primary Dependencies**: `python-socketio` e `uvicorn`; Vue 3.5.13, Socket.IO
Client 4.7.5 e Phaser 3.90.0 carregados por CDN; mapa JSON criado com Tiled.

**Storage**: Estado compartilhado em memória no processo servidor existente; nenhuma
persistência ou recuperação após reinício está prevista.

**Testing**: O repositório não contém suíte ou framework de testes. Usar testes com
`unittest` da biblioteca padrão quando forem adicionados e validar integração em
navegadores com duas sessões Socket.IO.

**Target Platform**: Servidor ASGI Python e navegadores que executam a interface
Vue/JavaScript atual.

**Project Type**: Aplicação web de tempo real com servidor e cliente no mesmo
repositório.

**Performance Goals**: Respeitar os tempos de negócio de 4, 60 e 10 segundos e
propagar fatos de transição após sua ocorrência; não há meta de latência ou volume
de clientes definida pelo projeto.

**Constraints**: Preservar `server.py`, `client/index.html`, o estado em memória e os
eventos Socket.IO existentes. Produção somente em temporada aberta; até dois padeiros,
um forno livre por produção e seis pães entre prontos e em produção; venda bloqueada
fora da temporada aberta. Encerramento cancela produções pendentes, libera recursos
e devolve o custo de farinha.

**Scale/Scope**: Uma vila compartilhada e o limite funcional atual de seis pães; a
especificação não define implantação com múltiplos processos ou persistência.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Specification Fidelity**: PASS — quantidades, tempos, estados, recusas, venda e
  cancelamento no encerramento seguem a especificação da feature.
- **Architectural Continuity**: PASS — mantém o servidor autoritativo, o cliente
  orientado a eventos e os arquivos/padrões atuais; sem reorganização arquitetural.
- **Approved Technology Stack**: PASS — Python, Vue, JavaScript, Phaser 3 e Tiled;
  sem substituição tecnológica ou dependência nova.
- **Server-Authoritative Event Model**: PASS — comandos são pedidos Socket.IO; fatos
  com estado atualizado são emitidos pelo servidor para todos ou recusados apenas ao
  solicitante.
- **Verifiable Business Rules**: PASS — testes cobrem limites, concorrência, tempos,
  venda, valor mínimo e encerramento; guia inclui validação com dois clientes.

No gate violations identified.

## Project Structure

### Documentation (this feature)

```text
specs/001-producao-venda-paes/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── socketio-events.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
server.py
client/
├── index.html
└── assets/
    ├── vila.json
    ├── tileset-vila.png
    └── sprites-vila.png
docs/
└── especificacao.md
requirements.txt
```

**Structure Decision**: Manter a estrutura única existente: regras e fatos no
`server.py`; apresentação e listeners em `client/index.html`; assets Tiled/Phaser sem
alteração estrutural. A feature não introduz serviços, pacotes ou armazenamento novo.

## Complexity Tracking

Não há violações da constituição ou complexidade adicional a justificar.
