from __future__ import annotations

import json
import sys
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
from nucleo.saida_canonica import construir_saida_canonica

ARQUIVO_DIAGNOSTICO = RAIZ_REPOSITORIO / "saidas" / "diagnostico" / "gate_remocao_ponte_v17_f0_p0.csv"


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
    mapa = {_norm(k): k for k in d}
    for nome in nomes:
        chave = mapa.get(_norm(nome))
        if chave is not None and _txt(d.get(chave)):
            return d.get(chave)
    return ""


def _num(v: Any) -> float:
    texto = _txt(v)
    if not texto:
        return 0.0
    try:
        return round(float(v), 2)
    except Exception:
        pass
    limpo = texto.replace("R$", "").strip()
    if "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    return round(float(limpo), 2)


def _data(v: Any) -> str:
    if not _txt(v):
        return ""
    for dayfirst in (False, True):
        try:
            dt = pd.to_datetime(v, errors="raise", dayfirst=dayfirst)
            if not pd.isna(dt):
                return dt.date().isoformat()
        except Exception:
            pass
    return _txt(v)[:10]


def _canon_switching(registros: list[dict[str, Any]]) -> list[dict[str, Any]]:
    saida = []
    for r in registros:
        data = _data(_pick(r, ["Data", "data_switching", "Data sugerida", "data_aplicacao"]))
        lote_origem = _txt(_pick(r, ["Lote origem", "lote_origem", "lote_id_origem", "lote_id_antes"]))
        lote_destino = _txt(_pick(r, ["Lote destino", "lote_destino", "lote_id_destino", "lote_id_depois", "lote_pos_switching"]))
        produto_destino = _txt(_pick(r, ["Produto destino switching", "produto_destino", "produto_destino_nome", "Investimento"]))
        valor_liquido = _num(_pick(r, ["Valor líquido origem", "valor_liquido_origem", "Valor líquido total", "valor_liquido_migrado"]))
        chave = (data, lote_origem, lote_destino, produto_destino, f"{valor_liquido:.2f}")
        saida.append({
            "data": data,
            "lote_origem": lote_origem,
            "lote_destino": lote_destino,
            "produto_destino": produto_destino,
            "valor_liquido": f"{valor_liquido:.2f}",
            "chave": "|".join(chave),
            "registro_json": json.dumps(r, ensure_ascii=False, default=str, sort_keys=True),
        })
    return sorted(saida, key=lambda x: (x["data"], x["lote_origem"], x["lote_destino"], x["produto_destino"], x["valor_liquido"]))


def _valor_metrica(lista_metricas: Any, chaves: list[str]) -> float:
    if not isinstance(lista_metricas, list):
        return 0.0
    alvo = [_norm(c) for c in chaves]
    for item in lista_metricas:
        if not isinstance(item, dict):
            continue
        metrica = _norm(item.get("Métrica", ""))
        if any(ch in metrica for ch in alvo):
            return _num(item.get("Valor", ""))
    return 0.0


def _metricas_invariantes(saida: Any, qtd_eventos_ledger: int) -> dict[str, Any]:
    return {
        "valor_liquido_migrado_destinos_pos_switching": _valor_metrica(saida.fechamento_atual, ["valor líquido migrado para destinos pós-switching"]),
        "patrimonio_liquido_atual": _valor_metrica(saida.fechamento_atual, ["patrimônio líquido atual"]),
        "patrimonio_liquido_reconciliado_origens_migradas": _valor_metrica(saida.fechamento_atual, ["patrimônio líquido reconciliado com origens migradas"]),
        "rendimento_liquido_atual": _valor_metrica(saida.resumo_recebidos, ["rendimento líquido atual"]),
        "rendimento_liquido_reconciliado_contra_recebidos": _valor_metrica(saida.resumo_recebidos, ["rendimento líquido reconciliado contra recebidos"]),
        "qtd_extrato_futuro": len(getattr(saida, "extrato_futuro", []) or []),
        "qtd_eventos_ledger": qtd_eventos_ledger,
    }


