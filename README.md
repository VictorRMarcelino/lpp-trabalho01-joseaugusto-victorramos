# Vila em Tempo Real — Padaria

## Integrantes
- José Augusto Jacinto @joshe24
- Victor Ramos Marcelino @VictorRMarcelino

## Como instalar e executar
- Na primeira vez, execute os seguintes comandos para rodar o projeto:
-- python -m venv .venv
-- .venv\Scripts\activate
-- pip install -r requirements.txt
-- uvicorn server:app --reload

- Se for a segunda vez, rode apenas:
-- .venv\Scripts\activate
-- uvicorn server:app --reload

- No navegador, em dois navegadores diferentes, acesse a url: *http://localhost:8000*
-- Na primeira aba, insira um nome e entre como mestre. Já na outra, insira outro nome qualquer e entre como jogador.

## Como testar com duas abas
- Primeiro, abra o projeto e execute o servidor com o comando uvicorn server:app --reload.
- Abra duas abas do navegador e acesse http://localhost:8000 nas duas.
- Na primeira aba (Mestre):
-- Digite um nome e entre como Mestre.
-- Aguarde a tela da vila carregar.
-- O Mestre será responsável por iniciar a vila e acompanhar seu andamento.
- Na segunda aba (Jogador):
-- Digite outro nome e entre como Jogador.
-- Entre na mesma vila para acompanhar o que está acontecendo.
- Para testar a comunicação em tempo real:
-- Na aba do Mestre, inicie a vila.
-- Na aba do Jogador, observe se a vila foi iniciada também.
-- Faça algumas ações disponíveis no jogo, como construir, produzir recursos ou produzir e vender pães.
-- Observe se as mudanças aparecem nas duas abas sem precisar atualizar a página.
- Resultado esperado:
-- As duas abas devem mostrar as mesmas informações da vila. Quando o Mestre ou o Jogador realizar alguma ação, as mudanças devem ser atualizadas automaticamente para os dois, mostrando que a comunicação em tempo real está funcionando.


## Perguntas
1. Quais eventos o seu sistema emite e escuta?
- O sistema escuta eventos quando os jogadores realizam alguma ação, como iniciar a vila, construir, produzir pães ou vender recursos. Quando alguma dessas ações acontece, o servidor processa o pedido e envia eventos avisando os outros jogadores sobre o que mudou na vila.
2. Como o sistema sabe quando deve atualizar os outros jogadores?
- Sempre que um jogador faz alguma ação que muda alguma coisa na vila, o servidor atualiza as informações e avisa os outros jogadores automaticamente. Isso acontece através do Socket.IO, que permite que todos acompanhem as mudanças em tempo real, sem precisar atualizar a página. Algumas mudanças também acontecem automaticamente, como a produção de recursos e a conclusão das construções.
3. Que parte do código mostra claramente o uso do paradigma orientado a eventos?
- Isso aparece principalmente em três partes do projeto: no server.py, no HTML e no JavaScript.
No Python (server.py), usamos @sio.on() para receber os eventos dos jogadores e sio.emit() para enviar atualizações para todos.
No JavaScript, usamos os eventos do Socket.IO, como socket.on() para receber as atualizações do servidor e socket.emit() para enviar ações dos jogadores.
Já no HTML, temos os botões e elementos da página que permitem ao jogador realizar essas ações, como construir, produzir e vender pães.
Assim, quando o jogador clica em um botão, o JavaScript envia um evento para o servidor, que processa a ação e envia uma atualização para os outros jogadores. Isso mostra como o projeto utiliza a programação orientada a eventos.

## Uso de IA
### *Claude Code:* Geração das imagens extras para o visual.
### *Copilot:* Geração das specs para aplicação de novas implementações.


## Extras
- Adicionado sistema para evolução de nível do moinho que produz farinha(Max:5). Quanto maior o nível, mais farinha é produzida.
- Adicionado sistema de moedas, que são obtidas a partir da venda dos pães.
- Adicinado sistema de envelhecimento dos pães. Após 1 minuto depois de serem produzidos, se não forem vendidos, se tornam envelhecidos e perdem 0,5 centavos a cada 10 segundos.
- Personalidado mapa no estilo de padaria.