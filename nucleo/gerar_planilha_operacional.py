from __future__ import annotations

from pathlib import Path
from typing import Iterable, Any, Mapping
import sys

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import (
    caminho_artifact,
    caminho_saida_operacional,
    nome_relatorio_operacional,
    VERSAO_BASELINE,
    VERSAO_SLUG,
)
from nucleo.saida_canonica import construir_saida_canonica


DEFAULT_ABAS_PLANILHA_OPERACIONAL = {
    'extrato_passado': 'Extrato Passado',
    'extrato_futuro': 'Extrato Futuro',
    'switching': 'Switching',
    'carteira': 'Carteira',
    'top30': 'Top30',
    'resumo_switching': 'Resumo Switching',
    'situacao_atual': 'Situação Atual',
    'saida_canonica': 'Saida Canonica',
}

DEFAULT_CABECALHOS_PLANILHA_OPERACIONAL = {
    'extrato_passado': ['Data', 'Conta', 'Despesa ID', 'Lote', 'Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente'],
    'extrato_futuro': ['Data', 'Conta', 'Despesa ID', 'Valor', 'Lote sugerido', 'Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente', 'Cobertura integral', 'Estratégia', 'Lote reserva', 'Necessita switching'],
    'switching': ['Data sugerida', 'Lote origem', 'Produto origem', 'Produto destino switching', 'Ganho estimado', 'Valor líquido origem', 'Status'],
}


def _cfg_get(config: Mapping[str, Any], *caminho: str, padrao: Any = None) -> Any:
    atual: Any = config
    for chave in caminho:
        if not isinstance(atual, Mapping) or chave not in atual:
            return padrao
        atual = atual[chave]
    return atual


def _config_planilha_operacional(contexto) -> Mapping[str, Any]:
    config = getattr(getattr(contexto, 'pacote_config', None), 'conteudo', {}) or {}
    cfg = _cfg_get(config, 'saidas', 'planilha_operacional', padrao={})
    return cfg if isinstance(cfg, Mapping) else {}


def _nome_aba_operacional(contexto, chave: str) -> str:
    cfg = _config_planilha_operacional(contexto)
    abas = cfg.get('abas') if isinstance(cfg.get('abas'), Mapping) else {}
    valor = abas.get(chave) if isinstance(abas, Mapping) else None
    if valor is None or str(valor).strip() == '':
        valor = DEFAULT_ABAS_PLANILHA_OPERACIONAL[chave]
    return str(valor)


def _nome_arquivo_operacional(contexto) -> str:
    cfg = _config_planilha_operacional(contexto)
    valor = cfg.get('arquivo') or cfg.get('nome_arquivo') or nome_relatorio_operacional()
    nome = str(valor).strip() or nome_relatorio_operacional()
    try:
        nome = nome.format(versao=VERSAO_BASELINE, versao_slug=VERSAO_SLUG)
    except Exception:
        pass
    if not nome.lower().endswith('.xlsx'):
        nome = f'{nome}.xlsx'
    return nome


def _caminhos_saida_operacional(contexto) -> tuple[Path, Path]:
    nome_arquivo = _nome_arquivo_operacional(contexto)
    return caminho_saida_operacional(RAIZ, nome_arquivo), caminho_artifact(nome_arquivo)


def _cabecalhos_operacionais(contexto, chave: str) -> list[str]:
    config = getattr(getattr(contexto, 'pacote_config', None), 'conteudo', {}) or {}
    valor = _cfg_get(config, 'saidas', 'planilha_operacional', 'cabecalhos', chave, padrao=None)
    if isinstance(valor, list) and all(isinstance(item, str) and item.strip() for item in valor):
        return list(valor)
    return list(DEFAULT_CABECALHOS_PLANILHA_OPERACIONAL[chave])


def _valor(item: dict[str, Any], chave: str) -> Any:
    return item.get(chave)


def _rows(itens: Iterable[dict[str, Any]], headers: list[str]) -> list[list[Any]]:
    return [[_valor(item, header) for header in headers] for item in itens]


def _para_float(valor: Any) -> float:
    try:
        if valor is None or valor == '':
            return 0.0
        return float(valor)
    except Exception:
        return 0.0


def _lote_exaurido_sem_aplicacao(item: dict[str, Any]) -> bool:
    produto = str(item.get('Produto') or '').strip().lower()
    return produto in {'-', '', 'sem aplicação', 'sem aplicacao', 'não aplicado', 'nao aplicado'}


