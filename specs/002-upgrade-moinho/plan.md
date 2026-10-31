# Implementation Plan: Upgrade do moinho

**Branch**: `002-upgrade-moinho` | **Date**: 2026-10-31 | **Spec**:
[spec.md](./spec.md)

**Input**: Feature specification from
`/specs/002-upgrade-moinho/spec.md`

## Summary

Substituir o aumento de produção associado à conclusão de obras por um
aprimoramento explícito do moinho. O servidor Python continua como autoridade do
estado e valida o papel de Mestre, temporada, saldo e limite de nível antes de
debitar moedas e transmitir o novo estado via Socket.IO. O cliente Vue 3 apresenta
o nível, a produção atual e a ação exclusiva do Mestre; Phaser 3 e o mapa Tiled
permanecem integrados sem mudanças estruturais.

## Technical Context

**Language/Version**: Python 3 (o repositório não fixa uma versão mínima);
JavaScript no navegador.

**Primary Dependencies**: `python-socketio` e `uvicorn`; Vue 3, Socket.IO Client
4 e Phaser 3 carregados por CDN; Tiled para o mapa. Nenhuma dependência nova é
necessária.

**Storage**: Estado da vila em memória no processo servidor existente; nenhuma
persistência entre reinicializações.

**Testing**: `unittest` da biblioteca padrão, conforme a suíte existente em
`tests/test_server_bread.py`; validação manual do cliente em duas abas.

**Target Platform**: Servidor ASGI Python e navegadores compatíveis com a
interface Vue/JavaScript atual.

**Project Type**: Aplicação web de tempo real com servidor e cliente no mesmo
repositório.

**Performance Goals**: Preservar a produção automática a cada 5 segundos e
propagar cada transição aceita aos clientes conectados após sua ocorrência. O
projeto não define metas de latência ou volume de conexões.

**Constraints**: Preservar o estado compartilhado em `server.py`, os listeners e
controles em `client/index.html`, o modelo Socket.IO orientado a eventos e as
bibliotecas atuais. O moinho tem níveis inteiros de 1 a 5; o custo de avanço usa
o nível anterior multiplicado por 10; a produção é `5 + (5 × nível)` sacas a
cada 5 segundos. O início de temporada reinicia o moinho no nível 1. Concluir
uma obra não modifica a produção.

**Scale/Scope**: Uma vila compartilhada no processo atual, até cinco níveis do
moinho e os jogadores conectados a essa vila. O projeto não especifica
persistência nem execução distribuída em múltiplos processos.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Specification Fidelity**: PASS — `docs/especificacao.md` e a especificação
  da feature definem o nível inicial, custo, fórmula, limite, reinício por
  temporada e remoção do bônus por construção. A descrição antiga do evento de
  conclusão da obra foi alinhada ao novo comportamento.
- **Architectural Continuity**: PASS — mantém o estado em memória, o servidor
  autoritativo e os arquivos/padrões existentes; sem reorganização arquitetural.
- **Approved Technology Stack**: PASS — usa Vue 3, Python, JavaScript, Phaser 3
  e Tiled como solicitado, sem substituições ou novas dependências.
- **Server-Authoritative Event Model**: PASS — o cliente solicita; o servidor
  valida papel, temporada, moedas e limite, altera o estado uma única vez e
  transmite o fato aos clientes. Recusas são direcionadas ao solicitante.
- **Verifiable Business Rules**: PASS — testes cobrirão os cinco níveis e
  respectivos custos/produções, recusas, concorrência, reinício da temporada e
  ausência de bônus ao concluir obras; o guia inclui validação sincronizada em
  dois clientes.

No gate violations identified.

## Project Structure

### Documentation (this feature)

```text
specs/002-upgrade-moinho/
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
tests/
└── test_server_bread.py
```

**Structure Decision**: Preservar a estrutura única existente. Regras,
validações, temporizador e emissão dos fatos ficam em `server.py`; controles,
estado reativo, atualização da cena e listeners ficam em `client/index.html`.
Assets Phaser/Tiled e dependências permanecem inalterados. Os testes de unidade
do servidor ficam na suíte `tests/`.

## Complexity Tracking

Não há violações da constituição ou complexidade adicional a justificar.
