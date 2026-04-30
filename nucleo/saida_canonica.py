"""Camada única de saída canônica da baseline V203.

Este módulo materializa a camada observável oficial do projeto. Console,
planilha e futuras saídas JSON/CSV/Markdown devem consumir este pacote em vez
de recalcular saldos, resgates, switchings ou amostras em paralelo.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import pandas as pd

from nucleo.calendario_financeiro import calcular_dias_lote, proximo_dia_util_bancario_em_ou_apos
from nucleo.contexto_baseline import obter_limiar_residuo_resolvido
from nucleo.nucleo_financeiro_minimo import executar_saque_lote
from nucleo.rotulagem_fechamento import resumir_fechamento_situacao_atual
from nucleo.utilitarios_neutros import normalizar_valores_situacao_atual_exaurida


@dataclass(frozen=True)
class PacoteSaidaCanonica:
    versao: str
    data_referencia: Any = None
    extrato_passado: list[dict[str, Any]] = field(default_factory=list)
    extrato_futuro: list[dict[str, Any]] = field(default_factory=list)
    switchings: list[dict[str, Any]] = field(default_factory=list)
    ranking_amostra: list[dict[str, Any]] = field(default_factory=list)
    lotes_ativos: list[dict[str, Any]] = field(default_factory=list)
    lotes_exauridos: list[dict[str, Any]] = field(default_factory=list)
    recebidos_atuais: list[dict[str, Any]] = field(default_factory=list)
    fechamento_atual: list[dict[str, Any]] = field(default_factory=list)
    resumo_recebidos: list[dict[str, Any]] = field(default_factory=list)
    auditoria: dict[str, Any] = field(default_factory=dict)

    def pagamentos_realizados_console(self, limite: int = 5) -> list[dict[str, Any]]:
        return [
            {
                'Data': item.get('Data'),
                'Descrição': item.get('Conta') or item.get('Descrição') or '',
                'Valor': item.get('Líquido'),
                'Lotes usados': item.get('Lotes usados') or item.get('Lote') or '',
                'Saldo Antes': item.get('Saldo Antes'),
                'Bruto': item.get('Bruto'),
                'Imposto': item.get('Imposto'),
                'Líquido': item.get('Líquido'),
                'Saldo Remanescente': item.get('Saldo Remanescente'),
            }
            for item in self.extrato_passado[:limite]
        ]

    def pagamentos_proximos_console(self, limite: int = 5) -> list[dict[str, Any]]:
        return [
            {
                'Data': item.get('Data'),
                'Conta': item.get('Conta') or '',
                'Valor': item.get('Valor'),
                'Lote': item.get('Lote sugerido') or '',
                'Pacote': item.get('Pacote do dia') or item.get('Estratégia') or '',
                'Switch?': item.get('Necessita switching') or '',
                'Reserva': item.get('Lote reserva') or '',
                'Saldo ant.': item.get('Saldo Antes'),
                'Bruto': item.get('Bruto'),
                'IR': item.get('Imposto'),
                'Liq.': item.get('Líquido'),
                'Rem.': item.get('Saldo Remanescente'),
                'Sw. ant.': item.get('Switching antes do pagamento') if item.get('Switching antes do pagamento') not in (None, '') else 'n/d',
                'Sw. dep.': item.get('Switching depois do pagamento') if item.get('Switching depois do pagamento') not in (None, '') else 'n/d',
                'Status': item.get('Status recomendação') if item.get('Status recomendação') not in (None, '') else 'n/d',
                'Bloq.': item.get('Motivo bloqueio lote') if item.get('Motivo bloqueio lote') not in (None, '') else 'n/d',
            }
            for item in self.extrato_futuro[:limite]
        ]

    def recebidos_futuros_console(self, limite: int = 5) -> list[dict[str, Any]]:
        lotes_futuros: set[str] = set()
        for item in self.extrato_futuro:
            for fonte in _split_fontes(item.get('Lote sugerido')):
                lotes_futuros.add(fonte)

        top1 = 'não determinado'
        for row in self.ranking_amostra:
            produto = row.get('Produto')
            if produto:
                top1 = "Top1 [prov.]"
                break

        def _prioridade(linha: dict[str, Any]) -> tuple[int, str, str]:
            return (-int(linha.get('_usado_int', 0)), str(linha.get('Data') or ''), str(linha.get('Lote') or ''))

        data_ref = str(self.data_referencia or '')
        candidatos = []
        for item in self.recebidos_atuais:
            data_item = str(item.get('Recebimento') or '')
            status_item = str(item.get('Status') or '').lower()
            if data_ref and data_item and data_item < data_ref:
                continue
            if status_item in {'exaurido', 'aplicado'}:
                continue
            candidatos.append(item)

        linhas: list[dict[str, Any]] = []
        for item in candidatos:
            lote = str(item.get('Lote origem') or item.get('Recebido') or '')
            status = item.get('Status') or 'não determinado'
            destino = item.get('Destino') or 'não determinado'
            valor = item.get('Valor líquido') if item.get('Valor líquido') not in ('', None) else item.get('Valor bruto')
            valor_vinc = _round_monetario(item.get('Valor vinculado'), 0.0)
            pagamentos_vinc = int(item.get('Pagamentos vinculados') or 0)
            usado_int = 1 if (lote in lotes_futuros or pagamentos_vinc > 0 or float(valor_vinc or 0.0) > 0.0) else 0
            usado = 'sim' if usado_int else 'não'
            linhas.append({
                'Data': item.get('Recebimento'),
                'Lote': lote,
                'Valor': _round_monetario(valor, 0.0),
                'Status': status,
                'Destino': destino,
                'Carteira': item.get('Carteira') or item.get('Produto') or top1,
                'Usado': usado,
                'Saldo': _round_monetario(item.get('Residual aplicação'), 'n/d'),
                '_usado_int': usado_int,
            })
        linhas.sort(key=_prioridade)
        return [{k: v for k, v in linha.items() if not k.startswith('_')} for linha in linhas[:limite]]


def _fmt_data(valor: Any) -> Any:
    return valor.isoformat() if hasattr(valor, 'isoformat') else valor


def _round_monetario(valor: Any, padrao: Any = '') -> Any:
    if valor is None or valor == '':
        return padrao
    try:
        return round(float(valor), 2)
    except Exception:
        return padrao


def _split_fontes(valor: Any) -> list[str]:
    partes = [parte.strip() for parte in str(valor or '').split('+')]
    return [parte for parte in partes if parte]


def _mapa_saldo_disponivel(contexto: Any) -> dict[str, dict[str, Any]]:
    mapa: dict[str, dict[str, Any]] = {}
    pacote = getattr(contexto, 'saldo_disponivel_geral', None)
    quadro = getattr(pacote, 'quadro_saldo_disponivel', None) if pacote is not None else None
    if isinstance(quadro, pd.DataFrame) and len(quadro):
        for _, row in quadro.iterrows():
            mapa[str(row.get('pagamento_id') or '').strip()] = row.to_dict()
    return mapa


def _mapa_pagamentos_central(contexto: Any) -> dict[str, dict[str, Any]]:
    mapa: dict[str, dict[str, Any]] = {}
    pacote = getattr(contexto, 'recomputacao_sequencial_central_v1', None)
    quadro = getattr(pacote, 'quadro_recomputacao_sequencial_central', None) if pacote is not None else None
    if isinstance(quadro, pd.DataFrame) and len(quadro):
        for _, row in quadro.iterrows():
            mapa[str(row.get('pagamento_id') or '').strip()] = row.to_dict()
    return mapa


def _ultimo_fator_cache_cdi(contexto: Any) -> tuple[float, Any]:
    serie = getattr(getattr(contexto, 'cache_cdi', None), 'serie_cdi', {}) or {}
    if not serie:
        return 1.0, None
    try:
        data_ult = max(serie.keys())
        fator = float(serie.get(data_ult) or 1.0)
        return fator if fator > 0 else 1.0, data_ult
    except Exception:
        return 1.0, None


def _mapa_saldos_correntes_lotes(contexto: Any) -> dict[str, dict[str, float]]:
    replay = getattr(contexto, 'replay_passado', None)
    lotes = getattr(replay, 'lotes_apos_replay', []) if replay is not None else []
    ctx = contexto.execucao
    cal = contexto.calendario_financeiro
    serie = getattr(getattr(contexto, 'cache_cdi', None), 'serie_cdi', None)
    tabela_iof = contexto.tabela_iof
    faixas_ir = contexto.faixas_ir
    mapa: dict[str, dict[str, float]] = {}
    for lote in lotes:
        try:
            bruto = round(float(lote.valor_bruto_em_data(ctx.data_referencia, cal, serie_cdi=serie, data_base_referencia=ctx.data_referencia) or 0.0), 2)
            liquido = round(float(lote.valor_liquido_em_data(ctx.data_referencia, cal, tabela_iof=tabela_iof, faixas_ir=faixas_ir, serie_cdi=serie, data_base_referencia=ctx.data_referencia) or 0.0), 2)
        except Exception:
            bruto = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
            liquido = round(float(lote.valor_liquido_hoje(ctx.data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
        mapa[str(lote.id)] = {
            'bruto': bruto,
            'liquido': liquido,
            'saldo_rem': round(float(getattr(lote, 'principal_remanescente', 0.0) or 0.0), 2),
        }
    return mapa


def _avancar_lote_para_data(lote: Any, data_origem: Any, data_alvo: Any, contexto: Any) -> None:
    if data_alvo is None or data_origem is None or data_alvo <= data_origem:
        return
    fator_dia, _ = _ultimo_fator_cache_cdi(contexto)
    taxa_diaria = max(float(fator_dia) - 1.0, 0.0)
    data_cursor = data_origem
    while data_cursor < data_alvo:
        data_cursor = data_cursor + timedelta(days=1)
        lote.atualizar_juros(data_cursor, taxa_diaria, contexto.calendario_financeiro, serie_cdi=None, data_fechamento_referencia=data_cursor)


def _quadro_futuro_preferencial(contexto: Any) -> pd.DataFrame | None:
    motor = getattr(contexto, 'motor_recomendacao_pagamentos_switching_v1', None)
    quadro = getattr(motor, 'quadro_recomendacoes', None) if motor is not None else None
    if isinstance(quadro, pd.DataFrame) and len(quadro):
        return quadro.copy().sort_values(['data_pagamento', 'pagamento_id'], kind='stable')
    decisao = getattr(contexto, 'decisao_local_v1', None)
    quadro = getattr(decisao, 'quadro_decisao_local_v1', None) if decisao is not None else None
    if isinstance(quadro, pd.DataFrame) and len(quadro):
        return quadro.copy().sort_values(['data_pagamento', 'pagamento_id'], kind='stable')
    return None


def _mapa_resumos_futuros(contexto: Any, quadro_futuro: pd.DataFrame | None) -> dict[str, dict[str, Any]]:
    if not isinstance(quadro_futuro, pd.DataFrame) or len(quadro_futuro) == 0:
        return {}
    tabela_iof = contexto.tabela_iof
    faixas_ir = contexto.faixas_ir
    replay = getattr(contexto, 'replay_passado', None)
    lotes_orig = getattr(replay, 'lotes_apos_replay', []) if replay is not None else []
    lotes_estado = {str(l.id): deepcopy(l) for l in lotes_orig}
    lotes_data = {str(l.id): contexto.execucao.data_referencia for l in lotes_orig}
    saldo_map = _mapa_saldo_disponivel(contexto)
    saldos_correntes = _mapa_saldos_correntes_lotes(contexto)
    consumo_saldo = 0.0
    limiar = obter_limiar_residuo_resolvido(contexto.pacote_config.conteudo)
    resumos: dict[str, dict[str, Any]] = {}

    quadro = quadro_futuro.copy().sort_values(['data_pagamento', 'pagamento_id'], kind='stable')
    for _, row in quadro.iterrows():
        pagamento_id = str(row.get('pagamento_id') or '').strip()
        data_pag = row.get('data_pagamento')
        valor = round(float(row.get('valor_pagamento') or 0.0), 2)
        lote_sug = str(row.get('lote_recomendado') or row.get('lote_id_escolhido') or row.get('fonte_base_escolhida') or row.get('tipo_fonte_escolhida') or '')
        fontes = _split_fontes(lote_sug)
        reserva = str(row.get('lote_reserva') or '').strip()
        if reserva and str(row.get('estrategia_recomendada') or '') == 'combinacao_minima':
            for fonte_reserva in _split_fontes(reserva):
                if fonte_reserva not in fontes:
                    fontes.append(fonte_reserva)
        resumo = {'Lote sugerido': ' + '.join(fontes) if fontes else lote_sug, 'Saldo Antes': '', 'Bruto': '', 'Imposto': '', 'Líquido': '', 'Saldo Remanescente': ''}
        restante = valor
        saldo_antes_total = 0.0
        bruto_total = 0.0
        imposto_total = 0.0
        liquido_total = 0.0
        saldo_rem_final: Any = ''
        fontes_usadas: list[str] = []
        for fonte in fontes:
            if restante <= 0.01:
                break
            if fonte in lotes_estado and data_pag is not None:
                lote = lotes_estado[fonte]
                corrente = saldos_correntes.get(fonte, {})
                saldo_corrente_bruto = round(float(corrente.get('bruto') or 0.0), 2)
                fator_atual = max(float(getattr(lote, 'fator_acumulado', 1.0) or 1.0), 1.0)
                principal = max(float(getattr(lote, 'principal_remanescente', 0.0) or 0.0), 0.0)
                if saldo_corrente_bruto > 0:
                    lote.saldo_bruto = saldo_corrente_bruto
                    if principal > 0:
                        lote.fator_acumulado = max(saldo_corrente_bruto / principal, fator_atual)
                _avancar_lote_para_data(lote, lotes_data.get(fonte, contexto.execucao.data_referencia), data_pag, contexto)
                lotes_data[fonte] = data_pag
                liquido_disponivel = round(float(lote.valor_liquido_hoje(data_pag, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
                if liquido_disponivel <= 0.01:
                    continue
                alvo = round(min(restante, liquido_disponivel), 2)
                mov = executar_saque_lote(lote, alvo, data_pag, tabela_iof=tabela_iof, faixas_ir=faixas_ir)
                if mov is None:
                    continue
                saldo_rem = round(float(mov.get('saldo_remanescente') or 0.0), 2)
                if saldo_rem <= limiar:
                    saldo_rem = 0.0
                saldo_antes_total = round(saldo_antes_total + float(mov.get('saldo_antes') or 0.0), 2)
                bruto_total = round(bruto_total + float(mov.get('bruto') or 0.0), 2)
                imposto_total = round(imposto_total + float(mov.get('imposto') or 0.0), 2)
                liquido = round(float(mov.get('liquido') or 0.0), 2)
                liquido_total = round(liquido_total + liquido, 2)
                restante = round(max(restante - liquido, 0.0), 2)
                saldo_rem_final = saldo_rem
                fontes_usadas.append(fonte)
            elif fonte == 'saldo_disponivel_geral':
                base = saldo_map.get(pagamento_id, {})
                saldo_base = round(float(base.get('saldo_disponivel_bruto') or base.get('saldo_disponivel_liquido') or 0.0), 2)
                saldo_antes = max(round(saldo_base - consumo_saldo, 2), 0.0)
                if saldo_antes <= 0.01:
                    continue
                liquido = round(min(restante, saldo_antes), 2)
                saldo_rem = max(round(saldo_antes - liquido, 2), 0.0)
                consumo_saldo = round(consumo_saldo + liquido, 2)
                saldo_antes_total = round(saldo_antes_total + saldo_antes, 2)
                bruto_total = round(bruto_total + liquido, 2)
                liquido_total = round(liquido_total + liquido, 2)
                restante = round(max(restante - liquido, 0.0), 2)
                saldo_rem_final = saldo_rem
                fontes_usadas.append(fonte)
        if fontes_usadas:
            resumo = {
                'Lote sugerido': ' + '.join(fontes_usadas),
                'Saldo Antes': saldo_antes_total,
                'Bruto': bruto_total,
                'Imposto': imposto_total,
                'Líquido': liquido_total,
                'Saldo Remanescente': saldo_rem_final,
            }
        resumos[pagamento_id] = resumo
    return resumos


def _resumo_futuro(contexto: Any, pagamento_id: str, decisao_row: dict[str, Any], mapa_resumos: dict[str, dict[str, Any]], mapa_central: dict[str, dict[str, Any]]) -> dict[str, Any]:
    central = mapa_central.get(str(pagamento_id or '').strip(), {})
    if central:
        return {
            'Saldo Antes': _round_monetario(central.get('saldo_antes_central')),
            'Bruto': _round_monetario(central.get('bruto_central')),
            'Imposto': _round_monetario(central.get('imposto_central')),
            'Líquido': _round_monetario(central.get('liquido_central')),
            'Saldo Remanescente': _round_monetario(central.get('saldo_remanescente_central')),
            'Lote sugerido': central.get('lote_final_central') or central.get('lote_sugerido_original') or '',
        }
    resumo = mapa_resumos.get(str(pagamento_id or '').strip())
    if resumo:
        return resumo
    return {
        'Saldo Antes': '',
        'Bruto': '',
        'Imposto': '',
        'Líquido': '',
        'Saldo Remanescente': '',
        'Lote sugerido': decisao_row.get('lote_recomendado') or decisao_row.get('lote_id_escolhido') or decisao_row.get('fonte_base_escolhida') or decisao_row.get('tipo_fonte_escolhida') or '',
    }


def _ranking_destino_para_lote(contexto: Any, lote: Any) -> dict[str, Any] | None:
    ranking = getattr(contexto, 'ranking_carteira', None)
    destinos = getattr(ranking, 'quadro_destinos_switch', None) if ranking is not None else None
    if not isinstance(destinos, pd.DataFrame) or len(destinos) == 0:
        return None
    destinos = destinos.copy()
    origem_key = str(getattr(lote, 'produto_key', '') or '').strip()
    if 'produto_key' in destinos.columns:
        destinos = destinos[destinos['produto_key'].fillna('').astype(str).str.strip() != origem_key]
    status_col = 'Status_Confirmação' if 'Status_Confirmação' in destinos.columns else ('status_confirmacao' if 'status_confirmacao' in destinos.columns else None)
    if status_col is not None:
        destinos = destinos[destinos[status_col].fillna('').astype(str).isin(['', 'Confirmado', 'confirmado', 'Fortemente sustentado'])]
    if 'elegivel_switch_in' in destinos.columns:
        destinos = destinos[destinos['elegivel_switch_in'].fillna(False).astype(bool)]
    valor_liquido = round(float(lote.valor_liquido_hoje(contexto.execucao.data_referencia, tabela_iof=contexto.tabela_iof, faixas_ir=contexto.faixas_ir) or 0.0), 2)
    if 'aplicacao_minima' in destinos.columns:
        elegiveis = destinos[destinos['aplicacao_minima'].fillna(0.0).astype(float) <= valor_liquido + 1e-9]
        if len(elegiveis):
            destinos = elegiveis
    if len(destinos) == 0:
        return None
    if 'rank_destino' in destinos.columns:
        destinos = destinos.sort_values(['rank_destino', 'score_final', 'nome'], ascending=[True, False, True], kind='stable')
    else:
        destinos = destinos.sort_values(['score_final', 'nome'], ascending=[False, True], kind='stable')
    return destinos.iloc[0].to_dict()


def _data_sugerida_switching_lote(contexto: Any, lote: Any) -> Any:
    carteira = getattr(contexto, 'carteira_canonica', None)
    mapa = getattr(carteira, 'mapa_produtos', {}) if carteira is not None else {}
    meta = ((mapa.get('by_key') or {}).get(getattr(lote, 'produto_key', None)) or {}) if isinstance(mapa, dict) else {}
    prazo = int(meta.get('prazo_dias') or 0)
    datas_candidatas = []
    if prazo > 0:
        datas_candidatas.append(lote.data_aplicacao + timedelta(days=prazo))
    carencia = getattr(lote, 'carencia_ate', None)
    if carencia is not None:
        datas_candidatas.append(carencia)
    base = max(datas_candidatas) if datas_candidatas else contexto.execucao.data_referencia
    try:
        return proximo_dia_util_bancario_em_ou_apos(base, contexto.calendario_financeiro)
    except Exception:
        return base


def _construir_extrato_passado(contexto: Any) -> list[dict[str, Any]]:
    replay = getattr(contexto, 'replay_passado', None)
    log = getattr(replay, 'log_passado', None) if replay is not None else None
    if not isinstance(log, pd.DataFrame) or len(log) == 0:
        return []
    limiar = obter_limiar_residuo_resolvido(contexto.pacote_config.conteudo)
    quadro = log.copy()
    if {'Data', 'Sequencia Saque'}.issubset(quadro.columns):
        quadro = quadro.sort_values(['Data', 'Sequencia Saque'], kind='stable')
    chave = 'Despesa ID' if 'Despesa ID' in quadro.columns else None
    linhas: list[dict[str, Any]] = []
    if chave is not None:
        quadro['_ordem_saida'] = range(len(quadro))
        agreg = (
            quadro.sort_values(['Data', '_ordem_saida'], kind='stable')
            .groupby(chave, dropna=False, sort=False)
            .agg({
                'Data': 'last',
                'Conta': 'last' if 'Conta' in quadro.columns else 'first',
                'Liquido': 'sum' if 'Liquido' in quadro.columns else 'first',
                'Bruto': 'sum' if 'Bruto' in quadro.columns else 'first',
                'Imposto': 'sum' if 'Imposto' in quadro.columns else 'first',
                'Saldo Antes': 'first' if 'Saldo Antes' in quadro.columns else 'last',
                'Saldo Remanescente': 'last' if 'Saldo Remanescente' in quadro.columns else 'first',
                'Lote': lambda s: ' + '.join(dict.fromkeys([str(x) for x in s if str(x).strip()])),
            })
            .reset_index()
        )
        for _, row in agreg.iterrows():
            rem = _round_monetario(row.get('Saldo Remanescente'), 0.0)
            if rem != '' and rem <= limiar:
                rem = 0.0
            linhas.append({
                'Data': _fmt_data(row.get('Data')),
                'Conta': row.get('Conta') or '',
                'Despesa ID': row.get(chave) or '',
                'Lote': row.get('Lote') or '',
                'Lotes usados': row.get('Lote') or '',
                'Saldo Antes': _round_monetario(row.get('Saldo Antes'), None),
                'Bruto': _round_monetario(row.get('Bruto'), 0.0),
                'Imposto': _round_monetario(row.get('Imposto'), 0.0),
                'Líquido': _round_monetario(row.get('Liquido'), 0.0),
                'Saldo Remanescente': rem,
            })
        linhas.sort(key=lambda x: str(x.get('Data') or ''), reverse=True)
        return linhas
    for _, row in quadro.iterrows():
        rem = _round_monetario(row.get('Saldo Remanescente'), 0.0)
        if rem != '' and rem <= limiar:
            rem = 0.0
        linhas.append({
            'Data': _fmt_data(row.get('Data')),
            'Conta': row.get('Conta') or '',
            'Despesa ID': row.get('Despesa ID') or '',
            'Lote': row.get('Lote') or '',
            'Lotes usados': row.get('Lote') or '',
            'Saldo Antes': _round_monetario(row.get('Saldo Antes'), None),
            'Bruto': _round_monetario(row.get('Bruto'), 0.0),
            'Imposto': _round_monetario(row.get('Imposto'), 0.0),
            'Líquido': _round_monetario(row.get('Liquido'), 0.0),
            'Saldo Remanescente': rem,
        })
    linhas.sort(key=lambda x: str(x.get('Data') or ''), reverse=True)
    return linhas


def _construir_extrato_futuro(contexto: Any) -> list[dict[str, Any]]:
    quadro = _quadro_futuro_preferencial(contexto)
    if not isinstance(quadro, pd.DataFrame) or len(quadro) == 0:
        return []
    mapa_resumos = _mapa_resumos_futuros(contexto, quadro)
    mapa_central = _mapa_pagamentos_central(contexto)
    linhas: list[dict[str, Any]] = []
    for _, row in quadro.iterrows():
        row_dict = row.to_dict()
        pagamento_id = str(row_dict.get('pagamento_id') or '').strip()
        valor = round(float(row.get('valor_pagamento') or 0.0), 2)
        central = mapa_central.get(pagamento_id, {})
        resumo = _resumo_futuro(contexto, pagamento_id, row_dict, mapa_resumos, mapa_central)
        liquido = _round_monetario(resumo.get('Líquido'), '')
        estrategia_real = _primeiro_texto_preenchido(
            row_dict.get('estrategia_recomendada'),
            central.get('estrategia_recomendada'),
            row_dict.get('tipo_fonte_escolhida'),
            central.get('tipo_fonte_escolhida'),
            row_dict.get('tipo_fonte'),
            central.get('tipo_fonte'),
            row_dict.get('fonte_escolhida'),
            central.get('fonte_escolhida'),
        )
        lote_sugerido_real = _primeiro_texto_preenchido(
            resumo.get('Lote sugerido'),
            row_dict.get('lote_recomendado'),
            row_dict.get('lote_id_escolhido'),
            central.get('lote_final_central'),
            central.get('lote_sugerido_original'),
        )
        lote_reserva_real = _primeiro_texto_preenchido(row_dict.get('lote_reserva'), central.get('lote_reserva'))
        estrategia = _texto_decisao(estrategia_real)
        lote_sugerido = _texto_decisao(lote_sugerido_real)
        lote_reserva = _texto_lote_reserva(lote_reserva_real, lote_sugerido_real)
        cobertura_real = row_dict.get('cobertura_integral_recomendada')
        if cobertura_real is None:
            cobertura_real = central.get('pagamento_totalmente_coberto_central')
        if isinstance(cobertura_real, bool):
            cobertura_txt = 'sim' if cobertura_real else 'não'
        elif liquido != '':
            cobertura_txt = 'sim' if float(liquido) + 0.01 >= valor else 'não'
        else:
            cobertura_txt = 'não determinado'
        linhas.append({
            'Data': _fmt_data(row.get('data_pagamento')),
            'Conta': row.get('descricao_pagamento') or '',
            'Despesa ID': pagamento_id,
            'Valor': valor,
            'Lote sugerido': lote_sugerido,
            'Saldo Antes': resumo.get('Saldo Antes', ''),
            'Bruto': resumo.get('Bruto', ''),
            'Imposto': resumo.get('Imposto', ''),
            'Líquido': liquido,
            'Saldo Remanescente': resumo.get('Saldo Remanescente', ''),
            'Cobertura integral': cobertura_txt,
            'Estratégia': estrategia,
            'Pacote do dia': _texto_pacote_do_dia({**central, **row_dict}, estrategia),
            'Lote reserva': lote_reserva,
            'Necessita switching': _texto_necessita_switching({**central, **row_dict}, estrategia),
            'Switching antes do pagamento': 'sim' if bool(row_dict.get('switching_antes_pagamento')) else 'não',
            'Switching depois do pagamento': 'sim' if bool(row_dict.get('switching_depois_pagamento')) else 'não',
            'Motivo bloqueio lote': _texto_decisao(row_dict.get('motivo_bloqueio_lote')) if str(row_dict.get('motivo_bloqueio_lote') or '').strip() else '',
            'Status recomendação': _texto_decisao(row_dict.get('status_recomendacao')) if str(row_dict.get('status_recomendacao') or '').strip() else 'não determinado',
        })
    return linhas




def _texto_decisao(valor: Any) -> str:
    txt = str(valor or '').strip()
    return txt if txt else 'não determinado'


def _texto_pacote_do_dia(row: dict[str, Any], estrategia: str) -> str:
    pacote_real = str(row.get('pacote_dia_escolhido') or '').strip()
    if pacote_real:
        return pacote_real
    if estrategia == 'sem_switching' or estrategia == 'combinacao_minima':
        return 'pay_only'
    if estrategia == 'switching_simples':
        data_pag = row.get('data_pagamento')
        data_sw = row.get('data_sugerida_switching')
        if data_pag is not None and data_sw is not None:
            try:
                data_pag_cmp = data_pag.isoformat() if hasattr(data_pag, 'isoformat') else str(data_pag)
                data_sw_cmp = data_sw.isoformat() if hasattr(data_sw, 'isoformat') else str(data_sw)
                return 'switch_then_pay' if data_sw_cmp <= data_pag_cmp else 'pay_then_switch'
            except Exception:
                return 'não determinado'
    return 'não determinado'


def _texto_necessita_switching(row: dict[str, Any], estrategia: str) -> str:
    valor = row.get('necessita_switching')
    if valor is None:
        valor = row.get('necessidade_switching')
    if isinstance(valor, bool):
        return 'sim' if valor else 'não'
    if hasattr(valor, 'item'):
        try:
            convertido = valor.item()
            if isinstance(convertido, bool):
                return 'sim' if convertido else 'não'
            valor = convertido
        except Exception:
            pass
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        if valor == 1:
            return 'sim'
        if valor == 0:
            return 'não'
    txt = str(valor or '').strip().lower()
    if txt in {'sim', 'true', '1'}:
        return 'sim'
    if txt in {'não', 'nao', 'false', '0'}:
        return 'não'
    if estrategia == 'switching_simples':
        return 'sim'
    return 'não determinado'


def _primeiro_texto_preenchido(*valores: Any) -> str:
    for valor in valores:
        txt = str(valor or '').strip()
        if txt:
            return txt
    return ''


def _texto_lote_reserva(lote_reserva: Any, lote_sugerido: Any) -> str:
    reserva = str(lote_reserva or '').strip()
    sugerido = str(lote_sugerido or '').strip()
    if not reserva:
        return 'não determinado'
    if sugerido and reserva == sugerido:
        return 'não determinado'
    return reserva

def _construir_switchings(contexto: Any, limite: int = 30) -> list[dict[str, Any]]:
    shadow = getattr(contexto, 'switching_economico_shadow', None)
    plano = getattr(shadow, 'plano_shadow', None) if shadow is not None else None
    linhas: list[dict[str, Any]] = []
    lotes_by_id = {str(l.id): l for l in (getattr(getattr(contexto, 'replay_passado', None), 'lotes_apos_replay', []) or [])}
    if isinstance(plano, pd.DataFrame) and len(plano):
        plano_f = plano.copy()
        if 'recomendado_shadow' in plano_f.columns:
            plano_f = plano_f[plano_f['recomendado_shadow'].fillna(False)]
        plano_f = plano_f.sort_values(['ganho_liquido_estimado', 'score_switch_shadow', 'lote_id'], ascending=[False, False, True], kind='stable')
        usados: set[str] = set()
        for _, row in plano_f.iterrows():
            lote_id = str(row.get('lote_id') or '')
            if not lote_id or lote_id in usados:
                continue
            lote = lotes_by_id.get(lote_id)
            if lote is None:
                continue
            destino_rank = _ranking_destino_para_lote(contexto, lote) or {}
            data_sug = _data_sugerida_switching_lote(contexto, lote)
            ganho = _round_monetario(row.get('ganho_liquido_estimado'), _round_monetario(destino_rank.get('proxy_terminal_destino'), 0.0))
            valor_liq = _round_monetario(lote.valor_liquido_hoje(contexto.execucao.data_referencia, tabela_iof=contexto.tabela_iof, faixas_ir=contexto.faixas_ir), 0.0)
            linhas.append({
                'Data sugerida': _fmt_data(data_sug),
                'Data': _fmt_data(data_sug),
                'Lote origem': lote_id,
                'Produto origem': getattr(lote, 'investimento', '') if lote is not None else row.get('produto_origem_nome') or '',
                'Produto destino switching': destino_rank.get('nome') or '',
                'Destino': destino_rank.get('nome') or '',
                'Ganho estimado': ganho,
                'Valor líquido origem': valor_liq,
                'Status': 'destino ranqueado elegível',
            })
            usados.add(lote_id)
            if len(linhas) >= limite:
                break
    return linhas


def _construir_ranking_amostra(contexto: Any, limite: int = 10) -> list[dict[str, Any]]:
    ranking = getattr(contexto, 'ranking_carteira', None)
    destinos = getattr(ranking, 'quadro_destinos_switch', None) if ranking is not None else None
    if not isinstance(destinos, pd.DataFrame) or len(destinos) == 0:
        return []
    linhas = []
    for _, row in destinos.head(limite).iterrows():
        status = str(row.get('Status_Confirmação') or '').strip()
        linhas.append({
            'Rank': row.get('rank_destino'),
            'Produto': row.get('nome'),
            'Score': row.get('score_final'),
            'Proxy terminal': row.get('proxy_terminal_destino'),
            'Liquidez': row.get('liquidez_dias'),
            'Carência': row.get('carencia_dias'),
            'Ticket mín.': row.get('aplicacao_minima'),
            'Status': 'elegível' if status in {'', 'Confirmado', 'confirmado'} else status,
        })
    return linhas


def _construir_lotes_situacao(contexto: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    replay = getattr(contexto, 'replay_passado', None)
    if replay is None:
        return [], []
    data_referencia = contexto.execucao.data_referencia
    cal = contexto.calendario_financeiro
    config = contexto.pacote_config.conteudo
    serie_cdi = getattr(getattr(contexto, 'cache_cdi', None), 'serie_cdi', None)
    limiar = obter_limiar_residuo_resolvido(config)
    tabela_iof = contexto.tabela_iof
    faixas_ir = contexto.faixas_ir
    log = replay.log_passado.copy() if isinstance(getattr(replay, 'log_passado', None), pd.DataFrame) else None
    lotes_ativos: list[dict[str, Any]] = []
    lotes_exauridos: list[dict[str, Any]] = []

    def _ultimo_uso_lote(lote_id: Any) -> str:
        if log is None or len(log) == 0 or 'Lote' not in log.columns:
            return ''
        sub = log[log['Lote'].fillna('').astype(str) == str(lote_id)]
        if len(sub) == 0:
            return ''
        data_ult = sub['Data'].max() if 'Data' in sub.columns else None
        return data_ult.isoformat() if hasattr(data_ult, 'isoformat') else str(data_ult or '')

    for lote in sorted(replay.lotes_apos_replay, key=lambda x: (x.data_recebimento, x.data_aplicacao, x.id)):
        if lote.data_recebimento > data_referencia or lote.data_aplicacao > data_referencia:
            continue
        try:
            saldo_bruto = round(float(lote.valor_bruto_em_data(data_referencia, cal, serie_cdi=serie_cdi, data_base_referencia=data_referencia) or 0.0), 2)
            saldo_liquido = round(float(lote.valor_liquido_em_data(data_referencia, cal, tabela_iof=tabela_iof, faixas_ir=faixas_ir, serie_cdi=serie_cdi, data_base_referencia=data_referencia) or 0.0), 2)
        except Exception:
            saldo_bruto = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
            saldo_liquido = round(float(lote.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
        saldo_rem = round(float(getattr(lote, 'principal_remanescente', 0.0) or 0.0), 2)
        ultimo_uso_txt = _ultimo_uso_lote(lote.id)
        exaurido = bool(lote.esgotado or saldo_bruto <= limiar or saldo_liquido <= limiar or saldo_rem <= limiar)

        # V218: para lotes ativos, a idade do investimento deve usar a data
        # atual/de referência da execução; para lotes exauridos, preserva-se a
        # data do último uso como referência histórica. Em ambos os casos, a
        # contagem parte da data de aplicação, nunca da data de recebimento.
        data_base_tempo = data_referencia
        if exaurido and ultimo_uso_txt:
            try:
                data_base_tempo = date.fromisoformat(str(ultimo_uso_txt))
            except Exception:
                data_base_tempo = data_referencia
        idade_lote_v218 = calcular_dias_lote(
            lote.data_aplicacao,
            data_base_tempo,
            cal,
            serie_cdi=serie_cdi,
            data_fechamento_referencia=data_base_tempo,
        )
        dias_corridos = idade_lote_v218["dias_corridos"]
        dias_uteis = idade_lote_v218["dias_uteis"]
        saldo_bruto_exib, saldo_liquido_exib, saldo_rem_exib = normalizar_valores_situacao_atual_exaurida(saldo_bruto=saldo_bruto, saldo_liquido=saldo_liquido, saldo_rem=saldo_rem, exaurido=exaurido)
        linha = {
            'Lote': lote.id,
            'Recebimento': _fmt_data(lote.data_recebimento),
            'Aplicação': _fmt_data(lote.data_aplicacao),
            'Último uso': ultimo_uso_txt,
            'Produto': lote.investimento,
            'Dias corridos': dias_corridos,
            'Dias úteis': dias_uteis,
            'Valor original': round(float(getattr(lote, 'valor_inicial', 0.0) or 0.0), 2),
            'Bruto': saldo_bruto_exib,
            'Líquido': saldo_liquido_exib,
            'Saldo rem': saldo_rem_exib,
        }
        if exaurido:
            lotes_exauridos.append(linha)
        else:
            lotes_ativos.append(linha)
    lotes_exauridos.sort(key=lambda item: (str(item.get('Último uso') or ''), str(item.get('Aplicação') or ''), str(item.get('Lote') or '')), reverse=True)
    lotes_ativos.sort(key=lambda item: (str(item.get('Aplicação') or ''), str(item.get('Lote') or '')), reverse=True)
    return lotes_ativos, lotes_exauridos


def _construir_recebidos_atuais(contexto: Any) -> list[dict[str, Any]]:
    recebidos = getattr(contexto, 'recebidos_auditaveis', None)
    quadro = getattr(recebidos, 'quadro_recebidos_auditaveis', None) if recebidos is not None else None
    if not isinstance(quadro, pd.DataFrame) or len(quadro) == 0:
        return []
    quadro = quadro.sort_values(by=['data_recebimento', 'lote_id_origem', 'recebido_id'], kind='stable').reset_index(drop=True)
    linhas = []
    for _, row in quadro.iterrows():
        linhas.append({
            'Recebido': row.get('recebido_id'),
            'Lote origem': row.get('lote_id_origem'),
            'Recebimento': _fmt_data(row.get('data_recebimento')),
            'Aplicação': _fmt_data(row.get('data_aplicacao')),
            'Valor bruto': _round_monetario(row.get('valor_bruto'), 0.0),
            'Valor líquido': _round_monetario(row.get('valor_liquido'), 0.0),
            'Status': row.get('status_recebido'),
            'Destino': row.get('destino_potencial'),
            'Pagamentos vinculados': int(row.get('qtd_pagamentos_vinculados') or 0),
            'Valor vinculado': _round_monetario(row.get('valor_total_vinculado'), 0.0),
            'Residual aplicação': _round_monetario(row.get('valor_residual_para_aplicacao_origem'), 0.0),
            'Disponível ref': 'sim' if bool(row.get('disponivel_na_data_referencia', False)) else 'não',
            'Observação': row.get('observacao_auditavel') or '',
        })
    return linhas


def _linhas_fechamento_atual(contexto: Any) -> list[dict[str, Any]]:
    resumo = resumir_fechamento_situacao_atual(data_referencia=contexto.execucao.data_referencia, calendario_financeiro=contexto.calendario_financeiro, serie_cdi=contexto.cache_cdi.serie_cdi)
    return [
        {'Métrica': 'Data de referência', 'Valor': resumo.get('data_referencia')},
        {'Métrica': 'Status do fechamento econômico', 'Valor': resumo.get('status_fechamento')},
        {'Métrica': 'Fonte do fechamento', 'Valor': resumo.get('fonte_fechamento')},
        {'Métrica': 'Fechamentos com fallback CDI', 'Valor': resumo.get('qtd_fechamentos_fallback_cdi', 0)},
        {'Métrica': 'Último fator explícito CDI', 'Valor': resumo.get('data_ultimo_fator_explicito_cdi')},
        {'Métrica': 'Data confirmada da série', 'Valor': resumo.get('data_fechamento_confirmado')},
        {'Métrica': 'Leitura auditável', 'Valor': resumo.get('observacao')},
    ]


def _linhas_resumo_recebidos(contexto: Any) -> list[dict[str, Any]]:
    resumo = getattr(getattr(contexto, 'recebidos_auditaveis', None), 'auditoria', {}).get('resumo', {}) if getattr(contexto, 'recebidos_auditaveis', None) is not None else {}
    return [
        {'Métrica': 'Total de recebidos', 'Valor': resumo.get('total_recebidos', 0)},
        {'Métrica': 'Valor total bruto', 'Valor': resumo.get('valor_total_bruto', 0.0)},
        {'Métrica': 'Status recebido', 'Valor': str(resumo.get('status_recebido', {}))},
        {'Métrica': 'Destino potencial', 'Valor': str(resumo.get('destino_potencial', {}))},
        {'Métrica': 'Recebidos com pagamento vinculado', 'Valor': resumo.get('recebidos_com_pagamento_vinculado', 0)},
        {'Métrica': 'Recebidos em janela pré-aplicação', 'Valor': resumo.get('recebidos_em_janela_pre_aplicacao', 0)},
        {'Métrica': 'Recebidos usados antes da aplicação', 'Valor': resumo.get('recebidos_usados_antes_da_aplicacao_observado', 0)},
    ]


def construir_saida_canonica(contexto: Any, *, versao: str = 'V203') -> PacoteSaidaCanonica:
    extrato_passado = _construir_extrato_passado(contexto)
    extrato_futuro = _construir_extrato_futuro(contexto)
    switchings = _construir_switchings(contexto)
    ranking_amostra = _construir_ranking_amostra(contexto)
    lotes_ativos, lotes_exauridos = _construir_lotes_situacao(contexto)
    recebidos_atuais = _construir_recebidos_atuais(contexto)
    auditoria = {
        'origem': 'nucleo.saida_canonica.construir_saida_canonica',
        'camada_unica_saida': True,
        'qtd_extrato_passado': len(extrato_passado),
        'qtd_extrato_futuro': len(extrato_futuro),
        'qtd_switchings': len(switchings),
        'qtd_lotes_ativos': len(lotes_ativos),
        'qtd_lotes_exauridos': len(lotes_exauridos),
        'qtd_futuro_sem_cobertura_integral': sum(1 for item in extrato_futuro if item.get('Cobertura integral') != 'sim'),
        'qtd_futuro_multifonte': sum(1 for item in extrato_futuro if '+' in str(item.get('Lote sugerido') or '')),
    }
    return PacoteSaidaCanonica(
        versao=versao,
        data_referencia=_fmt_data(contexto.execucao.data_referencia),
        extrato_passado=extrato_passado,
        extrato_futuro=extrato_futuro,
        switchings=switchings,
        ranking_amostra=ranking_amostra,
        lotes_ativos=lotes_ativos,
        lotes_exauridos=lotes_exauridos,
        recebidos_atuais=recebidos_atuais,
        fechamento_atual=_linhas_fechamento_atual(contexto),
        resumo_recebidos=_linhas_resumo_recebidos(contexto),
        auditoria=auditoria,
    )
