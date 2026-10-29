import copy
import itertools
import time

import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio, static_files={
    "/": "client/index.html",
    "/assets": "client/assets",      # mapa, tileset e sprites da vila
})

CUSTO = 50     # moedas por construção
TEMPO_OBRA = 8 # segundos até a obra terminar
INTERVALO = 5  # segundos entre as produções
CUSTO_PAO = 10
TEMPO_PRODUCAO_PAO = 4
VALOR_PAO_CENTAVOS = 500
QTD_MAX_PAO = 6
TEMPO_FRESCOR_PAO = 60
INTERVALO_DECRESCIMENTO_PAO = 10
PERDA_VALOR_PAO_CENTAVOS = 50
INTERVALO_VERIFICACAO_PAO = 1

estado = {
    "fase": "aguardando",     # aguardando -> aberta -> encerrada
    "farinhas": 150,
    "paes": 0,                # pães prontos
    "paes_em_producao": 0,
    "paes_itens": [],
    "producoes_paes": [],
    "paes_maximos": QTD_MAX_PAO,
    "padeiros": 0,       # ocupados agora
    "limite": 2,              # máximo de padeiros
    "producao": 10,           # farinhas produzidas a cada INTERVALO
    "intervalo": INTERVALO,
    "tempo_obra": TEMPO_OBRA,
    "custo": CUSTO,
    "concluidas": 0,
    "fornos_ocupados": 0,
    "em_obra": 0,
    "moedas": 50
}

jogadores = {}                # sid -> {"nome": ..., "papel": ...}
_moedas_centavos = 5000
_producao_ids = itertools.count(1)
_paes_em_andamento = {}
_instantes_conclusao_paes = {}
_agendador_envelhecimento_ativo = False


