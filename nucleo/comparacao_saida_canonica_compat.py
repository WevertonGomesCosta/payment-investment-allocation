from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.contexto_saida_canonica_compat import (
    ComponentesTransicionaisSaidaCanonica,
    construir_contexto_saida_canonica_compat,
)
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.pacote_saida_observavel_temporal import construir_pacote_saida_observavel_temporal
from nucleo.saida_observavel import (
    construir_amostras_pagamentos_operacionais,
    construir_blocos_situacao_atual,
    construir_linhas_lotes_consolidados,
)


@dataclass(frozen=True)
class ResultadoComparacaoSaidaCanonicaCompat:
    """Resultado observável da comparação controlada de saída canônica."""

    ok: bool
    resumo_baseline: dict[str, Any]
    resumo_compat: dict[str, Any]
    divergencias: list[dict[str, Any]]
    metadados: dict[str, Any]


def _normalizar_json(valor: Any) -> Any:
    if isinstance(valor, dict):
        return {str(k): _normalizar_json(v) for k, v in sorted(valor.items(), key=lambda item: str(item[0]))}
    if isinstance(valor, (list, tuple)):
        return [_normalizar_json(v) for v in valor]
    if isinstance(valor, set):
        return sorted(_normalizar_json(v) for v in valor)
    if hasattr(valor, "isoformat"):
        try:
            return valor.isoformat()
        except Exception:
            return str(valor)
    if isinstance(valor, Decimal):
        return str(valor)
    return valor


