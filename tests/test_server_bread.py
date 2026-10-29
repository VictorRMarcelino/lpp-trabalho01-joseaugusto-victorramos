import asyncio
import copy
import itertools
import unittest
from unittest.mock import AsyncMock, Mock, patch

import server


class BreadProductionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        server.estado.update({
            "fase": "aberta",
            "farinhas": 150,
            "paes": 0,
            "paes_em_producao": 0,
            "paes_itens": [],
            "producoes_paes": [],
            "paes_maximos": server.QTD_MAX_PAO,
            "padeiros": 0,
            "limite": 2,
            "producao": 10,
            "intervalo": server.INTERVALO,
            "tempo_obra": server.TEMPO_OBRA,
            "custo": server.CUSTO,
            "concluidas": 0,
            "fornos_ocupados": 0,
            "em_obra": 0,
            "moedas": 50,
        })
        server.jogadores.clear()
        server._paes_em_andamento.clear()
        server._instantes_conclusao_paes.clear()
        server._moedas_centavos = 5000
        server._producao_ids = itertools.count(1)
        server._agendador_envelhecimento_ativo = False

        self.emit = AsyncMock()
        self.start_background_task = Mock()
        self.sleep = AsyncMock()
        self.patches = [
            patch.object(server.sio, "emit", self.emit),
            patch.object(
                server.sio, "start_background_task", self.start_background_task
            ),
            patch.object(server.sio, "sleep", self.sleep),
        ]
        for active_patch in self.patches:
            active_patch.start()

    async def asyncTearDown(self):
        for active_patch in reversed(self.patches):
            active_patch.stop()
        server._paes_em_andamento.clear()
        server._instantes_conclusao_paes.clear()
        server._agendador_envelhecimento_ativo = False

    async def test_production_reserves_then_completes_and_releases_resources(self):
        server.estado["farinhas"] = 20
        server.estado["concluidas"] = 1
        server.jogadores["player"] = {"nome": "Ada", "papel": "jogador"}

        await server.produzir_pao("player")

        self.assertEqual(server.estado["farinhas"], 10)
        self.assertEqual(server.estado["paes_em_producao"], 1)
        self.assertEqual(server.estado["padeiros"], 1)
        self.assertEqual(server.estado["fornos_ocupados"], 1)
        self.assertEqual(server.estado["paes"], 0)
        self.assertEqual(self.start_background_task.call_args.args[0],
                         server.concluir_producao_pao)

        with patch.object(server.time, "monotonic", return_value=100):
            await server.concluir_producao_pao(1)

        self.assertEqual(server.estado["paes"], 1)
        self.assertEqual(server.estado["paes_em_producao"], 0)
        self.assertEqual(server.estado["padeiros"], 0)
        self.assertEqual(server.estado["fornos_ocupados"], 0)
        self.assertEqual(server.estado["paes_itens"], [{
            "id": 1,
            "estado": "fresco",
            "valor_centavos": 500,
            "idade_segundos": 0,
        }])
        produzido = next(
            call for call in self.emit.await_args_list
            if call.args[0] == "pao.produzido"
        )
        payload = produzido.args[1]
        self.assertEqual(payload["pao"]["valor_centavos"], 500)
        self.assertEqual(payload["estado"]["paes"], 1)
        payload["estado"]["paes_itens"][0]["valor_centavos"] = 0
        self.assertEqual(server.estado["paes_itens"][0]["valor_centavos"], 500)

    async def test_invalid_production_is_rejected_without_state_change(self):
        server.estado["concluidas"] = 1
        server.estado["farinhas"] = 9
        before = copy.deepcopy(server.estado)

        await server.produzir_pao("player")

        self.assertEqual(server.estado, before)
        self.emit.assert_awaited_once_with(
            "operacao.recusada",
            {"motivo": "Farinhas insuficientes", "causa": "pao.produzir"},
            to="player",
        )

    async def test_production_requires_open_season_free_baker_oven_and_capacity(self):
        cases = [
            ("season", {"fase": "encerrada"}, "A temporada não está aberta"),
            ("baker", {"padeiros": server.estado["limite"]}, "Sem trabalhador livre"),
            ("oven", {"concluidas": 0}, "Sem forno livre"),
            ("capacity", {"paes": server.QTD_MAX_PAO}, "Limite de pães atingido"),
        ]
        for _, changes, expected_reason in cases:
            with self.subTest(reason=expected_reason):
                server.estado.update({
                    "fase": "aberta",
                    "farinhas": 20,
                    "paes": 0,
                    "paes_em_producao": 0,
                    "padeiros": 0,
                    "concluidas": 1,
                    "fornos_ocupados": 0,
                })
                server.estado.update(changes)
                before = copy.deepcopy(server.estado)
                self.emit.reset_mock()

                await server.produzir_pao("player")

                self.assertEqual(server.estado, before)
                self.emit.assert_awaited_once_with(
                    "operacao.recusada",
                    {"motivo": expected_reason, "causa": "pao.produzir"},
                    to="player",
                )

    async def test_concurrent_production_requests_cannot_reserve_one_oven_twice(self):
        server.estado["farinhas"] = 20
        server.estado["concluidas"] = 1
        server.jogadores.update({
            "one": {"nome": "Ada", "papel": "jogador"},
            "two": {"nome": "Lin", "papel": "jogador"},
        })

        await asyncio.gather(
            server.produzir_pao("one"),
            server.produzir_pao("two"),
        )

        self.assertEqual(server.estado["paes_em_producao"], 1)
        self.assertEqual(server.estado["padeiros"], 1)
        self.assertEqual(server.estado["fornos_ocupados"], 1)
        self.assertEqual(server.estado["farinhas"], 10)
        self.assertEqual(len(server._paes_em_andamento), 1)
        refusal = [
            call for call in self.emit.await_args_list
            if call.args[0] == "operacao.recusada"
        ]
        self.assertEqual(len(refusal), 1)

    async def test_sale_recalculates_bread_and_credits_exact_current_value(self):
        server.estado["paes_itens"] = [{
            "id": 1,
            "estado": "fresco",
            "valor_centavos": 500,
            "idade_segundos": 0,
        }]
        server.estado["paes"] = 1
        server._instantes_conclusao_paes[1] = 10

        with patch.object(server.time, "monotonic", return_value=80):
            await server.vender_paes("player")

        self.assertEqual(server.estado["paes"], 0)
        self.assertEqual(server.estado["paes_itens"], [])
        self.assertEqual(server.estado["moedas"], 54.5)
        self.assertEqual(server._instantes_conclusao_paes, {})
        self.assertEqual(
            [call.args[0] for call in self.emit.await_args_list],
            ["pao.amanhecido", "pao.valor_reduzido", "paes.vendidos"],
        )
        sale_payload = self.emit.await_args_list[-1].args[1]
        self.assertEqual(sale_payload["valor_total_centavos"], 450)
        self.assertEqual(sale_payload["estado"]["moedas"], 54.5)

    async def test_sale_is_rejected_without_ready_bread_or_outside_open_season(self):
        cases = [
            {"fase": "aberta", "paes": 0, "paes_itens": []},
            {
                "fase": "encerrada",
                "paes": 1,
                "paes_itens": [{
                    "id": 1,
                    "estado": "fresco",
                    "valor_centavos": 500,
                    "idade_segundos": 0,
                }],
            },
        ]
        for changes in cases:
            with self.subTest(phase=changes["fase"], breads=changes["paes"]):
                server.estado.update(changes)
                before = copy.deepcopy(server.estado)
                coins_before = server._moedas_centavos
                self.emit.reset_mock()

                await server.vender_paes("player")

                self.assertEqual(server.estado, before)
                self.assertEqual(server._moedas_centavos, coins_before)
                self.assertEqual(self.emit.await_args.args[0], "operacao.recusada")

    async def test_closing_season_refunds_and_cancels_pending_production(self):
        server.estado["farinhas"] = 20
        server.estado["concluidas"] = 1
        server.jogadores["player"] = {"nome": "Ada", "papel": "jogador"}
        server.jogadores["master"] = {"nome": "Mestre", "papel": "mestre"}
        await server.produzir_pao("player")
        self.emit.reset_mock()

        await server.encerrar_vila("master")
        await server.concluir_producao_pao(1)

        self.assertEqual(server.estado["fase"], "encerrada")
        self.assertEqual(server.estado["farinhas"], 20)
        self.assertEqual(server.estado["paes"], 0)
        self.assertEqual(server.estado["paes_em_producao"], 0)
        self.assertEqual(server.estado["padeiros"], 0)
        self.assertEqual(server.estado["fornos_ocupados"], 0)
        self.assertEqual(server._paes_em_andamento, {})
        self.assertEqual(
            [call.args[0] for call in self.emit.await_args_list],
            ["paes.producao_cancelada", "vila.encerrada"],
        )

    async def test_age_and_value_boundaries_are_independent(self):
        server.estado["paes_itens"] = [{
            "id": 1,
            "estado": "fresco",
            "valor_centavos": 500,
            "idade_segundos": 0,
        }]
        server._instantes_conclusao_paes[1] = 0

        transitions = server._atualizar_paes(60)
        self.assertEqual(server.estado["paes_itens"][0]["estado"], "amanhecido")
        self.assertEqual(server.estado["paes_itens"][0]["valor_centavos"], 500)
        self.assertEqual([name for name, _ in transitions], ["pao.amanhecido"])

        transitions = server._atualizar_paes(70)
        self.assertEqual(server.estado["paes_itens"][0]["valor_centavos"], 450)
        self.assertEqual([name for name, _ in transitions], ["pao.valor_reduzido"])

        server._atualizar_paes(200)
        self.assertEqual(server.estado["paes_itens"][0]["valor_centavos"], 0)

    async def test_construction_spends_coins_not_flour(self):
        server.estado["moedas"] = 50
        server._moedas_centavos = 5000
        server.jogadores["player"] = {"nome": "Ada", "papel": "jogador"}

        await server.construir("player")

        self.assertEqual(server.estado["moedas"], 0)
        self.assertEqual(server._moedas_centavos, 0)
        self.assertEqual(server.estado["farinhas"], 150)
        self.assertEqual(server.estado["padeiros"], 1)


if __name__ == "__main__":
    unittest.main()
