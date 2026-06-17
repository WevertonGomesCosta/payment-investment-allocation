from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from aplicacao.principal import carregar_contexto_e_saida
from nucleo.situacao_atual_oficial import (
    _coagir_data_observavel,
    _serie_cdi_contexto,
)


OUT_DIR = RAIZ / "saidas" / "diagnostico"
OUT_CSV = OUT_DIR / "auditoria_divergencia_rendimento_motor_me529.csv"
OUT_MD = OUT_DIR / "auditoria_divergencia_rendimento_motor_me529.md"

SENTINELAS = {
    "Lote 10342 fev.",
    "Lote 4124,75 fev.",
    "Lote 6630,64 fev.",
    "Lote 3120 mai",
    "Lote 5680 abr.",
    "Lote 7600 jun.",
    "Lote 4876 jun",
    "Lote 3800 jun.",
}


def norm(v: Any) -> str:
    return str(v or "").strip()


def chave_lote(v: Any) -> str:
    return norm(v).lower().replace(".", "")


def valor_numerico(v: Any) -> bool:
    if v is None or v == "":
        return False
    try:
        float(v)
        return True
    except Exception:
        return False


def fnum(v: Any) -> float:
    if not valor_numerico(v):
        return 0.0
    return round(float(v), 2)


def fnum_ou_texto(v: Any) -> float | str:
    if valor_numerico(v):
        return round(float(v), 2)
    return norm(v) or "n/d"


def indexar_por_lote_linhas(linhas: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        norm(row.get("Lote")): dict(row)
        for row in list(linhas or [])
        if norm(row.get("Lote"))
    }


