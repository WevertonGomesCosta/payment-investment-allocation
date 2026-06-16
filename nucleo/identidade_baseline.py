from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Identificador histórico preservado apenas para rotas antigas que ainda
# recebem o parâmetro `versao`. Não define artefato operacional atual.
VERSAO_BASELINE = "V225"
VERSAO_SLUG = VERSAO_BASELINE.lower()

PR_VERSAO_ATUAL = 532
VERSAO_ATUAL = f"PR-{PR_VERSAO_ATUAL}"
VERSAO_ATUAL_SLUG = f"pr{PR_VERSAO_ATUAL}"


_ROTULOS_METADADOS_VERSAO = [
    ("versão atual", "versao_atual"),
    ("arquivo operacional oficial", "arquivo_operacional_oficial"),
]


def nome_relatorio_operacional() -> str:
    return f"relatorio_operacional_{VERSAO_ATUAL_SLUG}.xlsx"


def metadados_versao_operacional(
    raiz: Path | str | None = None,
    *,
    data_referencia: Any = None,
) -> dict[str, Any]:
    _ = raiz, data_referencia
    return {
        "versao_atual": VERSAO_ATUAL,
        "arquivo_operacional_oficial": nome_relatorio_operacional(),
    }


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
