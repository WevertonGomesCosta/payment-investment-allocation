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
from nucleo.ledger_switching_estado_temporal_v17_f0_o2 import materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2
from nucleo.ledger_temporal_conjunto import construir_ledger_temporal_conjunto
from nucleo.pacote_orquestrado_pre_saida import montar_pacote_orquestrado_pre_saida

ARQUIVO_COMPARACAO = RAIZ_REPOSITORIO / "saidas" / "diagnostico" / "gate_equivalencia_switching_v17_f0_o1.csv"


@dataclass(slots=True)
class FonteSwitching:
    nome: str
    registros: list[dict[str, Any]]
    erro: str = ""
    detalhes: dict[str, Any] | None = None


def _txt(v: Any) -> str:
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass
    return str(v).strip()


def _norm(v: Any) -> str:
    return " ".join(_txt(v).lower().split())


def _pick(d: dict[str, Any], nomes: list[str]) -> Any:
    mapa = {_norm(k): k for k in d.keys()}
    for nome in nomes:
        chave = mapa.get(_norm(nome))
        if chave is not None and _txt(d.get(chave)):
            return d.get(chave)
    return ""


def _data(v: Any) -> str:
    if not _txt(v):
        return ""
    if hasattr(v, "date") and not isinstance(v, str):
        try:
            return v.date().isoformat()
        except Exception:
            pass
    for dayfirst in (False, True):
        try:
            dt = pd.to_datetime(v, errors="raise", dayfirst=dayfirst)
            if not pd.isna(dt):
                return dt.date().isoformat()
        except Exception:
            pass
    return _txt(v)[:10]


def _num(v: Any) -> str:
    texto = _txt(v)
    if not texto:
        return ""
    try:
        return f"{float(v):.2f}"
    except Exception:
        pass
    try:
        limpo = texto.replace("R$", "").strip()
        if "," in limpo:
            limpo = limpo.replace(".", "").replace(",", ".")
        return f"{float(limpo):.2f}"
    except Exception:
        return texto


def _df_records(df: Any) -> list[dict[str, Any]]:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return []
    return [dict(x) for x in df.to_dict(orient="records")]


def _canon(registros: list[dict[str, Any]], origem: str) -> list[dict[str, Any]]:
    saida = []
    for i, r in enumerate(registros, start=1):
        if not isinstance(r, dict):
            continue
        data = _data(_pick(r, ["Data", "Data sugerida", "data_switching", "Data Aplicação", "data_aplicacao", "Data Recebimento", "data_recebimento"]))
        origem_lote = _txt(_pick(r, ["Lote origem", "lote_origem", "lote_id_origem", "lote_id_antes", "Lote (ID) Antes", "lote_id"]))
        destino_lote = _txt(_pick(r, ["Lote destino", "lote_destino", "lote_id_destino", "lote_id_depois", "Lote (ID) Depois", "lote_pos_switching"]))
        produto_destino = _txt(_pick(r, ["Produto destino switching", "produto_destino", "Investimento", "investimento", "Destino", "produto_destino_nome", "produto_destino_key"]))
        valor = _num(_pick(r, ["Valor líquido origem", "valor_liquido_origem", "Valor líquido total", "Valor Líquido Migrado", "valor_liquido_migrado", "valor_liquido_resgatavel"]))
        status = _txt(_pick(r, ["Status", "status", "Status reconciliação", "status_reconciliacao", "status_switching", "status_materializacao_passiva", "status_materializacao"]))
        chave = "|".join([_norm(data), _norm(origem_lote), _norm(destino_lote), _norm(produto_destino), valor])
        saida.append({
            "origem": origem,
            "indice_origem": i,
            "data": data,
            "lote_origem": origem_lote,
            "lote_destino": destino_lote,
            "produto_destino": produto_destino,
            "valor_liquido": valor,
            "status": status,
            "chave_equivalencia": chave,
            "registro_json": json.dumps(r, ensure_ascii=False, default=str, sort_keys=True),
        })
    return saida


