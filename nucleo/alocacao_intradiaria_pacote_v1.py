from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from nucleo.caixa_recebidos_auditaveis import (
    _construir_candidatos_decisao_local_v1,
    _construir_mapa_produtos_proxy,
    _pagamentos_alvo_f1_4,
)
from nucleo.recomputacao_sequencial_central_v1 import (
    _perfil_pagamento_operacional,
    _demanda_protegida_futura_ponderada,
    _simular_movimento_candidato,
    _comparador_central,
    _coerce_date,
    _rotulo_fonte,
)
from nucleo.reescolha_dinamica_pos_quebra import _ajustar_candidatos_dinamicos


@dataclass(slots=True)
class PacoteAlocacaoIntradiariaPacoteV1:
    quadro_alocacao_intradiaria_pacote: pd.DataFrame
    quadro_resumo_pacotes: pd.DataFrame
    auditoria: dict[str, Any]


def _gerar_politicas_pacote(pagamentos_dia: list[dict[str, Any]]) -> list[tuple[str, str, list[dict[str, Any]]]]:
    base = sorted(
        pagamentos_dia,
        key=lambda p: (
            int(p.get('prioridade_classe_operacional') or 99),
            int(p.get('prioridade_intraclasse_operacional') or 99),
            str(p.get('despesa_id') or ''),
        ),
    )

    def ordenar(chave):
        return sorted(pagamentos_dia, key=chave)

    politicas = [
        (
            'padrao_classe',
            'ordem padrão por classe, intraclasse e despesa_id',
            base,
        ),
        (
            'valor_desc_intraclasse',
            'dentro de cada classe, maiores valores primeiro',
            ordenar(lambda p: (
                int(p.get('prioridade_classe_operacional') or 99),
                int(p.get('prioridade_intraclasse_operacional') or 99),
                -round(float(p.get('valor') or 0.0), 2),
                str(p.get('despesa_id') or ''),
            )),
        ),
        (
            'valor_asc_intraclasse',
            'dentro de cada classe, menores valores primeiro',
            ordenar(lambda p: (
                int(p.get('prioridade_classe_operacional') or 99),
                int(p.get('prioridade_intraclasse_operacional') or 99),
                round(float(p.get('valor') or 0.0), 2),
                str(p.get('despesa_id') or ''),
            )),
        ),
        (
            'protegida_maior_valor',
            'PROTEGIDA maiores primeiro; demais por classe padrão',
            ordenar(lambda p: (
                int(p.get('prioridade_classe_operacional') or 99),
                0 if str(p.get('classe_pagamento_operacional') or '') == 'PROTEGIDA' else 1,
                -round(float(p.get('valor') or 0.0), 2) if str(p.get('classe_pagamento_operacional') or '') == 'PROTEGIDA' else int(p.get('prioridade_intraclasse_operacional') or 99),
                str(p.get('despesa_id') or ''),
            )),
        ),
        (
            'semiprotegida_maior_valor',
            'mantém PROTEGIDA; SEMIPROTEGIDA maiores primeiro no mesmo dia',
            ordenar(lambda p: (
                int(p.get('prioridade_classe_operacional') or 99),
                int(p.get('prioridade_intraclasse_operacional') or 99) if str(p.get('classe_pagamento_operacional') or '') != 'SEMIPROTEGIDA' else -round(float(p.get('valor') or 0.0), 2),
                str(p.get('despesa_id') or ''),
            )),
        ),
    ]

    unicos: list[tuple[str, str, list[dict[str, Any]]]] = []
    assinaturas: set[tuple[str, ...]] = set()
    for politica_id, descricao, ordem in politicas:
        assinatura = tuple(str(p.get('despesa_id') or '') for p in ordem)
        if assinatura in assinaturas:
            continue
        assinaturas.add(assinatura)
        unicos.append((politica_id, descricao, ordem))
    return unicos


