from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
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
    status_modelo: str = 'integracao_minima_v118'

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
        'valor_inicial',
        'principal_remanescente',
        'valor_liquido_resgatavel',
        'produto_destino_sugerido',
        'data_aplicacao',
        'carencia_ate',
        'proxy_terminal_atual',
    ):
        dados[campo] = getattr(item, campo, None)
    return dados


def _normalizar_proxy_terminal(valor: Any) -> float:
    try:
        numero = float(valor or 0.0)
    except Exception:
        return 0.0
    if numero > 1.0:
        numero = numero / 100.0
    return max(numero, 0.0)


def planejar_switching_temporal_v1(
    estado_global: dict[str, Any] | None,
    config: dict[str, Any] | None,
    horizonte_planejamento: Any = None,
    filtros_eventos: dict[str, Any] | None = None,
    limite_candidatos_por_data: int | None = None,
) -> dict[str, Any]:
    """Gera candidatos temporais auditáveis para o recorte curto da V118.

    Nesta integração mínima, o planejador continua conservador, mas deixa de ser
    meramente documental: ele propõe datas de switching independentes da conta e
    calcula um ganho terminal proxy simples com base na diferença entre proxies
    terminais origem/destino no horizonte remanescente do recorte.
    """

    estado = dict(estado_global or {})
    filtros = dict(filtros_eventos or {})
    data_inicio = _coerce_date(estado.get('data_evento_corrente') or estado.get('data_referencia'))
    data_fim = _coerce_date(
        (horizonte_planejamento or {}).get('data_fim') if isinstance(horizonte_planejamento, dict) else None
    ) or _coerce_date(estado.get('data_fim_recorte')) or data_inicio
    data_inicio_str = data_inicio.isoformat() if data_inicio else ''
    produto_destino = dict(estado.get('produto_destino_padrao') or {})
    produto_destino_nome = str(produto_destino.get('nome') or filtros.get('produto_destino_padrao') or '')
    proxy_destino = _normalizar_proxy_terminal(produto_destino.get('proxy_terminal_destino') or produto_destino.get('score_final'))

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
        data_carencia = _coerce_date(lote.get('carencia_ate'))
        data_acao = max([x for x in (data_inicio, data_carencia) if x is not None], default=data_inicio)
        if data_acao is None:
            continue
        dias_restantes = max(((data_fim or data_acao) - data_acao).days, 0)
        proxy_origem = _normalizar_proxy_terminal(lote.get('proxy_terminal_atual'))
        ganho_proxy = max(proxy_destino - proxy_origem, 0.0) * valor_liquido * (dias_restantes / 365.0)
        perda_liquidez = 0.15 * valor_liquido if data_carencia and data_inicio and data_carencia > data_inicio else 0.0
        impacto_pagamentos = 0.0 if data_carencia is None or data_carencia <= data_acao else valor_liquido
        elegivel = bool(produto_destino_nome) and (data_fim is None or data_acao <= data_fim)
        justificativa = (
            f"Switching temporal candidato no recorte curto: data ótima mínima = {data_acao.isoformat()}, "
            f"proxy_origem={proxy_origem:.4f}, proxy_destino={proxy_destino:.4f}, dias_restantes={dias_restantes}."
        )
        registros_candidatos.append(
            AcaoSwitchingTemporalCandidata(
                id_acao=f'switching_candidato_{indice}',
                tipo_acao='switching_simples',
                data_acao=data_acao.isoformat(),
                lote_origem_id=str(lote.get('id') or f'lote_{indice}'),
                produto_origem=str(lote.get('investimento') or ''),
                produto_destino=produto_destino_nome,
                valor_bruto_origem=float(lote.get('valor_inicial') or valor_liquido),
                valor_liquido_resgatavel=valor_liquido,
                custo_fiscal_estimado=0.0,
                perda_liquidez_estimada=round(perda_liquidez, 2),
                ganho_terminal_proxy_estimado=round(ganho_proxy, 2),
                impacto_pagamentos_futuros_estimado=round(impacto_pagamentos, 2),
                justificativa=justificativa,
                elegivel=elegivel,
                proxy_terminal_origem=round(proxy_origem, 6),
                proxy_terminal_destino=round(proxy_destino, 6),
            )
        )

    registros_candidatos.sort(
        key=lambda item: (
            not item.elegivel,
            item.data_acao or '',
            -float(item.ganho_terminal_proxy_estimado or 0.0),
            item.lote_origem_id or '',
        )
    )
    limite = None if limite_candidatos_por_data is None else max(limite_candidatos_por_data, 0)
    if limite is not None:
        registros_candidatos = registros_candidatos[:limite]
    candidatos.extend(registros_candidatos)

    return {
        'status': 'integracao_minima_v118',
        'implementado': True,
        'horizonte_planejamento': horizonte_planejamento,
        'limite_candidatos_por_data': limite_candidatos_por_data,
        'filtros_eventos': filtros,
        'quantidade_candidatos': len(candidatos),
        'acoes_candidatas': [item.para_dict() for item in candidatos],
        'config_resumido': dict(config or {}),
        'produto_destino_padrao': produto_destino,
    }
