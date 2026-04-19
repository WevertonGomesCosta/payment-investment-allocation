from __future__ import annotations

from pathlib import Path
from copy import deepcopy
from datetime import date
from typing import Iterable
import sys

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline, obter_limiar_residuo_resolvido
from nucleo.identidade_baseline import caminho_artifact, caminho_saida_operacional, nome_relatorio_operacional
from nucleo.calendario_financeiro import contar_dias_rendimento
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

    currency_cols = {'Valor', 'Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente', 'Aplicação Mínima', 'Bruto Atual', 'Líquido Atual', 'Saldo rem', 'Score Final', 'Valor Original', 'Valor bruto', 'Valor líquido', 'Valor vinculado', 'Residual aplicação'}
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
    for lote in sorted(rep.lotes_apos_replay, key=lambda x: (x.data_recebimento, x.data_aplicacao, x.id)):
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
        dias_corridos = max((ctx.data_referencia - lote.data_recebimento).days, 0)
        dias_uteis = 0 if data_economica < lote.data_aplicacao else contar_dias_rendimento(
            lote.data_base_fiscal,
            data_economica,
            cal,
            serie_cdi=cache.serie_cdi,
            data_fechamento_referencia=data_economica,
        )
        lote_exaurido_na_situacao = bool(lote.esgotado or saldo_bruto <= limiar)
        saldo_bruto_exibicao, saldo_liquido_exibicao, saldo_rem_exibicao = normalizar_valores_situacao_atual_exaurida(
            saldo_bruto=saldo_bruto,
            saldo_liquido=saldo_liquido,
            saldo_rem=saldo_rem,
            exaurido=lote_exaurido_na_situacao,
        )
        linha_ident = [lote.id, lote.data_recebimento, lote.data_aplicacao, lote.investimento, dias_corridos, dias_uteis]
        linha_valores = [lote.id, round(float(getattr(lote, 'valor_inicial', 0.0) or 0.0), 2), saldo_bruto_exibicao, saldo_liquido_exibicao, saldo_rem_exibicao]
        if lote_exaurido_na_situacao:
            rows_exauridos_ident.append(linha_ident)
            rows_exauridos_valores.append(linha_valores)
        else:
            rows_ativos_ident.append(linha_ident)
            rows_ativos_valores.append(linha_valores)
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
    ws_passado.title = 'Extrato passado'
    log = rep.log_passado.copy().sort_values(by=['Data', 'Sequencia Saque'], kind='stable')
    cols_passado = [
        ('Data', 'Data'), ('Conta', 'Conta'), ('Despesa ID', 'Despesa ID'), ('Lote', 'Lote'),
        ('Saldo Antes', 'Saldo Antes'), ('Bruto', 'Bruto'), ('Imposto', 'Imposto'), ('Liquido', 'Líquido'),
        ('Dias Corridos', 'Dias Corridos'), ('Dias Úteis', 'Dias Úteis'), ('Saldo Remanescente', 'Saldo Remanescente'),
        ('Fase Operacional Lote', 'Fase')
    ]
    rows_passado = list(_as_rows(log.to_dict('records'), cols_passado))
    _apply_table_style(ws_passado, [dst for _, dst in cols_passado], rows_passado, freeze=True)

    ws_futuro = wb.create_sheet('Extrato futuro')
    gastos_futuros = dados.gastos_canonicos[dados.gastos_canonicos['futuro_ou_pendente_na_data_referencia'] == True].copy().sort_values(by=['data', 'despesa_id'], kind='stable')
    quadro_decisao = contexto.decisao_local_v1.quadro_decisao_local_v1.copy() if contexto.decisao_local_v1 is not None else None
    mapa_decisao = {}
    if quadro_decisao is not None and len(quadro_decisao):
        for _, row_dec in quadro_decisao.iterrows():
            mapa_decisao[str(row_dec.get('pagamento_id') or '').strip()] = row_dec.to_dict()
    rows_futuro = []
    for item in gastos_futuros.to_dict('records'):
        data_evt = item.get('data')
        dias_ate = max((data_evt - ctx.data_referencia).days, 0) if isinstance(data_evt, date) else None
        despesa_id = str(item.get('despesa_id') or '').strip()
        decisao = mapa_decisao.get(despesa_id, {})
        resumo_financeiro = _calcular_resumo_financeiro_fonte(contexto, decisao)
        rows_futuro.append([
            data_evt,
            item.get('descricao'),
            item.get('despesa_id'),
            item.get('valor'),
            item.get('pago'),
            str(decisao.get('lote_id_escolhido') or ''),
            resumo_financeiro.get('Saldo Antes', ''),
            resumo_financeiro.get('Bruto', ''),
            resumo_financeiro.get('Imposto', ''),
            resumo_financeiro.get('Líquido', ''),
            resumo_financeiro.get('Saldo Remanescente', ''),
            round(float(decisao.get('custo_economico_proxy') or 0.0), 4) if decisao else '',
            'integral na decisão local' if bool(decisao.get('pagamento_totalmente_coberto')) else ('parcial/ausente na decisão local' if decisao else ''),
            dias_ate,
            'futuro/pendente',
        ])
    headers_futuro = ['Data', 'Conta', 'Despesa ID', 'Valor', 'Pago', 'Lote sugerido', 'Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente', 'Score proxy', 'Status local', 'Dias até evento', 'Status']
    _apply_table_style(ws_futuro, headers_futuro, rows_futuro, freeze=True)

    ws_melhores = wb.create_sheet('Melhores produtos')
    candidatos = tri.quadro_candidatos.copy().sort_values(by=['score_final', 'score_retorno'], ascending=[False, False], kind='stable')
    rows_melhores = []
    for _, row in candidatos.iterrows():
        rows_melhores.append([
            row.get('nome'), row.get('familia_produto'), row.get('regime_taxa'), row.get('taxa_base_cdi'), row.get('taxa_bonus_cdi'),
            row.get('dias_bonus'), row.get('carencia_dias'), row.get('aplicacao_minima'), row.get('score_final'), row.get('rank_global'), row.get('rank_familia')
        ])
    headers_melhores = ['Produto', 'Família', 'Regime', 'Taxa Base CDI', 'Taxa Bônus CDI', 'Dias Bônus', 'Carência Dias', 'Aplicação Mínima', 'Score Final', 'Rank Global', 'Rank Família']
    _apply_table_style(ws_melhores, headers_melhores, rows_melhores, freeze=True)

    ws_atual = wb.create_sheet('Situação atual')
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
    headers_atual_ident = ['Lote', 'Recebimento', 'Aplicação', 'Produto', 'Dias Corridos', 'Dias Úteis']
    headers_atual_valores = ['Lote', 'Valor Original', 'Bruto Atual', 'Líquido Atual', 'Saldo rem']
    ultima_linha = _apply_table_style(ws_atual, headers_atual_ident, rows_exauridos_ident, start_row=1, title='Identificação e tempo dos lotes exauridos')
    ultima_linha = _apply_table_style(ws_atual, headers_atual_valores, rows_exauridos_valores, start_row=ultima_linha + 3, title='Valores atuais dos lotes exauridos')
    ultima_linha = _apply_table_style(ws_atual, headers_atual_ident, rows_ativos_ident, start_row=ultima_linha + 3, title='Identificação e tempo dos lotes ativos')
    ultima_linha = _apply_table_style(ws_atual, headers_atual_valores, rows_ativos_valores, start_row=ultima_linha + 3, title='Valores atuais dos lotes ativos')
    ultima_linha = _apply_table_style(ws_atual, ['Métrica', 'Valor'], rows_recebidos_resumo, start_row=ultima_linha + 3, title='Resumo dos recebidos auditáveis (inclui exauridos)')
    _apply_table_style(ws_atual, ['Métrica', 'Valor'], rows_fechamento_atual, start_row=ultima_linha + 3, title='Fechamento econômico da situação atual')

    SAIDA_INTERNA.parent.mkdir(parents=True, exist_ok=True)
    wb.save(SAIDA_INTERNA)
    print(SAIDA_INTERNA)
    try:
        if SAIDA_EXTERNA.parent.exists():
            wb.save(SAIDA_EXTERNA)
            print(SAIDA_EXTERNA)
    except Exception as exc:
        print(f"[AVISO] cópia externa não gerada: {type(exc).__name__}:{exc}")
    return SAIDA_INTERNA


if __name__ == '__main__':
    main()