def _switchings_ponte(saida: Any) -> FonteSwitching:
    return FonteSwitching("saida.switchings_pos_ponte_v17_c7", _canon(list(getattr(saida, "switchings", []) or []), "saida.switchings_pos_ponte_v17_c7"))


def _switchings_pre_saida(contexto: Any) -> FonteSwitching:
    try:
        pacote = montar_pacote_orquestrado_pre_saida(contexto)
        return FonteSwitching("pacote_orquestrado_pre_saida.estado_temporal_switching", _canon(_df_records(getattr(pacote, "estado_temporal_switching", pd.DataFrame())), "pacote_orquestrado_pre_saida.estado_temporal_switching"))
    except Exception as e:
        return FonteSwitching("pacote_orquestrado_pre_saida.estado_temporal_switching", [], f"{e.__class__.__name__}: {e}")


def _quadro_aba_switching(contexto: Any) -> tuple[str, pd.DataFrame]:
    pacote = getattr(contexto, "pacote_planilha", None)
    canonicos = getattr(pacote, "quadros_canonicos", {}) if pacote is not None else {}
    brutos = getattr(pacote, "quadros_brutos", {}) if pacote is not None else {}
    config = getattr(getattr(contexto, "pacote_config", None), "conteudo", {}) or {}
    nome_cfg = ((config.get("abas") or {}).get("switching") if isinstance(config, dict) else None) or "Switching"
    for nome in [nome_cfg, "Switching", "Switiching", "Swtiching"]:
        for quadros in [canonicos, brutos]:
            if isinstance(quadros, dict) and isinstance(quadros.get(nome), pd.DataFrame):
                return nome, quadros[nome].copy()
    return "", pd.DataFrame()


def _switchings_aba(contexto: Any) -> FonteSwitching:
    try:
        nome, df = _quadro_aba_switching(contexto)
        origem = f"planilha.aba_switching[{nome or 'nao_encontrada'}]"
        return FonteSwitching(origem, _canon(_df_records(df), origem))
    except Exception as e:
        return FonteSwitching("planilha.aba_switching", [], f"{e.__class__.__name__}: {e}")


def _mapa_central(contexto: Any) -> dict[str, dict[str, Any]]:
    pacote = getattr(contexto, "recomputacao_sequencial_central_v1", None)
    quadro = getattr(pacote, "quadro_recomputacao_sequencial_central", None) if pacote is not None else None
    if not isinstance(quadro, pd.DataFrame) or quadro.empty:
        return {}
    mapa = {}
    for _, row in quadro.iterrows():
        pid = _txt(row.get("pagamento_id"))
        if pid:
            mapa[pid] = row.to_dict()
    return mapa


def _evento_switching_explicito(e: dict[str, Any]) -> bool:
    return bool(_txt(_pick(e, ["evento_switching_id"]))) or _norm(_pick(e, ["tipo_evento", "evento", "tipo"])) == "switching"


def _eventos_switching_ledger(resultado: Any) -> tuple[list[dict[str, Any]], int, int]:
    bruto = []
    if isinstance(resultado, dict):
        bruto = resultado.get("eventos") or resultado.get("ledger") or []
    elif isinstance(resultado, list):
        bruto = resultado
    if isinstance(bruto, pd.DataFrame):
        bruto = bruto.to_dict(orient="records")
    if not isinstance(bruto, list):
        return [], 0, 0
    validos = [dict(e) for e in bruto if isinstance(e, dict) and _evento_switching_explicito(e)]
    return validos, len(bruto), len(bruto) - len(validos)


