from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

try:
    import pandas as pd
except Exception:  # pragma: no cover - import defensivo
    pd = None  # type: ignore[assignment]


@dataclass(frozen=True)
class ResultadoDetalhamentoDivergenciasComponentes:
    """Resultado diagnóstico granular de divergências internas entre contextos.

    Este artefato é isolado. Ele não altera runtime, não constrói saída canônica,
    não executa motor, não reexecuta replay e não promove contexto compatível.
    """

    ok: bool
    componentes: dict[str, Any]
    divergencias: list[dict[str, Any]]
    metadados: dict[str, Any]


def _normalizar(valor: Any) -> Any:
    if isinstance(valor, Decimal):
        return str(valor)
    if hasattr(valor, "isoformat"):
        try:
            return valor.isoformat()
        except Exception:
            return str(valor)
    if isinstance(valor, dict):
        return {str(k): _normalizar(v) for k, v in sorted(valor.items(), key=lambda item: str(item[0]))}
    if isinstance(valor, (list, tuple)):
        return [_normalizar(v) for v in valor]
    if isinstance(valor, set):
        return sorted(_normalizar(v) for v in valor)
    return valor


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


def _valores_iguais(a: Any, b: Any) -> bool:
    return _normalizar(a) == _normalizar(b)


def _detalhar_dicts(base: Any, canonico: Any, *, limite: int = 40) -> dict[str, Any]:
    base_dict = dict(base or {}) if isinstance(base, dict) else {}
    canonico_dict = dict(canonico or {}) if isinstance(canonico, dict) else {}
    chaves_base = {str(k) for k in base_dict}
    chaves_canonico = {str(k) for k in canonico_dict}

    ausentes_no_canonico = sorted(chaves_base - chaves_canonico)
    ausentes_no_baseline = sorted(chaves_canonico - chaves_base)
    divergentes = []

    canonico_por_str = {str(k): v for k, v in canonico_dict.items()}
    base_por_str = {str(k): v for k, v in base_dict.items()}

    for chave in sorted(chaves_base & chaves_canonico):
        valor_base = base_por_str[chave]
        valor_canonico = canonico_por_str[chave]
        if not _valores_iguais(valor_base, valor_canonico):
            divergentes.append(
                {
                    "chave": chave,
                    "baseline": _normalizar(valor_base),
                    "canonico": _normalizar(valor_canonico),
                }
            )
        if len(divergentes) >= limite:
            break

    return {
        "qtd_baseline": len(base_dict),
        "qtd_canonico": len(canonico_dict),
        "qtd_ausentes_no_canonico": len(ausentes_no_canonico),
        "qtd_ausentes_no_baseline": len(ausentes_no_baseline),
        "qtd_valores_divergentes_amostrados": len(divergentes),
        "ausentes_no_canonico_amostra": ausentes_no_canonico[:limite],
        "ausentes_no_baseline_amostra": ausentes_no_baseline[:limite],
        "valores_divergentes_amostra": divergentes,
    }


def _chave_dataframe(linha: dict[str, Any], indice: int) -> str:
    candidatos = [
        "id",
        "pagamento_id",
        "despesa_id",
        "lote_id",
        "Lote",
        "Lote usado",
        "Data",
        "data",
        "Descrição",
        "descricao",
        "Valor",
        "valor",
    ]
    partes = []
    for nome in candidatos:
        if nome in linha and linha.get(nome) not in (None, ""):
            partes.append(str(linha.get(nome)))
    return "|".join(partes[:6]) or f"linha_{indice}"


def _registros_dataframe(df: Any) -> list[dict[str, Any]]:
    if pd is None or not isinstance(df, pd.DataFrame):
        return []
    return [_normalizar(x) for x in df.to_dict(orient="records")]