def _simular_pacote_dia(
    politica_id: str,
    politica_descricao: str,
    pagamentos_dia: list[dict[str, Any]],
    pagamentos_futuros_apos_dia: list[dict[str, Any]],
    *,
    quadro_saldo,
    quadro_fontes,
    mapa_produtos_proxy,
    mapa_lotes,
    consumo_generico,
    data_referencia,
    tabela_iof,
    faixas_ir,
    proxy_version,
    tolerancia_monetaria,
):
    mapa_lotes_local = {k: deepcopy(v) for k, v in mapa_lotes.items()}
    consumo_local = {k: round(float(v or 0.0), 2) for k, v in consumo_generico.items()}
    registros: list[dict[str, Any]] = []
    total_score = 0.0
    total_patrimonio = 0.0
    for ordem_no_pacote, pagamento in enumerate(pagamentos_dia, start=1):
        pagamento_id = str(pagamento.get('despesa_id') or '').strip()
        valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)
        classe_pagamento = str(pagamento.get('classe_pagamento_operacional') or '')
        subclasse_pagamento = str(pagamento.get('subclasse_pagamento_operacional') or '')
        data_pagamento = _coerce_date(pagamento.get('data')) or data_referencia
        pagamentos_restantes = pagamentos_dia[ordem_no_pacote:] + pagamentos_futuros_apos_dia
        demanda_futura = _demanda_protegida_futura_ponderada(pagamentos_restantes, data_pagamento)
        candidatos_base = _construir_candidatos_decisao_local_v1(pagamento, quadro_saldo, quadro_fontes, mapa_produtos_proxy)
        candidatos = _ajustar_candidatos_dinamicos(
            candidatos_base,
            valor_pagamento=valor_pagamento,
            mapa_lotes=mapa_lotes_local,
            consumo_generico=consumo_local,
            data_referencia=data_referencia,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            tolerancia_monetaria=tolerancia_monetaria,
        )
        if not candidatos:
            continue

        avaliacoes: list[dict[str, Any]] = []
        for candidato in candidatos:
            movimento = _simular_movimento_candidato(
                candidato,
                valor_pagamento=valor_pagamento,
                mapa_lotes=mapa_lotes_local,
                consumo_generico=consumo_local,
                data_referencia=data_referencia,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                tolerancia_monetaria=tolerancia_monetaria,
            )
            comparador, diagnostico = _comparador_central(
                classe_pagamento=classe_pagamento,
                subclasse_pagamento=subclasse_pagamento,
                valor_pagamento=valor_pagamento,
                candidato=candidato,
                candidatos_ajustados=candidatos,
                movimento_simulado=movimento,
                data_referencia=data_referencia,
                mapa_lotes=mapa_lotes_local,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                proxy_version=proxy_version,
                demanda_futura=demanda_futura,
            )
            avaliacoes.append({'candidato': candidato, 'movimento': movimento, 'comparador': comparador, 'diagnostico': diagnostico})

        avaliacoes.sort(key=lambda x: x['comparador'])
        melhor = avaliacoes[0]
        escolhido = melhor['candidato']
        mov = melhor['movimento']
        diag = melhor['diagnostico']
        max_liquido = max(round(float(item['movimento'].get('liquido_central') or 0.0), 2) for item in avaliacoes)
        fallback = bool(max_liquido <= tolerancia_monetaria)
        tipo_final = str(escolhido.get('tipo_fonte_escolhida') or '').strip()
        lote_final = str(escolhido.get('lote_id') or '').strip() or _rotulo_fonte(escolhido)
        if not fallback:
            if tipo_final == 'lote_resgatavel' and str(escolhido.get('lote_id') or '').strip() and mov.get('mapa_lotes_pos') is not None:
                mapa_lotes_local[str(escolhido.get('lote_id') or '').strip()] = mov['mapa_lotes_pos']
            elif mov.get('consumo_generico_pos'):
                for fonte_id_item, consumido in mov['consumo_generico_pos'].items():
                    consumo_local[fonte_id_item] = round(float(consumido or 0.0), 2)
        else:
            tipo_final = 'sem_fonte_viavel'
            lote_final = 'sem_fonte_viavel'
        coberto = bool(mov.get('pagamento_totalmente_coberto_central')) and not fallback
        total_score += round(float(diag.get('score_proxy_central') or 0.0), 4)
        total_patrimonio += round(float(diag.get('patrimonio_terminal_proxy') or 0.0), 2)
        registros.append({
            'pagamento_id': pagamento_id,
            'data_pagamento': pagamento.get('data'),
            'descricao_pagamento': str(pagamento.get('descricao') or ''),
            'valor_pagamento': valor_pagamento,
            'classe_pagamento_operacional': classe_pagamento,
            'subclasse_pagamento_operacional': subclasse_pagamento,
            'prioridade_intraclasse_operacional': int(pagamento.get('prioridade_intraclasse_operacional') or 99),
            'politica_pacote_id': politica_id,
            'politica_pacote_descricao': politica_descricao,
            'ordem_no_pacote': ordem_no_pacote,
            'lote_final_pacote': lote_final,
            'fonte_final_id': str(escolhido.get('fonte_escolhida_id') or ''),
            'tipo_fonte_final': tipo_final,
            'status_pacote': 'sem fonte viável no pacote' if fallback else ('coberto pelo pacote intradiário' if coberto else 'cobertura parcial no pacote intradiário'),
            'score_proxy_pacote': diag.get('score_proxy_central'),
            'violacao_protegida_pacote': diag.get('violacao_protegida'),
            'deficit_liquido_total_pacote': diag.get('deficit_liquido_total'),
            'pagamento_sem_cobertura_integral_pacote': diag.get('pagamento_sem_cobertura_integral'),
            'saldo_antes_pacote': 0.0 if fallback else mov.get('saldo_antes_central'),
            'bruto_pacote': 0.0 if fallback else mov.get('bruto_central'),
            'imposto_pacote': 0.0 if fallback else mov.get('imposto_central'),
            'liquido_pacote': 0.0 if fallback else mov.get('liquido_central'),
            'saldo_remanescente_pacote': 0.0 if fallback else mov.get('saldo_remanescente_central'),
            'pagamento_totalmente_coberto_pacote': coberto,
            'fallback_sem_fonte_viavel_pacote': fallback,
            'observacao_pacote': f"pacote={politica_id}; ordem={ordem_no_pacote}; classe={classe_pagamento}; deficit={diag.get('deficit_liquido_total'):.2f}",
        })
    quadro = pd.DataFrame(registros)
    if len(quadro) == 0:
        comparador = (999, 999999.0, 999999.0, 999, 999, 999999.0)
    else:
        viol_prot = int(quadro['violacao_protegida_pacote'].sum())
        deficit_prot = round(float(quadro.loc[quadro['classe_pagamento_operacional'] == 'PROTEGIDA', 'deficit_liquido_total_pacote'].sum()), 2)
        deficit_total = round(float(quadro['deficit_liquido_total_pacote'].sum()), 2)
        uncovered = int(quadro['pagamento_sem_cobertura_integral_pacote'].sum())
        cobertos = int(quadro['pagamento_totalmente_coberto_pacote'].sum())
        comparador = (
            viol_prot,
            deficit_prot,
            deficit_total,
            uncovered,
            -cobertos,
            round(total_score, 4),
            -round(total_patrimonio, 2),
        )
    return {
        'politica_id': politica_id,
        'politica_descricao': politica_descricao,
        'quadro': quadro,
        'comparador_pacote': comparador,
        'mapa_lotes_pos': mapa_lotes_local,
        'consumo_generico_pos': consumo_local,
        'resumo': {
            'violacoes_protegida_pacote': 0 if len(quadro) == 0 else int(quadro['violacao_protegida_pacote'].sum()),
            'deficit_protegida_pacote': 0.0 if len(quadro) == 0 else round(float(quadro.loc[quadro['classe_pagamento_operacional'] == 'PROTEGIDA', 'deficit_liquido_total_pacote'].sum()), 2),
            'deficit_total_pacote': 0.0 if len(quadro) == 0 else round(float(quadro['deficit_liquido_total_pacote'].sum()), 2),
            'pagamentos_sem_cobertura_pacote': 0 if len(quadro) == 0 else int(quadro['pagamento_sem_cobertura_integral_pacote'].sum()),
            'pagamentos_cobertos_pacote': 0 if len(quadro) == 0 else int(quadro['pagamento_totalmente_coberto_pacote'].sum()),
        },
    }