def _hash_registros(registros: Any) -> str:
    serializado = json.dumps(_normalizar_json(registros or []), ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def _normalizar_texto_chave(valor: Any) -> str:
    texto = str(valor or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = texto.replace("—", " ").replace("–", " ").replace("-", " ")
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def _como_decimal(valor: Any) -> Decimal | None:
    if valor is None or valor == "":
        return None

    texto = str(valor).replace("R$", "").strip().replace(" ", "")
    if not texto:
        return None

    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")

    try:
        return Decimal(texto)
    except (InvalidOperation, ValueError):
        try:
            return Decimal(str(float(texto)))
        except Exception:
            return None


def _iter_dicts(objeto: Any):
    if isinstance(objeto, dict):
        yield objeto
        for valor in objeto.values():
            yield from _iter_dicts(valor)
    elif isinstance(objeto, (list, tuple)):
        for item in objeto:
            yield from _iter_dicts(item)


def _valor_preferencial_linha_metrica(linha: dict[str, Any], chave_metrica: str | None = None) -> Any:
    if chave_metrica and chave_metrica in linha:
        return linha.get(chave_metrica)

    for chave in ("Valor", "valor", "VALOR", "value", "Value"):
        if chave in linha:
            return linha.get(chave)

    for chave, valor in linha.items():
        chave_norm = _normalizar_texto_chave(chave)
        if chave_norm in {"valor", "valor r", "valor atual", "total"}:
            return valor

    for chave, valor in linha.items():
        if chave_metrica and chave == chave_metrica:
            continue
        if _como_decimal(valor) is not None:
            return valor

    return ""


def _valor_metrica(fechamento: Any, *aliases: str) -> str:
    aliases_norm = {_normalizar_texto_chave(alias) for alias in aliases if alias}
    if not aliases_norm:
        return ""

    for linha in _iter_dicts(fechamento or []):
        for chave, valor in linha.items():
            chave_norm = _normalizar_texto_chave(chave)
            valor_norm = _normalizar_texto_chave(valor)

            if chave_norm in aliases_norm:
                return str(_valor_preferencial_linha_metrica(linha, chave))

            if chave_norm in {"metrica", "métrica", "nome", "indicador"} and valor_norm in aliases_norm:
                return str(_valor_preferencial_linha_metrica(linha))

            if valor_norm in aliases_norm:
                return str(_valor_preferencial_linha_metrica(linha))

    return ""


def _valor_metrica_decimal(fechamento: Any, *aliases: str) -> str:
    valor = _como_decimal(_valor_metrica(fechamento, *aliases))
    if valor is None:
        return ""
    return str(valor.quantize(Decimal("0.01")))


def _ranking_top1(saida: Any) -> str:
    ranking = getattr(saida, "ranking_amostra", None) or []
    if not ranking:
        return ""
    primeira = ranking[0]
    return str(primeira.get("Produto") or primeira.get("produto") or "")


def _valor_campo(registro: dict[str, Any], *nomes: str) -> str:
    for nome in nomes:
        if nome in registro and registro.get(nome) not in (None, ""):
            return str(registro.get(nome))
    nomes_norm = {_normalizar_texto_chave(nome) for nome in nomes}
    for chave, valor in registro.items():
        if _normalizar_texto_chave(chave) in nomes_norm and valor not in (None, ""):
            return str(valor)
    return ""


def _chave_estavel_registro(tabela: str, registro: dict[str, Any], indice: int) -> str:
    if tabela in {"lotes_ativos", "lotes_exauridos"}:
        chave = "|".join(
            [
                _valor_campo(registro, "Lote", "Lote (ID)", "nome", "id"),
                _valor_campo(registro, "Status", "Status ciclo", "status_ciclo"),
                _valor_campo(registro, "Aplic.", "Aplicação", "Data Aplicação", "data_aplicacao"),
            ]
        ).strip("|")
    elif tabela == "extrato_passado":
        chave = "|".join(
            [
                _valor_campo(registro, "Data", "data"),
                _valor_campo(registro, "Conta", "Descrição", "Descricao", "descrição"),
                _valor_campo(registro, "Valor", "Líquido", "Liquido"),
                _valor_campo(registro, "Lotes usados", "Lote", "Lote usado"),
            ]
        ).strip("|")
    elif tabela == "extrato_futuro":
        chave = "|".join(
            [
                _valor_campo(registro, "Data", "data"),
                _valor_campo(registro, "Conta", "Descrição", "Descricao", "descrição"),
                _valor_campo(registro, "Valor", "Líquido", "Liquido"),
            ]
        ).strip("|")
    elif tabela == "switchings":
        chave = "|".join(
            [
                _valor_campo(registro, "Data", "data", "Data switching"),
                _valor_campo(registro, "Lote origem", "Lote (ID) Antes", "Origem"),
                _valor_campo(registro, "Destino", "Produto destino", "Investimento"),
            ]
        ).strip("|")
    elif tabela == "situacao_atual":
        chave = _valor_campo(registro, "titulo", "Título", "Titulo")
    else:
        chave = "|".join(str(v) for v in list(registro.values())[:3] if v not in (None, "")).strip("|")

    return chave or f"linha_{indice}"


def _indexar_registros(registros: list[dict[str, Any]], tabela: str) -> dict[str, dict[str, Any]]:
    indice: dict[str, dict[str, Any]] = {}
    contagens: dict[str, int] = {}
    for i, registro in enumerate(registros or []):
        chave_base = _chave_estavel_registro(tabela, registro, i)
        ocorrencia = contagens.get(chave_base, 0) + 1
        contagens[chave_base] = ocorrencia
        chave = chave_base if ocorrencia == 1 else f"{chave_base}#{ocorrencia}"
        indice[chave] = registro
    return indice


def _valores_iguais(a: Any, b: Any) -> bool:
    return _normalizar_json(a) == _normalizar_json(b)


def _detalhar_divergencias_registros(
    registros_baseline: list[dict[str, Any]],
    registros_compat: list[dict[str, Any]],
    *,
    tabela: str,
    limite_registros: int = 20,
    limite_campos: int = 12,
) -> list[dict[str, Any]]:
    idx_baseline = _indexar_registros(registros_baseline, tabela)
    idx_compat = _indexar_registros(registros_compat, tabela)
    chaves = sorted(set(idx_baseline) | set(idx_compat))
    detalhes: list[dict[str, Any]] = []

    for chave in chaves:
        linha_base = idx_baseline.get(chave)
        linha_compat = idx_compat.get(chave)

        if linha_base is None:
            detalhes.append({"chave": chave, "status": "ausente_no_baseline"})
        elif linha_compat is None:
            detalhes.append({"chave": chave, "status": "ausente_no_compat"})
        else:
            campos = sorted(set(linha_base) | set(linha_compat), key=str)
            campos_divergentes = []
            for campo in campos:
                valor_base = linha_base.get(campo)
                valor_compat = linha_compat.get(campo)
                if not _valores_iguais(valor_base, valor_compat):
                    campos_divergentes.append(
                        {
                            "campo": str(campo),
                            "baseline": valor_base,
                            "compat": valor_compat,
                        }
                    )
            if campos_divergentes:
                detalhes.append(
                    {
                        "chave": chave,
                        "status": "campos_divergentes",
                        "qtd_campos_divergentes": len(campos_divergentes),
                        "campos": campos_divergentes[:limite_campos],
                    }
                )

        if len(detalhes) >= limite_registros:
            break

    return detalhes


def _construir_pacote_observavel_temporal(contexto: Any, saida: Any) -> Any:
    """Replica a montagem observável usada pelo console, sem escrever saída oficial."""

    ativos_obs = construir_linhas_lotes_consolidados(
        contexto,
        saida,
        tipo="ativos",
        modo_bootstrap_pacote=True,
    )
    exauridos_obs = construir_linhas_lotes_consolidados(
        contexto,
        saida,
        tipo="exauridos",
        modo_bootstrap_pacote=True,
    )
    pacote_bootstrap = construir_pacote_saida_observavel_temporal(
        contexto,
        saida,
        lotes_ativos_observaveis=ativos_obs,
        lotes_exauridos_observaveis=exauridos_obs,
    )
    amostras_obs = construir_amostras_pagamentos_operacionais(
        saida,
        limite=1000,
        contexto=contexto,
        pacote_saida_observavel_temporal=pacote_bootstrap,
    )
    pagamentos_obs = list((amostras_obs.get("realizados") or {}).get("linhas") or [])
    return construir_pacote_saida_observavel_temporal(
        contexto,
        saida,
        lotes_ativos_observaveis=ativos_obs,
        lotes_exauridos_observaveis=exauridos_obs,
        pagamentos_realizados_observaveis=pagamentos_obs,
    )


def _construir_situacao_atual_completa(contexto: Any, saida: Any) -> list[dict[str, Any]]:
    pacote = _construir_pacote_observavel_temporal(contexto, saida)
    return construir_blocos_situacao_atual(
        contexto,
        saida,
        pacote_saida_observavel_temporal=pacote,
    )


def _linhas_bloco_situacao(blocos: list[dict[str, Any]], titulo: str) -> list[dict[str, Any]]:
    alvo = _normalizar_texto_chave(titulo)
    for bloco in blocos or []:
        if _normalizar_texto_chave(bloco.get("titulo")) == alvo:
            return list(bloco.get("linhas") or [])
    return []


def _resumir_saida(contexto: Any, saida: Any) -> dict[str, Any]:
    extrato_passado = getattr(saida, "extrato_passado", None) or []
    extrato_futuro = getattr(saida, "extrato_futuro", None) or []
    lotes_ativos = getattr(saida, "lotes_ativos", None) or []
    lotes_exauridos = getattr(saida, "lotes_exauridos", None) or []
    switchings = getattr(saida, "switchings", None) or []
    situacao_atual = _construir_situacao_atual_completa(contexto, saida)
    patrimonio_total_lotes = _linhas_bloco_situacao(situacao_atual, "Patrimônio total dos lotes")

    return {
        "versao": str(getattr(saida, "versao", "")),
        "data_referencia": str(getattr(saida, "data_referencia", "")),
        "patrimonio_liquido_atual": _valor_metrica_decimal(
            patrimonio_total_lotes,
            "Patrimônio líquido atual",
            "patrimonio liquido atual",
        ),
        "rendimento_liquido_atual": _valor_metrica_decimal(
            patrimonio_total_lotes,
            "Rendimento líquido atual",
            "rendimento liquido atual",
        ),
        "rendimento_liquido_reconciliado_recebidos": _valor_metrica_decimal(
            patrimonio_total_lotes,
            "Rendimento líquido atual — reconciliado contra recebidos",
            "rendimento liquido atual reconciliado contra recebidos",
        ),
        "ranking_top1": _ranking_top1(saida),
        "qtd_switchings_reais": len(switchings),
        "qtd_lotes_ativos": len(lotes_ativos),
        "qtd_lotes_exauridos": len(lotes_exauridos),
        "qtd_extrato_passado": len(extrato_passado),
        "qtd_extrato_futuro": len(extrato_futuro),
        "qtd_blocos_situacao_atual": len(situacao_atual),
        "hash_lotes_ativos": _hash_registros(lotes_ativos),
        "hash_lotes_exauridos": _hash_registros(lotes_exauridos),
        "hash_extrato_passado": _hash_registros(extrato_passado),
        "hash_extrato_futuro": _hash_registros(extrato_futuro),
        "hash_situacao_atual": _hash_registros(situacao_atual),
        "hash_switchings": _hash_registros(switchings),
    }


def _detalhes_por_hash(saida_baseline: Any, saida_compat: Any, contexto_baseline: Any, contexto_compat: Any) -> dict[str, list[dict[str, Any]]]:
    situacao_baseline = _construir_situacao_atual_completa(contexto_baseline, saida_baseline)
    situacao_compat = _construir_situacao_atual_completa(contexto_compat, saida_compat)
    return {
        "hash_lotes_ativos": _detalhar_divergencias_registros(
            getattr(saida_baseline, "lotes_ativos", None) or [],
            getattr(saida_compat, "lotes_ativos", None) or [],
            tabela="lotes_ativos",
        ),
        "hash_lotes_exauridos": _detalhar_divergencias_registros(
            getattr(saida_baseline, "lotes_exauridos", None) or [],
            getattr(saida_compat, "lotes_exauridos", None) or [],
            tabela="lotes_exauridos",
        ),
        "hash_extrato_passado": _detalhar_divergencias_registros(
            getattr(saida_baseline, "extrato_passado", None) or [],
            getattr(saida_compat, "extrato_passado", None) or [],
            tabela="extrato_passado",
        ),
        "hash_extrato_futuro": _detalhar_divergencias_registros(
            getattr(saida_baseline, "extrato_futuro", None) or [],
            getattr(saida_compat, "extrato_futuro", None) or [],
            tabela="extrato_futuro",
        ),
        "hash_situacao_atual": _detalhar_divergencias_registros(
            situacao_baseline,
            situacao_compat,
            tabela="situacao_atual",
        ),
        "hash_switchings": _detalhar_divergencias_registros(
            getattr(saida_baseline, "switchings", None) or [],
            getattr(saida_compat, "switchings", None) or [],
            tabela="switchings",
        ),
    }


def _comparar_resumos(
    resumo_baseline: dict[str, Any],
    resumo_compat: dict[str, Any],
    detalhes_por_hash: dict[str, list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    chaves = sorted(set(resumo_baseline) | set(resumo_compat))
    divergencias = []
    detalhes_por_hash = detalhes_por_hash or {}
    for chave in chaves:
        valor_baseline = resumo_baseline.get(chave)
        valor_compat = resumo_compat.get(chave)
        if valor_baseline != valor_compat:
            divergencia = {
                "campo": chave,
                "baseline": valor_baseline,
                "compat": valor_compat,
            }
            if chave in detalhes_por_hash:
                divergencia["detalhes"] = detalhes_por_hash[chave]
            divergencias.append(divergencia)
    return divergencias


def _construir_contexto_compat(
    contexto_baseline: Any,
    contexto_operacional_canonico: Any,
):
    componentes = ComponentesTransicionaisSaidaCanonica(
        decisao_local_v1=getattr(contexto_baseline, "decisao_local_v1"),
        recomputacao_sequencial_central_v1=getattr(
            contexto_baseline,
            "recomputacao_sequencial_central_v1",
        ),
    )
    return construir_contexto_saida_canonica_compat(
        contexto_operacional_canonico,
        componentes,
    )


def construir_saida_canonica_via_contexto_compat(
    contexto_baseline: Any,
    contexto_operacional_canonico: Any,
    *,
    versao: str = VERSAO_BASELINE,
):
    """Constrói saída em memória usando ContextoSaidaCanonicaCompat.

    A função não altera a rota principal e não escreve XLSX. Os componentes
    transicionais são retirados explicitamente do ContextoBaseline já carregado.
    """

    contexto_compat = _construir_contexto_compat(contexto_baseline, contexto_operacional_canonico)
    return construir_saida_canonica_com_switching_v17_c7(contexto_compat, versao=versao)


def comparar_saida_canonica_baseline_vs_compat(
    contexto_baseline: Any,
    contexto_operacional_canonico: Any,
    *,
    versao: str = VERSAO_BASELINE,
) -> ResultadoComparacaoSaidaCanonicaCompat:
    """Compara saída atual por ContextoBaseline contra saída via adaptador compatível.

    A comparação é controlada e isolada. Ela constrói duas saídas em memória,
    calcula resumos observáveis e retorna divergências sem promover a rota
    compatível e sem substituir ContextoBaseline.
    """

    contexto_compat = _construir_contexto_compat(contexto_baseline, contexto_operacional_canonico)
    saida_baseline = construir_saida_canonica_com_switching_v17_c7(contexto_baseline, versao=versao)
    saida_compat = construir_saida_canonica_com_switching_v17_c7(contexto_compat, versao=versao)

    resumo_baseline = _resumir_saida(contexto_baseline, saida_baseline)
    resumo_compat = _resumir_saida(contexto_compat, saida_compat)
    detalhes = _detalhes_por_hash(saida_baseline, saida_compat, contexto_baseline, contexto_compat)
    divergencias = _comparar_resumos(resumo_baseline, resumo_compat, detalhes)

    return ResultadoComparacaoSaidaCanonicaCompat(
        ok=not divergencias,
        resumo_baseline=resumo_baseline,
        resumo_compat=resumo_compat,
        divergencias=divergencias,
        metadados={
            "artefato": "ResultadoComparacaoSaidaCanonicaCompat",
            "microetapa": "ME-RUNTIME-CANON-08",
            "promove_rota_compat": False,
            "substitui_contexto_baseline": False,
            "altera_runtime_principal": False,
            "altera_xlsx_oficial": False,
            "versao": versao,
            "detalha_divergencias_por_chave_estavel": True,
            "hash_situacao_atual_completa": True,
            "metricas_financeiras_do_bloco_patrimonio_total_lotes": True,
        },
    )


def imprimir_resumo_comparacao(resultado: ResultadoComparacaoSaidaCanonicaCompat) -> None:
    """Imprime resumo textual curto da comparação isolada."""

    print("=== COMPARAÇÃO OBSERVÁVEL CONTROLADA — CONTEXTO COMPAT ===")
    print(f"ok={resultado.ok}")
    print(f"divergencias={len(resultado.divergencias)}")
    for chave in (
        "patrimonio_liquido_atual",
        "rendimento_liquido_atual",
        "rendimento_liquido_reconciliado_recebidos",
        "ranking_top1",
        "qtd_switchings_reais",
        "qtd_lotes_ativos",
        "qtd_lotes_exauridos",
        "qtd_extrato_passado",
        "qtd_extrato_futuro",
        "qtd_blocos_situacao_atual",
    ):
        print(
            f"{chave}: baseline={resultado.resumo_baseline.get(chave)} | "
            f"compat={resultado.resumo_compat.get(chave)}"
        )
    if resultado.divergencias:
        print("--- divergências ---")
        for divergencia in resultado.divergencias:
            print(
                f"{divergencia['campo']}: baseline={divergencia['baseline']} | "
                f"compat={divergencia['compat']}"
            )
            detalhes = divergencia.get("detalhes") or []
            for detalhe in detalhes[:5]:
                print(
                    f"  chave={detalhe.get('chave')} | status={detalhe.get('status')} | "
                    f"campos={detalhe.get('qtd_campos_divergentes', '')}"
                )
                for campo in (detalhe.get("campos") or [])[:5]:
                    print(
                        f"    {campo.get('campo')}: baseline={campo.get('baseline')} | "
                        f"compat={campo.get('compat')}"
                    )