def _indexar_registros(registros: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    saida: dict[str, dict[str, Any]] = {}
    contagens: dict[str, int] = {}
    for i, registro in enumerate(registros):
        chave_base = _chave_dataframe(registro, i)
        ocorrencia = contagens.get(chave_base, 0) + 1
        contagens[chave_base] = ocorrencia
        chave = chave_base if ocorrencia == 1 else f"{chave_base}#{ocorrencia}"
        saida[chave] = registro
    return saida


def _detalhar_dataframes(base: Any, canonico: Any, *, limite_linhas: int = 30, limite_campos: int = 20) -> dict[str, Any]:
    registros_base = _registros_dataframe(base)
    registros_canonico = _registros_dataframe(canonico)
    idx_base = _indexar_registros(registros_base)
    idx_canonico = _indexar_registros(registros_canonico)
    chaves = sorted(set(idx_base) | set(idx_canonico))
    divergencias = []

    for chave in chaves:
        linha_base = idx_base.get(chave)
        linha_canonico = idx_canonico.get(chave)
        if linha_base is None:
            divergencias.append({"chave": chave, "status": "ausente_no_baseline"})
        elif linha_canonico is None:
            divergencias.append({"chave": chave, "status": "ausente_no_canonico"})
        else:
            campos = []
            for campo in sorted(set(linha_base) | set(linha_canonico), key=str):
                valor_base = linha_base.get(campo)
                valor_canonico = linha_canonico.get(campo)
                if not _valores_iguais(valor_base, valor_canonico):
                    campos.append(
                        {
                            "campo": str(campo),
                            "baseline": valor_base,
                            "canonico": valor_canonico,
                        }
                    )
            if campos:
                divergencias.append(
                    {
                        "chave": chave,
                        "status": "campos_divergentes",
                        "qtd_campos_divergentes": len(campos),
                        "campos": campos[:limite_campos],
                    }
                )
        if len(divergencias) >= limite_linhas:
            break

    colunas_base = list(base.columns) if pd is not None and isinstance(base, pd.DataFrame) else []
    colunas_canonico = list(canonico.columns) if pd is not None and isinstance(canonico, pd.DataFrame) else []
    return {
        "linhas_baseline": len(registros_base),
        "linhas_canonico": len(registros_canonico),
        "colunas_baseline": [str(x) for x in colunas_base],
        "colunas_canonico": [str(x) for x in colunas_canonico],
        "colunas_apenas_baseline": sorted(str(x) for x in set(colunas_base) - set(colunas_canonico)),
        "colunas_apenas_canonico": sorted(str(x) for x in set(colunas_canonico) - set(colunas_base)),
        "qtd_divergencias_amostradas": len(divergencias),
        "divergencias_amostra": divergencias,
    }


def _lote_para_dict(lote: Any) -> dict[str, Any]:
    campos = {}
    for nome in sorted(dir(lote)):
        if nome.startswith("_"):
            continue
        try:
            valor = getattr(lote, nome)
        except Exception:
            continue
        if callable(valor):
            continue
        if isinstance(valor, (str, int, float, bool, type(None), Decimal)) or hasattr(valor, "isoformat"):
            campos[nome] = _normalizar(valor)
    return campos


def _chave_lote(lote_dict: dict[str, Any], indice: int) -> str:
    for nome in ("id", "lote_id", "nome", "Lote", "descricao"):
        if lote_dict.get(nome) not in (None, ""):
            return str(lote_dict.get(nome))
    return f"lote_{indice}"


def _detalhar_lotes(base: Any, canonico: Any, *, limite_lotes: int = 30, limite_campos: int = 25) -> dict[str, Any]:
    lotes_base = [_lote_para_dict(x) for x in list(base or [])]
    lotes_canonico = [_lote_para_dict(x) for x in list(canonico or [])]
    idx_base = {_chave_lote(lote, i): lote for i, lote in enumerate(lotes_base)}
    idx_canonico = {_chave_lote(lote, i): lote for i, lote in enumerate(lotes_canonico)}
    divergencias = []

    for chave in sorted(set(idx_base) | set(idx_canonico)):
        lote_base = idx_base.get(chave)
        lote_canonico = idx_canonico.get(chave)
        if lote_base is None:
            divergencias.append({"lote": chave, "status": "ausente_no_baseline"})
        elif lote_canonico is None:
            divergencias.append({"lote": chave, "status": "ausente_no_canonico"})
        else:
            campos = []
            for campo in sorted(set(lote_base) | set(lote_canonico), key=str):
                valor_base = lote_base.get(campo)
                valor_canonico = lote_canonico.get(campo)
                if not _valores_iguais(valor_base, valor_canonico):
                    campos.append(
                        {
                            "campo": str(campo),
                            "baseline": valor_base,
                            "canonico": valor_canonico,
                        }
                    )
            if campos:
                divergencias.append(
                    {
                        "lote": chave,
                        "status": "campos_divergentes",
                        "qtd_campos_divergentes": len(campos),
                        "campos": campos[:limite_campos],
                    }
                )
        if len(divergencias) >= limite_lotes:
            break

    return {
        "qtd_lotes_baseline": len(lotes_base),
        "qtd_lotes_canonico": len(lotes_canonico),
        "ids_baseline_amostra": sorted(idx_base)[:20],
        "ids_canonico_amostra": sorted(idx_canonico)[:20],
        "qtd_divergencias_amostradas": len(divergencias),
        "divergencias_amostra": divergencias,
    }


def detalhar_divergencias_componentes_contextos(
    contexto_baseline: Any,
    contexto_operacional_canonico: Any,
) -> ResultadoDetalhamentoDivergenciasComponentes:
    """Detalha divergências internas detectadas pela ME-RUNTIME-CANON-10.

    A função compara apenas objetos já carregados. Ela não altera runtime, não
    constrói saída canônica, não executa motor e não reexecuta replay.
    """

    cache_base = _obter_caminho(contexto_baseline, "cache_cdi.serie_cdi")
    cache_canonico = _obter_caminho(contexto_operacional_canonico, "cache_cdi.serie_cdi")
    log_base = _obter_caminho(contexto_baseline, "replay_passado.log_passado")
    log_canonico = _obter_caminho(contexto_operacional_canonico, "replay_passado.log_passado")
    lotes_base = _obter_caminho(contexto_baseline, "replay_passado.lotes_apos_replay")
    lotes_canonico = _obter_caminho(contexto_operacional_canonico, "replay_passado.lotes_apos_replay")

    componentes = {
        "cache_cdi.serie_cdi": _detalhar_dicts(cache_base, cache_canonico),
        "replay_passado.log_passado": _detalhar_dataframes(log_base, log_canonico),
        "replay_passado.lotes_apos_replay": _detalhar_lotes(lotes_base, lotes_canonico),
    }

    divergencias = []
    for nome, detalhe in componentes.items():
        qtd = detalhe.get("qtd_divergencias_amostradas")
        if qtd is None:
            qtd = (
                int(detalhe.get("qtd_ausentes_no_canonico", 0))
                + int(detalhe.get("qtd_ausentes_no_baseline", 0))
                + int(detalhe.get("qtd_valores_divergentes_amostrados", 0))
            )
        if int(qtd or 0) > 0:
            divergencias.append({"componente": nome, "qtd_divergencias_amostradas": qtd})

    return ResultadoDetalhamentoDivergenciasComponentes(
        ok=not divergencias,
        componentes=componentes,
        divergencias=divergencias,
        metadados={
            "artefato": "ResultadoDetalhamentoDivergenciasComponentes",
            "microetapa": "ME-RUNTIME-CANON-11",
            "altera_runtime_principal": False,
            "altera_saida_canonica": False,
            "altera_motor": False,
            "altera_replay": False,
            "promove_contexto_compat": False,
            "substitui_contexto_baseline": False,
        },
    )


def imprimir_detalhamento_divergencias_componentes(
    resultado: ResultadoDetalhamentoDivergenciasComponentes,
) -> None:
    print("=== DETALHAMENTO DE DIVERGÊNCIAS INTERNAS — CONTEXTOS ===")
    print(f"ok={resultado.ok}")
    print(f"componentes={len(resultado.componentes)}")
    print(f"componentes_com_divergencia={len(resultado.divergencias)}")
    for nome, detalhe in resultado.componentes.items():
        print(f"--- {nome} ---")
        for chave, valor in detalhe.items():
            if chave.endswith("amostra"):
                print(f"{chave}: {len(valor or [])}")
            else:
                print(f"{chave}: {valor}")
        amostras = detalhe.get("divergencias_amostra") or detalhe.get("valores_divergentes_amostra") or []
        for item in list(amostras)[:5]:
            print(f"  {item}")