def _switchings_ledger(contexto: Any) -> FonteSwitching:
    motor = getattr(contexto, "motor_recomendacao_pagamentos_switching_v1", None)
    quadro = getattr(motor, "quadro_recomendacoes", None) if motor is not None else None
    detalhes = {
        "usa_saida_extrato_futuro_renderizado": False,
        "tentativas_ledger": [],
        "eventos_ledger_brutos": 0,
        "eventos_ledger_descartados_por_nao_switching_explicito": 0,
        "eventos_switching_materializados_v17_f0_o2": 0,
    }
    erros = []
    eventos: list[dict[str, Any]] = []
    if isinstance(quadro, pd.DataFrame) and not quadro.empty:
        detalhes["tentativas_ledger"].append("motor_recomendacao_pagamentos_switching_v1.quadro_recomendacoes")
        try:
            resultado = construir_ledger_temporal_conjunto(quadro.copy(), _mapa_central(contexto), contexto)
            eventos_ledger, total, descartados = _eventos_switching_ledger(resultado)
            detalhes["eventos_ledger_brutos"] = total
            detalhes["eventos_ledger_descartados_por_nao_switching_explicito"] = descartados
            for evento in eventos_ledger:
                evento["_origem_tentativa_ledger"] = detalhes["tentativas_ledger"][0]
            eventos.extend(eventos_ledger)
        except Exception as e:
            erros.append(f"motor_recomendacao_pagamentos_switching_v1.quadro_recomendacoes: {e.__class__.__name__}: {e}")
    else:
        erros.append("nenhum_quadro_interno_do_motor_disponivel_para_construir_ledger_temporal_conjunto")

    try:
        eventos_materializados = materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2(contexto)
        detalhes["eventos_switching_materializados_v17_f0_o2"] = len(eventos_materializados)
        detalhes["tentativas_ledger"].append("ledger_switching_estado_temporal_v17_f0_o2")
        eventos.extend(eventos_materializados)
    except Exception as e:
        erros.append(f"ledger_switching_estado_temporal_v17_f0_o2: {e.__class__.__name__}: {e}")

    vistos = set()
    unicos = []
    for evento in eventos:
        regs = _canon([evento], "ledger_temporal_conjunto.eventos_switching_explicitos")
        if not regs:
            continue
        chave = regs[0]["chave_equivalencia"]
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(evento)
    return FonteSwitching("ledger_temporal_conjunto.eventos_switching_explicitos", _canon(unicos, "ledger_temporal_conjunto.eventos_switching_explicitos"), " | ".join(erros), detalhes)


