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


__all__ = [
    "AuditoriaCacheCDI",
    "AuditoriaEntradaBruta",
    "AuditoriaResolucaoEntrada",
    "JanelaConsultaCDI",
    "MapaAbasResolvidas",
    "MapaColunasResolvidas",
    "PacoteEntradaResolvida",
]