def _somas_sacadas_por_lote(contexto) -> dict[str, dict[str, float]]:
    replay = getattr(contexto, 'replay_passado', None)
    log = getattr(replay, 'log_passado', None) if replay is not None else None
    somas: dict[str, dict[str, float]] = {}
    if log is None or not hasattr(log, 'iterrows') or len(log) == 0 or 'Lote' not in getattr(log, 'columns', []):
        return somas
    for _, row in log.iterrows():
        lote_id = str(row.get('Lote') or '').strip()
        if not lote_id:
            continue
        atual = somas.setdefault(lote_id, {'bruto_sacado': 0.0, 'liquido_sacado': 0.0})
        atual['bruto_sacado'] = round(atual['bruto_sacado'] + _para_float(row.get('Bruto')), 2)
        atual['liquido_sacado'] = round(atual['liquido_sacado'] + _para_float(row.get('Liquido') if 'Liquido' in row else row.get('Líquido')), 2)
    return somas


def _lotes_exauridos_valores(contexto, saida) -> list[dict[str, Any]]:
    somas = _somas_sacadas_por_lote(contexto)
    linhas: list[dict[str, Any]] = []
    for item in getattr(saida, 'lotes_exauridos', []) or []:
        lote_id = str(item.get('Lote') or '').strip()
        valores = somas.get(lote_id, {})
        valor_original = _para_float(item.get('Valor original'))
        liquido_sacado = round(_para_float(valores.get('liquido_sacado')), 2)
        patrimonio_liquido = round(liquido_sacado, 2)
        linhas.append({
            'Lote': item.get('Lote'),
            'Valor original': valor_original,
            'Bruto Sacado': round(_para_float(valores.get('bruto_sacado')), 2),
            'Líquido Sacado': liquido_sacado,
            'Patrimônio líquido': patrimonio_liquido,
            'Rendimento líquido': round(patrimonio_liquido - valor_original, 2),
        })
    return linhas


def _lotes_ativos_valores(contexto, saida) -> list[dict[str, Any]]:
    somas = _somas_sacadas_por_lote(contexto)
    linhas: list[dict[str, Any]] = []
    for item in getattr(saida, 'lotes_ativos', []) or []:
        lote_id = str(item.get('Lote') or '').strip()
        valores = somas.get(lote_id, {})
        valor_original = _para_float(item.get('Valor original'))
        liquido_sacado = round(_para_float(valores.get('liquido_sacado')), 2)
        liquido_atual = round(_para_float(item.get('Líquido')), 2)
        patrimonio_liquido_atual = round(liquido_sacado + liquido_atual, 2)
        linhas.append({
            'Lote': item.get('Lote'),
            'Valor original': valor_original,
            'Bruto Atual': round(_para_float(item.get('Bruto')), 2),
            'Líquido Atual': liquido_atual,
            'Patrimônio líquido atual': patrimonio_liquido_atual,
            'Rendimento líquido atual': round(patrimonio_liquido_atual - valor_original, 2),
        })
    return linhas


def _resumo_patrimonio_total_lotes(contexto, saida) -> list[dict[str, Any]]:
    lotes_exauridos = list(getattr(saida, 'lotes_exauridos', []) or [])
    lotes_ativos = list(getattr(saida, 'lotes_ativos', []) or [])
    lotes_visiveis = lotes_exauridos + lotes_ativos
    somas = _somas_sacadas_por_lote(contexto)

    valor_original_total = round(sum(_para_float(item.get('Valor original')) for item in lotes_visiveis), 2)
    valor_original_exaurido_sem_aplicacao = round(
        sum(_para_float(item.get('Valor original')) for item in lotes_exauridos if _lote_exaurido_sem_aplicacao(item)),
        2,
    )
    valor_original_aplicado_ajustado = round(valor_original_total - valor_original_exaurido_sem_aplicacao, 2)
    valor_total_bruto_sacado = round(sum(v['bruto_sacado'] for v in somas.values()), 2)
    valor_total_liquido_sacado = round(sum(v['liquido_sacado'] for v in somas.values()), 2)
    valor_bruto_atual = round(sum(_para_float(item.get('Bruto')) for item in lotes_ativos), 2)
    valor_liquido_atual = round(sum(_para_float(item.get('Líquido')) for item in lotes_ativos), 2)
    patrimonio_liquido_atual = round(valor_total_liquido_sacado + valor_liquido_atual, 2)
    rendimento_liquido_atual = round(patrimonio_liquido_atual - valor_original_aplicado_ajustado, 2)

    return [
        {'Métrica': 'Valor original total', 'Valor': valor_original_total},
        {'Métrica': 'Valor original exaurido sem aplicação', 'Valor': valor_original_exaurido_sem_aplicacao},
        {'Métrica': 'Valor original aplicado ajustado', 'Valor': valor_original_aplicado_ajustado},
        {'Métrica': 'Valor total bruto sacado', 'Valor': valor_total_bruto_sacado},
        {'Métrica': 'Valor total líquido sacado', 'Valor': valor_total_liquido_sacado},
        {'Métrica': 'Valor bruto atual', 'Valor': valor_bruto_atual},
        {'Métrica': 'Valor líquido atual', 'Valor': valor_liquido_atual},
        {'Métrica': 'Patrimônio líquido atual', 'Valor': patrimonio_liquido_atual},
        {'Métrica': 'Rendimento líquido atual', 'Valor': rendimento_liquido_atual},
    ]


