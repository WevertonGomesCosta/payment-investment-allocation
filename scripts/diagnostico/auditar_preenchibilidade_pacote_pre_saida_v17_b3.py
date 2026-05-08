from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.carregador_config import carregar_config
from nucleo.leitor_planilha import carregar_planilha

IN_B2 = RAIZ / "saidas" / "diagnostico" / "v17_b2" / "v17_b2_campos_minimos_pacote_orquestrado_pre_saida.csv"
OUT = RAIZ / "saidas" / "diagnostico" / "v17_b3"
OUT.mkdir(parents=True, exist_ok=True)

ARQ_CAMPOS = OUT / "v17_b3_preenchibilidade_campos_minimos.csv"
ARQ_COMPONENTES = OUT / "v17_b3_preenchibilidade_por_componente.csv"
ARQ_FONTES = OUT / "v17_b3_fontes_existentes_inspecionadas.csv"
ARQ_LACUNAS = OUT / "v17_b3_lacunas_para_estado_temporal_futuro.csv"
ARQ_RESUMO = OUT / "v17_b3_resumo.csv"

REGRAS = {
    "recomendacoes_futuras": {
        "fontes": ["motor_recomendacao_pagamentos_switching_v1.quadro_recomendacoes", "decisao_local_v1.quadro_decisao_local_v1", "Todos os Gastos"],
        "preenchiveis": {"pagamento_id", "data_pagamento", "conta_descricao", "valor_pagamento", "status_recomendacao", "motivo_bloqueio", "pacote_do_dia", "necessita_switching"},
        "ambiguos": {"fonte_verdade_origem"},
        "dependentes": set(),
    },
    "decisoes_pagamento": {
        "fontes": ["decisao_local_v1.quadro_decisao_local_v1", "motor_recomendacao_pagamentos_switching_v1.quadro_recomendacoes", "recomputacao_sequencial_central_v1"],
        "preenchiveis": {"pagamento_id", "tipo_fonte_escolhida_v17", "fonte_id", "status_decisao"},
        "ambiguos": {"valor_bruto_resgate", "valor_imposto", "valor_liquido_resgate"},
        "dependentes": {"saldo_antes", "saldo_depois"},
    },
    "fontes_pagamento_v17": {
        "fontes": ["V17-A2 taxonomia", "V17-A3 semantica", "Inventário de Lotes", "Salários", "Todos os Gastos", "Switching"],
        "preenchiveis": {"fonte_id", "tipo_v17", "familia_entrada", "data_materializacao", "status_elegibilidade"},
        "ambiguos": {"valor_disponivel_bruto"},
        "dependentes": {"valor_disponivel_liquido"},
    },
    "estado_temporal_switching": {
        "fontes": ["Switching", "V17-A3 auditoria switching"],
        "preenchiveis": {"switching_id", "lote_id_origem", "lote_id_destino", "data_switching", "produto_destino", "valor_liquido_migrado", "status_reconciliacao"},
        "ambiguos": set(),
        "dependentes": set(),
    },
    "saldos_financeiros_lotes": {
        "fontes": ["replay_passado.lotes_apos_replay", "ledger_temporal_conjunto", "estado financeiro futuro"],
        "preenchiveis": {"fonte_id", "data_referencia", "status_lote"},
        "ambiguos": {"principal_remanescente"},
        "dependentes": {"saldo_bruto", "imposto_estimado", "saldo_liquido"},
    },
    "ranking_informativo": {
        "fontes": ["ranking_amostra", "Carteira"],
        "preenchiveis": {"produto_id", "posicao_ranking", "score", "uso_permitido"},
        "ambiguos": set(),
        "dependentes": set(),
    },
    "auditoria_orquestracao": {
        "fontes": ["V17-B1", "V17-B2", "orquestrador futuro"],
        "preenchiveis": {"componente", "mensagem_auditoria"},
        "ambiguos": {"origem_funcional"},
        "dependentes": {"status_orquestracao"},
    },
}


def gravar(df: pd.DataFrame, arq: Path, cols: list[str]) -> None:
    if df is None or df.empty:
        df = pd.DataFrame(columns=cols)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df[cols].to_csv(arq, index=False)


def ler_campos_b2() -> pd.DataFrame:
    cols = ["pacote", "componente", "campo_minimo", "tipo_esperado", "obrigatorio", "estado", "altera_codigo_v17_b2"]
    if not IN_B2.exists():
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(IN_B2)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df


