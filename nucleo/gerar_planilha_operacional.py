from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import (
    VERSAO_BASELINE,
    VERSAO_SLUG,
    caminho_artifact,
    caminho_saida_operacional,
    nome_relatorio_operacional,
)
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.saida_observavel import construir_blocos_situacao_atual, construir_switchings_observaveis


DEFAULT_ABAS_PLANILHA_OPERACIONAL = {
    'extrato_passado': 'Extrato Passado',
    'extrato_futuro': 'Extrato Futuro',
    'switching': 'Switching',
    'carteira': 'Carteira',
    'top30': 'Top30',
    'resumo_switching': 'Resumo Switching',
    'situacao_atual': 'Situação Atual',
    'saida_canonica': 'Saida Canonica',
    'auditoria_fontes': 'Auditoria Fontes',
    'auditoria_fifo': 'Auditoria FIFO',
    'auditoria_fifo_candidatos': 'Auditoria FIFO Candidatos',
}

DEFAULT_CABECALHOS_PLANILHA_OPERACIONAL = {
    'extrato_passado': ['Data', 'Conta', 'Despesa ID', 'Lote', 'Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente'],
    'extrato_futuro': ['Data', 'Conta', 'Despesa ID', 'Valor', 'Lote sugerido', 'Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente', 'Cobertura integral', 'Estratégia', 'Pacote do dia', 'Lote reserva', 'Lote pós-switching', 'Destino switching', 'Origem switching', 'Fonte switching', 'Data switching', 'Score switching', 'Necessita switching', 'Switching antes do pagamento', 'Switching depois do pagamento', 'Motivo bloqueio lote', 'Status recomendação', 'Saldo temp. ant.', 'Consumo temp.', 'Saldo temp. dep.', 'Pos sw?', 'Fonte pos sw', 'Saldo pos sw', 'Motivo pos sw', 'Origem saldo pos', 'Bruto pos', 'Líq. pos', 'Data saldo pos', 'Motivo saldo pos'],
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




def _usar_abas_diagnosticas(contexto) -> bool:
    cfg = _config_planilha_operacional(contexto)
    valor = cfg.get('incluir_abas_diagnosticas', False)
    return bool(valor)

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
    default_headers = list(DEFAULT_CABECALHOS_PLANILHA_OPERACIONAL[chave])

    if not (isinstance(valor, list) and all(isinstance(item, str) and item.strip() for item in valor)):
        return default_headers

    headers_cfg = [str(item).strip() for item in valor if str(item).strip()]
    if not headers_cfg:
        return default_headers
    if chave != 'extrato_futuro':
        return headers_cfg

    merged = []
    seen = set()
    for h in headers_cfg + default_headers:
        if h not in seen:
            merged.append(h)
            seen.add(h)
    return merged


def _valor(item: dict[str, Any], chave: str) -> Any:
    return item.get(chave)


def _rows(itens: Iterable[dict[str, Any]], headers: list[str]) -> list[list[Any]]:
    return [[_valor(item, header) for header in headers] for item in itens]


def _apply_table_style(
    ws,
    headers: list[str],
    rows: list[list[Any]],
    *,
    start_row: int = 1,
    title: str | None = None,
    freeze: bool = False,
) -> int:
    ws.sheet_view.showGridLines = False

    header_fill = PatternFill('solid', fgColor='D9EAF7')
    header_font = Font(color='1F1F1F', bold=True)
    title_fill = PatternFill('solid', fgColor='EDF4FA')
    title_font = Font(color='1F1F1F', bold=True, size=12)
    thin_gray = Side(style='thin', color='D9E1F2')

    header_row = start_row

    if title:
        ws.cell(row=start_row, column=1, value=title).fill = title_fill
        ws.cell(row=start_row, column=1).font = title_font
        ws.cell(row=start_row, column=1).alignment = Alignment(horizontal='left')
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
            cell.alignment = Alignment(
                horizontal='right' if isinstance(value, (int, float)) else 'left',
                vertical='center',
            )
            cell.border = Border(bottom=thin_gray)

    if freeze:
        ws.freeze_panes = f'A{header_row + 1}'

    if headers:
        ws.auto_filter.ref = (
            f"A{header_row}:"
            f"{get_column_letter(len(headers))}{max(header_row + len(rows), header_row)}"
        )

    currency_cols = {
        'Valor',
        'Saldo Antes',
        'Bruto',
        'Imposto',
        'Líquido',
        'Saldo Remanescente',
        'Ganho estimado',
        'Valor líquido origem',
        'Score',
        'Proxy terminal',
        'Ticket mín.',
        'Valor bruto',
        'Valor líquido',
        'Valor vinculado',
        'Residual aplicação',
        'Orig.',
        'Bruto sac.',
        'Líq. sac.',
        'Bruto atual',
        'Líq. atual',
        'Patr. líq.',
        'Rend. líq.',
    }

    int_cols = {
        'Dias corr.',
        'Dias úteis',
        'Rank',
        'Liquidez',
        'Carência',
        'Pagamentos vinculados',
    }

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
            elif hasattr(value, 'year'):
                cell.number_format = 'dd/mm/yyyy'

        ws.column_dimensions[letter].width = min(max(max_len + 2, 10), 42)

    return header_row + len(rows)


def _adicionar_aba_tabela_operacional_pagamentos(wb) -> tuple[str, int, int]:
    nome_aba = 'Tabela Operacional Pagamentos'
    caminho_csv = RAIZ / 'saidas' / 'diagnostico' / 'tabela_operacional_pagamentos_v17_f0_s7g.csv'
    if not caminho_csv.exists():
        return nome_aba, 0, 0

    import pandas as pd

    df = pd.read_csv(caminho_csv)
    colunas = [
        'data','conta','valor','lote_recomendado','fontes_componentes','qtd_fontes_componentes',
        'fonte_principal','fonte_reserva','status_recomendacao_original','status_operacional',
        'acao_recomendada','motivo','saldo_liquido_disponivel','valor_liquido_necessario',
        'saldo_pos_pagamento','saldo_pos_pagamento_origem','patrimonio_liquido_fonte',
        'usa_lote_pos_switching','qtd_componentes_pos_switching','alerta_operacional',
        'tipo_alerta_operacional','problema_operacional','motivo_operacional',
        'saldo_temporal_insuficiente_tipo','estado_terminal_bloqueante','fonte_aprovada_para_pagamento',
    ]
    cols_presentes = [c for c in colunas if c in df.columns]
    if cols_presentes:
        df = df[cols_presentes]

    ws = wb.create_sheet(nome_aba)
    _apply_table_style(ws, list(df.columns), df.fillna('').values.tolist(), freeze=True)
    return nome_aba, len(df), len(df.columns)


def _adicionar_abas_ranking(wb, contexto) -> None:
    ranking = getattr(contexto, 'ranking_carteira', None)
    if ranking is None:
        return

    ws_carteira = wb.create_sheet(_nome_aba_operacional(contexto, 'carteira'))
    quadro_carteira = ranking.quadro_destinos_switch.copy()

    cols_carteira = [
        'rank_destino',
        'nome',
        'score_final',
        'proxy_terminal_destino',
        'retorno_anual_proxy',
        'liquidez_dias',
        'carencia_dias',
        'aplicacao_minima',
        'aplicacao_maxima',
        'tipo_produto',
        'somente_combo',
        'Status_Confirmação',
        'Campos_Pendentes',
    ]
    cols_carteira = [c for c in cols_carteira if c in quadro_carteira.columns]
    quadro_carteira = quadro_carteira[cols_carteira].copy()

    headers_carteira = [
        'Rank',
        'Produto',
        'Score Final',
        'Proxy Terminal',
        'Retorno Proxy aa',
        'Liquidez Dias',
        'Carência Dias',
        'Aplicação Mínima',
        'Aplicação Máxima',
        'Tipo Produto',
        'Somente Combo',
        'Status Confirmação',
        'Campos Pendentes',
    ][:len(cols_carteira)]

    rows_carteira = quadro_carteira.astype(object).where(quadro_carteira.notna(), '').values.tolist()
    _apply_table_style(ws_carteira, headers_carteira, rows_carteira, freeze=True)

    if _usar_abas_diagnosticas(contexto):
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

    for idx, bloco in enumerate(construir_blocos_situacao_atual(contexto, saida)):
        r = _apply_table_style(
            ws,
            bloco['headers'],
            _rows(bloco['linhas'], bloco['headers']),
            start_row=r if idx == 0 else r + 3,
            title=bloco['titulo'],
        )


def _adicionar_auditoria_saida_canonica(wb, contexto, saida) -> None:
    ws = wb.create_sheet(_nome_aba_operacional(contexto, 'saida_canonica'))
    auditoria = dict(getattr(saida, 'auditoria', {}) or {})
    auditoria['qtd_switchings'] = len(getattr(saida, 'switchings', None) or [])

    linhas = []
    for k, v in auditoria.items():
        if isinstance(v, (list, dict, tuple, set)):
            continue
        linhas.append({'Métrica': k, 'Valor': v})
    _apply_table_style(ws, ['Métrica', 'Valor'], _rows(linhas, ['Métrica', 'Valor']), freeze=True)

def main(*, contexto=None, saida=None) -> Path:
    """Gera a planilha operacional.

    Quando contexto e saida são informados, esta função não recarrega planilha,
    não baixa dados e não reconstrói cache. Ela apenas renderiza a planilha a
    partir dos objetos já construídos pela rota principal.
    """
    if contexto is None:
        contexto = carregar_contexto_baseline(
            raiz_repositorio=RAIZ,
            instalar_automaticamente=False,
            incluir_resolver_hibrido_5p_shadow=False,
            incluir_benchmark_agrupado_individual_shadow=False,
            incluir_benchmark_runner_futuro_shadow=False,
            incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
        )

    if saida is None:
        saida = construir_saida_canonica(contexto, versao=VERSAO_BASELINE)

    saida_interna, saida_externa = _caminhos_saida_operacional(contexto)

    wb = Workbook()

    ws_passado = wb.active
    ws_passado.title = _nome_aba_operacional(contexto, "extrato_passado")
    headers_passado = _cabecalhos_operacionais(contexto, "extrato_passado")
    _apply_table_style(ws_passado, headers_passado, _rows(saida.extrato_passado, headers_passado), freeze=True)

    ws_futuro = wb.create_sheet(_nome_aba_operacional(contexto, "extrato_futuro"))
    headers_futuro = _cabecalhos_operacionais(contexto, "extrato_futuro")
    _apply_table_style(ws_futuro, headers_futuro, _rows(saida.extrato_futuro, headers_futuro), freeze=True)

    ws_switching = wb.create_sheet(_nome_aba_operacional(contexto, "switching"))
    headers_switching = _cabecalhos_operacionais(contexto, "switching")
    switchings_observaveis = construir_switchings_observaveis(contexto, saida)
    _apply_table_style(ws_switching, headers_switching, _rows(switchings_observaveis, headers_switching), freeze=True)

    if _usar_abas_diagnosticas(contexto):
        ws_switching_sint = wb.create_sheet("Lotes Sinteticos Pos-Sw")
        headers_switching_sint = ['Data', 'Lotes origem', 'Destino', 'Novo lote', 'Valor líquido total', 'Origem valor']
        linhas_switching_sint = list(getattr(saida, 'lotes_sinteticos_pos_switching_console', lambda **_: [])(limite=200) or [])
        _apply_table_style(
            ws_switching_sint,
            headers_switching_sint,
            _rows(linhas_switching_sint, headers_switching_sint),
            freeze=True,
        )

        ws_estado_pos = wb.create_sheet("Estado Pos-Switching")
        headers_estado_pos = ['Data', 'Novo lote', 'Produto destino', 'Valor inicial', 'Lotes origem', 'Status origem', 'Status novo', 'Liquidez', 'Carência', 'Ticket mín.', 'Origem valor']
        linhas_estado_pos = list(getattr(saida, 'estado_pos_switching_lotes_console', lambda **_: [])(limite=200) or [])
        _apply_table_style(
            ws_estado_pos,
            headers_estado_pos,
            _rows(linhas_estado_pos, headers_estado_pos),
            freeze=True,
        )

    _adicionar_abas_ranking(wb, contexto)
    _adicionar_situacao_atual(wb, contexto, saida)
    _adicionar_auditoria_saida_canonica(wb, contexto, saida)
    _adicionar_aba_tabela_operacional_pagamentos(wb)
    _adicionar_aba_auditoria_fontes(wb, contexto, saida)
    if _usar_abas_diagnosticas(contexto):
        _adicionar_aba_auditoria_fifo(wb, contexto, saida)
        _adicionar_aba_auditoria_fifo_candidatos(wb, contexto, saida)

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


def _adicionar_aba_auditoria_fontes(wb, contexto, pacote_saida) -> None:
    ws = wb.create_sheet(_nome_aba_operacional(contexto, 'auditoria_fontes'))
    headers = [
        'Data','Conta','Despesa ID','Valor','Lote sugerido','Lote reserva',
        'fonte_candidata_id','tipo_fonte_candidata','origem_fonte_candidata','elegivel_temporalmente',
        'saldo_liquido_disponivel','elegivel_liquidez_carencia','promovida_para_lote_sugerido',
        'etapa_descarte_fonte','motivo_descarte_fonte','origem_motivo_descarte','evento_switching_id',
        'lote_pos_switching_materializado','pacote_do_dia_ledger','status_ledger','motivo_bloqueio_ledger'
    ]
    itens = []
    for row in pacote_saida.extrato_futuro:
        itens.append({h: row.get(h) for h in headers})
    rows = _rows(itens, headers)
    _apply_table_style(ws, headers, rows, freeze=True)


def _adicionar_aba_auditoria_fifo(wb, contexto, pacote_saida) -> None:
    ws = wb.create_sheet(_nome_aba_operacional(contexto, 'auditoria_fifo'))
    headers = [
        'Data','Conta','Despesa ID','Valor','Lote sugerido','Pacote do dia',
        'fifo_qtd_lotes_estado','fifo_qtd_lotes_avaliados','fifo_qtd_lotes_saldo_suficiente','fifo_qtd_lotes_elegiveis',
        'fifo_qtd_lotes_bloqueados_por_saldo','fifo_qtd_lotes_bloqueados_por_data',
        'fifo_qtd_lotes_bloqueados_por_carencia','fifo_qtd_lotes_bloqueados_por_migracao',
        'fifo_melhor_lote_candidato','fifo_saldo_melhor_lote','fifo_data_aplicacao_melhor_lote',
        'fifo_carencia_melhor_lote','fifo_motivo_nao_promocao','origem_fonte_candidata','status_ledger'
    ]
    candidatos = list((getattr(pacote_saida, 'auditoria', {}) or {}).get('fifo_candidatos_avaliados', []) or [])
    cand_por_despesa: dict[str, list[dict[str, object]]] = {}
    for cand in candidatos:
        key = str(cand.get('Despesa ID') or '').strip()
        cand_por_despesa.setdefault(key, []).append(cand)
    itens=[]
    for row in pacote_saida.extrato_futuro:
        despesa_id = str(row.get('Despesa ID') or '').strip()
        cands = cand_por_despesa.get(despesa_id, [])
        qtd_av = len(cands)
        qtd_suf = sum(1 for c in cands if not bool(c.get('bloqueado_por_saldo')))
        qtd_eleg = sum(1 for c in cands if bool(c.get('elegivel_fifo')))
        b_saldo = sum(1 for c in cands if bool(c.get('bloqueado_por_saldo')))
        b_data = sum(1 for c in cands if bool(c.get('bloqueado_por_data')))
        b_car = sum(1 for c in cands if bool(c.get('bloqueado_por_carencia')))
        b_mig = sum(1 for c in cands if bool(c.get('bloqueado_por_migracao')))
        cands_ordenados = sorted(cands, key=lambda c: (float(c.get('ordem_fifo') or 10**9), str(c.get('lote_id') or '')))
        cands_elegiveis = [c for c in cands_ordenados if bool(c.get('elegivel_fifo'))]
        melhor = cands_elegiveis[0] if cands_elegiveis else {}
        motivo = row.get('fifo_motivo_nao_promocao')
        lote_sugerido_nd = str(row.get('Lote sugerido') or '').strip().lower() in {'', 'n/d', 'nd', 'não determinado', 'nao determinado'}
        if qtd_eleg == 0 and (not str(motivo or '').strip() or str(motivo).strip() == 'fifo_nao_aplicavel_lote_ja_determinado'):
            motivo = 'fifo_sem_candidato_elegivel'
        if lote_sugerido_nd and str(motivo or '').strip() == 'fifo_nao_aplicavel_lote_ja_determinado':
            motivo = 'fifo_sem_candidato_elegivel' if qtd_eleg == 0 else 'fifo_candidato_elegivel_sem_promocao'
        if (row.get('fifo_qtd_lotes_estado') or 0) > 0 and qtd_av == 0 and not str(motivo or '').strip():
            motivo = 'fifo_nao_aplicavel_sem_motivo_explicito'
        item = {h: row.get(h) for h in headers}
        item.update({
            'fifo_qtd_lotes_avaliados': qtd_av,
            'fifo_qtd_lotes_saldo_suficiente': qtd_suf,
            'fifo_qtd_lotes_elegiveis': qtd_eleg,
            'fifo_qtd_lotes_bloqueados_por_saldo': b_saldo,
            'fifo_qtd_lotes_bloqueados_por_data': b_data,
            'fifo_qtd_lotes_bloqueados_por_carencia': b_car,
            'fifo_qtd_lotes_bloqueados_por_migracao': b_mig,
            'fifo_melhor_lote_candidato': melhor.get('lote_id', 'n/d'),
            'fifo_saldo_melhor_lote': melhor.get('saldo_liquido', 'n/d'),
            'fifo_data_aplicacao_melhor_lote': melhor.get('data_aplicacao', 'n/d'),
            'fifo_carencia_melhor_lote': melhor.get('carencia_ate', 'n/d'),
            'fifo_motivo_nao_promocao': motivo,
        })
        itens.append(item)
    _apply_table_style(ws, headers, _rows(itens, headers), freeze=True)


def _adicionar_aba_auditoria_fifo_candidatos(wb, contexto, pacote_saida) -> None:
    ws = wb.create_sheet(_nome_aba_operacional(contexto, 'auditoria_fifo_candidatos'))
    headers = ['Data','Conta','Despesa ID','Valor','lote_id','data_aplicacao','carencia_ate','migrado_em','saldo_liquido','avaliado_fifo','bloqueado_por_saldo','bloqueado_por_data','bloqueado_por_carencia','bloqueado_por_migracao','elegivel_fifo','ordem_fifo','motivo_bloqueio_fifo']
    itens=[]
    for cand in list((getattr(pacote_saida, 'auditoria', {}) or {}).get('fifo_candidatos_avaliados', []) or []):
        itens.append({h: cand.get(h) for h in headers})
    _apply_table_style(ws, headers, _rows(itens, headers), freeze=True)
