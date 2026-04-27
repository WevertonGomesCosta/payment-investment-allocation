from __future__ import annotations

import re
from pathlib import Path

VERSAO_BASELINE = "V217"
VERSAO_SLUG = VERSAO_BASELINE.lower()


def nome_relatorio_operacional() -> str:
    return f"relatorio_operacional_{VERSAO_SLUG}.xlsx"


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


def nome_auditoria_comparativa_proxy_v3_vs_hibrido_shadow(extensao: str) -> str:
    return f"auditoria_comparativa_proxy_v3_vs_hibrido_shadow_{VERSAO_SLUG}.{extensao.lstrip('.')}"


def nome_auditoria_residual_proxy_v3_vs_hibrido_shadow(extensao: str) -> str:
    return f"auditoria_residual_proxy_v3_vs_hibrido_shadow_{VERSAO_SLUG}.{extensao.lstrip('.')}"


def nome_auditoria_cirurgica_reaproveitaveis_proxy_v3_vs_hibrido_shadow(extensao: str) -> str:
    return f"auditoria_cirurgica_reaproveitaveis_proxy_v3_vs_hibrido_shadow_{VERSAO_SLUG}.{extensao.lstrip('.')}"


def nome_auditoria_fina_transicao_dominante_proxy_v3_vs_hibrido_shadow(extensao: str) -> str:
    return f"auditoria_fina_transicao_dominante_proxy_v3_vs_hibrido_shadow_{VERSAO_SLUG}.{extensao.lstrip('.')}"



def nome_auditoria_mapa_execucao_principal_script2(extensao: str) -> str:
    return f"auditoria_mapa_execucao_principal_script2_{VERSAO_SLUG}.{extensao.lstrip('.')}"


def nome_auditoria_benchmark_agrupado_individual_shadow(extensao: str) -> str:
    return f"auditoria_benchmark_agrupado_individual_shadow_{VERSAO_SLUG}.{extensao.lstrip('.')}"


def nome_auditoria_benchmark_runner_futuro_shadow(extensao: str) -> str:
    return f"auditoria_benchmark_runner_futuro_shadow_{VERSAO_SLUG}.{extensao.lstrip('.')}"


def nome_auditoria_casos_criticos_runner_futuro_shadow(extensao: str) -> str:
    return f"auditoria_casos_criticos_runner_futuro_shadow_{VERSAO_SLUG}.{extensao.lstrip('.')}"


def nome_auditoria_primeira_quebra_runner_futuro_shadow(extensao: str) -> str:
    return f"auditoria_primeira_quebra_runner_futuro_shadow_{VERSAO_SLUG}.{extensao.lstrip('.')}"
