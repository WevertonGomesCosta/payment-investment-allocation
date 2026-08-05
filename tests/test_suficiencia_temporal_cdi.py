from __future__ import annotations

from datetime import date
import unittest

from nucleo.suficiencia_temporal_cdi import (
    ClassificacaoSuficienciaCDI,
    avaliar_suficiencia_temporal_cdi,
)


class SuficienciaTemporalCDITest(unittest.TestCase):
    def test_cenario_real_classifica_bordas_sem_bloquear(self) -> None:
        resultado = avaliar_suficiencia_temporal_cdi(
            {
                date(2026, 1, 2): 1.0005,
                date(2026, 8, 3): 1.0006,
            },
            data_inicial_consulta=date(2026, 1, 1),
            data_final_consulta=date(2026, 8, 5),
            data_referencia=date(2026, 8, 5),
            max_defasagem_dias=2,
            max_lacuna_inicial_dias=1,
        )

        self.assertTrue(resultado.ok)
        self.assertEqual(
            resultado.classificacao_principal,
            ClassificacaoSuficienciaCDI.DEFASAGEM_ADMISSIVEL,
        )
        self.assertIn(
            ClassificacaoSuficienciaCDI.DIA_SEM_OBSERVACAO,
            resultado.classificacoes,
        )

    def test_serie_com_cobertura_requerida_e_suficiente(self) -> None:
        resultado = avaliar_suficiencia_temporal_cdi(
            {
                date(2026, 1, 2): 1.0005,
                date(2026, 1, 3): 1.0005,
            },
            data_inicial_consulta=date(2026, 1, 2),
            data_final_consulta=date(2026, 1, 3),
            data_referencia=date(2026, 1, 3),
            datas_requeridas=(date(2026, 1, 2), date(2026, 1, 3)),
        )

        self.assertTrue(resultado.ok)
        self.assertEqual(
            resultado.classificacao_principal,
            ClassificacaoSuficienciaCDI.SUFICIENTE,
        )

    def test_fator_requerido_ausente_bloqueia(self) -> None:
        resultado = avaliar_suficiencia_temporal_cdi(
            {date(2026, 1, 2): 1.0005},
            data_inicial_consulta=date(2026, 1, 2),
            data_final_consulta=date(2026, 1, 3),
            data_referencia=date(2026, 1, 3),
            datas_requeridas=(date(2026, 1, 3),),
            max_defasagem_dias=2,
        )

        self.assertFalse(resultado.ok)
        self.assertEqual(
            resultado.classificacao_principal,
            ClassificacaoSuficienciaCDI.FATOR_REQUERIDO_AUSENTE,
        )
        self.assertTrue(resultado.bloqueios)

    def test_data_sem_observacao_explicitamente_permitida_nao_bloqueia(self) -> None:
        resultado = avaliar_suficiencia_temporal_cdi(
            {
                date(2026, 1, 2): 1.0005,
                date(2026, 1, 4): 1.0005,
            },
            data_inicial_consulta=date(2026, 1, 2),
            data_final_consulta=date(2026, 1, 4),
            data_referencia=date(2026, 1, 4),
            datas_requeridas=(date(2026, 1, 3),),
            datas_sem_observacao_permitidas=(date(2026, 1, 3),),
        )

        self.assertTrue(resultado.ok)
        self.assertEqual(
            resultado.classificacao_principal,
            ClassificacaoSuficienciaCDI.DIA_SEM_OBSERVACAO,
        )

    def test_defasagem_acima_da_tolerancia_bloqueia(self) -> None:
        resultado = avaliar_suficiencia_temporal_cdi(
            {date(2026, 1, 2): 1.0005},
            data_inicial_consulta=date(2026, 1, 2),
            data_final_consulta=date(2026, 1, 6),
            data_referencia=date(2026, 1, 6),
            max_defasagem_dias=2,
        )

        self.assertFalse(resultado.ok)
        self.assertEqual(
            resultado.classificacao_principal,
            ClassificacaoSuficienciaCDI.FATOR_REQUERIDO_AUSENTE,
        )

    def test_fator_invalido_em_data_requerida_bloqueia(self) -> None:
        resultado = avaliar_suficiencia_temporal_cdi(
            {date(2026, 1, 2): 1.0},
            data_inicial_consulta=date(2026, 1, 2),
            data_final_consulta=date(2026, 1, 2),
            data_referencia=date(2026, 1, 2),
            datas_requeridas=(date(2026, 1, 2),),
        )

        self.assertFalse(resultado.ok)
        self.assertIn(
            "2026-01-02",
            " ".join(resultado.avisos),
        )


if __name__ == "__main__":
    unittest.main()
