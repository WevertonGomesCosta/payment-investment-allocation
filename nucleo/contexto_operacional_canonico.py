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
from nucleo.entrada_resolvida import AuditoriaPacoteEntradaResolvida, PacoteEntradaResolvida, auditar_pacote_entrada_resolvida, montar_pacote_entrada_resolvida
from nucleo.leitor_planilha import PacotePlanilha, carregar_planilha
from nucleo.nucleo_financeiro_minimo import construir_faixas_ir, construir_tabela_iof, carregar_nucleo_financeiro_minimo
from nucleo.replay_passado_controlado import carregar_replay_passado_controlado
from nucleo.ranking_carteira_estabilizado import carregar_ranking_carteira_estabilizado
from nucleo.config_utils import obter_config
from nucleo.validacao_pre_execucao import PacoteValidacaoPreExecucao, validar_pre_execucao_pacote_entrada_resolvida
from nucleo.caixa_recebidos_auditaveis import materializar_fontes_elegiveis_pagamento, materializar_recebidos_auditaveis, materializar_saldo_disponivel_geral

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


@dataclass(slots=True)
class ContextoOperacionalCanonico:
    pacote_config: PacoteConfig
    execucao: ContextoExecucao
    calendario_financeiro: Any
    pacote_planilha: PacotePlanilha
    pacote_entrada_resolvida: PacoteEntradaResolvida
    auditoria_pacote_entrada_resolvida: AuditoriaPacoteEntradaResolvida
    validacao_pre_execucao: PacoteValidacaoPreExecucao
    carteira_canonica: Any
    dados_operacionais: Any
    recebidos_auditaveis: Any
    fontes_elegiveis_pagamento: Any
    saldo_disponivel_geral: Any
    cache_cdi: PacoteCacheCDIDiario
    nucleo_financeiro: Any
    replay_passado: Any
    ranking_carteira: Any
    tabela_iof: list[float]
    faixas_ir: list[dict[str, Any]]
    metadados: dict[str, Any]


def carregar_contexto_operacional_canonico(
    *,
    raiz_repositorio: Path | None = None,
    instalar_automaticamente: bool = False,
    incluir_replay: bool = True,
) -> ContextoOperacionalCanonico:
    pacote_config = carregar_config(raiz_repositorio=raiz_repositorio)
    contexto_execucao = bootstrap_ambiente(
        pacote_config.conteudo,
        grupos_extras=['financeiro'],
        instalar_automaticamente=instalar_automaticamente,
    )
    calendario_financeiro = construir_calendario_financeiro(
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
    )
    pacote_planilha = carregar_planilha(
        pacote_config.conteudo,
        raiz_repositorio=pacote_config.raiz_repositorio,
        data_referencia=contexto_execucao.data_referencia,
    )
    carteira_canonica = carregar_carteira_canonica(pacote_planilha, pacote_config.conteudo)

    cache_cdi = carregar_cache_cdi_diario(
        None,
        pacote_config.conteudo,
        data_referencia=contexto_execucao.data_referencia,
        raiz_repositorio=pacote_config.raiz_repositorio,
        janela_consulta_cdi=getattr(pacote_planilha, 'janela_consulta_cdi', None),
    )
    pacote_entrada_resolvida = montar_pacote_entrada_resolvida(
        pacote_config=pacote_config,
        contexto_execucao=contexto_execucao,
        pacote_planilha=pacote_planilha,
        pacote_cache_cdi=cache_cdi,
        metadados={
            'artefato_operacional_contexto_canonico': True,
            'modo_operacional_canonico': True,
            'integra_validacao_pre_execucao': True,
            'substitui_validacao_pre_execucao': False,
            'substitui_dados_operacionais_canonicos': False,
            'substitui_cache_cdi_operacional': False,
            'ordem_contratual_etapas_1_2_3_preservada': True,
            'altera_motor': False,
            'altera_replay': False,
            'altera_ledger': False,
            'altera_ranking': False,
            'altera_saida_xlsx': False,
        },
    )
    auditoria_pacote_entrada_resolvida = auditar_pacote_entrada_resolvida(
        pacote_entrada_resolvida,
        exigir_cache_cdi=True,
    )
    validacao_pre_execucao = validar_pre_execucao_pacote_entrada_resolvida(
        pacote_entrada_resolvida,
    )
    if not validacao_pre_execucao.ok:
        detalhes = "\n - ".join(validacao_pre_execucao.erros_bloqueantes)
        raise RuntimeError(f"Validação pré-execução por PacoteEntradaResolvida reprovada:\n - {detalhes}")

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
    ranking_carteira = carregar_ranking_carteira_estabilizado(
        pacote_planilha,
        carteira_canonica,
        raiz_repositorio=pacote_config.raiz_repositorio,
        config=pacote_config.conteudo,
    )
    tabela_iof = construir_tabela_iof(pacote_config.conteudo)
    faixas_ir = construir_faixas_ir(pacote_config.conteudo)
    fontes_elegiveis_pagamento = materializar_fontes_elegiveis_pagamento(
        dados_operacionais,
        recebidos_auditaveis,
        replay_passado,
        data_referencia=contexto_execucao.data_referencia,
        tabela_iof=tabela_iof,
        faixas_ir=faixas_ir,
        calendario_financeiro=calendario_financeiro,
        serie_cdi=cache_cdi.serie_cdi,
    )
    saldo_disponivel_geral = materializar_saldo_disponivel_geral(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        data_referencia=contexto_execucao.data_referencia,
        limiar_valor=obter_limiar_residuo_resolvido(pacote_config.conteudo),
    )
    return ContextoOperacionalCanonico(
        pacote_config=pacote_config,
        execucao=contexto_execucao,
        calendario_financeiro=calendario_financeiro,
        pacote_planilha=pacote_planilha,
        pacote_entrada_resolvida=pacote_entrada_resolvida,
        auditoria_pacote_entrada_resolvida=auditoria_pacote_entrada_resolvida,
        validacao_pre_execucao=validacao_pre_execucao,
        carteira_canonica=carteira_canonica,
        dados_operacionais=dados_operacionais,
        recebidos_auditaveis=recebidos_auditaveis,
        fontes_elegiveis_pagamento=fontes_elegiveis_pagamento,
        saldo_disponivel_geral=saldo_disponivel_geral,
        cache_cdi=cache_cdi,
        nucleo_financeiro=nucleo_financeiro,
        replay_passado=replay_passado,
        ranking_carteira=ranking_carteira,
        tabela_iof=tabela_iof,
        faixas_ir=faixas_ir,
        metadados={
            'artefato': 'ContextoOperacionalCanonico',
            'microetapa': 'MICRO-RUNTIME-02',
            'ordem_contratual_etapas_1_2_3_preservada': True,
            'altera_contexto_baseline_historico': False,
            'altera_motor': False,
            'altera_replay': False,
            'altera_ledger': False,
            'altera_ranking': False,
            'altera_saida_xlsx': False,
        },
    )