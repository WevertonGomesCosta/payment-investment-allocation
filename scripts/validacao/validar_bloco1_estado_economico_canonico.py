from __future__ import annotations

import argparse
import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_operacional_canonico import carregar_contexto_operacional_canonico
from nucleo.estado_economico_canonico import (
    construir_estado_economico_canonico,
    exigir_estado_economico_canonico_valido,
)
from nucleo.estado_temporal_inicial import construir_estado_temporal_inicial


_ARQUIVOS_ENTRADA_AUDITADOS = (
    Path("dados/dados_financeiros.xlsx"),
    Path("dados/cache_bcb.json"),
)


def _argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida identidade econômica e conservação patrimonial do Bloco 1."
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=RAIZ_REPOSITORIO / "saidas" / "diagnostico" / "estado_economico_canonico_bloco1.json",
        help="Caminho do JSON diagnóstico.",
    )
    parser.add_argument(
        "--nao-bloquear",
        action="store_true",
        help="Gera o diagnóstico sem retornar erro quando houver bloqueios.",
    )
    return parser.parse_args()


def _executar_git(*argumentos: str) -> str | None:
    try:
        resultado = subprocess.run(
            ["git", "-C", str(RAIZ_REPOSITORIO), *argumentos],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None
    texto = (resultado.stdout or "").strip()
    return texto or None


def _sha256_arquivo(caminho: Path) -> str | None:
    if not caminho.exists() or not caminho.is_file():
        return None
    digest = sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def _proveniencia_execucao() -> dict[str, Any]:
    status_por_arquivo = _executar_git(
        "status",
        "--porcelain",
        "--",
        *[str(caminho).replace("\\", "/") for caminho in _ARQUIVOS_ENTRADA_AUDITADOS],
    )
    linhas_status = [
        linha
        for linha in (status_por_arquivo or "").splitlines()
        if linha.strip()
    ]
    arquivos: dict[str, Any] = {}
    for caminho_relativo in _ARQUIVOS_ENTRADA_AUDITADOS:
        caminho = RAIZ_REPOSITORIO / caminho_relativo
        arquivos[str(caminho_relativo).replace("\\", "/")] = {
            "existe": caminho.exists(),
            "tamanho_bytes": caminho.stat().st_size if caminho.exists() else None,
            "sha256": _sha256_arquivo(caminho),
        }
    return {
        "branch": _executar_git("rev-parse", "--abbrev-ref", "HEAD") or "nao_detectada",
        "commit": _executar_git("rev-parse", "HEAD") or "indisponivel",
        "commit_curto": (_executar_git("rev-parse", "--short=12", "HEAD") or "indisponivel"),
        "dados_entrada_modificados_localmente": bool(linhas_status),
        "status_git_arquivos_entrada": linhas_status,
        "arquivos_entrada": arquivos,
    }


def main() -> int:
    args = _argumentos()
    contexto = carregar_contexto_operacional_canonico(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
    )
    estado_temporal = construir_estado_temporal_inicial(contexto)
    estado_economico = construir_estado_economico_canonico(estado_temporal)
    estado_economico.metadados["proveniencia_execucao"] = _proveniencia_execucao()

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(
        json.dumps(
            estado_economico.como_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    resumo = dict(estado_economico.auditoria.resumo)
    saida_console = {
        "artefato": estado_economico.metadados.get("artefato"),
        "bloco": estado_economico.metadados.get("bloco"),
        "ok": estado_economico.auditoria.ok,
        "bloqueios": estado_economico.auditoria.bloqueios,
        "avisos": estado_economico.auditoria.avisos,
        "resumo": resumo,
        "proveniencia_execucao": estado_economico.metadados.get("proveniencia_execucao"),
        "arquivo": str(args.saida),
    }
    print(
        "BLOCO1_ESTADO_ECONOMICO_CANONICO="
        + json.dumps(saida_console, ensure_ascii=False, sort_keys=True)
    )

    if args.nao_bloquear:
        return 0
    exigir_estado_economico_canonico_valido(estado_economico)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
