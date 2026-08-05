from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

from nucleo.proveniencia_portatil import (
    auditar_json_portatil,
    detectar_formato_eol,
    sha256_fisico_arquivo,
    sha256_json_canonico,
)


class ProvenienciaPortatilTest(unittest.TestCase):
    def test_lf_e_crlf_tem_hash_fisico_diferente_e_semantico_igual(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            arquivo_lf = raiz / "lf.json"
            arquivo_crlf = raiz / "crlf.json"
            arquivo_lf.write_bytes(b'{\n  "b": 2,\n  "a": 1\n}\n')
            arquivo_crlf.write_bytes(b'{\r\n  "a": 1,\r\n  "b": 2\r\n}\r\n')

            self.assertNotEqual(
                sha256_fisico_arquivo(arquivo_lf),
                sha256_fisico_arquivo(arquivo_crlf),
            )
            self.assertEqual(
                sha256_json_canonico(arquivo_lf),
                sha256_json_canonico(arquivo_crlf),
            )
            self.assertEqual(detectar_formato_eol(arquivo_lf), "lf")
            self.assertEqual(detectar_formato_eol(arquivo_crlf), "crlf")

    def test_alteracao_semantica_muda_hash_canonico(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            arquivo_a = raiz / "a.json"
            arquivo_b = raiz / "b.json"
            arquivo_a.write_text('{"valor": 1}', encoding="utf-8")
            arquivo_b.write_text('{"valor": 2}', encoding="utf-8")

            self.assertNotEqual(
                sha256_json_canonico(arquivo_a),
                sha256_json_canonico(arquivo_b),
            )

    def test_auditoria_registra_blob_git_e_status_limpo(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            arquivo = raiz / "cache.json"
            arquivo.write_text('{"a": 1}\n', encoding="utf-8")

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
                ["git", "-C", str(raiz), "add", "cache.json"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(raiz), "commit", "-q", "-m", "adiciona cache"],
                check=True,
            )

            auditoria = auditar_json_portatil(
                arquivo,
                raiz_repositorio=raiz,
            )

            self.assertTrue(auditoria.ok)
            self.assertEqual(auditoria.status_git, ())
            self.assertIsNotNone(auditoria.git_blob_sha)
            self.assertEqual(len(auditoria.git_blob_sha or ""), 40)
            self.assertEqual(auditoria.formato_eol, "lf")

    def test_json_invalido_reprova_identidade_semantica(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            arquivo = raiz / "invalido.json"
            arquivo.write_text('{"a": }', encoding="utf-8")

            auditoria = auditar_json_portatil(
                arquivo,
                raiz_repositorio=raiz,
            )

            self.assertFalse(auditoria.ok)
            self.assertIsNone(auditoria.sha256_semantico)
            self.assertIsNotNone(auditoria.erro_semantico)


if __name__ == "__main__":
    unittest.main()