def main() -> None:
    contexto = carregar_contexto_baseline(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    saida_com_ponte = construir_saida_canonica_com_switching_v17_c7(contexto, versao=VERSAO_BASELINE)
    saida_sem_ponte = construir_saida_canonica(contexto, versao=VERSAO_BASELINE)
    eventos_ledger = materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2(contexto)

    switchings_com_ponte = _canon_switching(list(getattr(saida_com_ponte, "switchings", []) or []))
    switchings_sem_ponte_simulada = _canon_switching([dict(e) for e in eventos_ledger if isinstance(e, dict)])

    mapa_com_ponte = {r["chave"]: r for r in switchings_com_ponte}
    mapa_sem_ponte = {r["chave"]: r for r in switchings_sem_ponte_simulada}
    chaves = sorted(set(mapa_com_ponte) | set(mapa_sem_ponte))

    divergencias = []
    for chave in chaves:
        em_com = chave in mapa_com_ponte
        em_sem = chave in mapa_sem_ponte
        if em_com and em_sem:
            continue
        base = mapa_com_ponte.get(chave) or mapa_sem_ponte.get(chave) or {}
        divergencias.append({
            "tipo_linha": "divergencia_switching",
            "data": base.get("data", ""),
            "lote_origem": base.get("lote_origem", ""),
            "lote_destino": base.get("lote_destino", ""),
            "produto_destino": base.get("produto_destino", ""),
            "valor_liquido": base.get("valor_liquido", ""),
            "em_saida_oficial_com_ponte": "sim" if em_com else "nao",
            "em_saida_base_sem_ponte_simulada": "sim" if em_sem else "nao",
            "json_com_ponte": mapa_com_ponte.get(chave, {}).get("registro_json", ""),
            "json_sem_ponte": mapa_sem_ponte.get(chave, {}).get("registro_json", ""),
        })

    metricas_com_ponte = _metricas_invariantes(saida_com_ponte, len(eventos_ledger))
    metricas_sem_ponte = _metricas_invariantes(saida_sem_ponte, len(eventos_ledger))
    divergencias_metricas = []
    for metrica, valor_com in metricas_com_ponte.items():
        valor_sem = metricas_sem_ponte.get(metrica)
        if valor_com != valor_sem:
            divergencias_metricas.append({"metrica": metrica, "valor_com_ponte": valor_com, "valor_sem_ponte": valor_sem})

    resumo = {
        "tipo_linha": "resumo",
        "ponte_removivel": "sim" if (not divergencias and not divergencias_metricas) else "nao",
        "switchings_com_ponte": len(switchings_com_ponte),
        "switchings_sem_ponte_simulada": len(switchings_sem_ponte_simulada),
        "divergencias_switching": len(divergencias),
        "divergencias_metricas": len(divergencias_metricas),
        **metricas_com_ponte,
    }

    linhas_metricas = [{"tipo_linha": "divergencia_metrica", **d} for d in divergencias_metricas]
    ARQUIVO_DIAGNOSTICO.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([resumo] + divergencias + linhas_metricas).to_csv(ARQUIVO_DIAGNOSTICO, index=False)

    print("=== GATE V17-F0-P.0 — REMOCAO PREVENTIVA DA PONTE V17-C7 ===")
    print(f"versao_baseline={VERSAO_BASELINE}")
    print(f"ponte_removivel={resumo['ponte_removivel']}")
    print(f"switchings_com_ponte={resumo['switchings_com_ponte']}")
    print(f"switchings_sem_ponte_simulada={resumo['switchings_sem_ponte_simulada']}")
    print(f"divergencias_switching={resumo['divergencias_switching']}")
    print(f"divergencias_metricas={resumo['divergencias_metricas']}")
    print(f"qtd_eventos_ledger={resumo['qtd_eventos_ledger']}")
    print(f"qtd_extrato_futuro={resumo['qtd_extrato_futuro']}")
    print(f"csv={ARQUIVO_DIAGNOSTICO}")


if __name__ == "__main__":
    main()
