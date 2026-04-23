from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Any, Mapping
import json


CONFIG_FASE1 = Path(__file__).resolve().parents[3] / 'config' / 'modelos_script1_pagamentos_v140.json'


@dataclass(frozen=True, slots=True)
class ResultadoHeuristicasFase1:
    score_hibrido_5p_fonte: float
    penalidade_cliff_idade: float
    oportunidade_vpl_marginal: float
    score_auxiliar_script1: tuple[float, float, float]
    componentes_score: dict[str, float]
    justificativa: str
    metadados_modelo: dict[str, Any]

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safe_float(valor: Any, default: float = 0.0) -> float:
    try:
        if valor in (None, ''):
            return float(default)
        return float(valor)
    except Exception:
        return float(default)


_DEFAULTS = {
    'peso_deficit_rel': 4.0,
    'peso_custo_fiscal_rel': 1.5,
    'peso_perda_terminal_rel': 3.0,
    'peso_penalidade_liquidez_rel': 1.0,
    'peso_penalidade_estrategica_rel': 1.25,
    'peso_cliff_curto': 0.75,
    'peso_cliff_medio': 0.35,
    'peso_oportunidade_vpl_rel': 2.0,
    'janela_cliff_curta_dias': 15,
    'janela_cliff_media_dias': 30,
    'epsilon_empate_terminal': 5.0,
    'epsilon_empate_deficit': 1.0,
}


def carregar_parametros_fase1(config: Mapping[str, Any] | None = None) -> dict[str, float]:
    if isinstance(config, Mapping) and bool(config.get('desabilitar_modelos_script1_fase1')):
        params = dict(_DEFAULTS)
        for chave in list(params.keys()):
            params[chave] = 0.0
        return params
    params = dict(_DEFAULTS)
    if CONFIG_FASE1.exists():
        try:
            externo = json.loads(CONFIG_FASE1.read_text(encoding='utf-8'))
            bloco = externo.get('parametros_fase_1') if isinstance(externo, dict) else None
            if isinstance(bloco, dict):
                for chave, valor in bloco.items():
                    params[chave] = _safe_float(valor, params.get(chave, 0.0))
        except Exception:
            pass
    if isinstance(config, Mapping):
        bloco = config.get('modelos_script1_fase1') or config.get('parametros_modelos_script1_fase1') or {}
        if isinstance(bloco, Mapping):
            for chave, valor in bloco.items():
                params[chave] = _safe_float(valor, params.get(chave, 0.0))
    return params


def _proximo_cliff_idade(dias_idade: int) -> int | None:
    if dias_idade < 180:
        return 180
    if dias_idade < 360:
        return 360
    if dias_idade < 720:
        return 720
    return None


def _calcular_penalidade_cliff_idade(dias_idade: int, params: Mapping[str, float]) -> tuple[float, dict[str, Any]]:
    if dias_idade <= 0:
        return 0.0, {'distancia_cliff_dias': None, 'janela_cliff': 'na'}
    prox = _proximo_cliff_idade(dias_idade)
    if prox is None:
        return 0.0, {'distancia_cliff_dias': 999, 'janela_cliff': 'fora'}
    distancia = max(prox - dias_idade, 0)
    curta = int(params.get('janela_cliff_curta_dias', 15) or 15)
    media = int(params.get('janela_cliff_media_dias', 30) or 30)
    if distancia <= curta:
        base = params.get('peso_cliff_curto', 0.75)
        penalidade = base * (1.0 + (curta - distancia) / max(curta, 1))
        janela = 'curta'
    elif distancia <= media:
        base = params.get('peso_cliff_medio', 0.35)
        penalidade = base * (1.0 + (media - distancia) / max(media, 1))
        janela = 'media'
    else:
        penalidade = 0.0
        janela = 'fora'
    return round(float(penalidade), 6), {'distancia_cliff_dias': int(distancia), 'janela_cliff': janela}


