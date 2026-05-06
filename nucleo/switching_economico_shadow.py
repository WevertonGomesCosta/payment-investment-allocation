"""Camada shadow de switching econômico legado.

Esta etapa absorve, de forma isolada e auditável, a lógica material do legado
relativa a **switching econômico de lotes já aportados**, sem substituir o
fluxo principal nem acoplar a decisão ao replay/runner atual.

Escopo desta etapa:
- avaliar lotes ativos pós-replay como candidatos a switching econômico;
- comparar manter o lote atual vs. resgatar hoje e reaplicar em produto destino;
- projetar riqueza líquida no horizonte-base com taxa-modelo futura;
- materializar ranking por lote, melhor oportunidade e plano shadow;
- registrar bloqueios auditáveis (mínimo, máximo, carência, mesmo produto etc.).

Fora do escopo desta etapa:
- executar switching no fluxo principal;
- combinar switches com pagamento/saldo disponível;
- otimização conjunta de portfólio;
- solver/multifonte;
- exportação pesada do legado.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Mapping

import pandas as pd

from nucleo.calendario_financeiro import PacoteCalendarioFinanceiro, obter_taxa_dia_rendimento_lote
from nucleo.carteira_canonica import PacoteCarteiraCanonica
from nucleo.config_utils import obter_config
from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.helpers_shadow_compartilhados import simular_lote_ate_data_shadow
from nucleo.nucleo_financeiro_minimo import Lote, PacoteNucleoFinanceiroMinimo, criar_lote_de_aporte
from nucleo.replay_passado_controlado import PacoteReplayPassadoControlado
from nucleo.triagem_motor import PacoteTriagemMotor
from nucleo.utilitarios_neutros import arredondar_monetario, limpar_texto, normalizar_texto, para_float_monetario, para_int


@dataclass(slots=True)
class PacoteSwitchingEconomicoShadow:
    quadro_oportunidades: pd.DataFrame
    quadro_melhores_oportunidades: pd.DataFrame
    plano_shadow: pd.DataFrame
    auditoria: dict[str, Any]
    validacao: dict[str, Any]




def _produto_meta_por_key(carteira_canonica: PacoteCarteiraCanonica, produto_key: Any) -> dict[str, Any]:
    return dict((carteira_canonica.mapa_produtos.get('by_key', {}) or {}).get(produto_key) or {})


def _normalizar_bool_series(df: pd.DataFrame, coluna: str, padrao: bool = False) -> pd.Series:
    if coluna not in df.columns:
        return pd.Series([padrao] * len(df), index=df.index)
    return df[coluna].fillna(padrao).astype(bool)


def _selecionar_produtos_candidatos(carteira_canonica: PacoteCarteiraCanonica, triagem_motor: PacoteTriagemMotor | None) -> pd.DataFrame:
    if triagem_motor is not None and isinstance(getattr(triagem_motor, 'quadro_candidatos', None), pd.DataFrame) and len(triagem_motor.quadro_candidatos) > 0:
        df = triagem_motor.quadro_candidatos.copy()
    else:
        df = carteira_canonica.quadro_canonico.copy()
    if len(df) == 0:
        return df
    mask = (
        _normalizar_bool_series(df, 'ativo', True)
        & _normalizar_bool_series(df, 'elegivel_switch_in', True)
    )
    if 'produto_key' in df.columns:
        df = df[mask].drop_duplicates(subset=['produto_key'], keep='first').copy()
    else:
        df = df[mask].copy()
    if 'score_final' in df.columns:
        df = df.sort_values(['score_final', 'nome'], ascending=[False, True], kind='stable').reset_index(drop=True)
    elif 'nome' in df.columns:
        df = df.sort_values(['nome'], kind='stable').reset_index(drop=True)
    return df


def _lotes_ativos_switching(replay_passado: PacoteReplayPassadoControlado | None) -> list[Lote]:
    if replay_passado is None:
        return []
    lotes: list[Lote] = []
    for lote in replay_passado.lotes_apos_replay:
        if lote.esgotado:
            continue
        if float(getattr(lote, 'saldo_bruto', 0.0) or 0.0) <= 0.01:
            continue
        if limpar_texto(getattr(lote, 'situacao_investimento', '')) != 'aportado':
            continue
        if not limpar_texto(getattr(lote, 'produto_key', '')):
            continue
        lotes.append(lote)
    return lotes


def _data_primeira_despesa_futura(dados_operacionais: PacoteDadosOperacionaisCanonicos, data_referencia: date) -> date | None:
    gastos = dados_operacionais.gastos_canonicos.copy()
    if len(gastos) == 0 or 'data' not in gastos.columns:
        return None
    datas = pd.to_datetime(gastos['data'], errors='coerce').dt.date
    mask = datas.notna() & (datas >= data_referencia)
    if 'futuro_ou_pendente_na_data_referencia' in gastos.columns:
        mask &= gastos['futuro_ou_pendente_na_data_referencia'].fillna(False)
    datas_validas = [d for d in datas[mask].tolist() if isinstance(d, date)]
    return min(datas_validas) if datas_validas else None



def _criar_lote_destino_shadow(produto_row: Mapping[str, Any], valor_inicial: float, data_referencia: date) -> Lote:
    carencia_dias = para_int(produto_row.get('carencia_dias'), 0)
    carencia_ate = (data_referencia + timedelta(days=carencia_dias)) if carencia_dias > 0 else None
    return criar_lote_de_aporte(
        data_referencia,
        float(valor_inicial),
        f"shadow::{limpar_texto(produto_row.get('produto_key'))}",
        {
            'investimento': limpar_texto(produto_row.get('nome')),
            'produto_key': limpar_texto(produto_row.get('produto_key')),
            'data_base_fiscal': data_referencia,
            'data_recebimento': data_referencia,
            'fator_acumulado_inicial': 1.0,
            'taxa_base_cdi': float(para_float_monetario(produto_row.get('taxa_base_cdi'), 1.0) or 1.0),
            'taxa_bonus_cdi': float(para_float_monetario(produto_row.get('taxa_bonus_cdi'), 0.0) or 0.0),
            'dias_bonus': int(para_int(produto_row.get('dias_bonus'), 0) or 0),
            'principal_remanescente': float(valor_inicial),
            'produto_isento_ir': bool(produto_row.get('isento_ir', False)),
            'carencia_ate': carencia_ate,
            'nao_disponivel_para_aporte': False,
            'situacao_investimento': 'shadow_switch_destino',
        },
    )


def _valor_liquido_lote(lote: Lote, data_ref: date, tabela_iof: list[float], faixas_ir: list[dict[str, Any]]) -> float:
    return float(lote.valor_liquido_hoje(data_ref, tabela_iof=tabela_iof, faixas_ir=faixas_ir))


def _avaliar_bloqueio_candidato(
    lote: Lote,
    produto_row: Mapping[str, Any],
    *,
    valor_liquido_resgatavel: float,
    data_referencia: date,
    data_horizonte: date,
    primeira_despesa_futura: date | None,
) -> tuple[bool, str | None]:
    produto_key = limpar_texto(produto_row.get('produto_key'))
    if produto_key and produto_key == limpar_texto(getattr(lote, 'produto_key', '')):
        return False, 'mesmo_produto_atual'

    minimo = float(para_float_monetario(produto_row.get('aplicacao_minima'), 0.0) or 0.0)
    maximo = float(para_float_monetario(produto_row.get('aplicacao_maxima'), 0.0) or 0.0)
    if minimo > 0.0 and valor_liquido_resgatavel + 1e-9 < minimo:
        return False, 'abaixo_da_aplicacao_minima'
    if maximo > 0.0 and valor_liquido_resgatavel - 1e-9 > maximo:
        return False, 'acima_da_aplicacao_maxima'

    carencia_dias = int(para_int(produto_row.get('carencia_dias'), 0) or 0)
    carencia_ate = data_referencia + timedelta(days=carencia_dias) if carencia_dias > 0 else None
    if carencia_ate is not None and carencia_ate > data_horizonte:
        return False, 'carencia_ultrapassa_horizonte_shadow'
    if primeira_despesa_futura is not None and carencia_ate is not None and carencia_ate > primeira_despesa_futura:
        return False, 'carencia_ultrapassa_primeira_despesa_futura'

    return True, None


def _score_shadow(
    ganho_liquido: float,
    *,
    valor_liquido_resgatavel: float,
    score_triagem: float,
    carencia_dias: int,
    prazo_dias: int,
    fgc: bool,
    risco_real: str,
) -> float:
    excesso_prazo = max(prazo_dias - 180, 0)
    risco_bonus = 3.0 if fgc else 0.0
    risco_pen = 8.0 if 'alto' in normalizar_texto(risco_real) else (4.0 if 'medio' in normalizar_texto(risco_real) else 0.0)
    carencia_pen = min(float(carencia_dias) * 0.05, 8.0)
    prazo_pen = min(float(excesso_prazo) * 0.01, 12.0)
    materialidade = (ganho_liquido / max(valor_liquido_resgatavel, 1.0)) * 1000.0
    return float(ganho_liquido + materialidade + (score_triagem * 0.10) + risco_bonus - risco_pen - carencia_pen - prazo_pen)


def carregar_switching_economico_shadow(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    carteira_canonica: PacoteCarteiraCanonica,
    triagem_motor: PacoteTriagemMotor | None,
    replay_passado: PacoteReplayPassadoControlado | None,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    config: Mapping[str, Any],
    *,
    ranking_carteira: Any | None = None,
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
) -> PacoteSwitchingEconomicoShadow:
    horizonte_dias = int(obter_config(config, 'simulacao', 'horizonte_alocacao_dias', padrao=180) or 180)
    ganho_minimo = float(obter_config(config, 'switching_shadow', 'ganho_minimo_absoluto', padrao=5.0) or 5.0)
    taxa_proj = float(calendario_financeiro.taxa_dia_base)
    data_horizonte = data_referencia + timedelta(days=horizonte_dias)
    primeira_despesa_futura = _data_primeira_despesa_futura(dados_operacionais, data_referencia)
    destinos_oficiais = getattr(ranking_carteira, 'quadro_destinos_switch', None) if ranking_carteira is not None else None
    rank_oficial_por_key: dict[str, int] = {}
    score_oficial_por_key: dict[str, float] = {}
    semantica_por_key: dict[str, str] = {}
    indexador_por_key: dict[str, str] = {}
    if isinstance(destinos_oficiais, pd.DataFrame) and len(destinos_oficiais):
        for _, rk in destinos_oficiais.iterrows():
            k = limpar_texto(rk.get('produto_key'))
            if not k:
                continue
            rank_oficial_por_key[k] = int(para_int(rk.get('rank_destino'), 999) or 999)
            score_oficial_por_key[k] = float(rk.get('score_final', 0.0) or 0.0)
            semantica_por_key[k] = limpar_texto(rk.get('semantica_taxa_base'))
            indexador_por_key[k] = limpar_texto(rk.get('tipo_produto'))

    lotes = _lotes_ativos_switching(replay_passado)
    candidatos = _selecionar_produtos_candidatos(carteira_canonica, triagem_motor)
    quadro_linhas: list[dict[str, Any]] = []

    for lote in lotes:
        valor_liquido_resgatavel = _valor_liquido_lote(lote, data_referencia, tabela_iof, faixas_ir)
        lote_projetado = simular_lote_ate_data_shadow(lote, data_referencia, data_horizonte, calendario_financeiro, taxa_proj=taxa_proj, serie_cdi=None)
        manter_liquido_horizonte = _valor_liquido_lote(lote_projetado, data_horizonte, tabela_iof, faixas_ir)
        produto_origem_meta = _produto_meta_por_key(carteira_canonica, lote.produto_key)
        produto_origem_nome = limpar_texto(produto_origem_meta.get('nome')) or limpar_texto(lote.investimento) or lote.produto_key

        for _, produto_row in candidatos.iterrows():
            elegivel, motivo_bloqueio = _avaliar_bloqueio_candidato(
                lote,
                produto_row,
                valor_liquido_resgatavel=valor_liquido_resgatavel,
                data_referencia=data_referencia,
                data_horizonte=data_horizonte,
                primeira_despesa_futura=primeira_despesa_futura,
            )
            produto_destino_key = limpar_texto(produto_row.get('produto_key'))
            produto_destino_nome = limpar_texto(produto_row.get('nome'))
            linha = {
                'lote_id': lote.id,
                'produto_origem_key': lote.produto_key,
                'produto_origem_nome': produto_origem_nome,
                'produto_destino_key': produto_destino_key,
                'produto_destino_nome': produto_destino_nome,
                'data_referencia': data_referencia,
                'data_horizonte': data_horizonte,
                'valor_bruto_atual': arredondar_monetario(float(lote.saldo_bruto)),
                'valor_liquido_resgatavel': arredondar_monetario(valor_liquido_resgatavel),
                'riqueza_manter_horizonte': arredondar_monetario(manter_liquido_horizonte),
                'carencia_dias_destino': int(para_int(produto_row.get('carencia_dias'), 0) or 0),
                'prazo_dias_destino': int(para_int(produto_row.get('prazo_dias'), 0) or 0),
                'score_triagem_destino': float(produto_row.get('score_final', 0.0) or 0.0),
                'regime_taxa_destino': limpar_texto(produto_row.get('regime_taxa')),
                'risco_real_destino': limpar_texto(produto_row.get('risco_real')),
                'status_confirmacao_destino': limpar_texto(produto_row.get('status_confirmacao')),
                'campos_pendentes_destino': limpar_texto(produto_row.get('campos_pendentes')),
                'fgc_destino': bool(produto_row.get('fgc', False)),
                'elegivel_shadow': bool(elegivel),
                'motivo_bloqueio_shadow': motivo_bloqueio,
                'riqueza_switch_horizonte': None,
                'ganho_liquido_estimado': None,
                'score_switch_shadow': None,
                'ranking_lote': None,
                'recomendado_shadow': False,
                'rank_origem': int(rank_oficial_por_key.get(limpar_texto(lote.produto_key), 999)),
                'rank_destino': int(rank_oficial_por_key.get(produto_destino_key, 999)),
                'score_destino_oficial': float(score_oficial_por_key.get(produto_destino_key, 0.0)),
                'semantica_taxa_base_destino': semantica_por_key.get(produto_destino_key, limpar_texto(produto_row.get('semantica_taxa_base'))),
                'tipo_produto_destino': indexador_por_key.get(produto_destino_key, limpar_texto(produto_row.get('tipo_produto'))),
                'bloqueado_pos_gate': False,
                'motivo_gate_switching': '',
                'candidato_promovivel_pos_gate': False,
            }
            if elegivel:
                lote_destino = _criar_lote_destino_shadow(produto_row, valor_liquido_resgatavel, data_referencia)
                lote_destino_proj = simular_lote_ate_data_shadow(lote_destino, data_referencia, data_horizonte, calendario_financeiro, taxa_proj=taxa_proj)
                riqueza_switch = _valor_liquido_lote(lote_destino_proj, data_horizonte, tabela_iof, faixas_ir)
                ganho = round(float(riqueza_switch) - float(manter_liquido_horizonte), 2)
                score = _score_shadow(
                    ganho,
                    valor_liquido_resgatavel=valor_liquido_resgatavel,
                    score_triagem=float(produto_row.get('score_final', 0.0) or 0.0),
                    carencia_dias=int(para_int(produto_row.get('carencia_dias'), 0) or 0),
                    prazo_dias=int(para_int(produto_row.get('prazo_dias'), 0) or 0),
                    fgc=bool(produto_row.get('fgc', False)),
                    risco_real=limpar_texto(produto_row.get('risco_real')),
                )
                linha['riqueza_switch_horizonte'] = arredondar_monetario(riqueza_switch)
                linha['ganho_liquido_estimado'] = arredondar_monetario(ganho)
                linha['score_switch_shadow'] = round(float(score), 4)
            quadro_linhas.append(linha)

    quadro = pd.DataFrame(quadro_linhas)
    if len(quadro) == 0:
        auditoria = {
            'resumo': {
                'qtd_lotes_ativos_avaliados': len(lotes),
                'qtd_candidatos_switch': len(candidatos),
                'qtd_linhas_analise': 0,
                'qtd_recomendacoes_shadow': 0,
            },
            'amostras': {},
        }
        validacao = {'ok': False, 'erros': ['sem_lotes_ou_sem_candidatos_para_switching_shadow'], 'avisos': []}
        return PacoteSwitchingEconomicoShadow(pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([]), auditoria, validacao)

    if 'elegivel_shadow' in quadro.columns:
        elegiveis = quadro[quadro['elegivel_shadow'].fillna(False)].copy()
    else:
        elegiveis = pd.DataFrame([])
    if len(elegiveis) > 0:
        elegiveis = elegiveis.sort_values(['lote_id', 'score_switch_shadow', 'ganho_liquido_estimado', 'produto_destino_nome'], ascending=[True, False, False, True], kind='stable')
        elegiveis['ranking_lote'] = elegiveis.groupby('lote_id').cumcount() + 1
        elegiveis['recomendado_shadow_antes_gate'] = (elegiveis['ranking_lote'] == 1) & (elegiveis['ganho_liquido_estimado'].fillna(0.0) >= ganho_minimo)
        ganho_rel = elegiveis['ganho_liquido_estimado'].fillna(0.0) / elegiveis['valor_liquido_resgatavel'].replace(0.0, 1.0)
        rank_dest = elegiveis['rank_destino'].fillna(999).astype(int)
        rank_ori = elegiveis['rank_origem'].fillna(999).astype(int)
        delta_rank = rank_dest - rank_ori
        limiar_rank_baixo = 0.80
        gate_rank_baixo = (rank_dest >= 20) & (ganho_rel < limiar_rank_baixo)
        gate_rank_pior = (delta_rank > 0) & (ganho_rel < 0.60)
        semantica = elegiveis['semantica_taxa_base_destino'].fillna('').astype(str).str.lower().str.strip()
        gate_semantica = semantica.ne('percentual_cdi')
        gate = gate_rank_baixo | gate_rank_pior | gate_semantica
        elegiveis.loc[gate_rank_baixo, 'motivo_gate_switching'] = 'bloqueado_rank_muito_inferior_sem_ganho_robusto'
        elegiveis.loc[gate_rank_pior, 'motivo_gate_switching'] = 'bloqueado_rank_pior_sem_ganho_excepcional'
        elegiveis.loc[gate_semantica, 'motivo_gate_switching'] = 'bloqueado_semantica_taxa_nao_suportada_shadow'
        elegiveis.loc[gate, 'bloqueado_pos_gate'] = True
        elegiveis['candidato_promovivel_pos_gate'] = (~elegiveis['bloqueado_pos_gate']) & (elegiveis['ganho_liquido_estimado'].fillna(0.0) >= ganho_minimo)
        elegiveis['recomendado_shadow'] = False
        idx = elegiveis[elegiveis['candidato_promovivel_pos_gate']].groupby('lote_id', as_index=False).head(1).index
        elegiveis.loc[idx, 'recomendado_shadow'] = True
        elegiveis['recomendado_shadow_depois_gate'] = elegiveis['recomendado_shadow']
        quadro.loc[elegiveis.index, 'ranking_lote'] = elegiveis['ranking_lote']
        quadro.loc[elegiveis.index, 'recomendado_shadow'] = elegiveis['recomendado_shadow']
        quadro.loc[elegiveis.index, 'recomendado_shadow_antes_gate'] = elegiveis['recomendado_shadow_antes_gate']
        quadro.loc[elegiveis.index, 'recomendado_shadow_depois_gate'] = elegiveis['recomendado_shadow_depois_gate']
        quadro.loc[elegiveis.index, 'bloqueado_pos_gate'] = elegiveis['bloqueado_pos_gate']
        quadro.loc[elegiveis.index, 'motivo_gate_switching'] = elegiveis['motivo_gate_switching']
        quadro.loc[elegiveis.index, 'candidato_promovivel_pos_gate'] = elegiveis['candidato_promovivel_pos_gate']

    melhores = quadro[quadro['ranking_lote'] == 1].copy() if 'ranking_lote' in quadro.columns else pd.DataFrame([])
    melhores = melhores.sort_values(['recomendado_shadow', 'ganho_liquido_estimado', 'score_switch_shadow', 'lote_id'], ascending=[False, False, False, True], kind='stable') if len(melhores) > 0 else melhores
    plano = melhores[melhores['recomendado_shadow'].fillna(False)].copy() if len(melhores) > 0 else pd.DataFrame([])

    auditoria = {
        'resumo': {
            'horizonte_dias_shadow': horizonte_dias,
            'data_referencia': data_referencia,
            'data_horizonte': data_horizonte,
            'primeira_despesa_futura': primeira_despesa_futura,
            'ganho_minimo_absoluto_shadow': ganho_minimo,
            'qtd_lotes_ativos_avaliados': int(len(lotes)),
            'qtd_candidatos_switch': int(len(candidatos)),
            'qtd_linhas_analise': int(len(quadro)),
            'qtd_linhas_elegiveis': int(len(elegiveis)),
            'qtd_recomendacoes_shadow': int(len(plano)),
            'soma_ganho_shadow_recomendado': arredondar_monetario(plano['ganho_liquido_estimado'].fillna(0.0).sum()) if len(plano) > 0 else 0.0,
            'bloqueios_por_motivo': {str(k): int(v) for k, v in quadro['motivo_bloqueio_shadow'].fillna('sem_bloqueio').value_counts(dropna=False).to_dict().items()},
        },
        'amostras': {
            'melhores_oportunidades': melhores.head(10).to_dict('records') if len(melhores) > 0 else [],
            'plano_shadow': plano.head(10).to_dict('records') if len(plano) > 0 else [],
        },
    }
    validacao = {
        'ok': True,
        'erros': [],
        'avisos': [] if len(plano) > 0 else ['nenhum_switch_shadow_superou_o_limiar_minimo'],
    }
    return PacoteSwitchingEconomicoShadow(
        quadro_oportunidades=quadro,
        quadro_melhores_oportunidades=melhores.reset_index(drop=True),
        plano_shadow=plano.reset_index(drop=True),
        auditoria=auditoria,
        validacao=validacao,
    )
