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


class EstadoEconomicoCanonicoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data_ref = date(2026, 7, 14)

    def _estado(self, *, inventario=None, fontes=None, recebidos=None, switchings=None):
        return EstadoFake(
            data_referencia=self.data_ref,
            inventario_temporal=list(inventario or []),
            fontes_temporais=list(fontes or []),
            recebidos_temporais=list(recebidos or []),
            switching_temporal_realizado=list(switchings or []),
        )

    def test_recebido_aplicado_nao_e_duplamente_contado_com_lote(self) -> None:
        estado = self._estado(
            inventario=[{
                "lote_id": "Lote 100 jul.",
                "status_temporal": "ativo",
                "disponibilidade": "disponivel",
                "data_aplicacao": self.data_ref,
                "valor_original": 100.0,
                "valor_liquido_disponivel_atual": 100.0,
            }],
            recebidos=[{
                "recebido_id": "salario-1",
                "data_recebimento": self.data_ref,
                "data_aplicacao": self.data_ref,
                "valor": 100.0,
                "aplicado": True,
                "disponivel_na_referencia": True,
                "lote_id_operacional_previsto": "Lote 100 jul.",
            }],
            fontes=[{
                "fonte_id": "salario-1",
                "valor_estimado": 100.0,
                "disponivel_na_referencia": True,
            }, {
                "fonte_id": "Lote 100 jul.",
                "valor_estimado": 100.0,
                "disponivel_na_referencia": True,
            }],
        )
        resultado = construir_estado_economico_canonico(estado)
        self.assertTrue(resultado.auditoria.ok)
        self.assertEqual(resultado.auditoria.resumo["valor_total_disponivel_canonico"], 100.0)
        self.assertEqual(resultado.auditoria.resumo["qtd_recebidos_aplicados_excluidos"], 1)
        self.assertEqual(len(resultado.fontes_disponiveis), 1)
        self.assertEqual(resultado.fontes_disponiveis[0]["fonte_id"], "Lote 100 jul.")

    def test_recebido_consumido_antes_da_aplicacao_nao_reaparece(self) -> None:
        estado = self._estado(recebidos=[{
            "recebido_id": "r1",
            "data_recebimento": self.data_ref,
            "valor": 250.0,
            "usado_antes_da_aplicacao": True,
            "disponivel_na_referencia": True,
        }])
        resultado = construir_estado_economico_canonico(estado)
        self.assertTrue(resultado.auditoria.ok)
        self.assertEqual(resultado.auditoria.resumo["valor_recebidos_disponiveis"], 0.0)
        self.assertEqual(resultado.auditoria.resumo["qtd_recebidos_consumidos_excluidos"], 1)

    def test_lote_zerado_nao_recupera_valor_original(self) -> None:
        estado = self._estado(
            inventario=[{
                "lote_id": "Lote zero",
                "status_temporal": "ativo",
                "disponibilidade": "disponivel",
                "valor_original": 1000.0,
                "valor_liquido_disponivel_atual": 0.0,
                "saldo_disponivel_atual": 0.0,
            }],
            fontes=[{
                "fonte_id": "Lote zero",
                "valor_estimado": 1000.0,
                "disponivel_na_referencia": True,
            }],
        )
        resultado = construir_estado_economico_canonico(estado)
        self.assertTrue(resultado.auditoria.ok)
        self.assertEqual(resultado.auditoria.resumo["valor_total_disponivel_canonico"], 0.0)
        self.assertEqual(resultado.auditoria.resumo["qtd_lotes_zerados_nao_ressuscitados"], 1)
        self.assertEqual(resultado.auditoria.resumo["qtd_fallbacks_valor_original_proibidos"], 1)

    def test_snapshot_futuro_nao_e_antecipado(self) -> None:
        estado = self._estado(
            inventario=[{
                "lote_id": "Lote A",
                "status_temporal": "ativo",
                "disponibilidade": "disponivel",
                "valor_liquido_disponivel_atual": 80.0,
            }],
            fontes=[{
                "fonte_id": "Lote A",
                "data_disponibilidade": self.data_ref + timedelta(days=10),
                "valor_estimado": 500.0,
                "disponivel_na_referencia": True,
            }],
        )
        resultado = construir_estado_economico_canonico(estado)
        self.assertTrue(resultado.auditoria.ok)
        self.assertEqual(resultado.auditoria.resumo["valor_total_disponivel_canonico"], 80.0)
        self.assertEqual(resultado.auditoria.resumo["qtd_snapshots_futuros_ignorados"], 1)

    def test_switching_remove_origem_e_materializa_destino_sem_criar_valor(self) -> None:
        estado = self._estado(
            inventario=[{
                "lote_id": "origem",
                "status_temporal": "ativo",
                "disponibilidade": "disponivel",
                "valor_liquido_disponivel_atual": 60.0,
            }],
            switchings=[{
                "switching_id": "sw1",
                "lote_origem": "origem",
                "lote_destino": "destino",
                "data_switching": self.data_ref,
                "data_aplicacao": self.data_ref,
                "valor_liquido_migrado": 60.0,
                "status_temporal": "materializado",
            }],
        )
        resultado = construir_estado_economico_canonico(estado)
        self.assertTrue(resultado.auditoria.ok)
        disponiveis = {f["fonte_id"]: f["valor_liquido_disponivel"] for f in resultado.fontes_disponiveis}
        self.assertNotIn("origem", disponiveis)
        self.assertEqual(disponiveis["destino"], 60.0)
        self.assertEqual(resultado.eventos_conservacao[0].diferenca_conservacao, 0.0)

    def test_lote_sintetico_usa_valor_migrado_sem_valor_original(self) -> None:
        estado = self._estado(inventario=[{
            "lote_id": "destino",
            "status_temporal": "ativo_pos_switching",
            "sintetico_pos_switching": True,
            "disponibilidade": "disponivel",
            "valor_liquido_disponivel_atual": 0.0,
            "valor_liquido_migrado": 75.0,
            "valor_original": 999.0,
        }])
        resultado = construir_estado_economico_canonico(estado)
        self.assertTrue(resultado.auditoria.ok)
        self.assertEqual(resultado.fontes_disponiveis[0]["valor_liquido_disponivel"], 75.0)

    def test_residual_explicito_de_recebido_pode_permanecer_disponivel(self) -> None:
        estado = self._estado(recebidos=[{
            "recebido_id": "r1",
            "data_recebimento": self.data_ref,
            "valor": 1000.0,
            "vinculado": True,
            "saldo_residual_recebido": 120.0,
            "disponivel_na_referencia": False,
        }])
        resultado = construir_estado_economico_canonico(estado)
        self.assertTrue(resultado.auditoria.ok)
        self.assertEqual(resultado.auditoria.resumo["valor_recebidos_disponiveis"], 120.0)
        self.assertEqual(resultado.fontes_disponiveis[0]["estado_ciclo"], "residual_disponivel")

    def test_duplicata_conflitante_bloqueia_estado(self) -> None:
        estado = self._estado(recebidos=[{
            "recebido_id": "r1",
            "data_recebimento": self.data_ref,
            "valor": 100.0,
            "disponivel_na_referencia": True,
        }, {
            "recebido_id": "r1",
            "data_recebimento": self.data_ref,
            "valor": 200.0,
            "disponivel_na_referencia": True,
        }])
        resultado = construir_estado_economico_canonico(estado)
        self.assertFalse(resultado.auditoria.ok)
        self.assertIn("recebido_duplicado_conflitante:r1", resultado.auditoria.bloqueios)

    def test_linhas_de_fonte_repetidas_nao_sao_somadas(self) -> None:
        estado = self._estado(
            inventario=[{
                "lote_id": "L1",
                "status_temporal": "ativo",
                "disponibilidade": "disponivel",
                "valor_liquido_disponivel_atual": 50.0,
            }],
            fontes=[{
                "fonte_id": "L1",
                "valor_estimado": 50.0,
                "disponivel_na_referencia": True,
            }, {
                "fonte_id": "L1",
                "valor_estimado": 50.0,
                "disponivel_na_referencia": True,
            }],
        )
        resultado = construir_estado_economico_canonico(estado)
        self.assertTrue(resultado.auditoria.ok)
        self.assertEqual(resultado.auditoria.resumo["valor_total_disponivel_canonico"], 50.0)
        self.assertEqual(resultado.auditoria.resumo["qtd_linhas_duplicadas_por_identidade"], 1)

    def test_fonte_materializada_fecha_com_total_canonico(self) -> None:
        estado = self._estado(
            inventario=[{
                "lote_id": "L1",
                "status_temporal": "ativo",
                "disponibilidade": "disponivel",
                "valor_liquido_disponivel_atual": 90.0,
            }],
            recebidos=[{
                "recebido_id": "R1",
                "data_recebimento": self.data_ref,
                "valor": 10.0,
                "disponivel_na_referencia": True,
            }],
        )
        resultado = construir_estado_economico_canonico(estado)
        self.assertTrue(resultado.auditoria.ok)
        self.assertEqual(resultado.auditoria.resumo["valor_total_disponivel_canonico"], 100.0)
        self.assertEqual(resultado.auditoria.resumo["diferenca_conservacao_fontes"], 0.0)


if __name__ == "__main__":
    unittest.main()
