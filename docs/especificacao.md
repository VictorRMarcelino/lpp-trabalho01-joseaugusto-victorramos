# Especificação — Vila em Tempo Real: Padaria

**Integrante(s):** 
-- José Augusto Jacinto @joshe24
-- Victor Ramos Marcelino @VictorRMarcelino
**Tipo de vila (sorteio):** 
-- Padaria

## 1. Regras da vila

- **Recurso primário e recurso refinado:** Farinha → Pães
- **Construções da vila:** Moinho e Forno
- **Trabalhadores:** Padeiros
- **Custo de um pão:** 10 sacas de farinha
- **Limite de pães** 6
- **Valor por pão** 5
- **Custo da obra:** 50 moedas
- **Tempo da obra:** 8 segundos até a conclusão da construção
- **Tempo de produção do pão:** 4 segundos até o pão ser produzido por um padeiro em um forno livre
- **Limite de trabalhadores:** 2 padeiros ativos simultaneamente
- **Intervalo e quantidade da produção automática:** A cada 5 segundos, o moinho produz 10 sacas de farinha.
- **O que muda quando uma obra termina:** O canteiro de obras se transforma em uma construção funcional da padaria, o trabalhador retorna a ficar livre e a capacidade de produção de pães aumenta.
- **Pão amanhecido:** Ao completar 60 segundos sem venda desde o fim da produção, o pão se torna amanhecido. O primeiro desconto de 0,50 moeda ocorre após mais 10 segundos completos e se repete a cada 10 segundos; o valor mínimo é zero.
- **Encerramento:** Pães em produção são cancelados quando o Mestre encerra a temporada; padeiro, forno e vaga são liberados e as 10 sacas de farinha debitadas são devolvidas. Vendas e novas produções ficam bloqueadas fora da temporada aberta.

## 2. Eventos

| Evento | Emite | Recebe | O que muda no estado |
|---|---|---|---|
| `vila.iniciada` | Servidor | Todos | A fase da vila muda de "aguardando" para "aberta" e os temporizadores de produção são iniciados.
| `construcao.solicitada` | Jogador | Servidor | É um pedido de construção; nenhum estado é alterado diretamente neste momento.
| `construcao.iniciada` | Servidor | Todos | O custo de 50 moedas é debitado, um trabalhador é ocupado e o canteiro de obras surge na tela.
| `operacao.recusada` | Servidor | Só quem pediu | Nenhum estado global muda; apenas o cliente solicitante recebe o aviso de erro (ex: falta de farinha ou sem padeiros livres)
| `recurso.produzido` | Servidor | Todos | O estoque de farinha da padaria aumenta de acordo com a taxa de produção.
| `construcao.concluida` | Servidor | Todos | A obra passa de canteiro para construída, o trabalhador é liberado e a produção de pães/farinha é bonificada
| `vila.encerrada` | Servidor | Todos | A fase muda para "encerrada", parando a produção automática e bloqueando novas construções, produções de pão e vendas.
| `pao.produzir` | Jogador | Servidor | Pedido para produzir um pão; nenhum estado muda até ser validado.
| `pao.producao_iniciada` | Servidor | Todos | Debita 10 sacas de farinha e reserva um padeiro, um forno e uma vaga de pão.
| `pao.produzido` | Servidor | Todos | Após 4 segundos, conclui um pão fresco de 5 moedas e libera padeiro e forno.
| `pao.amanhecido` | Servidor | Todos | Aos 60 segundos desde a conclusão, muda o pão para amanhecido sem reduzir seu valor.
| `pao.valor_reduzido` | Servidor | Todos | A cada 10 segundos completos depois de amanhecer, reduz o valor em 0,50 moeda até zero.
| `pao.vender` | Jogador | Servidor | Pedido para vender todos os pães prontos durante uma temporada aberta.
| `paes.vendidos` | Servidor | Todos | Remove os pães prontos e adiciona ao saldo de moedas a soma dos valores atuais.
| `paes.producao_cancelada` | Servidor | Todos | Ao encerrar, cancela as produções pendentes, libera recursos e devolve a farinha.

## 3. Cenários de teste (Dado / Quando / Então, escritos com eventos)

### Recusa
Dado que a temporada da padaria está aberta e o estoque atual é de 20 sacas de farinha (abaixo do custo de 50), quando o jogador emite `construcao.solicitada`, então o servidor valida os recursos insuficientes e emite `operacao.recusada` apenas para o jogador solicitante, mantendo o estado da vila inalterado.

### Passagem do tempo
Dado que a temporada da padaria está aberta, quando o temporizador do servidor atinge o intervalo estipulado de 5 segundos, então o servidor atualiza o estoque somando a produção automática e emite o evento `recurso.produzido` para todos os jogadores.

### Disputa entre dois jogadores
Dado que a padaria possui apenas 1 vaga livre de trabalhador (padeiro), quando os jogadores A e B emitem `construcao.solicitada` exatamente ao mesmo tempo, então o servidor processa os pedidos sequencialmente, emitindo `construcao.iniciada` para o primeiro jogador que teve o pedido atendido e `operacao.recusada` (por falta de trabalhadores livres) para o segundo jogador.

### Produção de pão
Dado que a temporada está aberta, há 10 sacas de farinha, um padeiro e um forno livre e menos de seis pães prontos ou em produção, quando um jogador emite `pao.produzir`, então o servidor debita 10 sacas, reserva os recursos e emite `pao.producao_iniciada`; após 4 segundos emite `pao.produzido` com um pão fresco de 5 moedas e libera padeiro e forno. Sem farinha, padeiro, forno, vaga ou temporada aberta, o servidor emite `operacao.recusada` apenas ao solicitante sem alterar o estado.

### Venda de pães
Dado que a temporada está aberta e há pães prontos, quando um jogador emite `pao.vender`, então o servidor remove todos os pães prontos, soma seus valores atuais ao saldo e emite `paes.vendidos` para todos. Pães ainda em produção não são vendidos. Sem pães prontos ou fora da temporada aberta, a solicitação é recusada sem alteração do estado.

### Envelhecimento
Dado que um pão não foi vendido, quando completa 60 segundos desde o fim da produção, então o servidor emite `pao.amanhecido` sem reduzir o preço; aos 70 segundos e a cada 10 segundos completos subsequentes emite `pao.valor_reduzido` e retira 0,50 moeda, sem permitir valor negativo.

### Encerramento durante produção
Dado que há produções de pão em andamento, quando o Mestre emite `vila.encerramento_solicitado`, então o servidor as cancela, libera padeiros, fornos e vagas, devolve 10 sacas por produção e emite `paes.producao_cancelada` antes de `vila.encerrada`; nenhum pão cancelado é concluído.