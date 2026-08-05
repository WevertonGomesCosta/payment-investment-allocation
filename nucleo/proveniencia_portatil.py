"""Proveniência portátil para arquivos JSON versionados.

Separa a identidade física do arquivo no working tree da identidade semântica
canônica. Diferenças de EOL, indentação ou ordem das chaves não alteram o hash
semântico.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any


@dataclass(frozen=True, slots=True)
class ProvenienciaArquivoPortatil:
    caminho: str
    existe: bool
    tamanho_bytes: int | None
    sha256_fisico: str | None
    sha256_semantico: str | None
    algoritmo_semantico: str | None
    git_blob_sha: str | None
    status_git: tuple[str, ...]
    formato_eol: str | None
    erro_semantico: str | None

    @property
    def ok(self) -> bool:
        return bool(
            self.existe
            and self.sha256_fisico
            and self.sha256_semantico
            and not self.erro_semantico
        )

    def como_dict(self) -> dict[str, Any]:
        dados = asdict(self)
        dados["status_git"] = list(self.status_git)
        dados["ok"] = self.ok
        return dados


def _sha256_bytes(conteudo: bytes) -> str:
    return sha256(conteudo).hexdigest()


def sha256_fisico_arquivo(caminho: Path) -> str:
    digest = sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def serializar_json_canonico(payload: Any) -> bytes:
    """Serializa JSON de modo determinístico e independente de EOL."""

    texto = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return texto.encode("utf-8")


def sha256_json_canonico(caminho: Path) -> str:
    payload = json.loads(caminho.read_text(encoding="utf-8"))
    return _sha256_bytes(serializar_json_canonico(payload))


def detectar_formato_eol(caminho: Path) -> str:
    conteudo = caminho.read_bytes()
    if not conteudo:
        return "vazio"

    qtd_crlf = conteudo.count(b"\r\n")
    restante = conteudo.replace(b"\r\n", b"")
    qtd_lf = restante.count(b"\n")
    qtd_cr = restante.count(b"\r")

    formatos: list[str] = []
    if qtd_crlf:
        formatos.append("crlf")
    if qtd_lf:
        formatos.append("lf")
    if qtd_cr:
        formatos.append("cr")

    if not formatos:
        return "sem_quebra"
    if len(formatos) == 1:
        return formatos[0]
    return "misto:" + "+".join(formatos)


def _executar_git(raiz_repositorio: Path, *argumentos: str) -> str | None:
    try:
        resultado = subprocess.run(
            ["git", "-C", str(raiz_repositorio), *argumentos],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None
    texto = (resultado.stdout or "").strip()
    return texto or None


def _caminho_relativo_git(caminho: Path, raiz_repositorio: Path) -> str | None:
    try:
        return caminho.resolve().relative_to(raiz_repositorio.resolve()).as_posix()
    except Exception:
        return None


def auditar_json_portatil(
    caminho: Path,
    *,
    raiz_repositorio: Path,
) -> ProvenienciaArquivoPortatil:
    caminho = caminho.resolve()
    raiz_repositorio = raiz_repositorio.resolve()
    existe = caminho.exists() and caminho.is_file()
    relativo = _caminho_relativo_git(caminho, raiz_repositorio)

    status_git: tuple[str, ...] = ()
    git_blob_sha = None
    if relativo:
        status = _executar_git(
            raiz_repositorio,
            "status",
            "--porcelain",
            "--",
            relativo,
        )
        status_git = tuple(
            linha for linha in (status or "").splitlines() if linha.strip()
        )
        git_blob_sha = _executar_git(
            raiz_repositorio,
            "rev-parse",
            f"HEAD:{relativo}",
        )

    if not existe:
        return ProvenienciaArquivoPortatil(
            caminho=str(caminho),
            existe=False,
            tamanho_bytes=None,
            sha256_fisico=None,
            sha256_semantico=None,
            algoritmo_semantico="json_canonico_v1",
            git_blob_sha=git_blob_sha,
            status_git=status_git,
            formato_eol=None,
            erro_semantico="arquivo_inexistente",
        )

    erro_semantico = None
    hash_semantico = None
    try:
        hash_semantico = sha256_json_canonico(caminho)
    except Exception as exc:
        erro_semantico = f"{exc.__class__.__name__}:{exc}"

    return ProvenienciaArquivoPortatil(
        caminho=str(caminho),
        existe=True,
        tamanho_bytes=caminho.stat().st_size,
        sha256_fisico=sha256_fisico_arquivo(caminho),
        sha256_semantico=hash_semantico,
        algoritmo_semantico="json_canonico_v1",
        git_blob_sha=git_blob_sha,
        status_git=status_git,
        formato_eol=detectar_formato_eol(caminho),
        erro_semantico=erro_semantico,
    )
