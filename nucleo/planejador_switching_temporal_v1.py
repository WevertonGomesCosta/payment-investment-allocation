from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from typing import Any


@dataclass(slots=True)
class AcaoSwitchingTemporalCandidata:
    """Representa uma ação temporal candidata de switching/aporte na V117+."""

    id_acao: str
    tipo_acao: str
    data_acao: str | None
    lote_origem_id: str | None
    produto_origem: str | None
    produto_destino: str | None
    valor_bruto_origem: float
    valor_liquido_resgatavel: float
    custo_fiscal_estimado: float
    perda_liquidez_estimada: float
    ganho_terminal_proxy_estimado: float
    impacto_pagamentos_futuros_estimado: float
    justificativa: str
    elegivel: bool
    proxy_terminal_origem: float = 0.0
    proxy_terminal_destino: float = 0.0
    produto_destino_key: str | None = None
    retorno_anual_destino: float = 0.0
    liquidez_dias_destino: int = 0
    carencia_dias_destino: int = 0
    valor_migrado_estimado: float = 0.0
    patrimonio_terminal_origem_estimado: float = 0.0
    patrimonio_terminal_destino_estimado: float = 0.0
    penalidade_carencia_reprojetada: float = 0.0
    ganho_terminal_economico_minimo_estimado: float = 0.0
    dias_carencia_incremental: int = 0
    retorno_anual_origem_estimado: float = 0.0
    score_ranqueamento_economico: float = 0.0
    rank_destino_sugerido: int = 0
    status_modelo: str = 'integral_multidestino_v127'

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


def _coerce_date(valor: Any) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, date):
        return valor
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor).date()
        except Exception:
            return None
    return None


