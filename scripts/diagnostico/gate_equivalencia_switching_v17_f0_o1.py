from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.ledger_temporal_conjunto import construir_ledger_temporal_conjunto
from nucleo.pacote_orquestrado_pre_saida import montar_pacote_orquestrado_pre_saida


ARQUIVO_COMPARACAO = RAIZ_REPOSITORIO / "saidas" / "diagnostico" / "gate_equivalencia_switching_v17_f0_o1.csv"


@dataclass(slots=True)
class FonteSwitching:
    nome: str
    registros: list[dict[str, Any]]
    erro: str = ""


def _txt(valor: Any) -> str:
    if valor is None:
        return ""
    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass
    return str(valor).strip()


def _norm(valor: Any) -> str:
    texto = _txt(valor).lower()
    texto = " ".join(texto.split())
    return texto


def _data_iso(valor: Any) -> str:
    if valor is None:
        return ""
    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass
    if hasattr(valor, "date") and not isinstance(valor, str):
        try:
            return valor.date().isoformat()
        except Exception:
            pass
    if hasattr(valor, "isoformat") and not isinstance(valor, str):
        try:
            return valor.isoformat()[:10]
        except Exception:
            pass
    texto = _txt(valor)
    if not texto:
        return ""
    for dayfirst in (False, True):
        try:
            data = pd.to_datetime(texto, errors="raise", dayfirst=dayfirst)
            if not pd.isna(data):
                return data.date().isoformat()
        except Exception:
            continue
    return texto[:10]


def _numero(valor: Any) -> str:
    texto = _txt(valor)
    if not texto:
        return ""
    try:
        return f"{float(valor):.2f}"
    except Exception:
        pass
    try:
        limpo = texto.replace("R$", "").strip()
        if "," in limpo:
            limpo = limpo.replace(".", "").replace(",", ".")
        return f"{float(limpo):.2f}"
    except Exception:
        return texto


def _primeiro(d: dict[str, Any], nomes: list[str]) -> Any:
    mapa = {_norm(k): k for k in d.keys()}
    for nome in nomes:
        chave = mapa.get(_norm(nome))
        if chave is None:
            continue
        valor = d.get(chave)
        if _txt(valor):
            return valor
    return ""


def _df_para_registros(df: Any) -> list[dict[str, Any]]:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return []
    return [dict(row) for row in df.to_dict(orient="records")]


def _canonizar(registros: list[dict[str, Any]], origem: str) -> list[dict[str, Any]]:
    saida: list[dict[str, Any]] = []
    for indice, registro in enumerate(registros, start=1):
        if not isinstance(registro, dict):
            continue
        data = _data_iso(_primeiro(registro, [
            "Data", "Data sugerida", "data_switching", "data_sugerida_switching",
            "Data Aplicação", "data_aplicacao", "Data Recebimento", "data_recebimento",
        ]))
        lote_origem = _txt(_primeiro(registro, [
            "Lote origem", "lote_origem", "lote_id_origem", "lote_id_antes",
            "Lote (ID) Antes", "lote antes", "Lote Antes", "lote_id",
        ]))
        lote_destino = _txt(_primeiro(registro, [
            "Lote destino", "lote_destino", "lote_id_destino", "lote_id_depois",
            "Lote (ID) Depois", "lote depois", "Lote Depois", "lote_pos_switching",
        ]))
        produto_destino = _txt(_primeiro(registro, [
            "Produto destino switching", "produto_destino_switching", "produto_destino",
            "Investimento", "investimento", "Destino", "destino", "produto_destino_nome",
            "produto_destino_key",
        ]))
        valor_liquido = _numero(_primeiro(registro, [
            "Valor líquido origem", "valor_liquido_origem", "Valor líquido total",
            "Valor Líquido Migrado", "valor_liquido_migrado", "valor_liquido_resgatavel",
            "Valor migrado",
        ]))
        status = _txt(_primeiro(registro, [
            "Status", "status", "Status reconciliação", "status_reconciliacao",
            "status_switching", "status_materializacao_passiva",
        ]))
        chave = "|".join([
            _norm(data),
            _norm(lote_origem),
            _norm(lote_destino),
            _norm(produto_destino),
            valor_liquido,
        ])
        saida.append({
            "origem": origem,
            "indice_origem": indice,
            "data": data,
            "lote_origem": lote_origem,
            "lote_destino": lote_destino,
            "produto_destino": produto_destino,
            "valor_liquido": valor_liquido,
            "status": status,
            "chave_equivalencia": chave,
            "registro_json": json.dumps(registro, ensure_ascii=False, default=str, sort_keys=True),
        })
    return saida


