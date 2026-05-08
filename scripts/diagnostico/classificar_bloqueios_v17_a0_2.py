from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

IN_DIR = RAIZ / "saidas" / "diagnostico" / "v17_a0_1"
OUT_DIR = RAIZ / "saidas" / "diagnostico" / "v17_a0_2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARQ_IN_ABAS = IN_DIR / "v17_a0_1_abas_planilha_config.csv"
ARQ_IN_CAMPOS = IN_DIR / "v17_a0_1_campos_por_familia.csv"
ARQ_IN_FONTES_ANTIGAS = IN_DIR / "v17_a0_1_fontes_antigas_detectadas.csv"
ARQ_IN_FONTES_V17 = IN_DIR / "v17_a0_1_fontes_v17_aderencia.csv"
ARQ_IN_SALDO = IN_DIR / "v17_a0_1_ocorrencias_saldo_em_gastos.csv"
ARQ_IN_LOTES_CAIXA = IN_DIR / "v17_a0_1_lotes_caixa_disponivel_candidatos.csv"
ARQ_IN_SWITCHING = IN_DIR / "v17_a0_1_switchings_entrada_candidatos.csv"
ARQ_IN_SAIDA = IN_DIR / "v17_a0_1_pontos_saida_altera_limpa_completa.csv"
ARQ_IN_RESUMO = IN_DIR / "v17_a0_1_resumo.csv"

ARQ_OUT_ABAS = OUT_DIR / "v17_a0_2_classificacao_abas.csv"
ARQ_OUT_CAMPOS = OUT_DIR / "v17_a0_2_classificacao_campos.csv"
ARQ_OUT_FONTES_ANTIGAS = OUT_DIR / "v17_a0_2_classificacao_fontes_antigas.csv"
ARQ_OUT_FONTES_V17 = OUT_DIR / "v17_a0_2_classificacao_fontes_v17.csv"
ARQ_OUT_SALDO = OUT_DIR / "v17_a0_2_classificacao_saldo_gastos.csv"
ARQ_OUT_LOTES_CAIXA = OUT_DIR / "v17_a0_2_classificacao_lotes_caixa_disponivel.csv"
ARQ_OUT_SWITCHING = OUT_DIR / "v17_a0_2_classificacao_switching.csv"
ARQ_OUT_SAIDA = OUT_DIR / "v17_a0_2_classificacao_saida.csv"
ARQ_OUT_MATRIZ = OUT_DIR / "v17_a0_2_matriz_final_decisao.csv"
ARQ_OUT_RESUMO = OUT_DIR / "v17_a0_2_resumo.csv"

SEVERIDADE_ORDEM = {
    "ok": 0,
    "baixo": 1,
    "medio": 2,
    "alto": 3,
    "bloqueante": 4,
}

CAMPOS_OPCIONAIS = {
    ("produto_carteira", "ativo"),
    ("entrada_externa_salario", "descricao"),
    ("entrada_externa_salario", "status"),
    ("pagamento_por_saldo", "descricao"),
    ("pagamento_por_saldo", "pago"),
    ("pagamento_por_lote", "descricao"),
    ("switching_origem", "produto_origem"),
}

CAMPOS_CRITICOS = {
    ("entrada_externa_salario", "data_recebimento"),
    ("entrada_externa_salario", "valor_bruto"),
    ("entrada_externa_salario", "valor_liquido"),
    ("pagamento_por_saldo", "lote_usado"),
    ("pagamento_por_lote", "lote_usado_1"),
    ("lote_caixa_disponivel", "data_recebimento"),
    ("lote_caixa_disponivel", "valor_original"),
    ("switching_origem", "lote_id_antes"),
    ("switching_origem", "valor_liquido_migrado"),
    ("switching_destino_materializado", "lote_id_depois"),
    ("switching_destino_materializado", "valor_liquido_migrado"),
    ("switching_destino_materializado", "investimento"),
}

