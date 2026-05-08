from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.carregador_config import carregar_config
from nucleo.leitor_planilha import carregar_planilha

OUT_DIR = RAIZ / "saidas" / "diagnostico" / "v17_a0_1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARQ_ABAS = OUT_DIR / "v17_a0_1_abas_planilha_config.csv"
ARQ_CAMPOS = OUT_DIR / "v17_a0_1_campos_por_familia.csv"
ARQ_FONTES_ANTIGAS = OUT_DIR / "v17_a0_1_fontes_antigas_detectadas.csv"
ARQ_FONTES_V17 = OUT_DIR / "v17_a0_1_fontes_v17_aderencia.csv"
ARQ_SALDO_GASTOS = OUT_DIR / "v17_a0_1_ocorrencias_saldo_em_gastos.csv"
ARQ_LOTES_CAIXA = OUT_DIR / "v17_a0_1_lotes_caixa_disponivel_candidatos.csv"
ARQ_SWITCHING = OUT_DIR / "v17_a0_1_switchings_entrada_candidatos.csv"
ARQ_SAIDA = OUT_DIR / "v17_a0_1_pontos_saida_altera_limpa_completa.csv"
ARQ_RESUMO = OUT_DIR / "v17_a0_1_resumo.csv"

ABAS_V17 = {
    "Carteira": "produto_carteira",
    "Salários": "entrada_externa_salario",
    "Todos os Gastos": "pagamentos",
    "Inventário de Lotes": "lotes",
    "Switching": "switching",
}

ABAS_ALIASES = {
    "Carteira": ["Carteira"],
    "Salários": ["Salários", "Salarios"],
    "Todos os Gastos": ["Todos os Gastos"],
    "Inventário de Lotes": ["Inventário de Lotes", "Inventario de Lotes"],
    "Switching": ["Switching", "Switiching", "Swtiching"],
}

