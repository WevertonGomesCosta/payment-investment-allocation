from __future__ import annotations

import unittest
from dataclasses import dataclass
from datetime import date, timedelta

from nucleo.estado_economico_canonico import construir_estado_economico_canonico


@dataclass
class EstadoFake:
    data_referencia: date
    inventario_temporal: list[dict]
    fontes_temporais: list[dict]
    recebidos_temporais: list[dict]
    switching_temporal_realizado: list[dict]


class EstadoEconomicoCanonicoFechamentoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data_ref = date(2026, 8, 4)

    def _estado(self, *, inventario=None, fontes=None, recebidos=None, switchings=None):
        return EstadoFake(
            data_referencia=self.data_ref,
            inventario_temporal=list(inventario or []),
            fontes_temporais=list(fontes or []),
            recebidos_temporais=list(recebidos or []),
            switching_temporal_realizado=list(switchings or []),
        )

    def test_lote_migrado_nao_mantem_valor_liquido_atual(self) -> None:
        resultado = construir_estado_economico_canonico(
            self._estado(
                inventario=[{
                    "lote_id": "destino-antigo",
                    "status_temporal": "migrado_por_switching",
                    "migrado_por_switching": True,
                    "sintetico_pos_switching": True,
                    "valor_liquido_disponivel_atual": 0.0,
                    "valor_liquido_migrado": 3119.0,
                }]
            )
        )
        unidade = resultado.unidades[0]
        self.assertTrue(resultado.auditoria.ok)
        self.assertEqual(unidade.estado_ciclo, "migrado_por_switching")
        self.assertEqual(unidade.valor_liquido_atual, 0.0)
        self.assertEqual(
            unidade.evidencias["valor_transferido_historico"],
            3119.0,
        )
        self.assertEqual(resultado.auditoria.resumo["valor_estados_encerrados"], 0.0)

    def test_cadeia_de_switching_conserva_apenas_destino_final(self) -> None:
        resultado = construir_estado_economico_canonico(
            self._estado(
                inventario=[
                    {
                        "lote_id": "A",
                        "status_temporal": "migrado_por_switching",
                        "migrado_por_switching": True,
                        "valor_liquido_disponivel_atual": 0.0,
                    },
                    {
                        "lote_id": "B",
                        "status_temporal": "migrado_por_switching",
                        "migrado_por_switching": True,
                        "sintetico_pos_switching": True,
                        "valor_liquido_disponivel_atual": 0.0,
                        "valor_liquido_migrado": 100.0,
                    },
                    {
                        "lote_id": "C",
                        "status_temporal": "ativo_pos_switching",
                        "sintetico_pos_switching": True,
                        "valor_liquido_disponivel_atual": 0.0,
                        "valor_liquido_migrado": 110.0,
                    },
                ],
                switchings=[
                    {
                        "switching_id": "sw1",
                        "lote_origem": "A",
                        "lote_destino": "B",
                        "data_switching": self.data_ref - timedelta(days=2),
                        "valor_liquido_migrado": 100.0,
                        "status_temporal": "materializado",
                    },
                    {
                        "switching_id": "sw2",
                        "lote_origem": "B",
                        "lote_destino": "C",
                        "data_switching": self.data_ref - timedelta(days=1),
                        "valor_liquido_migrado": 110.0,
                        "status_temporal": "materializado",
                    },
                ],
            )
        )
        valores = {
            unidade.identidade_origem: unidade.valor_liquido_atual
            for unidade in resultado.unidades
        }
        self.assertTrue(resultado.auditoria.ok, resultado.auditoria.bloqueios)
        self.assertEqual(valores["A"], 0.0)
        self.assertEqual(valores["B"], 0.0)
        self.assertEqual(valores["C"], 110.0)
        self.assertEqual(resultado.auditoria.resumo["valor_total_unidades_atuais"], 110.0)
        self.assertEqual(resultado.auditoria.resumo["valor_total_disponivel_canonico"], 110.0)
        self.assertEqual(resultado.auditoria.resumo["diferenca_conservacao_unidades_vivas"], 0.0)

    def test_id_de_recebido_ja_prefixado_nao_duplica_prefixo(self) -> None:
        resultado = construir_estado_economico_canonico(
            self._estado(
                recebidos=[{
                    "recebido_id": "recebido::salario-1",
                    "data_recebimento": self.data_ref,
                    "valor": 50.0,
                    "disponivel_na_referencia": True,
                }]
            )
        )
        self.assertTrue(resultado.auditoria.ok)
        self.assertEqual(resultado.unidades[0].unidade_id, "recebido::salario-1")

    def test_recebido_aplicado_e_usado_antes_tem_duas_evidencias(self) -> None:
        resultado = construir_estado_economico_canonico(
            self._estado(
                recebidos=[{
                    "recebido_id": "r1",
                    "data_recebimento": self.data_ref,
                    "data_aplicacao": self.data_ref,
                    "valor": 100.0,
                    "aplicado": True,
                    "usado_antes_da_aplicacao": True,
                    "disponivel_na_referencia": True,
                }]
            )
        )
        resumo = resultado.auditoria.resumo
        self.assertTrue(resultado.auditoria.ok)
        self.assertEqual(resumo["qtd_recebidos_aplicados_excluidos"], 1)
        self.assertEqual(
            resumo["qtd_recebidos_usados_antes_aplicacao_excluidos"],
            1,
        )


if __name__ == "__main__":
    unittest.main()
