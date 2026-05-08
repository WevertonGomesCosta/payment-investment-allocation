from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.carregador_config import carregar_config
from nucleo.leitor_planilha import carregar_planilha, resolver_coluna

OUT_DIR = RAIZ / "saidas" / "diagnostico" / "v17_a1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARQ_ABAS = OUT_DIR / "v17_a1_abas_reconhecidas.csv"
ARQ_CAMPOS = OUT_DIR / "v17_a1_campos_criticos_reconhecidos.csv"
ARQ_FAMILIAS = OUT_DIR / "v17_a1_familias_v17_reconhecidas.csv"
ARQ_RESUMO = OUT_DIR / "v17_a1_resumo.csv"

ABAS_ESPERADAS = {
    "carteira": "Carteira",
    "salarios": "Salários",
    "despesas": "Todos os Gastos",
    "lotes": "Inventário de Lotes",
    "switching": "Switching",
}

CAMPOS_CRITICOS = {
    "carteira": ["nome", "taxa_base", "prazo_dias", "carencia_dias", "liquidez_dias", "aplicacao_minima"],
    "salarios": ["data_recebimento", "valor_bruto", "valor_liquido"],
    "despesas": ["despesa_id", "data", "valor", "lote_usado_1"],
    "lotes": ["lote_id", "data_recebimento", "data_aplicacao", "valor_original", "produto_id"],
    "switching": ["lote_id_antes", "lote_id_depois", "valor_liquido_migrado", "data_aplicacao", "investimento"],
}

FAMILIAS_V17 = [
    "produto_carteira",
    "entrada_externa_salario",
    "pagamento_por_saldo",
    "pagamento_por_lote",
    "lote_investido",
    "lote_caixa_disponivel",
    "switching_origem",
    "switching_destino_materializado",
]


def _gravar_csv(df: pd.DataFrame, caminho: Path, colunas: list[str]) -> None:
    if df is None or df.empty:
        df = pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    df[colunas].to_csv(caminho, index=False)


def _resolver_coluna_seguro(df: pd.DataFrame | None, config: dict[str, Any], secao: str, chave: str) -> tuple[bool, str, str]:
    if df is None:
        return False, "", "aba_nao_lida"
    try:
        coluna = resolver_coluna(df, config, secao, chave, obrigatoria=True)
        return True, str(coluna), "reconhecido"
    except Exception as erro:
        return False, "", str(erro).replace("\n", " ")[:300]


