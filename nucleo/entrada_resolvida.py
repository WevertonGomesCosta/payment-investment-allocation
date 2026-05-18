"""Estruturas formais da Etapa 1: entrada resolvida."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Mapping, Optional

import pandas as pd


@dataclass(slots=True)
class MapaAbasResolvidas:
    """Mapa estrutural entre blocos canônicos e abas físicas."""

    abas_por_bloco: Mapping[str, str] = field(default_factory=dict)
    metadados_por_bloco: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    auditoria: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MapaColunasResolvidas:
    """Mapa estrutural entre campos canônicos e colunas físicas."""

    colunas_por_bloco: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    metadados_por_bloco: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    auditoria: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class JanelaConsultaCDI:
    """Janela bruta de consulta da série CDI/BCB."""

    data_inicial_consulta: Optional[date] = None
    data_final_consulta: Optional[date] = None
    metadados: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AuditoriaEntradaBruta:
    """Auditoria da obtenção física da entrada bruta."""

    fonte_planilha: str = ""
    fetch_status_planilha: str = ""
    caminho_planilha: str = ""
    qtd_abas_planilha: int = 0
    detalhes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AuditoriaResolucaoEntrada:
    """Auditoria da resolução estrutural da entrada."""

    abas_resolvidas: Mapping[str, Any] = field(default_factory=dict)
    colunas_resolvidas: Mapping[str, Any] = field(default_factory=dict)
    aliases_testados: Mapping[str, Any] = field(default_factory=dict)
    ausencias: Mapping[str, Any] = field(default_factory=dict)
    colisoes: Mapping[str, Any] = field(default_factory=dict)
    duplicidades_estruturais: Mapping[str, Any] = field(default_factory=dict)
    detalhes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AuditoriaCacheCDI:
    """Auditoria da disponibilidade do cache CDI/BCB."""

    fonte_serie_cdi: str = ""
    fetch_status: str = ""
    qtd_datas_serie_cdi: int = 0
    ultima_data_serie_cdi: Optional[date] = None
    cache_atualizado_para_referencia: Optional[bool] = None
    caminho_cache: str = ""
    detalhes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PacoteEntradaResolvida:
    """Artefato único produzido pela Etapa 1."""

    pacote_config: Optional[Any] = None
    contexto_execucao: Optional[Any] = None
    pacote_planilha: Optional[Any] = None
    mapa_abas_resolvidas: Optional[MapaAbasResolvidas] = None
    mapa_colunas_resolvidas: Optional[MapaColunasResolvidas] = None
    quadros_brutos: Mapping[str, pd.DataFrame] = field(default_factory=dict)
    quadros_estruturais_resolvidos: Mapping[str, pd.DataFrame] = field(default_factory=dict)
    janela_consulta_cdi: Optional[JanelaConsultaCDI] = None
    pacote_cache_cdi: Optional[Any] = None
    auditoria_entrada_bruta: Optional[AuditoriaEntradaBruta] = None
    auditoria_resolucao_entrada: Optional[AuditoriaResolucaoEntrada] = None
    auditoria_cache_cdi: Optional[AuditoriaCacheCDI] = None
    metadados: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AuditoriaPacoteEntradaResolvida:
    """Resultado da auditoria estrutural do PacoteEntradaResolvida."""

    ok: bool = True
    erros: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    evidencias: Mapping[str, Any] = field(default_factory=dict)
    detalhes: Mapping[str, Any] = field(default_factory=dict)


def _mapping_atributo(objeto: Any, nome: str) -> Mapping[str, Any]:
    valor = getattr(objeto, nome, {}) if objeto is not None else {}
    return valor if isinstance(valor, Mapping) else {}


def _inteiro_seguro(valor: Any, padrao: int = 0) -> int:
    try:
        return int(valor)
    except Exception:
        return padrao


def _texto_seguro(valor: Any) -> str:
    return "" if valor is None else str(valor)


def _data_ou_none(valor: Any) -> Optional[date]:
    if valor is None:
        return None
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        try:
            return date.fromisoformat(valor)
        except Exception:
            return None
    return None


def _qtd_dataframes(mapa_quadros: Mapping[str, Any]) -> int:
    if not isinstance(mapa_quadros, Mapping):
        return 0
    return sum(1 for quadro in mapa_quadros.values() if isinstance(quadro, pd.DataFrame))


def montar_auditoria_entrada_bruta(pacote_planilha: Any) -> AuditoriaEntradaBruta:
    """Monta a auditoria formal da obtenção física da entrada bruta."""

    auditoria = _mapping_atributo(pacote_planilha, "auditoria")
    return AuditoriaEntradaBruta(
        fonte_planilha=_texto_seguro(auditoria.get("fonte_planilha")),
        fetch_status_planilha=_texto_seguro(auditoria.get("fetch_status_planilha")),
        caminho_planilha=_texto_seguro(auditoria.get("caminho_planilha")),
        qtd_abas_planilha=_inteiro_seguro(auditoria.get("qtd_abas_planilha")),
        detalhes=dict(auditoria),
    )


def montar_auditoria_resolucao_entrada(
    mapa_abas_resolvidas: Optional[MapaAbasResolvidas],
    mapa_colunas_resolvidas: Optional[MapaColunasResolvidas],
) -> AuditoriaResolucaoEntrada:
    """Monta a auditoria formal da resolução estrutural da entrada."""

    auditoria_abas = dict(mapa_abas_resolvidas.auditoria) if mapa_abas_resolvidas else {}
    auditoria_colunas = dict(mapa_colunas_resolvidas.auditoria) if mapa_colunas_resolvidas else {}
    ausencias = {
        "blocos_ausentes": auditoria_abas.get("blocos_ausentes", []),
        "campos_ausentes_por_bloco": auditoria_colunas.get("campos_ausentes_por_bloco", {}),
    }
    return AuditoriaResolucaoEntrada(
        abas_resolvidas=auditoria_abas,
        colunas_resolvidas=auditoria_colunas,
        aliases_testados={},
        ausencias=ausencias,
        colisoes={},
        duplicidades_estruturais={},
        detalhes={
            "mapa_abas_resolvidas_presente": mapa_abas_resolvidas is not None,
            "mapa_colunas_resolvidas_presente": mapa_colunas_resolvidas is not None,
        },
    )


def montar_auditoria_cache_cdi(pacote_cache_cdi: Any) -> Optional[AuditoriaCacheCDI]:
    """Monta a auditoria formal da disponibilidade do cache CDI/BCB."""

    if pacote_cache_cdi is None:
        return None
    auditoria = _mapping_atributo(pacote_cache_cdi, "auditoria")
    return AuditoriaCacheCDI(
        fonte_serie_cdi=_texto_seguro(auditoria.get("fonte_serie_cdi")),
        fetch_status=_texto_seguro(auditoria.get("fetch_status")),
        qtd_datas_serie_cdi=_inteiro_seguro(auditoria.get("qtd_datas_serie_cdi")),
        ultima_data_serie_cdi=_data_ou_none(auditoria.get("ultima_data_serie_cdi")),
        cache_atualizado_para_referencia=auditoria.get("cache_atualizado_para_referencia"),
        caminho_cache=_texto_seguro(auditoria.get("caminho_cache")),
        detalhes=dict(auditoria),
    )


def montar_pacote_entrada_resolvida(
    *,
    pacote_config: Optional[Any] = None,
    contexto_execucao: Optional[Any] = None,
    pacote_planilha: Optional[Any] = None,
    pacote_cache_cdi: Optional[Any] = None,
    metadados: Optional[Mapping[str, Any]] = None,
) -> PacoteEntradaResolvida:
    """Monta o artefato único da Etapa 1 sem alterar os produtores atuais.

    A função agrega os artefatos estruturais já produzidos por módulos da
    Etapa 1. Ela não lê planilha, não consulta BCB, não cria dados
    operacionais canônicos, não executa validação pré-execução e não altera
    motor, saída, console ou XLSX.
    """

    mapa_abas_resolvidas = getattr(pacote_planilha, "mapa_abas_resolvidas", None)
    mapa_colunas_resolvidas = getattr(pacote_planilha, "mapa_colunas_resolvidas", None)
    quadros_brutos = getattr(pacote_planilha, "quadros_brutos", {}) or {}
    quadros_estruturais_resolvidos = getattr(
        pacote_planilha,
        "quadros_estruturais_resolvidos",
        None,
    )
    if quadros_estruturais_resolvidos is None:
        quadros_estruturais_resolvidos = getattr(pacote_planilha, "quadros_canonicos", {}) or {}
    janela_consulta_cdi = getattr(pacote_planilha, "janela_consulta_cdi", None)

    metadados_base: dict[str, Any] = {
        "artefato": "PacoteEntradaResolvida",
        "etapa": "Etapa 1",
        "montagem_estrutural": True,
        "altera_leitura_planilha": False,
        "altera_cache_cdi": False,
        "altera_validacao_pre_execucao": False,
        "altera_dados_operacionais_canonicos": False,
        "altera_motor": False,
        "altera_saida": False,
        "pacote_planilha_informado": pacote_planilha is not None,
        "pacote_cache_cdi_informado": pacote_cache_cdi is not None,
    }
    if metadados:
        metadados_base.update(dict(metadados))

    return PacoteEntradaResolvida(
        pacote_config=pacote_config,
        contexto_execucao=contexto_execucao,
        pacote_planilha=pacote_planilha,
        mapa_abas_resolvidas=mapa_abas_resolvidas,
        mapa_colunas_resolvidas=mapa_colunas_resolvidas,
        quadros_brutos=quadros_brutos,
        quadros_estruturais_resolvidos=quadros_estruturais_resolvidos,
        janela_consulta_cdi=janela_consulta_cdi,
        pacote_cache_cdi=pacote_cache_cdi,
        auditoria_entrada_bruta=montar_auditoria_entrada_bruta(pacote_planilha),
        auditoria_resolucao_entrada=montar_auditoria_resolucao_entrada(
            mapa_abas_resolvidas,
            mapa_colunas_resolvidas,
        ),
        auditoria_cache_cdi=montar_auditoria_cache_cdi(pacote_cache_cdi),
        metadados=metadados_base,
    )


def auditar_pacote_entrada_resolvida(
    pacote: Any,
    *,
    exigir_cache_cdi: bool = False,
) -> AuditoriaPacoteEntradaResolvida:
    """Audita estruturalmente um PacoteEntradaResolvida já montado.

    Esta auditoria pertence ainda à Etapa 1. Ela não substitui a validação
    pré-execução da Etapa 2, não cria dados operacionais canônicos, não calcula
    rendimento e não altera motor, saída, console ou XLSX.
    """

    erros: list[str] = []
    avisos: list[str] = []

    if not isinstance(pacote, PacoteEntradaResolvida):
        erros.append("pacote_nao_e_PacoteEntradaResolvida")
        return AuditoriaPacoteEntradaResolvida(
            ok=False,
            erros=erros,
            avisos=avisos,
            evidencias={"tipo_recebido": type(pacote).__name__},
            detalhes={"exigir_cache_cdi": exigir_cache_cdi},
        )

    metadados = dict(pacote.metadados) if isinstance(pacote.metadados, Mapping) else {}
    quadros_brutos = pacote.quadros_brutos if isinstance(pacote.quadros_brutos, Mapping) else {}
    quadros_estruturais = (
        pacote.quadros_estruturais_resolvidos
        if isinstance(pacote.quadros_estruturais_resolvidos, Mapping)
        else {}
    )

    campos_obrigatorios = {
        "pacote_planilha": pacote.pacote_planilha is not None,
        "mapa_abas_resolvidas": isinstance(pacote.mapa_abas_resolvidas, MapaAbasResolvidas),
        "mapa_colunas_resolvidas": isinstance(pacote.mapa_colunas_resolvidas, MapaColunasResolvidas),
        "quadros_brutos": isinstance(pacote.quadros_brutos, Mapping) and len(quadros_brutos) > 0,
        "quadros_estruturais_resolvidos": isinstance(pacote.quadros_estruturais_resolvidos, Mapping)
        and len(quadros_estruturais) > 0,
        "janela_consulta_cdi": isinstance(pacote.janela_consulta_cdi, JanelaConsultaCDI),
        "auditoria_entrada_bruta": isinstance(pacote.auditoria_entrada_bruta, AuditoriaEntradaBruta),
        "auditoria_resolucao_entrada": isinstance(pacote.auditoria_resolucao_entrada, AuditoriaResolucaoEntrada),
    }

    for campo, presente in campos_obrigatorios.items():
        if not presente:
            erros.append(f"campo_obrigatorio_ausente_ou_invalido:{campo}")

    if exigir_cache_cdi:
        if pacote.pacote_cache_cdi is None:
            erros.append("cache_cdi_exigido_mas_pacote_cache_cdi_ausente")
        if not isinstance(pacote.auditoria_cache_cdi, AuditoriaCacheCDI):
            erros.append("cache_cdi_exigido_mas_auditoria_cache_cdi_ausente_ou_invalida")
    elif pacote.pacote_cache_cdi is None:
        avisos.append("pacote_cache_cdi_ausente_cache_opcional")

    qtd_quadros_brutos = _qtd_dataframes(quadros_brutos)
    qtd_quadros_estruturais = _qtd_dataframes(quadros_estruturais)
    if qtd_quadros_brutos != len(quadros_brutos):
        erros.append("quadros_brutos_contem_item_nao_dataframe")
    if qtd_quadros_estruturais != len(quadros_estruturais):
        erros.append("quadros_estruturais_resolvidos_contem_item_nao_dataframe")

    if isinstance(pacote.janela_consulta_cdi, JanelaConsultaCDI):
        data_ini = pacote.janela_consulta_cdi.data_inicial_consulta
        data_fim = pacote.janela_consulta_cdi.data_final_consulta
        if data_ini is None or data_fim is None:
            avisos.append("janela_consulta_cdi_sem_datas_completas")
        elif data_fim < data_ini:
            erros.append("janela_consulta_cdi_data_final_menor_que_data_inicial")

    for chave in (
        "altera_leitura_planilha",
        "altera_cache_cdi",
        "altera_validacao_pre_execucao",
        "altera_dados_operacionais_canonicos",
        "altera_motor",
        "altera_saida",
    ):
        if metadados.get(chave) is not False:
            erros.append(f"metadado_flag_nao_false:{chave}")

    if metadados.get("artefato") != "PacoteEntradaResolvida":
        erros.append("metadado_artefato_invalido")
    if metadados.get("etapa") != "Etapa 1":
        erros.append("metadado_etapa_invalido")
    if metadados.get("montagem_estrutural") is not True:
        erros.append("metadado_montagem_estrutural_nao_true")

    evidencias = {
        "tipo_pacote": type(pacote).__name__,
        "campos_obrigatorios": campos_obrigatorios,
        "qtd_quadros_brutos": len(quadros_brutos),
        "qtd_dataframes_quadros_brutos": qtd_quadros_brutos,
        "qtd_quadros_estruturais_resolvidos": len(quadros_estruturais),
        "qtd_dataframes_quadros_estruturais_resolvidos": qtd_quadros_estruturais,
        "tem_cache_cdi": pacote.pacote_cache_cdi is not None,
        "tem_auditoria_cache_cdi": isinstance(pacote.auditoria_cache_cdi, AuditoriaCacheCDI),
        "janela_consulta_cdi_presente": isinstance(pacote.janela_consulta_cdi, JanelaConsultaCDI),
        "metadados_chaves": sorted(metadados.keys()),
    }

    detalhes = {
        "exigir_cache_cdi": exigir_cache_cdi,
        "auditoria_etapa": "Etapa 1",
        "nao_substitui_validacao_pre_execucao": True,
        "altera_motor": False,
        "altera_saida": False,
    }

    return AuditoriaPacoteEntradaResolvida(
        ok=len(erros) == 0,
        erros=erros,
        avisos=avisos,
        evidencias=evidencias,
        detalhes=detalhes,
    )


__all__ = [
    "AuditoriaCacheCDI",
    "AuditoriaEntradaBruta",
    "AuditoriaPacoteEntradaResolvida",
    "AuditoriaResolucaoEntrada",
    "JanelaConsultaCDI",
    "MapaAbasResolvidas",
    "MapaColunasResolvidas",
    "PacoteEntradaResolvida",
    "auditar_pacote_entrada_resolvida",
    "montar_auditoria_cache_cdi",
    "montar_auditoria_entrada_bruta",
    "montar_auditoria_resolucao_entrada",
    "montar_pacote_entrada_resolvida",
]
