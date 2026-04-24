from __future__ import annotations

from pathlib import Path
from copy import deepcopy
from datetime import date, timedelta
from typing import Iterable
import sys

import pandas as pd

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline, obter_limiar_residuo_resolvido
from nucleo.identidade_baseline import caminho_artifact, caminho_saida_operacional, nome_relatorio_operacional
from nucleo.calendario_financeiro import contar_dias_rendimento, proximo_dia_util_bancario_em_ou_apos
from nucleo.rotulagem_fechamento import resumir_fechamento_situacao_atual
from nucleo.nucleo_financeiro_minimo import executar_saque_lote
from nucleo.utilitarios_neutros import normalizar_valores_situacao_atual_exaurida

SAIDA_INTERNA = caminho_saida_operacional(RAIZ, nome_relatorio_operacional())
SAIDA_EXTERNA = caminho_artifact(nome_relatorio_operacional())
def _as_rows(iterable: Iterable[dict], columns: list[tuple[str, str]]):
    for item in iterable:
        yield [item.get(src) for src, _ in columns]


def _apply_table_style(ws, headers: list[str], rows: list[list], *, start_row: int = 1, title: str | None = None, freeze: bool = False):
    ws.sheet_view.showGridLines = False
    header_fill = PatternFill('solid', fgColor='1F4E78')
    header_font = Font(color='FFFFFF', bold=True)
    title_fill = PatternFill('solid', fgColor='D9EAF7')
    title_font = Font(color='1F1F1F', bold=True)
    thin_gray = Side(style='thin', color='D9E1F2')

    header_row = start_row
    if title:
        title_row = start_row
        ws.cell(row=title_row, column=1, value=title).fill = title_fill
        ws.cell(row=title_row, column=1).font = title_font
        header_row = start_row + 1

    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = Border(bottom=thin_gray)
    for row_offset, row in enumerate(rows, start=1):
        row_idx = header_row + row_offset
        for col_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            if isinstance(value, (int, float)):
                cell.alignment = Alignment(horizontal='right')
            else:
                cell.alignment = Alignment(horizontal='left')

    if freeze:
        ws.freeze_panes = f'A{header_row + 1}'
    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(len(headers))}{max(header_row + len(rows), header_row)}"

    currency_cols = {'Valor', 'Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente', 'Aplicação Mínima', 'Bruto Atual', 'Líquido Atual', 'Saldo rem', 'Score Final', 'Valor Original', 'Valor bruto', 'Valor líquido', 'Valor vinculado', 'Residual aplicação', 'Saldo Antes temporal', 'Bruto temporal', 'Imposto temporal', 'Líquido temporal', 'Saldo Remanescente temporal', 'Saldo Antes dinâmico', 'Bruto dinâmico', 'Imposto dinâmico', 'Líquido dinâmico', 'Saldo Remanescente dinâmico', 'Score proxy', 'Score final dinâmico', 'Score proxy original', 'Score proxy heurística', 'Score ajustado heurística', 'Penalidade preservação estratégica', 'Reserva planejada fonte', 'Saldo Antes heurística', 'Bruto heurística', 'Imposto heurística', 'Líquido heurística', 'Saldo Remanescente heurística'}
    percent_cols = {'Taxa Base CDI', 'Taxa Bônus CDI'}
    int_cols = {'Dias Corridos', 'Dias Úteis', 'Dias até evento', 'Rank Global', 'Rank Família', 'Dias Bônus', 'Carência Dias', 'Pagamentos vinculados'}

    for col_idx, header in enumerate(headers, start=1):
        letter = get_column_letter(col_idx)
        max_len = len(header)
        for row_idx in range(header_row + 1, ws.max_row + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            value = cell.value
            if value is None:
                continue
            max_len = max(max_len, len(str(value)))
            if header in currency_cols and isinstance(value, (int, float)):
                cell.number_format = 'R$ #,##0.00;[Red](R$ #,##0.00);-'
            elif header in percent_cols and isinstance(value, (int, float)):
                cell.number_format = '0.0%'
            elif header in int_cols and isinstance(value, (int, float)):
                cell.number_format = '0'
            elif 'Data' in header and hasattr(value, 'year'):
                cell.number_format = 'dd/mm/yyyy'
        ws.column_dimensions[letter].width = min(max_len + 2, 32)

    return header_row + len(rows)






def _sheet_exists(wb, title: str) -> bool:
    return any(ws.title == title for ws in wb.worksheets)


def _drop_sheet_if_exists(wb, title: str) -> None:
    for ws in list(wb.worksheets):
        if ws.title == title:
            wb.remove(ws)
            break


def _dataframe_to_rows(df):
    if df is None or len(df) == 0:
        return []
    rows = []
    safe = df.copy().infer_objects(copy=False)
    safe = safe.astype(object).where(pd.notna(safe), '')
    for row in safe.to_dict('records'):
        rows.append(list(row.values()))
    return rows


def _adicionar_abas_ranking(wb, contexto):
    ranking = getattr(contexto, 'ranking_carteira', None)
    if ranking is None:
        return

    _drop_sheet_if_exists(wb, 'Carteira')
    ws_carteira = wb.create_sheet('Carteira')
    quadro_carteira = ranking.quadro_destinos_switch.copy()
    cols_carteira = [
        'rank_destino', 'nome', 'score_final', 'proxy_terminal_destino', 'retorno_anual_proxy',
        'liquidez_dias', 'carencia_dias', 'aplicacao_minima', 'aplicacao_maxima',
        'tipo_produto', 'somente_combo', 'Status_Confirmação', 'Campos_Pendentes'
    ]
    cols_carteira = [c for c in cols_carteira if c in quadro_carteira.columns]
    quadro_carteira = quadro_carteira[cols_carteira].copy()
    headers_carteira = [
        'Rank', 'Produto', 'Score Final', 'Proxy Terminal', 'Retorno Proxy aa', 'Liquidez Dias',
        'Carência Dias', 'Aplicação Mínima', 'Aplicação Máxima', 'Tipo Produto',
        'Somente Combo', 'Status Confirmação', 'Campos Pendentes'
    ][:len(cols_carteira)]
    _apply_table_style(ws_carteira, headers_carteira, _dataframe_to_rows(quadro_carteira), freeze=True)

    _drop_sheet_if_exists(wb, 'Top30')
    ws_top30 = wb.create_sheet('Top30')
    top30 = ranking.top30.copy()
    _apply_table_style(ws_top30, list(top30.columns), _dataframe_to_rows(top30), freeze=True)

    _drop_sheet_if_exists(wb, 'Resumo Switching')
    _drop_sheet_if_exists(wb, 'Resumo')
    ws_resumo = wb.create_sheet('Resumo Switching')
    resumo_rows = [
        ['produtos_total', ranking.resumo.get('produtos_total')],
        ['produtos_ativos_ranqueados', ranking.resumo.get('produtos_ativos_ranqueados')],
        ['qtd_destinos_switch', ranking.auditoria.get('qtd_destinos_switch')],
        ['destino_top1', ranking.auditoria.get('destino_top1')],
        ['qtd_diffs_materiais_nucleo', ranking.validacao.get('qtd_diffs_materiais_nucleo')],
        ['aceite_nucleo', ranking.validacao.get('aceite_nucleo')],
    ]
    _apply_table_style(ws_resumo, ['indicador', 'valor'], resumo_rows, freeze=False)

    _drop_sheet_if_exists(wb, 'Validacao')
    ws_val = wb.create_sheet('Validacao')
    validacao_rows = []
    validacao_rows.append([str(ranking.validacao.get('colunas')), ranking.validacao.get('qtd_diffs_materiais_nucleo'), ranking.validacao.get('aceite_nucleo'), ranking.auditoria.get('metodo')])
    _apply_table_style(ws_val, ['colunas', 'qtd_diffs_materiais_nucleo', 'aceite_nucleo', 'metodo'], validacao_rows, freeze=False)


def _limpar_abas_legadas(wb):
    legadas = [
        'Auditoria temporal', 'Reescolha dinâmica', 'Heurística conjunta', 'Planejamento conjunto',
        'Microplanejamento v2', 'Recomp. central v1', 'Melhores produtos', 'Ranking_Completo', 'Destinos_Switch', 'Resumo'
    ]
    for title in legadas:
        _drop_sheet_if_exists(wb, title)
    for ws in wb.worksheets:
        if ws.title == 'Rec. pgto+switch':
            ws.title = 'Switching'
            break

def _calcular_resumo_financeiro_fonte(contexto, decisao: dict) -> dict[str, object]:
    if not decisao:
        return {
            'Saldo Antes': '',
            'Bruto': '',
            'Imposto': '',
            'Líquido': '',
            'Saldo Remanescente': '',
        }
    valor_pagamento = round(float(decisao.get('valor_pagamento') or 0.0), 2)
    saldo_antes = round(float(decisao.get('valor_disponivel_escolhido') or 0.0), 2)
    tipo_fonte = str(decisao.get('tipo_fonte_escolhida') or '')
    lote_id = str(decisao.get('lote_id_escolhido') or '')

    if tipo_fonte == 'lote_resgatavel' and lote_id:
        lote_original = next((l for l in contexto.replay_passado.lotes_apos_replay if str(l.id) == lote_id), None)
        if lote_original is not None:
            lote = deepcopy(lote_original)
            movimento = executar_saque_lote(
                lote,
                valor_pagamento,
                contexto.execucao.data_referencia,
                tabela_iof=contexto.tabela_iof,
                faixas_ir=contexto.faixas_ir,
            )
            if movimento is not None:
                return {
                    'Saldo Antes': round(float(movimento.get('saldo_antes') or 0.0), 2),
                    'Bruto': round(float(movimento.get('bruto') or 0.0), 2),
                    'Imposto': round(float(movimento.get('imposto') or 0.0), 2),
                    'Líquido': round(float(movimento.get('liquido') or 0.0), 2),
                    'Saldo Remanescente': round(float(movimento.get('saldo_remanescente') or 0.0), 2),
                }

    bruto = min(valor_pagamento, saldo_antes) if saldo_antes else valor_pagamento
    imposto = 0.0
    liquido = bruto
    saldo_rem = max(saldo_antes - bruto, 0.0) if saldo_antes else ''
    return {
        'Saldo Antes': saldo_antes if saldo_antes else '',
        'Bruto': round(float(bruto), 2) if bruto != '' else '',
        'Imposto': imposto,
        'Líquido': round(float(liquido), 2) if liquido != '' else '',
        'Saldo Remanescente': round(float(saldo_rem), 2) if saldo_rem != '' else '',
    }


def _ultimo_fator_cache_contexto(contexto):
    serie = getattr(getattr(contexto, 'cache_cdi', None), 'serie_cdi', {}) or {}
    if not serie:
        return 1.0, None
    try:
        data_ult = max(serie.keys())
        fator = float(serie.get(data_ult) or 1.0)
        return fator if fator > 0 else 1.0, data_ult
    except Exception:
        return 1.0, None


def _mapa_saldo_disponivel_contexto(contexto):
    mapa = {}
    pacote = getattr(contexto, 'saldo_disponivel_geral', None)
    quadro = getattr(pacote, 'quadro_saldo_disponivel', None) if pacote is not None else None
    if isinstance(quadro, pd.DataFrame) and len(quadro):
        for _, row in quadro.iterrows():
            mapa[str(row.get('pagamento_id') or '').strip()] = row.to_dict()
    return mapa


def _avancar_lote_para_data_contexto(lote, data_origem, data_alvo, contexto):
    if data_alvo is None or data_origem is None or data_alvo <= data_origem:
        return
    fator_dia, _ = _ultimo_fator_cache_contexto(contexto)
    taxa_diaria = max(float(fator_dia) - 1.0, 0.0)
    data_cursor = data_origem
    while data_cursor < data_alvo:
        data_cursor = data_cursor + timedelta(days=1)
        lote.atualizar_juros(
            data_cursor,
            taxa_diaria,
            contexto.calendario_financeiro,
            serie_cdi=None,
            data_fechamento_referencia=data_cursor,
        )


def _mapa_resumos_futuros_contexto(contexto, quadro_futuro: pd.DataFrame) -> dict[str, dict[str, object]]:
    if not isinstance(quadro_futuro, pd.DataFrame) or len(quadro_futuro) == 0:
        return {}
    tabela_iof = contexto.tabela_iof
    faixas_ir = contexto.faixas_ir
    replay = getattr(contexto, 'replay_passado', None)
    lotes_orig = getattr(replay, 'lotes_apos_replay', []) if replay is not None else []
    lotes_estado = {str(l.id): deepcopy(l) for l in lotes_orig}
    lotes_data = {str(l.id): contexto.execucao.data_referencia for l in lotes_orig}
    saldo_map = _mapa_saldo_disponivel_contexto(contexto)
    consumo_saldo = 0.0
    resumos = {}
    quadro = quadro_futuro.copy().sort_values(['data_pagamento', 'pagamento_id'], kind='stable')
    for _, row in quadro.iterrows():
        pagamento_id = str(row.get('pagamento_id') or '').strip()
        data_pag = row.get('data_pagamento')
        valor = round(float(row.get('valor_pagamento') or 0.0), 2)
        lote_sug = str(row.get('lote_recomendado') or row.get('lote_id_escolhido') or row.get('fonte_base_escolhida') or row.get('tipo_fonte_escolhida') or '')
        resumo = {'Lote sugerido': lote_sug, 'Saldo Antes': '', 'Bruto': '', 'Imposto': '', 'Líquido': '', 'Saldo Remanescente': ''}
        if lote_sug in lotes_estado and data_pag is not None:
            lote = lotes_estado[lote_sug]
            _avancar_lote_para_data_contexto(lote, lotes_data.get(lote_sug, contexto.execucao.data_referencia), data_pag, contexto)
            lotes_data[lote_sug] = data_pag
            saldo_antes = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
            mov = executar_saque_lote(lote, valor, data_pag, tabela_iof=tabela_iof, faixas_ir=faixas_ir)
            if mov is not None:
                saldo_rem = round(float(mov.get('saldo_remanescente') or 0.0), 2)
                if saldo_rem <= obter_limiar_residuo_resolvido(contexto.pacote_config.conteudo):
                    saldo_rem = 0.0
                resumo = {
                    'Lote sugerido': lote_sug,
                    'Saldo Antes': round(float(mov.get('saldo_antes') or saldo_antes), 2),
                    'Bruto': round(float(mov.get('bruto') or 0.0), 2),
                    'Imposto': round(float(mov.get('imposto') or 0.0), 2),
                    'Líquido': round(float(mov.get('liquido') or 0.0), 2),
                    'Saldo Remanescente': saldo_rem,
                }
        elif lote_sug == 'saldo_disponivel_geral':
            base = saldo_map.get(pagamento_id, {})
            saldo_liq_base = round(float(base.get('saldo_disponivel_liquido') or base.get('saldo_disponivel_bruto') or 0.0), 2)
            saldo_antes = max(round(saldo_liq_base - consumo_saldo, 2), 0.0)
            bruto = min(valor, saldo_antes)
            imposto = 0.0
            liquido = bruto
            saldo_rem = max(round(saldo_antes - liquido, 2), 0.0)
            consumo_saldo = round(consumo_saldo + liquido, 2)
            resumo = {
                'Lote sugerido': lote_sug,
                'Saldo Antes': saldo_antes,
                'Bruto': bruto,
                'Imposto': imposto,
                'Líquido': liquido,
                'Saldo Remanescente': saldo_rem,
            }
        resumos[pagamento_id] = resumo
    return resumos


def _resumo_financeiro_futuro_preferencial(contexto, pagamento_id: str, decisao: dict, central: dict | None = None, mapa_resumos: dict[str, dict[str, object]] | None = None) -> dict[str, object]:
    mapa_resumos = mapa_resumos or {}
    resumo_mapa = mapa_resumos.get(str(pagamento_id or '').strip())
    if resumo_mapa:
        return resumo_mapa
    central = central or {}
    if central:
        return {
            'Lote sugerido': central.get('lote_final_central') or central.get('lote_sugerido_original') or decisao.get('lote_id_escolhido') or '',
            'Saldo Antes': round(float(central.get('saldo_antes_central') or 0.0), 2) if central.get('saldo_antes_central') not in (None, '') else '',
            'Bruto': round(float(central.get('bruto_central') or 0.0), 2) if central.get('bruto_central') not in (None, '') else '',
            'Imposto': round(float(central.get('imposto_central') or 0.0), 2) if central.get('imposto_central') not in (None, '') else '',
            'Líquido': round(float(central.get('liquido_central') or 0.0), 2) if central.get('liquido_central') not in (None, '') else '',
            'Saldo Remanescente': round(float(central.get('saldo_remanescente_central') or 0.0), 2) if central.get('saldo_remanescente_central') not in (None, '') else '',
        }
    resumo = _calcular_resumo_financeiro_fonte(contexto, decisao)
    resumo['Lote sugerido'] = str(decisao.get('lote_id_escolhido') or decisao.get('fonte_base_escolhida') or decisao.get('tipo_fonte_escolhida') or '')
    return resumo


def _data_sugerida_switching_planilha(contexto, lote):
    mapa = getattr(contexto.carteira_canonica, 'mapa_produtos', {}) or {}
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


def _destino_ranking_planilha(contexto, lote):
    ranking = getattr(contexto, 'ranking_carteira', None)
    if ranking is None or not isinstance(getattr(ranking, 'quadro_destinos_switch', None), pd.DataFrame):
        return None
    destinos = ranking.quadro_destinos_switch.copy()
    if len(destinos) == 0:
        return None
    origem_key = str(getattr(lote, 'produto_key', '') or '').strip()
    if 'produto_key' in destinos.columns:
        destinos = destinos[destinos['produto_key'].fillna('').astype(str).str.strip() != origem_key]
    status_col = 'Status_Confirmação' if 'Status_Confirmação' in destinos.columns else ('status_confirmacao' if 'status_confirmacao' in destinos.columns else None)
    if status_col is not None:
        destinos = destinos[destinos[status_col].fillna('').astype(str).isin(['', 'Confirmado', 'confirmado', 'Fortemente sustentado'])]
    if 'elegivel_switch_in' in destinos.columns:
        destinos = destinos[destinos['elegivel_switch_in'].fillna(False).astype(bool)]
    valor_liq = round(float(lote.valor_liquido_hoje(contexto.execucao.data_referencia, tabela_iof=contexto.tabela_iof, faixas_ir=contexto.faixas_ir) or 0.0), 2)
    if 'aplicacao_minima' in destinos.columns:
        elegiveis = destinos[destinos['aplicacao_minima'].fillna(0.0).astype(float) <= valor_liq + 1e-9]
        if len(elegiveis):
            destinos = elegiveis
    if len(destinos) == 0:
        return None
    destinos = destinos.sort_values(['rank_destino', 'score_final', 'nome'], ascending=[True, False, True], kind='stable') if 'rank_destino' in destinos.columns else destinos.sort_values(['score_final', 'nome'], ascending=[False, True], kind='stable')
    return destinos.iloc[0].to_dict()


def _switchings_oficiais_para_saida(contexto, limite=30):
    rows = []
    shadow = getattr(contexto, 'switching_economico_shadow', None)
    plano = getattr(shadow, 'plano_shadow', None) if shadow is not None else None
    lotes_by_id = {str(l.id): l for l in (getattr(getattr(contexto, 'replay_passado', None), 'lotes_apos_replay', []) or [])}
    if isinstance(plano, pd.DataFrame) and len(plano):
        plano_f = plano.copy()
        if 'recomendado_shadow' in plano_f.columns:
            plano_f = plano_f[plano_f['recomendado_shadow'].fillna(False)]
        plano_f = plano_f.sort_values(['ganho_liquido_estimado','score_switch_shadow','lote_id'], ascending=[False,False,True], kind='stable')
        usados = set()
        for _, row in plano_f.iterrows():
            lote_id = str(row.get('lote_id') or '')
            if not lote_id or lote_id in usados:
                continue
            lote = lotes_by_id.get(lote_id)
            if lote is None:
                continue
            destino = _destino_ranking_planilha(contexto, lote) or {}
            data_sug = _data_sugerida_switching_planilha(contexto, lote) if lote is not None else contexto.execucao.data_referencia
            rows.append([
                data_sug, '', '', '', '', '', 'switching_shadow',
                lote_id, '', '',
                data_sug, lote_id, destino.get('nome') or '',
                round(float(row.get('ganho_liquido_estimado') or destino.get('proxy_terminal_destino') or 0.0), 2),
                round(float(getattr(lote, 'valor_liquido_hoje', lambda *_args, **_kwargs: 0.0)(contexto.execucao.data_referencia, tabela_iof=contexto.tabela_iof, faixas_ir=contexto.faixas_ir) if lote is not None else 0.0), 2),
                'sim', '', '', '', 'destino ranqueado elegível',
            ])
            usados.add(lote_id)
            if len(rows) >= limite:
                break
    return rows[:limite]


def _classificar_lotes_situacao_atual(contexto):
    ctx = contexto.execucao
    cal = contexto.calendario_financeiro
    cache = contexto.cache_cdi
    rep = contexto.replay_passado
    tabela_iof = contexto.tabela_iof
    faixas_ir = contexto.faixas_ir
    limiar = obter_limiar_residuo_resolvido(contexto.pacote_config.conteudo)
    rows_ativos_ident = []
    rows_ativos_valores = []
    rows_exauridos_ident = []
    rows_exauridos_valores = []
    data_economica = ctx.data_referencia
    log = rep.log_passado.copy() if getattr(rep, 'log_passado', None) is not None else None

    def _ultimo_uso(lote_id):
        if not isinstance(log, pd.DataFrame) or len(log) == 0 or 'Lote' not in log.columns:
            return ''
        sub = log[log['Lote'].fillna('').astype(str) == str(lote_id)]
        if len(sub) == 0:
            return ''
        d = sub['Data'].max() if 'Data' in sub.columns else None
        return d.isoformat() if hasattr(d, 'isoformat') else str(d or '')

    for lote in sorted(rep.lotes_apos_replay, key=lambda x: (x.data_recebimento, x.data_aplicacao, x.id)):
        if lote.data_recebimento > ctx.data_referencia or lote.data_aplicacao > ctx.data_referencia:
            continue
        saldo_bruto = round(float(lote.valor_bruto_em_data(
            data_economica,
            cal,
            serie_cdi=cache.serie_cdi,
            data_base_referencia=ctx.data_referencia,
        ) or 0.0), 2)
        saldo_liquido = round(float(lote.valor_liquido_em_data(
            data_economica,
            cal,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            serie_cdi=cache.serie_cdi,
            data_base_referencia=ctx.data_referencia,
        ) or 0.0), 2)
        saldo_rem = round(float(getattr(lote, 'principal_remanescente', 0.0) or 0.0), 2)
        ultimo_uso_txt = _ultimo_uso(lote.id)
        data_base_tempo = ctx.data_referencia
        if ultimo_uso_txt:
            try:
                data_base_tempo = date.fromisoformat(str(ultimo_uso_txt))
            except Exception:
                data_base_tempo = ctx.data_referencia
        dias_corridos = max((data_base_tempo - lote.data_recebimento).days, 0)
        dias_uteis = 0 if data_base_tempo < lote.data_aplicacao else contar_dias_rendimento(
            lote.data_base_fiscal,
            data_base_tempo,
            cal,
            serie_cdi=cache.serie_cdi,
            data_fechamento_referencia=min(data_economica, data_base_tempo),
        )
        lote_exaurido_na_situacao = bool(lote.esgotado or saldo_bruto <= limiar or saldo_liquido <= limiar or saldo_rem <= limiar)
        saldo_bruto_exibicao, saldo_liquido_exibicao, saldo_rem_exibicao = normalizar_valores_situacao_atual_exaurida(
            saldo_bruto=saldo_bruto, saldo_liquido=saldo_liquido, saldo_rem=saldo_rem, exaurido=lote_exaurido_na_situacao,
        )
        linha_ident = [lote.id, lote.data_recebimento, lote.data_aplicacao, lote.investimento, dias_corridos, dias_uteis]
        linha_ident_ex = [lote.id, lote.data_recebimento, lote.data_aplicacao, ultimo_uso_txt, lote.investimento, dias_corridos, dias_uteis]
        linha_valores = [lote.id, round(float(getattr(lote, 'valor_inicial', 0.0) or 0.0), 2), saldo_bruto_exibicao, saldo_liquido_exibicao, saldo_rem_exibicao]
        if lote_exaurido_na_situacao:
            rows_exauridos_ident.append(linha_ident_ex)
            rows_exauridos_valores.append(linha_valores)
        else:
            rows_ativos_ident.append(linha_ident)
            rows_ativos_valores.append(linha_valores)
    rows_exauridos_ident.sort(key=lambda row: (str(row[3] or ''), str(row[2] or ''), str(row[0] or '')), reverse=True)
    # manter valores na mesma ordem da tabela de identificação dos exauridos
    rows_ativos_ident.sort(key=lambda row: (str(row[2] or ''), str(row[0] or '')), reverse=True)
    ordem_ex = [row[0] for row in rows_exauridos_ident]
    ordem_at = [row[0] for row in rows_ativos_ident]
    mapa_ex_val = {row[0]: row for row in rows_exauridos_valores}
    mapa_at_val = {row[0]: row for row in rows_ativos_valores}
    rows_exauridos_valores = [mapa_ex_val[lote_id] for lote_id in ordem_ex if lote_id in mapa_ex_val]
    rows_ativos_valores = [mapa_at_val[lote_id] for lote_id in ordem_at if lote_id in mapa_at_val]
    return rows_exauridos_ident, rows_exauridos_valores, rows_ativos_ident, rows_ativos_valores


def main() -> None:

    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ, instalar_automaticamente=False)
    cfg = contexto.pacote_config
    ctx = contexto.execucao
    cal = contexto.calendario_financeiro
    plan = contexto.pacote_planilha
    cart = contexto.carteira_canonica
    dados = contexto.dados_operacionais
    cache = contexto.cache_cdi
    tri = contexto.triagem_motor
    rep = contexto.replay_passado

    tabela_iof = contexto.tabela_iof
    faixas_ir = contexto.faixas_ir
    limiar = obter_limiar_residuo_resolvido(cfg.conteudo)

    wb = Workbook()
    ws_passado = wb.active
    ws_passado.title = 'Extrato Passado'
    log = rep.log_passado.copy().sort_values(by=['Data', 'Sequencia Saque'], kind='stable')
    cols_passado = [
        ('Data', 'Data'), ('Conta', 'Conta'), ('Despesa ID', 'Despesa ID'), ('Lote', 'Lote'),
        ('Saldo Antes', 'Saldo Antes'), ('Bruto', 'Bruto'), ('Imposto', 'Imposto'), ('Liquido', 'Líquido'),
        ('Dias Corridos', 'Dias Corridos'), ('Dias Úteis', 'Dias Úteis'), ('Saldo Remanescente', 'Saldo Remanescente'),
        ('Fase Operacional Lote', 'Fase')
    ]
    rows_passado = []
    for row in log.to_dict('records'):
        rem = round(float(row.get('Saldo Remanescente') or 0.0), 2)
        if rem <= limiar:
            row['Saldo Remanescente'] = 0.0
        rows_passado.append([row.get(src) for src, _ in cols_passado])
    _apply_table_style(ws_passado, [dst for _, dst in cols_passado], rows_passado, freeze=True)

    ws_futuro = wb.create_sheet('Extrato Futuro')
    gastos_futuros = dados.gastos_canonicos[dados.gastos_canonicos['futuro_ou_pendente_na_data_referencia'] == True].copy().sort_values(by=['data', 'despesa_id'], kind='stable')
    quadro_decisao = contexto.decisao_local_v1.quadro_decisao_local_v1.copy() if contexto.decisao_local_v1 is not None else None
    quadro_temporal = contexto.auditoria_temporal_decisao_local.quadro_auditoria_temporal.copy() if contexto.auditoria_temporal_decisao_local is not None else None
    quadro_reescolha = contexto.reescolha_dinamica_pos_quebra.quadro_reescolha_dinamica.copy() if contexto.reescolha_dinamica_pos_quebra is not None else None
    quadro_heuristica = contexto.heuristica_conjunta_parcial_bloco_critico.quadro_heuristica_conjunta_parcial.copy() if contexto.heuristica_conjunta_parcial_bloco_critico is not None else None
    quadro_planejamento = contexto.planejamento_conjunto_local_bloco_critico_v1.quadro_planejamento_conjunto_local.copy() if contexto.planejamento_conjunto_local_bloco_critico_v1 is not None else None
    quadro_microplanejamento = contexto.microplanejamento_conjunto_bloco_critico_v2.quadro_microplanejamento_conjunto.copy() if getattr(contexto, 'microplanejamento_conjunto_bloco_critico_v2', None) is not None else None
    quadro_central = contexto.recomputacao_sequencial_central_v1.quadro_recomputacao_sequencial_central.copy() if getattr(contexto, 'recomputacao_sequencial_central_v1', None) is not None else None
    quadro_recomendacao = contexto.motor_recomendacao_pagamentos_switching_v1.quadro_recomendacoes.copy() if getattr(contexto, 'motor_recomendacao_pagamentos_switching_v1', None) is not None else None
    mapa_decisao = {}
    mapa_temporal = {}
    mapa_reescolha = {}
    mapa_heuristica = {}
    mapa_planejamento = {}
    mapa_microplanejamento = {}
    mapa_central = {}
    mapa_recomendacao = {}
    if quadro_decisao is not None and len(quadro_decisao):
        for _, row_dec in quadro_decisao.iterrows():
            mapa_decisao[str(row_dec.get('pagamento_id') or '').strip()] = row_dec.to_dict()
    if quadro_temporal is not None and len(quadro_temporal):
        for _, row_tmp in quadro_temporal.iterrows():
            mapa_temporal[str(row_tmp.get('pagamento_id') or '').strip()] = row_tmp.to_dict()
    if quadro_reescolha is not None and len(quadro_reescolha):
        for _, row_dyn in quadro_reescolha.iterrows():
            mapa_reescolha[str(row_dyn.get('pagamento_id') or '').strip()] = row_dyn.to_dict()
    if quadro_heuristica is not None and len(quadro_heuristica):
        for _, row_h in quadro_heuristica.iterrows():
            mapa_heuristica[str(row_h.get('pagamento_id') or '').strip()] = row_h.to_dict()
    if quadro_planejamento is not None and len(quadro_planejamento):
        for _, row_p in quadro_planejamento.iterrows():
            mapa_planejamento[str(row_p.get('pagamento_id') or '').strip()] = row_p.to_dict()
    if quadro_microplanejamento is not None and len(quadro_microplanejamento):
        for _, row_m in quadro_microplanejamento.iterrows():
            mapa_microplanejamento[str(row_m.get('pagamento_id') or '').strip()] = row_m.to_dict()
    if quadro_central is not None and len(quadro_central):
        for _, row_c in quadro_central.iterrows():
            mapa_central[str(row_c.get('pagamento_id') or '').strip()] = row_c.to_dict()
    if quadro_recomendacao is not None and len(quadro_recomendacao):
        for _, row_r in quadro_recomendacao.iterrows():
            mapa_recomendacao[str(row_r.get('pagamento_id') or '').strip()] = row_r.to_dict()
    mapa_resumos_futuros = _mapa_resumos_futuros_contexto(contexto, quadro_recomendacao if quadro_recomendacao is not None and len(quadro_recomendacao) else quadro_decisao)
    rows_futuro = []
    for item in gastos_futuros.to_dict('records'):
        data_evt = item.get('data')
        dias_ate = max((data_evt - ctx.data_referencia).days, 0) if isinstance(data_evt, date) else None
        despesa_id = str(item.get('despesa_id') or '').strip()
        decisao = mapa_recomendacao.get(despesa_id, {}) or mapa_decisao.get(despesa_id, {})
        resumo_financeiro = _resumo_financeiro_futuro_preferencial(contexto, despesa_id, decisao, mapa_central.get(despesa_id, {}), mapa_resumos=mapa_resumos_futuros)
        temporal = mapa_temporal.get(despesa_id, {})
        dinamico = mapa_reescolha.get(despesa_id, {})
        heuristica = mapa_heuristica.get(despesa_id, {})
        planejamento = mapa_planejamento.get(despesa_id, {})
        microplanejamento = mapa_microplanejamento.get(despesa_id, {})
        central = mapa_central.get(despesa_id, {})
        recomendacao = mapa_recomendacao.get(despesa_id, {})
        rows_futuro.append([
            data_evt,
            item.get('descricao'),
            item.get('valor'),
            resumo_financeiro.get('Lote sugerido', ''),
            resumo_financeiro.get('Saldo Antes', ''),
            resumo_financeiro.get('Bruto', ''),
            resumo_financeiro.get('Imposto', ''),
            resumo_financeiro.get('Líquido', ''),
            resumo_financeiro.get('Saldo Remanescente', ''),
        ])
    headers_futuro = ['Data', 'Conta', 'Valor', 'Lote sugerido', 'Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente']
    _apply_table_style(ws_futuro, headers_futuro, rows_futuro, freeze=True)

    ws_temporal = wb.create_sheet('Auditoria temporal')
    quadro_temporal_full = contexto.auditoria_temporal_decisao_local.quadro_auditoria_temporal.copy() if contexto.auditoria_temporal_decisao_local is not None else None
    rows_temporal = []
    if quadro_temporal_full is not None and len(quadro_temporal_full):
        quadro_temporal_full = quadro_temporal_full.sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable')
        for _, row_tmp in quadro_temporal_full.iterrows():
            rows_temporal.append([
                row_tmp.get('data_pagamento'),
                row_tmp.get('descricao_pagamento'),
                row_tmp.get('pagamento_id'),
                row_tmp.get('valor_pagamento'),
                row_tmp.get('lote_id_escolhido'),
                row_tmp.get('status_local'),
                row_tmp.get('status_temporal'),
                row_tmp.get('sequencia_na_fonte'),
                row_tmp.get('saldo_antes_local'),
                row_tmp.get('saldo_antes_temporal'),
                row_tmp.get('bruto_temporal'),
                row_tmp.get('imposto_temporal'),
                row_tmp.get('liquido_temporal'),
                row_tmp.get('saldo_remanescente_temporal'),
                'sim' if bool(row_tmp.get('primeira_quebra_global')) else '',
                'sim' if bool(row_tmp.get('primeira_quebra_na_fonte')) else '',
                'sim' if bool(row_tmp.get('requer_reescolha_dinamica')) else '',
                row_tmp.get('observacao_temporal'),
            ])
    headers_temporal = ['Data', 'Conta', 'Despesa ID', 'Valor', 'Lote sugerido', 'Status local', 'Status temporal', 'Seq. fonte', 'Saldo Antes local', 'Saldo Antes temporal', 'Bruto temporal', 'Imposto temporal', 'Líquido temporal', 'Saldo Remanescente temporal', 'Primeira quebra global', 'Primeira quebra da fonte', 'Requer reescolha dinâmica', 'Observação temporal']
    _apply_table_style(ws_temporal, headers_temporal, rows_temporal, freeze=True)

    ws_reescolha = wb.create_sheet('Reescolha dinâmica')
    quadro_reescolha_full = contexto.reescolha_dinamica_pos_quebra.quadro_reescolha_dinamica.copy() if contexto.reescolha_dinamica_pos_quebra is not None else None
    rows_reescolha = []
    if quadro_reescolha_full is not None and len(quadro_reescolha_full):
        quadro_reescolha_full = quadro_reescolha_full.sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable')
        for _, row_dyn in quadro_reescolha_full.iterrows():
            rows_reescolha.append([
                row_dyn.get('data_pagamento'),
                row_dyn.get('descricao_pagamento'),
                row_dyn.get('pagamento_id'),
                row_dyn.get('valor_pagamento'),
                row_dyn.get('lote_sugerido_original'),
                'sim' if bool(row_dyn.get('reescolha_acionada')) else '',
                'sim' if bool(row_dyn.get('mudou_fonte')) else '',
                row_dyn.get('lote_final_dinamico'),
                row_dyn.get('tipo_fonte_final'),
                row_dyn.get('criterio_reescolha'),
                row_dyn.get('score_proxy_final'),
                row_dyn.get('status_pos_reescolha'),
                row_dyn.get('saldo_antes_dinamico'),
                row_dyn.get('bruto_dinamico'),
                row_dyn.get('imposto_dinamico'),
                row_dyn.get('liquido_dinamico'),
                row_dyn.get('saldo_remanescente_dinamico'),
                'sim' if bool(row_dyn.get('pagamento_totalmente_coberto_dinamico')) else '',
                row_dyn.get('observacao_reescolha'),
            ])
    headers_reescolha = ['Data', 'Conta', 'Despesa ID', 'Valor', 'Lote sugerido original', 'Reescolha acionada', 'Mudou fonte', 'Lote final dinâmico', 'Tipo fonte final', 'Critério reescolha', 'Score final dinâmico', 'Status pós-reescolha', 'Saldo Antes dinâmico', 'Bruto dinâmico', 'Imposto dinâmico', 'Líquido dinâmico', 'Saldo Remanescente dinâmico', 'Cobertura dinâmica integral', 'Observação reescolha']
    _apply_table_style(ws_reescolha, headers_reescolha, rows_reescolha, freeze=True)


    ws_heuristica = wb.create_sheet('Heurística conjunta')
    quadro_heuristica_full = contexto.heuristica_conjunta_parcial_bloco_critico.quadro_heuristica_conjunta_parcial.copy() if contexto.heuristica_conjunta_parcial_bloco_critico is not None else None
    rows_heuristica = []
    if quadro_heuristica_full is not None and len(quadro_heuristica_full):
        quadro_heuristica_full = quadro_heuristica_full.sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable')
        for _, row_h in quadro_heuristica_full.iterrows():
            rows_heuristica.append([
                row_h.get('data_pagamento'),
                row_h.get('descricao_pagamento'),
                row_h.get('pagamento_id'),
                row_h.get('valor_pagamento'),
                'sim' if bool(row_h.get('esta_no_bloco_critico')) else '',
                row_h.get('lote_sugerido_original'),
                row_h.get('lote_final_heuristica'),
                row_h.get('tipo_fonte_final'),
                'sim' if bool(row_h.get('mudou_fonte_heuristica')) else '',
                'sim' if bool(row_h.get('troca_preventiva_heuristica')) else '',
                'sim' if bool(row_h.get('troca_por_inviabilidade_heuristica')) else '',
                row_h.get('criterio_heuristica'),
                row_h.get('score_proxy_original'),
                row_h.get('score_proxy_heuristica'),
                row_h.get('score_proxy_ajustado_heuristica'),
                row_h.get('penalidade_preservacao_estrategica'),
                row_h.get('reserva_planejada_fonte'),
                row_h.get('status_heuristica'),
                row_h.get('saldo_antes_heuristica'),
                row_h.get('bruto_heuristica'),
                row_h.get('imposto_heuristica'),
                row_h.get('liquido_heuristica'),
                row_h.get('saldo_remanescente_heuristica'),
                'sim' if bool(row_h.get('pagamento_totalmente_coberto_heuristica')) else '',
                row_h.get('observacao_heuristica'),
            ])
    headers_heuristica = ['Data', 'Conta', 'Despesa ID', 'Valor', 'Bloco crítico', 'Lote sugerido original', 'Lote final heurístico', 'Tipo fonte final', 'Mudou fonte heurística', 'Troca preventiva heurística', 'Troca por inviabilidade heurística', 'Critério heurística', 'Score proxy original', 'Score proxy heurística', 'Score ajustado heurística', 'Penalidade preservação estratégica', 'Reserva planejada fonte', 'Status heurística', 'Saldo Antes heurística', 'Bruto heurística', 'Imposto heurística', 'Líquido heurística', 'Saldo Remanescente heurística', 'Cobertura heurística integral', 'Observação heurística']
    _apply_table_style(ws_heuristica, headers_heuristica, rows_heuristica, freeze=True)


    ws_planejamento = wb.create_sheet('Planejamento conjunto')
    quadro_planejamento_full = contexto.planejamento_conjunto_local_bloco_critico_v1.quadro_planejamento_conjunto_local.copy() if contexto.planejamento_conjunto_local_bloco_critico_v1 is not None else None
    quadro_politicas_full = contexto.planejamento_conjunto_local_bloco_critico_v1.quadro_comparativo_politicas.copy() if contexto.planejamento_conjunto_local_bloco_critico_v1 is not None else None
    rows_planejamento = []
    if quadro_planejamento_full is not None and len(quadro_planejamento_full):
        quadro_planejamento_full = quadro_planejamento_full.sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable')
        for _, row_p in quadro_planejamento_full.iterrows():
            rows_planejamento.append([
                row_p.get('data_pagamento'),
                row_p.get('descricao_pagamento'),
                row_p.get('pagamento_id'),
                row_p.get('valor_pagamento'),
                row_p.get('politica_id'),
                row_p.get('politica_descricao'),
                'sim' if bool(row_p.get('evento_ancora')) else '',
                row_p.get('lote_final_planejamento'),
                row_p.get('tipo_fonte_final'),
                row_p.get('score_planejamento'),
                row_p.get('status_planejamento'),
                row_p.get('saldo_antes_planejamento'),
                row_p.get('bruto_planejamento'),
                row_p.get('imposto_planejamento'),
                row_p.get('liquido_planejamento'),
                row_p.get('saldo_remanescente_planejamento'),
                'sim' if bool(row_p.get('pagamento_totalmente_coberto_planejamento')) else '',
                'sim' if bool(row_p.get('mudou_vs_v103')) else '',
                row_p.get('observacao_planejamento'),
            ])
    headers_planejamento = ['Data', 'Conta', 'Despesa ID', 'Valor', 'Política', 'Descrição política', 'Evento-âncora', 'Lote final planejamento', 'Tipo fonte final', 'Score planejamento', 'Status planejamento', 'Saldo Antes planejamento', 'Bruto planejamento', 'Imposto planejamento', 'Líquido planejamento', 'Saldo Remanescente planejamento', 'Cobertura planejamento integral', 'Mudou vs V103', 'Observação planejamento']
    _apply_table_style(ws_planejamento, headers_planejamento, rows_planejamento, freeze=True)

    if quadro_politicas_full is not None and len(quadro_politicas_full):
        rows_politicas = []
        for _, row_pol in quadro_politicas_full.iterrows():
            rows_politicas.append([
                row_pol.get('politica_id'),
                row_pol.get('politica_descricao'),
                'sim' if bool(row_pol.get('cobertura_integral_ancora')) else '',
                row_pol.get('liquido_coberto_ancora'),
                row_pol.get('deficit_ancora'),
                row_pol.get('pagamentos_cobertos_bloco'),
                row_pol.get('deficit_total_bloco'),
                row_pol.get('mudancas_vs_v103'),
                row_pol.get('primeira_sem_cobertura_data'),
                row_pol.get('primeira_sem_cobertura_pagamento'),
            ])
        _apply_table_style(ws_planejamento, ['Política', 'Descrição', 'Cobertura integral da âncora', 'Líquido coberto na âncora', 'Déficit da âncora', 'Pagamentos cobertos no bloco', 'Déficit total do bloco', 'Mudanças vs V103', 'Primeira sem cobertura', 'Pagamento da primeira sem cobertura'], rows_politicas, start_row=len(rows_planejamento)+4, title='Comparativo das políticas do bloco crítico')

    ws_micro = wb.create_sheet('Microplanejamento v2')
    quadro_micro_full = contexto.microplanejamento_conjunto_bloco_critico_v2.quadro_microplanejamento_conjunto.copy() if getattr(contexto, 'microplanejamento_conjunto_bloco_critico_v2', None) is not None else None
    quadro_micro_politicas = contexto.microplanejamento_conjunto_bloco_critico_v2.quadro_comparativo_politicas.copy() if getattr(contexto, 'microplanejamento_conjunto_bloco_critico_v2', None) is not None else None
    rows_micro = []
    if quadro_micro_full is not None and len(quadro_micro_full):
        quadro_micro_full = quadro_micro_full.sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable')
        for _, row_m in quadro_micro_full.iterrows():
            rows_micro.append([
                row_m.get('data_pagamento'),
                row_m.get('descricao_pagamento'),
                row_m.get('pagamento_id'),
                row_m.get('valor_pagamento'),
                row_m.get('politica_id'),
                row_m.get('politica_descricao'),
                'sim' if bool(row_m.get('evento_ancora')) else '',
                row_m.get('lote_final_microplanejamento'),
                row_m.get('fontes_usadas_microplanejamento'),
                'sim' if bool(row_m.get('multifonte_microplanejamento')) else '',
                row_m.get('status_microplanejamento'),
                row_m.get('criterio_microplanejamento'),
                row_m.get('reserva_explicita_microplanejamento'),
                row_m.get('score_microplanejamento'),
                row_m.get('saldo_antes_microplanejamento'),
                row_m.get('bruto_microplanejamento'),
                row_m.get('imposto_microplanejamento'),
                row_m.get('liquido_microplanejamento'),
                row_m.get('saldo_remanescente_microplanejamento'),
                'sim' if bool(row_m.get('pagamento_totalmente_coberto_microplanejamento')) else '',
                'sim' if bool(row_m.get('mudou_vs_v104')) else '',
                row_m.get('observacao_microplanejamento'),
            ])
    headers_micro = ['Data', 'Conta', 'Despesa ID', 'Valor', 'Política', 'Descrição política', 'Evento-âncora', 'Lote final microplanejamento', 'Fontes usadas', 'Multifonte', 'Status microplanejamento', 'Critério microplanejamento', 'Reserva explícita', 'Score microplanejamento', 'Saldo Antes microplanejamento', 'Bruto microplanejamento', 'Imposto microplanejamento', 'Líquido microplanejamento', 'Saldo Remanescente microplanejamento', 'Cobertura microplanejamento integral', 'Mudou vs V104', 'Observação microplanejamento']
    _apply_table_style(ws_micro, headers_micro, rows_micro, freeze=True)
    rows_micro_politicas = []
    if quadro_micro_politicas is not None and len(quadro_micro_politicas):
        quadro_micro_politicas = quadro_micro_politicas.sort_values(by=['cobertura_integral_ancora', 'liquido_coberto_ancora', 'pagamentos_cobertos_bloco'], ascending=[False, False, False], kind='stable')
        for _, row_p in quadro_micro_politicas.iterrows():
            primeira = row_p.get('primeira_sem_cobertura_pagamento') or ''
            rows_micro_politicas.append([
                row_p.get('politica_id'),
                row_p.get('politica_descricao'),
                'sim' if bool(row_p.get('cobertura_integral_ancora')) else '',
                row_p.get('liquido_coberto_ancora'),
                row_p.get('deficit_ancora'),
                row_p.get('pagamentos_cobertos_bloco'),
                row_p.get('deficit_total_bloco'),
                row_p.get('uso_multifonte'),
                row_p.get('reservas_acionadas'),
                row_p.get('primeira_sem_cobertura_data'),
                primeira,
            ])
        _apply_table_style(ws_micro, ['Política', 'Descrição', 'Cobertura integral da âncora', 'Líquido coberto na âncora', 'Déficit da âncora', 'Pagamentos cobertos no bloco', 'Déficit total do bloco', 'Uso multifonte', 'Reservas acionadas', 'Primeira sem cobertura', 'Pagamento da primeira sem cobertura'], rows_micro_politicas, start_row=len(rows_micro)+4, title='Comparativo das políticas do microplanejamento v2')

    ws_central = wb.create_sheet('Recomp. central v1')
    quadro_central_full = contexto.recomputacao_sequencial_central_v1.quadro_recomputacao_sequencial_central.copy() if getattr(contexto, 'recomputacao_sequencial_central_v1', None) is not None else None
    rows_central = []
    if quadro_central_full is not None and len(quadro_central_full):
        quadro_central_full = quadro_central_full.sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable')
        for _, row_c in quadro_central_full.iterrows():
            rows_central.append([
                row_c.get('data_pagamento'), row_c.get('descricao_pagamento'), row_c.get('pagamento_id'), row_c.get('valor_pagamento'),
                row_c.get('classe_pagamento_operacional'), row_c.get('subclasse_pagamento_operacional'), row_c.get('prioridade_intraclasse_operacional'), row_c.get('lote_sugerido_original'), row_c.get('lote_final_central'),
                row_c.get('tipo_fonte_final'), 'sim' if bool(row_c.get('mudou_vs_decisao_local')) else '', row_c.get('status_central'),
                row_c.get('score_proxy_central'), row_c.get('violacao_protegida'), row_c.get('severidade_protegida'),
                row_c.get('deficit_liquido_total'), row_c.get('patrimonio_terminal_proxy'), row_c.get('penalidade_estrategica_central'),
                row_c.get('penalidade_fragmentacao_central'), row_c.get('penalidade_escassez_protegida_futura'), row_c.get('demanda_protegida_futura_ponderada'),
                row_c.get('demanda_protegida_futura_7d'), row_c.get('demanda_protegida_futura_14d'), row_c.get('demanda_protegida_futura_21d'),
                'sim' if bool(row_c.get('fonte_critica_para_protegida_futura')) else '', 'sim' if bool(row_c.get('fallback_sem_fonte_viavel')) else '',
                row_c.get('saldo_antes_central'), row_c.get('bruto_central'),
                row_c.get('imposto_central'), row_c.get('liquido_central'), row_c.get('saldo_remanescente_central'),
                'sim' if bool(row_c.get('pagamento_totalmente_coberto_central')) else '', row_c.get('observacao_central'),
            ])
    headers_central = ['Data', 'Conta', 'Despesa ID', 'Valor', 'Classe operacional', 'Subclasse operacional', 'Prioridade intraclasse', 'Lote local', 'Lote central', 'Tipo fonte central', 'Mudou vs decisão local', 'Status central', 'Score proxy central', 'Violação protegida', 'Severidade protegida', 'Déficit líquido total', 'Patrimônio terminal proxy', 'Penalidade estratégica', 'Penalidade fragmentação', 'Penalidade escassez protegida futura', 'Demanda protegida futura ponderada', 'Demanda protegida 7d', 'Demanda protegida 14d', 'Demanda protegida 21d', 'Fonte crítica para protegida futura', 'Fallback sem fonte viável', 'Saldo Antes central', 'Bruto central', 'Imposto central', 'Líquido central', 'Saldo Remanescente central', 'Cobertura central integral', 'Observação central']
    _apply_table_style(ws_central, headers_central, rows_central, freeze=True)


    ws_recomendacao = wb.create_sheet('Switching')
    rows_recomendacao = []
    for row_sw in _switchings_oficiais_para_saida(contexto, limite=30):
        rows_recomendacao.append([
            row_sw[10],
            row_sw[7],
            next((str(l.investimento or '') for l in rep.lotes_apos_replay if str(l.id) == str(row_sw[7])), ''),
            row_sw[12],
            row_sw[13],
            row_sw[14],
            row_sw[19],
        ])
    _apply_table_style(ws_recomendacao, ['Data sugerida', 'Lote origem', 'Produto origem', 'Produto destino switching', 'Ganho estimado', 'Valor líquido origem', 'Status'], rows_recomendacao, freeze=True)

    ws_atual = wb.create_sheet('Situação Atual')
    resumo_fechamento_situacao_atual = resumir_fechamento_situacao_atual(
        data_referencia=ctx.data_referencia,
        calendario_financeiro=cal,
        serie_cdi=cache.serie_cdi,
    )
    rows_fechamento_atual = [
        ['Data de referência', resumo_fechamento_situacao_atual.get('data_referencia')],
        ['Status do fechamento econômico', resumo_fechamento_situacao_atual.get('status_fechamento')],
        ['Fonte do fechamento', resumo_fechamento_situacao_atual.get('fonte_fechamento')],
        ['Fechamentos com fallback CDI', resumo_fechamento_situacao_atual.get('qtd_fechamentos_fallback_cdi', 0)],
        ['Último fator explícito CDI', resumo_fechamento_situacao_atual.get('data_ultimo_fator_explicito_cdi')],
        ['Data confirmada da série', resumo_fechamento_situacao_atual.get('data_fechamento_confirmado')],
        ['Leitura auditável', resumo_fechamento_situacao_atual.get('observacao')],
    ]
    rows_exauridos_ident, rows_exauridos_valores, rows_ativos_ident, rows_ativos_valores = _classificar_lotes_situacao_atual(contexto)
    rows_recebidos_resumo = [
        ['Total de recebidos', contexto.recebidos_auditaveis.auditoria.get('resumo', {}).get('total_recebidos', 0)],
        ['Valor total bruto', contexto.recebidos_auditaveis.auditoria.get('resumo', {}).get('valor_total_bruto', 0.0)],
        ['Status recebido', str(contexto.recebidos_auditaveis.auditoria.get('resumo', {}).get('status_recebido', {}))],
        ['Destino potencial', str(contexto.recebidos_auditaveis.auditoria.get('resumo', {}).get('destino_potencial', {}))],
        ['Recebidos com pagamento vinculado', contexto.recebidos_auditaveis.auditoria.get('resumo', {}).get('recebidos_com_pagamento_vinculado', 0)],
        ['Recebidos em janela pré-aplicação', contexto.recebidos_auditaveis.auditoria.get('resumo', {}).get('recebidos_em_janela_pre_aplicacao', 0)],
        ['Recebidos usados antes da aplicação', contexto.recebidos_auditaveis.auditoria.get('resumo', {}).get('recebidos_usados_antes_da_aplicacao_observado', 0)],
    ]
    headers_exauridos_ident = ['Lote', 'Recebimento', 'Aplicação', 'Último uso', 'Produto', 'Dias Corridos', 'Dias Úteis']
    headers_ativos_ident = ['Lote', 'Recebimento', 'Aplicação', 'Produto', 'Dias Corridos', 'Dias Úteis']
    headers_atual_valores = ['Lote', 'Valor Original', 'Bruto Atual', 'Líquido Atual', 'Saldo rem']
    ultima_linha = _apply_table_style(ws_atual, headers_exauridos_ident, rows_exauridos_ident, start_row=1, title='Identificação e tempo dos lotes exauridos')
    ultima_linha = _apply_table_style(ws_atual, headers_atual_valores, rows_exauridos_valores, start_row=ultima_linha + 3, title='Valores atuais dos lotes exauridos')
    ultima_linha = _apply_table_style(ws_atual, headers_ativos_ident, rows_ativos_ident, start_row=ultima_linha + 3, title='Identificação e tempo dos lotes ativos')
    ultima_linha = _apply_table_style(ws_atual, headers_atual_valores, rows_ativos_valores, start_row=ultima_linha + 3, title='Valores atuais dos lotes ativos')
    _apply_table_style(ws_atual, ['Métrica', 'Valor'], rows_fechamento_atual, start_row=ultima_linha + 3, title='Fechamento econômico da situação atual')

    _limpar_abas_legadas(wb)
    _adicionar_abas_ranking(wb, contexto)

    SAIDA_INTERNA.parent.mkdir(parents=True, exist_ok=True)
    wb.save(SAIDA_INTERNA)
    try:
        if SAIDA_EXTERNA.parent.exists():
            wb.save(SAIDA_EXTERNA)
    except Exception as exc:
        print(f"[AVISO] cópia externa não gerada: {type(exc).__name__}:{exc}")
    return SAIDA_INTERNA


if __name__ == '__main__':
    main()