FONTES_ANTIGAS_ACAO = {
    "saldo_disponivel": ("traduzir_para_v17", "pagamento_por_saldo/caixa_operacional_inferido", "alto"),
    "saldo_disponivel_geral": ("traduzir_para_v17", "caixa_operacional_inferido", "alto"),
    "caixa_pre_aplicacao": ("traduzir_para_v17", "lote_caixa_disponivel", "alto"),
    "lote_resgatavel": ("manter_temporariamente_com_adapter", "lote_investido", "medio"),
    "recebido_disponivel": ("traduzir_para_v17", "entrada_externa_salario/lote_caixa_disponivel", "alto"),
    "estado_pos_switching_janela": ("bloquear_como_estado_canonico", "switching_destino_materializado", "bloqueante"),
    "pos_switch::": ("bloquear_como_identificador_canonico", "switching_destino_materializado", "bloqueante"),
    "sem_saldo_temporal_auditavel": ("manter_como_status_terminal_apenas", "falha_terminal_pos_refactibilizacao", "medio"),
}

FONTES_V17_ACAO_AUSENTE = {
    "produto_carteira": ("criar_tipo_canonico_explicito", "alto"),
    "entrada_externa_salario": ("criar_tipo_canonico_explicito", "bloqueante"),
    "lote_investido": ("criar_tipo_canonico_explicito", "alto"),
    "lote_caixa_disponivel": ("criar_tipo_canonico_explicito", "bloqueante"),
    "pagamento_por_saldo": ("criar_tipo_canonico_explicito", "bloqueante"),
    "pagamento_por_lote": ("criar_tipo_canonico_explicito", "alto"),
    "switching_origem": ("criar_tipo_canonico_explicito", "bloqueante"),
    "switching_destino_materializado": ("criar_tipo_canonico_explicito", "bloqueante"),
}


def _ler_csv(caminho: Path, colunas: list[str]) -> pd.DataFrame:
    if not caminho.exists():
        return pd.DataFrame(columns=colunas)
    try:
        df = pd.read_csv(caminho)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    return df


def _gravar_csv(df: pd.DataFrame, caminho: Path, colunas: list[str]) -> None:
    if df is None or df.empty:
        df = pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    df[colunas].to_csv(caminho, index=False)


def _txt(v: Any) -> str:
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass
    return str(v).strip()


def _bool(v: Any) -> bool:
    s = _txt(v).lower()
    return s in {"true", "1", "1.0", "sim", "s", "yes", "y"}


def _num(v: Any) -> float:
    if v is None:
        return 0.0
    try:
        if pd.isna(v):
            return 0.0
    except Exception:
        pass
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace("R$", "").replace(" ", "").strip()
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def _max_severidade(valores: list[str]) -> str:
    if not valores:
        return "ok"
    return max(valores, key=lambda v: SEVERIDADE_ORDEM.get(v, 0))


def _classificar_abas(df: pd.DataFrame) -> pd.DataFrame:
    linhas: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        familia = _txt(r.get("familia_v17"))
        aba_normativa = _txt(r.get("aba_normativa"))
        existe = _bool(r.get("existe_na_planilha"))
        configurada = _bool(r.get("reconhecida_no_config_abas"))
        status_in = _txt(r.get("status_aderencia"))
        if not aba_normativa:
            classe = "aba_auxiliar_ou_fora_escopo_v17"
            severidade = "baixo"
            acao = "manter_fora_do_escopo_da_v17_a_funcional"
            bloqueia = False
        elif not existe:
            classe = "aba_ausente_real"
            severidade = "bloqueante"
            acao = "corrigir_base_ou_alias_de_aba_antes_da_v17_a"
            bloqueia = True
        elif existe and not configurada:
            classe = "config_incompleto"
            severidade = "bloqueante" if aba_normativa in {"Salários", "Switching"} else "alto"
            acao = "adicionar_familia_ao_config_sem_acionar_motor"
            bloqueia = True
        else:
            classe = "aba_reconhecida"
            severidade = "ok"
            acao = "preservar"
            bloqueia = False
        linhas.append({
            "familia_v17": familia,
            "aba_normativa": aba_normativa,
            "aba_encontrada_planilha": _txt(r.get("aba_encontrada_planilha")),
            "status_entrada_v17_a0_1": status_in,
            "classe_bloqueio_v17_a0_2": classe,
            "severidade": severidade,
            "bloqueia_v17_a_funcional": bloqueia,
            "acao_recomendada": acao,
        })
    return pd.DataFrame(linhas)