def _comparar(origens: dict[str, FonteSwitching]) -> list[dict[str, Any]]:
    linhas: dict[str, dict[str, Any]] = {}
    for fonte, obj in origens.items():
        for r in obj.registros:
            chave = r["chave_equivalencia"]
            linha = linhas.setdefault(chave, {
                "tipo_linha": "comparacao",
                "chave_equivalencia": chave,
                "data": r["data"],
                "lote_origem": r["lote_origem"],
                "lote_destino": r["lote_destino"],
                "produto_destino": r["produto_destino"],
                "valor_liquido": r["valor_liquido"],
                "em_ponte": "nao", "em_pre_saida": "nao", "em_ledger": "nao", "em_aba": "nao",
                "json_ponte": "", "json_pre_saida": "", "json_ledger": "", "json_aba": "",
            })
            linha[f"em_{fonte}"] = "sim"
            linha[f"json_{fonte}"] = r["registro_json"]
    saida = list(linhas.values())
    for l in saida:
        divs = []
        if l["em_ponte"] == "sim" and l["em_ledger"] != "sim":
            divs.append("ponte_sem_equivalente_ledger")
        if l["em_ledger"] == "sim" and l["em_ponte"] != "sim":
            divs.append("ledger_sem_equivalente_ponte")
        if l["em_ponte"] == "sim" and l["em_aba"] != "sim":
            divs.append("ponte_sem_equivalente_aba")
        if l["em_ponte"] == "sim" and l["em_pre_saida"] != "sim":
            divs.append("ponte_sem_equivalente_pre_saida")
        l["divergencias"] = ";".join(divs) if divs else "n/d"
    return sorted(saida, key=lambda x: (x["data"], x["lote_origem"], x["produto_destino"], x["valor_liquido"]))


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
        "ledger": _switchings_ledger(contexto),
        "aba": _switchings_aba(contexto),
    }
    chaves_ponte = {r["chave_equivalencia"] for r in origens["ponte"].registros}
    chaves_ledger = {r["chave_equivalencia"] for r in origens["ledger"].registros}
    equivalente = bool(chaves_ponte) and chaves_ponte == chaves_ledger
    detalhes = origens["ledger"].detalhes or {}
    resumo = [{
        "tipo_linha": "resumo",
        "fonte": "veredito",
        "ponte_equivale_ledger": "sim" if equivalente else "nao",
        "switchings_ponte": len(origens["ponte"].registros),
        "switchings_pre_saida": len(origens["pre_saida"].registros),
        "switchings_ledger": len(origens["ledger"].registros),
        "switchings_aba": len(origens["aba"].registros),
        "usa_saida_extrato_futuro_renderizado": detalhes.get("usa_saida_extrato_futuro_renderizado", False),
        "eventos_ledger_brutos": detalhes.get("eventos_ledger_brutos", 0),
        "eventos_ledger_descartados_por_nao_switching_explicito": detalhes.get("eventos_ledger_descartados_por_nao_switching_explicito", 0),
        "eventos_switching_materializados_v17_f0_o2": detalhes.get("eventos_switching_materializados_v17_f0_o2", 0),
        "tentativas_ledger": json.dumps(detalhes.get("tentativas_ledger", []), ensure_ascii=False),
        "erro_ledger": origens["ledger"].erro,
    }]
    comparacao = _comparar(origens)
    ARQUIVO_COMPARACAO.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(resumo + comparacao).to_csv(ARQUIVO_COMPARACAO, index=False)

    print("=== GATE V17-F0-O.2 — EQUIVALÊNCIA SWITCHING PONTE VS LEDGER ===")
    print(f"versao_baseline={VERSAO_BASELINE}")
    print(f"ponte_equivale_ledger={'sim' if equivalente else 'nao'}")
    print(f"switchings_ponte={len(origens['ponte'].registros)}")
    print(f"switchings_pre_saida={len(origens['pre_saida'].registros)}")
    print(f"switchings_ledger={len(origens['ledger'].registros)}")
    print(f"switchings_aba={len(origens['aba'].registros)}")
    print(f"usa_saida_extrato_futuro_renderizado={detalhes.get('usa_saida_extrato_futuro_renderizado', False)}")
    print(f"eventos_ledger_brutos={detalhes.get('eventos_ledger_brutos', 0)}")
    print(f"eventos_ledger_descartados_por_nao_switching_explicito={detalhes.get('eventos_ledger_descartados_por_nao_switching_explicito', 0)}")
    print(f"eventos_switching_materializados_v17_f0_o2={detalhes.get('eventos_switching_materializados_v17_f0_o2', 0)}")
    if origens["ledger"].erro:
        print(f"erro_ledger={origens['ledger'].erro}")
    print(f"csv={ARQUIVO_COMPARACAO}")
    if comparacao:
        cols = ["data", "lote_origem", "lote_destino", "produto_destino", "valor_liquido", "em_ponte", "em_pre_saida", "em_ledger", "em_aba", "divergencias"]
        print("\n=== AMOSTRA COMPARATIVA ===")
        print(pd.DataFrame(comparacao)[cols].to_string(index=False))
    if equivalente:
        print("\nrecomendacao=ponte_pode_ser_removida_em_microetapa_posterior_apenas_com_gate_de_regressao")
    else:
        print("\nrecomendacao=manter_ponte_e_migrar_materializacao_dos_switchings_para_ledger_estado_temporal_em_microetapa_posterior")


if __name__ == "__main__":
    main()
