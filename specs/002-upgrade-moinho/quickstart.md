# Quickstart: validar o upgrade do moinho

## Pré-requisitos

- Python e dependências do projeto instalados (`pip install -r requirements.txt`).
- Dois clientes de navegador para confirmar a sincronização dos fatos.

## Iniciar e testar

Na raiz do repositório:

```powershell
uvicorn server:app --reload
```

Execute os testes automatizados:

```powershell
python -m unittest discover -s tests
```

Abra `http://127.0.0.1:8000` em duas abas, entre como Mestre na primeira e como
Jogador na segunda e inicie a temporada.

## Cenários de validação

1. Confirme que ambas as abas mostram nível 1 e produção de 10 sacas por ciclo
   de 5 segundos.
2. Com saldo suficiente, aprimore como Mestre. Confirme o débito de 10 moedas,
   nível 2, produção de 15 sacas no ciclo seguinte e estado sincronizado nas
   duas abas.
3. Continue os aprimoramentos válidos e confirme os custos 20, 30 e 40 moedas
   e as produções 20, 25 e 30 sacas, respectivamente.
4. No nível 5, solicite novo aprimoramento; confirme recusa individual e
   nenhuma alteração de moedas, nível ou produção.
5. Como Jogador, solicite um aprimoramento; confirme recusa apenas ao
   solicitante e nenhum débito.
6. Com saldo menor que o próximo custo, tente aprimorar e confirme que estado e
   saldo permanecem inalterados. Com saldo exatamente igual ao custo, confirme
   aceitação e saldo zero.
7. Conclua uma construção em uma sessão aberta e confirme que a obra não
   altera o nível nem a produção do moinho.
8. Recarregue uma aba e confirme que `estado.sincronizado` mostra o nível,
   produção e saldo atuais. Inicie uma nova sessão do servidor e confirme o
   moinho no nível 1.
9. Envie dois pedidos quando o moinho estiver no nível 4; confirme que apenas
   um é aceito e que o nível não excede 5.

## Resultado esperado

O servidor valida e aplica cada transição uma única vez; os clientes convergem
para o mesmo nível, saldo e taxa de produção a partir dos fatos recebidos.
Reiniciar o processo reinicia o estado em memória da vila.
