from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nucleo.ambiente import ContextoExecucao, bootstrap_ambiente
from nucleo.cache_cdi_bcb import PacoteCacheCDIDiario, carregar_cache_cdi_diario
from nucleo.calendario_financeiro import construir_calendario_financeiro
from nucleo.carregador_config import PacoteConfig, carregar_config
from nucleo.carteira_canonica import carregar_carteira_canonica
from nucleo.dados_operacionais_canonicos import carregar_dados_operacionais_canonicos
from nucleo.entrada_resolvida import (
    AuditoriaPacoteEntradaResolvida,
    PacoteEntradaResolvida,
    auditar_pacote_entrada_resolvida,
    montar_pacote_entrada_resolvida,
)
from nucleo.leitor_planilha import PacotePlanilha, carregar_planilha
from nucleo.nucleo_financeiro_minimo import construir_faixas_ir, construir_tabela_iof, carregar_nucleo_financeiro_minimo
from nucleo.replay_passado_controlado import carregar_replay_passado_controlado
from nucleo.switching_shadow_reconciliacao import carregar_switching_shadow_reconciliacao
from nucleo.triagem_motor import carregar_triagem_motor
from nucleo.ranking_carteira_estabilizado import carregar_ranking_carteira_estabilizado
from nucleo.switching_economico_shadow import carregar_switching_economico_shadow
from nucleo.resolver_hibrido_5p_shadow import carregar_resolver_hibrido_5p_shadow
from nucleo.benchmark_agrupado_individual_shadow import carregar_benchmark_agrupado_individual_shadow
from nucleo.benchmark_runner_futuro_shadow import carregar_benchmark_runner_futuro_shadow
from nucleo.auditoria_runner_futuro_shadow import carregar_auditoria_runner_futuro_shadow
from nucleo.auditoria_primeira_quebra_runner_futuro_shadow import carregar_auditoria_primeira_quebra_runner_futuro_shadow
from nucleo.auditoria_temporal_decisao_local import carregar_auditoria_temporal_decisao_local
from nucleo.reescolha_dinamica_pos_quebra import carregar_reescolha_dinamica_pos_quebra
from nucleo.heuristica_conjunta_parcial_bloco_critico import carregar_heuristica_conjunta_parcial_bloco_critico
from nucleo.planejamento_conjunto_local_bloco_critico_v1 import carregar_planejamento_conjunto_local_bloco_critico_v1
from nucleo.microplanejamento_conjunto_bloco_critico_v2 import carregar_microplanejamento_conjunto_bloco_critico_v2
from nucleo.recomputacao_sequencial_central_v1 import carregar_recomputacao_sequencial_central_v1
from nucleo.motor_recomendacao_pagamentos_switching_v1 import carregar_motor_recomendacao_pagamentos_switching_v1
from nucleo.config_utils import obter_config
from nucleo.validacao_pre_execucao import (
    PacoteValidacaoPreExecucao,
    validar_pre_execucao,
    validar_pre_execucao_pacote_entrada_resolvida,
)
from nucleo.caixa_recebidos_auditaveis import (
    materializar_fontes_elegiveis_pagamento,
    materializar_recebidos_auditaveis,
    materializar_saldo_disponivel_geral,
    materializar_decisao_local_v1,
)


