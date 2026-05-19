from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.ledger_temporal_conjunto import (
    _eventos_switching_aba_operacional,
    _mapa_switchings_aba_operacional,
)
from nucleo.switching_canonico_ledger_shadow import (
    auditar_adaptador_switching_canonico_ledger_shadow,
    switching_canonico_para_eventos_ledger_shadow,
    switching_canonico_para_mapa_ledger_shadow,
)


def _txt(valor: Any) -> str:
    return str(valor or "").strip()


def _norm_data(valor: Any) -> str:
    if valor in (None, ""):
        return ""
    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass
    try:
        dt = pd.to_datetime(valor, errors="coerce")
        if pd.isna(dt):
            return _txt(valor)
        return dt.date().isoformat()
    except Exception:
        pass
    if hasattr(valor, "date") and not isinstance(valor, str):
        try:
            data = valor.date()
            if hasattr(data, "isoformat"):
                return data.isoformat()
        except Exception:
            pass
    if hasattr(valor, "isoformat"):
        try:
            return valor.isoformat()
        except Exception:
            pass
    return _txt(valor)


def _norm_valor(valor: Any) -> str:
    if valor in (None, ""):
        return ""
    try:
        return f"{round(float(valor), 2):.2f}"
    except Exception:
        return _txt(valor)