def main() -> int:
    pacote_config = carregar_config(raiz_repositorio=RAIZ)
    config = pacote_config.conteudo
    pacote_planilha = carregar_planilha(config, raiz_repositorio=RAIZ, carregar_todas_as_abas=True)

    abas_cfg = config.get("abas", {}) if isinstance(config.get("abas"), dict) else {}
    familias_cfg = config.get("familias_v17", {}) if isinstance(config.get("familias_v17"), dict) else {}
    quadros_canonicos = pacote_planilha.quadros_canonicos

    linhas_abas = []
    for chave, nome_esperado in ABAS_ESPERADAS.items():
        nome_cfg = str(abas_cfg.get(chave, ""))
        existe_na_planilha = nome_cfg in pacote_planilha.nomes_abas
        lida_canonizada = nome_cfg in quadros_canonicos
        linhas_abas.append({
            "chave_config": chave,
            "aba_esperada": nome_esperado,
            "aba_config": nome_cfg,
            "existe_na_planilha": existe_na_planilha,
            "lida_canonizada": lida_canonizada,
            "status": "ok" if nome_cfg == nome_esperado and existe_na_planilha and lida_canonizada else "falha",
        })

    linhas_campos = []
    for secao, campos in CAMPOS_CRITICOS.items():
        nome_aba = str(abas_cfg.get(secao, ""))
        df = quadros_canonicos.get(nome_aba)
        for campo in campos:
            ok, coluna, detalhe = _resolver_coluna_seguro(df, config, secao, campo)
            linhas_campos.append({
                "secao_config": secao,
                "aba_config": nome_aba,
                "campo_critico": campo,
                "reconhecido": ok,
                "coluna_resolvida": coluna,
                "status": "ok" if ok else "falha",
                "detalhe": detalhe,
            })

    linhas_familias = []
    for familia in FAMILIAS_V17:
        spec = familias_cfg.get(familia, {}) if isinstance(familias_cfg.get(familia), dict) else {}
        aba_key = str(spec.get("aba", ""))
        tipo = str(spec.get("tipo_canonico", ""))
        modo = str(spec.get("modo_v17_a1", ""))
        aba_nome = str(abas_cfg.get(aba_key, ""))
        ok = bool(spec) and tipo == familia and modo == "canonizacao_sem_motor" and aba_nome in pacote_planilha.nomes_abas
        linhas_familias.append({
            "familia_v17": familia,
            "aba_key": aba_key,
            "aba_nome": aba_nome,
            "tipo_canonico": tipo,
            "modo_v17_a1": modo,
            "reconhecida": ok,
            "status": "ok" if ok else "falha",
        })

    df_abas = pd.DataFrame(linhas_abas)
    df_campos = pd.DataFrame(linhas_campos)
    df_familias = pd.DataFrame(linhas_familias)

    abas_ok = int((df_abas["status"] == "ok").sum())
    campos_ok = int((df_campos["status"] == "ok").sum())
    familias_ok = int((df_familias["status"] == "ok").sum())

    total_abas = len(df_abas)
    total_campos = len(df_campos)
    total_familias = len(df_familias)

    status_global = "ok" if abas_ok == total_abas and campos_ok == total_campos and familias_ok == total_familias else "falha"

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_a1", "valor": status_global, "status": status_global, "observacao": "canonizacao sem motor"},
        {"metrica": "abas_reconhecidas", "valor": abas_ok, "status": "ok" if abas_ok == total_abas else "falha", "observacao": f"total={total_abas}"},
        {"metrica": "campos_criticos_reconhecidos", "valor": campos_ok, "status": "ok" if campos_ok == total_campos else "falha", "observacao": f"total={total_campos}"},
        {"metrica": "familias_v17_reconhecidas", "valor": familias_ok, "status": "ok" if familias_ok == total_familias else "falha", "observacao": f"total={total_familias}"},
        {"metrica": "overlay_canonizacao_v17_a1", "valor": config.get("metadados_config", {}).get("overlay_canonizacao_v17_a1", ""), "status": "info", "observacao": "overlay aplicado pelo carregador"},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True, "status": "ok", "observacao": "validacao diagnostica apenas"},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True, "status": "ok", "observacao": "sem edicao documental normativa"},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True, "status": "ok", "observacao": "sem consumo funcional pelo motor"},
    ])

    _gravar_csv(df_abas, ARQ_ABAS, ["chave_config", "aba_esperada", "aba_config", "existe_na_planilha", "lida_canonizada", "status"])
    _gravar_csv(df_campos, ARQ_CAMPOS, ["secao_config", "aba_config", "campo_critico", "reconhecido", "coluna_resolvida", "status", "detalhe"])
    _gravar_csv(df_familias, ARQ_FAMILIAS, ["familia_v17", "aba_key", "aba_nome", "tipo_canonico", "modo_v17_a1", "reconhecida", "status"])
    _gravar_csv(resumo, ARQ_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-A1 — VALIDACAO DE CONFIG/CANONIZACAO SEM MOTOR ===")
    print(f"status_global_v17_a1={status_global}")
    print(f"abas_reconhecidas={abas_ok}/{total_abas}")
    print(f"campos_criticos_reconhecidos={campos_ok}/{total_campos}")
    print(f"familias_v17_reconhecidas={familias_ok}/{total_familias}")
    print(f"output_dir={OUT_DIR}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    return 0 if status_global == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