def _atualizar_paes(agora=None):
    """Recalcula idade e preço e retorna os fatos de envelhecimento ocorridos."""
    agora = time.monotonic() if agora is None else agora
    anteriores = {pao["id"]: pao for pao in estado["paes_itens"]}
    paes_atualizados = []
    transicoes = []

    for pao_id, concluido_em in _instantes_conclusao_paes.items():
        idade = max(0, agora - concluido_em)
        intervalos_desconto = max(
            0, int((idade - TEMPO_FRESCOR_PAO) // INTERVALO_DECRESCIMENTO_PAO)
        )
        pao = {
            "id": pao_id,
            "estado": "amanhecido" if idade >= TEMPO_FRESCOR_PAO else "fresco",
            "valor_centavos": max(
                0, VALOR_PAO_CENTAVOS - intervalos_desconto * PERDA_VALOR_PAO_CENTAVOS
            ),
            "idade_segundos": int(idade),
        }
        anterior = anteriores.get(pao_id)
        if anterior:
            if anterior["estado"] != pao["estado"]:
                transicoes.append(("pao.amanhecido", pao.copy()))
            if anterior["valor_centavos"] != pao["valor_centavos"]:
                transicoes.append(("pao.valor_reduzido", pao.copy()))
        paes_atualizados.append(pao)

    estado["paes_itens"] = paes_atualizados
    estado["paes"] = len(paes_atualizados)
    return transicoes


def _snapshot_transicoes(transicoes):
    """Captura snapshots imutáveis antes de qualquer await de emissão."""
    return [
        (evento, fato(evento, pao=pao))
        for evento, pao in transicoes
    ]


async def _emitir_transicoes(transicoes):
    for evento, dados in transicoes:
        await sio.emit(evento, dados)


def _proximo_limite_pao(concluido_em, agora):
    idade = max(0, agora - concluido_em)
    if idade < TEMPO_FRESCOR_PAO:
        return concluido_em + TEMPO_FRESCOR_PAO
    intervalos_desconto = int(
        (idade - TEMPO_FRESCOR_PAO) // INTERVALO_DECRESCIMENTO_PAO
    )
    valor_centavos = max(
        0,
        VALOR_PAO_CENTAVOS
        - intervalos_desconto * PERDA_VALOR_PAO_CENTAVOS,
    )
    if valor_centavos == 0:
        return None
    return (
        concluido_em
        + TEMPO_FRESCOR_PAO
        + (intervalos_desconto + 1) * INTERVALO_DECRESCIMENTO_PAO
    )


def _iniciar_agendador_envelhecimento():
    global _agendador_envelhecimento_ativo
    if not _agendador_envelhecimento_ativo:
        _agendador_envelhecimento_ativo = True
        sio.start_background_task(envelhecer_paes)


async def envelhecer_paes():
    global _agendador_envelhecimento_ativo
    try:
        while _instantes_conclusao_paes:
            if not _instantes_conclusao_paes:
                return

            agora = time.monotonic()
            limites = [
                _proximo_limite_pao(concluido_em, agora)
                for concluido_em in _instantes_conclusao_paes.values()
            ]
            limites = [limite for limite in limites if limite is not None]
            if not limites:
                return

            proximo_limite = min(limites)
            await sio.sleep(min(
                max(0, proximo_limite - time.monotonic()),
                INTERVALO_VERIFICACAO_PAO,
            ))
            transicoes = _snapshot_transicoes(_atualizar_paes())
            await _emitir_transicoes(transicoes)
    finally:
        _agendador_envelhecimento_ativo = False
        agora = time.monotonic()
        if any(
            _proximo_limite_pao(concluido_em, agora) is not None
            for concluido_em in _instantes_conclusao_paes.values()
        ):
            _iniciar_agendador_envelhecimento()

def fato(causa, **extras):
    """Monta o payload de um FATO: o estado atual, a CAUSA (o evento ou o
    temporizador que gerou o fato) e dados extras."""
    return {"estado": copy.deepcopy(estado), "causa": causa, **extras}

@sio.event
async def connect(sid, environ, auth):
    auth = auth or {}
    jogadores[sid] = {
        "nome": auth.get("nome", "Anônimo"),
        "papel": auth.get("papel", "jogador"),
    }
    # servidor -> UM cliente: entrega o estado atual
    transicoes = _snapshot_transicoes(_atualizar_paes())
    await _emitir_transicoes(transicoes)
    await sio.emit("estado.sincronizado", fato("conexao"), to=sid)

@sio.event
async def disconnect(sid):
    jogadores.pop(sid, None)


async def recusar(sid, motivo, causa):
    """Responde só a quem pediu."""
    await sio.emit("operacao.recusada", {"motivo": motivo, "causa": causa}, to=sid)

@sio.on("vila.abertura_solicitada")
async def abrir_vila(sid, dados=None):
    pedido = "vila.abertura_solicitada"
    if jogadores[sid]["papel"] != "mestre":
        await recusar(sid, "Só o Mestre pode abrir a temporada", pedido)
        return
    if estado["fase"] != "aguardando":
        await recusar(sid, "A temporada já foi aberta", pedido)
        return
    estado["fase"] = "aberta"
    sio.start_background_task(producao)          
    _iniciar_agendador_envelhecimento()
    await sio.emit("vila.iniciada", fato(pedido))


@sio.on("construcao.solicitada")
async def construir(sid, dados=None):
    global _moedas_centavos
    pedido = "construcao.solicitada"
    # Valide TUDO antes de alterar o estado e sem await no meio:
    # assim, dois pedidos simultâneos são decididos um de cada vez.
    if estado["fase"] != "aberta":
        motivo = "A temporada não está aberta"
    elif _moedas_centavos < CUSTO * 100:
        motivo = "Moedas insuficientes"
    elif estado["padeiros"] >= estado["limite"]:
        motivo = "Sem trabalhador livre"
    else:
        motivo = None

    if motivo:
        await recusar(sid, motivo, pedido)    # só quem pediu recebe
        return

    _moedas_centavos -= CUSTO * 100
    estado["moedas"] = _moedas_centavos / 100
    estado["padeiros"] += 1
    estado["em_obra"] += 1
    nome = jogadores[sid]["nome"]
    await sio.emit("construcao.iniciada", fato(pedido, por=nome))
    sio.start_background_task(obra, nome)  
    
async def producao():
    while estado["fase"] == "aberta":
        await sio.sleep(INTERVALO)
        if estado["fase"] != "aberta":
            break
        estado["farinhas"] += estado["producao"]
        await sio.emit("recurso.produzido", fato("temporizador"))


async def obra(nome):
    await sio.sleep(TEMPO_OBRA)
    if estado["fase"] != "aberta":
        return
    estado["padeiros"] -= 1
    estado["em_obra"] -= 1
    estado["concluidas"] += 1
    estado["producao"] += 5       # cada obra concluída aumenta a produção
    causa = "construcao.iniciada (temporizador)"
    await sio.emit("construcao.concluida", fato(causa, por=nome))


@sio.on("pao.produzir")
async def produzir_pao(sid, dados=None):
    pedido = "pao.produzir"
    if estado["fase"] != "aberta":
        motivo = "A temporada não está aberta"
    elif estado["farinhas"] < CUSTO_PAO:
        motivo = "Farinhas insuficientes"
    elif estado["padeiros"] >= estado["limite"]:
        motivo = "Sem trabalhador livre"
    elif estado["concluidas"] - estado["fornos_ocupados"] <= 0:
        motivo = "Sem forno livre"
    elif estado["paes"] + estado["paes_em_producao"] >= QTD_MAX_PAO:
        motivo = "Limite de pães atingido"
    else:
        motivo = None

    if motivo:
        await recusar(sid, motivo, pedido)
        return

    producao_id = next(_producao_ids)
    nome = jogadores.get(sid, {}).get("nome", "Anônimo")
    producao = {"id": producao_id, "por": nome}
    _paes_em_andamento[producao_id] = producao
    estado["producoes_paes"] = list(_paes_em_andamento.values())
    estado["farinhas"] -= CUSTO_PAO
    estado["paes_em_producao"] += 1
    estado["padeiros"] += 1
    estado["fornos_ocupados"] += 1
    sio.start_background_task(concluir_producao_pao, producao_id)
    await sio.emit(
        "pao.producao_iniciada",
        fato(pedido, pao_id=producao_id, por=nome),
    )


async def concluir_producao_pao(producao_id):
    await sio.sleep(TEMPO_PRODUCAO_PAO)
    producao = _paes_em_andamento.pop(producao_id, None)
    if producao is None or estado["fase"] != "aberta":
        return

    estado["producoes_paes"] = list(_paes_em_andamento.values())
    estado["paes_em_producao"] -= 1
    estado["padeiros"] -= 1
    estado["fornos_ocupados"] -= 1
    agora = time.monotonic()
    _instantes_conclusao_paes[producao_id] = agora
    _atualizar_paes(agora)
    _iniciar_agendador_envelhecimento()
    await sio.emit(
        "pao.produzido",
        fato(
            "pao.produzir (temporizador)",
            pao_id=producao_id,
            pao=next(p for p in estado["paes_itens"] if p["id"] == producao_id),
            por=producao["por"],
        ),
    )


@sio.on("pao.vender")
async def vender_paes(sid, dados=None):
    global _moedas_centavos
    pedido = "pao.vender"
    if estado["fase"] != "aberta":
        motivo = "A temporada não está aberta"
    elif estado["paes"] == 0:
        motivo = "Não há pães disponíveis para vender"
    else:
        motivo = None

    if motivo:
        await recusar(sid, motivo, pedido)
        return

    transicoes = _snapshot_transicoes(_atualizar_paes())
    pães_vendidos = copy.deepcopy(estado["paes_itens"])
    valor_total = sum(pao["valor_centavos"] for pao in pães_vendidos)
    _moedas_centavos += valor_total
    estado["moedas"] = _moedas_centavos / 100
    estado["paes_itens"] = []
    estado["paes"] = 0
    for pao in pães_vendidos:
        _instantes_conclusao_paes.pop(pao["id"], None)
    fato_venda = fato(
        pedido,
        quantidade=len(pães_vendidos),
        valor_total_centavos=valor_total,
    )

    await _emitir_transicoes(transicoes)
    await sio.emit("paes.vendidos", fato_venda)


@sio.on("vila.encerramento_solicitado")
async def encerrar_vila(sid, dados=None):
    pedido = "vila.encerramento_solicitado"
    if jogadores[sid]["papel"] != "mestre":
        await recusar(sid, "Só o Mestre pode encerrar a temporada", pedido)
        return
    if estado["fase"] != "aberta":
        await recusar(sid, "A temporada não está aberta", pedido)
        return
    estado["fase"] = "encerrada"
    producoes_canceladas = list(_paes_em_andamento.values())
    if producoes_canceladas:
        quantidade_cancelada = len(producoes_canceladas)
        estado["farinhas"] += quantidade_cancelada * CUSTO_PAO
        estado["padeiros"] -= quantidade_cancelada
        estado["fornos_ocupados"] -= quantidade_cancelada
        estado["paes_em_producao"] = 0
        estado["producoes_paes"] = []
        _paes_em_andamento.clear()
        await sio.emit(
            "paes.producao_cancelada",
            fato(
                pedido,
                paes_ids=[producao["id"] for producao in producoes_canceladas],
                farinhas_devolvidas=quantidade_cancelada * CUSTO_PAO,
            ),
        )
    await sio.emit("vila.encerrada", fato(pedido))
