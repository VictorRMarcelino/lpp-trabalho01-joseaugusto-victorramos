# Especificação — Vila em Tempo Real: Padaria

**Integrante(s):** 
-- José Augusto Jacinto @joshe24
-- Victor Ramos Marcelino @VictorRMarcelino
**Tipo de vila (sorteio):** 
-- Padaria

## 1. Regras da vila

- **Recurso primário e recurso refinado:** Farinha → Pães
- **Construções da vila:** Moinho, Forno e Vitrine
- **Trabalhadores:** Padeiros
- **Custo de uma construção:** 50 sacas de farinha
- **Tempo da obra:** 8 segundos até a conclusão da construção
- **Limite de trabalhadores:** 2 padeiros ativos simultaneamente
- **Intervalo e quantidade da produção automática:** A cada 5 segundos, o moinho produz 10 sacas de farinha
- **O que muda quando uma obra termina:** O canteiro de obras se transforma em uma construção funcional da padaria, o trabalhador retorna a ficar livre e a capacidade de produção de pães aumenta. Além disso, o pão amanhecido perde o valor caso não seja processado a tempo.

## 2. Eventos

| Evento | Emite | Recebe | O que muda no estado |
|---|---|---|---|
| `vila.iniciada` | Servidor | Todos | A fase da vila muda de "aguardando" para "aberta" e os temporizadores de produção são iniciados.
| `construcao.solicitada` | Jogador | Servidor | É um pedido de construção; nenhum estado é alterado diretamente neste momento.
| `construcao.iniciada` | Servidor | Todos | O custo em farinha é debitado, um trabalhador é ocupado e o canteiro de obras surge na tela.
| `operacao.recusada` | Servidor | Só quem pediu | Nenhum estado global muda; apenas o cliente solicitante recebe o aviso de erro (ex: falta de farinha ou sem padeiros livres)
| `recurso.produzido` | Servidor | Todos | O estoque de farinha da padaria aumenta de acordo com a taxa de produção.
| `construcao.concluida` | Servidor | Todos | A obra passa de canteiro para construída, o trabalhador é liberado e a produção de pães/farinha é bonificada
| `vila.encerrada` | Servidor | Todos | A fase da vila muda para "encerrada", parando a produção automática e bloqueando novas construções

## 3. Cenários de teste (Dado / Quando / Então, escritos com eventos)

### Recusa
Dado que a temporada da padaria está aberta e o estoque atual é de 20 sacas de farinha (abaixo do custo de 50), quando o jogador emite `construcao.solicitada`, então o servidor valida os recursos insuficientes e emite `operacao.recusada` apenas para o jogador solicitante, mantendo o estado da vila inalterado.

### Passagem do tempo
Dado que a temporada da padaria está aberta, quando o temporizador do servidor atinge o intervalo estipulado de 5 segundos, então o servidor atualiza o estoque somando a produção automática e emite o evento `recurso.produzido` para todos os jogadores.

### Disputa entre dois jogadores
Dado que a padaria possui apenas 1 vaga livre de trabalhador (padeiro), quando os jogadores A e B emitem `construcao.solicitada` exatamente ao mesmo tempo, então o servidor processa os pedidos sequencialmente, emitindo `construcao.iniciada` para o primeiro jogador que teve o pedido atendido e `operacao.recusada` (por falta de trabalhadores livres) para o segundo jogador.