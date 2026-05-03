from __future__ import annotations
import glob
from pathlib import Path
import pandas as pd

OUT_DIR = Path('saidas/diagnostico')
OUT_DIR.mkdir(parents=True, exist_ok=True)

BLOCK_STATUS = {
    'sem_saldo_temporal_auditavel',
    'sem_fonte_auditavel',
    'switch_then_pay_sem_materializacao',
    'fonte_pos_switching_nao_materializada',
}


def norm(v):
    return str(v or '').strip().lower()


def is_nd(v):
    return norm(v) in {'', 'n/d', 'nd', 'não determinado', 'nao determinado', 'nan', 'none'}


def _inferir_causa(row: pd.Series) -> tuple[str, str, str]:
    """retorna (causa_raiz, etapa, tipo_causa)."""
    status = norm(row.get('Status recomendação'))
    motivo = norm(row.get('Motivo bloqueio lote'))
    reserva = row.get('_reserva_preenchida', False)
    saldo_ant = row.get('Saldo Antes')
    saldo_temporal = row.get('Saldo temp. ant.')

    if status == 'switch_then_pay_sem_materializacao' or motivo == 'switch_then_pay_sem_materializacao':
        return ('lote pós-switching não injetado no fluxo', 'ledger_temporal_conjunto', 'registrada_pipeline')
    if reserva and is_nd(saldo_ant):
        return ('reserva não promovida por saldo', 'promocao_reserva_para_lote', 'inferida')
    if reserva and row.get('_reserva_futura_sinal', False):
        return ('reserva não promovida por data', 'elegibilidade_temporal', 'inferida')
    if reserva and row.get('_reserva_prazo_sinal', False):
        return ('reserva não promovida por liquidez/carência', 'elegibilidade_liquidez_carencia', 'inferida')
    if reserva and (motivo in {'', 'n/d', 'nd', 'não determinado', 'nao determinado'}):
        return ('reserva descartada sem motivo estruturado', 'promocao_reserva_para_lote', 'causa_nao_rastreada_no_pipeline')
    if status in BLOCK_STATUS and not is_nd(saldo_temporal):
        return ('fonte disponível não propagada motor → ledger', 'propagacao_motor_ledger', 'inferida')
    if status == 'sem_fonte_auditavel':
        return ('sem fonte elegível real', 'motor_recomendacao', 'registrada_pipeline')
    return ('outro', 'nao_classificado', 'causa_nao_rastreada_no_pipeline')


