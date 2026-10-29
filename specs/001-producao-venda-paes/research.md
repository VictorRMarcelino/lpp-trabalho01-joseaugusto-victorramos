# Research: Produção e venda de pães

## Decisões

### Preservar o fluxo atual de eventos

- **Decision**: Usar `socketio.AsyncServer` como autoridade de estado; receber pedidos
  nomeados do cliente, validar e reservar antes do primeiro `await`, emitir fatos
  através do helper de estado existente e manter `ouvir()`/`pedir()` no cliente.
- **Rationale**: O servidor já usa esse fluxo em conexão, construção, temporizadores e
  recusas; o cliente registra e reage a cada fato pelo mesmo caminho.
- **Alternatives considered**: Criar API REST, separar frontend/backend ou adicionar
  uma camada de eventos. Todas alterariam a arquitetura sem necessidade funcional.
- **References**: [python-socketio server documentation](https://python-socketio.readthedocs.io/en/stable/server.html);
  [python-socketio AsyncServer API](https://python-socketio.readthedocs.io/en/stable/api_server.html#socketio.AsyncServer.start_background_task);
  [Socket.IO client API](https://socket.io/docs/v4/client-api/).

### Representar e cronometrar cada pão no servidor

- **Decision**: Manter pães prontos como registros individuais com identificador,
  estado e valor em centavos; manter produções pendentes separadas como reservas de
  pão, padeiro, forno e farinha. Usar tempo monotônico do processo como referência
  interna e derivar estado/valor da hora de conclusão.
- **Rationale**: A venda e o envelhecimento dependem do valor de cada item, enquanto
  os limites e a concorrência dependem da soma de pães prontos e reservados. Derivar
  o preço por intervalos completos evita erro acumulado de decrementos periódicos;
  centavos inteiros evitam imprecisão de ponto flutuante.
- **Alternatives considered**: Manter apenas um contador de pães não representa idade
  ou preço individual. Decrementar o preço a cada despertar do timer pode acumular
  atraso ou deriva. Usar hora monotônica enviada ao navegador exporia uma referência
  sem significado fora do processo.
- **Reference**: [Python `time.monotonic`](https://docs.python.org/3/library/time.html#time.monotonic).

### Propagar mudanças de idade e preço e sincronizar reconexões

- **Decision**: Um único agendador servidor verifica os próximos limites de frescor e
  valor, recalcula os pães afetados e emite fatos quando um pão fica amanhecido ou
  perde valor. Incluir a lista serializável de pães e o estado agregado no snapshot
  de conexão e nos fatos relevantes.
- **Rationale**: A interface precisa mostrar o valor correto mesmo sem venda, e uma
  conexão nova precisa receber estado atual, pois eventos Socket.IO perdidos não são
  automaticamente reproduzidos. Um agendador compartilhado evita criar uma tarefa
  independente para cada pão.
- **Alternatives considered**: Calcular apenas durante a venda deixa a interface
  desatualizada; tarefas independentes por pão repetem infraestrutura de timer e
  complexidade que não é necessária para o limite de seis itens.
- **References**: [Socket.IO delivery guarantees](https://socket.io/docs/v4/delivery-guarantees/);
  [python-socketio server documentation](https://python-socketio.readthedocs.io/en/stable/server.html).

### Manter estado compatível com o cliente atual

- **Decision**: Manter `estado.paes` como quantidade de pães prontos e acrescentar
  campos para moedas, reservas/em produção e detalhes individuais; preservar o helper
  `fato()` e a atualização Vue por `Object.assign`.
- **Rationale**: O painel atual lê `estado.paes` como número e espera snapshots
  contidos no payload de eventos. Um array em `paes` quebraria essa superfície.
- **Alternatives considered**: Trocar o significado de `estado.paes` por uma lista
  exigiria alterar todos os consumidores existentes e aumentaria o risco sem ganho.

### Validar sem adicionar infraestrutura de testes

- **Decision**: Usar a biblioteca padrão `unittest` para verificações automatizadas
  sem dependências e o percurso manual com duas abas para validação ponta a ponta.
- **Rationale**: Não há suíte de testes no repositório, `pytest` não está instalado e
  a implementação instalada contém `python-socketio`/`uvicorn`, sem `aiohttp`.
  Validações via navegador exercitam o mecanismo de eventos já usado pelo projeto.
- **Alternatives considered**: Adicionar uma framework ou dependências de teste não
  é necessário para especificar o comportamento e não foi solicitado.

## Riscos e decisões de comportamento

- Pedidos simultâneos devem verificar e reservar farinha, padeiro, forno e vaga no
  estoque antes de ceder o controle do loop assíncrono.
- Encerrar a temporada cancela produções pendentes, libera seus recursos e devolve
  10 sacas de farinha por produção; essa regra foi esclarecida na feature spec.
- Nenhum pão é vendido fora da temporada aberta. Uma tentativa sem pães prontos ou
  fora da fase aberta mantém o estado e usa a recusa individual existente.
- O estado continua limitado ao processo atual; reinício e execução multi-worker não
  são cobertos pelo escopo.