def avaliar_heuristicas_fase1_por_fonte(
    *,
    tipo_fonte: str,
    valor_pagamento: float,
    valor_coberto: float,
    valor_deficit: float,
    custo_fiscal_imediato: float,
    perda_retorno_terminal_estimada: float,
    penalidade_liquidez_futura: float,
    penalidade_estrategica_lote: float,
    dias_horizonte: int,
    dias_idade_fonte: int = 0,
    proxy_terminal_fonte: float = 0.0,
    params: Mapping[str, float] | None = None,
) -> ResultadoHeuristicasFase1:
    params = dict(params or _DEFAULTS)
    base_pag = max(float(valor_pagamento), 1.0)
    base_coberto = max(float(valor_coberto), 1.0)

    deficit_rel = max(float(valor_deficit), 0.0) / base_pag
    custo_fiscal_rel = max(float(custo_fiscal_imediato), 0.0) / base_coberto
    perda_terminal_rel = max(float(perda_retorno_terminal_estimada), 0.0) / base_pag
    penalidade_liquidez_rel = max(float(penalidade_liquidez_futura), 0.0) / base_pag
    penalidade_estrategica_rel = max(float(penalidade_estrategica_lote), 0.0) / base_pag

    penalidade_cliff, meta_cliff = _calcular_penalidade_cliff_idade(int(dias_idade_fonte or 0), params)
    fator_tempo = max(int(dias_horizonte), 1) / 365.0
    oportunidade_vpl = max(float(valor_coberto), 0.0) * max(float(proxy_terminal_fonte), 0.0) * fator_tempo
    oportunidade_vpl_rel = oportunidade_vpl / base_pag

    score_hibrido = (
        deficit_rel * params.get('peso_deficit_rel', 4.0)
        + custo_fiscal_rel * params.get('peso_custo_fiscal_rel', 1.5)
        + perda_terminal_rel * params.get('peso_perda_terminal_rel', 3.0)
        + penalidade_liquidez_rel * params.get('peso_penalidade_liquidez_rel', 1.0)
        + penalidade_estrategica_rel * params.get('peso_penalidade_estrategica_rel', 1.25)
    )
    score_hibrido += penalidade_cliff
    score_hibrido += oportunidade_vpl_rel * params.get('peso_oportunidade_vpl_rel', 2.0)

    score_hibrido = round(float(score_hibrido), 6)
    oportunidade_vpl = round(float(oportunidade_vpl), 6)

    justificativa = (
        f"H1-H3 aplicadas à fonte `{tipo_fonte}` com score híbrido {score_hibrido:.6f}, "
        f"penalidade cliff {penalidade_cliff:.6f} e oportunidade VPL marginal {oportunidade_vpl:.6f}."
    )

    return ResultadoHeuristicasFase1(
        score_hibrido_5p_fonte=score_hibrido,
        penalidade_cliff_idade=round(float(penalidade_cliff), 6),
        oportunidade_vpl_marginal=oportunidade_vpl,
        score_auxiliar_script1=(
            score_hibrido,
            round(float(penalidade_cliff), 6),
            round(float(oportunidade_vpl), 6),
        ),
        componentes_score={
            'deficit_rel': round(deficit_rel, 6),
            'custo_fiscal_rel': round(custo_fiscal_rel, 6),
            'perda_terminal_rel': round(perda_terminal_rel, 6),
            'penalidade_liquidez_rel': round(penalidade_liquidez_rel, 6),
            'penalidade_estrategica_rel': round(penalidade_estrategica_rel, 6),
            'penalidade_cliff_idade': round(float(penalidade_cliff), 6),
            'oportunidade_vpl_rel': round(float(oportunidade_vpl_rel), 6),
        },
        justificativa=justificativa,
        metadados_modelo={
            'dias_horizonte': int(dias_horizonte),
            'dias_idade_fonte': int(dias_idade_fonte or 0),
            'proxy_terminal_fonte': round(float(proxy_terminal_fonte), 6),
            **meta_cliff,
        },
    )