def inspecionar_fontes_planilha() -> pd.DataFrame:
    linhas = []
    try:
        pacote_config = carregar_config(raiz_repositorio=RAIZ)
        config = pacote_config.conteudo
        pacote = carregar_planilha(config, raiz_repositorio=RAIZ, carregar_todas_as_abas=True)
        abas_cfg = config.get("abas", {}) if isinstance(config.get("abas"), dict) else {}
        quadros = pacote.quadros_canonicos
        for key, aba in abas_cfg.items():
            df = quadros.get(str(aba))
            linhas.append({
                "fonte_inspecionada": f"planilha.{key}",
                "nome_aba": aba,
                "existe": df is not None,
                "linhas": int(len(df)) if isinstance(df, pd.DataFrame) else 0,
                "colunas": " | ".join(map(str, df.columns)) if isinstance(df, pd.DataFrame) else "",
                "status": "ok" if isinstance(df, pd.DataFrame) else "ausente",
            })
    except Exception as exc:
        linhas.append({
            "fonte_inspecionada": "planilha",
            "nome_aba": "",
            "existe": False,
            "linhas": 0,
            "colunas": "",
            "status": f"falha_inspecao:{type(exc).__name__}",
        })
    return pd.DataFrame(linhas)


def classificar_campo(componente: str, campo: str, obrigatorio: bool) -> tuple[str, str, str]:
    regra = REGRAS.get(componente, {"preenchiveis": set(), "ambiguos": set(), "dependentes": set(), "fontes": []})
    if campo in regra["preenchiveis"]:
        return "preenchivel_com_quadros_existentes", "ok", " | ".join(regra["fontes"])
    if campo in regra["ambiguos"]:
        return "ambiguo_depende_de_padronizacao", "pendente", " | ".join(regra["fontes"])
    if campo in regra["dependentes"]:
        return "dependente_de_estado_temporal_futuro", "bloqueio_preventivo" if obrigatorio else "pendente", " | ".join(regra["fontes"])
    return "ausente_sem_fonte_mapeada", "bloqueio_preventivo" if obrigatorio else "pendente", ""