def _classificar_campos(df: pd.DataFrame) -> pd.DataFrame:
    linhas: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        familia = _txt(r.get("familia_v17"))
        campo = _txt(r.get("campo_normativo"))
        status = _txt(r.get("status_campo"))
        chave = (familia, campo)
        if status == "reconhecido":
            classe = "campo_reconhecido"
            severidade = "ok"
            acao = "preservar_mapeamento"
            bloqueia = False
        elif status == "aba_ausente":
            classe = "aba_ausente_para_o_campo"
            severidade = "bloqueante"
            acao = "corrigir_aba_ou_config_antes_de_avaliar_campo"
            bloqueia = True
        elif chave in CAMPOS_OPCIONAIS:
            classe = "campo_opcional_nao_reconhecido"
            severidade = "medio"
            acao = "avaliar_alias_ou_documentar_como_opcional"
            bloqueia = False
        elif chave in CAMPOS_CRITICOS:
            classe = "campo_critico_nao_reconhecido"
            severidade = "bloqueante"
            acao = "mapear_alias_no_config_ou_corrigir_nome_da_coluna"
            bloqueia = True
        else:
            classe = "campo_obrigatorio_ou_estrutural_nao_reconhecido"
            severidade = "alto"
            acao = "classificar_manualmente_como_alias_insuficiente_config_incompleto_ou_campo_ausente"
            bloqueia = True
        linhas.append({
            "familia_v17": familia,
            "aba_normativa": _txt(r.get("aba_normativa")),
            "aba_encontrada": _txt(r.get("aba_encontrada")),
            "campo_normativo": campo,
            "coluna_encontrada": _txt(r.get("coluna_encontrada")),
            "status_entrada_v17_a0_1": status,
            "classe_bloqueio_v17_a0_2": classe,
            "severidade": severidade,
            "bloqueia_v17_a_funcional": bloqueia,
            "acao_recomendada": acao,
        })
    return pd.DataFrame(linhas)


def _classificar_fontes_antigas(df: pd.DataFrame) -> pd.DataFrame:
    linhas: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        fonte = _txt(r.get("fonte_antiga"))
        ocorr = int(_num(r.get("ocorrencias_codigo")))
        acao, alvo, severidade = FONTES_ANTIGAS_ACAO.get(fonte, ("auditar_manual", "", "alto"))
        detectada = ocorr > 0
        linhas.append({
            "fonte_antiga": fonte,
            "ocorrencias_codigo": ocorr,
            "arquivos": _txt(r.get("arquivos")),
            "detectada": detectada,
            "classe_bloqueio_v17_a0_2": "taxonomia_antiga_detectada" if detectada else "sem_ocorrencia_estatica",
            "tipo_v17_alvo": alvo,
            "severidade": severidade if detectada else "ok",
            "bloqueia_v17_a_funcional": bool(detectada and severidade in {"alto", "bloqueante"}),
            "acao_recomendada": acao if detectada else "nenhuma",
        })
    return pd.DataFrame(linhas)


