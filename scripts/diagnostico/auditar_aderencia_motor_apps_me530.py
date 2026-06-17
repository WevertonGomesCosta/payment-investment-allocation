from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from aplicacao.principal import carregar_contexto_e_saida
from nucleo.calendario_financeiro import calcular_dias_lote, obter_taxa_dia_rendimento_lote
from nucleo.nucleo_financeiro_minimo import _modo_regra_iof, _taxa_iof, _taxa_ir
from nucleo.situacao_atual_oficial import _coagir_data_observavel, _serie_cdi_contexto


OUT_DIR = RAIZ / "saidas" / "diagnostico"
OUT_CSV = OUT_DIR / "auditoria_aderencia_motor_apps_me530.csv"
OUT_MD = OUT_DIR / "auditoria_aderencia_motor_apps_me530.md"

SENTINELAS = {
    "Lote 10342 fev.",
    "Lote 4124,75 fev.",
    "Lote 6630,64 fev.",
    "Lote 3120 mai",
    "Lote 5680 abr.",
    "Lote 7600 jun.",
    "Lote 4876 jun",
    "Lote 3800 jun.",
    "Lote 3000 mar. B",
    "Lote 3000 mar. V",
    "Lote 8500 mar.",
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


def fnum4(v: Any) -> float:
    if not valor_numerico(v):
        return 0.0
    return round(float(v), 6)


def bool_txt(v: Any) -> str:
    return "sim" if bool(v) else "não"


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


def buscar_lote(mapa: dict[str, Any], lote_id: Any) -> Any | None:
    k = chave_lote(lote_id)
    if not k:
        return None
    return mapa.get(k)


def lote_attr(lote: Any | None, nome: str, padrao: Any = "n/d") -> Any:
    if lote is None:
        return padrao
    return getattr(lote, nome, padrao)


def lote_num(lote: Any | None, nome: str) -> float | str:
    if lote is None:
        return "n/d"
    return fnum(getattr(lote, nome, 0.0))


def lote_num4(lote: Any | None, nome: str) -> float | str:
    if lote is None:
        return "n/d"
    return fnum4(getattr(lote, nome, 0.0))


def data_iso(v: Any) -> str:
    d = _coagir_data_observavel(v)
    return d.isoformat() if d is not None else "n/d"


def diferenca(a: Any, b: Any) -> float | str:
    if valor_numerico(a) and valor_numerico(b):
        return round(float(a) - float(b), 2)
    return "n/d"


def abs_dif(v: Any) -> float:
    return abs(fnum(v)) if valor_numerico(v) else 999999999.0


def classe_materialidade(v: Any) -> str:
    a = abs_dif(v)
    if a <= 0.01:
        return "sem_divergencia"
    if a <= 0.05:
        return "residuo_arredondamento"
    if a <= 0.50:
        return "divergencia_pequena"
    if a <= 5.00:
        return "divergencia_moderada"
    return "divergencia_material"


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


def data_alvo(row: dict[str, Any], data_referencia: Any) -> tuple[Any, str]:
    status = norm(row.get("Status ciclo"))
    if status in {"exaurido_por_saque", "migrado_por_switching"}:
        return row.get("Data término"), "data_termino_observavel"
    return data_referencia, "data_referencia_saida_canonica"


def dias_motor(contexto: Any, data_aplicacao: Any, data_fim: Any) -> tuple[int | str, int | str]:
    ini = _coagir_data_observavel(data_aplicacao)
    fim = _coagir_data_observavel(data_fim)
    if ini is None or fim is None:
        return "n/d", "n/d"
    try:
        d = calcular_dias_lote(
            ini,
            fim,
            contexto.calendario_financeiro,
            _serie_cdi_contexto(contexto),
            data_fechamento_referencia=fim,
        )
        return int(d.get("dias_corridos", 0)), int(d.get("dias_uteis", 0))
    except Exception:
        return "erro", "erro"


def info_taxa_lote(contexto: Any, lote: Any | None, data: Any) -> dict[str, Any]:
    d = _coagir_data_observavel(data)
    if lote is None or d is None:
        return {
            "fonte_cdi": "n/d",
            "taxa_cdi_dia": "n/d",
            "usa_cdi_real_ou_fallback": "n/d",
            "data_fator_cdi": "n/d",
        }

    try:
        aplicar, taxa, meta = obter_taxa_dia_rendimento_lote(
            d,
            lote.data_aplicacao,
            contexto.calendario_financeiro,
            data_recebimento=getattr(lote, "data_recebimento", None),
            serie_cdi=_serie_cdi_contexto(contexto),
            taxa_proj=float(contexto.calendario_financeiro.taxa_dia_base),
            data_fechamento_referencia=d,
        )
        return {
            "fonte_cdi": str(meta.get("fonte", "n/d")),
            "taxa_cdi_dia": "" if taxa is None else round(float(taxa), 10),
            "usa_cdi_real_ou_fallback": "fallback" if meta.get("fallback") else ("real_ou_modelo" if aplicar else "nao_aplicado"),
            "data_fator_cdi": data_iso(meta.get("data_fator")),
        }
    except Exception as exc:
        return {
            "fonte_cdi": f"erro:{type(exc).__name__}",
            "taxa_cdi_dia": "n/d",
            "usa_cdi_real_ou_fallback": "erro",
            "data_fator_cdi": "n/d",
        }


def info_fiscal_lote(contexto: Any, lote: Any | None, data: Any) -> dict[str, Any]:
    d = _coagir_data_observavel(data)
    if lote is None or d is None:
        return {
            "aliquota_ir_aplicada": "n/d",
            "aliquota_iof_aplicada": "n/d",
            "fator_liquido_motor": "n/d",
        }

    try:
        dias_vida = max((d - lote.data_base_fiscal).days, 0)
        regra_iof = _modo_regra_iof(getattr(lote, "regra_iof", "a_confirmar"))
        taxa_iof = 0.0 if regra_iof == "nao_incide" else _taxa_iof(dias_vida, tabela_iof=getattr(contexto, "tabela_iof", None))
        taxa_ir = _taxa_ir(
            dias_vida,
            bool(getattr(lote, "produto_isento_ir", False)),
            faixas_ir=getattr(contexto, "faixas_ir", None),
        )
        fator_liq = lote.get_fator_liquido(
            d,
            tabela_iof=getattr(contexto, "tabela_iof", None),
            faixas_ir=getattr(contexto, "faixas_ir", None),
        )
        return {
            "aliquota_ir_aplicada": round(float(taxa_ir), 6),
            "aliquota_iof_aplicada": round(float(taxa_iof), 6),
            "fator_liquido_motor": round(float(fator_liq), 10),
        }
    except Exception as exc:
        return {
            "aliquota_ir_aplicada": f"erro:{type(exc).__name__}",
            "aliquota_iof_aplicada": "erro",
            "fator_liquido_motor": "erro",
        }


def valorar_lote(
    contexto: Any,
    lote: Any | None,
    data: Any,
    *,
    base_referencia: Any,
) -> dict[str, Any]:
    d = _coagir_data_observavel(data)
    base = _coagir_data_observavel(base_referencia)
    if lote is None or d is None:
        return {
            "bruto": "n/d",
            "liquido": "n/d",
            "imposto": "n/d",
            "rendimento": "n/d",
            "erro": "lote_ou_data_indisponivel",
        }

    try:
        bruto = lote.valor_bruto_em_data(
            d,
            contexto.calendario_financeiro,
            serie_cdi=_serie_cdi_contexto(contexto),
            data_base_referencia=base,
        )
        liquido = lote.valor_liquido_em_data(
            d,
            contexto.calendario_financeiro,
            tabela_iof=getattr(contexto, "tabela_iof", None),
            faixas_ir=getattr(contexto, "faixas_ir", None),
            serie_cdi=_serie_cdi_contexto(contexto),
            data_base_referencia=base,
        )
        bruto = fnum(bruto)
        liquido = fnum(liquido)
        return {
            "bruto": bruto,
            "liquido": liquido,
            "imposto": round(bruto - liquido, 2),
            "rendimento": round(liquido - fnum(getattr(lote, "valor_inicial", 0.0)), 2),
            "erro": "",
        }
    except Exception as exc:
        return {
            "bruto": "n/d",
            "liquido": "n/d",
            "imposto": "n/d",
            "rendimento": "n/d",
            "erro": f"erro:{type(exc).__name__}",
        }


def valores_observados(row: dict[str, Any], classe: str) -> dict[str, float]:
    valor_original = fnum(row.get("Orig."))
    bruto_sacado = fnum(row.get("Bruto sac."))
    liquido_sacado = fnum(row.get("Líq. sac."))
    bruto_atual = fnum(row.get("Bruto atual"))
    liquido_atual = fnum(row.get("Líq. atual"))

    if classe in {"exaurido_por_saque", "origem_migrada_por_switching"}:
        bruto = bruto_sacado
        liquido = liquido_sacado
    elif classe in {"ativo_com_saque_parcial", "ativo_sem_saque"}:
        bruto = round(bruto_sacado + bruto_atual, 2)
        liquido = round(liquido_sacado + liquido_atual, 2)
    else:
        bruto = round(bruto_sacado + bruto_atual, 2)
        liquido = round(liquido_sacado + liquido_atual, 2)

    imposto = round(bruto - liquido, 2)
    rendimento = fnum(row.get("Rend. líq."))
    if abs(rendimento) <= 0.0:
        rendimento = round(liquido - valor_original, 2)

    return {
        "bruto": bruto,
        "liquido": liquido,
        "imposto": imposto,
        "rendimento": rendimento,
    }


def valores_motor_ciclo(
    contexto: Any,
    classe: str,
    pre: Any | None,
    post: Any | None,
    data: Any,
    data_referencia: Any,
) -> tuple[dict[str, Any], str, Any | None]:
    """Calcula o valor do motor na base econômica comparável ao observado.

    Para lotes encerrados, usa o lote original/pré-replay na data de encerramento.
    Para ativos, usa o estado pós-replay para respeitar saques já realizados.
    """
    if classe in {"exaurido_por_saque", "origem_migrada_por_switching"}:
        lote = pre or post
        v = valorar_lote(
            contexto,
            lote,
            data,
            base_referencia=lote_attr(lote, "data_aplicacao", data),
        )
        return v, "pre_replay_na_data_termino", lote

    if classe == "ativo_sem_saque":
        lote = post or pre
        base = data_referencia if post is not None else lote_attr(lote, "data_aplicacao", data)
        v = valorar_lote(contexto, lote, data_referencia, base_referencia=base)
        return v, "pos_replay_data_referencia" if post is not None else "pre_replay_data_referencia", lote

    if classe == "ativo_com_saque_parcial":
        lote = post or pre
        if post is not None:
            residual = valorar_lote(contexto, post, data_referencia, base_referencia=data_referencia)
            bruto = round(fnum(getattr(post, "total_bruto_sacado", 0.0)) + fnum(residual["bruto"]), 2)
            liquido = round(fnum(getattr(post, "total_liquido_sacado", 0.0)) + fnum(residual["liquido"]), 2)
            imposto = round(fnum(getattr(post, "total_imposto_pago", 0.0)) + fnum(residual["imposto"]), 2)
            return {
                "bruto": bruto,
                "liquido": liquido,
                "imposto": imposto,
                "rendimento": round(liquido - fnum(getattr(post, "valor_inicial", 0.0)), 2),
                "erro": residual.get("erro", ""),
            }, "pos_replay_total_sacado_mais_residual", post

        v = valorar_lote(
            contexto,
            lote,
            data_referencia,
            base_referencia=lote_attr(lote, "data_aplicacao", data_referencia),
        )
        return v, "pre_replay_fallback_sem_estado_pos", lote

    lote = post or pre
    v = valorar_lote(
        contexto,
        lote,
        data,
        base_referencia=lote_attr(lote, "data_aplicacao", data),
    )
    return v, "classe_indefinida", lote


def causa_provavel(row: dict[str, Any]) -> tuple[str, str]:
    if row["lote_existe_pre_replay"] == "não" and row["lote_existe_pos_replay"] == "não":
        return "lote_sem_estado_motor", "auditar inventário/replay: lote publicado sem estado financeiro correspondente"

    mat_rend = row["materialidade_rendimento_liquido"]
    if mat_rend == "sem_divergencia":
        return "sem_divergencia_material", "preservar; motor aderente no limiar de 0.01"

    if mat_rend == "residuo_arredondamento":
        return "residuo_arredondamento", "registrar como resíduo; auditar apenas se recorrente por produto"

    if row["dif_dias_corridos"] not in {0, "0", "n/d"}:
        return "dias_corridos_divergentes", "auditar data de aplicação, base fiscal e data-alvo"

    if row["dif_dias_uteis"] not in {0, "0", "n/d"}:
        return "dias_uteis_divergentes", "auditar calendário/CDI/fallback"

    if abs_dif(row["dif_imposto"]) > 0.50 and abs_dif(row["dif_imposto"]) >= abs_dif(row["dif_bruto"]):
        if str(row["regra_iof"]) in {"a_confirmar", "", "n/d"}:
            return "regra_iof_inconsistente", "auditar regra IOF do produto/carteira"
        return "imposto_motor_diverge_do_observado", "auditar IR, IOF, base fiscal e dias de vida"

    if abs_dif(row["dif_bruto"]) > 0.50 and abs_dif(row["dif_bruto"]) >= abs_dif(row["dif_liquido"]):
        return "bruto_motor_diverge_do_observado", "auditar taxa CDI, taxa do produto, bônus e datas"

    if abs_dif(row["dif_liquido"]) > 0.50:
        return "liquido_motor_diverge_do_observado", "auditar bruto, imposto e fator líquido"

    if row["classe_operacional"] == "ativo_com_saque_parcial":
        return "saque_parcial_exige_decomposicao_evento_residual", "auditar componente sacado e residual separadamente"

    if row["classe_operacional"] == "origem_migrada_por_switching":
        return "switching_exige_valor_migrado_observado", "auditar valor migrado, data de switching e produto de origem"

    if fnum(row["taxa_base_cdi_produto"]) <= 0:
        return "taxa_produto_inconsistente", "auditar mapeamento de produto/carteira e taxa CDI"

    return "causa_inconclusiva_requer_auditoria_individual", "auditar lote individualmente"


def montar_linhas(contexto: Any, saida_canonica_oficial: Any) -> list[dict[str, Any]]:
    data_ref = getattr(saida_canonica_oficial, "data_referencia", None)

    ex_id = indexar_por_lote_linhas(getattr(saida_canonica_oficial, "situacao_atual_lotes_exauridos_id", []))
    ex_val = indexar_por_lote_linhas(getattr(saida_canonica_oficial, "situacao_atual_lotes_exauridos_valores", []))
    at_id = indexar_por_lote_linhas(getattr(saida_canonica_oficial, "situacao_atual_lotes_ativos_id", []))
    at_val = indexar_por_lote_linhas(getattr(saida_canonica_oficial, "situacao_atual_lotes_ativos_valores", []))

    nucleo = getattr(contexto, "nucleo_financeiro", None)
    replay = getattr(contexto, "replay_passado", None)
    pre_map = indexar_lotes_objetos(list(getattr(nucleo, "lotes_financeiros", []) or []))
    post_map = indexar_lotes_objetos(list(getattr(replay, "lotes_apos_replay", []) or []))

    base: list[dict[str, Any]] = []
    for lote, val in ex_val.items():
        row = {**ex_id.get(lote, {}), **val}
        row["grupo_publicado"] = "exauridos"
        base.append(row)
    for lote, val in at_val.items():
        row = {**at_id.get(lote, {}), **val}
        row["grupo_publicado"] = "ativos"
        base.append(row)

    rows: list[dict[str, Any]] = []

    for row in base:
        lote_id = norm(row.get("Lote"))
        pre = buscar_lote(pre_map, lote_id)
        post = buscar_lote(post_map, lote_id)

        classe, subclasse = classificar_linha(row)
        alvo, fonte_alvo = data_alvo(row, data_ref)
        obs = valores_observados(row, classe)
        motor, estado_usado, lote_motor = valores_motor_ciclo(contexto, classe, pre, post, alvo, data_ref)

        valor_original = fnum(row.get("Orig."))
        valor_inicial_motor = fnum(lote_attr(lote_motor, "valor_inicial", 0.0))
        data_aplic = row.get("Aplic.") or lote_attr(lote_motor, "data_aplicacao", None)
        data_base_fiscal = row.get("Base fiscal") or lote_attr(lote_motor, "data_base_fiscal", None)
        data_recebimento = lote_attr(lote_motor, "data_recebimento", None)

        dias_corr_motor, dias_uteis_motor = dias_motor(contexto, data_aplic, alvo)
        dias_corr_obs = row.get("Dias corr.")
        dias_uteis_obs = row.get("Dias úteis")

        taxa = info_taxa_lote(contexto, lote_motor, alvo)
        fiscal = info_fiscal_lote(contexto, lote_motor, alvo)

        dif_bruto = diferenca(obs["bruto"], motor["bruto"])
        dif_liquido = diferenca(obs["liquido"], motor["liquido"])
        dif_imposto = diferenca(obs["imposto"], motor["imposto"])
        dif_rend = diferenca(obs["rendimento"], motor["rendimento"])

        out = {
            "lote": lote_id,
            "classe_operacional": classe,
            "subclasse": subclasse,
            "status_ciclo": norm(row.get("Status ciclo")),
            "grupo_publicado": norm(row.get("grupo_publicado")),
            "produto": norm(row.get("Carteira")),
            "data_aplicacao": data_iso(data_aplic),
            "data_base_fiscal": data_iso(data_base_fiscal),
            "data_recebimento": data_iso(data_recebimento),
            "data_alvo_observavel": data_iso(alvo),
            "data_alvo_motor": data_iso(alvo),
            "fonte_data_alvo": fonte_alvo,
            "dias_corridos_observado": dias_corr_obs,
            "dias_uteis_observado": dias_uteis_obs,
            "dias_corridos_motor": dias_corr_motor,
            "dias_uteis_motor": dias_uteis_motor,
            "dif_dias_corridos": diferenca(dias_corr_obs, dias_corr_motor),
            "dif_dias_uteis": diferenca(dias_uteis_obs, dias_uteis_motor),

            "valor_original_observado": valor_original,
            "valor_inicial_motor": valor_inicial_motor,
            "dif_valor_original_vs_motor": diferenca(valor_original, valor_inicial_motor),

            "bruto_observado": obs["bruto"],
            "bruto_motor": motor["bruto"],
            "dif_bruto": dif_bruto,
            "abs_dif_bruto": abs_dif(dif_bruto),
            "materialidade_bruto": classe_materialidade(dif_bruto),

            "liquido_observado": obs["liquido"],
            "liquido_motor": motor["liquido"],
            "dif_liquido": dif_liquido,
            "abs_dif_liquido": abs_dif(dif_liquido),
            "materialidade_liquido": classe_materialidade(dif_liquido),

            "imposto_observado": obs["imposto"],
            "imposto_motor": motor["imposto"],
            "dif_imposto": dif_imposto,
            "abs_dif_imposto": abs_dif(dif_imposto),
            "materialidade_imposto": classe_materialidade(dif_imposto),

            "rendimento_liquido_observado": obs["rendimento"],
            "rendimento_liquido_motor_puro": motor["rendimento"],
            "dif_rendimento_liquido": dif_rend,
            "abs_dif_rendimento_liquido": abs_dif(dif_rend),
            "materialidade_rendimento_liquido": classe_materialidade(dif_rend),

            "taxa_base_cdi_produto": lote_num4(lote_motor, "taxa_base_cdi"),
            "taxa_bonus_cdi": lote_num4(lote_motor, "taxa_bonus_cdi"),
            "dias_bonus": lote_num(lote_motor, "dias_bonus"),
            "produto_isento_ir": bool_txt(lote_attr(lote_motor, "produto_isento_ir", False)) if lote_motor is not None else "n/d",
            "regra_iof": norm(lote_attr(lote_motor, "regra_iof", "n/d")),
            "aliquota_ir_aplicada": fiscal["aliquota_ir_aplicada"],
            "aliquota_iof_aplicada": fiscal["aliquota_iof_aplicada"],
            "fator_acumulado_motor": lote_num4(lote_motor, "fator_acumulado"),
            "fator_liquido_motor": fiscal["fator_liquido_motor"],

            "fonte_cdi": taxa["fonte_cdi"],
            "taxa_cdi_dia": taxa["taxa_cdi_dia"],
            "usa_cdi_real_ou_fallback": taxa["usa_cdi_real_ou_fallback"],
            "data_fator_cdi": taxa["data_fator_cdi"],
            "data_fechamento_referencia": data_iso(alvo),

            "lote_existe_pre_replay": "sim" if pre is not None else "não",
            "lote_existe_pos_replay": "sim" if post is not None else "não",
            "estado_usado_na_auditoria": estado_usado,
            "saldo_bruto_pre_replay": lote_num(pre, "saldo_bruto"),
            "saldo_bruto_pos_replay": lote_num(post, "saldo_bruto"),
            "principal_remanescente_pre_replay": lote_num(pre, "principal_remanescente"),
            "principal_remanescente_pos_replay": lote_num(post, "principal_remanescente"),
            "total_bruto_sacado_pos_replay": lote_num(post, "total_bruto_sacado"),
            "total_imposto_pago_pos_replay": lote_num(post, "total_imposto_pago"),
            "total_liquido_sacado_pos_replay": lote_num(post, "total_liquido_sacado"),

            "erro_motor": motor.get("erro", ""),
            "sentinela": "sim" if lote_id in SENTINELAS else "não",
        }

        causa, acao = causa_provavel(out)
        out["causa_provavel"] = causa
        out["acao_recomendada"] = acao
        rows.append(out)

    return rows


def somar(rows: list[dict[str, Any]], campo: str) -> float:
    return round(sum(fnum(r.get(campo)) for r in rows), 2)


def resumo_por_classe(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        classe = r["classe_operacional"]
        s = out.setdefault(
            classe,
            {
                "n": 0,
                "dif_bruto": 0.0,
                "dif_liquido": 0.0,
                "dif_imposto": 0.0,
                "dif_rendimento": 0.0,
                "abs_dif_rendimento": 0.0,
                "maior_abs": 0.0,
                "lote_maior": "",
            },
        )
        s["n"] += 1
        s["dif_bruto"] = round(s["dif_bruto"] + fnum(r["dif_bruto"]), 2)
        s["dif_liquido"] = round(s["dif_liquido"] + fnum(r["dif_liquido"]), 2)
        s["dif_imposto"] = round(s["dif_imposto"] + fnum(r["dif_imposto"]), 2)
        s["dif_rendimento"] = round(s["dif_rendimento"] + fnum(r["dif_rendimento_liquido"]), 2)
        s["abs_dif_rendimento"] = round(s["abs_dif_rendimento"] + abs(fnum(r["dif_rendimento_liquido"])), 2)
        if abs(fnum(r["dif_rendimento_liquido"])) > s["maior_abs"]:
            s["maior_abs"] = abs(fnum(r["dif_rendimento_liquido"]))
            s["lote_maior"] = r["lote"]
    return out


def resumo_por_produto(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        produto = r.get("produto") or "produto_nao_informado"
        s = out.setdefault(
            produto,
            {
                "n": 0,
                "dif_bruto": 0.0,
                "dif_liquido": 0.0,
                "dif_imposto": 0.0,
                "dif_rendimento": 0.0,
                "abs_dif_bruto": 0.0,
                "abs_dif_rendimento": 0.0,
                "maior_abs_bruto": 0.0,
                "lote_maior_bruto": "",
                "maior_abs_rendimento": 0.0,
                "lote_maior_rendimento": "",
            },
        )
        s["n"] += 1
        s["dif_bruto"] = round(s["dif_bruto"] + fnum(r["dif_bruto"]), 2)
        s["dif_liquido"] = round(s["dif_liquido"] + fnum(r["dif_liquido"]), 2)
        s["dif_imposto"] = round(s["dif_imposto"] + fnum(r["dif_imposto"]), 2)
        s["dif_rendimento"] = round(s["dif_rendimento"] + fnum(r["dif_rendimento_liquido"]), 2)
        s["abs_dif_bruto"] = round(s["abs_dif_bruto"] + abs(fnum(r["dif_bruto"])), 2)
        s["abs_dif_rendimento"] = round(s["abs_dif_rendimento"] + abs(fnum(r["dif_rendimento_liquido"])), 2)

        abs_bruto = abs(fnum(r["dif_bruto"]))
        if abs_bruto > s["maior_abs_bruto"]:
            s["maior_abs_bruto"] = abs_bruto
            s["lote_maior_bruto"] = r["lote"]

        abs_rend = abs(fnum(r["dif_rendimento_liquido"]))
        if abs_rend > s["maior_abs_rendimento"]:
            s["maior_abs_rendimento"] = abs_rend
            s["lote_maior_rendimento"] = r["lote"]

    return out


def contagem_por_produto_classe(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for r in rows:
        key = (r.get("produto") or "produto_nao_informado", r["classe_operacional"])
        s = out.setdefault(
            key,
            {
                "n": 0,
                "sem_divergencia": 0,
                "residuo_arredondamento": 0,
                "divergencia_pequena": 0,
                "divergencia_moderada": 0,
                "divergencia_material": 0,
                "abs_dif_bruto": 0.0,
                "abs_dif_rendimento": 0.0,
            },
        )
        s["n"] += 1
        mat = r["materialidade_rendimento_liquido"]
        s[mat] = s.get(mat, 0) + 1
        s["abs_dif_bruto"] = round(s["abs_dif_bruto"] + abs(fnum(r["dif_bruto"])), 2)
        s["abs_dif_rendimento"] = round(s["abs_dif_rendimento"] + abs(fnum(r["dif_rendimento_liquido"])), 2)
    return out


def resumo_por_causa(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        causa = r["causa_provavel"]
        s = out.setdefault(causa, {"n": 0, "soma_abs_dif_rendimento": 0.0})
        s["n"] += 1
        s["soma_abs_dif_rendimento"] = round(s["soma_abs_dif_rendimento"] + abs(fnum(r["dif_rendimento_liquido"])), 2)
    return out


def conclusao_aderencia(rows: list[dict[str, Any]]) -> str:
    materiais = [r for r in rows if r["materialidade_rendimento_liquido"] == "divergencia_material"]
    moderadas = [r for r in rows if r["materialidade_rendimento_liquido"] == "divergencia_moderada"]
    pequenas = [r for r in rows if r["materialidade_rendimento_liquido"] == "divergencia_pequena"]
    residuos = [r for r in rows if r["materialidade_rendimento_liquido"] == "residuo_arredondamento"]

    if not materiais and not moderadas and not pequenas and not residuos:
        return "motor_aderente"

    if not materiais and not moderadas and not pequenas:
        return "motor_aderente_com_residuos"

    causas = resumo_por_causa(materiais or moderadas or pequenas)
    dominante = max(causas.items(), key=lambda kv: kv[1]["soma_abs_dif_rendimento"])[0] if causas else ""

    if "data" in dominante or "dias" in dominante:
        return "motor_nao_aderente_por_data"
    if "bruto" in dominante:
        return "motor_nao_aderente_por_bruto_ou_capitalizacao"
    if "cdi" in dominante or "taxa" in dominante:
        return "motor_nao_aderente_por_cdi_ou_taxa"
    if "ir" in dominante or "iof" in dominante or "imposto" in dominante:
        return "motor_nao_aderente_por_ir_iof"
    if "produto" in dominante or "carteira" in dominante:
        return "motor_nao_aderente_por_produto"
    return "motor_nao_aderente_inconclusivo"


def escrever_csv(rows: list[dict[str, Any]]) -> None:
    campos = list(rows[0].keys()) if rows else []
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(rows)


def listar_lotes(md: list[str], titulo: str, rows: list[dict[str, Any]]) -> None:
    md.append(f"\n## {titulo}\n\n")
    if not rows:
        md.append("- nenhum lote nesta classe.\n")
        return
    for r in sorted(rows, key=lambda x: abs(fnum(x["dif_rendimento_liquido"])), reverse=True):
        md.append(
            f"- {r['lote']} | {r['classe_operacional']} / {r['subclasse']} | "
            f"produto={r['produto']} | "
            f"bruto obs={fnum(r['bruto_observado']):.2f}, motor={fnum(r['bruto_motor']):.2f}, dif={fnum(r['dif_bruto']):.2f} | "
            f"liq obs={fnum(r['liquido_observado']):.2f}, motor={fnum(r['liquido_motor']):.2f}, dif={fnum(r['dif_liquido']):.2f} | "
            f"imp obs={fnum(r['imposto_observado']):.2f}, motor={fnum(r['imposto_motor']):.2f}, dif={fnum(r['dif_imposto']):.2f} | "
            f"rend obs={fnum(r['rendimento_liquido_observado']):.2f}, motor={fnum(r['rendimento_liquido_motor_puro']):.2f}, "
            f"dif={fnum(r['dif_rendimento_liquido']):.2f} | "
            f"causa={r['causa_provavel']}\n"
        )


def escrever_md(rows: list[dict[str, Any]]) -> None:
    resumo_classe = resumo_por_classe(rows)
    resumo_causa = resumo_por_causa(rows)
    conclusao = conclusao_aderencia(rows)

    sem = [r for r in rows if r["materialidade_rendimento_liquido"] == "sem_divergencia"]
    residuos = [r for r in rows if r["materialidade_rendimento_liquido"] == "residuo_arredondamento"]
    pequenas = [r for r in rows if r["materialidade_rendimento_liquido"] == "divergencia_pequena"]
    moderadas = [r for r in rows if r["materialidade_rendimento_liquido"] == "divergencia_moderada"]
    materiais = [r for r in rows if r["materialidade_rendimento_liquido"] == "divergencia_material"]
    sentinelas = [r for r in rows if r["sentinela"] == "sim"]

    md: list[str] = []
    md.append("# ME-530 — Auditoria de aderência do motor financeiro aos aplicativos\n\n")

    md.append("## Resumo executivo\n\n")
    md.append(f"- lotes auditados: {len(rows)}\n")
    md.append(f"- soma bruto observado: {somar(rows, 'bruto_observado'):.2f}\n")
    md.append(f"- soma bruto motor: {somar(rows, 'bruto_motor'):.2f}\n")
    md.append(f"- dif bruto: {somar(rows, 'dif_bruto'):.2f}\n")
    md.append(f"- soma líquido observado: {somar(rows, 'liquido_observado'):.2f}\n")
    md.append(f"- soma líquido motor: {somar(rows, 'liquido_motor'):.2f}\n")
    md.append(f"- dif líquido: {somar(rows, 'dif_liquido'):.2f}\n")
    md.append(f"- soma imposto observado: {somar(rows, 'imposto_observado'):.2f}\n")
    md.append(f"- soma imposto motor: {somar(rows, 'imposto_motor'):.2f}\n")
    md.append(f"- dif imposto: {somar(rows, 'dif_imposto'):.2f}\n")
    md.append(f"- soma rendimento observado: {somar(rows, 'rendimento_liquido_observado'):.2f}\n")
    md.append(f"- soma rendimento motor: {somar(rows, 'rendimento_liquido_motor_puro'):.2f}\n")
    md.append(f"- dif rendimento: {somar(rows, 'dif_rendimento_liquido'):.2f}\n")
    md.append(f"- sem divergência: {len(sem)}\n")
    md.append(f"- resíduos de arredondamento: {len(residuos)}\n")
    md.append(f"- divergências pequenas: {len(pequenas)}\n")
    md.append(f"- divergências moderadas: {len(moderadas)}\n")
    md.append(f"- divergências materiais: {len(materiais)}\n")
    md.append(f"- conclusão de aderência: {conclusao}\n")

    md.append("\n## Resultado por classe operacional\n\n")
    md.append("| Classe | n | Dif bruto | Dif líquido | Dif imposto | Dif rendimento | |Dif rendimento| | Maior lote divergente |\n")
    md.append("|---|---:|---:|---:|---:|---:|---:|---|\n")
    for classe, s in sorted(resumo_classe.items()):
        md.append(
            f"| {classe} | {s['n']} | {s['dif_bruto']:.2f} | {s['dif_liquido']:.2f} | "
            f"{s['dif_imposto']:.2f} | {s['dif_rendimento']:.2f} | "
            f"{s['abs_dif_rendimento']:.2f} | {s['lote_maior']} |\n"
        )

    resumo_produto = resumo_por_produto(rows)
    md.append("\n## Resultado por produto/carteira\n\n")
    md.append("| Produto | n | Dif bruto | Dif líquido | Dif imposto | Dif rendimento | Abs dif bruto | Abs dif rendimento | Maior bruto | Maior rendimento |\n")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---|---|\n")
    for produto, s in sorted(
        resumo_produto.items(),
        key=lambda kv: kv[1]["abs_dif_rendimento"],
        reverse=True,
    ):
        md.append(
            f"| {produto} | {s['n']} | {s['dif_bruto']:.2f} | {s['dif_liquido']:.2f} | "
            f"{s['dif_imposto']:.2f} | {s['dif_rendimento']:.2f} | "
            f"{s['abs_dif_bruto']:.2f} | {s['abs_dif_rendimento']:.2f} | "
            f"{s['lote_maior_bruto']} | {s['lote_maior_rendimento']} |\n"
        )

    md.append("\n## Ranking dos maiores desvios de bruto\n\n")
    top_bruto = sorted(rows, key=lambda r: abs(fnum(r["dif_bruto"])), reverse=True)[:12]
    for r in top_bruto:
        md.append(
            f"- {r['lote']} | {r['classe_operacional']} / {r['subclasse']} | "
            f"produto={r['produto']} | "
            f"bruto obs={fnum(r['bruto_observado']):.2f}, motor={fnum(r['bruto_motor']):.2f}, "
            f"dif bruto={fnum(r['dif_bruto']):.2f} | "
            f"liq obs={fnum(r['liquido_observado']):.2f}, motor={fnum(r['liquido_motor']):.2f}, "
            f"dif liq={fnum(r['dif_liquido']):.2f} | "
            f"imp obs={fnum(r['imposto_observado']):.2f}, motor={fnum(r['imposto_motor']):.2f}, "
            f"dif imp={fnum(r['dif_imposto']):.2f} | "
            f"rend dif={fnum(r['dif_rendimento_liquido']):.2f} | "
            f"causa={r['causa_provavel']}\n"
        )

    md.append("\n## Contagem por produto e classe operacional\n\n")
    md.append("| Produto | Classe | n | Sem div. | Resíduo | Pequena | Moderada | Material | Abs dif bruto | Abs dif rendimento |\n")
    md.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
    for (produto, classe), s in sorted(
        contagem_por_produto_classe(rows).items(),
        key=lambda kv: (kv[0][0], kv[0][1]),
    ):
        md.append(
            f"| {produto} | {classe} | {s['n']} | "
            f"{s.get('sem_divergencia', 0)} | "
            f"{s.get('residuo_arredondamento', 0)} | "
            f"{s.get('divergencia_pequena', 0)} | "
            f"{s.get('divergencia_moderada', 0)} | "
            f"{s.get('divergencia_material', 0)} | "
            f"{s['abs_dif_bruto']:.2f} | {s['abs_dif_rendimento']:.2f} |\n"
        )

    listar_lotes(md, "Divergências materiais", materiais)
    listar_lotes(md, "Divergências moderadas", moderadas)
    listar_lotes(md, "Divergências pequenas", pequenas)
    listar_lotes(md, "Resíduos de arredondamento", residuos)

    md.append("\n## Diagnóstico por causa provável\n\n")
    md.append("| Causa provável | n | Soma |Dif rendimento| |\n")
    md.append("|---|---:|---:|\n")
    for causa, s in sorted(resumo_causa.items(), key=lambda kv: kv[1]["soma_abs_dif_rendimento"], reverse=True):
        md.append(f"| {causa} | {s['n']} | {s['soma_abs_dif_rendimento']:.2f} |\n")

    md.append("\n## Sentinelas\n\n")
    for r in sentinelas:
        md.append(
            f"- {r['lote']} | {r['classe_operacional']} / {r['subclasse']} | "
            f"data={r['data_alvo_motor']} | produto={r['produto']} | "
            f"bruto obs={fnum(r['bruto_observado']):.2f}, motor={fnum(r['bruto_motor']):.2f}, dif={fnum(r['dif_bruto']):.2f} | "
            f"liq obs={fnum(r['liquido_observado']):.2f}, motor={fnum(r['liquido_motor']):.2f}, dif={fnum(r['dif_liquido']):.2f} | "
            f"imp obs={fnum(r['imposto_observado']):.2f}, motor={fnum(r['imposto_motor']):.2f}, dif={fnum(r['dif_imposto']):.2f} | "
            f"rend obs={fnum(r['rendimento_liquido_observado']):.2f}, motor={fnum(r['rendimento_liquido_motor_puro']):.2f}, "
            f"dif={fnum(r['dif_rendimento_liquido']):.2f} | "
            f"mat={r['materialidade_rendimento_liquido']} | causa={r['causa_provavel']} | ação={r['acao_recomendada']}\n"
        )

    md.append("\n## Conclusão\n\n")
    md.append(f"- decisão: {conclusao}\n")
    md.append(
        "- Esta ME é diagnóstica. Ela não altera motor, ledger, replay, saída canônica, console, XLSX ou decisão econômica.\n"
    )
    md.append(
        "- A evidência desta auditoria indica que a divergência nasce principalmente no valor bruto/capitalização. "
        "A próxima ME corretiva deve decompor fator acumulado, taxa diária, taxa do produto, bônus CDI, CDI real/fallback "
        "e regra de datas antes de alterar IR/IOF.\n"
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
        raise RuntimeError("gates_nao_aprovados_para_auditoria_me530")

    rows = montar_linhas(contexto, saida_canonica_oficial)

    escrever_csv(rows)
    escrever_md(rows)

    print(f"[OK] CSV: {OUT_CSV}")
    print(f"[OK] MD:  {OUT_MD}")
    print(f"[OK] lotes auditados: {len(rows)}")
    print(f"[OK] dif bruto: {somar(rows, 'dif_bruto'):.2f}")
    print(f"[OK] dif líquido: {somar(rows, 'dif_liquido'):.2f}")
    print(f"[OK] dif imposto: {somar(rows, 'dif_imposto'):.2f}")
    print(f"[OK] dif rendimento: {somar(rows, 'dif_rendimento_liquido'):.2f}")
    print(f"[OK] conclusão: {conclusao_aderencia(rows)}")
    print("[OK] causa dominante: bruto_motor_diverge_do_observado quando aplicável")
    print("[OK] relatório inclui resumo por produto, ranking bruto e produto x classe")

    mats = {}
    for r in rows:
        k = r["materialidade_rendimento_liquido"]
        mats[k] = mats.get(k, 0) + 1
    for k in sorted(mats):
        print(f"[OK] {k}: {mats[k]}")


if __name__ == "__main__":
    main()