def _switchings_ponte(saida: Any) -> FonteSwitching:
    return FonteSwitching("saida.switchings_pos_ponte_v17_c7", _canonizar(list(getattr(saida, "switchings", []) or []), "saida.switchings_pos_ponte_v17_c7"))


def _switchings_pre_saida(contexto: Any) -> FonteSwitching:
    try:
        pacote = montar_pacote_orquestrado_pre_saida(contexto)
        df = getattr(pacote, "estado_temporal_switching", pd.DataFrame())
        return FonteSwitching("pacote_orquestrado_pre_saida.estado_temporal_switching", _canonizar(_df_para_registros(df), "pacote_orquestrado_pre_saida.estado_temporal_switching"))
    except Exception as erro:
        return FonteSwitching("pacote_orquestrado_pre_saida.estado_temporal_switching", [], f"{erro.__class__.__name__}: {erro}")


def _resolver_quadro_switching_planilha(contexto: Any) -> tuple[str, pd.DataFrame]:
    pacote_planilha = getattr(contexto, "pacote_planilha", None)
    quadros_canonicos = getattr(pacote_planilha, "quadros_canonicos", {}) if pacote_planilha is not None else {}
    quadros_brutos = getattr(pacote_planilha, "quadros_brutos", {}) if pacote_planilha is not None else {}
    config = getattr(getattr(contexto, "pacote_config", None), "conteudo", {}) or {}
    nome_config = ((config.get("abas") or {}).get("switching") if isinstance(config, dict) else None) or "Switching"
    candidatos = [nome_config, "Switching", "Switiching", "Swtiching"]

    for nome in candidatos:
        if isinstance(quadros_canonicos, dict) and isinstance(quadros_canonicos.get(nome), pd.DataFrame):
            return nome, quadros_canonicos[nome].copy()
        if isinstance(quadros_brutos, dict) and isinstance(quadros_brutos.get(nome), pd.DataFrame):
            return nome, quadros_brutos[nome].copy()

    nomes = []
    if isinstance(quadros_canonicos, dict):
        nomes.extend(list(quadros_canonicos.keys()))
    if isinstance(quadros_brutos, dict):
        nomes.extend(list(quadros_brutos.keys()))
    for nome_real in nomes:
        if _norm(nome_real) in {_norm(x) for x in candidatos}:
            if isinstance(quadros_canonicos, dict) and isinstance(quadros_canonicos.get(nome_real), pd.DataFrame):
                return str(nome_real), quadros_canonicos[nome_real].copy()
            if isinstance(quadros_brutos, dict) and isinstance(quadros_brutos.get(nome_real), pd.DataFrame):
                return str(nome_real), quadros_brutos[nome_real].copy()

    return "", pd.DataFrame()


def _switchings_aba(contexto: Any) -> FonteSwitching:
    try:
        nome, df = _resolver_quadro_switching_planilha(contexto)
        origem = f"planilha.aba_switching[{nome or 'nao_encontrada'}]"
        return FonteSwitching(origem, _canonizar(_df_para_registros(df), origem))
    except Exception as erro:
        return FonteSwitching("planilha.aba_switching", [], f"{erro.__class__.__name__}: {erro}")


def _mapa_central(contexto: Any) -> dict[str, dict[str, Any]]:
    pacote = getattr(contexto, "recomputacao_sequencial_central_v1", None)
    quadro = getattr(pacote, "quadro_recomputacao_sequencial_central", None) if pacote is not None else None
    mapa: dict[str, dict[str, Any]] = {}
    if isinstance(quadro, pd.DataFrame) and not quadro.empty:
        for _, row in quadro.iterrows():
            pid = _txt(row.get("pagamento_id"))
            if pid:
                mapa[pid] = row.to_dict()
    return mapa