def _classificar_fontes_v17(df: pd.DataFrame) -> pd.DataFrame:
    linhas: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        fonte = _txt(r.get("fonte_v17"))
        ocorr = int(_num(r.get("ocorrencias_codigo")))
        if ocorr > 0:
            classe = "tipo_v17_presente_como_token"
            severidade = "medio"
            bloqueia = False
            acao = "auditar_se_o_token_representa_tipo_canonico_real"
        else:
            acao_base, severidade = FONTES_V17_ACAO_AUSENTE.get(fonte, ("criar_tipo_canonico_explicito", "alto"))
            classe = "tipo_v17_ausente_como_tipo_canonico_explicito"
            bloqueia = True
            acao = acao_base
        linhas.append({
            "fonte_v17": fonte,
            "ocorrencias_codigo": ocorr,
            "arquivos": _txt(r.get("arquivos")),
            "classe_bloqueio_v17_a0_2": classe,
            "severidade": severidade,
            "bloqueia_v17_a_funcional": bloqueia,
            "acao_recomendada": acao,
        })
    return pd.DataFrame(linhas)


def _classificar_saldo(df: pd.DataFrame) -> pd.DataFrame:
    linhas: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        valor = _num(r.get("valor"))
        if valor <= 0:
            classe = "ocorrencia_saldo_ambigua_valor_nao_positivo"
            severidade = "medio"
            acao = "auditar_cadastro_do_gasto"
            bloqueia = False
        else:
            classe = "pagamento_por_saldo_historico"
            severidade = "alto"
            acao = "criar_tipo_pagamento_por_saldo_sem_tratar_saldo_como_produto_ou_lote"
            bloqueia = True
        linhas.append({
            "linha_planilha_1base": r.get("linha_planilha_1base"),
            "despesa_id": _txt(r.get("despesa_id")),
            "data": _txt(r.get("data")),
            "descricao": _txt(r.get("descricao")),
            "valor": valor,
            "coluna_lote_usado": _txt(r.get("coluna_lote_usado")),
            "valor_lote_usado": _txt(r.get("valor_lote_usado")),
            "classe_bloqueio_v17_a0_2": classe,
            "severidade": severidade,
            "bloqueia_v17_a_funcional": bloqueia,
            "acao_recomendada": acao,
        })
    return pd.DataFrame(linhas)


def _classificar_lotes_caixa(df: pd.DataFrame) -> pd.DataFrame:
    linhas: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        valor = _num(r.get("valor_original"))
        data_rec = _txt(r.get("data_recebimento"))
        data_apl = _txt(r.get("data_aplicacao"))
        investimento = _txt(r.get("investimento"))
        if data_rec and valor > 0 and not data_apl and not investimento:
            classe = "lote_caixa_disponivel_valido"
            severidade = "bloqueante"
            acao = "preservar_sem_data_aplicacao_artificial_e_mapear_como_lote_caixa_disponivel"
            bloqueia = True
        else:
            classe = "lote_caixa_disponivel_ambiguo"
            severidade = "medio"
            acao = "auditar_cadastro_antes_de_usar_no_estado_temporal"
            bloqueia = False
        linhas.append({
            "linha_planilha_1base": r.get("linha_planilha_1base"),
            "lote_id": _txt(r.get("lote_id")),
            "data_recebimento": data_rec,
            "data_aplicacao": data_apl,
            "valor_original": valor,
            "investimento": investimento,
            "classe_bloqueio_v17_a0_2": classe,
            "severidade": severidade,
            "bloqueia_v17_a_funcional": bloqueia,
            "acao_recomendada": acao,
        })
    return pd.DataFrame(linhas)


