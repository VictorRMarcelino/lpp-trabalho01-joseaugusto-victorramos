# Quickstart: validar o limite de construções

## Pré-requisitos

- Python e dependências do projeto instalados (`pip install -r requirements.txt`).
- O servidor e duas conexões de navegador para verificar o aviso direcionado.

## Executar

Na raiz do repositório, rode os testes:

```powershell
python -m unittest discover -s tests
```

Para validar a interface manualmente, inicie o servidor:

```powershell
uvicorn server:app --reload
```

Abra a vila em duas abas, conecte um Mestre e um Jogador e inicie a temporada.
Para completar o limite manualmente, configure ou obtenha seis construções
concluídas e/ou obras em andamento, respeitando o saldo e trabalhadores exigidos
pelas regras existentes.

## Cenários de validação

1. Com cinco construções e recursos suficientes, solicite outra. Confirme que a
   sexta obra começa e o total passa a seis.
2. Com seis construções concluídas, solicite mais uma. Confirme a recusa com
   aviso de limite atingido e ausência de débito ou alteração dos contadores.
3. Com uma obra em andamento e cinco concluídas, solicite outra. Confirme que a
   tentativa é recusada; a obra em andamento conta para o limite.
4. Com cinco construções e dois clientes solicitando simultaneamente, confirme
   que somente uma solicitação é aceita e a outra recebe o aviso individual.
5. Observe ambas as abas: a recusa não altera as construções renderizadas para
   nenhum jogador.

## Resultado esperado

O total de construções concluídas e em andamento nunca ultrapassa seis. Uma
tentativa após ocupar todas as vagas não modifica o estado nem os recursos da
vila e apresenta o motivo de recusa somente a quem fez o pedido.
