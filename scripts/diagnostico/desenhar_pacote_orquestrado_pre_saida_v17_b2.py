from __future__ import annotations

from pathlib import Path
import sys
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

IN_B1 = RAIZ / "saidas" / "diagnostico" / "v17_b1" / "v17_b1_matriz_orquestracao_fonte_verdade.csv"
OUT = RAIZ / "saidas" / "diagnostico" / "v17_b2"
OUT.mkdir(parents=True, exist_ok=True)

ARQ_COMPONENTES = OUT / "v17_b2_componentes_pacote_orquestrado_pre_saida.csv"
ARQ_CAMPOS = OUT / "v17_b2_campos_minimos_pacote_orquestrado_pre_saida.csv"
ARQ_MATRIZ = OUT / "v17_b2_matriz_saida_para_pacote_orquestrado.csv"
ARQ_VALIDACOES = OUT / "v17_b2_validacoes_minimas_pre_saida.csv"
ARQ_RESUMO = OUT / "v17_b2_resumo.csv"

COMPONENTES = [
    ("recomendacoes_futuras", "quadro final de pagamentos futuros ja escolhido antes da saida", True),
    ("decisoes_pagamento", "decisao final por pagamento, fonte escolhida e bloqueio auditavel", True),
    ("fontes_pagamento_v17", "fontes de pagamento ja classificadas pela taxonomia V17", True),
    ("estado_temporal_switching", "origem e destino de switching ja materializados ou reconciliados", True),
    ("saldos_financeiros_lotes", "saldos bruto, liquido, imposto e remanescente ja calculados", True),
    ("ranking_informativo", "ranking apenas para apresentacao, sem decidir destino operacional", False),
    ("auditoria_orquestracao", "origem, status e rastreabilidade do pacote pre-saida", True),
]

CAMPOS = {
    "recomendacoes_futuras": [
        ("pagamento_id", "str", True),
        ("data_pagamento", "date|str_iso", True),
        ("conta_descricao", "str", True),
        ("valor_pagamento", "float", True),
        ("status_recomendacao", "str", True),
        ("motivo_bloqueio", "str", False),
        ("pacote_do_dia", "str", False),
        ("necessita_switching", "bool|str", False),
        ("fonte_verdade_origem", "str", True),
    ],
    "decisoes_pagamento": [
        ("pagamento_id", "str", True),
        ("tipo_fonte_escolhida_v17", "enum", True),
        ("fonte_id", "str", True),
        ("valor_bruto_resgate", "float", False),
        ("valor_imposto", "float", False),
        ("valor_liquido_resgate", "float", False),
        ("saldo_antes", "float", False),
        ("saldo_depois", "float", False),
        ("status_decisao", "str", True),
    ],
    "fontes_pagamento_v17": [
        ("fonte_id", "str", True),
        ("tipo_v17", "enum", True),
        ("familia_entrada", "str", True),
        ("data_materializacao", "date|str_iso", True),
        ("valor_disponivel_bruto", "float", False),
        ("valor_disponivel_liquido", "float", False),
        ("status_elegibilidade", "str", True),
    ],
    "estado_temporal_switching": [
        ("switching_id", "str", True),
        ("lote_id_origem", "str", True),
        ("lote_id_destino", "str", True),
        ("data_switching", "date|str_iso", True),
        ("produto_destino", "str", True),
        ("valor_liquido_migrado", "float", True),
        ("status_reconciliacao", "str", True),
    ],
    "saldos_financeiros_lotes": [
        ("fonte_id", "str", True),
        ("data_referencia", "date|str_iso", True),
        ("saldo_bruto", "float", True),
        ("imposto_estimado", "float", False),
        ("saldo_liquido", "float", True),
        ("principal_remanescente", "float", False),
        ("status_lote", "str", True),
    ],
    "ranking_informativo": [
        ("produto_id", "str", True),
        ("posicao_ranking", "int", False),
        ("score", "float", False),
        ("uso_permitido", "enum_informativo", True),
    ],
    "auditoria_orquestracao": [
        ("componente", "str", True),
        ("origem_funcional", "str", True),
        ("status_orquestracao", "str", True),
        ("mensagem_auditoria", "str", False),
    ],
}