def _eventos_switching_do_resultado_ledger(resultado: Any) -> list[dict[str, Any]]:
    eventos: list[dict[str, Any]] = []
    if isinstance(resultado, dict):
        bruto = resultado.get("eventos") or resultado.get("ledger") or []
    elif isinstance(resultado, list):
        bruto = resultado
    else:
        bruto = []
    if isinstance(bruto, pd.DataFrame):
        bruto = bruto.to_dict(orient="records")
    if not isinstance(bruto, list):
        return []
    for evento in bruto:
        if not isinstance(evento, dict):
            continue
        texto = json.dumps(evento, ensure_ascii=False, default=str).lower()
        chaves = {_norm(k) for k in evento.keys()}
        tem_campo_switching = bool({
            "evento_switching_id", "data_switching", "lote_origem", "lote_pos_switching",
            "produto_destino", "status_materializacao_passiva", "origem_mapa_migracao",
        } & chaves)
        tem_tipo_switching = "switching" in _norm(evento.get("tipo_evento") or evento.get("evento") or evento.get("tipo"))
        if tem_campo_switching or tem_tipo_switching or "switching" in texto:
            eventos.append(evento)
    return eventos


def _switchings_ledger(contexto: Any, saida: Any) -> FonteSwitching:
    tentativas: list[tuple[str, pd.DataFrame]] = []
    motor = getattr(contexto, "motor_recomendacao_pagamentos_switching_v1", None)
    quadro_motor = getattr(motor, "quadro_recomendacoes", None) if motor is not None else None
    if isinstance(quadro_motor, pd.DataFrame) and not quadro_motor.empty:
        tentativas.append(("motor_recomendacao_pagamentos_switching_v1.quadro_recomendacoes", quadro_motor.copy()))

    extrato_futuro = pd.DataFrame(list(getattr(saida, "extrato_futuro", []) or []))
    if not extrato_futuro.empty:
        tentativas.append(("saida.extrato_futuro", extrato_futuro))

    erros: list[str] = []
    todos_eventos: list[dict[str, Any]] = []
    for nome, quadro in tentativas:
        try:
            resultado = construir_ledger_temporal_conjunto(quadro, _mapa_central(contexto), contexto)
            eventos = _eventos_switching_do_resultado_ledger(resultado)
            for evento in eventos:
                evento = dict(evento)
                evento["_origem_tentativa_ledger"] = nome
                todos_eventos.append(evento)
        except Exception as erro:
            erros.append(f"{nome}: {erro.__class__.__name__}: {erro}")

    registros = _canonizar(todos_eventos, "ledger_temporal_conjunto.eventos_switching")
    return FonteSwitching("ledger_temporal_conjunto.eventos_switching", registros, " | ".join(erros))


def _linha_resumo(origens: dict[str, FonteSwitching], ponte_equivale_ledger: bool) -> list[dict[str, Any]]:
    return [{
        "tipo_linha": "resumo",
        "fonte": "veredito",
        "ponte_equivale_ledger": "sim" if ponte_equivale_ledger else "nao",
        "switchings_ponte": len(origens["ponte"].registros),
        "switchings_pre_saida": len(origens["pre_saida"].registros),
        "switchings_ledger": len(origens["ledger"].registros),
        "switchings_aba": len(origens["aba"].registros),
        "erro_pre_saida": origens["pre_saida"].erro,
        "erro_ledger": origens["ledger"].erro,
        "erro_aba": origens["aba"].erro,
    }]