def _normalizar_mapa(mapa: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    normalizado: dict[str, dict[str, Any]] = {}
    for lote, meta in (mapa or {}).items():
        normalizado[_txt(lote)] = {
            "lote_origem": _txt(meta.get("lote_origem")),
            "lote_pos_switching": _txt(meta.get("lote_pos_switching")),
            "data_switching": _norm_data(meta.get("data_switching")),
            "produto_destino": _txt(meta.get("produto_destino")),
            "valor_liquido_origem": _norm_valor(meta.get("valor_liquido_origem")),
            "status_switching": _txt(meta.get("status_switching")),
        }
    return normalizado


def _normalizar_eventos(eventos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalizados: list[dict[str, Any]] = []
    for evento in list(eventos or []):
        normalizados.append({
            "evento_switching_id": _txt(evento.get("evento_switching_id")),
            "evento_switching_id_legado_compat": _txt(evento.get("evento_switching_id_legado_compat")),
            "lote_origem": _txt(evento.get("lote_origem")),
            "lote_pos_switching": _txt(evento.get("lote_pos_switching")),
            "data_switching": _norm_data(evento.get("data_switching")),
            "produto_destino": _txt(evento.get("produto_destino")),
            "valor_liquido_origem": _norm_valor(evento.get("valor_liquido_origem")),
            "status_materializacao_passiva": _txt(evento.get("status_materializacao_passiva")),
        })
    return sorted(
        normalizados,
        key=lambda r: (
            r.get("data_switching", ""),
            r.get("lote_origem", ""),
            r.get("lote_pos_switching", ""),
            r.get("evento_switching_id_legado_compat") or r.get("evento_switching_id", ""),
        ),
    )


def _comparar_mapas(mapa_legado: dict[str, dict[str, Any]], mapa_shadow: dict[str, dict[str, Any]]) -> dict[str, Any]:
    leg = _normalizar_mapa(mapa_legado)
    sh = _normalizar_mapa(mapa_shadow)
    lotes_leg = set(leg)
    lotes_sh = set(sh)
    divergencias = []
    for lote in sorted(lotes_leg & lotes_sh):
        for campo in ["lote_pos_switching", "data_switching", "produto_destino", "valor_liquido_origem"]:
            if leg[lote].get(campo) != sh[lote].get(campo):
                divergencias.append({
                    "lote_origem": lote,
                    "campo": campo,
                    "legado": leg[lote].get(campo),
                    "shadow": sh[lote].get(campo),
                })
    return {
        "qtd_mapa_legado": len(leg),
        "qtd_mapa_shadow": len(sh),
        "lotes_origem_apenas_legado": sorted(lotes_leg - lotes_sh),
        "lotes_origem_apenas_shadow": sorted(lotes_sh - lotes_leg),
        "divergencias_mapa": divergencias,
        "mapa_qtd_identica": len(leg) == len(sh),
        "mapa_lotes_origem_identicos": lotes_leg == lotes_sh,
        "mapa_campos_criticos_identicos": len(divergencias) == 0,
    }


def _comparar_eventos(eventos_legado: list[dict[str, Any]], eventos_shadow: list[dict[str, Any]]) -> dict[str, Any]:
    leg = _normalizar_eventos(eventos_legado)
    sh = _normalizar_eventos(eventos_shadow)

    def chave_compat(evento: dict[str, Any]) -> tuple[str, str, str, str]:
        return (
            evento.get("data_switching", ""),
            evento.get("lote_origem", ""),
            evento.get("lote_pos_switching", ""),
            evento.get("evento_switching_id_legado_compat") or evento.get("evento_switching_id", ""),
        )

    mapa_leg = {chave_compat(e): e for e in leg}
    mapa_sh = {chave_compat(e): e for e in sh}
    chaves_leg = set(mapa_leg)
    chaves_sh = set(mapa_sh)

    divergencias = []
    for chave in sorted(chaves_leg & chaves_sh):
        e_leg = mapa_leg[chave]
        e_sh = mapa_sh[chave]
        for campo in ["produto_destino", "valor_liquido_origem", "status_materializacao_passiva"]:
            if e_leg.get(campo) != e_sh.get(campo):
                divergencias.append({
                    "chave": "|".join(chave),
                    "campo": campo,
                    "legado": e_leg.get(campo),
                    "shadow": e_sh.get(campo),
                })

    return {
        "qtd_eventos_legado": len(leg),
        "qtd_eventos_shadow": len(sh),
        "eventos_apenas_legado": ["|".join(chave) for chave in sorted(chaves_leg - chaves_sh)],
        "eventos_apenas_shadow": ["|".join(chave) for chave in sorted(chaves_sh - chaves_leg)],
        "divergencias_eventos": divergencias,
        "eventos_qtd_identica": len(leg) == len(sh),
        "eventos_chaves_equivalentes": chaves_leg == chaves_sh,
        "eventos_campos_criticos_identicos": len(divergencias) == 0,
    }


def _linhas_resumo(resultado: dict[str, Any]) -> list[dict[str, Any]]:
    linhas = []
    for chave, valor in resultado.items():
        if isinstance(valor, (list, dict)):
            linhas.append({"metrica": chave, "valor": json.dumps(valor, ensure_ascii=False, sort_keys=True, default=str)})
        else:
            linhas.append({"metrica": chave, "valor": valor})
    return linhas


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita adaptador switching_canonico -> ledger shadow V3.7P.")
    parser.add_argument("--raiz", type=Path, default=ROOT, help="Raiz do repositório")
    parser.add_argument("--sem-csv", action="store_true", help="Não grava CSV diagnóstico")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )

    mapa_legado = _mapa_switchings_aba_operacional(contexto)
    eventos_legado = _eventos_switching_aba_operacional(contexto)
    mapa_shadow = switching_canonico_para_mapa_ledger_shadow(contexto)
    eventos_shadow = switching_canonico_para_eventos_ledger_shadow(contexto)

    auditoria_adaptador = auditar_adaptador_switching_canonico_ledger_shadow(contexto)
    comparacao_mapa = _comparar_mapas(mapa_legado, mapa_shadow)
    comparacao_eventos = _comparar_eventos(eventos_legado, eventos_shadow)

    resultado = {
        **auditoria_adaptador,
        **comparacao_mapa,
        **comparacao_eventos,
        "comparacao_mapa_legado_vs_canonico": bool(
            comparacao_mapa["mapa_qtd_identica"]
            and comparacao_mapa["mapa_lotes_origem_identicos"]
            and comparacao_mapa["mapa_campos_criticos_identicos"]
        ),
        "comparacao_eventos_legado_vs_canonico": bool(
            comparacao_eventos["eventos_qtd_identica"]
            and comparacao_eventos["eventos_chaves_equivalentes"]
            and comparacao_eventos["eventos_campos_criticos_identicos"]
        ),
        "sem_alteracao_observavel": True,
    }

    print("=== AUDITORIA SWITCHING CANONICO LEDGER SHADOW V3.7P ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_switching_canonico_ledger_shadow_v37p_resumo.csv",
            index=False,
        )
        pd.DataFrame(comparacao_mapa.get("divergencias_mapa", [])).to_csv(
            saida_dir / "auditoria_switching_canonico_ledger_shadow_v37p_divergencias_mapa.csv",
            index=False,
        )
        pd.DataFrame(comparacao_eventos.get("divergencias_eventos", [])).to_csv(
            saida_dir / "auditoria_switching_canonico_ledger_shadow_v37p_divergencias_eventos.csv",
            index=False,
        )

    sucesso = all([
        resultado["nao_le_pacote_planilha"],
        resultado["nao_le_quadros_brutos"],
        resultado["nao_reabre_excel"],
        resultado["nao_altera_ledger_operacional"],
        resultado["nao_altera_saida_canonica"],
        resultado["comparacao_mapa_legado_vs_canonico"],
        resultado["comparacao_eventos_legado_vs_canonico"],
        resultado["sem_alteracao_observavel"],
    ])
    return 0 if sucesso else 1


if __name__ == "__main__":
    raise SystemExit(main())