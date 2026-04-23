from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import json

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.simulador_central_eventos_v1 import construir_estado_global_recorte_curto_v117, _ativar_recebidos_futuros_no_dia, _coerce_date

RELATORIO = Path(RAIZ) / 'relatorios' / 'atuais' / 'AUDITORIA_ATIVACAO_LOTES_NAO_APORTADOS_FUTUROS_V136.md'
JSON_OUT = Path(RAIZ) / 'saidas' / 'operacional' / 'auditoria_ativacao_lotes_nao_aportados_futuros_v136.json'


def executar() -> dict:
    contexto = carregar_contexto_baseline(
        raiz_repositorio=Path(RAIZ),
        instalar_automaticamente=False,
        incluir_switching_shadow=False,
        incluir_triagem=True,
        incluir_switching_economico_shadow=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    inventario = contexto.dados_operacionais.inventario_canonico.copy()
    futuros = inventario.loc[inventario.get('recebido_futuro_nao_disponivel').fillna(False)].copy()
    futuros = futuros.sort_values(['data_recebimento', 'lote_id'], kind='stable').reset_index(drop=True)
    estado = construir_estado_global_recorte_curto_v117(
        contexto,
        data_inicio=contexto.execucao.data_referencia,
        data_fim=contexto.execucao.data_referencia,
        limite_pagamentos=1,
    )
    registros = []
    for _, row in futuros.iterrows():
        lote_id = str(row.get('lote_id') or '')
        data_recebimento = _coerce_date(row.get('data_recebimento'))
        if data_recebimento is None:
            continue
        estado_antes = deepcopy(estado)
        _ativar_recebidos_futuros_no_dia(estado_antes, data_recebimento - timedelta(days=1))
        ids_antes = {str(x.get('id') or x.get('fonte_id') or '') for x in estado_antes.get('recebidos_nao_aportados_disponiveis', [])}
        estado_no_dia = deepcopy(estado)
        _ativar_recebidos_futuros_no_dia(estado_no_dia, data_recebimento)
        ids_no_dia = {str(x.get('id') or x.get('fonte_id') or '') for x in estado_no_dia.get('recebidos_nao_aportados_disponiveis', [])}
        registros.append({
            'lote_id': lote_id,
            'data_recebimento': data_recebimento.isoformat(),
            'valor_original': round(float(row.get('valor_original') or 0.0), 2),
            'elegivel_antes': lote_id in ids_antes,
            'elegivel_no_dia': lote_id in ids_no_dia,
            'ativacao_correta': (lote_id not in ids_antes) and (lote_id in ids_no_dia),
        })
    corretos = sum(1 for r in registros if r['ativacao_correta'])
    payload = {
        'data_referencia': contexto.execucao.data_referencia.isoformat(),
        'quantidade_futuros': int(len(futuros)),
        'quantidade_ativacao_correta': int(corretos),
        'quantidade_ativacao_incorreta': int(len(registros) - corretos),
        'registros': registros,
    }
    JSON_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    linhas = [
        '# Auditoria da ativação de lotes não aportados futuros — V136',
        '',
        f"- Data de referência: {payload['data_referencia']}",
        f"- Lotes futuros auditados: {payload['quantidade_futuros']}",
        f"- Ativações corretas na data de recebimento: {payload['quantidade_ativacao_correta']}",
        f"- Ativações incorretas: {payload['quantidade_ativacao_incorreta']}",
        '',
        '## Registros auditados',
        '',
        '| Lote | Data recebimento | Valor | Elegível antes | Elegível no dia | Ativação correta |',
        '|---|---|---:|---|---|---|',
    ]
    for r in registros:
        linhas.append(f"| {r['lote_id']} | {r['data_recebimento']} | {r['valor_original']:.2f} | {'Sim' if r['elegivel_antes'] else 'Não'} | {'Sim' if r['elegivel_no_dia'] else 'Não'} | {'Sim' if r['ativacao_correta'] else 'Não'} |")
    RELATORIO.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    print(str(JSON_OUT))
    print(str(RELATORIO))
    return payload


def main() -> int:
    executar()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