CAMPOS_V17 = {
    "produto_carteira": {
        "aba": "Carteira",
        "origem_config": "carteira",
        "campos": {
            "nome": ["Nome", "Produto", "Investimento"],
            "taxa_base": ["Taxa_Base_CDI", "taxa_base", "percentual_cdi"],
            "prazo_dias": ["Prazo_Dias", "prazo_dias"],
            "carencia_dias": ["Carência_Dias", "Carencia_Dias", "carencia_dias"],
            "liquidez_dias": ["Liquidez_Dias", "liquidez_dias"],
            "aplicacao_minima": ["Aplicação_Mínima", "Aplicacao_Minima", "aplicacao_minima"],
            "ativo": ["Ativo", "ativo"],
        },
    },
    "entrada_externa_salario": {
        "aba": "Salários",
        "origem_config": "salarios",
        "campos": {
            "data_recebimento": ["Data Recebimento", "Data", "data_recebimento"],
            "valor_bruto": ["Valor Bruto", "Valor", "valor_bruto"],
            "valor_liquido": ["Valor Líquido", "Valor Liquido", "valor_liquido"],
            "descricao": ["Descrição", "Descricao", "descricao"],
            "status": ["Status", "status"],
        },
    },
    "pagamento_por_saldo": {
        "aba": "Todos os Gastos",
        "origem_config": "despesas",
        "campos": {
            "despesa_id": ["ID", "despesa_id"],
            "data": ["Data", "data"],
            "descricao": ["Descrição", "Descricao", "descricao"],
            "valor": ["Valor", "valor"],
            "pago": ["Pago", "pago"],
            "lote_usado": ["Lote usado", "lote usado", "lote_usado_1"],
        },
    },
    "pagamento_por_lote": {
        "aba": "Todos os Gastos",
        "origem_config": "despesas",
        "campos": {
            "despesa_id": ["ID", "despesa_id"],
            "data": ["Data", "data"],
            "valor": ["Valor", "valor"],
            "lote_usado_1": ["Lote usado", "Lote usado 1", "lote_usado_1"],
            "lote_usado_2": ["Lote usado 2", "lote_usado_2"],
        },
    },
    "lote_investido": {
        "aba": "Inventário de Lotes",
        "origem_config": "lotes",
        "campos": {
            "lote_id": ["Lote (ID)", "lote_id", "ID"],
            "data_recebimento": ["Data Recebimento", "data_recebimento"],
            "data_aplicacao": ["Data Aplicação", "Data Aplicacao", "data_aplicacao"],
            "valor_original": ["Valor Original", "valor_original"],
            "investimento": ["Investimento", "Produto", "produto_id"],
        },
    },
    "lote_caixa_disponivel": {
        "aba": "Inventário de Lotes",
        "origem_config": "lotes",
        "campos": {
            "lote_id": ["Lote (ID)", "lote_id", "ID"],
            "data_recebimento": ["Data Recebimento", "data_recebimento"],
            "valor_original": ["Valor Original", "valor_original"],
            "data_aplicacao_vazia": ["Data Aplicação", "Data Aplicacao", "data_aplicacao"],
            "investimento_vazio": ["Investimento", "Produto", "produto_id"],
        },
    },
    "switching_origem": {
        "aba": "Switching",
        "origem_config": "switching",
        "campos": {
            "lote_id_antes": ["Lote (ID) Antes", "Lote Antes", "lote_id_antes"],
            "produto_origem": ["Produto Antes", "Investimento Antes", "produto_origem"],
            "valor_liquido_migrado": ["Valor Líquido Migrado", "Valor Liquido Migrado", "valor_liquido_migrado"],
        },
    },
    "switching_destino_materializado": {
        "aba": "Switching",
        "origem_config": "switching",
        "campos": {
            "lote_id_depois": ["Lote (ID) Depois", "Lote Depois", "lote_id_depois"],
            "data_recebimento": ["Data Recebimento", "data_recebimento"],
            "data_aplicacao": ["Data Aplicação", "Data Aplicacao", "data_aplicacao"],
            "valor_liquido_migrado": ["Valor Líquido Migrado", "Valor Liquido Migrado", "valor_liquido_migrado"],
            "investimento": ["Investimento", "Produto Destino", "produto_destino"],
        },
    },
}

FONTES_ANTIGAS = [
    "saldo_disponivel",
    "saldo_disponivel_geral",
    "caixa_pre_aplicacao",
    "lote_resgatavel",
    "recebido_disponivel",
    "estado_pos_switching_janela",
    "pos_switch::",
    "sem_saldo_temporal_auditavel",
]

FONTES_V17 = [
    "produto_carteira",
    "entrada_externa_salario",
    "lote_investido",
    "lote_caixa_disponivel",
    "pagamento_por_saldo",
    "pagamento_por_lote",
    "switching_origem",
    "switching_destino_materializado",
]

ARQUIVOS_CODIGO_ALVO = [
    RAIZ / "nucleo" / "caixa_recebidos_auditaveis.py",
    RAIZ / "nucleo" / "dados_operacionais_canonicos.py",
    RAIZ / "nucleo" / "ledger_temporal_conjunto.py",
    RAIZ / "nucleo" / "motor_recomendacao_pagamentos_switching_v1.py",
    RAIZ / "nucleo" / "recomputacao_sequencial_central_v1.py",
    RAIZ / "nucleo" / "saida_canonica.py",
    RAIZ / "nucleo" / "contexto_baseline.py",
]

