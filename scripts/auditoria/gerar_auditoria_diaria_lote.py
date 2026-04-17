from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import timedelta, date
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import caminho_saida_operacional, nome_auditoria_diaria_lote
from nucleo.calendario_financeiro import obter_taxa_dia_rendimento_lote
from nucleo.nucleo_financeiro_minimo import criar_lote_de_aporte, Lote
from nucleo.utilitarios_neutros import arredondar_monetario


@dataclass(slots=True)
class ContextoAuditoria:
    cfg: dict[str, Any]
    data_referencia: date
    calendario: Any
    serie_cdi: dict[date, float]
    tabela_iof: list[float]
    faixas_ir: list[dict[str, Any]]
    replay: Any
    nucleo: Any


def _clone_lote(lote: Lote) -> Lote:
    return criar_lote_de_aporte(
        lote.data_aplicacao,
        lote.valor_inicial,
        lote.id,
        {
            'investimento': lote.investimento,
            'produto_key': lote.produto_key,
            'data_base_fiscal': lote.data_base_fiscal,
            'data_recebimento': lote.data_recebimento,
            'fator_acumulado_inicial': 1.0,
            'taxa_base_cdi': lote.taxa_base_cdi,
            'taxa_bonus_cdi': lote.taxa_bonus_cdi,
            'dias_bonus': lote.dias_bonus,
            'principal_remanescente': lote.valor_inicial,
            'produto_isento_ir': lote.produto_isento_ir,
            'carencia_ate': lote.carencia_ate,
            'nao_disponivel_para_aporte': lote.nao_disponivel_para_aporte,
            'situacao_investimento': lote.situacao_investimento,
        },
    )


def _carregar_contexto() -> ContextoAuditoria:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ, instalar_automaticamente=False, incluir_switching_shadow=False, incluir_triagem=False)
    return ContextoAuditoria(
        cfg=contexto.pacote_config.conteudo,
        data_referencia=contexto.execucao.data_referencia,
        calendario=contexto.calendario_financeiro,
        serie_cdi=contexto.cache_cdi.serie_cdi,
        tabela_iof=contexto.tabela_iof,
        faixas_ir=contexto.faixas_ir,
        replay=contexto.replay_passado,
        nucleo=contexto.nucleo_financeiro,
    )


def _contar_dias_uteis_economicos_lote(lote: Lote, data_fim: date, contexto: ContextoAuditoria) -> int:
    if data_fim <= lote.data_aplicacao:
        return 0
    dias = 0
    atual = lote.data_aplicacao + timedelta(days=1)
    while atual <= data_fim:
        aplica, _, _ = obter_taxa_dia_rendimento_lote(
            atual,
            lote.data_aplicacao,
            contexto.calendario,
            data_recebimento=lote.data_recebimento,
            serie_cdi=contexto.serie_cdi,
            taxa_proj=float(contexto.calendario.taxa_dia_base),
            data_fechamento_referencia=contexto.data_referencia,
        )
        if aplica:
            dias += 1
        atual += timedelta(days=1)
    return dias


def _normalizar_str(v: Any) -> str:
    return '' if v is None else str(v)


def _agrupar_resgates_por_data(log_lote: pd.DataFrame) -> dict[date, list[dict[str, Any]]]:
    eventos: dict[date, list[dict[str, Any]]] = {}
    if log_lote.empty:
        return eventos
    for _, row in log_lote.sort_values(by=['Data', 'Sequencia Saque'], kind='stable').iterrows():
        dt = row['Data']
        eventos.setdefault(dt, []).append({
            'despesa_id': _normalizar_str(row.get('Despesa ID')),
            'conta': _normalizar_str(row.get('Conta')),
            'valor_conta': float(row.get('Valor Conta') or 0.0),
            'bruto': float(row.get('Bruto') or 0.0),
            'liquido': float(row.get('Liquido') or 0.0),
            'imposto': float(row.get('Imposto') or 0.0),
            'sequencia': int(row.get('Sequencia Saque') or 0),
        })
    return eventos


