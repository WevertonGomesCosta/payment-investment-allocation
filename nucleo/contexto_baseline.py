from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

from nucleo.ambiente import ContextoExecucao, bootstrap_ambiente
from nucleo.cache_cdi_bcb import PacoteCacheCDIDiario, carregar_cache_cdi_diario
from nucleo.calendario_financeiro import construir_calendario_financeiro
from nucleo.carregador_config import PacoteConfig, carregar_config
from nucleo.carteira_canonica import carregar_carteira_canonica
from nucleo.dados_operacionais_canonicos import carregar_dados_operacionais_canonicos
from nucleo.leitor_planilha import PacotePlanilha, carregar_planilha
from nucleo.nucleo_financeiro_minimo import construir_faixas_ir, construir_tabela_iof, carregar_nucleo_financeiro_minimo
from nucleo.replay_passado_controlado import carregar_replay_passado_controlado
from nucleo.switching_shadow_reconciliacao import carregar_switching_shadow_reconciliacao
from nucleo.triagem_motor import carregar_triagem_motor
from nucleo.config_utils import obter_config


@dataclass(slots=True)
class ContextoBaseline:
    pacote_config: PacoteConfig
    execucao: ContextoExecucao
    calendario_financeiro: Any
    pacote_planilha: PacotePlanilha
    carteira_canonica: Any
    dados_operacionais: Any
    cache_cdi: PacoteCacheCDIDiario
    switching_shadow: Any
    triagem_motor: Any
    nucleo_financeiro: Any
    replay_passado: Any
    tabela_iof: list[float]
    faixas_ir: list[dict[str, Any]]


@dataclass(slots=True)
class ContextoBaselineMenos1Dia:
    data_referencia_menos_1_dia: Any
    calendario_financeiro: Any
    dados_operacionais: Any
    nucleo_financeiro: Any
    replay_passado: Any


def obter_limiar_residuo_resolvido(config: dict[str, Any]) -> float:
    auditoria_cfg = obter_config(config, 'auditoria', padrao={}) or {}
    replay_cfg = obter_config(config, 'replay', padrao={}) or {}
    valor = auditoria_cfg.get('limiar_residuo_resolvido')
    if valor is None:
        valor = replay_cfg.get('valor_minimo_lote_ativo', 0.01)
    try:
        return round(float(valor), 2)
    except Exception:
        return 0.01


def carregar_contexto_baseline(
    *,
    raiz_repositorio: Path | None = None,
    instalar_automaticamente: bool = False,
    incluir_switching_shadow: bool = True,
    incluir_triagem: bool = True,
    incluir_replay: bool = True,
) -> ContextoBaseline:
    pacote_config = carregar_config(raiz_repositorio=raiz_repositorio)
    contexto_execucao = bootstrap_ambiente(
        pacote_config.conteudo,
        grupos_extras=['financeiro'],
        instalar_automaticamente=instalar_automaticamente,
    )
    calendario_financeiro = construir_calendario_financeiro(pacote_config.conteudo, data_referencia=contexto_execucao.data_referencia)
    pacote_planilha = carregar_planilha(pacote_config.conteudo, raiz_repositorio=pacote_config.raiz_repositorio)
    carteira_canonica = carregar_carteira_canonica(pacote_planilha, pacote_config.conteudo)
    dados_operacionais = carregar_dados_operacionais_canonicos(
        pacote_planilha,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
        carteira_canonica=carteira_canonica,
    )
    cache_cdi = carregar_cache_cdi_diario(
        dados_operacionais,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
        raiz_repositorio=pacote_config.raiz_repositorio,
    )
    switching_shadow = carregar_switching_shadow_reconciliacao(dados_operacionais, carteira_canonica=carteira_canonica) if incluir_switching_shadow else None
    triagem_motor = carregar_triagem_motor(
        carteira_canonica,
        dados_operacionais,
        calendario_financeiro,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
    ) if incluir_triagem else None
    nucleo_financeiro = carregar_nucleo_financeiro_minimo(
        dados_operacionais,
        carteira_canonica,
        calendario_financeiro,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
        serie_cdi=cache_cdi.serie_cdi,
    )
    replay_passado = carregar_replay_passado_controlado(
        dados_operacionais,
        nucleo_financeiro,
        calendario_financeiro,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
        serie_cdi=cache_cdi.serie_cdi,
    ) if incluir_replay else None
    return ContextoBaseline(
        pacote_config=pacote_config,
        execucao=contexto_execucao,
        calendario_financeiro=calendario_financeiro,
        pacote_planilha=pacote_planilha,
        carteira_canonica=carteira_canonica,
        dados_operacionais=dados_operacionais,
        cache_cdi=cache_cdi,
        switching_shadow=switching_shadow,
        triagem_motor=triagem_motor,
        nucleo_financeiro=nucleo_financeiro,
        replay_passado=replay_passado,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
    )


def carregar_contexto_baseline_menos_1_dia(contexto: ContextoBaseline) -> ContextoBaselineMenos1Dia:
    data_referencia_menos_1_dia = contexto.execucao.data_referencia - timedelta(days=1)
    calendario_financeiro = construir_calendario_financeiro(contexto.pacote_config.conteudo, data_referencia=data_referencia_menos_1_dia)
    dados_operacionais = carregar_dados_operacionais_canonicos(
        contexto.pacote_planilha,
        contexto.pacote_config.conteudo,
        data_referencia=data_referencia_menos_1_dia,
        carteira_canonica=contexto.carteira_canonica,
    )
    nucleo_financeiro = carregar_nucleo_financeiro_minimo(
        dados_operacionais,
        contexto.carteira_canonica,
        calendario_financeiro,
        contexto.pacote_config.conteudo,
        data_referencia=data_referencia_menos_1_dia,
        serie_cdi=contexto.cache_cdi.serie_cdi,
    )
    replay_passado = carregar_replay_passado_controlado(
        dados_operacionais,
        nucleo_financeiro,
        calendario_financeiro,
        contexto.pacote_config.conteudo,
        data_referencia=data_referencia_menos_1_dia,
        serie_cdi=contexto.cache_cdi.serie_cdi,
    )
    return ContextoBaselineMenos1Dia(
        data_referencia_menos_1_dia=data_referencia_menos_1_dia,
        calendario_financeiro=calendario_financeiro,
        dados_operacionais=dados_operacionais,
        nucleo_financeiro=nucleo_financeiro,
        replay_passado=replay_passado,
    )
