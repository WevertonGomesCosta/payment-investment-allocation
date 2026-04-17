"""Inspeciona a absorção do switching econômico legado em modo shadow."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_EXIBICAO = [
    'lote_id',
    'produto_origem_nome',
    'produto_destino_nome',
    'valor_liquido_resgatavel',
    'riqueza_manter_horizonte',
    'riqueza_switch_horizonte',
    'ganho_liquido_estimado',
    'score_switch_shadow',
    'status_confirmacao_destino',
    'elegivel_shadow',
    'motivo_bloqueio_shadow',
    'ranking_lote',
    'recomendado_shadow',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    pacote = contexto.switching_economico_shadow
    quadro = pacote.quadro_oportunidades
    melhores = pacote.quadro_melhores_oportunidades
    plano = pacote.plano_shadow
    auditoria = pacote.auditoria
    validacao = pacote.validacao

    print('=== SWITCHING ECONÔMICO LEGADO (SHADOW) ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"data_horizonte: {auditoria.get('resumo', {}).get('data_horizonte')}")
    print(f"qtd_lotes_ativos_avaliados: {auditoria.get('resumo', {}).get('qtd_lotes_ativos_avaliados')}")
    print(f"qtd_candidatos_switch: {auditoria.get('resumo', {}).get('qtd_candidatos_switch')}")
    print(f"qtd_linhas_analise: {auditoria.get('resumo', {}).get('qtd_linhas_analise')}")
    print(f"qtd_linhas_elegiveis: {auditoria.get('resumo', {}).get('qtd_linhas_elegiveis')}")
    print(f"qtd_recomendacoes_shadow: {auditoria.get('resumo', {}).get('qtd_recomendacoes_shadow')}")
    print(f"soma_ganho_shadow_recomendado: {auditoria.get('resumo', {}).get('soma_ganho_shadow_recomendado')}")
    print(f"bloqueios_por_motivo: {auditoria.get('resumo', {}).get('bloqueios_por_motivo', {})}")
    print(f"status_validacao: {'OK' if validacao.get('ok') else 'FALHA'}")
    if validacao.get('avisos'):
        print(f"avisos: {validacao['avisos']}")
    if validacao.get('erros'):
        print(f"erros: {validacao['erros']}")
        return 1

    if len(quadro) == 0:
        print('quadro vazio')
        return 1

    print('\n--- MELHORES OPORTUNIDADES POR LOTE ---')
    if len(melhores) > 0:
        print(melhores[COLUNAS_EXIBICAO].head(20).to_string(index=False))
    else:
        print('sem melhores oportunidades materializadas')

    print('\n--- PLANO SHADOW RECOMENDADO ---')
    if len(plano) > 0:
        print(plano[COLUNAS_EXIBICAO].head(20).to_string(index=False))
    else:
        print('sem recomendações acima do limiar mínimo')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