PONTOS_SAIDA = [
    ("_normalizar_sem_fonte_valida_extrato_futuro", "limpa/normaliza linha futura sem saldo temporal"),
    ("_mapa_fontes_elegiveis_auditaveis_por_pagamento", "completa fonte auditavel a partir de fontes elegiveis"),
    ("_pagamentos_decisao_recebido_disponivel_fallback_auditavel", "restringe fallback auditavel de recebido_disponivel"),
    ("_primeiro_valor_auditavel", "seleciona valor alternativo em camada de saida"),
    ("_primeiro_valor_preenchido_preserva_zero", "seleciona valor alternativo preservando zero"),
    ("lotes_sinteticos_pos_switching_console", "materializa representacao sintetica de lote pos-switching para console"),
    ("recebidos_futuros_console", "infere uso/estado observavel de recebidos no console"),
    ("Lote sugerido", "campo possivelmente alterado/limpo/completado na saida"),
    ("Saldo Antes", "campo financeiro possivelmente limpo/completado na saida"),
    ("Bruto", "campo financeiro possivelmente limpo/completado na saida"),
    ("Líquido", "campo financeiro possivelmente limpo/completado na saida"),
    ("Saldo Remanescente", "campo financeiro possivelmente limpo/completado na saida"),
]


def _norm(v: Any) -> str:
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass
    texto = str(v).strip().lower()
    troca = str.maketrans("áàãâéêíóôõúüç", "aaaaeeiooouuc")
    texto = texto.translate(troca)
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return " ".join(texto.split())


def _is_blank(v: Any) -> bool:
    if v is None:
        return True
    try:
        if pd.isna(v):
            return True
    except Exception:
        pass
    return str(v).strip() == ""


def _to_float(v: Any) -> float:
    if _is_blank(v):
        return 0.0
    if isinstance(v, (int, float)):
        try:
            return float(v)
        except Exception:
            return 0.0
    texto = str(v).strip().replace("R$", "").replace(" ", "")
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except Exception:
        return 0.0


def _fmt_data(v: Any) -> str:
    if _is_blank(v):
        return ""
    if hasattr(v, "date") and not isinstance(v, str):
        try:
            return v.date().isoformat()
        except Exception:
            pass
    if hasattr(v, "isoformat") and not isinstance(v, str):
        try:
            return v.isoformat()
        except Exception:
            pass
    return str(v)


def _encontrar_aba(nomes_abas: list[str], nome_normativo: str) -> str:
    mapa = {_norm(nome): nome for nome in nomes_abas}
    for alias in ABAS_ALIASES.get(nome_normativo, [nome_normativo]):
        encontrado = mapa.get(_norm(alias))
        if encontrado:
            return encontrado
    return ""


def _colunas_df(df: pd.DataFrame | None) -> list[str]:
    if df is None:
        return []
    return [str(c) for c in df.columns]


def _encontrar_coluna(colunas: list[str], aliases: list[str]) -> str:
    mapa = {_norm(c): c for c in colunas}
    for alias in aliases:
        achou = mapa.get(_norm(alias))
        if achou:
            return achou
    return ""


def _aliases_config(config: dict[str, Any], bloco: str, campo: str) -> list[str]:
    colunas_cfg = config.get("colunas", {}) if isinstance(config.get("colunas"), dict) else {}
    bloco_cfg = colunas_cfg.get(bloco, {}) if isinstance(colunas_cfg.get(bloco), dict) else {}
    aliases = bloco_cfg.get(campo)
    if isinstance(aliases, list):
        return [str(a) for a in aliases]
    return []


def _gravar_csv(df: pd.DataFrame, caminho: Path, colunas: list[str]) -> None:
    if df is None or df.empty:
        df = pd.DataFrame(columns=colunas)
    else:
        for c in colunas:
            if c not in df.columns:
                df[c] = ""
        df = df[colunas]
    df.to_csv(caminho, index=False)