def carregar_alocacao_intradiaria_pacote_v1(
    dados_operacionais,
    fontes_elegiveis_pagamento,
    saldo_disponivel_geral,
    decisao_local_v1,
    replay_passado,
    recomputacao_sequencial_central_v1,
    *,
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    carteira_canonica: Any | None = None,
    proxy_version: str = 'v3',
    tolerancia_monetaria: float = 0.01,
) -> PacoteAlocacaoIntradiariaPacoteV1:
    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    if len(pagamentos_alvo) == 0:
        vazio = pd.DataFrame()
        return PacoteAlocacaoIntradiariaPacoteV1(vazio, vazio, {'validacao': {'ok': False, 'erros': ['sem_pagamentos_alvo'], 'avisos': []}, 'resumo': {}})

    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    quadro_saldo = saldo_disponivel_geral.quadro_saldo_disponivel.copy()
    mapa_produtos_proxy = _construir_mapa_produtos_proxy(carteira_canonica)
    mapa_lotes = {str(l.id): deepcopy(l) for l in getattr(replay_passado, 'lotes_apos_replay', [])}
    consumo_generico: dict[str, float] = {}
    mapa_decisao_local = {str(r.get('pagamento_id') or '').strip(): r for r in decisao_local_v1.quadro_decisao_local_v1.to_dict(orient='records')} if decisao_local_v1 is not None else {}
    mapa_central = {str(r.get('pagamento_id') or '').strip(): r for r in recomputacao_sequencial_central_v1.quadro_recomputacao_sequencial_central.to_dict(orient='records')} if recomputacao_sequencial_central_v1 is not None else {}

    pagamentos_alvo = pagamentos_alvo.copy()
    perfis = pagamentos_alvo['descricao'].apply(_perfil_pagamento_operacional)
    pagamentos_alvo['classe_pagamento_operacional'] = perfis.apply(lambda x: x['classe'])
    pagamentos_alvo['subclasse_pagamento_operacional'] = perfis.apply(lambda x: x['subclasse'])
    pagamentos_alvo['prioridade_classe_operacional'] = perfis.apply(lambda x: x['prioridade_classe'])
    pagamentos_alvo['prioridade_intraclasse_operacional'] = perfis.apply(lambda x: x['prioridade_intraclasse'])
    pagamentos_alvo = pagamentos_alvo.sort_values(by=['data', 'prioridade_classe_operacional', 'prioridade_intraclasse_operacional', 'despesa_id'], kind='stable').reset_index(drop=True)
    pagamentos_ordenados = pagamentos_alvo.to_dict(orient='records')

    pagamentos_por_data: dict[date, list[dict[str, Any]]] = {}
    for pagamento in pagamentos_ordenados:
        data_pag = _coerce_date(pagamento.get('data'))
        if data_pag is None:
            continue
        pagamentos_por_data.setdefault(data_pag, []).append(pagamento)

    registros: list[dict[str, Any]] = []
    resumo_pacotes: list[dict[str, Any]] = []
    primeira_sem = None
    primeira_protegida = None

    datas_ordenadas = sorted(pagamentos_por_data.keys())
    for idx_data, data_dia in enumerate(datas_ordenadas):
        pagamentos_dia = pagamentos_por_data[data_dia]
        pagamentos_futuros_apos_dia: list[dict[str, Any]] = []
        for data_futura in datas_ordenadas[idx_data + 1:]:
            pagamentos_futuros_apos_dia.extend(pagamentos_por_data[data_futura])
        politicas = _gerar_politicas_pacote(pagamentos_dia)
        simulacoes = []
        for politica_id, politica_desc, ordem in politicas:
            simulacoes.append(_simular_pacote_dia(
                politica_id,
                politica_desc,
                ordem,
                pagamentos_futuros_apos_dia,
                quadro_saldo=quadro_saldo,
                quadro_fontes=quadro_fontes,
                mapa_produtos_proxy=mapa_produtos_proxy,
                mapa_lotes=mapa_lotes,
                consumo_generico=consumo_generico,
                data_referencia=data_referencia,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                proxy_version=proxy_version,
                tolerancia_monetaria=tolerancia_monetaria,
            ))
        simulacoes.sort(key=lambda x: x['comparador_pacote'])
        melhor = simulacoes[0]
        mapa_lotes = melhor['mapa_lotes_pos']
        consumo_generico = melhor['consumo_generico_pos']
        quadro_melhor = melhor['quadro'].copy()
        for _, row in quadro_melhor.iterrows():
            pid = str(row.get('pagamento_id') or '').strip()
            central = mapa_central.get(pid, {})
            local = mapa_decisao_local.get(pid, {})
            reg = row.to_dict()
            reg['lote_final_central_v108'] = str(central.get('lote_final_central') or '')
            reg['mudou_vs_central_v108'] = bool(str(central.get('lote_final_central') or '') != str(row.get('lote_final_pacote') or ''))
            reg['lote_sugerido_local'] = str(local.get('lote_id_escolhido') or '')
            reg['mudou_vs_decisao_local'] = bool(str(local.get('lote_id_escolhido') or '') != str(row.get('lote_final_pacote') or ''))
            registros.append(reg)
            if not bool(row.get('pagamento_totalmente_coberto_pacote')) and primeira_sem is None:
                primeira_sem = {'Data': row.get('data_pagamento'), 'Descrição': row.get('descricao_pagamento') or '', 'Valor': round(float(row.get('valor_pagamento') or 0.0), 2), 'Lote pacote': row.get('lote_final_pacote') or ''}
            if bool(row.get('violacao_protegida_pacote')) and primeira_protegida is None:
                primeira_protegida = {'Data': row.get('data_pagamento'), 'Descrição': row.get('descricao_pagamento') or '', 'Valor': round(float(row.get('valor_pagamento') or 0.0), 2), 'Lote pacote': row.get('lote_final_pacote') or ''}
        resumo = melhor['resumo']
        resumo_pacotes.append({
            'data_pacote': data_dia,
            'politicas_avaliadas': len(simulacoes),
            'politica_escolhida': melhor['politica_id'],
            'politica_descricao': melhor['politica_descricao'],
            'violacoes_protegida_pacote': resumo.get('violacoes_protegida_pacote', 0),
            'deficit_protegida_pacote': resumo.get('deficit_protegida_pacote', 0.0),
            'deficit_total_pacote': resumo.get('deficit_total_pacote', 0.0),
            'pagamentos_sem_cobertura_pacote': resumo.get('pagamentos_sem_cobertura_pacote', 0),
            'pagamentos_cobertos_pacote': resumo.get('pagamentos_cobertos_pacote', 0),
            'comparador_pacote': str(melhor['comparador_pacote']),
        })

    colunas = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'classe_pagamento_operacional', 'subclasse_pagamento_operacional',
        'politica_pacote_id', 'politica_pacote_descricao', 'ordem_no_pacote', 'lote_sugerido_local', 'lote_final_central_v108', 'lote_final_pacote',
        'mudou_vs_central_v108', 'mudou_vs_decisao_local', 'tipo_fonte_final', 'status_pacote', 'score_proxy_pacote', 'violacao_protegida_pacote',
        'deficit_liquido_total_pacote', 'pagamento_sem_cobertura_integral_pacote', 'saldo_antes_pacote', 'bruto_pacote', 'imposto_pacote', 'liquido_pacote', 'saldo_remanescente_pacote', 'pagamento_totalmente_coberto_pacote', 'fallback_sem_fonte_viavel_pacote', 'observacao_pacote'
    ]
    quadro = pd.DataFrame(registros, columns=colunas).sort_values(by=['data_pagamento', 'ordem_no_pacote', 'pagamento_id'], kind='stable').reset_index(drop=True)
    quadro_resumo = pd.DataFrame(resumo_pacotes).sort_values(by=['data_pacote'], kind='stable').reset_index(drop=True)
    resumo = {
        'total_pagamentos_auditados': int(len(quadro)),
        'datas_com_pacote': int(quadro_resumo['data_pacote'].nunique()) if len(quadro_resumo) else 0,
        'politicas_avaliadas_total': int(quadro_resumo['politicas_avaliadas'].sum()) if len(quadro_resumo) else 0,
        'pagamentos_cobertos_integral_pacote': int(quadro['pagamento_totalmente_coberto_pacote'].sum()) if len(quadro) else 0,
        'pagamentos_sem_cobertura_integral_pacote': int(quadro['pagamento_sem_cobertura_integral_pacote'].sum()) if len(quadro) else 0,
        'violacoes_pagamentos_protegida_pacote': int(quadro['violacao_protegida_pacote'].sum()) if len(quadro) else 0,
        'deficit_liquido_total_pacote': round(float(quadro['deficit_liquido_total_pacote'].sum()), 2) if len(quadro) else 0.0,
        'mudancas_vs_central_v108': int(quadro['mudou_vs_central_v108'].sum()) if len(quadro) else 0,
        'mudancas_vs_decisao_local': int(quadro['mudou_vs_decisao_local'].sum()) if len(quadro) else 0,
        'primeira_sem_cobertura_data': primeira_sem.get('Data') if primeira_sem else None,
        'primeira_sem_cobertura_pagamento': primeira_sem.get('Descrição') if primeira_sem else None,
        'primeira_violation_protegida_data': primeira_protegida.get('Data') if primeira_protegida else None,
        'primeira_violation_protegida_pagamento': primeira_protegida.get('Descrição') if primeira_protegida else None,
    }
    amostra_pacotes = []
    for _, row in quadro_resumo.head(10).iterrows():
        amostra_pacotes.append({
            'Data': row.get('data_pacote'),
            'Política': row.get('politica_escolhida') or '',
            'Cobertos': int(row.get('pagamentos_cobertos_pacote') or 0),
            'Sem cobertura': int(row.get('pagamentos_sem_cobertura_pacote') or 0),
            'Viol. PROT': int(row.get('violacoes_protegida_pacote') or 0),
            'Déficit': round(float(row.get('deficit_total_pacote') or 0.0), 2),
        })
    amostra_mudancas = []
    for _, row in quadro[quadro['mudou_vs_central_v108'] == True].head(10).iterrows():
        amostra_mudancas.append({
            'Data': row.get('data_pagamento'),
            'Descrição': row.get('descricao_pagamento') or '',
            'Valor': round(float(row.get('valor_pagamento') or 0.0), 2),
            'Lote V108': row.get('lote_final_central_v108') or '',
            'Lote pacote': row.get('lote_final_pacote') or '',
            'Classe': row.get('classe_pagamento_operacional') or '',
            'Ordem': int(row.get('ordem_no_pacote') or 0),
        })
    amostra_sem_cobertura = []
    for _, row in quadro[quadro['pagamento_totalmente_coberto_pacote'] == False].head(10).iterrows():
        amostra_sem_cobertura.append({
            'Data': row.get('data_pagamento'),
            'Descrição': row.get('descricao_pagamento') or '',
            'Valor': round(float(row.get('valor_pagamento') or 0.0), 2),
            'Classe': row.get('classe_pagamento_operacional') or '',
            'Lote pacote': row.get('lote_final_pacote') or '',
            'Déficit': round(float(row.get('deficit_liquido_total_pacote') or 0.0), 2),
            'Fallback': 'sim' if bool(row.get('fallback_sem_fonte_viavel_pacote')) else '',
        })
    auditoria = {
        'validacao': {'ok': True, 'erros': [], 'avisos': []},
        'resumo': resumo,
        'amostra_pacotes': amostra_pacotes,
        'amostra_mudancas': amostra_mudancas,
        'amostra_sem_cobertura': amostra_sem_cobertura,
    }
    return PacoteAlocacaoIntradiariaPacoteV1(quadro_alocacao_intradiaria_pacote=quadro, quadro_resumo_pacotes=quadro_resumo, auditoria=auditoria)