VALIDACOES = [
    ("recomendacoes_tem_pagamento_id_unico", "recomendacoes_futuras", True),
    ("decisoes_cobrem_recomendacoes", "decisoes_pagamento", True),
    ("fontes_usam_taxonomia_v17", "fontes_pagamento_v17", True),
    ("saldo_nao_e_produto_carteira", "fontes_pagamento_v17", True),
    ("switching_destino_reconciliado_ou_materializado", "estado_temporal_switching", True),
    ("saldos_financeiros_sem_recalculo_saida", "saldos_financeiros_lotes", True),
    ("ranking_apenas_informativo", "ranking_informativo", False),
    ("auditoria_origem_obrigatoria", "auditoria_orquestracao", True),
]

MAPA_FONTE_COMPONENTE = {
    "pacote_orquestrado_pre_saida.recomendacoes_futuras": "recomendacoes_futuras",
    "pacote_orquestrado_pre_saida.decisoes_pagamento": "decisoes_pagamento",
    "pacote_orquestrado_pre_saida.fontes_pagamento_v17": "fontes_pagamento_v17",
    "pacote_orquestrado_pre_saida.estado_temporal_switching": "estado_temporal_switching",
    "pacote_orquestrado_pre_saida.saldos_financeiros_lotes": "saldos_financeiros_lotes",
    "pacote_orquestrado_pre_saida.ranking_informativo": "ranking_informativo",
    "pacote_orquestrado_pre_saida.estado_caixa_pagamentos": "fontes_pagamento_v17",
    "pacote_orquestrado_pre_saida.replay_pagamentos_consolidado": "decisoes_pagamento",
    "pacote_orquestrado_pre_saida.destinos_switching_reconciliados": "estado_temporal_switching",
}


def gravar(df: pd.DataFrame, arq: Path, cols: list[str]) -> None:
    if df is None or df.empty:
        df = pd.DataFrame(columns=cols)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df[cols].to_csv(arq, index=False)


def ler_b1() -> pd.DataFrame:
    cols = ["fonte_detectada", "classe_risco", "prioridade", "qtd_ocorrencias", "linhas_min_max", "fonte_verdade_unica_proposta", "acao_orquestracao_anterior_saida"]
    if not IN_B1.exists():
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(IN_B1)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df


