from __future__ import annotations

import unittest
from datetime import date

from nucleo.estado_temporal_inicial import EstadoTemporalInicial
from nucleo.motor_temporal_conjunto import construir_resultado_motor_temporal_conjunto


class MotorTemporalFuncionalTest(unittest.TestCase):
    def _estado(
        self,
        *,
        valor_pagamento: float = 0.0,
        saldo_fonte: float = 1000.0,
        retorno_origem: float = 0.05,
        retorno_destino: float = 0.10,
    ) -> EstadoTemporalInicial:
        data_ref = date(2026, 1, 1)
        pagamentos = []
        if valor_pagamento > 0:
            pagamentos.append(
                {
                    "pagamento_id": "p1",
                    "data": data_ref,
                    "valor": valor_pagamento,
                    "pago": False,
                    "fonte_a_decidir": True,
                    "obrigacao_temporal": True,
                }
            )
        fontes = []
        if saldo_fonte > 0:
            fontes.append(
                {
                    "fonte_id": "f1",
                    "lote_id": "f1",
                    "valor_liquido_disponivel": saldo_fonte,
                    "valor_estimado": saldo_fonte,
                    "data_disponibilidade": data_ref,
                    "status_temporal": "disponivel",
                    "disponivel_na_referencia": True,
                    "produto": "produto origem",
                    "retorno_anual_proxy": retorno_origem,
                    "liquidez_dias": 0,
                    "data_base_fiscal": date(2025, 1, 1),
                    "isento_ir": False,
                    "regra_iof": "regressiva_30d",
                }
            )
        return EstadoTemporalInicial(
            data_referencia=data_ref,
            calendario_financeiro=None,
            cache_cdi=None,
            inventario_temporal=[],
            fontes_temporais=fontes,
            recebidos_temporais=[],
            pagamentos_temporais=pagamentos,
            switching_temporal_realizado=[],
            restricoes_temporais=[],
            elegibilidades_preliminares=[],
            auditoria_temporal={"ok": True, "bloqueios": [], "resumo": {}},
            metadados={
                "etapa": "4",
                "artefato": "EstadoTemporalInicial",
                "data_horizonte_terminal": date(2027, 1, 1),
                "destinos_switching": [
                    {
                        "rank_destino": 1,
                        "nome": "produto destino",
                        "retorno_anual_proxy": retorno_destino,
                        "liquidez_dias": 0,
                        "carencia_dias": 0,
                        "aplicacao_minima": 1.0,
                        "aplicacao_maxima": 0.0,
                        "elegivel_switch_in": True,
                        "isento_ir": False,
                        "regra_iof": "regressiva_30d",
                    }
                ],
            },
        )

    def test_dia_sem_pagamento_com_switching_vantajoso(self) -> None:
        resultado = construir_resultado_motor_temporal_conjunto(self._estado())
        data_ref = date(2026, 1, 1)
        tipos = {
            pacote.tipo_pacote
            for pacote in resultado.pacotes_temporais_candidatos_por_data[data_ref]
        }
        self.assertEqual(tipos, {"no_action", "switch_only"})
        self.assertEqual(resultado.pacote_vencedor_por_data[data_ref].tipo_pacote, "switch_only")
        self.assertTrue(resultado.pronto_para_etapa6)
        self.assertTrue(resultado.metadados["argmax_comprovado"])

    def test_dia_com_pagamento_compara_tres_trajetorias(self) -> None:
        resultado = construir_resultado_motor_temporal_conjunto(
            self._estado(valor_pagamento=100.0)
        )
        data_ref = date(2026, 1, 1)
        tipos = {
            pacote.tipo_pacote
            for pacote in resultado.pacotes_temporais_candidatos_por_data[data_ref]
        }
        self.assertEqual(
            tipos,
            {"pay_only", "switch_then_pay", "pay_then_switch"},
        )
        self.assertEqual(
            resultado.pacote_vencedor_por_data[data_ref].tipo_pacote,
            "pay_then_switch",
        )
        self.assertEqual(len(resultado.obrigacoes_cobertas_temporalmente), 1)
        self.assertTrue(resultado.pronto_para_etapa6)

    def test_sem_cobertura_bloqueia_progressao(self) -> None:
        resultado = construir_resultado_motor_temporal_conjunto(
            self._estado(valor_pagamento=100.0, saldo_fonte=0.0)
        )
        data_ref = date(2026, 1, 1)
        self.assertIsNone(resultado.pacote_vencedor_por_data[data_ref])
        self.assertFalse(resultado.pronto_para_etapa6)
        self.assertEqual(len(resultado.obrigacoes_bloqueadas_temporalmente), 1)
        self.assertFalse(resultado.metadados["aderencia_terminal"])

    def test_pacotes_partem_do_mesmo_estado(self) -> None:
        resultado = construir_resultado_motor_temporal_conjunto(
            self._estado(valor_pagamento=100.0)
        )
        data_ref = date(2026, 1, 1)
        ids = {
            pacote.metadados_auditoria["estado_inicial_id"]
            for pacote in resultado.pacotes_temporais_candidatos_por_data[data_ref]
        }
        self.assertEqual(len(ids), 1)


if __name__ == "__main__":
    unittest.main()
