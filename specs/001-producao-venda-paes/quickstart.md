# Quickstart: validar produção e venda de pães

## Pré-requisitos

- Python e as dependências do projeto instaladas.
- Dois clientes de navegador para observar os mesmos fatos compartilhados.

## Iniciar a aplicação

Na raiz do repositório:

```powershell
pip install -r requirements.txt
uvicorn server:app --reload
```

Abra `http://127.0.0.1:8000` em duas abas. Entre como Mestre na primeira e como
Jogador na segunda. O Mestre abre a temporada.

## Validar o fluxo principal

1. Como Jogador, solicite a construção de um forno e aguarde os oito segundos da obra.
2. Confirme que ambas as abas receberam os eventos de início e conclusão da obra.
3. Com farinha, padeiro, forno e vaga disponíveis, use **Produzir pão**.
4. Confirme a dedução de 10 sacas e a reserva do padeiro/forno nas duas abas.
5. Após quatro segundos, confirme um pão fresco de R$ 5,00 disponível nas duas abas.
6. Aguarde 60 segundos desde a conclusão: o pão deve ficar amanhecido sem alteração de
   preço. Aos 70 segundos, seu preço deve passar a R$ 4,50; novas reduções ocorrem a
   cada 10 segundos completos até R$ 0,00.
7. Use **Vender pães** e confirme a remoção de todos os pães prontos e o crédito do
   valor atual em moedas nas duas abas.

## Validar restrições e concorrência

- Sem farinha, padeiro, forno ou vaga livre, produza e confirme a recusa individual,
  sem alteração do estado global.
- Com uma vaga, dois padeiros ou uma única unidade de farinha suficiente, envie
  pedidos de produção nas duas abas em sequência rápida. Confirme que no máximo um
  pedido reserva os recursos disponíveis.
- Tente vender sem pães prontos; nenhuma moeda deve ser creditada e produções em curso
  devem permanecer reservadas.
- Inicie uma produção e encerre a temporada antes de quatro segundos. Confirme o
  cancelamento, a liberação do padeiro/forno/vaga, a devolução das 10 sacas e a
  ausência de um pão concluído.
- Depois do encerramento, tente vender ou produzir. Ambas as ações devem ser
  recusadas sem alteração do estoque.
- Recarregue uma aba e reconecte; o snapshot deve mostrar o estado corrente e os
  detalhes dos pães.

## Resultado esperado

Os fatos aparecem no painel de eventos existente; ambos os clientes convergem para o
mesmo estoque, estado, valor e saldo de moedas. Os intervalos de negócio são medidos
a partir do término da produção, não do início.

O servidor mantém o estado em memória. Reiniciar o processo reinicia a vila, portanto
execute cada percurso de validação em uma sessão nova.

## Verificações automatizadas

Quando os testes da feature estiverem implementados, execute a suíte `unittest` do
repositório. O projeto não possui testes automatizados existentes nesta etapa.