def _linhas_abas(pacote_planilha: Any, config: dict[str, Any]) -> list[dict[str, Any]]:
    abas_cfg = config.get("abas", {}) if isinstance(config.get("abas"), dict) else {}
    nomes_abas = list(getattr(pacote_planilha, "nomes_abas", []) or [])
    linhas: list[dict[str, Any]] = []
    for aba_normativa, familia in ABAS_V17.items():
        aba_encontrada = _encontrar_aba(nomes_abas, aba_normativa)
        reconhecida_config = aba_encontrada in set(str(v) for v in abas_cfg.values())
        chave_config = next((str(k) for k, v in abas_cfg.items() if str(v) == aba_encontrada), "")
        linhas.append({
            "familia_v17": familia,
            "aba_normativa": aba_normativa,
            "aba_encontrada_planilha": aba_encontrada,
            "existe_na_planilha": bool(aba_encontrada),
            "reconhecida_no_config_abas": bool(reconhecida_config),
            "chave_config": chave_config,
            "status_aderencia": "ok" if aba_encontrada and reconhecida_config else ("lida_fisicamente_mas_nao_canonizada" if aba_encontrada else "ausente"),
        })
    for nome in nomes_abas:
        if nome not in [l["aba_encontrada_planilha"] for l in linhas if l["aba_encontrada_planilha"]]:
            linhas.append({
                "familia_v17": "fora_escopo_v17_ou_auxiliar",
                "aba_normativa": "",
                "aba_encontrada_planilha": nome,
                "existe_na_planilha": True,
                "reconhecida_no_config_abas": nome in set(str(v) for v in abas_cfg.values()),
                "chave_config": next((str(k) for k, v in abas_cfg.items() if str(v) == nome), ""),
                "status_aderencia": "auxiliar_ou_nao_mapeada_v17",
            })
    return linhas


def _linhas_campos(pacote_planilha: Any, config: dict[str, Any]) -> list[dict[str, Any]]:
    nomes_abas = list(getattr(pacote_planilha, "nomes_abas", []) or [])
    quadros = getattr(pacote_planilha, "quadros_brutos", {}) or {}
    linhas: list[dict[str, Any]] = []
    for familia, spec in CAMPOS_V17.items():
        aba_normativa = spec["aba"]
        aba_encontrada = _encontrar_aba(nomes_abas, aba_normativa)
        df = quadros.get(aba_encontrada) if aba_encontrada else None
        colunas = _colunas_df(df)
        bloco_config = spec.get("origem_config", "")
        for campo, aliases_padrao in spec["campos"].items():
            aliases_cfg = _aliases_config(config, bloco_config, campo)
            aliases = aliases_cfg or aliases_padrao
            col = _encontrar_coluna(colunas, aliases)
            linhas.append({
                "familia_v17": familia,
                "aba_normativa": aba_normativa,
                "aba_encontrada": aba_encontrada,
                "campo_normativo": campo,
                "coluna_encontrada": col,
                "origem_alias": "config" if aliases_cfg else "inferido_v17_a0_1",
                "aliases_testados": " | ".join(aliases),
                "status_campo": "reconhecido" if col else ("aba_ausente" if not aba_encontrada else "campo_nao_reconhecido"),
            })
    return linhas


