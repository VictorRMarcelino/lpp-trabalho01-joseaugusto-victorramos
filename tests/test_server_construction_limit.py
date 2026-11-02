import asyncio
import copy
import unittest
from unittest.mock import AsyncMock, Mock, patch

import server


class ConstructionLimitTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.previous_state = copy.deepcopy(server.estado)
        self.previous_players = copy.deepcopy(server.jogadores)
        self.previous_coins = server._moedas_centavos

        server.estado.update({
            "fase": "aberta",
            "farinhas": 150,
            "padeiros": 0,
            "limite": 2,
            "concluidas": 0,
            "em_obra": 0,
            "moedas": 100,
        })
        server.jogadores.clear()
        server.jogadores.update({
            "one": {"nome": "Ada", "papel": "jogador"},
            "two": {"nome": "Lin", "papel": "jogador"},
        })
        server._moedas_centavos = 10000

        self.emit = AsyncMock()
        self.start_background_task = Mock()
        self.emit_patch = patch.object(server.sio, "emit", self.emit)
        self.task_patch = patch.object(
            server.sio, "start_background_task", self.start_background_task
        )
        self.emit_patch.start()
        self.task_patch.start()

    async def asyncTearDown(self):
        self.task_patch.stop()
        self.emit_patch.stop()
        server.estado.clear()
        server.estado.update(self.previous_state)
        server.jogadores.clear()
        server.jogadores.update(self.previous_players)
        server._moedas_centavos = self.previous_coins

    async def test_sixth_construction_is_accepted(self):
        server.estado["concluidas"] = 5

        await server.construir("one")

        self.assertEqual(server.estado["concluidas"] + server.estado["em_obra"], 6)
        self.assertEqual(server.estado["em_obra"], 1)
        self.assertEqual(server.estado["padeiros"], 1)
        self.assertEqual(server._moedas_centavos, 5000)
        self.emit.assert_awaited_once()
        self.assertEqual(self.emit.await_args.args[0], "construcao.iniciada")
        self.assertEqual(self.emit.await_args.kwargs, {})

    async def test_seventh_construction_is_refused_without_state_changes(self):
        server.estado.update({
            "concluidas": 6,
            "em_obra": 0,
            "padeiros": 0,
        })
        state_before = copy.deepcopy(server.estado)
        coins_before = server._moedas_centavos

        await server.construir("one")

        self.assertEqual(server.estado, state_before)
        self.assertEqual(server._moedas_centavos, coins_before)
        self.emit.assert_awaited_once_with(
            "operacao.recusada",
            {
                "motivo": "Limite de construções atingido",
                "causa": "construcao.solicitada",
            },
            to="one",
        )

    async def test_in_progress_construction_counts_toward_limit(self):
        server.estado.update({
            "concluidas": 5,
            "em_obra": 1,
            "padeiros": 1,
        })
        state_before = copy.deepcopy(server.estado)

        await server.construir("two")

        self.assertEqual(server.estado, state_before)
        self.emit.assert_awaited_once_with(
            "operacao.recusada",
            {
                "motivo": "Limite de construções atingido",
                "causa": "construcao.solicitada",
            },
            to="two",
        )

    async def test_concurrent_requests_for_last_slot_accept_only_one(self):
        server.estado["concluidas"] = 5

        await asyncio.gather(
            server.construir("one"),
            server.construir("two"),
        )

        self.assertEqual(server.estado["concluidas"] + server.estado["em_obra"], 6)
        self.assertEqual(server.estado["em_obra"], 1)
        self.assertEqual(server.estado["padeiros"], 1)
        self.assertEqual(server._moedas_centavos, 5000)

        started = [
            call for call in self.emit.await_args_list
            if call.args[0] == "construcao.iniciada"
        ]
        refused = [
            call for call in self.emit.await_args_list
            if call.args[0] == "operacao.recusada"
        ]
        self.assertEqual(len(started), 1)
        self.assertEqual(len(refused), 1)
        self.assertIn(refused[0].kwargs["to"], {"one", "two"})
        self.assertEqual(
            refused[0].args[1]["motivo"],
            "Limite de construções atingido",
        )
        self.assertEqual(
            refused[0].args[1]["causa"],
            "construcao.solicitada",
        )