def main() -> int:
    files = sorted(glob.glob('saidas/oficial/*.xlsx'), key=lambda p: Path(p).stat().st_mtime)
    if not files:
        print('sem xlsx em saidas/oficial')
        return 2
    xlsx = files[-1]

    extrato = pd.read_excel(xlsx, sheet_name='Extrato Futuro')
    try:
        switchings = pd.read_excel(xlsx, sheet_name='Switchings')
    except Exception:
        switchings = pd.DataFrame()

    extrato['_lote_nd'] = extrato['Lote sugerido'].apply(is_nd)
    extrato['_reserva_preenchida'] = ~extrato['Lote reserva'].apply(is_nd)
    extrato['_reserva_futura_sinal'] = extrato['Lote reserva'].astype(str).str.contains('mai\.|jun\.|jul\.|ago\.|set\.|out\.|nov\.|dez\.', case=False, na=False)
    extrato['_reserva_prazo_sinal'] = extrato['Lote reserva'].astype(str).str.contains('cdb|lc[ai]|tesouro|prazo|carência|carencia', case=False, na=False)
    extrato['_consumiu_lote_pos_sw'] = ~extrato.get('Lote pós-switching', pd.Series([''] * len(extrato))).apply(is_nd)

    total = len(extrato)
    total_determinado = int((~extrato['_lote_nd']).sum())
    total_nd = int(extrato['_lote_nd'].sum())
    total_reserva = int(extrato['_reserva_preenchida'].sum())
    total_reserva_nd = int((extrato['_reserva_preenchida'] & extrato['_lote_nd']).sum())
    total_consumo_pos_sw = int(extrato['_consumiu_lote_pos_sw'].sum())

    sem_lote = extrato[extrato['_lote_nd']].copy()
    causas = sem_lote.apply(_inferir_causa, axis=1, result_type='expand')
    sem_lote['causa_raiz'] = causas[0]
    sem_lote['etapa_descarte_fonte'] = causas[1]
    sem_lote['tipo_causa'] = causas[2]

    sem_lote['fontes_candidatas_motor'] = sem_lote['Lote reserva'].fillna('n/d')
    sem_lote['saldo_liquido_reserva_data'] = sem_lote['Saldo Antes'].fillna('n/d')
    sem_lote['elegibilidade_temporal_reserva'] = sem_lote['_reserva_futura_sinal'].map({True: 'ineligivel_data_inferido', False: 'sem_evidencia_ineligibilidade_data'})
    sem_lote['liquidez_carencia_reserva'] = sem_lote['_reserva_prazo_sinal'].map({True: 'sinal_produto_com_carencia_liquidez', False: 'n/d'})
    sem_lote['reserva_descartada'] = sem_lote['_reserva_preenchida'].map({True: 'sim', False: 'não'})

    detalhe_cols = [
        'Data', 'Conta', 'Valor', 'Lote reserva', 'Status recomendação', 'Motivo bloqueio lote',
        'fontes_candidatas_motor', 'saldo_liquido_reserva_data', 'elegibilidade_temporal_reserva',
        'liquidez_carencia_reserva', 'reserva_descartada', 'etapa_descarte_fonte', 'causa_raiz', 'tipo_causa'
    ]
    detalhe = sem_lote[detalhe_cols]
    detalhe.to_csv(OUT_DIR / 'diagnostico_baixa_resolutividade_detalhe.csv', index=False)

    causas_agg = sem_lote['causa_raiz'].value_counts().rename_axis('causa_raiz').reset_index(name='qtd')
    causas_agg.to_csv(OUT_DIR / 'diagnostico_baixa_resolutividade_causas.csv', index=False)

    sw_rows = []
    total_sw_materializados = 0
    if len(switchings):
        for _, r in switchings.iterrows():
            data = str(r.get('Data') or r.get('Data sugerida') or '')
            lote_origem = str(r.get('Lote origem') or '')
            lote_pos = str(r.get('Novo lote') or r.get('Lote pós-switching') or '')
            if is_nd(lote_origem) and is_nd(lote_pos):
                continue
            total_sw_materializados += 1
            elegiveis = extrato[extrato['Data'].astype(str) >= data] if data else extrato
            entrou = bool((extrato['Lote sugerido'].astype(str) == lote_pos).any()) if not is_nd(lote_pos) else False
            sw_rows.append({
                'evento_switching_id': f"sw::{data or 'n/d'}::{lote_origem or 'n/d'}::{lote_pos or 'n/d'}",
                'data': data or 'n/d',
                'lote_origem': lote_origem or 'n/d',
                'lote_pos_switching': lote_pos or 'n/d',
                'valor_liquido_materializado': r.get('Valor líquido total') or r.get('Valor líquido origem') or 'n/d',
                'produto_destino': r.get('Destino') or r.get('Produto destino switching') or 'n/d',
                'pagamentos_elegiveis_mesma_data_ou_depois': len(elegiveis),
                'entrou_como_fonte_candidata': 'sim' if entrou else 'não',
                'etapa_descarte': 'injeção_pos_switching_no_fluxo_pagamento' if not entrou else 'n/d',
                'motivo_descarte': 'fonte disponível não propagada motor → ledger' if not entrou else 'n/d',
                'tipo_causa': 'inferida' if not entrou else 'registrada_pipeline',
            })

    sw_df = pd.DataFrame(sw_rows)
    sw_df.to_csv(OUT_DIR / 'diagnostico_switchings_materializados.csv', index=False)

    resumo = pd.DataFrame([{
        'arquivo': xlsx,
        'total_pagamentos_futuros': total,
        'total_lote_sugerido_determinado': total_determinado,
        'total_lote_sugerido_nao_determinado': total_nd,
        'total_reserva_preenchida': total_reserva,
        'total_reserva_preenchida_e_lote_nd': total_reserva_nd,
        'total_lotes_pos_switching_materializados': total_sw_materializados,
        'total_pagamentos_que_consumiram_lote_pos_switching': total_consumo_pos_sw,
    }])
    resumo.to_csv(OUT_DIR / 'diagnostico_baixa_resolutividade_resumo.csv', index=False)

    print(f'arquivo={xlsx}')
    print(resumo.to_string(index=False))
    print('causas_raiz_agrupadas:')
    print(causas_agg.to_string(index=False))
    print('status_recomendacao:')
    print(extrato['Status recomendação'].fillna('n/d').astype(str).value_counts().to_string())
    print('arquivos_saida:')
    print(OUT_DIR / 'diagnostico_baixa_resolutividade_resumo.csv')
    print(OUT_DIR / 'diagnostico_baixa_resolutividade_detalhe.csv')
    print(OUT_DIR / 'diagnostico_baixa_resolutividade_causas.csv')
    print(OUT_DIR / 'diagnostico_switchings_materializados.csv')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