def _classificar_switching(df: pd.DataFrame) -> pd.DataFrame:
    linhas: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        lote_antes = _txt(r.get("lote_id_antes"))
        lote_depois = _txt(r.get("lote_id_depois"))
        valor = _num(r.get("valor_liquido_migrado"))
        destino_no_inv = _bool(r.get("destino_tambem_no_inventario"))
        if not lote_antes or not lote_depois or valor <= 0:
            classe = "switching_candidato_com_campo_insuficiente"
            severidade = "bloqueante"
            acao = "corrigir_mapeamento_de_lote_antes_lote_depois_valor_liquido_migrado"
            bloqueia = True
        elif destino_no_inv:
            classe = "switching_destino_ja_no_inventario_risco_dupla_contagem"
            severidade = "bloqueante"
            acao = "reconciliar_destino_com_inventario_antes_de_materializar"
            bloqueia = True
        else:
            classe = "switching_destino_materializavel"
            severidade = "bloqueante"
            acao = "criar_materializacao_diagnostica_de_destino_sem_acionar_motor"
            bloqueia = True
        linhas.append({
            "linha_planilha_1base": r.get("linha_planilha_1base"),
            "aba_switching_encontrada": _txt(r.get("aba_switching_encontrada")),
            "lote_id_antes": lote_antes,
            "lote_id_depois": lote_depois,
            "data_recebimento": _txt(r.get("data_recebimento")),
            "data_aplicacao": _txt(r.get("data_aplicacao")),
            "valor_liquido_migrado": valor,
            "investimento_destino": _txt(r.get("investimento_destino")),
            "destino_tambem_no_inventario": destino_no_inv,
            "classe_bloqueio_v17_a0_2": classe,
            "severidade": severidade,
            "bloqueia_v17_a_funcional": bloqueia,
            "acao_recomendada": acao,
        })
    return pd.DataFrame(linhas)


def _classificar_saida(df: pd.DataFrame) -> pd.DataFrame:
    linhas: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        termo = _txt(r.get("termo_detectado"))
        tipo = _txt(r.get("tipo_ponto"))
        trecho = _txt(r.get("trecho"))
        termo_lower = termo.lower()
        trecho_lower = trecho.lower()
        if "lote sugerido" in termo_lower or "saldo antes" in termo_lower or "bruto" in termo_lower or "líquido" in termo_lower or "liquido" in termo_lower or "saldo remanescente" in termo_lower:
            classe = "campo_operacional_financeiro_alteravel_na_saida"
            severidade = "alto"
            acao = "classificar_como_renderizacao_ou_mover_para_estado_temporal"
            bloqueia = True
        elif "fallback" in termo_lower or "mapa_fontes" in termo_lower or "primeiro_valor" in termo_lower:
            classe = "inferencia_ou_complementacao_operacional_na_saida"
            severidade = "bloqueante"
            acao = "mover_inferencia_para_estado_temporal_ou_motor_antes_da_v17_a"
            bloqueia = True
        elif "normalizar" in termo_lower or "sem_fonte" in termo_lower:
            classe = "normalizacao_de_status_na_saida"
            severidade = "alto"
            acao = "validar_se_apenas_renderiza_status_decidido"
            bloqueia = True
        elif "switching" in termo_lower or "switching" in trecho_lower:
            classe = "representacao_sintetica_de_switching_na_saida"
            severidade = "alto"
            acao = "mover_materializacao_para_estado_temporal_canonico"
            bloqueia = True
        elif "console" in termo_lower or "console" in tipo.lower():
            classe = "renderizacao_console_auditar"
            severidade = "medio"
            acao = "confirmar_que_nao_altera_decisao_operacional"
            bloqueia = False
        else:
            classe = "ponto_saida_requer_triagem_manual"
            severidade = "medio"
            acao = "auditar_trecho_manual"
            bloqueia = False
        linhas.append({
            "arquivo": _txt(r.get("arquivo")),
            "linha": r.get("linha"),
            "termo_detectado": termo,
            "tipo_ponto": tipo,
            "trecho": trecho,
            "classe_bloqueio_v17_a0_2": classe,
            "severidade": severidade,
            "bloqueia_v17_a_funcional": bloqueia,
            "acao_recomendada": acao,
        })
    return pd.DataFrame(linhas)