def _texto_arquivo(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _detectar_fontes_antigas() -> list[dict[str, Any]]:
    linhas: list[dict[str, Any]] = []
    for token in FONTES_ANTIGAS:
        total = 0
        arquivos = []
        for path in ARQUIVOS_CODIGO_ALVO:
            texto = _texto_arquivo(path)
            if not texto:
                continue
            qtd = texto.count(token)
            if qtd:
                total += qtd
                arquivos.append(f"{path.relative_to(RAIZ)}:{qtd}")
        linhas.append({
            "fonte_antiga": token,
            "ocorrencias_codigo": total,
            "arquivos": " | ".join(arquivos),
            "status": "detectada" if total else "nao_detectada",
            "leitura_v17_a0_1": "taxonomia_pre_v17_a_mapear" if total else "sem_ocorrencia_estatica",
        })
    return linhas


def _detectar_fontes_v17() -> list[dict[str, Any]]:
    linhas: list[dict[str, Any]] = []
    textos = {str(path.relative_to(RAIZ)): _texto_arquivo(path) for path in ARQUIVOS_CODIGO_ALVO}
    for token in FONTES_V17:
        total = sum(texto.count(token) for texto in textos.values())
        arquivos = [f"{nome}:{texto.count(token)}" for nome, texto in textos.items() if texto.count(token)]
        linhas.append({
            "fonte_v17": token,
            "ocorrencias_codigo": total,
            "arquivos": " | ".join(arquivos),
            "status_aderencia": "presente_como_token" if total else "ausente_como_tipo_canonico_explicito",
            "acao_recomendada": "auditar_semantica_antes_de_usar" if total else "criar_mapeamento_canonico_nao_funcional_primeiro",
        })
    return linhas


def _ocorrencias_saldo_gastos(pacote_planilha: Any, config: dict[str, Any]) -> list[dict[str, Any]]:
    nomes_abas = list(getattr(pacote_planilha, "nomes_abas", []) or [])
    aba = _encontrar_aba(nomes_abas, "Todos os Gastos")
    df = (getattr(pacote_planilha, "quadros_brutos", {}) or {}).get(aba)
    if df is None or df.empty:
        return []
    colunas = _colunas_df(df)
    col_id = _encontrar_coluna(colunas, _aliases_config(config, "despesas", "despesa_id") or ["ID", "despesa_id"])
    col_data = _encontrar_coluna(colunas, _aliases_config(config, "despesas", "data") or ["Data"])
    col_desc = _encontrar_coluna(colunas, _aliases_config(config, "despesas", "descricao") or ["Descrição", "Descricao"])
    col_valor = _encontrar_coluna(colunas, _aliases_config(config, "despesas", "valor") or ["Valor"])
    candidatos_lote = [
        _encontrar_coluna(colunas, _aliases_config(config, "despesas", "lote_usado_1") or ["Lote usado", "Lote usado 1"]),
        _encontrar_coluna(colunas, _aliases_config(config, "despesas", "lote_usado_2") or ["Lote usado 2"]),
    ]
    candidatos_lote = [c for c in candidatos_lote if c]
    linhas = []
    for idx, row in df.iterrows():
        for col_lote in candidatos_lote:
            valor_lote = row.get(col_lote)
            if _norm(valor_lote) == "saldo":
                linhas.append({
                    "linha_planilha_1base": int(idx) + 2,
                    "despesa_id": row.get(col_id, "") if col_id else "",
                    "data": _fmt_data(row.get(col_data, "")) if col_data else "",
                    "descricao": row.get(col_desc, "") if col_desc else "",
                    "valor": _to_float(row.get(col_valor, 0.0)) if col_valor else 0.0,
                    "coluna_lote_usado": col_lote,
                    "valor_lote_usado": valor_lote,
                    "classificacao_v17_esperada": "pagamento_por_saldo",
                    "risco_codigo_atual": "saldo_nao_pode_ser_produto_carteira_nem_lote_investido",
                })
    return linhas


def _lotes_caixa_disponivel_candidatos(pacote_planilha: Any, config: dict[str, Any]) -> list[dict[str, Any]]:
    nomes_abas = list(getattr(pacote_planilha, "nomes_abas", []) or [])
    aba = _encontrar_aba(nomes_abas, "Inventário de Lotes")
    df = (getattr(pacote_planilha, "quadros_brutos", {}) or {}).get(aba)
    if df is None or df.empty:
        return []
    colunas = _colunas_df(df)
    col_id = _encontrar_coluna(colunas, _aliases_config(config, "lotes", "lote_id") or ["Lote (ID)", "ID"])
    col_data_rec = _encontrar_coluna(colunas, _aliases_config(config, "lotes", "data_recebimento") or ["Data Recebimento"])
    col_data_apl = _encontrar_coluna(colunas, _aliases_config(config, "lotes", "data_aplicacao") or ["Data Aplicação", "Data Aplicacao"])
    col_valor = _encontrar_coluna(colunas, _aliases_config(config, "lotes", "valor_original") or ["Valor Original"])
    col_inv = _encontrar_coluna(colunas, _aliases_config(config, "lotes", "produto_id") or ["Investimento", "Produto"])
    linhas = []
    for idx, row in df.iterrows():
        tem_data_rec = not _is_blank(row.get(col_data_rec)) if col_data_rec else False
        valor = _to_float(row.get(col_valor, 0.0)) if col_valor else 0.0
        data_apl_vazia = _is_blank(row.get(col_data_apl)) if col_data_apl else True
        investimento_vazio = _is_blank(row.get(col_inv)) if col_inv else True
        if tem_data_rec and valor > 0 and data_apl_vazia and investimento_vazio:
            linhas.append({
                "linha_planilha_1base": int(idx) + 2,
                "lote_id": row.get(col_id, "") if col_id else "",
                "data_recebimento": _fmt_data(row.get(col_data_rec, "")) if col_data_rec else "",
                "data_aplicacao": _fmt_data(row.get(col_data_apl, "")) if col_data_apl else "",
                "valor_original": valor,
                "investimento": row.get(col_inv, "") if col_inv else "",
                "classificacao_v17_esperada": "lote_caixa_disponivel",
                "risco_codigo_atual": "nao_preencher_data_aplicacao_artificialmente",
            })
    return linhas


def _switchings_entrada_candidatos(pacote_planilha: Any) -> list[dict[str, Any]]:
    nomes_abas = list(getattr(pacote_planilha, "nomes_abas", []) or [])
    aba_sw = _encontrar_aba(nomes_abas, "Switching")
    aba_lotes = _encontrar_aba(nomes_abas, "Inventário de Lotes")
    quadros = getattr(pacote_planilha, "quadros_brutos", {}) or {}
    df = quadros.get(aba_sw)
    inv = quadros.get(aba_lotes)
    ids_inventario: set[str] = set()
    if inv is not None and not inv.empty:
        col_id_inv = _encontrar_coluna(_colunas_df(inv), ["Lote (ID)", "lote_id", "ID"])
        if col_id_inv:
            ids_inventario = {_norm(v) for v in inv[col_id_inv].tolist() if not _is_blank(v)}
    if df is None or df.empty:
        return []
    colunas = _colunas_df(df)
    col_antes = _encontrar_coluna(colunas, ["Lote (ID) Antes", "Lote Antes", "lote_id_antes"])
    col_depois = _encontrar_coluna(colunas, ["Lote (ID) Depois", "Lote Depois", "lote_id_depois"])
    col_data_rec = _encontrar_coluna(colunas, ["Data Recebimento", "data_recebimento"])
    col_data_apl = _encontrar_coluna(colunas, ["Data Aplicação", "Data Aplicacao", "data_aplicacao"])
    col_valor = _encontrar_coluna(colunas, ["Valor Líquido Migrado", "Valor Liquido Migrado", "valor_liquido_migrado", "Valor Original"])
    col_inv = _encontrar_coluna(colunas, ["Investimento", "Produto Destino", "produto_destino"])
    linhas = []
    for idx, row in df.iterrows():
        lote_depois = row.get(col_depois, "") if col_depois else ""
        linhas.append({
            "linha_planilha_1base": int(idx) + 2,
            "aba_switching_encontrada": aba_sw,
            "lote_id_antes": row.get(col_antes, "") if col_antes else "",
            "lote_id_depois": lote_depois,
            "data_recebimento": _fmt_data(row.get(col_data_rec, "")) if col_data_rec else "",
            "data_aplicacao": _fmt_data(row.get(col_data_apl, "")) if col_data_apl else "",
            "valor_liquido_migrado": _to_float(row.get(col_valor, 0.0)) if col_valor else 0.0,
            "investimento_destino": row.get(col_inv, "") if col_inv else "",
            "destino_tambem_no_inventario": _norm(lote_depois) in ids_inventario if lote_depois else False,
            "classificacao_v17_esperada": "switching_destino_materializado",
            "risco_v17": "reconciliar_com_inventario_para_impedir_contagem_dupla",
        })
    return linhas


def _pontos_saida() -> list[dict[str, Any]]:
    path = RAIZ / "nucleo" / "saida_canonica.py"
    texto = _texto_arquivo(path)
    linhas_txt = texto.splitlines()
    linhas: list[dict[str, Any]] = []
    for termo, leitura in PONTOS_SAIDA:
        for i, line in enumerate(linhas_txt, start=1):
            if termo in line:
                contexto = line.strip()
                linhas.append({
                    "arquivo": str(path.relative_to(RAIZ)),
                    "linha": i,
                    "termo_detectado": termo,
                    "tipo_ponto": leitura,
                    "trecho": contexto[:240],
                    "risco_v17_a0_1": "saida_deve_renderizar_estado_decidido_sem_inferir_ou_corrigir_decisao",
                })
    return linhas


def main() -> int:
    pacote_config = carregar_config(raiz_repositorio=RAIZ)
    config = pacote_config.conteudo
    pacote_planilha = carregar_planilha(config, raiz_repositorio=RAIZ, carregar_todas_as_abas=True)

    linhas_abas = _linhas_abas(pacote_planilha, config)
    linhas_campos = _linhas_campos(pacote_planilha, config)
    linhas_fontes_antigas = _detectar_fontes_antigas()
    linhas_fontes_v17 = _detectar_fontes_v17()
    linhas_saldo = _ocorrencias_saldo_gastos(pacote_planilha, config)
    linhas_lotes_caixa = _lotes_caixa_disponivel_candidatos(pacote_planilha, config)
    linhas_switching = _switchings_entrada_candidatos(pacote_planilha)
    linhas_saida = _pontos_saida()

    _gravar_csv(pd.DataFrame(linhas_abas), ARQ_ABAS, [
        "familia_v17", "aba_normativa", "aba_encontrada_planilha", "existe_na_planilha",
        "reconhecida_no_config_abas", "chave_config", "status_aderencia",
    ])
    _gravar_csv(pd.DataFrame(linhas_campos), ARQ_CAMPOS, [
        "familia_v17", "aba_normativa", "aba_encontrada", "campo_normativo", "coluna_encontrada",
        "origem_alias", "aliases_testados", "status_campo",
    ])
    _gravar_csv(pd.DataFrame(linhas_fontes_antigas), ARQ_FONTES_ANTIGAS, [
        "fonte_antiga", "ocorrencias_codigo", "arquivos", "status", "leitura_v17_a0_1",
    ])
    _gravar_csv(pd.DataFrame(linhas_fontes_v17), ARQ_FONTES_V17, [
        "fonte_v17", "ocorrencias_codigo", "arquivos", "status_aderencia", "acao_recomendada",
    ])
    _gravar_csv(pd.DataFrame(linhas_saldo), ARQ_SALDO_GASTOS, [
        "linha_planilha_1base", "despesa_id", "data", "descricao", "valor", "coluna_lote_usado",
        "valor_lote_usado", "classificacao_v17_esperada", "risco_codigo_atual",
    ])
    _gravar_csv(pd.DataFrame(linhas_lotes_caixa), ARQ_LOTES_CAIXA, [
        "linha_planilha_1base", "lote_id", "data_recebimento", "data_aplicacao", "valor_original",
        "investimento", "classificacao_v17_esperada", "risco_codigo_atual",
    ])
    _gravar_csv(pd.DataFrame(linhas_switching), ARQ_SWITCHING, [
        "linha_planilha_1base", "aba_switching_encontrada", "lote_id_antes", "lote_id_depois",
        "data_recebimento", "data_aplicacao", "valor_liquido_migrado", "investimento_destino",
        "destino_tambem_no_inventario", "classificacao_v17_esperada", "risco_v17",
    ])
    _gravar_csv(pd.DataFrame(linhas_saida), ARQ_SAIDA, [
        "arquivo", "linha", "termo_detectado", "tipo_ponto", "trecho", "risco_v17_a0_1",
    ])

    abas_obrigatorias_ausentes = [l for l in linhas_abas if l["aba_normativa"] and not l["existe_na_planilha"]]
    abas_nao_config = [l for l in linhas_abas if l["aba_normativa"] and l["existe_na_planilha"] and not l["reconhecida_no_config_abas"]]
    fontes_antigas_detectadas = [l for l in linhas_fontes_antigas if l["ocorrencias_codigo"] > 0]
    fontes_v17_ausentes = [l for l in linhas_fontes_v17 if l["ocorrencias_codigo"] == 0]
    campos_nao_reconhecidos = [l for l in linhas_campos if l["status_campo"] != "reconhecido"]

    resumo = [
        {"metrica": "versao_diagnostico", "valor": "V17-A0.1", "status": "diagnostico_sem_motor", "observacao": "script novo; sem alteracao funcional"},
        {"metrica": "abas_planilha_total", "valor": len(getattr(pacote_planilha, "nomes_abas", []) or []), "status": "info", "observacao": "leitura fisica via carregar_planilha"},
        {"metrica": "abas_v17_ausentes", "valor": len(abas_obrigatorias_ausentes), "status": "bloqueia_v17_a_funcional" if abas_obrigatorias_ausentes else "ok", "observacao": " | ".join(l["aba_normativa"] for l in abas_obrigatorias_ausentes)},
        {"metrica": "abas_v17_existentes_mas_nao_configuradas", "valor": len(abas_nao_config), "status": "bloqueia_v17_a_funcional" if abas_nao_config else "ok", "observacao": " | ".join(l["aba_normativa"] for l in abas_nao_config)},
        {"metrica": "campos_v17_nao_reconhecidos", "valor": len(campos_nao_reconhecidos), "status": "requer_mapeamento", "observacao": "ver CSV de campos"},
        {"metrica": "fontes_antigas_detectadas", "valor": len(fontes_antigas_detectadas), "status": "requer_traducao_taxonomica", "observacao": "ver CSV de fontes antigas"},
        {"metrica": "fontes_v17_ausentes_como_tipo_explicito", "valor": len(fontes_v17_ausentes), "status": "requer_camada_canonica_v17", "observacao": "ver CSV de aderencia de fontes V17"},
        {"metrica": "ocorrencias_saldo_em_gastos", "valor": len(linhas_saldo), "status": "diagnostico", "observacao": "Saldo deve ser pagamento_por_saldo"},
        {"metrica": "lotes_caixa_disponivel_candidatos", "valor": len(linhas_lotes_caixa), "status": "diagnostico", "observacao": "lotes com recebimento/valor e sem aplicacao/investimento"},
        {"metrica": "switchings_entrada_candidatos", "valor": len(linhas_switching), "status": "diagnostico", "observacao": "destinos devem ser materializados/reconciliados"},
        {"metrica": "pontos_saida_altera_limpa_completa", "valor": len(linhas_saida), "status": "risco_arquitetural", "observacao": "saida deve apenas renderizar estado"},
    ]
    _gravar_csv(pd.DataFrame(resumo), ARQ_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-A0.1 — AUDITORIA DIAGNOSTICA DE ADERENCIA ===")
    print(f"abas_planilha_total={len(getattr(pacote_planilha, 'nomes_abas', []) or [])}")
    print(f"abas_v17_ausentes={len(abas_obrigatorias_ausentes)}")
    print(f"abas_v17_existentes_mas_nao_configuradas={len(abas_nao_config)}")
    print(f"campos_v17_nao_reconhecidos={len(campos_nao_reconhecidos)}")
    print(f"fontes_antigas_detectadas={len(fontes_antigas_detectadas)}")
    print(f"fontes_v17_ausentes_como_tipo_explicito={len(fontes_v17_ausentes)}")
    print(f"ocorrencias_saldo_em_gastos={len(linhas_saldo)}")
    print(f"lotes_caixa_disponivel_candidatos={len(linhas_lotes_caixa)}")
    print(f"switchings_entrada_candidatos={len(linhas_switching)}")
    print(f"pontos_saida_altera_limpa_completa={len(linhas_saida)}")
    print(f"saida_dir={OUT_DIR}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