def gerar_auditoria_diaria_lote(lote_id: str) -> pd.DataFrame:
    contexto = _carregar_contexto()
    lotes_por_id = {l.id: l for l in contexto.nucleo.lotes_financeiros}
    if lote_id not in lotes_por_id:
        raise KeyError(f'Lote não encontrado na baseline atual: {lote_id}')

    lote_base = _clone_lote(lotes_por_id[lote_id])
    log_lote = contexto.replay.log_passado.copy()
    log_lote = log_lote[log_lote['Lote'].astype(str) == lote_id].copy()
    eventos_por_data = _agrupar_resgates_por_data(log_lote)

    linhas: list[dict[str, Any]] = []
    data_inicio = lote_base.data_aplicacao
    data_fim = contexto.data_referencia
    atual = data_inicio

    while atual <= data_fim:
        saldo_abertura_bruto = arredondar_monetario(float(lote_base.saldo_bruto or 0.0))
        saldo_abertura_liquido = arredondar_monetario(
            float(lote_base.valor_liquido_hoje(atual, tabela_iof=contexto.tabela_iof, faixas_ir=contexto.faixas_ir))
        )
        dias_corridos = max((atual - lote_base.data_aplicacao).days, 0)
        dias_uteis = _contar_dias_uteis_economicos_lote(lote_base, atual, contexto)

        aplica, taxa_dia, meta = obter_taxa_dia_rendimento_lote(
            atual,
            lote_base.data_aplicacao,
            contexto.calendario,
            data_recebimento=lote_base.data_recebimento,
            serie_cdi=contexto.serie_cdi,
            taxa_proj=float(contexto.calendario.taxa_dia_base),
            data_fechamento_referencia=contexto.data_referencia,
        )

        rendimento_bruto_dia = 0.0
        rendimento_liquido_dia = 0.0
        fator_dia = None
        multiplicador_lote = None
        if aplica and taxa_dia is not None:
            multiplicador_lote = lote_base.get_taxa_dia(atual, contexto.calendario)
            fator_dia = (1.0 + float(taxa_dia)) ** float(multiplicador_lote)
            saldo_antes = float(lote_base.saldo_bruto)
            lote_base.atualizar_juros(
                atual,
                taxa_dia,
                contexto.calendario,
                serie_cdi=contexto.serie_cdi,
                data_fechamento_referencia=contexto.data_referencia,
            )
            saldo_depois = float(lote_base.saldo_bruto)
            rendimento_bruto_dia = arredondar_monetario(saldo_depois - saldo_antes)
            liquido_antes = saldo_abertura_liquido
            liquido_depois_juros = arredondar_monetario(
                float(lote_base.valor_liquido_hoje(atual, tabela_iof=contexto.tabela_iof, faixas_ir=contexto.faixas_ir))
            )
            rendimento_liquido_dia = arredondar_monetario(liquido_depois_juros - liquido_antes)

        eventos = eventos_por_data.get(atual, [])
        resgate_bruto_dia = 0.0
        resgate_liquido_dia = 0.0
        imposto_dia = 0.0
        eventos_texto: list[str] = []
        if eventos:
            for evento in eventos:
                lote_base.sacar(evento['bruto'], tolerancia_monetaria=float(((contexto.cfg.get('replay') or {}).get('tolerancia_monetaria', 0.01)) or 0.01))
                resgate_bruto_dia += evento['bruto']
                resgate_liquido_dia += evento['liquido']
                imposto_dia += evento['imposto']
                eventos_texto.append(
                    f"{evento['despesa_id']} | {evento['conta']} | bruto={evento['bruto']:.2f} | liquido={evento['liquido']:.2f} | imposto={evento['imposto']:.2f}"
                )

        saldo_fechamento_bruto = arredondar_monetario(float(lote_base.saldo_bruto or 0.0))
        saldo_fechamento_liquido = arredondar_monetario(
            float(lote_base.valor_liquido_hoje(atual, tabela_iof=contexto.tabela_iof, faixas_ir=contexto.faixas_ir))
        )

        if atual < lote_base.data_recebimento:
            fase = 'antes_recebimento'
        elif atual <= lote_base.data_aplicacao:
            fase = 'aplicacao'
        elif lote_base.taxa_bonus_cdi > 0 and (atual - lote_base.data_base_fiscal).days < lote_base.dias_bonus:
            fase = 'bonus'
        else:
            fase = 'base'

        linhas.append({
            'Data': atual.isoformat(),
            'Fase': fase,
            'Dia rendimento': 'VERDADEIRO' if aplica else 'FALSO',
            'Fonte fator': meta.get('fonte'),
            'Data fator': meta.get('data_fator').isoformat() if getattr(meta.get('data_fator'), 'isoformat', None) else '',
            'Fallback': 'VERDADEIRO' if bool(meta.get('fallback')) else 'FALSO',
            'Dias corridos': dias_corridos,
            'Dias úteis': dias_uteis,
            'Dias úteis efetivos': dias_uteis,
            'Flag divergência dias úteis': 'FALSO',
            'Saldo abertura bruto': saldo_abertura_bruto,
            'Saldo abertura líquido': saldo_abertura_liquido,
            'Taxa dia decimal': round(float(taxa_dia or 0.0), 12) if taxa_dia is not None else None,
            'Multiplicador lote': float(multiplicador_lote) if multiplicador_lote is not None else None,
            'Fator dia lote': round(float(fator_dia), 12) if fator_dia is not None else None,
            'Rendimento bruto do dia': rendimento_bruto_dia,
            'Rendimento líquido do dia': rendimento_liquido_dia,
            'Resgate bruto do dia': arredondar_monetario(resgate_bruto_dia),
            'Resgate líquido do dia': arredondar_monetario(resgate_liquido_dia),
            'Imposto do dia': arredondar_monetario(imposto_dia),
            'Saldo fechamento bruto': saldo_fechamento_bruto,
            'Saldo fechamento líquido': saldo_fechamento_liquido,
            'Principal remanescente': arredondar_monetario(float(lote_base.principal_remanescente or 0.0)),
            'Eventos do dia': ' || '.join(eventos_texto),
        })
        atual += timedelta(days=1)

    return pd.DataFrame(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description='Gera auditoria diária de um lote usando a mesma convenção econômica da série CDI.')
    parser.add_argument('--lote', default='Lote 6630,64 fev.', help='ID do lote a auditar')
    parser.add_argument('--xlsx', default=str(caminho_saida_operacional(RAIZ, nome_auditoria_diaria_lote('Lote 6630,64 fev.', 'xlsx'))))
    parser.add_argument('--csv', default=str(caminho_saida_operacional(RAIZ, nome_auditoria_diaria_lote('Lote 6630,64 fev.', 'csv'))))
    args = parser.parse_args()

    df = gerar_auditoria_diaria_lote(args.lote)
    xlsx = Path(args.xlsx)
    csv = Path(args.csv)
    xlsx.parent.mkdir(parents=True, exist_ok=True)
    csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(xlsx, index=False)
    df.to_csv(csv, index=False, encoding='utf-8-sig')
    print(f'Auditoria diária gerada: {xlsx}')
    print(f'Auditoria diária gerada: {csv}')


if __name__ == '__main__':
    main()
