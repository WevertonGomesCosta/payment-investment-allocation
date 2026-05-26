from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

try:
    import pandas as pd
except Exception:  # pragma: no cover - import defensivo
    pd = None  # type: ignore[assignment]


@dataclass(frozen=True)
class ResultadoComparacaoComponentesContextos:
    """Resultado diagnóstico da comparação interna entre contextos.

    Este artefato é isolado. Ele não altera runtime, não constrói saída canônica,
    não executa motor, não reexecuta replay e não promove contexto compatível.
    """

    ok: bool
    componentes: list[dict[str, Any]]
    divergencias: list[dict[str, Any]]
    metadados: dict[str, Any]


def _normalizar_json(valor: Any) -> Any:
    if isinstance(valor, dict):
        return {str(k): _normalizar_json(v) for k, v in sorted(valor.items(), key=lambda item: str(item[0]))}
    if isinstance(valor, (list, tuple)):
        return [_normalizar_json(v) for v in valor]
    if isinstance(valor, set):
        return sorted(_normalizar_json(v) for v in valor)
    if isinstance(valor, Decimal):
        return str(valor)
    if hasattr(valor, "isoformat"):
        try:
            return valor.isoformat()
        except Exception:
            return str(valor)
    return valor


def _hash_objeto(valor: Any) -> str:
    serializado = json.dumps(_normalizar_json(valor), ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def _resumir_dataframe(df: Any) -> dict[str, Any]:
    if pd is None or not isinstance(df, pd.DataFrame):
        return {"tipo": type(df).__name__, "eh_dataframe": False, "hash": _hash_objeto(df)}
    colunas = [str(c) for c in df.columns]
    registros = df.to_dict(orient="records")
    return {
        "tipo": "DataFrame",
        "eh_dataframe": True,
        "linhas": int(len(df)),
        "colunas": colunas,
        "hash": _hash_objeto(registros),
        "colunas_hash": _hash_objeto(colunas),
    }


def _resumir_lote(lote: Any) -> dict[str, Any]:
    campos = {}
    for nome in (
        "id",
        "data_recebimento",
        "data_aplicacao",
        "investimento",
        "valor_inicial",
        "principal_remanescente",
        "saldo_bruto",
        "esgotado",
    ):
        if hasattr(lote, nome):
            campos[nome] = getattr(lote, nome)
    return _normalizar_json(campos)


def _resumir_lotes(lotes: Any) -> dict[str, Any]:
    lista = list(lotes or [])
    registros = [_resumir_lote(lote) for lote in lista]
    registros.sort(key=lambda x: str(x.get("id") or ""))
    return {
        "tipo": "lotes_apos_replay",
        "qtd": len(registros),
        "hash": _hash_objeto(registros),
        "amostra_ids": [str(x.get("id") or "") for x in registros[:10]],
    }


def _resumir_objeto_publico(objeto: Any) -> dict[str, Any]:
    if objeto is None:
        return {"tipo": "None", "presente": False, "hash": _hash_objeto(None)}
    if pd is not None and isinstance(objeto, pd.DataFrame):
        return _resumir_dataframe(objeto)
    if isinstance(objeto, (str, int, float, bool, list, tuple, dict)):
        return {"tipo": type(objeto).__name__, "presente": True, "hash": _hash_objeto(objeto)}

    campos = {}
    for nome in sorted(dir(objeto)):
        if nome.startswith("_"):
            continue
        try:
            valor = getattr(objeto, nome)
        except Exception:
            continue
        if callable(valor):
            continue
        if pd is not None and isinstance(valor, pd.DataFrame):
            campos[nome] = _resumir_dataframe(valor)
        elif isinstance(valor, (str, int, float, bool, list, tuple, dict, type(None))):
            campos[nome] = _normalizar_json(valor)
        else:
            campos[nome] = {"tipo": type(valor).__name__, "repr": str(valor)[:300]}
    return {
        "tipo": type(objeto).__name__,
        "presente": True,
        "campos": campos,
        "hash": _hash_objeto(campos),
    }


def _obter_caminho(objeto: Any, caminho: str) -> Any:
    atual = objeto
    for parte in caminho.split("."):
        if atual is None:
            return None
        if hasattr(atual, parte):
            atual = getattr(atual, parte)
        elif isinstance(atual, dict):
            atual = atual.get(parte)
        else:
            return None
    return atual


def _resumir_componente(contexto: Any, caminho: str) -> dict[str, Any]:
    valor = _obter_caminho(contexto, caminho)
    if caminho.endswith("lotes_apos_replay"):
        return _resumir_lotes(valor)
    return _resumir_objeto_publico(valor)


def _comparar_resumos(nome: str, base: dict[str, Any], canonico: dict[str, Any]) -> dict[str, Any]:
    igual = base.get("hash") == canonico.get("hash")
    registro = {
        "componente": nome,
        "igual": bool(igual),
        "hash_baseline": base.get("hash"),
        "hash_canonico": canonico.get("hash"),
        "tipo_baseline": base.get("tipo"),
        "tipo_canonico": canonico.get("tipo"),
    }
    for chave in ("linhas", "qtd", "colunas", "amostra_ids"):
        if chave in base or chave in canonico:
            registro[f"{chave}_baseline"] = base.get(chave)
            registro[f"{chave}_canonico"] = canonico.get(chave)
    return registro


def comparar_componentes_contextos(
    contexto_baseline: Any,
    contexto_operacional_canonico: Any,
    *,
    componentes: list[str] | None = None,
) -> ResultadoComparacaoComponentesContextos:
    """Compara componentes internos antes da construção da saída canônica.

    A função apenas inspeciona objetos já carregados. Ela não altera runtime,
    não chama a saída canônica, não chama motor e não promove contexto compatível.
    """

    componentes = componentes or [
        "cache_cdi.serie_cdi",
        "calendario_financeiro",
        "replay_passado.log_passado",
        "replay_passado.lotes_apos_replay",
        "fontes_elegiveis_pagamento",
        "saldo_disponivel_geral",
        "decisao_local_v1",
        "recomputacao_sequencial_central_v1",
    ]

    linhas: list[dict[str, Any]] = []
    divergencias: list[dict[str, Any]] = []
    for nome in componentes:
        resumo_base = _resumir_componente(contexto_baseline, nome)
        resumo_canonico = _resumir_componente(contexto_operacional_canonico, nome)
        linha = _comparar_resumos(nome, resumo_base, resumo_canonico)
        linhas.append(linha)
        if not linha["igual"]:
            divergencias.append(linha)

    return ResultadoComparacaoComponentesContextos(
        ok=not divergencias,
        componentes=linhas,
        divergencias=divergencias,
        metadados={
            "artefato": "ResultadoComparacaoComponentesContextos",
            "microetapa": "ME-RUNTIME-CANON-10",
            "altera_runtime_principal": False,
            "altera_saida_canonica": False,
            "altera_motor": False,
            "altera_replay": False,
            "promove_contexto_compat": False,
            "substitui_contexto_baseline": False,
        },
    )


def imprimir_resumo_comparacao_componentes(resultado: ResultadoComparacaoComponentesContextos) -> None:
    print("=== COMPARAÇÃO DE COMPONENTES INTERNOS — CONTEXTOS ===")
    print(f"ok={resultado.ok}")
    print(f"divergencias={len(resultado.divergencias)}")
    for item in resultado.componentes:
        print(
            f"{item['componente']}: igual={item['igual']} | "
            f"tipo_base={item.get('tipo_baseline')} | tipo_can={item.get('tipo_canonico')}"
        )
        for chave in ("linhas", "qtd"):
            kb = f"{chave}_baseline"
            kc = f"{chave}_canonico"
            if kb in item or kc in item:
                print(f"  {chave}: baseline={item.get(kb)} | canonico={item.get(kc)}")
