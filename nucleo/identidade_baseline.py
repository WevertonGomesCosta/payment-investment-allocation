from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

# Identificador histórico preservado apenas para rotas antigas que ainda
# recebem o parâmetro `versao`. Não define artefato operacional atual.
VERSAO_BASELINE = "V225"
VERSAO_SLUG = VERSAO_BASELINE.lower()

PR_VERSAO_ATUAL = 532
VERSAO_ATUAL = f"PR-{PR_VERSAO_ATUAL}"
VERSAO_ATUAL_SLUG = f"pr{PR_VERSAO_ATUAL}"


_COMMIT_INDISPONIVEL = "indisponivel"
_BRANCH_INDISPONIVEL = "nao_detectado"
_FONTE_GIT_INDISPONIVEL = "git_indisponivel"


_ROTULOS_METADADOS_VERSAO = [
    ("versão atual", "versao_atual"),
    ("arquivo operacional oficial", "arquivo_operacional_oficial"),
]


def _executar_git(raiz: Path | str | None, *args: str) -> str | None:
    raiz_git = Path(raiz).resolve() if raiz is not None else Path.cwd()
    try:
        resultado = subprocess.run(
            ["git", "-C", str(raiz_git), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except Exception:
        return None
    texto = (resultado.stdout or "").strip()
    return texto or None


def _identidade_git(raiz: Path | str | None = None) -> dict[str, str]:
    commit = _executar_git(raiz, "rev-parse", "HEAD")
    branch = _executar_git(raiz, "rev-parse", "--abbrev-ref", "HEAD")

    if commit:
        commit_curto = commit[:12]
        fonte_commit = "git"
    else:
        commit = _COMMIT_INDISPONIVEL
        commit_curto = _COMMIT_INDISPONIVEL
        fonte_commit = _FONTE_GIT_INDISPONIVEL

    if branch:
        fonte_branch = "git"
    else:
        branch = _BRANCH_INDISPONIVEL
        fonte_branch = _FONTE_GIT_INDISPONIVEL

    return {
        "commit": commit,
        "commit_curto": commit_curto,
        "branch": branch,
        "fonte_commit": fonte_commit,
        "fonte_branch": fonte_branch,
    }


def _serializar_data_referencia(data_referencia: Any) -> str:
    if data_referencia is None:
        return ""
    if hasattr(data_referencia, "isoformat") and not isinstance(data_referencia, str):
        try:
            return data_referencia.isoformat()
        except Exception:
            return str(data_referencia)
    return str(data_referencia)


def nome_relatorio_operacional() -> str:
    return f"relatorio_operacional_{VERSAO_ATUAL_SLUG}.xlsx"


def metadados_versao_operacional(
    raiz: Path | str | None = None,
    *,
    data_referencia: Any = None,
) -> dict[str, Any]:
    metadados = {
        "versao_atual": VERSAO_ATUAL,
        "pr_versao_atual": PR_VERSAO_ATUAL,
        "data_referencia": _serializar_data_referencia(data_referencia),
        "arquivo_operacional_oficial": nome_relatorio_operacional(),
    }
    metadados.update(_identidade_git(raiz))
    return metadados


def linhas_metadados_versao_operacional(metadados: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"Campo": rotulo, "Valor": metadados.get(chave)}
        for rotulo, chave in _ROTULOS_METADADOS_VERSAO
    ]


def slug_lote(lote_id: str) -> str:
    texto = re.sub(r"[^a-zA-Z0-9]+", "_", str(lote_id).strip().lower()).strip('_')
    return texto or 'lote'


def nome_auditoria_diaria_lote(lote_id: str, extensao: str) -> str:
    return f"auditoria_diaria_{slug_lote(lote_id)}_{VERSAO_SLUG}.{extensao.lstrip('.')}"


def caminho_saida_oficial(raiz: Path, nome_arquivo: str) -> Path:
    return raiz / 'saidas' / 'oficial' / nome_arquivo


def caminho_saida_diagnostico(raiz: Path, nome_arquivo: str) -> Path:
    return raiz / 'saidas' / 'diagnostico' / nome_arquivo


def caminho_saida_historico(raiz: Path, nome_arquivo: str) -> Path:
    return raiz / 'saidas' / 'historico' / nome_arquivo


def caminho_saida_operacional(raiz: Path, nome_arquivo: str) -> Path:
    return caminho_saida_oficial(raiz, nome_arquivo)


def caminho_artifact(nome_arquivo: str) -> Path:
    return Path('/mnt/data') / f"payment-investment-allocation_{nome_arquivo}" if nome_arquivo.startswith('relatorio_operacional_') else Path('/mnt/data') / nome_arquivo


def nome_auditoria_comparativa_proxy_v2_v3(extensao: str) -> str:
    return f"auditoria_comparativa_proxy_v2_v3_{VERSAO_SLUG}.{extensao.lstrip('.')}"


def nome_auditoria_mapa_execucao_principal_script2(extensao: str) -> str:
    return f"auditoria_mapa_execucao_principal_script2_{VERSAO_SLUG}.{extensao.lstrip('.')}"
