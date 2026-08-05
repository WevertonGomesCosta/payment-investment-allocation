from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from nucleo.contexto_operacional_canonico import ContextoOperacionalCanonico
from nucleo.estado_temporal_inicial import EstadoTemporalInicial
from nucleo.entrada_economica_motor_canonico import (
    EntradaEconomicaMotorCanonicoInvalida,
    construir_entrada_economica_motor_canonico,
    exigir_entrada_economica_motor_canonico,
)
from nucleo.estado_economico_canonico import (
    AuditoriaEstadoEconomicoCanonico,
    EstadoEconomicoCanonico,
    UnidadeEconomicaCanonica,
)
from nucleo.fundacao_entrada_bloco2 import FundacaoEntradaBloco2
from nucleo.integracao_estado_motor_canonico import (
    construir_integracao_estado_motor_canonico,
)
from nucleo.proveniencia_portatil import ProvenienciaArquivoPortatil
from nucleo.suficiencia_temporal_cdi import (
    ClassificacaoSuficienciaCDI,
    ResultadoSuficienciaTemporalCDI,
)


class EntradaEconomicaMotorCanonicoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data_ref = date(2026, 8, 5)

    def _fundacao(self, *, ok: bool = True, data_ref: date | None = None):
        proveniencia = ProvenienciaArquivoPortatil(
            caminho="dados/cache_bcb.json",
            existe=True,
            tamanho_bytes=10,
            sha256_fisico="f" * 64,
            sha256_semantico="s" * 64,
            algoritmo_semantico="json_canonico_v1",
            git_blob_sha="b" * 40,
            status_git=(),
            formato_eol="lf",
            erro_semantico=None,
        )
        suficiencia = ResultadoSuficienciaTemporalCDI(
            ok=ok,
            classificacao_principal=(
                ClassificacaoSuficienciaCDI.SUFICIENTE
                if ok
                else ClassificacaoSuficienciaCDI.FATOR_REQUERIDO_AUSENTE
            ),
            classificacoes=(ClassificacaoSuficienciaCDI.SUFICIENTE,),
            bloqueios=() if ok else ("fator_ausente",),
            avisos=(),
            evidencias={},
        )
        return FundacaoEntradaBloco2(
            data_referencia=data_ref or self.data_ref,
            proveniencia_cache_json=proveniencia,
            suficiencia_temporal_cdi=suficiencia,
            auditoria_cache_cdi={},
            bloqueios=() if ok else ("fundacao_reprovada",),
            avisos=(),
            metadados={},
        )

    def _unidade(
        self,
        unidade_id: str,
        *,
        estado: str,
        valor: float,
        disponivel: bool,
    ) -> UnidadeEconomicaCanonica:
        return UnidadeEconomicaCanonica(
            unidade_id=unidade_id,
            tipo_unidade="lote",
            identidade_origem=unidade_id.split("::", 1)[-1],
            estado_ciclo=estado,
            valor_liquido_atual=valor,
            disponivel_pagamento_na_referencia=disponivel,
            data_referencia=self.data_ref,
            data_aplicacao=self.data_ref - timedelta(days=30),
            produto="Produto teste",
        )

    def _estado(self) -> EstadoEconomicoCanonico:
        unidades = [
            self._unidade(
                "lote::disponivel",
                estado="ativo_disponivel",
                valor=100.0,
                disponivel=True,
            ),
            self._unidade(
                "lote::carencia",
                estado="ativo_bloqueado_carencia",
                valor=50.0,
                disponivel=False,
            ),
            self._unidade(
                "lote::encerrado",
                estado="migrado_por_switching",
                valor=0.0,
                disponivel=False,
            ),
        ]
        auditoria = AuditoriaEstadoEconomicoCanonico(
            ok=True,
            bloqueios=[],
            avisos=[],
            reconciliacoes=[],
            resumo={"valor_total_disponivel_canonico": 100.0},
        )
        return EstadoEconomicoCanonico(
            data_referencia=self.data_ref,
            unidades=unidades,
            fontes_disponiveis=[],
            fontes_bloqueadas=[],
            eventos_conservacao=[],
            auditoria=auditoria,
            metadados={},
        )

    def test_transporta_fontes_bloqueadas_e_encerradas(self) -> None:
        entrada = construir_entrada_economica_motor_canonico(
            self._estado(),
            self._fundacao(),
        )
        self.assertTrue(entrada.auditoria.ok)
        self.assertEqual(len(entrada.fontes_disponiveis), 1)
        self.assertEqual(len(entrada.unidades_bloqueadas), 1)
        self.assertEqual(len(entrada.unidades_encerradas), 1)
        self.assertEqual(
            entrada.fontes_disponiveis[0].identidade_origem,
            "disponivel",
        )
        self.assertEqual(
            entrada.fontes_disponiveis[0].valor_liquido_atual,
            100.0,
        )
        self.assertEqual(
            entrada.unidades_encerradas[0].valor_liquido_atual,
            0.0,
        )

    def test_rejeita_contexto_estado_temporal_lista_e_dict(self) -> None:
        fundacao = self._fundacao()
        for legado in (
            object.__new__(ContextoOperacionalCanonico),
            object.__new__(EstadoTemporalInicial),
            [],
            {},
        ):
            with self.subTest(tipo=type(legado).__name__):
                with self.assertRaises(EntradaEconomicaMotorCanonicoInvalida):
                    construir_entrada_economica_motor_canonico(
                        legado,
                        fundacao,
                    )

    def test_rejeita_fundacao_reprovada(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "FundacaoEntradaBloco2 reprovada",
        ):
            construir_entrada_economica_motor_canonico(
                self._estado(),
                self._fundacao(ok=False),
            )

    def test_rejeita_data_de_referencia_divergente(self) -> None:
        with self.assertRaisesRegex(
            EntradaEconomicaMotorCanonicoInvalida,
            "data_referencia_divergente",
        ):
            construir_entrada_economica_motor_canonico(
                self._estado(),
                self._fundacao(
                    data_ref=self.data_ref - timedelta(days=1),
                ),
            )

    def test_rejeita_unidade_encerrada_com_saldo(self) -> None:
        estado = self._estado()
        estado.unidades[-1].valor_liquido_atual = 1.0
        with self.assertRaisesRegex(
            EntradaEconomicaMotorCanonicoInvalida,
            "unidade_encerrada_com_saldo",
        ):
            construir_entrada_economica_motor_canonico(
                estado,
                self._fundacao(),
            )

    def test_gate_do_novo_motor_rejeita_objetos_legados(self) -> None:
        entrada = construir_entrada_economica_motor_canonico(
            self._estado(),
            self._fundacao(),
        )
        exigir_entrada_economica_motor_canonico(entrada)
        for legado in (
            self._estado(),
            object.__new__(ContextoOperacionalCanonico),
            object.__new__(EstadoTemporalInicial),
            [],
            {},
        ):
            with self.subTest(tipo=type(legado).__name__):
                with self.assertRaises(EntradaEconomicaMotorCanonicoInvalida):
                    exigir_entrada_economica_motor_canonico(legado)

    def test_integracao_nao_muta_contexto_nem_estado_temporal(self) -> None:
        contexto = SimpleNamespace(nome="contexto")
        estado_temporal = SimpleNamespace(nome="estado")
        contexto_antes = deepcopy(contexto.__dict__)
        estado_antes = deepcopy(estado_temporal.__dict__)
        fundacao = self._fundacao()
        estado = self._estado()
        entrada = construir_entrada_economica_motor_canonico(
            estado,
            fundacao,
        )

        with (
            patch(
                "nucleo.integracao_estado_motor_canonico."
                "construir_fundacao_entrada_bloco2",
                return_value=fundacao,
            ),
            patch(
                "nucleo.integracao_estado_motor_canonico."
                "construir_estado_economico_canonico",
                return_value=estado,
            ),
            patch(
                "nucleo.integracao_estado_motor_canonico."
                "construir_entrada_economica_motor_canonico",
                return_value=entrada,
            ),
        ):
            integracao = construir_integracao_estado_motor_canonico(
                contexto,
                estado_temporal,
                raiz_repositorio=Path("."),
            )

        self.assertTrue(integracao.ok)
        self.assertEqual(contexto.__dict__, contexto_antes)
        self.assertEqual(estado_temporal.__dict__, estado_antes)

    def test_principal_executa_integracao_antes_do_motor_legado(self) -> None:
        raiz = Path(__file__).resolve().parents[1]
        fonte = (raiz / "aplicacao" / "principal.py").read_text(
            encoding="utf-8"
        )
        chamada_integracao = "construir_integracao_estado_motor_canonico("
        chamada_motor_legado = (
            "construir_resultado_motor_temporal_conjunto("
            "estado_temporal_inicial)"
        )
        self.assertIn(chamada_integracao, fonte)
        self.assertIn(chamada_motor_legado, fonte)
        self.assertLess(
            fonte.index(chamada_integracao),
            fonte.index(chamada_motor_legado),
        )


if __name__ == "__main__":
    unittest.main()
