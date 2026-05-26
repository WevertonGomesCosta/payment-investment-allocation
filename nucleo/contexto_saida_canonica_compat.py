from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Mapping


@dataclass(slots=True)
class ComponentesTransicionaisSaidaCanonica:
    """Componentes transitórios exigidos pela saída canônica legada.

    Estes campos não pertencem ao ContextoOperacionalCanonico e devem ser
    fornecidos explicitamente enquanto a rota de saída ainda depender da forma
    compatível com ContextoBaseline.
    """

    decisao_local_v1: Any
    recomputacao_sequencial_central_v1: Any


@dataclass(slots=True)
class ContextoSaidaCanonicaCompat:
    """Contexto compatível isolado para construção futura de saída canônica.

    O objeto combina campos canônicos vindos de ContextoOperacionalCanonico com
    os componentes transicionais estritamente necessários para consumidores que
    ainda esperam parte da forma histórica de ContextoBaseline.

    Este módulo não carrega dados, não executa I/O, não altera runtime principal
    e não substitui carregar_contexto_baseline().
    """

    pacote_config: Any
    execucao: Any
    calendario_financeiro: Any
    pacote_planilha: Any
    pacote_entrada_resolvida: Any
    auditoria_pacote_entrada_resolvida: Any
    validacao_pre_execucao: Any
    carteira_canonica: Any
    dados_operacionais: Any
    recebidos_auditaveis: Any
    fontes_elegiveis_pagamento: Any
    saldo_disponivel_geral: Any
    cache_cdi: Any
    nucleo_financeiro: Any
    replay_passado: Any
    ranking_carteira: Any
    tabela_iof: list[float]
    faixas_ir: list[dict[str, Any]]
    decisao_local_v1: Any
    recomputacao_sequencial_central_v1: Any
    metadados: dict[str, Any]


def _obter_campo(objeto: Any, nome: str) -> Any:
    if hasattr(objeto, nome):
        return getattr(objeto, nome)
    raise ValueError(f"campo_obrigatorio_ausente:{nome}")


def _normalizar_componentes_transicionais(
    componentes_transicionais: ComponentesTransicionaisSaidaCanonica | Mapping[str, Any] | Any,
) -> ComponentesTransicionaisSaidaCanonica:
    if isinstance(componentes_transicionais, ComponentesTransicionaisSaidaCanonica):
        return componentes_transicionais

    if isinstance(componentes_transicionais, Mapping):
        faltantes = [
            nome
            for nome in ("decisao_local_v1", "recomputacao_sequencial_central_v1")
            if nome not in componentes_transicionais
        ]
        if faltantes:
            raise ValueError("componentes_transicionais_ausentes:" + ",".join(faltantes))
        return ComponentesTransicionaisSaidaCanonica(
            decisao_local_v1=componentes_transicionais["decisao_local_v1"],
            recomputacao_sequencial_central_v1=componentes_transicionais[
                "recomputacao_sequencial_central_v1"
            ],
        )

    return ComponentesTransicionaisSaidaCanonica(
        decisao_local_v1=_obter_campo(componentes_transicionais, "decisao_local_v1"),
        recomputacao_sequencial_central_v1=_obter_campo(
            componentes_transicionais,
            "recomputacao_sequencial_central_v1",
        ),
    )


def construir_contexto_saida_canonica_compat(
    contexto_operacional_canonico: Any,
    componentes_transicionais: ComponentesTransicionaisSaidaCanonica | Mapping[str, Any] | Any,
) -> ContextoSaidaCanonicaCompat:
    """Constrói adaptador compatível para uso isolado futuro.

    A função apenas copia campos já materializados. Ela não executa download, não
    lê planilha, não recalcula motor, não chama replay, não gera XLSX e não
    altera a rota principal.
    """

    transicionais = _normalizar_componentes_transicionais(componentes_transicionais)

    return ContextoSaidaCanonicaCompat(
        pacote_config=_obter_campo(contexto_operacional_canonico, "pacote_config"),
        execucao=_obter_campo(contexto_operacional_canonico, "execucao"),
        calendario_financeiro=_obter_campo(contexto_operacional_canonico, "calendario_financeiro"),
        pacote_planilha=_obter_campo(contexto_operacional_canonico, "pacote_planilha"),
        pacote_entrada_resolvida=_obter_campo(
            contexto_operacional_canonico,
            "pacote_entrada_resolvida",
        ),
        auditoria_pacote_entrada_resolvida=_obter_campo(
            contexto_operacional_canonico,
            "auditoria_pacote_entrada_resolvida",
        ),
        validacao_pre_execucao=_obter_campo(
            contexto_operacional_canonico,
            "validacao_pre_execucao",
        ),
        carteira_canonica=_obter_campo(contexto_operacional_canonico, "carteira_canonica"),
        dados_operacionais=_obter_campo(contexto_operacional_canonico, "dados_operacionais"),
        recebidos_auditaveis=_obter_campo(contexto_operacional_canonico, "recebidos_auditaveis"),
        fontes_elegiveis_pagamento=_obter_campo(
            contexto_operacional_canonico,
            "fontes_elegiveis_pagamento",
        ),
        saldo_disponivel_geral=_obter_campo(
            contexto_operacional_canonico,
            "saldo_disponivel_geral",
        ),
        cache_cdi=_obter_campo(contexto_operacional_canonico, "cache_cdi"),
        nucleo_financeiro=_obter_campo(contexto_operacional_canonico, "nucleo_financeiro"),
        replay_passado=_obter_campo(contexto_operacional_canonico, "replay_passado"),
        ranking_carteira=_obter_campo(contexto_operacional_canonico, "ranking_carteira"),
        tabela_iof=_obter_campo(contexto_operacional_canonico, "tabela_iof"),
        faixas_ir=_obter_campo(contexto_operacional_canonico, "faixas_ir"),
        decisao_local_v1=transicionais.decisao_local_v1,
        recomputacao_sequencial_central_v1=transicionais.recomputacao_sequencial_central_v1,
        metadados={
            "artefato": "ContextoSaidaCanonicaCompat",
            "microetapa": "ME-RUNTIME-CANON-07",
            "uso_runtime_principal": False,
            "substitui_contexto_baseline": False,
            "altera_motor": False,
            "altera_replay": False,
            "altera_ledger": False,
            "altera_ranking": False,
            "altera_saida_xlsx": False,
            "campos_transicionais": [
                "decisao_local_v1",
                "recomputacao_sequencial_central_v1",
            ],
        },
    )


def campos_contexto_saida_canonica_compat() -> list[str]:
    """Retorna os campos expostos pelo adaptador compatível."""

    return [campo.name for campo in fields(ContextoSaidaCanonicaCompat)]


def validar_contexto_saida_canonica_compat(contexto: ContextoSaidaCanonicaCompat) -> dict[str, Any]:
    """Valida presença nominal dos campos requeridos pelo adaptador isolado."""

    campos = campos_contexto_saida_canonica_compat()
    ausentes = [nome for nome in campos if not hasattr(contexto, nome)]
    return {
        "artefato": "ContextoSaidaCanonicaCompat",
        "ok": not ausentes,
        "campos": campos,
        "campos_ausentes": ausentes,
        "uso_runtime_principal": False,
        "substitui_contexto_baseline": False,
    }