@dataclass(slots=True)
class ContextoBaseline:
    pacote_config: PacoteConfig
    execucao: ContextoExecucao
    calendario_financeiro: Any
    pacote_planilha: PacotePlanilha
    validacao_pre_execucao: PacoteValidacaoPreExecucao
    validacao_pre_execucao_legada_shadow: PacoteValidacaoPreExecucao
    validacao_pre_execucao_pacote_entrada_resolvida_shadow: PacoteValidacaoPreExecucao
    carteira_canonica: Any
    dados_operacionais: Any
    recebidos_auditaveis: Any
    fontes_elegiveis_pagamento: Any
    saldo_disponivel_geral: Any
    decisao_local_v1: Any
    cache_cdi: PacoteCacheCDIDiario
    pacote_entrada_resolvida_shadow: PacoteEntradaResolvida
    auditoria_pacote_entrada_resolvida_shadow: AuditoriaPacoteEntradaResolvida
    auditoria_temporal_decisao_local: Any
    reescolha_dinamica_pos_quebra: Any
    heuristica_conjunta_parcial_bloco_critico: Any
    planejamento_conjunto_local_bloco_critico_v1: Any
    microplanejamento_conjunto_bloco_critico_v2: Any
    recomputacao_sequencial_central_v1: Any
    motor_recomendacao_pagamentos_switching_v1: Any
    switching_shadow: Any
    switching_economico_shadow: Any
    resolver_hibrido_5p_shadow: Any
    benchmark_agrupado_individual_shadow: Any
    benchmark_runner_futuro_shadow: Any
    auditoria_runner_futuro_shadow: Any
    auditoria_primeira_quebra_runner_futuro_shadow: Any
    triagem_motor: Any
    ranking_carteira: Any
    nucleo_financeiro: Any
    replay_passado: Any
    tabela_iof: list[float]
    faixas_ir: list[dict[str, Any]]


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
    incluir_switching_economico_shadow: bool = True,
    incluir_resolver_hibrido_5p_shadow: bool = True,
    incluir_benchmark_agrupado_individual_shadow: bool = True,
    incluir_benchmark_runner_futuro_shadow: bool = True,
    incluir_auditoria_primeira_quebra_runner_futuro_shadow: bool = True,
) -> ContextoBaseline:
    pacote_config = carregar_config(raiz_repositorio=raiz_repositorio)
    contexto_execucao = bootstrap_ambiente(
        pacote_config.conteudo,
        grupos_extras=['financeiro'],
        instalar_automaticamente=instalar_automaticamente,
    )
    calendario_financeiro = construir_calendario_financeiro(pacote_config.conteudo, data_referencia=contexto_execucao.data_referencia)
    pacote_planilha = carregar_planilha(
        pacote_config.conteudo,
        raiz_repositorio=pacote_config.raiz_repositorio,
        data_referencia=contexto_execucao.data_referencia,
    )
    validacao_pre_execucao_legada_shadow = validar_pre_execucao(
        pacote_config,
        contexto_execucao,
        pacote_planilha,
    )
    carteira_canonica = carregar_carteira_canonica(pacote_planilha, pacote_config.conteudo)
    dados_operacionais = carregar_dados_operacionais_canonicos(
        pacote_planilha,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
        carteira_canonica=carteira_canonica,
    )
    recebidos_auditaveis = materializar_recebidos_auditaveis(
        dados_operacionais,
        data_referencia=contexto_execucao.data_referencia,
    )
    cache_cdi = carregar_cache_cdi_diario(
        dados_operacionais,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
        raiz_repositorio=pacote_config.raiz_repositorio,
    )
    pacote_entrada_resolvida_shadow = montar_pacote_entrada_resolvida(
        pacote_config=pacote_config,
        contexto_execucao=contexto_execucao,
        pacote_planilha=pacote_planilha,
        pacote_cache_cdi=cache_cdi,
        metadados={
            'modo_shadow_contexto_baseline': True,
            'substitui_atributos_legados': False,
            'substitui_validacao_pre_execucao': True,
            'validacao_legada_preservada_shadow': True,
            'substitui_dados_operacionais_canonicos': False,
            'substitui_cache_cdi_operacional': False,
        },
    )
    auditoria_pacote_entrada_resolvida_shadow = auditar_pacote_entrada_resolvida(
        pacote_entrada_resolvida_shadow,
        exigir_cache_cdi=True,
    )
    validacao_pre_execucao = validar_pre_execucao_pacote_entrada_resolvida(
        pacote_entrada_resolvida_shadow,
    )
    validacao_pre_execucao_pacote_entrada_resolvida_shadow = validacao_pre_execucao
    if not validacao_pre_execucao.ok:
        detalhes = "\n - ".join(validacao_pre_execucao.erros_bloqueantes)
        raise RuntimeError(f"Validação pré-execução por PacoteEntradaResolvida reprovada:\n - {detalhes}")
    switching_shadow = carregar_switching_shadow_reconciliacao(dados_operacionais, carteira_canonica=carteira_canonica) if incluir_switching_shadow else None
    triagem_motor = carregar_triagem_motor(
        carteira_canonica,
        dados_operacionais,
        calendario_financeiro,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
    ) if incluir_triagem else None
    ranking_carteira = carregar_ranking_carteira_estabilizado(
        pacote_planilha,
        carteira_canonica,
        raiz_repositorio=pacote_config.raiz_repositorio,
        config=pacote_config.conteudo,
    )
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
    switching_economico_shadow = carregar_switching_economico_shadow(
        dados_operacionais,
        carteira_canonica,
        triagem_motor,
        replay_passado,
        calendario_financeiro,
        pacote_config.conteudo,
        ranking_carteira=ranking_carteira,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
    ) if incluir_switching_economico_shadow else None
    fontes_elegiveis_pagamento = materializar_fontes_elegiveis_pagamento(
        dados_operacionais,
        recebidos_auditaveis,
        replay_passado,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
        calendario_financeiro=calendario_financeiro,
        serie_cdi=cache_cdi.serie_cdi,
    )
    saldo_disponivel_geral = materializar_saldo_disponivel_geral(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        data_referencia=contexto_execucao.data_referencia,
        limiar_valor=obter_limiar_residuo_resolvido(pacote_config.conteudo),
    )
    decisao_local_v1 = materializar_decisao_local_v1(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        saldo_disponivel_geral,
        data_referencia=contexto_execucao.data_referencia,
        carteira_canonica=carteira_canonica,
    )
    auditoria_temporal_decisao_local = carregar_auditoria_temporal_decisao_local(
        decisao_local_v1,
        replay_passado,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
    ) if decisao_local_v1 is not None and replay_passado is not None else None
    reescolha_dinamica_pos_quebra = carregar_reescolha_dinamica_pos_quebra(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        saldo_disponivel_geral,
        decisao_local_v1,
        auditoria_temporal_decisao_local,
        replay_passado,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
        carteira_canonica=carteira_canonica,
        proxy_version='v3',
        calendario_financeiro=calendario_financeiro,
        serie_cdi=cache_cdi.serie_cdi,
    ) if decisao_local_v1 is not None and replay_passado is not None else None
    heuristica_conjunta_parcial_bloco_critico = carregar_heuristica_conjunta_parcial_bloco_critico(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        saldo_disponivel_geral,
        decisao_local_v1,
        replay_passado,
        auditoria_temporal_decisao_local,
        reescolha_dinamica_pos_quebra,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
        carteira_canonica=carteira_canonica,
        proxy_version='v3',
    ) if decisao_local_v1 is not None and replay_passado is not None else None
    planejamento_conjunto_local_bloco_critico_v1 = carregar_planejamento_conjunto_local_bloco_critico_v1(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        saldo_disponivel_geral,
        replay_passado,
        reescolha_dinamica_pos_quebra,
        heuristica_conjunta_parcial_bloco_critico,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
        carteira_canonica=carteira_canonica,
    ) if decisao_local_v1 is not None and replay_passado is not None else None
    recomputacao_sequencial_central_v1 = carregar_recomputacao_sequencial_central_v1(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        saldo_disponivel_geral,
        decisao_local_v1,
        replay_passado,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
        carteira_canonica=carteira_canonica,
        proxy_version='v3',
        calendario_financeiro=calendario_financeiro,
        serie_cdi=cache_cdi.serie_cdi,
    ) if decisao_local_v1 is not None and replay_passado is not None else None
    motor_recomendacao_pagamentos_switching_v1 = carregar_motor_recomendacao_pagamentos_switching_v1(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        saldo_disponivel_geral,
        decisao_local_v1,
        recomputacao_sequencial_central_v1,
        switching_economico_shadow,
        data_referencia=contexto_execucao.data_referencia,
    ) if decisao_local_v1 is not None and recomputacao_sequencial_central_v1 is not None and switching_economico_shadow is not None else None
    
    microplanejamento_conjunto_bloco_critico_v2 = carregar_microplanejamento_conjunto_bloco_critico_v2(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        saldo_disponivel_geral,
        replay_passado,
        heuristica_conjunta_parcial_bloco_critico,
        planejamento_conjunto_local_bloco_critico_v1,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
        carteira_canonica=carteira_canonica,
    ) if decisao_local_v1 is not None and replay_passado is not None and planejamento_conjunto_local_bloco_critico_v1 is not None else None
    resolver_hibrido_5p_shadow = carregar_resolver_hibrido_5p_shadow(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        decisao_local_v1,
        replay_passado,
        calendario_financeiro,
        cache_cdi,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
    ) if incluir_resolver_hibrido_5p_shadow else None
    benchmark_agrupado_individual_shadow = carregar_benchmark_agrupado_individual_shadow(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        decisao_local_v1,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
        carteira_canonica=carteira_canonica,
        proxy_version='v3',
    ) if incluir_benchmark_agrupado_individual_shadow else None
    benchmark_runner_futuro_shadow = carregar_benchmark_runner_futuro_shadow(
        dados_operacionais,
        replay_passado,
        calendario_financeiro,
        cache_cdi,
        decisao_local_v1,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
    ) if incluir_benchmark_runner_futuro_shadow else None
    auditoria_runner_futuro_shadow = carregar_auditoria_runner_futuro_shadow(
        benchmark_runner_futuro_shadow,
        data_referencia=contexto_execucao.data_referencia,
    ) if benchmark_runner_futuro_shadow is not None else None
    auditoria_primeira_quebra_runner_futuro_shadow = carregar_auditoria_primeira_quebra_runner_futuro_shadow(
        benchmark_runner_futuro_shadow,
        auditoria_runner_futuro_shadow,
        dados_operacionais,
        replay_passado,
        calendario_financeiro,
        cache_cdi,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
    ) if (incluir_auditoria_primeira_quebra_runner_futuro_shadow and benchmark_runner_futuro_shadow is not None) else None
    return ContextoBaseline(
        pacote_config=pacote_config,
        execucao=contexto_execucao,
        calendario_financeiro=calendario_financeiro,
        pacote_planilha=pacote_planilha,
        validacao_pre_execucao=validacao_pre_execucao,
        validacao_pre_execucao_legada_shadow=validacao_pre_execucao_legada_shadow,
        validacao_pre_execucao_pacote_entrada_resolvida_shadow=validacao_pre_execucao_pacote_entrada_resolvida_shadow,
        carteira_canonica=carteira_canonica,
        dados_operacionais=dados_operacionais,
        recebidos_auditaveis=recebidos_auditaveis,
        fontes_elegiveis_pagamento=fontes_elegiveis_pagamento,
        saldo_disponivel_geral=saldo_disponivel_geral,
        decisao_local_v1=decisao_local_v1,
        cache_cdi=cache_cdi,
        pacote_entrada_resolvida_shadow=pacote_entrada_resolvida_shadow,
        auditoria_pacote_entrada_resolvida_shadow=auditoria_pacote_entrada_resolvida_shadow,
        auditoria_temporal_decisao_local=auditoria_temporal_decisao_local,
        reescolha_dinamica_pos_quebra=reescolha_dinamica_pos_quebra,
        heuristica_conjunta_parcial_bloco_critico=heuristica_conjunta_parcial_bloco_critico,
        planejamento_conjunto_local_bloco_critico_v1=planejamento_conjunto_local_bloco_critico_v1,
        microplanejamento_conjunto_bloco_critico_v2=microplanejamento_conjunto_bloco_critico_v2,
        recomputacao_sequencial_central_v1=recomputacao_sequencial_central_v1,
        motor_recomendacao_pagamentos_switching_v1=motor_recomendacao_pagamentos_switching_v1,
        switching_shadow=switching_shadow,
        switching_economico_shadow=switching_economico_shadow,
        resolver_hibrido_5p_shadow=resolver_hibrido_5p_shadow,
        benchmark_agrupado_individual_shadow=benchmark_agrupado_individual_shadow,
        benchmark_runner_futuro_shadow=benchmark_runner_futuro_shadow,
        auditoria_runner_futuro_shadow=auditoria_runner_futuro_shadow,
        auditoria_primeira_quebra_runner_futuro_shadow=auditoria_primeira_quebra_runner_futuro_shadow,
        triagem_motor=triagem_motor,
        ranking_carteira=ranking_carteira,
        nucleo_financeiro=nucleo_financeiro,
        replay_passado=replay_passado,
        tabela_iof=construir_tabela_iof(pacote_config.conteudo),
        faixas_ir=construir_faixas_ir(pacote_config.conteudo),
    )