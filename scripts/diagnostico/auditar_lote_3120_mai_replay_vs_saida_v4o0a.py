from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida_shadow
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.saida_observavel import construir_linhas_lotes_consolidados
from scripts.diagnostico.auditar_lote_3120_mai_estado_temporal_v4o import (
    _as_list_dict,
    _iguais,
    _linhas_resumo,
    _normalizar_texto,
    _to_float,
)


def _norm_lote(valor: Any) -> str:
    return _normalizar_texto(valor).replace('.', '').strip()


def _row_lote_exato(row: Mapping[str, Any], lote: str) -> bool:
    alvo = _norm_lote(lote)
    for campo in ['Lote', 'Lote Informado', 'Lotes usados', 'lote_id', 'lote']:
        if campo in row and _norm_lote(row.get(campo)) == alvo:
            return True
    return False


def _filtrar_lote_exato(rows: Any, lote: str) -> list[dict[str, Any]]:
    return [row for row in _as_list_dict(rows) if _row_lote_exato(row, lote)]


def _data_key(valor: Any) -> str:
    if valor is None or valor == '':
        return ''
    if hasattr(valor, 'isoformat'):
        return valor.isoformat()[:10]
    txt = str(valor)[:10]
    try:
        return datetime.fromisoformat(txt).date().isoformat()
    except Exception:
        return txt