def main() -> int:
    df_b2 = ler_campos_b2()
    df_fontes = inspecionar_fontes_planilha()

    linhas = []
    for _, row in df_b2.iterrows():
        componente = str(row.get("componente") or "")
        campo = str(row.get("campo_minimo") or "")
        obrigatorio = str(row.get("obrigatorio") or "").lower() in {"true", "1", "sim"}
        classe, status, fontes = classificar_campo(componente, campo, obrigatorio)
        linhas.append({
            "pacote": row.get("pacote") or "pacote_orquestrado_pre_saida",
            "componente": componente,
            "campo_minimo": campo,
            "tipo_esperado": row.get("tipo_esperado"),
            "obrigatorio": obrigatorio,
            "classe_preenchibilidade": classe,
            "status_v17_b3": status,
            "fontes_candidatas": fontes,
            "decisao_v17_b3": "pode_compor_pacote_diagnostico" if status == "ok" else "nao_abrir_consumo_funcional_sem_resolver",
            "altera_codigo_v17_b3": False,
        })
    df_campos = pd.DataFrame(linhas)

    comp = []
    if not df_campos.empty:
        for componente, sub in df_campos.groupby("componente", dropna=False):
            total = int(len(sub))
            obrig = int(sub["obrigatorio"].astype(bool).sum())
            preench = int((sub["classe_preenchibilidade"] == "preenchivel_com_quadros_existentes").sum())
            amb = int((sub["classe_preenchibilidade"] == "ambiguo_depende_de_padronizacao").sum())
            dep = int((sub["classe_preenchibilidade"] == "dependente_de_estado_temporal_futuro").sum())
            aus = int((sub["classe_preenchibilidade"] == "ausente_sem_fonte_mapeada").sum())
            bloqueios = int((sub["status_v17_b3"] == "bloqueio_preventivo").sum())
            comp.append({
                "componente": componente,
                "campos_total": total,
                "campos_obrigatorios": obrig,
                "preenchiveis_quadros_existentes": preench,
                "ambiguos": amb,
                "dependentes_estado_temporal": dep,
                "ausentes_sem_fonte": aus,
                "bloqueios_preventivos": bloqueios,
                "decisao_componente": "ok_diagnostico" if bloqueios == 0 else "depende_estado_temporal_ou_padronizacao",
            })
    df_comp = pd.DataFrame(comp)

    df_lacunas = df_campos[df_campos["status_v17_b3"].isin(["bloqueio_preventivo", "pendente"])].copy() if not df_campos.empty else pd.DataFrame()

    total_campos = int(len(df_campos))
    preenchiveis = int((df_campos["classe_preenchibilidade"] == "preenchivel_com_quadros_existentes").sum()) if not df_campos.empty else 0
    ambiguos = int((df_campos["classe_preenchibilidade"] == "ambiguo_depende_de_padronizacao").sum()) if not df_campos.empty else 0
    dependentes = int((df_campos["classe_preenchibilidade"] == "dependente_de_estado_temporal_futuro").sum()) if not df_campos.empty else 0
    ausentes = int((df_campos["classe_preenchibilidade"] == "ausente_sem_fonte_mapeada").sum()) if not df_campos.empty else 0
    bloqueios = int((df_campos["status_v17_b3"] == "bloqueio_preventivo").sum()) if not df_campos.empty else 0
    status = "ok_diagnostico"
    decisao = "manter_bloqueio_v17_funcional_ate_resolver_campos_nao_preenchiveis"

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_b3", "valor": status, "status": "ok", "observacao": "auditoria diagnostica de preenchibilidade"},
        {"metrica": "decisao_v17_funcional", "valor": decisao, "status": "bloqueio_preventivo", "observacao": "V17-B3 nao implementa pacote"},
        {"metrica": "campos_minimos_auditados", "valor": total_campos, "status": "ok" if total_campos else "falha", "observacao": "campos lidos da V17-B2"},
        {"metrica": "campos_preenchiveis_quadros_existentes", "valor": preenchiveis, "status": "info", "observacao": "podem ser montados diagnosticamente"},
        {"metrica": "campos_ambiguos", "valor": ambiguos, "status": "pendente", "observacao": "dependem padronizacao/ponte"},
        {"metrica": "campos_dependentes_estado_temporal_futuro", "valor": dependentes, "status": "bloqueio_preventivo" if dependentes else "ok", "observacao": "exigem estado temporal"},
        {"metrica": "campos_ausentes_sem_fonte_mapeada", "valor": ausentes, "status": "bloqueio_preventivo" if ausentes else "ok", "observacao": "deve ser zero ou justificado"},
        {"metrica": "bloqueios_preventivos_campos_obrigatorios", "valor": bloqueios, "status": "bloqueio_preventivo" if bloqueios else "ok", "observacao": "impede consumo funcional"},
        {"metrica": "componentes_auditados", "valor": int(df_comp["componente"].nunique()) if not df_comp.empty else 0, "status": "ok", "observacao": "componentes do pacote"},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True, "status": "ok", "observacao": "script diagnostico isolado"},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True, "status": "ok", "observacao": "sem edicao documental normativa"},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True, "status": "ok", "observacao": "sem consumo por motor/ranking/switching"},
        {"metrica": "confirmacao_sem_alterar_saida_canonica", "valor": True, "status": "ok", "observacao": "saida_canonica nao alterada"},
    ])

    gravar(df_campos, ARQ_CAMPOS, ["pacote", "componente", "campo_minimo", "tipo_esperado", "obrigatorio", "classe_preenchibilidade", "status_v17_b3", "fontes_candidatas", "decisao_v17_b3", "altera_codigo_v17_b3"])
    gravar(df_comp, ARQ_COMPONENTES, ["componente", "campos_total", "campos_obrigatorios", "preenchiveis_quadros_existentes", "ambiguos", "dependentes_estado_temporal", "ausentes_sem_fonte", "bloqueios_preventivos", "decisao_componente"])
    gravar(df_fontes, ARQ_FONTES, ["fonte_inspecionada", "nome_aba", "existe", "linhas", "colunas", "status"])
    gravar(df_lacunas, ARQ_LACUNAS, ["pacote", "componente", "campo_minimo", "tipo_esperado", "obrigatorio", "classe_preenchibilidade", "status_v17_b3", "fontes_candidatas", "decisao_v17_b3", "altera_codigo_v17_b3"])
    gravar(resumo, ARQ_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-B3 — AUDITORIA DIAGNOSTICA DE PREENCHIBILIDADE DO PACOTE PRE-SAIDA ===")
    print(f"status_global_v17_b3={status}")
    print(f"decisao_v17_funcional={decisao}")
    print(f"campos_minimos_auditados={total_campos}")
    print(f"campos_preenchiveis_quadros_existentes={preenchiveis}")
    print(f"campos_ambiguos={ambiguos}")
    print(f"campos_dependentes_estado_temporal_futuro={dependentes}")
    print(f"campos_ausentes_sem_fonte_mapeada={ausentes}")
    print(f"bloqueios_preventivos_campos_obrigatorios={bloqueios}")
    print(f"componentes_auditados={int(df_comp['componente'].nunique()) if not df_comp.empty else 0}")
    print(f"output_dir={OUT}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    print("confirmacao_sem_alterar_saida_canonica=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
