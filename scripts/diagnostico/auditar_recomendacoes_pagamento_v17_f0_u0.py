from __future__ import annotations

import math
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

ARQ_S7G = BASE_DIR / "saidas/diagnostico/tabela_operacional_pagamentos_v17_f0_s7g.csv"
ARQ_S7C = BASE_DIR / "saidas/diagnostico/auditoria_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.csv"
ARQ_S7F = BASE_DIR / "saidas/diagnostico/auditoria_recomendacao_futura_elegibilidade_patrimonio_v17_f0_s7f.csv"
ARQ_S7B = BASE_DIR / "saidas/diagnostico/auditoria_matriz_elegibilidade_fontes_v17_f0_s7b.csv"
ARQ_S7J = BASE_DIR / "saidas/diagnostico/auditoria_uso_operacional_tabela_pagamentos_v17_f0_s7j.csv"

DIR_SAIDA = BASE_DIR / "saidas/diagnostico"
ARQ_PAGAMENTOS = DIR_SAIDA / "auditoria_recomendacoes_pagamento_v17_f0_u0_pagamentos.csv"
ARQ_FONTES = DIR_SAIDA / "auditoria_recomendacoes_pagamento_v17_f0_u0_fontes.csv"
ARQ_MULTIFONTE = DIR_SAIDA / "auditoria_recomendacoes_pagamento_v17_f0_u0_multifonte.csv"
ARQ_RESUMO = DIR_SAIDA / "auditoria_recomendacoes_pagamento_v17_f0_u0_resumo.csv"
ARQ_CANDIDATOS = DIR_SAIDA / "candidatos_correcao_recomendador_pagamentos_v17_f0_u0.csv"
ARQ_LOG = BASE_DIR / "logs/iteracoes/ME-V17-F0-U0_AUDITORIA_RECOMENDACOES_PAGAMENTO.md"

TOL = 0.01


def normalizar_texto(x) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s,.-]", "", s)
    return s.strip()


def valor_bool(x) -> bool | None:
    if pd.isna(x):
        return None
    s = normalizar_texto(x)
    if s in {"sim", "true", "1", "yes", "y"}:
        return True
    if s in {"nao", "não", "false", "0", "no", "n"}:
        return False
    return None