def _ultimo_replay(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    enumeradas = list(enumerate(rows))
    def chave(item: tuple[int, dict[str, Any]]) -> tuple[str, float, int]:
        idx, row = item
        seq = _to_float(row.get('Sequencia Saque') or row.get('sequencia_saque') or 0) or 0.0
        return (_data_key(row.get('Data') or row.get('data')), seq, idx)
    return sorted(enumeradas, key=chave)[-1][1]


def _primeiro_saldo_antes_negativo(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    for idx, row in enumerate(rows, start=1):
        valor = _to_float(row.get('Saldo Antes'))
        if valor is not None and valor < 0:
            return {'indice': idx, 'campo': 'Saldo Antes', 'valor': valor, 'linha': row}
    return None


def _linha_exauridos(saida: Any, lote: str) -> dict[str, Any] | None:
    for row in _as_list_dict(getattr(saida, 'lotes_exauridos', [])):
        if _norm_lote(row.get('Lote')) == _norm_lote(lote):
            return dict(row)
    return None


def _linha_valores_observaveis(contexto: Any, saida: Any, lote: str) -> dict[str, Any] | None:
    for row in construir_linhas_lotes_consolidados(contexto, saida, tipo='exauridos'):
        if _norm_lote(row.get('Lote')) == _norm_lote(lote):
            return dict(row)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description='Refina diagnostico do Lote 3120 mai entre replay e saida observavel V4O.0a.')
    parser.add_argument('--raiz', type=Path, default=ROOT)
    parser.add_argument('--lote', default='Lote 3120 mai')
    parser.add_argument('--saldo-app', type=float, default=50.0)
    parser.add_argument('--sem-csv', action='store_true')
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )
    saida_antes = construir_saida_canonica(contexto)
    agregados = construir_pacotes_temporais_agregados_saida_shadow(contexto)
    saida_depois = construir_saida_canonica(contexto)

    replay = agregados.pacote_replay_passado
    replay_rows = _filtrar_lote_exato(getattr(replay, 'log_movimentos_passados', []), args.lote)
    replay_final = _ultimo_replay(replay_rows)
    saldo_replay_final = _to_float((replay_final or {}).get('Saldo Remanescente'))

    saida_extrato_rows = _filtrar_lote_exato(getattr(saida_antes, 'extrato_passado', []), args.lote)
    saldo_negativo_saida = _primeiro_saldo_antes_negativo(saida_extrato_rows)

    linha_exaurido = _linha_exauridos(saida_antes, args.lote)
    linha_valores = _linha_valores_observaveis(contexto, saida_antes, args.lote)

    bruto_atual = _to_float((linha_valores or {}).get('Bruto atual'))
    liquido_atual = _to_float((linha_valores or {}).get('Líq. atual'))
    patrimonio_liquido = _to_float((linha_valores or {}).get('Patr. líq.'))
    rendimento_liquido = _to_float((linha_valores or {}).get('Rend. líq.'))
    status_saida = _normalizar_texto((linha_exaurido or {}).get('Status') or (linha_exaurido or {}).get('Status ciclo'))

    saida_classifica_exaurido = 'exaurido' in status_saida
    saida_zerada = bruto_atual == 0.0 and liquido_atual == 0.0
    rendimento_negativo = rendimento_liquido is not None and rendimento_liquido < 0
    saldo_modelo_comparado = saldo_replay_final is not None
    divergencia_replay_saida = bool(
        saldo_replay_final is not None
        and saldo_replay_final > 0
        and (saida_classifica_exaurido or saida_zerada or (liquido_atual is not None and abs(saldo_replay_final - liquido_atual) > 0.01))
    )
    causa_classificada = bool(divergencia_replay_saida and rendimento_negativo and saldo_negativo_saida is not None)

    resultado = {
        'adaptador': 'auditar_lote_3120_mai_replay_vs_saida_v4o0a',
        'lote_alvo': args.lote,
        'saldo_app_referencia': args.saldo_app,
        'replay_saldo_final_lote_3120_identificado': saldo_replay_final is not None,
        'replay_saldo_final_lote_3120': saldo_replay_final,
        'replay_linha_final_lote_3120': replay_final,
        'saida_extrato_passado_saldo_negativo_identificado': saldo_negativo_saida is not None,
        'saida_extrato_passado_saldo_negativo_evidencia': saldo_negativo_saida,
        'saida_lotes_exauridos_linha': linha_exaurido,
        'saida_lotes_exauridos_valores_observaveis': linha_valores,
        'saida_classifica_exaurido': saida_classifica_exaurido,
        'saida_zerada': saida_zerada,
        'bruto_atual_saida': bruto_atual,
        'liquido_atual_saida': liquido_atual,
        'patrimonio_liquido_saida': patrimonio_liquido,
        'rendimento_liquido_saida': rendimento_liquido,
        'rendimento_negativo_saida_identificado': rendimento_negativo,
        'saldo_modelo_replay_vs_saldo_app_comparado': saldo_modelo_comparado,
        'diferenca_saldo_app_menos_replay': None if saldo_replay_final is None else round(args.saldo_app - saldo_replay_final, 2),
        'diferenca_replay_menos_saida_liquido_atual': None if saldo_replay_final is None or liquido_atual is None else round(saldo_replay_final - liquido_atual, 2),
        'divergencia_replay_vs_saida_identificada': divergencia_replay_saida,
        'causa_classificada': causa_classificada,
        'causa_provavel': 'saida_observavel_classifica_como_exaurido_e_zera_lote_com_replay_saldo_positivo' if causa_classificada else 'pendente_classificacao',
        'replay_linhas_lote_qtd': len(replay_rows),
        'saida_extrato_passado_linhas_lote_qtd': len(saida_extrato_rows),
        'sem_alteracao_observavel': _iguais(saida_antes, saida_depois),
    }
    resultado['validacao_v4o0a_ok'] = all([
        resultado['replay_saldo_final_lote_3120_identificado'],
        resultado['saida_extrato_passado_saldo_negativo_identificado'],
        resultado['divergencia_replay_vs_saida_identificada'],
        resultado['rendimento_negativo_saida_identificado'],
        resultado['saldo_modelo_replay_vs_saldo_app_comparado'],
        resultado['causa_classificada'],
        resultado['sem_alteracao_observavel'],
    ])

    print('=== AUDITORIA LOTE 3120 MAI REPLAY VS SAIDA OBSERVAVEL V4O.0A ===')
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / 'saidas' / 'diagnostico'
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(saida_dir / 'auditoria_lote_3120_mai_replay_vs_saida_v4o0a_resumo.csv', index=False)
        pd.DataFrame(replay_rows).to_csv(saida_dir / 'auditoria_lote_3120_mai_replay_vs_saida_v4o0a_replay.csv', index=False)
        pd.DataFrame(saida_extrato_rows).to_csv(saida_dir / 'auditoria_lote_3120_mai_replay_vs_saida_v4o0a_saida_extrato.csv', index=False)

    return 0 if resultado['validacao_v4o0a_ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