def _apply_table_style(ws, headers: list[str], rows: list[list[Any]], *, start_row: int = 1, title: str | None = None, freeze: bool = False) -> int:
    ws.sheet_view.showGridLines = False
    header_fill = PatternFill('solid', fgColor='D9EAF7')
    header_font = Font(color='1F1F1F', bold=True)
    title_fill = PatternFill('solid', fgColor='EDF4FA')
    title_font = Font(color='1F1F1F', bold=True, size=12)
    thin_gray = Side(style='thin', color='D9E1F2')

    header_row = start_row
    if title:
        title_row = start_row
        ws.cell(row=title_row, column=1, value=title).fill = title_fill
        ws.cell(row=title_row, column=1).font = title_font
        ws.cell(row=title_row, column=1).alignment = Alignment(horizontal='left')
        header_row = start_row + 1

    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = Border(bottom=thin_gray)

    for row_offset, row in enumerate(rows, start=1):
        row_idx = header_row + row_offset
        for col_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            if isinstance(value, (int, float)):
                cell.alignment = Alignment(horizontal='right', vertical='center')
            else:
                cell.alignment = Alignment(horizontal='left', vertical='center')
            cell.border = Border(bottom=thin_gray)

    if freeze:
        ws.freeze_panes = f'A{header_row + 1}'

    if headers:
        ws.auto_filter.ref = f"A{header_row}:{get_column_letter(len(headers))}{max(header_row + len(rows), header_row)}"

    currency_cols = {
        'Valor', 'Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente',
        'Ganho estimado', 'Valor líquido origem', 'Score', 'Proxy terminal', 'Ticket mín.',
        'Valor original', 'Saldo rem', 'Valor bruto', 'Valor líquido', 'Valor vinculado',
        'Residual aplicação', 'Bruto Sacado', 'Líquido Sacado', 'Bruto Atual', 'Líquido Atual',
        'Patrimônio líquido', 'Rendimento líquido', 'Patrimônio líquido atual',
        'Rendimento líquido atual'
    }
    int_cols = {'Dias corridos', 'Dias úteis', 'Rank', 'Liquidez', 'Carência', 'Pagamentos vinculados'}

    for col_idx, header in enumerate(headers, start=1):
        letter = get_column_letter(col_idx)
        max_len = len(str(header))
        for row_idx in range(header_row + 1, ws.max_row + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            value = cell.value
            if value is None:
                continue
            max_len = max(max_len, len(str(value)))
            if header in currency_cols and isinstance(value, (int, float)):
                cell.number_format = 'R$ #,##0.00;[Red](R$ #,##0.00);-'
            elif header in int_cols and isinstance(value, (int, float)):
                cell.number_format = '0'
            elif 'Data' in header and hasattr(value, 'year'):
                cell.number_format = 'dd/mm/yyyy'
        ws.column_dimensions[letter].width = min(max(max_len + 2, 10), 38)
    return header_row + len(rows)


def _adicionar_abas_ranking(wb, contexto) -> None:
    ranking = getattr(contexto, 'ranking_carteira', None)
    if ranking is None:
        return

    ws_carteira = wb.create_sheet(_nome_aba_operacional(contexto, 'carteira'))
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
    rows_carteira = quadro_carteira.astype(object).where(quadro_carteira.notna(), '').values.tolist()
    _apply_table_style(ws_carteira, headers_carteira, rows_carteira, freeze=True)

    ws_top30 = wb.create_sheet(_nome_aba_operacional(contexto, 'top30'))
    top30 = ranking.top30.copy()
    rows_top30 = top30.astype(object).where(top30.notna(), '').values.tolist()
    _apply_table_style(ws_top30, list(top30.columns), rows_top30, freeze=True)

    ws_resumo = wb.create_sheet(_nome_aba_operacional(contexto, 'resumo_switching'))
    resumo_rows = [
        ['produtos_total', ranking.resumo.get('produtos_total')],
        ['produtos_ativos_ranqueados', ranking.resumo.get('produtos_ativos_ranqueados')],
        ['qtd_destinos_switch', ranking.auditoria.get('qtd_destinos_switch')],
        ['destino_top1', ranking.auditoria.get('destino_top1')],
        ['qtd_diffs_materiais_nucleo', ranking.validacao.get('qtd_diffs_materiais_nucleo')],
        ['aceite_nucleo', ranking.validacao.get('aceite_nucleo')],
    ]
    _apply_table_style(ws_resumo, ['indicador', 'valor'], resumo_rows)


def _adicionar_situacao_atual(wb, contexto, saida) -> None:
    ws = wb.create_sheet(_nome_aba_operacional(contexto, 'situacao_atual'))
    r = 1
    secoes = [
        ('Lotes exauridos — identificação e tempo', ['Lote', 'Recebimento', 'Aplicação', 'Último uso', 'Produto', 'Dias corridos', 'Dias úteis'], getattr(saida, 'lotes_exauridos', []) or []),
        ('Lotes exauridos — valores sacados e patrimônio', ['Lote', 'Valor original', 'Bruto Sacado', 'Líquido Sacado', 'Patrimônio líquido', 'Rendimento líquido'], _lotes_exauridos_valores(contexto, saida)),
        ('Lotes ativos — identificação e tempo', ['Lote', 'Recebimento', 'Aplicação', 'Produto', 'Dias corridos', 'Dias úteis'], getattr(saida, 'lotes_ativos', []) or []),
        ('Lotes ativos — valores atuais e patrimônio', ['Lote', 'Valor original', 'Bruto Atual', 'Líquido Atual', 'Patrimônio líquido atual', 'Rendimento líquido atual'], _lotes_ativos_valores(contexto, saida)),
        ('Patrimônio total dos lotes', ['Métrica', 'Valor'], _resumo_patrimonio_total_lotes(contexto, saida)),
        ('Recebidos auditáveis', ['Recebido', 'Lote origem', 'Recebimento', 'Aplicação', 'Valor bruto', 'Valor líquido', 'Status', 'Destino', 'Pagamentos vinculados', 'Valor vinculado', 'Residual aplicação', 'Disponível ref', 'Observação'], getattr(saida, 'recebidos_atuais', []) or []),
        ('Fechamento econômico', ['Métrica', 'Valor'], getattr(saida, 'fechamento_atual', []) or []),
        ('Resumo de recebidos', ['Métrica', 'Valor'], getattr(saida, 'resumo_recebidos', []) or []),
    ]
    for idx, (titulo, headers, itens) in enumerate(secoes):
        r = _apply_table_style(ws, headers, _rows(itens, headers), start_row=r if idx == 0 else r + 3, title=titulo)



COLUNAS_LOTES_CONSOLIDADOS = [
    'Lote ID',
    'Carteira',
    'Data Aplicação',
    'Data Base Fiscal',
    'Dias Corridos até Hoje',
    'Dias Úteis até Hoje',
    'Valor Original (R$)',
    'Total Bruto Sacado (R$)',
    'Total Líquido Sacado (R$)',
    'Saldo Bruto Atual (R$)',
    'Saldo Líquido Atual (R$)',
    'Patrimônio Líquido até Hoje (R$)',
    'Rendimento Líquido Acumulado dos Lotes (R$)',
]


def _somas_sacadas_por_lote_consolidado(contexto, saida=None):
    replay = getattr(contexto, 'replay_passado', None)
    log = getattr(replay, 'log_passado', None) if replay is not None else None
    somas = {}

    if log is not None and hasattr(log, 'iterrows') and len(log) and 'Lote' in getattr(log, 'columns', []):
        for _, row in log.iterrows():
            lote_id = str(row.get('Lote') or '').strip()
            if not lote_id:
                continue
            atual = somas.setdefault(lote_id, {'bruto_sacado': 0.0, 'liquido_sacado': 0.0})
            atual['bruto_sacado'] = round(atual['bruto_sacado'] + _para_float(row.get('Bruto')), 2)
            atual['liquido_sacado'] = round(
                atual['liquido_sacado'] + _para_float(row.get('Liquido') if 'Liquido' in row else row.get('Líquido')),
                2,
            )

    if saida is not None:
        for recebido in (getattr(saida, 'recebidos_atuais', []) or []):
            lote_id = str(recebido.get('Lote origem') or '').strip()
            if not lote_id:
                continue

            status = str(recebido.get('Status') or '').strip().lower()
            destino = str(recebido.get('Destino') or '').strip().lower()
            usar_recebido = (
                status in {'exaurido', 'uso_pre_aplicacao_com_aporte_posterior'}
                or destino in {'pagamento', 'pagamento_e_aplicacao'}
            )
            if not usar_recebido:
                continue

            valor_vinculado = _para_float(recebido.get('Valor vinculado'))
            valor_liquido = _para_float(recebido.get('Valor líquido'))
            valor_bruto = _para_float(recebido.get('Valor bruto'))

            liquido_ref = valor_vinculado if valor_vinculado > 0 else valor_liquido
            bruto_ref = max(valor_vinculado, valor_bruto if status == 'exaurido' else 0.0, liquido_ref)

            atual = somas.setdefault(lote_id, {'bruto_sacado': 0.0, 'liquido_sacado': 0.0})
            atual['bruto_sacado'] = round(max(atual['bruto_sacado'], bruto_ref), 2)
            atual['liquido_sacado'] = round(max(atual['liquido_sacado'], liquido_ref), 2)

    return somas


def _linhas_lotes_consolidados(contexto, saida, *, tipo):
    itens = list(getattr(saida, 'lotes_exauridos' if tipo == 'exauridos' else 'lotes_ativos', []) or [])
    somas = _somas_sacadas_por_lote_consolidado(contexto, saida)
    linhas = []

    for item in itens:
        lote_id = str(item.get('Lote') or '').strip()
        sacado = somas.get(lote_id, {})

        valor_original = round(_para_float(item.get('Valor original')), 2)
        total_bruto_sacado = round(_para_float(sacado.get('bruto_sacado')), 2)
        total_liquido_sacado = round(_para_float(sacado.get('liquido_sacado')), 2)

        saldo_bruto_atual = 0.0 if tipo == 'exauridos' else round(_para_float(item.get('Bruto')), 2)
        saldo_liquido_atual = 0.0 if tipo == 'exauridos' else round(_para_float(item.get('Líquido')), 2)

        patrimonio_liquido = round(total_liquido_sacado + saldo_liquido_atual, 2)
        rendimento_liquido = round(patrimonio_liquido - valor_original, 2)

        linhas.append({
            'Lote ID': item.get('Lote'),
            'Carteira': item.get('Produto'),
            'Data Aplicação': item.get('Aplicação'),
            'Data Base Fiscal': item.get('Aplicação'),
            'Dias Corridos até Hoje': item.get('Dias corridos'),
            'Dias Úteis até Hoje': item.get('Dias úteis'),
            'Valor Original (R$)': valor_original,
            'Total Bruto Sacado (R$)': total_bruto_sacado,
            'Total Líquido Sacado (R$)': total_liquido_sacado,
            'Saldo Bruto Atual (R$)': saldo_bruto_atual,
            'Saldo Líquido Atual (R$)': saldo_liquido_atual,
            'Patrimônio Líquido até Hoje (R$)': patrimonio_liquido,
            'Rendimento Líquido Acumulado dos Lotes (R$)': rendimento_liquido,
        })

    return linhas


def _resumo_patrimonio_total_lotes_consolidado(contexto, saida):
    linhas = (
        _linhas_lotes_consolidados(contexto, saida, tipo='exauridos')
        + _linhas_lotes_consolidados(contexto, saida, tipo='ativos')
    )

    valor_original_total = round(sum(_para_float(x.get('Valor Original (R$)')) for x in linhas), 2)
    valor_total_bruto_sacado = round(sum(_para_float(x.get('Total Bruto Sacado (R$)')) for x in linhas), 2)
    valor_total_liquido_sacado = round(sum(_para_float(x.get('Total Líquido Sacado (R$)')) for x in linhas), 2)
    valor_bruto_atual = round(sum(_para_float(x.get('Saldo Bruto Atual (R$)')) for x in linhas), 2)
    valor_liquido_atual = round(sum(_para_float(x.get('Saldo Líquido Atual (R$)')) for x in linhas), 2)
    patrimonio_liquido_atual = round(sum(_para_float(x.get('Patrimônio Líquido até Hoje (R$)')) for x in linhas), 2)
    rendimento_liquido_atual = round(patrimonio_liquido_atual - valor_original_total, 2)

    return [
        {'Métrica': 'Valor original total', 'Valor': valor_original_total},
        {'Métrica': 'Valor total bruto sacado', 'Valor': valor_total_bruto_sacado},
        {'Métrica': 'Valor total líquido sacado', 'Valor': valor_total_liquido_sacado},
        {'Métrica': 'Valor bruto atual', 'Valor': valor_bruto_atual},
        {'Métrica': 'Valor líquido atual', 'Valor': valor_liquido_atual},
        {'Métrica': 'Patrimônio líquido atual', 'Valor': patrimonio_liquido_atual},
        {'Métrica': 'Rendimento líquido atual', 'Valor': rendimento_liquido_atual},
    ]


def _adicionar_situacao_atual(wb, contexto, saida):
    ws = wb.create_sheet(_nome_aba_operacional(contexto, 'situacao_atual'))
    r = 1

    secoes = [
        ('Lotes exauridos', COLUNAS_LOTES_CONSOLIDADOS, _linhas_lotes_consolidados(contexto, saida, tipo='exauridos')),
        ('Lotes ativos', COLUNAS_LOTES_CONSOLIDADOS, _linhas_lotes_consolidados(contexto, saida, tipo='ativos')),
        ('Patrimônio total dos lotes', ['Métrica', 'Valor'], _resumo_patrimonio_total_lotes_consolidado(contexto, saida)),
        ('Recebidos auditáveis', ['Recebido', 'Lote origem', 'Recebimento', 'Aplicação', 'Valor bruto', 'Valor líquido', 'Status', 'Destino', 'Pagamentos vinculados', 'Valor vinculado', 'Residual aplicação', 'Disponível ref', 'Observação'], getattr(saida, 'recebidos_atuais', []) or []),
        ('Fechamento econômico', ['Métrica', 'Valor'], getattr(saida, 'fechamento_atual', []) or []),
        ('Resumo de recebidos', ['Métrica', 'Valor'], getattr(saida, 'resumo_recebidos', []) or []),
    ]

    for idx, (titulo, headers, itens) in enumerate(secoes):
        r = _apply_table_style(
            ws,
            headers,
            _rows(itens, headers),
            start_row=r if idx == 0 else r + 3,
            title=titulo,
        )

def _adicionar_auditoria_saida_canonica(wb, contexto, saida) -> None:
    ws = wb.create_sheet(_nome_aba_operacional(contexto, 'saida_canonica'))
    linhas = [{'Métrica': k, 'Valor': v} for k, v in saida.auditoria.items()]
    _apply_table_style(ws, ['Métrica', 'Valor'], _rows(linhas, ['Métrica', 'Valor']), freeze=True)


def main() -> Path:
    contexto = carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    saida = construir_saida_canonica(contexto, versao=VERSAO_BASELINE)
    saida_interna, saida_externa = _caminhos_saida_operacional(contexto)

    wb = Workbook()
    ws_passado = wb.active
    ws_passado.title = _nome_aba_operacional(contexto, 'extrato_passado')
    headers_passado = _cabecalhos_operacionais(contexto, 'extrato_passado')
    _apply_table_style(ws_passado, headers_passado, _rows(saida.extrato_passado, headers_passado), freeze=True)

    ws_futuro = wb.create_sheet(_nome_aba_operacional(contexto, 'extrato_futuro'))
    headers_futuro = _cabecalhos_operacionais(contexto, 'extrato_futuro')
    _apply_table_style(ws_futuro, headers_futuro, _rows(saida.extrato_futuro, headers_futuro), freeze=True)

    ws_switching = wb.create_sheet(_nome_aba_operacional(contexto, 'switching'))
    headers_switching = _cabecalhos_operacionais(contexto, 'switching')
    _apply_table_style(ws_switching, headers_switching, _rows(saida.switchings, headers_switching), freeze=True)

    _adicionar_abas_ranking(wb, contexto)
    _adicionar_situacao_atual(wb, contexto, saida)
    _adicionar_auditoria_saida_canonica(wb, contexto, saida)

    saida_interna.parent.mkdir(parents=True, exist_ok=True)
    wb.save(saida_interna)
    try:
        if saida_externa.parent.exists():
            wb.save(saida_externa)
    except Exception as exc:
        print(f"[AVISO] cópia externa não gerada: {type(exc).__name__}:{exc}")
    return saida_interna


if __name__ == '__main__':
    print(main())