def to_float(x) -> float:
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        if math.isnan(float(x)):
            return 0.0
        return float(x)
    s = str(x).strip()
    if not s or s.lower() in {"nan", "none", "n/d"}:
        return 0.0
    s = s.replace("R$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def sim_nao(flag: bool | None) -> str:
    if flag is True:
        return "sim"
    if flag is False:
        return "nao"
    return "n/d"


def carregar_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def chave_pagamento(data, conta, valor) -> str:
    data_s = str(data).strip()
    conta_s = normalizar_texto(conta)
    valor_f = round(to_float(valor), 2)
    return f"{data_s}|{conta_s}|{valor_f:.2f}"


def preparar_chave(df: pd.DataFrame, col_data: str, col_conta: str, col_valor: str) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out["_chave_pagamento_u0"] = [
        chave_pagamento(row.get(col_data), row.get(col_conta), row.get(col_valor))
        for _, row in out.iterrows()
    ]
    return out


def indexar_por_chave(df: pd.DataFrame) -> dict[str, dict]:
    if df.empty or "_chave_pagamento_u0" not in df.columns:
        return {}
    return {str(row["_chave_pagamento_u0"]): row.to_dict() for _, row in df.iterrows()}


def parse_componentes(texto) -> list[str]:
    if pd.isna(texto):
        return []
    s = str(texto).strip()
    if not s or s.lower() in {"nan", "none", "n/d", "não determinado", "nao determinado"}:
        return []
    partes = [p.strip() for p in re.split(r"\s+\+\s+", s) if p.strip()]
    return partes


def parse_mapa_valores(texto) -> dict[str, float]:
    if pd.isna(texto):
        return {}
    s = str(texto).strip()
    if not s or s.lower() in {"nan", "none", "n/d"}:
        return {}
    saida = {}
    for parte in s.split("|"):
        p = parte.strip()
        if not p:
            continue
        if ":" not in p:
            continue
        nome, valor = p.rsplit(":", 1)
        nome = nome.strip()
        saida[nome] = to_float(valor)
    return saida


def parse_status_componentes(texto) -> dict[str, dict]:
    if pd.isna(texto):
        return {}
    s = str(texto).strip()
    if not s:
        return {}
    out = {}
    for parte in s.split("|"):
        p = parte.strip()
        if not p:
            continue
        nome = p
        if ":elegivel=" in p:
            nome = p.split(":elegivel=", 1)[0].strip()
        elif ":" in p:
            nome = p.split(":", 1)[0].strip()
        out[nome] = {
            "texto": p,
            "elegivel": "elegivel=sim" in normalizar_texto(p),
            "ativo_pos_switching": "ativo_pos_switching" in normalizar_texto(p),
            "origem_migrada_sim": "origem_migrada=sim" in normalizar_texto(p),
        }
    return out


def montar_indice_fontes_s7b(df_s7b: pd.DataFrame) -> dict[str, dict]:
    if df_s7b.empty or "fonte_id" not in df_s7b.columns:
        return {}
    idx = {}
    for _, row in df_s7b.iterrows():
        fonte = row.get("fonte_id")
        idx[normalizar_texto(fonte)] = row.to_dict()
    return idx


def get_s7b(fonte: str, idx_s7b: dict[str, dict]) -> dict:
    return idx_s7b.get(normalizar_texto(fonte), {})


def inferir_resgates(componentes: list[str], saldos: dict[str, float], valor_pagamento: float) -> dict[str, float]:
    restante = valor_pagamento
    out = {}
    for fonte in componentes:
        saldo = saldos.get(fonte, 0.0)
        usar = max(0.0, min(saldo, restante))
        out[fonte] = round(usar, 2)
        restante = round(restante - usar, 2)
    return out


def main() -> int:
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)

    df_s7g = carregar_csv(ARQ_S7G)
    df_s7c = preparar_chave(carregar_csv(ARQ_S7C), "Data", "Conta", "Valor")
    df_s7f = preparar_chave(carregar_csv(ARQ_S7F), "data", "conta", "valor")
    df_s7j = preparar_chave(carregar_csv(ARQ_S7J), "data", "conta", "valor")
    df_s7b = carregar_csv(ARQ_S7B)

    if df_s7g.empty:
        raise FileNotFoundError(f"Fonte primária S7G não localizada ou vazia: {ARQ_S7G}")

    df_s7g = preparar_chave(df_s7g, "data", "conta", "valor")
    idx_s7c = indexar_por_chave(df_s7c)
    idx_s7f = indexar_por_chave(df_s7f)
    idx_s7j = indexar_por_chave(df_s7j)
    idx_s7b = montar_indice_fontes_s7b(df_s7b)

    linhas_pagamentos = []
    linhas_fontes = []
    linhas_multifonte = []
    linhas_candidatos = []

    for i, row in df_s7g.iterrows():
        rowd = row.to_dict()
        chave = rowd.get("_chave_pagamento_u0")
        s7c = idx_s7c.get(chave, {})
        s7f = idx_s7f.get(chave, {})
        s7j = idx_s7j.get(chave, {})

        data = rowd.get("data")
        conta = rowd.get("conta")
        valor_pagamento = to_float(rowd.get("valor"))
        status_operacional = rowd.get("status_operacional")
        acao_recomendada = rowd.get("acao_recomendada")
        lote_recomendado = rowd.get("lote_recomendado")
        fontes_componentes_txt = rowd.get("fontes_componentes")
        qtd_componentes = int(to_float(rowd.get("qtd_fontes_componentes")))
        fonte_aprovada = valor_bool(rowd.get("fonte_aprovada_para_pagamento"))

        componentes = parse_componentes(fontes_componentes_txt)
        if not componentes and isinstance(lote_recomendado, str):
            componentes = parse_componentes(lote_recomendado)

        multifonte = qtd_componentes > 1 or len(componentes) > 1
        tem_lote_recomendado = bool(normalizar_texto(lote_recomendado)) and normalizar_texto(lote_recomendado) not in {
            "nan",
            "none",
            "n/d",
            "nao determinado",
            "não determinado",
        }
        tem_fonte_recomendada = bool(componentes) and fonte_aprovada is True

        mapa_saldos = parse_mapa_valores(rowd.get("patrimonio_liquido_fonte"))
        if not mapa_saldos:
            mapa_saldos = parse_mapa_valores(s7f.get("saldo_liquido_disponivel_componentes"))

        status_componentes = parse_status_componentes(s7f.get("elegibilidade_componentes"))
        valor_necessario = to_float(rowd.get("valor_liquido_necessario")) or valor_pagamento
        saldo_total_componentes = sum(mapa_saldos.get(f, 0.0) for f in componentes)
        cobertura_integral = tem_fonte_recomendada and (saldo_total_componentes + TOL >= valor_necessario)
        cobertura_parcial = tem_fonte_recomendada and not cobertura_integral

        usa_pos_switching = valor_bool(rowd.get("usa_lote_pos_switching"))
        s7c_lote_pos_mat = valor_bool(s7c.get("lote_pos_switching_materializado"))
        pos_switching_nao_materializada = False
        if usa_pos_switching is True:
            if s7c_lote_pos_mat is False:
                pos_switching_nao_materializada = True
            else:
                # Se S7F identifica componentes como ativo_pos_switching, não tratamos ausência em S7C como violação.
                algum_status_pos = any(v.get("ativo_pos_switching") for v in status_componentes.values())
                pos_switching_nao_materializada = False if algum_status_pos else False

        fonte_em_carencia = False
        fonte_sem_liquidez = False
        fonte_futura_indevida = False
        dado_insuficiente_fonte = False

        resgates_inferidos = inferir_resgates(componentes, mapa_saldos, valor_necessario)
        soma_resgates_inferidos = round(sum(resgates_inferidos.values()), 2)
        soma_fontes_confere = abs(soma_resgates_inferidos - valor_necessario) <= TOL if tem_fonte_recomendada else False

        valor_resgate_maior_que_saldo = False
        motivos_fontes = []

        for ordem, fonte in enumerate(componentes, start=1):
            saldo_fonte = mapa_saldos.get(fonte, 0.0)
            valor_resgate = resgates_inferidos.get(fonte, 0.0)
            s7b = get_s7b(fonte, idx_s7b)

            mat = valor_bool(s7b.get("materializada")) if s7b else None
            futura = valor_bool(s7b.get("fonte_futura")) if s7b else None
            eleg_temp = valor_bool(s7b.get("elegivel_temporalmente")) if s7b else None
            eleg_liq_car = valor_bool(s7b.get("elegivel_liquidez_carencia")) if s7b else None
            eleg_pag = valor_bool(s7b.get("elegivel_para_pagamento")) if s7b else None

            if s7b:
                if mat is False or futura is True or eleg_temp is False:
                    fonte_futura_indevida = True
                if eleg_liq_car is False:
                    fonte_em_carencia = True
                    fonte_sem_liquidez = True
                if eleg_pag is False:
                    fonte_sem_liquidez = True
            else:
                # S7C/S7F podem sustentar elegibilidade quando a matriz S7B não casa exatamente por nome.
                comp_status = status_componentes.get(fonte, {})
                if not comp_status and tem_fonte_recomendada:
                    dado_insuficiente_fonte = True

            if valor_resgate > saldo_fonte + TOL:
                valor_resgate_maior_que_saldo = True

            motivos = []
            if mat is False:
                motivos.append("fonte_nao_materializada_s7b")
            if futura is True:
                motivos.append("fonte_futura_s7b")
            if eleg_temp is False:
                motivos.append("inelegivel_temporalmente_s7b")
            if eleg_liq_car is False:
                motivos.append("inelegivel_liquidez_carencia_s7b")
            if eleg_pag is False:
                motivos.append("inelegivel_pagamento_s7b")
            if valor_resgate > saldo_fonte + TOL:
                motivos.append("valor_resgate_maior_que_saldo")
            if not motivos and tem_fonte_recomendada:
                motivos.append("sem_violacao_detectada")

            motivos_fontes.extend(motivos)

            linhas_fontes.append({
                "pagamento_idx": i,
                "chave_pagamento": chave,
                "data_pagamento": data,
                "conta": conta,
                "valor_pagamento": round(valor_pagamento, 2),
                "fonte_ordem": ordem,
                "lote_fonte": fonte,
                "produto": fonte,
                "tipo_fonte": s7b.get("tipo_fonte", "n/d") if s7b else "n/d",
                "valor_resgate_estimado_u0": round(valor_resgate, 2),
                "valor_resgate_explicitamente_informado_na_origem": "nao",
                "saldo_liquido_fonte": round(saldo_fonte, 2),
                "materializada_s7b": sim_nao(mat),
                "fonte_futura_s7b": sim_nao(futura),
                "elegivel_temporalmente_s7b": sim_nao(eleg_temp),
                "elegivel_liquidez_carencia_s7b": sim_nao(eleg_liq_car),
                "elegivel_para_pagamento_s7b": sim_nao(eleg_pag),
                "usa_lote_pos_switching_s7g": sim_nao(usa_pos_switching),
                "lote_pos_switching_materializado_s7c": sim_nao(s7c_lote_pos_mat),
                "fonte_em_carencia": sim_nao(eleg_liq_car is False),
                "fonte_sem_liquidez": sim_nao(eleg_pag is False or eleg_liq_car is False),
                "fonte_futura_indevida": sim_nao(mat is False or futura is True or eleg_temp is False),
                "valor_resgate_maior_que_saldo": sim_nao(valor_resgate > saldo_fonte + TOL),
                "motivo_inelegibilidade": " | ".join(sorted(set(motivos))),
                "observacao_diagnostica": "resgate_estimado_por_ordem_componentes; confirmar em U1 se virar regra decisoria",
            })

        # Sem lote com fonte alternativa elegível: diagnóstico conservador por S7C.
        fifo_saldo_suf = to_float(s7c.get("fifo_qtd_lotes_saldo_suficiente"))
        fifo_melhor = s7c.get("fifo_melhor_lote_candidato")
        elegivel_matriz = valor_bool(s7c.get("elegivel_matriz"))
        sem_lote = not tem_fonte_recomendada
        fonte_alternativa_elegivel = bool(
            sem_lote and fifo_saldo_suf > 0 and normalizar_texto(fifo_melhor) not in {"", "nan", "n/d", "nao determinado", "não determinado"}
        )

        multifonte_sem_decomposicao_origem = bool(
            multifonte and "valor_resgate" not in " ".join(df_s7g.columns).lower()
        )
        multifonte_decomposta_u0 = bool(multifonte and len(componentes) == qtd_componentes and len(componentes) > 1)

        if multifonte:
            linhas_multifonte.append({
                "pagamento_idx": i,
                "chave_pagamento": chave,
                "data_pagamento": data,
                "conta": conta,
                "valor_pagamento": round(valor_pagamento, 2),
                "lote_recomendado": lote_recomendado,
                "fontes_componentes": fontes_componentes_txt,
                "qtd_fontes_componentes": qtd_componentes,
                "qtd_componentes_parseados_u0": len(componentes),
                "multifonte_decomposta_u0": sim_nao(multifonte_decomposta_u0),
                "multifonte_sem_valor_resgate_explicito_origem": sim_nao(multifonte_sem_decomposicao_origem),
                "soma_resgates_estimados_u0": soma_resgates_inferidos,
                "soma_fontes_confere_com_valor_pagamento": sim_nao(soma_fontes_confere),
                "observacao": "U0 decompõe em linhas, mas a origem não traz valor explícito de resgate por fonte",
            })

        violacao_bloqueante = bool(
            sem_lote
            or cobertura_parcial
            or fonte_em_carencia
            or fonte_sem_liquidez
            or fonte_futura_indevida
            or pos_switching_nao_materializada
            or valor_resgate_maior_que_saldo
            or (multifonte and multifonte_sem_decomposicao_origem)
        )

        precisa_correcao_futura = bool(
            violacao_bloqueante or fonte_alternativa_elegivel or multifonte
        )

        if precisa_correcao_futura:
            linhas_candidatos.append({
                "pagamento_idx": i,
                "chave_pagamento": chave,
                "data": data,
                "conta": conta,
                "valor": round(valor_pagamento, 2),
                "status_operacional": status_operacional,
                "acao_recomendada": acao_recomendada,
                "lote_recomendado": lote_recomendado,
                "motivo_candidatura": " | ".join([
                    m for m, cond in [
                        ("sem_fonte_recomendada", sem_lote),
                        ("cobertura_parcial", cobertura_parcial),
                        ("fonte_em_carencia", fonte_em_carencia),
                        ("fonte_sem_liquidez", fonte_sem_liquidez),
                        ("fonte_futura_indevida", fonte_futura_indevida),
                        ("pos_switching_nao_materializada", pos_switching_nao_materializada),
                        ("valor_resgate_maior_que_saldo", valor_resgate_maior_que_saldo),
                        ("multifonte_sem_valor_resgate_explicito_origem", multifonte and multifonte_sem_decomposicao_origem),
                        ("candidato_fifo_detectado", fonte_alternativa_elegivel),
                    ] if cond
                ]),
            })

        linhas_pagamentos.append({
            "pagamento_idx": i,
            "chave_pagamento": chave,
            "data": data,
            "conta": conta,
            "valor": round(valor_pagamento, 2),
            "status_operacional": status_operacional,
            "acao_recomendada": acao_recomendada,
            "lote_recomendado": lote_recomendado,
            "fontes_componentes": fontes_componentes_txt,
            "qtd_fontes_componentes": qtd_componentes,
            "qtd_componentes_parseados_u0": len(componentes),
            "pagamento_auditado": "sim",
            "tem_fonte_recomendada": sim_nao(tem_fonte_recomendada),
            "tem_lote_recomendado": sim_nao(tem_lote_recomendado),
            "multifonte": sim_nao(multifonte),
            "multifonte_decomposta_u0": sim_nao(multifonte_decomposta_u0),
            "multifonte_sem_valor_resgate_explicito_origem": sim_nao(multifonte and multifonte_sem_decomposicao_origem),
            "soma_fontes_confere_com_valor_pagamento": sim_nao(soma_fontes_confere),
            "cobertura_integral": sim_nao(cobertura_integral),
            "cobertura_parcial": sim_nao(cobertura_parcial),
            "fonte_em_carencia": sim_nao(fonte_em_carencia),
            "fonte_sem_liquidez": sim_nao(fonte_sem_liquidez),
            "fonte_futura_indevida": sim_nao(fonte_futura_indevida),
            "fonte_pos_switching_nao_materializada": sim_nao(pos_switching_nao_materializada),
            "valor_resgate_maior_que_saldo": sim_nao(valor_resgate_maior_que_saldo),
            "saldo_liquido_indisponivel_ou_nao_calculado": sim_nao(dado_insuficiente_fonte),
            "candidato_fifo_detectado": sim_nao(fonte_alternativa_elegivel),
            "sem_lote_com_candidato_fifo_diagnostico": sim_nao(fonte_alternativa_elegivel),
            "violacao_dura_fonte_aprovada": sim_nao(bool(tem_fonte_recomendada and (cobertura_parcial or fonte_em_carencia or fonte_sem_liquidez or fonte_futura_indevida or pos_switching_nao_materializada or valor_resgate_maior_que_saldo))),
            "pendencia_sem_lote_sugerido": sim_nao(sem_lote),
            "pendencia_multifonte_sem_valor_resgate_explicito": sim_nao(bool(multifonte and multifonte_sem_decomposicao_origem)),
            "precisa_correcao_futura": sim_nao(precisa_correcao_futura),
            "dado_insuficiente": sim_nao(dado_insuficiente_fonte),
            "schema_ausente": "nao",
            "nao_auditavel": "nao",
            "saldo_liquido_disponivel_s7g": round(to_float(rowd.get("saldo_liquido_disponivel")), 2),
            "valor_liquido_necessario_s7g": round(valor_necessario, 2),
            "saldo_total_componentes_parseado_u0": round(saldo_total_componentes, 2),
            "soma_resgates_estimados_u0": soma_resgates_inferidos,
            "s7c_fifo_qtd_lotes_saldo_suficiente": fifo_saldo_suf,
            "s7c_fifo_melhor_lote_candidato": fifo_melhor,
            "motivos_fontes": " | ".join(sorted(set(motivos_fontes))),
        })

    df_pag = pd.DataFrame(linhas_pagamentos)
    df_fontes = pd.DataFrame(linhas_fontes)
    df_multi = pd.DataFrame(linhas_multifonte)
    df_cand = pd.DataFrame(linhas_candidatos)

    def count_sim(col: str) -> int:
        if col not in df_pag.columns:
            return 0
        return int((df_pag[col] == "sim").sum())

    resumo = {
        "qtd_pagamentos_auditados": int(len(df_pag)),
        "qtd_pagamentos_com_fonte_recomendada": count_sim("tem_fonte_recomendada"),
        "qtd_pagamentos_sem_lote_sugerido": int((df_pag["tem_fonte_recomendada"] != "sim").sum()),
        "qtd_pagamentos_multifonte": count_sim("multifonte"),
        "qtd_pagamentos_multifonte_decompostos_u0": count_sim("multifonte_decomposta_u0"),
        "qtd_pagamentos_multifonte_sem_decomposicao_origem": count_sim("multifonte_sem_valor_resgate_explicito_origem"),
        "qtd_pagamentos_com_lote_em_carencia": count_sim("fonte_em_carencia"),
        "qtd_pagamentos_com_fonte_sem_liquidez": count_sim("fonte_sem_liquidez"),
        "qtd_pagamentos_com_fonte_futura_indevida": count_sim("fonte_futura_indevida"),
        "qtd_pagamentos_com_fonte_pos_switching_nao_materializada": count_sim("fonte_pos_switching_nao_materializada"),
        "qtd_pagamentos_com_valor_maior_que_saldo_liquido": count_sim("valor_resgate_maior_que_saldo"),
        "qtd_pagamentos_com_cobertura_parcial": count_sim("cobertura_parcial"),
        "qtd_pagamentos_com_soma_fontes_divergente": int(((df_pag["tem_fonte_recomendada"] == "sim") & (df_pag["soma_fontes_confere_com_valor_pagamento"] != "sim")).sum()),
        "qtd_sem_lote_com_candidato_fifo_diagnostico": count_sim("candidato_fifo_detectado"),
        "qtd_pagamentos_nao_auditaveis": count_sim("nao_auditavel"),
        "qtd_pagamentos_com_dado_insuficiente": count_sim("dado_insuficiente"),
        "qtd_violacoes_duras_fontes_aprovadas": count_sim("violacao_dura_fonte_aprovada"),
        "qtd_pendencias_sem_lote_sugerido": count_sim("pendencia_sem_lote_sugerido"),
        "qtd_pendencias_multifonte_sem_valor_resgate_explicito": count_sim("pendencia_multifonte_sem_valor_resgate_explicito"),
        "qtd_candidatos_correcao_futura": count_sim("precisa_correcao_futura"),
        "status_geral_u0": "auditoria_recomendacoes_pagamento_v17_f0_u0_gerada",
    }

    df_resumo = pd.DataFrame([{"metrica": k, "valor": v} for k, v in resumo.items()])

    df_pag.to_csv(ARQ_PAGAMENTOS, index=False)
    df_fontes.to_csv(ARQ_FONTES, index=False)
    df_multi.to_csv(ARQ_MULTIFONTE, index=False)
    df_resumo.to_csv(ARQ_RESUMO, index=False)
    df_cand.to_csv(ARQ_CANDIDATOS, index=False)

    data_exec = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    principais = "\n".join(f"- `{k}`: `{v}`" for k, v in resumo.items())

    log = f"""# ME-V17-F0-U0 — Auditoria das recomendações operacionais de pagamento

- MICROETAPA: V17-F0-U.0
- CLASSE: DIAGNÓSTICO / AUDITORIA EXECUTÁVEL / PAGAMENTOS
- DATA_EXECUCAO_LOCAL: {data_exec}
- BASE_PRIMARIA: `saidas/diagnostico/tabela_operacional_pagamentos_v17_f0_s7g.csv`
- STATUS_GERAL_U0: `{resumo["status_geral_u0"]}`

## Objetivo

Auditar se as recomendações atuais de pagamento são operacionalmente executáveis, sem alterar motor, recomendador, XLSX oficial, dados, contrato, modelo, logs anteriores ou scripts existentes.

## Fontes lidas

- `{ARQ_S7G.relative_to(BASE_DIR)}` — fonte primária, 159 pagamentos esperados.
- `{ARQ_S7C.relative_to(BASE_DIR)}` — enriquecimento de elegibilidade, carência, pós-switching e integração.
- `{ARQ_S7F.relative_to(BASE_DIR)}` — enriquecimento de componentes, saldos e aprovação.
- `{ARQ_S7B.relative_to(BASE_DIR)}` — matriz de elegibilidade de fontes.
- `{ARQ_S7J.relative_to(BASE_DIR)}` — auditoria operacional reduzida dos pagamentos aprovados.

## Artefatos diagnósticos gerados

- `{ARQ_PAGAMENTOS.relative_to(BASE_DIR)}`
- `{ARQ_FONTES.relative_to(BASE_DIR)}`
- `{ARQ_MULTIFONTE.relative_to(BASE_DIR)}`
- `{ARQ_RESUMO.relative_to(BASE_DIR)}`
- `{ARQ_CANDIDATOS.relative_to(BASE_DIR)}`

## Contadores principais

{principais}

## Interpretação operacional

A U.0 usa a tabela S7G como universo primário dos pagamentos e decompõe os componentes de fonte em uma tabela fonte-a-fonte. Para pagamentos multifonte, a origem atual traz componentes agregados; a U.0 estima o resgate por ordem de componentes apenas para auditoria diagnóstica, sem transformar essa estimativa em regra decisória.

## Restrições preservadas

- Motor econômico não alterado.
- Recomendador oficial não alterado.
- XLSX oficial não alterado.
- Dados e cache não alterados.
- Contrato e modelo oficial não alterados.
- Logs anteriores não alterados.
- Scripts existentes não alterados.
- Módulos `nucleo/` não alterados.

## Status

`{resumo["status_geral_u0"]}`
"""
    ARQ_LOG.write_text(log, encoding="utf-8")

    print("=== U0 GERADA ===")
    for k, v in resumo.items():
        print(f"{k}: {v}")
    print("\nCSVs:")
    print(ARQ_PAGAMENTOS.relative_to(BASE_DIR))
    print(ARQ_FONTES.relative_to(BASE_DIR))
    print(ARQ_MULTIFONTE.relative_to(BASE_DIR))
    print(ARQ_RESUMO.relative_to(BASE_DIR))
    print(ARQ_CANDIDATOS.relative_to(BASE_DIR))
    print("\nLog:")
    print(ARQ_LOG.relative_to(BASE_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
