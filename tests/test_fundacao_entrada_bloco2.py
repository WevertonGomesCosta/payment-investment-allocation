from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import subprocess
import tempfile
import unittest

from nucleo.fundacao_entrada_bloco2 import (
    FundacaoEntradaBloco2Invalida,
    construir_fundacao_entrada_bloco2,
    construir_fundacao_entrada_bloco2_do_cache,
)


@dataclass
class CacheFake:
    caminho_cache: Path
    serie_cdi: dict[date, float]
    data_inicial_consulta: date
    data_final_consulta: date
    auditoria: dict


@dataclass
class ExecucaoFake:
    data_referencia: date


@dataclass
class ContextoFake:
    execucao: ExecucaoFake
    cache_cdi: CacheFake


class FundacaoEntradaBloco2Test(unittest.TestCase):
    def _repositorio_cache(self):
        temporario = tempfile.TemporaryDirectory()
        raiz = Path(temporario.name)
        cache_path = raiz / "dados" / "cache_bcb.json"
        cache_path.parent.mkdir(parents=True)
        cache_path.write_bytes(b'{"mapa":{"2026-08-04":1.0005}}\n')
        subprocess.run(["git", "init", "-q", str(raiz)], check=True)
        subprocess.run(
            ["git", "-C", str(raiz), "config", "user.email", "teste@example.com"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(raiz), "config", "user.name", "Teste"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(raiz), "add", "dados/cache_bcb.json"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(raiz), "commit", "-q", "-m", "cache"],
            check=True,
        )
        cache = CacheFake(
            caminho_cache=cache_path,
            serie_cdi={date(2026, 8, 4): 1.0005},
            data_inicial_consulta=date(2026, 8, 4),
            data_final_consulta=date(2026, 8, 5),
            auditoria={"fonte_serie_cdi": "cache_local"},
        )
        return temporario, raiz, cache

    def test_constroi_fundacao_aprovada_do_cache_versionado(self) -> None:
        temporario, raiz, cache = self._repositorio_cache()
        self.addCleanup(temporario.cleanup)
        resultado = construir_fundacao_entrada_bloco2_do_cache(
            cache,
            data_referencia=date(2026, 8, 5),
            raiz_repositorio=raiz,
        )
        self.assertTrue(resultado.ok)
        self.assertEqual(resultado.bloqueios, ())
        self.assertEqual(resultado.proveniencia_cache_json.status_git, ())
        self.assertIsNotNone(resultado.proveniencia_cache_json.git_blob_sha)

    def test_wrapper_do_contexto_reutiliza_mesma_fundacao(self) -> None:
        temporario, raiz, cache = self._repositorio_cache()
        self.addCleanup(temporario.cleanup)
        contexto = ContextoFake(
            execucao=ExecucaoFake(date(2026, 8, 5)),
            cache_cdi=cache,
        )
        resultado = construir_fundacao_entrada_bloco2(
            contexto,
            raiz_repositorio=raiz,
        )
        self.assertTrue(resultado.ok)
        self.assertEqual(
            resultado.suficiencia_temporal_cdi.evidencias["qtd_fatores_validos"],
            1,
        )

    def test_cache_modificado_localmente_bloqueia(self) -> None:
        temporario, raiz, cache = self._repositorio_cache()
        self.addCleanup(temporario.cleanup)
        cache.caminho_cache.write_bytes(
            b'{"mapa":{"2026-08-04":1.0006}}\n'
        )
        resultado = construir_fundacao_entrada_bloco2_do_cache(
            cache,
            data_referencia=date(2026, 8, 5),
            raiz_repositorio=raiz,
        )
        self.assertFalse(resultado.ok)
        self.assertIn(
            "cache_json_com_alteracoes_locais_nao_versionadas",
            resultado.bloqueios,
        )

    def test_contexto_ausente_e_rejeitado(self) -> None:
        with self.assertRaises(FundacaoEntradaBloco2Invalida):
            construir_fundacao_entrada_bloco2(
                None,
                raiz_repositorio=Path("."),
            )


if __name__ == "__main__":
    unittest.main()