def _linha_matriz(eixo: str, df: pd.DataFrame, criterio_bloqueio: str) -> dict[str, Any]:
    if df is None or df.empty:
        return {
            "eixo_auditado": eixo,
            "total_itens": 0,
            "total_bloqueantes": 0,
            "severidade_maxima": "ok",
            "decisao": "sem_itens_a_classificar",
            "criterio_bloqueio": criterio_bloqueio,
        }
    total_bloq = int(df["bloqueia_v17_a_funcional"].astype(bool).sum()) if "bloqueia_v17_a_funcional" in df.columns else 0
    severidades = [_txt(v) for v in df.get("severidade", pd.Series(dtype=str)).tolist()]
    sev_max = _max_severidade(severidades)
    decisao = "bloquear_v17_a_funcional" if total_bloq > 0 or sev_max == "bloqueante" else "liberado_para_proxima_auditoria"
    return {
        "eixo_auditado": eixo,
        "total_itens": int(len(df)),
        "total_bloqueantes": total_bloq,
        "severidade_maxima": sev_max,
        "decisao": decisao,
        "criterio_bloqueio": criterio_bloqueio,
    }


def main() -> int:
    df_abas = _ler_csv(ARQ_IN_ABAS, ["familia_v17", "aba_normativa", "aba_encontrada_planilha", "existe_na_planilha", "reconhecida_no_config_abas", "status_aderencia"])
    df_campos = _ler_csv(ARQ_IN_CAMPOS, ["familia_v17", "aba_normativa", "aba_encontrada", "campo_normativo", "coluna_encontrada", "status_campo"])
    df_fontes_antigas = _ler_csv(ARQ_IN_FONTES_ANTIGAS, ["fonte_antiga", "ocorrencias_codigo", "arquivos", "status"])
    df_fontes_v17 = _ler_csv(ARQ_IN_FONTES_V17, ["fonte_v17", "ocorrencias_codigo", "arquivos", "status_aderencia"])
    df_saldo = _ler_csv(ARQ_IN_SALDO, ["linha_planilha_1base", "despesa_id", "data", "descricao", "valor", "coluna_lote_usado", "valor_lote_usado"])
    df_lotes_caixa = _ler_csv(ARQ_IN_LOTES_CAIXA, ["linha_planilha_1base", "lote_id", "data_recebimento", "data_aplicacao", "valor_original", "investimento"])
    df_switching = _ler_csv(ARQ_IN_SWITCHING, ["linha_planilha_1base", "aba_switching_encontrada", "lote_id_antes", "lote_id_depois", "data_recebimento", "data_aplicacao", "valor_liquido_migrado", "investimento_destino", "destino_tambem_no_inventario"])
    df_saida = _ler_csv(ARQ_IN_SAIDA, ["arquivo", "linha", "termo_detectado", "tipo_ponto", "trecho"])

    out_abas = _classificar_abas(df_abas)
    out_campos = _classificar_campos(df_campos)
    out_fontes_antigas = _classificar_fontes_antigas(df_fontes_antigas)
    out_fontes_v17 = _classificar_fontes_v17(df_fontes_v17)
    out_saldo = _classificar_saldo(df_saldo)
    out_lotes_caixa = _classificar_lotes_caixa(df_lotes_caixa)
    out_switching = _classificar_switching(df_switching)
    out_saida = _classificar_saida(df_saida)

    _gravar_csv(out_abas, ARQ_OUT_ABAS, ["familia_v17", "aba_normativa", "aba_encontrada_planilha", "status_entrada_v17_a0_1", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    _gravar_csv(out_campos, ARQ_OUT_CAMPOS, ["familia_v17", "aba_normativa", "aba_encontrada", "campo_normativo", "coluna_encontrada", "status_entrada_v17_a0_1", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    _gravar_csv(out_fontes_antigas, ARQ_OUT_FONTES_ANTIGAS, ["fonte_antiga", "ocorrencias_codigo", "arquivos", "detectada", "classe_bloqueio_v17_a0_2", "tipo_v17_alvo", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    _gravar_csv(out_fontes_v17, ARQ_OUT_FONTES_V17, ["fonte_v17", "ocorrencias_codigo", "arquivos", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    _gravar_csv(out_saldo, ARQ_OUT_SALDO, ["linha_planilha_1base", "despesa_id", "data", "descricao", "valor", "coluna_lote_usado", "valor_lote_usado", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    _gravar_csv(out_lotes_caixa, ARQ_OUT_LOTES_CAIXA, ["linha_planilha_1base", "lote_id", "data_recebimento", "data_aplicacao", "valor_original", "investimento", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    _gravar_csv(out_switching, ARQ_OUT_SWITCHING, ["linha_planilha_1base", "aba_switching_encontrada", "lote_id_antes", "lote_id_depois", "data_recebimento", "data_aplicacao", "valor_liquido_migrado", "investimento_destino", "destino_tambem_no_inventario", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    _gravar_csv(out_saida, ARQ_OUT_SAIDA, ["arquivo", "linha", "termo_detectado", "tipo_ponto", "trecho", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])

    matriz = pd.DataFrame([
        _linha_matriz("abas", out_abas, "aba V17 ausente ou existente sem config bloqueia"),
        _linha_matriz("campos", out_campos, "campo critico/estrutural nao reconhecido bloqueia"),
        _linha_matriz("fontes_antigas", out_fontes_antigas, "taxonomia antiga alto/bloqueante requer traducao"),
        _linha_matriz("fontes_v17", out_fontes_v17, "tipo V17 ausente como canonico explicito bloqueia"),
        _linha_matriz("saldo_em_gastos", out_saldo, "Saldo deve virar pagamento_por_saldo antes da V17-A"),
        _linha_matriz("lotes_caixa_disponivel", out_lotes_caixa, "lote caixa valido deve ser preservado sem data_aplicacao artificial"),
        _linha_matriz("switching", out_switching, "switching de entrada deve materializar/reconciliar destino"),
        _linha_matriz("saida_canonica", out_saida, "saida nao pode inferir/corrigir estado operacional"),
    ])
    decisao_global = "bloquear_v17_a_funcional" if (matriz["decisao"] == "bloquear_v17_a_funcional").any() else "liberado_para_v17_a_funcional"
    matriz["decisao_global_v17_a0_2"] = decisao_global
    _gravar_csv(matriz, ARQ_OUT_MATRIZ, ["eixo_auditado", "total_itens", "total_bloqueantes", "severidade_maxima", "decisao", "criterio_bloqueio", "decisao_global_v17_a0_2"])

    resumo = []
    for _, r in matriz.iterrows():
        resumo.append({
            "metrica": f"{r['eixo_auditado']}_total_itens",
            "valor": r["total_itens"],
            "status": r["decisao"],
            "observacao": r["criterio_bloqueio"],
        })
        resumo.append({
            "metrica": f"{r['eixo_auditado']}_total_bloqueantes",
            "valor": r["total_bloqueantes"],
            "status": r["severidade_maxima"],
            "observacao": "bloqueios classificados pela V17-A0.2",
        })
    resumo.append({
        "metrica": "decisao_global_v17_a0_2",
        "valor": decisao_global,
        "status": "bloqueio_preventivo" if decisao_global == "bloquear_v17_a_funcional" else "liberado",
        "observacao": "nao alterar motor antes de resolver os eixos bloqueantes",
    })
    _gravar_csv(pd.DataFrame(resumo), ARQ_OUT_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-A0.2 — CLASSIFICACAO DIAGNOSTICA DOS BLOQUEIOS ===")
    print(f"input_dir={IN_DIR}")
    print(f"output_dir={OUT_DIR}")
    print(f"decisao_global_v17_a0_2={decisao_global}")
    for _, r in matriz.iterrows():
        print(
            f"{r['eixo_auditado']}: total={r['total_itens']}; "
            f"bloqueantes={r['total_bloqueantes']}; severidade_maxima={r['severidade_maxima']}; "
            f"decisao={r['decisao']}"
        )
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