def _linhas_comparacao(origens: dict[str, FonteSwitching]) -> list[dict[str, Any]]:
    por_chave: dict[str, dict[str, Any]] = {}
    for nome_curto, fonte in origens.items():
        for registro in fonte.registros:
            chave = registro.get("chave_equivalencia", "")
            linha = por_chave.setdefault(chave, {
                "tipo_linha": "comparacao",
                "chave_equivalencia": chave,
                "data": registro.get("data", ""),
                "lote_origem": registro.get("lote_origem", ""),
                "lote_destino": registro.get("lote_destino", ""),
                "produto_destino": registro.get("produto_destino", ""),
                "valor_liquido": registro.get("valor_liquido", ""),
                "em_ponte": "nao",
                "em_pre_saida": "nao",
                "em_ledger": "nao",
                "em_aba": "nao",
                "status_ponte": "",
                "status_pre_saida": "",
                "status_ledger": "",
                "status_aba": "",
                "json_ponte": "",
                "json_pre_saida": "",
                "json_ledger": "",
                "json_aba": "",
            })
            if nome_curto == "ponte":
                linha["em_ponte"] = "sim"
                linha["status_ponte"] = registro.get("status", "")
                linha["json_ponte"] = registro.get("registro_json", "")
            elif nome_curto == "pre_saida":
                linha["em_pre_saida"] = "sim"
                linha["status_pre_saida"] = registro.get("status", "")
                linha["json_pre_saida"] = registro.get("registro_json", "")
            elif nome_curto == "ledger":
                linha["em_ledger"] = "sim"
                linha["status_ledger"] = registro.get("status", "")
                linha["json_ledger"] = registro.get("registro_json", "")
            elif nome_curto == "aba":
                linha["em_aba"] = "sim"
                linha["status_aba"] = registro.get("status", "")
                linha["json_aba"] = registro.get("registro_json", "")
    linhas = list(por_chave.values())
    linhas.sort(key=lambda r: (str(r.get("data", "")), str(r.get("lote_origem", "")), str(r.get("produto_destino", "")), str(r.get("valor_liquido", ""))))
    for linha in linhas:
        divergencias = []
        if linha.get("em_ponte") == "sim" and linha.get("em_ledger") != "sim":
            divergencias.append("ponte_sem_equivalente_ledger")
        if linha.get("em_ledger") == "sim" and linha.get("em_ponte") != "sim":
            divergencias.append("ledger_sem_equivalente_ponte")
        if linha.get("em_ponte") == "sim" and linha.get("em_aba") != "sim":
            divergencias.append("ponte_sem_equivalente_aba")
        if linha.get("em_ponte") == "sim" and linha.get("em_pre_saida") != "sim":
            divergencias.append("ponte_sem_equivalente_pre_saida")
        linha["divergencias"] = ";".join(divergencias) if divergencias else "n/d"
    return linhas


def main() -> None:
    contexto = carregar_contexto_baseline(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    saida = construir_saida_canonica_com_switching_v17_c7(contexto, versao=VERSAO_BASELINE)

    origens = {
        "ponte": _switchings_ponte(saida),
        "pre_saida": _switchings_pre_saida(contexto),
        "ledger": _switchings_ledger(contexto, saida),
        "aba": _switchings_aba(contexto),
    }

    chaves_ponte = {r["chave_equivalencia"] for r in origens["ponte"].registros}
    chaves_ledger = {r["chave_equivalencia"] for r in origens["ledger"].registros}
    ponte_equivale_ledger = bool(chaves_ponte) and chaves_ponte == chaves_ledger

    linhas = _linha_resumo(origens, ponte_equivale_ledger) + _linhas_comparacao(origens)
    ARQUIVO_COMPARACAO.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(linhas).to_csv(ARQUIVO_COMPARACAO, index=False)

    print("=== GATE V17-F0-O.1 — EQUIVALÊNCIA SWITCHING PONTE VS LEDGER ===")
    print(f"versao_baseline={VERSAO_BASELINE}")
    print(f"ponte_equivale_ledger={'sim' if ponte_equivale_ledger else 'nao'}")
    print(f"switchings_ponte={len(origens['ponte'].registros)}")
    print(f"switchings_pre_saida={len(origens['pre_saida'].registros)}")
    print(f"switchings_ledger={len(origens['ledger'].registros)}")
    print(f"switchings_aba={len(origens['aba'].registros)}")
    if origens["ledger"].erro:
        print(f"erro_ledger={origens['ledger'].erro}")
    print(f"csv={ARQUIVO_COMPARACAO}")

    comparacao = pd.DataFrame(_linhas_comparacao(origens))
    if not comparacao.empty:
        colunas = ["data", "lote_origem", "lote_destino", "produto_destino", "valor_liquido", "em_ponte", "em_pre_saida", "em_ledger", "em_aba", "divergencias"]
        print("\n=== AMOSTRA COMPARATIVA ===")
        print(comparacao[colunas].to_string(index=False))

    if ponte_equivale_ledger:
        print("\nrecomendacao=ponte_pode_ser_removida_em_microetapa_posterior_apenas_com_gate_de_regressao")
    else:
        print("\nrecomendacao=manter_ponte_e_migrar_materializacao_dos_switchings_para_ledger_estado_temporal_em_microetapa_posterior")


if __name__ == "__main__":
    main()