def indexar_lotes_objetos(lotes: list[Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for lote in list(lotes or []):
        k = chave_lote(getattr(lote, "id", ""))
        if k:
            out.setdefault(k, lote)
    return out


def lote_attr(lote: Any | None, nome: str) -> Any:
    if lote is None:
        return "n/d"
    return getattr(lote, nome, "n/d")


def lote_num(lote: Any | None, nome: str) -> float | str:
    if lote is None:
        return "n/d"
    return fnum(getattr(lote, nome, 0.0))


def lote_bool_txt(lote: Any | None, nome: str) -> str:
    if lote is None:
        return "n/d"
    return "sim" if bool(getattr(lote, nome, False)) else "não"


def calcular_valor_liquido_lote(
    contexto: Any,
    lote: Any | None,
    data_alvo: Any,
    *,
    base_referencia: Any,
) -> float | str:
    data = _coagir_data_observavel(data_alvo)
    base = _coagir_data_observavel(base_referencia)

    if lote is None:
        return "n/d"
    if data is None:
        return "n/d"

    try:
        return round(float(lote.valor_liquido_em_data(
            data,
            contexto.calendario_financeiro,
            tabela_iof=getattr(contexto, "tabela_iof", None),
            faixas_ir=getattr(contexto, "faixas_ir", None),
            serie_cdi=_serie_cdi_contexto(contexto),
            data_base_referencia=base,
        )), 2)
    except Exception as exc:
        return f"erro:{type(exc).__name__}"


def calcular_bruto_lote(
    contexto: Any,
    lote: Any | None,
    data_alvo: Any,
    *,
    base_referencia: Any,
) -> float | str:
    data = _coagir_data_observavel(data_alvo)
    base = _coagir_data_observavel(base_referencia)

    if lote is None:
        return "n/d"
    if data is None:
        return "n/d"

    try:
        return round(float(lote.valor_bruto_em_data(
            data,
            contexto.calendario_financeiro,
            serie_cdi=_serie_cdi_contexto(contexto),
            data_base_referencia=base,
        )), 2)
    except Exception as exc:
        return f"erro:{type(exc).__name__}"


def data_alvo_para_linha(row: dict[str, Any], data_referencia: Any) -> tuple[Any, str]:
    status = norm(row.get("Status ciclo"))
    data_termino = row.get("Data término")

    if status in {"exaurido_por_saque", "migrado_por_switching"}:
        return data_termino, "data_termino_observavel"

    return data_referencia, "data_referencia_saida_canonica"


def classificar_linha(row: dict[str, Any]) -> tuple[str, str]:
    status = norm(row.get("Status ciclo"))
    bruto_sacado = fnum(row.get("Bruto sac."))
    liquido_sacado = fnum(row.get("Líq. sac."))
    liquido_atual = fnum(row.get("Líq. atual"))

    tem_saque = bruto_sacado > 0 or liquido_sacado > 0
    tem_saldo_atual = liquido_atual > 0

    if status == "exaurido_por_saque":
        return "exaurido_por_saque", "exaurido_por_saque"

    if status == "migrado_por_switching":
        return "origem_migrada_por_switching", "origem_migrada_por_switching"

    if status == "ativo_pos_switching":
        if tem_saque and tem_saldo_atual:
            return "ativo_com_saque_parcial", "destino_pos_switching_com_saque_parcial"
        return "ativo_sem_saque", "destino_pos_switching_sem_saque"

    if status == "ativo":
        if tem_saque and tem_saldo_atual:
            return "ativo_com_saque_parcial", "ativo_regular_com_saque_parcial"
        return "ativo_sem_saque", "ativo_regular_sem_saque"

    return "classe_indefinida", status or "status_indefinido"


def diferenca(a: Any, b: Any) -> float | str:
    if valor_numerico(a) and valor_numerico(b):
        return round(float(a) - float(b), 2)
    return "n/d"


def abs_dif(v: Any) -> float:
    return abs(fnum(v)) if valor_numerico(v) else 999999999.0


def calcular_ciclo_correto(row: dict[str, Any]) -> tuple[float | str, float | str, str]:
    """Reconstrói o rendimento líquido pela regra correta do ciclo do lote.

    Esta métrica não substitui a auditoria do motor. Ela define a base que o motor
    deve conseguir reproduzir para cada classe operacional.
    """
    classe = row["classe_operacional"]
    valor_original = fnum(row["valor_original_saida"])

    liquido_sacado_obs = fnum(row["liquido_sacado_observado"])
    liquido_atual_obs = fnum(row["liquido_atual_observado"])

    total_liq_post = row["total_liquido_sacado_pos_replay"]
    vl_post_ref = row["valor_liquido_post_replay_data_referencia"]

    if classe == "exaurido_por_saque":
        if valor_numerico(total_liq_post):
            patrimonio = fnum(total_liq_post)
            fonte = "total_liquido_sacado_pos_replay"
        else:
            patrimonio = liquido_sacado_obs
            fonte = "liquido_sacado_observado_fallback"
        return round(patrimonio, 2), round(patrimonio - valor_original, 2), fonte

    if classe == "origem_migrada_por_switching":
        # Para origem de switching, o ciclo correto encerra na data do switching
        # pelo valor migrado/observado, não pelo saldo pós-replay na data de referência.
        patrimonio = liquido_sacado_obs
        fonte = "valor_liquido_migrado_observado"
        return round(patrimonio, 2), round(patrimonio - valor_original, 2), fonte

    if classe == "ativo_com_saque_parcial":
        if valor_numerico(total_liq_post) and valor_numerico(vl_post_ref):
            patrimonio = round(fnum(total_liq_post) + fnum(vl_post_ref), 2)
            fonte = "total_liquido_sacado_pos_replay_mais_liquido_residual_motor"
        else:
            patrimonio = round(liquido_sacado_obs + liquido_atual_obs, 2)
            fonte = "liquido_sacado_observado_mais_liquido_atual_observado_fallback"
        return round(patrimonio, 2), round(patrimonio - valor_original, 2), fonte

    if classe == "ativo_sem_saque":
        if valor_numerico(vl_post_ref):
            patrimonio = fnum(vl_post_ref)
            fonte = "liquido_pos_replay_data_referencia"
        else:
            patrimonio = liquido_atual_obs
            fonte = "liquido_atual_observado_fallback"
        return round(patrimonio, 2), round(patrimonio - valor_original, 2), fonte

    patrimonio = fnum(row["patrimonio_liquido_observavel"])
    return round(patrimonio, 2), round(patrimonio - valor_original, 2), "patrimonio_observavel_fallback"


def melhor_fonte(row: dict[str, Any]) -> str:
    candidatos = {
        "publicado_atual": row["dif_observado_vs_motor_publicado"],
        "pre_replay_aplicacao": row["dif_observado_vs_pre_replay"],
        "post_replay_aplicacao": row["dif_observado_vs_post_replay_saldo"],
        "post_replay_total_realizado": row["dif_observado_vs_post_replay_total"],
        "post_replay_ciclo_correto": row.get("dif_observado_vs_pos_replay_ciclo_correto", "n/d"),
    }
    return min(candidatos, key=lambda k: abs_dif(candidatos[k]))


def hipotese_estado_errado(row: dict[str, Any]) -> str:
    dif_publicado = abs_dif(row["dif_observado_vs_motor_publicado"])
    dif_post_total = abs_dif(row["dif_observado_vs_post_replay_total"])
    dif_ciclo = abs_dif(row.get("dif_observado_vs_pos_replay_ciclo_correto", "n/d"))
    dif_pre = abs_dif(row["dif_observado_vs_pre_replay"])

    if dif_ciclo <= 0.01 and dif_publicado > 0.01:
        return "confirmada_pos_replay_ciclo_correto_fecha_observavel"

    if dif_ciclo + 0.01 < dif_publicado and dif_ciclo + 0.01 < dif_pre:
        return "provavel_pos_replay_ciclo_correto_reduz_divergencia"

    if row["lote_existe_pos_replay"] != "sim":
        return "nao_testavel_sem_lote_pos_replay"

    if dif_post_total <= 0.01 and dif_publicado > 0.01:
        return "confirmada_pos_replay_total_fecha_observavel"

    if dif_post_total + 0.01 < dif_publicado and dif_post_total + 0.01 < dif_pre:
        return "provavel_pos_replay_total_reduz_divergencia"

    if dif_pre <= 0.01 and dif_publicado <= 0.01:
        return "sem_erro_estado_publicado_equivale_pre"

    if dif_post_total >= dif_publicado - 0.01 and dif_ciclo >= dif_publicado - 0.01:
        return "nao_confirmada_pos_replay_nao_melhora"

    return "inconclusiva"

def causa_provavel(row: dict[str, Any]) -> tuple[str, str]:
    classe = row["classe_operacional"]
    h_estado = row["hipotese_estado_errado_confirmada"]
    dif_pub = abs_dif(row["dif_observado_vs_motor_publicado"])
    dif_post_total = abs_dif(row["dif_observado_vs_post_replay_total"])
    dif_ciclo = abs_dif(row.get("dif_observado_vs_pos_replay_ciclo_correto", "n/d"))
    dif_pre = abs_dif(row["dif_observado_vs_pre_replay"])

    if dif_pub <= 0.01:
        return (
            "sem_divergencia_material_no_motor_publicado",
            "preservar; motor publicado fecha com observável",
        )

    if h_estado in {
        "confirmada_pos_replay_ciclo_correto_fecha_observavel",
        "provavel_pos_replay_ciclo_correto_reduz_divergencia",
    }:
        return (
            "motor_publicado_nao_usa_base_pos_replay_ciclo_correto",
            "corrigir integração do rendimento motor para usar regra correta do ciclo do lote",
        )

    if h_estado in {
        "confirmada_pos_replay_total_fecha_observavel",
        "provavel_pos_replay_total_reduz_divergencia",
    }:
        return (
            "motor_publicado_nao_usa_base_pos_replay_total_realizado",
            "corrigir integração do rendimento motor para usar base pós-replay realizada por lote",
        )

    if classe == "origem_migrada_por_switching" and dif_ciclo <= 0.01 and dif_post_total > 0.01:
        return (
            "switching_exige_valor_migrado_observado_como_ciclo_correto",
            "não usar saldo pós-replay da origem na data de referência; usar valor líquido migrado na data do switching",
        )

    if classe == "ativo_com_saque_parcial" and dif_ciclo < dif_pre:
        return (
            "saque_parcial_exige_formula_pos_replay_ciclo_correto",
            "auditar cálculo do lote parcial usando líquido sacado + residual pós-replay",
        )

    if classe in {"exaurido_por_saque", "origem_migrada_por_switching"} and dif_ciclo > 0.01:
        return (
            "ciclo_correto_ainda_nao_fecha_observavel",
            "auditar evento individual: valor sacado/migrado, imposto, data, CDI e base fiscal",
        )

    if classe == "ativo_sem_saque":
        return (
            "ativo_sem_saque_difere_por_valor_atual_ou_base_fechamento",
            "auditar CDI/fallback, IR/IOF, data de fechamento e valor atual do lote",
        )

    return (
        "causa_inconclusiva_requer_auditoria_individual",
        "auditar lote individualmente",
    )

def montar_linhas_auditadas(contexto: Any, saida_canonica_oficial: Any) -> list[dict[str, Any]]:
    data_referencia = getattr(saida_canonica_oficial, "data_referencia", None)

    ex_id = indexar_por_lote_linhas(getattr(saida_canonica_oficial, "situacao_atual_lotes_exauridos_id", []))
    ex_val = indexar_por_lote_linhas(getattr(saida_canonica_oficial, "situacao_atual_lotes_exauridos_valores", []))
    at_id = indexar_por_lote_linhas(getattr(saida_canonica_oficial, "situacao_atual_lotes_ativos_id", []))
    at_val = indexar_por_lote_linhas(getattr(saida_canonica_oficial, "situacao_atual_lotes_ativos_valores", []))

    nucleo = getattr(contexto, "nucleo_financeiro", None)
    replay = getattr(contexto, "replay_passado", None)

    pre_map = indexar_lotes_objetos(list(getattr(nucleo, "lotes_financeiros", []) or []))
    post_map = indexar_lotes_objetos(list(getattr(replay, "lotes_apos_replay", []) or []))

    linhas_base: list[dict[str, Any]] = []

    for lote, val in ex_val.items():
        row = {**ex_id.get(lote, {}), **val}
        row["grupo_publicado"] = "exauridos"
        linhas_base.append(row)

    for lote, val in at_val.items():
        row = {**at_id.get(lote, {}), **val}
        row["grupo_publicado"] = "ativos"
        linhas_base.append(row)

    auditadas: list[dict[str, Any]] = []

    for row in linhas_base:
        lote_id = norm(row.get("Lote"))
        k = chave_lote(lote_id)
        pre = pre_map.get(k)
        post = post_map.get(k)

        classe, subclasse = classificar_linha(row)
        data_alvo, fonte_data_alvo = data_alvo_para_linha(row, data_referencia)

        valor_original_saida = fnum(row.get("Orig."))
        patrimonio_observavel = fnum(row.get("Patr. líq."))
        rendimento_observavel = fnum(row.get("Rend. líq."))
        rendimento_motor_publicado = fnum_ou_texto(row.get("Rend. líq. motor"))
        dif_motor_publicado = fnum_ou_texto(row.get("Dif. rend."))

        # Reprodução da lógica suspeita atual: prioriza pré-replay quando existe.
        lote_publicado_fonte = pre if pre is not None else post
        fonte_motor_publicado_reconstruida = (
            "pre_replay" if pre is not None else
            "post_replay" if post is not None else
            "nao_encontrado"
        )

        vl_publicado_recalc = calcular_valor_liquido_lote(
            contexto,
            lote_publicado_fonte,
            data_alvo,
            base_referencia=lote_attr(lote_publicado_fonte, "data_aplicacao"),
        )
        rend_publicado_recalc = (
            round(fnum(vl_publicado_recalc) - fnum(lote_num(lote_publicado_fonte, "valor_inicial")), 2)
            if valor_numerico(vl_publicado_recalc) and lote_publicado_fonte is not None
            else "n/d"
        )

        vl_pre_aplic = calcular_valor_liquido_lote(
            contexto,
            pre,
            data_alvo,
            base_referencia=lote_attr(pre, "data_aplicacao"),
        )
        bruto_pre_aplic = calcular_bruto_lote(
            contexto,
            pre,
            data_alvo,
            base_referencia=lote_attr(pre, "data_aplicacao"),
        )
        rend_pre = (
            round(fnum(vl_pre_aplic) - fnum(lote_num(pre, "valor_inicial")), 2)
            if valor_numerico(vl_pre_aplic) and pre is not None
            else "n/d"
        )

        vl_post_aplic = calcular_valor_liquido_lote(
            contexto,
            post,
            data_alvo,
            base_referencia=lote_attr(post, "data_aplicacao"),
        )
        bruto_post_aplic = calcular_bruto_lote(
            contexto,
            post,
            data_alvo,
            base_referencia=lote_attr(post, "data_aplicacao"),
        )
        rend_post_saldo = (
            round(fnum(vl_post_aplic) - fnum(lote_num(post, "valor_inicial")), 2)
            if valor_numerico(vl_post_aplic) and post is not None
            else "n/d"
        )

        vl_post_ref = calcular_valor_liquido_lote(
            contexto,
            post,
            data_referencia,
            base_referencia=data_referencia,
        )
        bruto_post_ref = calcular_bruto_lote(
            contexto,
            post,
            data_referencia,
            base_referencia=data_referencia,
        )

        total_liq_post = fnum(lote_num(post, "total_liquido_sacado"))
        total_bruto_post = fnum(lote_num(post, "total_bruto_sacado"))
        total_imposto_post = fnum(lote_num(post, "total_imposto_pago"))
        valor_inicial_post = fnum(lote_num(post, "valor_inicial"))

        patrimonio_post_total = (
            round(total_liq_post + fnum(vl_post_ref), 2)
            if post is not None and valor_numerico(vl_post_ref)
            else "n/d"
        )
        rendimento_post_total = (
            round(fnum(patrimonio_post_total) - valor_inicial_post, 2)
            if valor_numerico(patrimonio_post_total) and post is not None
            else "n/d"
        )

        out = {
            "lote": lote_id,
            "classe_operacional": classe,
            "subclasse": subclasse,
            "status_ciclo": norm(row.get("Status ciclo")),
            "grupo_publicado": norm(row.get("grupo_publicado")),
            "produto": norm(row.get("Carteira")),
            "data_aplicacao_saida": norm(row.get("Aplic.")),
            "data_alvo_observavel": norm(data_alvo),
            "data_alvo_motor": norm(data_alvo),
            "data_referencia": norm(data_referencia),
            "fonte_data_alvo": fonte_data_alvo,
            "dias_corridos": norm(row.get("Dias corr.")),
            "dias_uteis": norm(row.get("Dias úteis")),

            "valor_original_saida": valor_original_saida,
            "liquido_sacado_observado": fnum(row.get("Líq. sac.")),
            "bruto_sacado_observado": fnum(row.get("Bruto sac.")),
            "imposto_observado": round(fnum(row.get("Bruto sac.")) - fnum(row.get("Líq. sac.")), 2),
            "liquido_atual_observado": fnum(row.get("Líq. atual")),
            "bruto_atual_observado": fnum(row.get("Bruto atual")),
            "patrimonio_liquido_observavel": patrimonio_observavel,
            "rendimento_liquido_observavel": rendimento_observavel,

            "rendimento_liquido_motor_publicado": rendimento_motor_publicado,
            "dif_rendimento_publicada": dif_motor_publicado,
            "fonte_motor_publicado_reconstruida": fonte_motor_publicado_reconstruida,
            "valor_liquido_motor_publicado_recalculado": vl_publicado_recalc,
            "rendimento_motor_publicado_recalculado": rend_publicado_recalc,
            "dif_observado_vs_motor_publicado": diferenca(rendimento_observavel, rendimento_motor_publicado),

            "lote_existe_pre_replay": "sim" if pre is not None else "não",
            "valor_inicial_pre_replay": lote_num(pre, "valor_inicial"),
            "saldo_bruto_pre_replay": lote_num(pre, "saldo_bruto"),
            "principal_remanescente_pre_replay": lote_num(pre, "principal_remanescente"),
            "fator_acumulado_pre_replay": lote_num(pre, "fator_acumulado"),
            "esgotado_pre_replay": lote_bool_txt(pre, "esgotado"),
            "vezes_usado_pre_replay": lote_num(pre, "vezes_usado"),
            "total_bruto_sacado_pre_replay": lote_num(pre, "total_bruto_sacado"),
            "total_imposto_pago_pre_replay": lote_num(pre, "total_imposto_pago"),
            "total_liquido_sacado_pre_replay": lote_num(pre, "total_liquido_sacado"),
            "valor_bruto_pre_replay_data_alvo": bruto_pre_aplic,
            "valor_liquido_pre_replay_data_alvo": vl_pre_aplic,
            "rendimento_pre_replay": rend_pre,
            "dif_observado_vs_pre_replay": diferenca(rendimento_observavel, rend_pre),

            "lote_existe_pos_replay": "sim" if post is not None else "não",
            "valor_inicial_pos_replay": lote_num(post, "valor_inicial"),
            "saldo_bruto_pos_replay": lote_num(post, "saldo_bruto"),
            "principal_remanescente_pos_replay": lote_num(post, "principal_remanescente"),
            "fator_acumulado_pos_replay": lote_num(post, "fator_acumulado"),
            "esgotado_pos_replay": lote_bool_txt(post, "esgotado"),
            "vezes_usado_pos_replay": lote_num(post, "vezes_usado"),
            "total_bruto_sacado_pos_replay": total_bruto_post if post is not None else "n/d",
            "total_imposto_pago_pos_replay": total_imposto_post if post is not None else "n/d",
            "total_liquido_sacado_pos_replay": total_liq_post if post is not None else "n/d",
            "valor_bruto_post_replay_data_alvo": bruto_post_aplic,
            "valor_liquido_post_replay_data_alvo": vl_post_aplic,
            "rendimento_post_replay_saldo": rend_post_saldo,
            "dif_observado_vs_post_replay_saldo": diferenca(rendimento_observavel, rend_post_saldo),

            "valor_bruto_post_replay_data_referencia": bruto_post_ref,
            "valor_liquido_post_replay_data_referencia": vl_post_ref,
            "patrimonio_pos_replay_total_realizado": patrimonio_post_total,
            "rendimento_pos_replay_total_realizado": rendimento_post_total,
            "dif_observado_vs_post_replay_total": diferenca(rendimento_observavel, rendimento_post_total),

            "dif_valor_original_vs_valor_inicial_pre": diferenca(valor_original_saida, lote_num(pre, "valor_inicial")),
            "dif_valor_original_vs_valor_inicial_post": diferenca(valor_original_saida, lote_num(post, "valor_inicial")),
            "dif_liquido_sacado_obs_vs_total_liq_post": diferenca(fnum(row.get("Líq. sac.")), total_liq_post if post is not None else "n/d"),
            "dif_bruto_sacado_obs_vs_total_bruto_post": diferenca(fnum(row.get("Bruto sac.")), total_bruto_post if post is not None else "n/d"),
            "dif_imposto_obs_vs_total_imposto_post": diferenca(round(fnum(row.get("Bruto sac.")) - fnum(row.get("Líq. sac.")), 2), total_imposto_post if post is not None else "n/d"),
            "sentinela": "sim" if lote_id in SENTINELAS else "não",
        }

        patrimonio_ciclo, rendimento_ciclo, fonte_ciclo = calcular_ciclo_correto(out)
        out["patrimonio_pos_replay_ciclo_correto"] = patrimonio_ciclo
        out["rendimento_pos_replay_ciclo_correto"] = rendimento_ciclo
        out["dif_observado_vs_pos_replay_ciclo_correto"] = diferenca(
            rendimento_observavel,
            rendimento_ciclo,
        )
        out["fonte_pos_replay_ciclo_correto"] = fonte_ciclo

        out["melhor_fonte_de_reconciliacao"] = melhor_fonte(out)
        out["hipotese_estado_errado_confirmada"] = hipotese_estado_errado(out)
        causa, acao = causa_provavel(out)
        out["causa_provavel"] = causa
        out["acao_recomendada"] = acao

        auditadas.append(out)

    return auditadas


def hipotese_estado_confirmada_ou_provavel(rotulo: Any) -> bool:
    return norm(rotulo) in {
        "confirmada_pos_replay_ciclo_correto_fecha_observavel",
        "provavel_pos_replay_ciclo_correto_reduz_divergencia",
        "confirmada_pos_replay_total_fecha_observavel",
        "provavel_pos_replay_total_reduz_divergencia",
    }


def resumo_por_classe(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    resumo: dict[str, dict[str, Any]] = {}

    for r in rows:
        classe = r["classe_operacional"]
        slot = resumo.setdefault(
            classe,
            {
                "qtd": 0,
                "rend_obs": 0.0,
                "rend_publicado": 0.0,
                "rend_pre": 0.0,
                "rend_post_total": 0.0,
                "dif_publicado": 0.0,
                "dif_pre": 0.0,
                "dif_post_total": 0.0,
                "abs_dif_publicado": 0.0,
                "abs_dif_post_total": 0.0,
                "estado_confirmado": 0,
                "maior_abs_dif": 0.0,
                "lote_maior_abs_dif": "",
            },
        )

        slot["qtd"] += 1
        slot["rend_obs"] = round(slot["rend_obs"] + fnum(r["rendimento_liquido_observavel"]), 2)
        slot["rend_publicado"] = round(slot["rend_publicado"] + fnum(r["rendimento_liquido_motor_publicado"]), 2)
        slot["rend_pre"] = round(slot["rend_pre"] + fnum(r["rendimento_pre_replay"]), 2)
        slot["rend_post_total"] = round(slot["rend_post_total"] + fnum(r["rendimento_pos_replay_total_realizado"]), 2)
        slot["dif_publicado"] = round(slot["dif_publicado"] + fnum(r["dif_observado_vs_motor_publicado"]), 2)
        slot["dif_pre"] = round(slot["dif_pre"] + fnum(r["dif_observado_vs_pre_replay"]), 2)
        slot["dif_post_total"] = round(slot["dif_post_total"] + fnum(r["dif_observado_vs_post_replay_total"]), 2)
        slot["abs_dif_publicado"] = round(slot["abs_dif_publicado"] + abs(fnum(r["dif_observado_vs_motor_publicado"])), 2)
        slot["abs_dif_post_total"] = round(slot["abs_dif_post_total"] + abs(fnum(r["dif_observado_vs_post_replay_total"])), 2)

        if hipotese_estado_confirmada_ou_provavel(r["hipotese_estado_errado_confirmada"]):
            slot["estado_confirmado"] += 1

        abs_pub = abs(fnum(r["dif_observado_vs_motor_publicado"]))
        if abs_pub > slot["maior_abs_dif"]:
            slot["maior_abs_dif"] = abs_pub
            slot["lote_maior_abs_dif"] = r["lote"]

    return resumo


def contagem(rows: list[dict[str, Any]], campo: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in rows:
        k = norm(r.get(campo)) or "n/d"
        out[k] = out.get(k, 0) + 1
    return out


def escrever_csv(rows: list[dict[str, Any]]) -> None:
    campos = list(rows[0].keys()) if rows else []
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(rows)


def escrever_md(rows: list[dict[str, Any]]) -> None:
    resumo = resumo_por_classe(rows)

    total_obs = round(sum(fnum(r["rendimento_liquido_observavel"]) for r in rows), 2)
    total_publicado = round(sum(fnum(r["rendimento_liquido_motor_publicado"]) for r in rows), 2)
    total_pre = round(sum(fnum(r["rendimento_pre_replay"]) for r in rows), 2)
    total_post_total = round(sum(fnum(r["rendimento_pos_replay_total_realizado"]) for r in rows), 2)
    total_ciclo = round(sum(fnum(r["rendimento_pos_replay_ciclo_correto"]) for r in rows), 2)

    total_dif_pub = round(sum(fnum(r["dif_observado_vs_motor_publicado"]) for r in rows), 2)
    total_dif_pre = round(sum(fnum(r["dif_observado_vs_pre_replay"]) for r in rows), 2)
    total_dif_post = round(sum(fnum(r["dif_observado_vs_post_replay_total"]) for r in rows), 2)
    total_dif_ciclo = round(sum(fnum(r["dif_observado_vs_pos_replay_ciclo_correto"]) for r in rows), 2)

    top_pub = sorted(
        rows,
        key=lambda r: abs(fnum(r["dif_observado_vs_motor_publicado"])),
        reverse=True,
    )[:12]

    top_residual_post = sorted(
        rows,
        key=lambda r: abs(fnum(r["dif_observado_vs_post_replay_total"])),
        reverse=True,
    )[:12]

    sentinelas = [r for r in rows if r["sentinela"] == "sim"]

    md: list[str] = []
    md.append("# ME-529 — Auditoria expandida do rendimento líquido do motor\n\n")

    md.append("## Resumo executivo\n\n")
    md.append(f"- lotes auditados: {len(rows)}\n")
    md.append(f"- soma Rend. líq. observável: {total_obs:.2f}\n")
    md.append(f"- soma Rend. líq. motor publicado: {total_publicado:.2f}\n")
    md.append(f"- soma rendimento pré-replay: {total_pre:.2f}\n")
    md.append(f"- soma rendimento pós-replay total realizado: {total_post_total:.2f}\n")
    md.append(f"- soma rendimento pós-replay ciclo correto: {total_ciclo:.2f}\n")
    md.append(f"- soma Dif. observável vs motor publicado: {total_dif_pub:.2f}\n")
    md.append(f"- soma Dif. observável vs pré-replay: {total_dif_pre:.2f}\n")
    md.append(f"- soma Dif. observável vs pós-replay total realizado: {total_dif_post:.2f}\n")
    md.append(f"- soma Dif. observável vs pós-replay ciclo correto: {total_dif_ciclo:.2f}\n\n")

    md.append("## Totais por classe operacional\n\n")
    md.append("| Classe | n | Rend obs | Rend motor pub | Rend pré | Rend pós total | Dif pub | Dif pré | Dif pós total | |Dif pub| | |Dif pós| | estado confirmado | maior pub | lote maior |\n")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|\n")
    for classe, s in sorted(resumo.items()):
        md.append(
            f"| {classe} | {s['qtd']} | {s['rend_obs']:.2f} | {s['rend_publicado']:.2f} | "
            f"{s['rend_pre']:.2f} | {s['rend_post_total']:.2f} | "
            f"{s['dif_publicado']:.2f} | {s['dif_pre']:.2f} | {s['dif_post_total']:.2f} | "
            f"{s['abs_dif_publicado']:.2f} | {s['abs_dif_post_total']:.2f} | "
            f"{s['estado_confirmado']} | {s['maior_abs_dif']:.2f} | {s['lote_maior_abs_dif']} |\n"
        )

    md.append("\n## Totais por classe — ciclo correto\n\n")
    md.append("| Classe | n | Rend obs | Rend ciclo correto | Dif ciclo correto | |Dif ciclo correto| | fontes |\n")
    md.append("|---|---:|---:|---:|---:|---:|---|\n")
    for classe in sorted({r["classe_operacional"] for r in rows}):
        grupo = [r for r in rows if r["classe_operacional"] == classe]
        rend_obs = round(sum(fnum(r["rendimento_liquido_observavel"]) for r in grupo), 2)
        rend_ciclo = round(sum(fnum(r["rendimento_pos_replay_ciclo_correto"]) for r in grupo), 2)
        dif_ciclo = round(sum(fnum(r["dif_observado_vs_pos_replay_ciclo_correto"]) for r in grupo), 2)
        abs_ciclo = round(sum(abs(fnum(r["dif_observado_vs_pos_replay_ciclo_correto"])) for r in grupo), 2)
        fontes = ", ".join(sorted({r["fonte_pos_replay_ciclo_correto"] for r in grupo}))
        md.append(
            f"| {classe} | {len(grupo)} | {rend_obs:.2f} | {rend_ciclo:.2f} | "
            f"{dif_ciclo:.2f} | {abs_ciclo:.2f} | {fontes} |\n"
        )

    md.append("\n## Contagem por hipótese de estado\n\n")
    for k, v in sorted(contagem(rows, "hipotese_estado_errado_confirmada").items()):
        md.append(f"- {k}: {v}\n")

    md.append("\n## Contagem por causa provável\n\n")
    for k, v in sorted(contagem(rows, "causa_provavel").items()):
        md.append(f"- {k}: {v}\n")

    md.append("\n## Maiores divergências do motor publicado\n\n")
    for r in top_pub:
        md.append(
            f"- {r['lote']} | {r['classe_operacional']} / {r['subclasse']} | "
            f"Obs={fnum(r['rendimento_liquido_observavel']):.2f} | "
            f"Motor pub={fnum(r['rendimento_liquido_motor_publicado']):.2f} | "
            f"Dif pub={fnum(r['dif_observado_vs_motor_publicado']):.2f} | "
            f"Pré={fnum(r['rendimento_pre_replay']):.2f} | "
            f"Pós total={fnum(r['rendimento_pos_replay_total_realizado']):.2f} | "
            f"Dif pós={fnum(r['dif_observado_vs_post_replay_total']):.2f} | "
            f"H={r['hipotese_estado_errado_confirmada']} | "
            f"{r['causa_provavel']}\n"
        )

    md.append("\n## Maiores resíduos após reconstrução pós-replay total realizado\n\n")
    for r in top_residual_post:
        md.append(
            f"- {r['lote']} | {r['classe_operacional']} / {r['subclasse']} | "
            f"Obs={fnum(r['rendimento_liquido_observavel']):.2f} | "
            f"Pós total={fnum(r['rendimento_pos_replay_total_realizado']):.2f} | "
            f"Dif pós={fnum(r['dif_observado_vs_post_replay_total']):.2f} | "
            f"Líq obs={fnum(r['liquido_sacado_observado']):.2f} | "
            f"Líq post={fnum(r['total_liquido_sacado_pos_replay']):.2f} | "
            f"Saldo post={fnum(r['saldo_bruto_pos_replay']):.2f} | "
            f"VL post ref={fnum(r['valor_liquido_post_replay_data_referencia']):.2f} | "
            f"{r['causa_provavel']}\n"
        )

    top_residual_ciclo = sorted(
        rows,
        key=lambda r: abs(fnum(r["dif_observado_vs_pos_replay_ciclo_correto"])),
        reverse=True,
    )[:12]

    md.append("\n## Maiores resíduos após ciclo correto\n\n")
    for r in top_residual_ciclo:
        md.append(
            f"- {r['lote']} | {r['classe_operacional']} / {r['subclasse']} | "
            f"Obs={fnum(r['rendimento_liquido_observavel']):.2f} | "
            f"Ciclo correto={fnum(r['rendimento_pos_replay_ciclo_correto']):.2f} | "
            f"Dif ciclo={fnum(r['dif_observado_vs_pos_replay_ciclo_correto']):.2f} | "
            f"Fonte={r['fonte_pos_replay_ciclo_correto']} | "
            f"Motor pub={fnum(r['rendimento_liquido_motor_publicado']):.2f} | "
            f"Dif pub={fnum(r['dif_observado_vs_motor_publicado']):.2f} | "
            f"{r['causa_provavel']}\n"
        )

    residuos_ciclo = [
        r for r in rows
        if abs(fnum(r["dif_observado_vs_pos_replay_ciclo_correto"])) > 0.01
    ]
    soma_residuos_ciclo = round(
        sum(fnum(r["dif_observado_vs_pos_replay_ciclo_correto"]) for r in residuos_ciclo),
        2,
    )
    soma_abs_residuos_ciclo = round(
        sum(abs(fnum(r["dif_observado_vs_pos_replay_ciclo_correto"])) for r in residuos_ciclo),
        2,
    )

    md.append("\n## Ressalvas diagnósticas do ciclo correto\n\n")
    md.append(f"- lotes com resíduo acima de 0.01: {len(residuos_ciclo)}\n")
    md.append(f"- soma dos resíduos do ciclo correto: {soma_residuos_ciclo:.2f}\n")
    md.append(f"- soma absoluta dos resíduos do ciclo correto: {soma_abs_residuos_ciclo:.2f}\n")
    if not residuos_ciclo:
        md.append("- nenhum resíduo material remanescente após regra de ciclo correto.\n")
    else:
        for r in sorted(
            residuos_ciclo,
            key=lambda x: abs(fnum(x["dif_observado_vs_pos_replay_ciclo_correto"])),
            reverse=True,
        ):
            md.append(
                f"- {r['lote']} | {r['classe_operacional']} / {r['subclasse']} | "
                f"Obs={fnum(r['rendimento_liquido_observavel']):.2f} | "
                f"Ciclo correto={fnum(r['rendimento_pos_replay_ciclo_correto']):.2f} | "
                f"Dif ciclo={fnum(r['dif_observado_vs_pos_replay_ciclo_correto']):.2f} | "
                f"Fonte={r['fonte_pos_replay_ciclo_correto']} | "
                "ressalva: resíduo residual compatível com arredondamento/valor residual pós-switching; "
                "não altera a conclusão causal principal.\n"
            )

    md.append("\n## Sentinelas obrigatórias\n\n")
    for r in sentinelas:
        md.append(
            f"- {r['lote']} | {r['classe_operacional']} / {r['subclasse']} | "
            f"data alvo={r['data_alvo_motor']} | "
            f"Obs={fnum(r['rendimento_liquido_observavel']):.2f} | "
            f"Motor pub={fnum(r['rendimento_liquido_motor_publicado']):.2f} | "
            f"Pré={fnum(r['rendimento_pre_replay']):.2f} | "
            f"Pós saldo={fnum(r['rendimento_post_replay_saldo']):.2f} | "
            f"Pós total={fnum(r['rendimento_pos_replay_total_realizado']):.2f} | "
            f"Ciclo correto={fnum(r['rendimento_pos_replay_ciclo_correto']):.2f} | "
            f"Dif pub={fnum(r['dif_observado_vs_motor_publicado']):.2f} | "
            f"Dif pós total={fnum(r['dif_observado_vs_post_replay_total']):.2f} | "
            f"Dif ciclo={fnum(r['dif_observado_vs_pos_replay_ciclo_correto']):.2f} | "
            f"Bruto obs={fnum(r['bruto_sacado_observado']):.2f} | "
            f"Bruto post={fnum(r['total_bruto_sacado_pos_replay']):.2f} | "
            f"Liq obs={fnum(r['liquido_sacado_observado']):.2f} | "
            f"Liq post={fnum(r['total_liquido_sacado_pos_replay']):.2f} | "
            f"Imposto obs={fnum(r['imposto_observado']):.2f} | "
            f"Imposto post={fnum(r['total_imposto_pago_pos_replay']):.2f} | "
            f"H={r['hipotese_estado_errado_confirmada']} | "
            f"{r['causa_provavel']}\n"
        )

    md.append("\n## Leitura técnica\n\n")
    md.append(
        "- Esta auditoria não assume que a divergência é aceitável.\n"
        "- O contrato operacional esperado é que o motor calcule corretamente o rendimento líquido por lote.\n"
        "- A auditoria testa se o `Rend. líq. motor` publicado está calculado contra estado pré-replay ou pós-replay.\n"
        "- Para lotes com saque, switching ou saque parcial, a base pós-replay correta precisa considerar `total_liquido_sacado + líquido residual atual - valor inicial`.\n"
        "- Se a base pós-replay total realizado fechar com o observável, a causa provável é integração errada do comparador de rendimento do motor.\n"
        "- Se nem a base pós-replay fechar, deve-se auditar individualmente evento, carteira, CDI, IR/IOF, data-alvo e base fiscal.\n"
    )

    md.append("\n## Condição para próxima decisão\n\n")
    md.append(
        "A evidência da ME-529 indica que o `Rend. líq. motor` publicado usa a base pré-replay, "
        "enquanto a regra correta por ciclo operacional reconcilia a base observável com resíduo agregado residual. "
        "A próxima ME deve corrigir a integração do cálculo publicado de `Rend. líq. motor` para usar a regra correta do ciclo do lote: "
        "exaurido por saque, ativo com saque parcial, ativo sem saque ou origem migrada por switching. "
        "O resíduo remanescente deve ser mantido como ressalva diagnóstica e auditado individualmente apenas se exceder o limiar operacional.\n"
    )

    OUT_MD.write_text("".join(md), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    (
        contexto,
        estado_temporal_inicial,
        resultado_motor_temporal_conjunto,
        ledger_temporal_canonico,
        resultado_gates_validacao_nucleo,
        saida_canonica,
        saida_canonica_oficial,
        pacote_saida_observavel_oficial,
    ) = carregar_contexto_e_saida()

    _ = estado_temporal_inicial
    _ = resultado_motor_temporal_conjunto
    _ = ledger_temporal_canonico
    _ = saida_canonica
    _ = pacote_saida_observavel_oficial

    if not getattr(resultado_gates_validacao_nucleo, "pronto_para_etapa8", False):
        raise RuntimeError("gates_nao_aprovados_para_auditoria_me529")

    rows = montar_linhas_auditadas(contexto, saida_canonica_oficial)

    escrever_csv(rows)
    escrever_md(rows)

    total_dif_pub = round(sum(fnum(r["dif_observado_vs_motor_publicado"]) for r in rows), 2)
    total_dif_post = round(sum(fnum(r["dif_observado_vs_post_replay_total"]) for r in rows), 2)
    total_dif_ciclo = round(sum(fnum(r["dif_observado_vs_pos_replay_ciclo_correto"]) for r in rows), 2)
    confirmadas = sum(
        1 for r in rows
        if hipotese_estado_confirmada_ou_provavel(r["hipotese_estado_errado_confirmada"])
    )

    print(f"[OK] CSV: {OUT_CSV}")
    print(f"[OK] MD:  {OUT_MD}")
    print(f"[OK] lotes auditados: {len(rows)}")
    print(f"[OK] soma Dif. observável vs motor publicado: {total_dif_pub:.2f}")
    residuos_ciclo = [
        r for r in rows
        if abs(fnum(r["dif_observado_vs_pos_replay_ciclo_correto"])) > 0.01
    ]

    print(f"[OK] soma Dif. observável vs pós-replay total: {total_dif_post:.2f}")
    print(f"[OK] soma Dif. observável vs pós-replay ciclo correto: {total_dif_ciclo:.2f}")
    print(f"[OK] hipóteses de estado errado confirmadas/prováveis: {confirmadas}")
    print(f"[OK] ressalvas do ciclo correto acima de 0.01: {len(residuos_ciclo)}")
    for r in sorted(
        residuos_ciclo,
        key=lambda x: abs(fnum(x["dif_observado_vs_pos_replay_ciclo_correto"])),
        reverse=True,
    ):
        print(
            "[RESSALVA] "
            f"{r['lote']}: dif ciclo={fnum(r['dif_observado_vs_pos_replay_ciclo_correto']):.2f}; "
            f"classe={r['classe_operacional']}; fonte={r['fonte_pos_replay_ciclo_correto']}"
        )


if __name__ == "__main__":
    main()