def _normalizar_lote(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        return dict(item)
    dados: dict[str, Any] = {}
    for campo in (
        'id',
        'investimento',
        'produto_key',
        'valor_inicial',
        'principal_remanescente',
        'valor_liquido_resgatavel',
        'produto_destino_sugerido',
        'data_aplicacao',
        'carencia_ate',
        'proxy_terminal_atual',
        'retorno_anual_proxy_atual',
        'liquidez_dias_atual',
        'carencia_dias_atual',
        'taxa_base_cdi',
        'taxa_bonus_cdi',
    ):
        dados[campo] = getattr(item, campo, None)
    return dados


def _aliquota_ir_estimada(data_aplicacao: date | None, data_acao: date | None) -> float:
    if data_aplicacao is None or data_acao is None:
        return 0.15
    dias = max((data_acao - data_aplicacao).days, 0)
    if dias <= 180:
        return 0.225
    if dias <= 360:
        return 0.20
    if dias <= 720:
        return 0.175
    return 0.15


def _estimar_custo_fiscal(valor_liquido: float, principal: float, aliquota_ir: float) -> float:
    ganho_liquido = max(float(valor_liquido or 0.0) - float(principal or 0.0), 0.0)
    if ganho_liquido <= 0.0 or aliquota_ir <= 0.0 or aliquota_ir >= 1.0:
        return 0.0
    ganho_bruto = ganho_liquido / max(1.0 - aliquota_ir, 1e-9)
    imposto = ganho_bruto * aliquota_ir
    return round(max(imposto, 0.0), 2)


def _normalizar_proxy_terminal(valor: Any) -> float:
    try:
        numero = float(valor or 0.0)
    except Exception:
        return 0.0
    if numero > 1.0:
        numero = numero / 100.0
    return max(numero, 0.0)


def _normalizar_retorno_anual(valor: Any, taxa_base_cdi: Any, taxa_bonus_cdi: Any, cdi_anual_modelo: Any) -> float:
    taxa_ref = max(float(taxa_base_cdi or 0.0), float(taxa_bonus_cdi or 0.0))
    cdi = float(cdi_anual_modelo or 0.0)
    try:
        numero = float(valor or 0.0)
    except Exception:
        numero = 0.0
    if numero <= 0.0 and taxa_ref > 0.0 and cdi > 0.0:
        return round(taxa_ref * cdi, 6)
    if 0.0 < numero <= 1.0:
        numero *= 100.0
    if numero <= 0.0 and taxa_ref > 0.0 and cdi > 0.0:
        numero = taxa_ref * cdi
    return round(max(numero, 0.0), 6)


def _projetar_valor_terminal(valor_base: float, retorno_anual_pct: float, dias: int) -> float:
    valor = max(float(valor_base or 0.0), 0.0)
    retorno = max(float(retorno_anual_pct or 0.0), 0.0)
    dias = max(int(dias or 0), 0)
    if valor <= 0.0 or dias <= 0:
        return round(valor, 2)
    fator = (1.0 + retorno / 100.0) ** (dias / 365.0)
    return round(valor * fator, 2)


def _somar_pagamentos_em_janela(pagamentos: list[dict[str, Any]], data_inicio_exclusiva: date, data_fim_inclusiva: date) -> tuple[float, float, int]:
    total = 0.0
    protegidos = 0.0
    quantidade = 0
    for pagamento in pagamentos:
        data_pag = _coerce_date(pagamento.get('data'))
        if data_pag is None or data_pag <= data_inicio_exclusiva or data_pag > data_fim_inclusiva:
            continue
        valor = round(float(pagamento.get('valor') or 0.0), 2)
        if valor <= 0.0:
            continue
        total += valor
        quantidade += 1
        if str(pagamento.get('classe_pagamento') or '').upper() == 'PROTEGIDA':
            protegidos += valor
    return round(total, 2), round(protegidos, 2), quantidade


def planejar_switching_temporal_v1(
    estado_global: dict[str, Any] | None,
    config: dict[str, Any] | None,
    horizonte_planejamento: Any = None,
    filtros_eventos: dict[str, Any] | None = None,
    limite_candidatos_por_data: int | None = None,
) -> dict[str, Any]:
    """Gera candidatos temporais auditáveis para o recorte curto da V121.

    Nesta expansão, o planejador compara múltiplos destinos elegíveis por lote e
    ranqueia cada candidato pelo ganho terminal econômico mínimo real estimado,
    incorporando custo fiscal do resgate, patrimônio terminal reprojetado da
    origem e do destino, e penalidade incremental de carência/liquidez.
    """

    estado = dict(estado_global or {})
    filtros = dict(filtros_eventos or {})
    data_inicio = _coerce_date(estado.get('data_evento_corrente') or estado.get('data_referencia'))
    data_fim = _coerce_date(
        (horizonte_planejamento or {}).get('data_fim') if isinstance(horizonte_planejamento, dict) else None
    ) or _coerce_date(estado.get('data_fim_recorte')) or data_inicio
    data_inicio_str = data_inicio.isoformat() if data_inicio else ''
    produto_destino_padrao = dict(estado.get('produto_destino_padrao') or {})
    destinos_brutos = list(estado.get('produtos_destino_elegiveis') or [])
    if not destinos_brutos and produto_destino_padrao:
        destinos_brutos = [produto_destino_padrao]
    cdi_anual_modelo = float(estado.get('cdi_anual_modelo') or 0.0)
    pagamentos_futuros = list(estado.get('pagamentos_futuros') or [])

    candidatos: list[AcaoSwitchingTemporalCandidata] = [
        AcaoSwitchingTemporalCandidata(
            id_acao='manter_estado_atual',
            tipo_acao='manter',
            data_acao=data_inicio_str,
            lote_origem_id=None,
            produto_origem=None,
            produto_destino=None,
            valor_bruto_origem=0.0,
            valor_liquido_resgatavel=0.0,
            custo_fiscal_estimado=0.0,
            perda_liquidez_estimada=0.0,
            ganho_terminal_proxy_estimado=0.0,
            impacto_pagamentos_futuros_estimado=0.0,
            justificativa='Ação neutra obrigatória para benchmark interno do recorte curto.',
            elegivel=True,
        )
    ]

    lotes = estado.get('lotes_aportados') or []
    registros_candidatos: list[AcaoSwitchingTemporalCandidata] = []
    for indice, bruto in enumerate(lotes, start=1):
        lote = _normalizar_lote(bruto)
        valor_liquido = float(lote.get('valor_liquido_resgatavel') or lote.get('principal_remanescente') or 0.0)
        if valor_liquido <= 0.0:
            continue
        data_carencia_origem = _coerce_date(lote.get('carencia_ate'))
        data_acao = max([x for x in (data_inicio, data_carencia_origem) if x is not None], default=data_inicio)
        if data_acao is None:
            continue
        dias_restantes = max(((data_fim or data_acao) - data_acao).days, 0)
        principal = float(lote.get('principal_remanescente') or 0.0)
        data_aplicacao = _coerce_date(lote.get('data_aplicacao'))
        aliquota_ir = _aliquota_ir_estimada(data_aplicacao, data_acao)
        custo_fiscal = _estimar_custo_fiscal(valor_liquido, principal, aliquota_ir)
        valor_migrado = round(max(valor_liquido - custo_fiscal, 0.0), 2)
        if valor_migrado <= 0.0:
            continue

        proxy_origem = _normalizar_proxy_terminal(lote.get('proxy_terminal_atual'))
        retorno_anual_origem = _normalizar_retorno_anual(
            lote.get('retorno_anual_proxy_atual'),
            lote.get('taxa_base_cdi'),
            lote.get('taxa_bonus_cdi'),
            cdi_anual_modelo,
        )
        patrimonio_terminal_origem = _projetar_valor_terminal(valor_liquido, retorno_anual_origem, dias_restantes)
        liquidez_dias_origem = int(lote.get('liquidez_dias_atual') or 0)
        data_disponibilidade_origem = max(
            data_acao,
            (data_carencia_origem or data_acao),
            data_acao + timedelta(days=max(liquidez_dias_origem, 0)),
        )
        produto_origem_key = str(lote.get('produto_key') or '')

        for rank_destino, destino_bruto in enumerate(destinos_brutos, start=1):
            produto_destino = dict(destino_bruto or {})
            produto_destino_nome = str(produto_destino.get('nome') or filtros.get('produto_destino_padrao') or '')
            produto_destino_key = str(produto_destino.get('produto_key') or '')
            if produto_destino_key and produto_destino_key == produto_origem_key:
                continue

            proxy_destino = _normalizar_proxy_terminal(produto_destino.get('proxy_terminal_destino') or produto_destino.get('score_final'))
            retorno_anual_destino = _normalizar_retorno_anual(
                produto_destino.get('retorno_anual_proxy'),
                produto_destino.get('taxa_base_cdi'),
                produto_destino.get('taxa_bonus_cdi'),
                cdi_anual_modelo,
            )
            liquidez_dias_destino = int(produto_destino.get('liquidez_dias') or 0)
            carencia_dias_destino = int(produto_destino.get('carencia_dias') or 0)
            patrimonio_terminal_destino = _projetar_valor_terminal(valor_migrado, retorno_anual_destino, dias_restantes)
            data_disponibilidade_destino = max(
                data_acao,
                data_acao + timedelta(days=max(liquidez_dias_destino, 0)),
                data_acao + timedelta(days=max(carencia_dias_destino, 0)),
            )
            dias_carencia_incremental = max((data_disponibilidade_destino - data_disponibilidade_origem).days, 0)
            total_pag_janela = 0.0
            total_protegido_janela = 0.0
            if dias_carencia_incremental > 0:
                total_pag_janela, total_protegido_janela, _ = _somar_pagamentos_em_janela(
                    pagamentos_futuros,
                    data_disponibilidade_origem,
                    min(data_disponibilidade_destino, data_fim or data_disponibilidade_destino),
                )
            penalidade_carencia = round(
                min(valor_migrado, total_pag_janela) * 0.10 + min(valor_migrado, total_protegido_janela) * 0.15,
                2,
            )
            ganho_proxy = max(proxy_destino - proxy_origem, 0.0) * valor_migrado * (dias_restantes / 365.0)
            ganho_terminal_economico = round(
                patrimonio_terminal_destino - patrimonio_terminal_origem - penalidade_carencia,
                2,
            )
            elegivel = (
                bool(produto_destino_nome)
                and (data_fim is None or data_acao <= data_fim)
                and ganho_terminal_economico > 0.0
            )
            justificativa = (
                f"Switching temporal multidestino: data={data_acao.isoformat()}, destino={produto_destino_nome}, "
                f"terminal_origem={patrimonio_terminal_origem:.2f}, terminal_destino={patrimonio_terminal_destino:.2f}, "
                f"custo_fiscal={custo_fiscal:.2f}, penalidade_carencia={penalidade_carencia:.2f}, ganho_economico={ganho_terminal_economico:.2f}."
            )
            registros_candidatos.append(
                AcaoSwitchingTemporalCandidata(
                    id_acao=f'switching_candidato_{indice}_{rank_destino}',
                    tipo_acao='switching_simples',
                    data_acao=data_acao.isoformat(),
                    lote_origem_id=str(lote.get('id') or f'lote_{indice}'),
                    produto_origem=str(lote.get('investimento') or ''),
                    produto_destino=produto_destino_nome,
                    valor_bruto_origem=float(lote.get('valor_inicial') or valor_liquido),
                    valor_liquido_resgatavel=valor_liquido,
                    custo_fiscal_estimado=round(custo_fiscal, 2),
                    perda_liquidez_estimada=round(penalidade_carencia, 2),
                    ganho_terminal_proxy_estimado=round(ganho_proxy, 2),
                    impacto_pagamentos_futuros_estimado=round(total_pag_janela, 2),
                    justificativa=justificativa,
                    elegivel=elegivel,
                    proxy_terminal_origem=round(proxy_origem, 6),
                    proxy_terminal_destino=round(proxy_destino, 6),
                    produto_destino_key=produto_destino_key or None,
                    retorno_anual_destino=round(retorno_anual_destino, 6),
                    liquidez_dias_destino=liquidez_dias_destino,
                    carencia_dias_destino=carencia_dias_destino,
                    valor_migrado_estimado=valor_migrado,
                    patrimonio_terminal_origem_estimado=patrimonio_terminal_origem,
                    patrimonio_terminal_destino_estimado=patrimonio_terminal_destino,
                    penalidade_carencia_reprojetada=penalidade_carencia,
                    ganho_terminal_economico_minimo_estimado=ganho_terminal_economico,
                    dias_carencia_incremental=dias_carencia_incremental,
                    retorno_anual_origem_estimado=retorno_anual_origem,
                    score_ranqueamento_economico=ganho_terminal_economico,
                    rank_destino_sugerido=int(produto_destino.get('rank_destino') or rank_destino),
                    status_modelo='integral_multidestino_v127',
                )
            )

    recebidos_disponiveis = list(estado.get('recebidos_nao_aportados_disponiveis') or [])
    for indice_recebido, recebido in enumerate(recebidos_disponiveis, start=1):
        valor_disponivel = round(float(recebido.get('valor_disponivel') or recebido.get('valor') or 0.0), 2)
        if valor_disponivel <= 0.0:
            continue
        data_acao = data_inicio
        if data_acao is None:
            continue
        dias_restantes = max(((data_fim or data_acao) - data_acao).days, 0)
        patrimonio_terminal_origem = round(valor_disponivel, 2)
        data_disponibilidade_origem = data_acao
        for rank_destino, destino_bruto in enumerate(destinos_brutos, start=1):
            produto_destino = dict(destino_bruto or {})
            produto_destino_nome = str(produto_destino.get('nome') or filtros.get('produto_destino_padrao') or '')
            produto_destino_key = str(produto_destino.get('produto_key') or '')
            retorno_anual_destino = _normalizar_retorno_anual(
                produto_destino.get('retorno_anual_proxy'),
                produto_destino.get('taxa_base_cdi'),
                produto_destino.get('taxa_bonus_cdi'),
                cdi_anual_modelo,
            )
            liquidez_dias_destino = int(produto_destino.get('liquidez_dias') or 0)
            carencia_dias_destino = int(produto_destino.get('carencia_dias') or 0)
            patrimonio_terminal_destino = _projetar_valor_terminal(valor_disponivel, retorno_anual_destino, dias_restantes)
            data_disponibilidade_destino = max(
                data_acao,
                data_acao + timedelta(days=max(liquidez_dias_destino, 0)),
                data_acao + timedelta(days=max(carencia_dias_destino, 0)),
            )
            dias_carencia_incremental = max((data_disponibilidade_destino - data_disponibilidade_origem).days, 0)
            total_pag_janela = 0.0
            total_protegido_janela = 0.0
            if dias_carencia_incremental > 0:
                total_pag_janela, total_protegido_janela, _ = _somar_pagamentos_em_janela(
                    pagamentos_futuros,
                    data_disponibilidade_origem,
                    min(data_disponibilidade_destino, data_fim or data_disponibilidade_destino),
                )
            penalidade_carencia = round(
                min(valor_disponivel, total_pag_janela) * 0.10 + min(valor_disponivel, total_protegido_janela) * 0.15,
                2,
            )
            ganho_proxy = max(_normalizar_proxy_terminal(produto_destino.get('proxy_terminal_destino') or produto_destino.get('score_final')), 0.0) * valor_disponivel * (dias_restantes / 365.0)
            ganho_terminal_economico = round(
                patrimonio_terminal_destino - patrimonio_terminal_origem - penalidade_carencia,
                2,
            )
            elegivel = bool(produto_destino_nome) and (data_fim is None or data_acao <= data_fim) and ganho_terminal_economico > 0.0
            justificativa = (
                f"Aporte temporal de não aportado: data={data_acao.isoformat()}, destino={produto_destino_nome}, "
                f"terminal_origem={patrimonio_terminal_origem:.2f}, terminal_destino={patrimonio_terminal_destino:.2f}, "
                f"penalidade_carencia={penalidade_carencia:.2f}, ganho_economico={ganho_terminal_economico:.2f}."
            )
            registros_candidatos.append(
                AcaoSwitchingTemporalCandidata(
                    id_acao=f'aporte_nao_aportado_{indice_recebido}_{rank_destino}',
                    tipo_acao='aporte_nao_aportado',
                    data_acao=data_acao.isoformat(),
                    lote_origem_id=str(recebido.get('id') or f'recebido_{indice_recebido}'),
                    produto_origem='NAO_APORTADO_DISPONIVEL',
                    produto_destino=produto_destino_nome,
                    valor_bruto_origem=valor_disponivel,
                    valor_liquido_resgatavel=valor_disponivel,
                    custo_fiscal_estimado=0.0,
                    perda_liquidez_estimada=round(penalidade_carencia, 2),
                    ganho_terminal_proxy_estimado=round(ganho_proxy, 2),
                    impacto_pagamentos_futuros_estimado=round(total_pag_janela, 2),
                    justificativa=justificativa,
                    elegivel=elegivel,
                    proxy_terminal_origem=0.0,
                    proxy_terminal_destino=round(_normalizar_proxy_terminal(produto_destino.get('proxy_terminal_destino') or produto_destino.get('score_final')), 6),
                    produto_destino_key=produto_destino_key or None,
                    retorno_anual_destino=round(retorno_anual_destino, 6),
                    liquidez_dias_destino=liquidez_dias_destino,
                    carencia_dias_destino=carencia_dias_destino,
                    valor_migrado_estimado=valor_disponivel,
                    patrimonio_terminal_origem_estimado=patrimonio_terminal_origem,
                    patrimonio_terminal_destino_estimado=patrimonio_terminal_destino,
                    penalidade_carencia_reprojetada=penalidade_carencia,
                    ganho_terminal_economico_minimo_estimado=ganho_terminal_economico,
                    dias_carencia_incremental=dias_carencia_incremental,
                    retorno_anual_origem_estimado=0.0,
                    score_ranqueamento_economico=ganho_terminal_economico,
                    rank_destino_sugerido=int(produto_destino.get('rank_destino') or rank_destino),
                    status_modelo='integral_multidestino_v127',
                )
            )


    registros_candidatos.sort(
        key=lambda item: (
            not item.elegivel,
            item.data_acao or '',
            -float(item.score_ranqueamento_economico or 0.0),
            -float(item.patrimonio_terminal_destino_estimado or 0.0),
            item.lote_origem_id or '',
            int(item.rank_destino_sugerido or 0),
        )
    )
    limite = None if limite_candidatos_por_data is None else max(limite_candidatos_por_data, 0)
    if limite is not None:
        registros_candidatos = registros_candidatos[:limite]
    candidatos.extend(registros_candidatos)

    return {
        'status': 'integral_multidestino_v127',
        'implementado': True,
        'horizonte_planejamento': horizonte_planejamento,
        'limite_candidatos_por_data': limite_candidatos_por_data,
        'filtros_eventos': filtros,
        'quantidade_candidatos': len(candidatos),
        'quantidade_candidatos_elegiveis_switching': sum(1 for x in registros_candidatos if x.elegivel),
        'quantidade_destinos_elegiveis_considerados': len(destinos_brutos),
        'acoes_candidatas': [item.para_dict() for item in candidatos],
        'config_resumido': dict(config or {}),
        'produto_destino_padrao': produto_destino_padrao,
        'criterio_ranqueamento': 'ganho_terminal_economico_minimo_estimado',
        'escopo_fontes': 'lotes_aportados_e_nao_aportados_disponiveis',
    }