def main() -> int:
    df_b1 = ler_b1()

    df_componentes = pd.DataFrame([
        {
            "pacote": "pacote_orquestrado_pre_saida",
            "componente": c,
            "fonte_verdade_unica": f"pacote_orquestrado_pre_saida.{c}",
            "papel": p,
            "obrigatorio_antes_v17_funcional": o,
            "altera_codigo_v17_b2": False,
        }
        for c, p, o in COMPONENTES
    ])

    linhas_campos = []
    for componente, campos in CAMPOS.items():
        for campo, tipo, obrigatorio in campos:
            linhas_campos.append({
                "pacote": "pacote_orquestrado_pre_saida",
                "componente": componente,
                "campo_minimo": campo,
                "tipo_esperado": tipo,
                "obrigatorio": obrigatorio,
                "estado": "desenho_diagnostico",
                "altera_codigo_v17_b2": False,
            })
    df_campos = pd.DataFrame(linhas_campos)

    matriz = []
    for _, row in df_b1.iterrows():
        fv = str(row.get("fonte_verdade_unica_proposta") or "")
        comp = MAPA_FONTE_COMPONENTE.get(fv, fv.split(".")[-1] if "." in fv else "")
        matriz.append({
            "fonte_detectada_saida": row.get("fonte_detectada"),
            "classe_risco": row.get("classe_risco"),
            "prioridade_b1": row.get("prioridade"),
            "fonte_verdade_unica_proposta": fv,
            "componente_pacote": comp,
            "acao_pre_saida": row.get("acao_orquestracao_anterior_saida"),
            "qtd_ocorrencias_b1": row.get("qtd_ocorrencias"),
            "linhas_min_max_b1": row.get("linhas_min_max"),
            "decisao_v17_b2": "campo_minimo_definido_no_pacote" if comp in CAMPOS else "pendente_triangulacao",
        })
    df_matriz = pd.DataFrame(matriz)

    df_valid = pd.DataFrame([
        {"validacao": v, "componente": c, "bloqueia_v17_funcional": b, "estado": "desenho_diagnostico"}
        for v, c, b in VALIDACOES
    ])

    componentes = int(df_componentes["componente"].nunique())
    campos_total = int(len(df_campos))
    campos_obrig = int(df_campos["obrigatorio"].astype(bool).sum())
    linhas_b1 = int(len(df_matriz))
    sem_comp = int((df_matriz["decisao_v17_b2"] != "campo_minimo_definido_no_pacote").sum()) if not df_matriz.empty else 0
    valid_bloq = int(df_valid["bloqueia_v17_funcional"].astype(bool).sum())
    status = "ok_diagnostico" if componentes == 7 and campos_total > 0 and sem_comp == 0 else "falha_diagnostica"
    decisao = "manter_bloqueio_v17_funcional_ate_implementar_pacote_pre_saida"

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_b2", "valor": status, "status": "ok" if status == "ok_diagnostico" else "falha", "observacao": "desenho diagnostico do pacote pre-saida"},
        {"metrica": "decisao_v17_funcional", "valor": decisao, "status": "bloqueio_preventivo", "observacao": "V17-B2 nao implementa consumo funcional"},
        {"metrica": "componentes_pacote_definidos", "valor": componentes, "status": "ok", "observacao": "componentes do pacote"},
        {"metrica": "campos_minimos_definidos", "valor": campos_total, "status": "ok", "observacao": "campos por componente"},
        {"metrica": "campos_obrigatorios", "valor": campos_obrig, "status": "ok", "observacao": "campos obrigatorios"},
        {"metrica": "validacoes_minimas_definidas", "valor": len(df_valid), "status": "ok", "observacao": "validacoes pre-saida"},
        {"metrica": "validacoes_bloqueantes", "valor": valid_bloq, "status": "bloqueio_preventivo", "observacao": "falhas bloqueiam V17 funcional"},
        {"metrica": "linhas_matriz_b1_mapeadas_para_pacote", "valor": linhas_b1, "status": "ok", "observacao": "cruzamento com V17-B1"},
        {"metrica": "fontes_b1_sem_componente_pacote", "valor": sem_comp, "status": "ok" if sem_comp == 0 else "falha", "observacao": "deve ser zero"},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True, "status": "ok", "observacao": "script diagnostico isolado"},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True, "status": "ok", "observacao": "sem edicao documental normativa"},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True, "status": "ok", "observacao": "sem consumo por motor/ranking/switching"},
        {"metrica": "confirmacao_sem_alterar_saida_canonica", "valor": True, "status": "ok", "observacao": "saida_canonica nao alterada"},
    ])

    gravar(df_componentes, ARQ_COMPONENTES, ["pacote", "componente", "fonte_verdade_unica", "papel", "obrigatorio_antes_v17_funcional", "altera_codigo_v17_b2"])
    gravar(df_campos, ARQ_CAMPOS, ["pacote", "componente", "campo_minimo", "tipo_esperado", "obrigatorio", "estado", "altera_codigo_v17_b2"])
    gravar(df_matriz, ARQ_MATRIZ, ["fonte_detectada_saida", "classe_risco", "prioridade_b1", "fonte_verdade_unica_proposta", "componente_pacote", "acao_pre_saida", "qtd_ocorrencias_b1", "linhas_min_max_b1", "decisao_v17_b2"])
    gravar(df_valid, ARQ_VALIDACOES, ["validacao", "componente", "bloqueia_v17_funcional", "estado"])
    gravar(resumo, ARQ_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-B2 — DESENHO DIAGNOSTICO DO PACOTE ORQUESTRADO PRE-SAIDA ===")
    print(f"status_global_v17_b2={status}")
    print(f"decisao_v17_funcional={decisao}")
    print(f"componentes_pacote_definidos={componentes}")
    print(f"campos_minimos_definidos={campos_total}")
    print(f"campos_obrigatorios={campos_obrig}")
    print(f"validacoes_minimas_definidas={len(df_valid)}")
    print(f"validacoes_bloqueantes={valid_bloq}")
    print(f"linhas_matriz_b1_mapeadas_para_pacote={linhas_b1}")
    print(f"fontes_b1_sem_componente_pacote={sem_comp}")
    print(f"output_dir={OUT}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    print("confirmacao_sem_alterar_saida_canonica=true")
    return 0 if status == "ok_diagnostico" else 2


if __name__ == "__main__":
    raise SystemExit(main())
