from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class AcaoSwitchingTemporalCandidata:
    """Representa uma ação temporal candidata de switching/aporte na V117.

    Este módulo é um esqueleto executável. Ele não substitui o motor econômico
    central vigente; apenas formaliza o contrato mínimo necessário para a V117.
    """

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
    status_modelo: str = 'esqueleto_v117'

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalizar_lote(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        return item
    dados: dict[str, Any] = {}
    for campo in (
        'id',
        'investimento',
        'valor_inicial',
        'principal_remanescente',
        'produto_destino_sugerido',
        'data_aplicacao',
    ):
        dados[campo] = getattr(item, campo, None)
    return dados


def planejar_switching_temporal_v1(
    estado_global: dict[str, Any] | None,
    config: dict[str, Any] | None,
    horizonte_planejamento: Any = None,
    filtros_eventos: dict[str, Any] | None = None,
    limite_candidatos_por_data: int | None = None,
) -> dict[str, Any]:
    """Gera uma coleção mínima e auditável de ações temporais candidatas.

    A implementação desta versão é propositalmente conservadora: produz uma
    ação explícita de manutenção e, quando houver lotes na estrutura de entrada,
    registra candidatos descritivos de switching sem promover qualquer decisão.
    """

    estado = dict(estado_global or {})
    filtros = dict(filtros_eventos or {})
    candidatos: list[AcaoSwitchingTemporalCandidata] = [
        AcaoSwitchingTemporalCandidata(
            id_acao='manter_estado_atual',
            tipo_acao='manter',
            data_acao=str(estado.get('data_evento_corrente') or estado.get('data_referencia') or ''),
            lote_origem_id=None,
            produto_origem=None,
            produto_destino=None,
            valor_bruto_origem=0.0,
            valor_liquido_resgatavel=0.0,
            custo_fiscal_estimado=0.0,
            perda_liquidez_estimada=0.0,
            ganho_terminal_proxy_estimado=0.0,
            impacto_pagamentos_futuros_estimado=0.0,
            justificativa='Ação neutra obrigatória do esqueleto V117 para comparação contratual.',
            elegivel=True,
        )
    ]

    lotes = estado.get('lotes_aportados') or []
    data_base = str(estado.get('data_evento_corrente') or estado.get('data_referencia') or '')
    for indice, bruto in enumerate(lotes, start=1):
        if limite_candidatos_por_data is not None and len(candidatos) - 1 >= max(limite_candidatos_por_data, 0):
            break
        lote = _normalizar_lote(bruto)
        candidatos.append(
            AcaoSwitchingTemporalCandidata(
                id_acao=f'switching_candidato_{indice}',
                tipo_acao='switching_simples',
                data_acao=data_base,
                lote_origem_id=str(lote.get('id') or f'lote_{indice}'),
                produto_origem=str(lote.get('investimento') or ''),
                produto_destino=str(lote.get('produto_destino_sugerido') or filtros.get('produto_destino_padrao') or ''),
                valor_bruto_origem=float(lote.get('valor_inicial') or lote.get('principal_remanescente') or 0.0),
                valor_liquido_resgatavel=float(lote.get('principal_remanescente') or 0.0),
                custo_fiscal_estimado=0.0,
                perda_liquidez_estimada=0.0,
                ganho_terminal_proxy_estimado=0.0,
                impacto_pagamentos_futuros_estimado=0.0,
                justificativa='Candidato estrutural da V117. Não implica recomendação econômica final.',
                elegivel=True,
            )
        )

    return {
        'status': 'esqueleto_v117',
        'implementado': False,
        'horizonte_planejamento': horizonte_planejamento,
        'limite_candidatos_por_data': limite_candidatos_por_data,
        'filtros_eventos': filtros,
        'quantidade_candidatos': len(candidatos),
        'acoes_candidatas': [item.para_dict() for item in candidatos],
        'config_resumido': dict(config or {}),
    }
