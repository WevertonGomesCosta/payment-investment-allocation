from __future__ import annotations

from pathlib import Path

from aplicacao.console.common import imprimir_itens_severidade, imprimir_linha_status, imprimir_pares, imprimir_titulo
from nucleo.identidade_baseline import metadados_versao_operacional

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]


def render_secao_execucao(*, versao, pacote_config, pacote_planilha, contexto, severidade_dependencias, auditoria_cache_cdi, data_ultimo_fator_cdi, resumo_por_aba, abas_primarias_reais, abas_auxiliares):
    metadados_versao = metadados_versao_operacional(
        RAIZ_REPOSITORIO,
        data_referencia=getattr(contexto, 'data_referencia', None),
    )

    imprimir_titulo('VERSÃO OPERACIONAL')
    imprimir_pares([
        ('versão atual', metadados_versao.get('versao_atual')),
        ('arquivo operacional oficial', metadados_versao.get('arquivo_operacional_oficial')),
    ])

    imprimir_titulo('BASELINE / ENTRADAS')
    imprimir_pares([
        ('raiz do repositório', pacote_config.raiz_repositorio),
        ('config carregado', pacote_config.caminho),
        ('planilha carregada', pacote_planilha.caminho),
    ])

    imprimir_titulo('EXECUÇÃO')
    imprimir_pares([
        ('timezone', contexto.timezone_nome),
        ('data de referência', contexto.data_referencia.isoformat()),
        ('warnings de rede configurados', 'sim' if contexto.warnings_configurados else 'não'),
    ])

    imprimir_titulo('ORIGEM DOS DADOS')
    imprimir_pares([
        ('dados financeiros', (getattr(pacote_planilha, 'auditoria', {}) or {}).get('fonte_planilha') or 'fallback_local'),
        ('status obtenção planilha', (getattr(pacote_planilha, 'auditoria', {}) or {}).get('fetch_status_planilha') or 'nao_tentado'),
        ('dados CDI/BCB', auditoria_cache_cdi.get('fonte_serie_cdi') or 'indisponivel'),
        ('status obtenção CDI/BCB', auditoria_cache_cdi.get('fetch_status') or ('cache_local' if auditoria_cache_cdi.get('fonte_serie_cdi') == 'cache_local' else 'nao_tentado')),
    ])

    imprimir_titulo('DEPENDÊNCIAS')
    imprimir_linha_status('Dependências essenciais da baseline', severidade_dependencias, 'baseline mínima e auditoria estrutural')
    imprimir_pares([
        ('instaladas', ', '.join(contexto.relatorio_dependencias.get('instaladas', [])) or 'nenhuma'),
        ('ausentes', ', '.join(contexto.relatorio_dependencias.get('ausentes', [])) or 'nenhuma'),
    ])

    imprimir_titulo('CACHE CDI DIÁRIO (BCB)')
    imprimir_linha_status('Cache diário de CDI para auditoria e replay', 'OK' if not str(auditoria_cache_cdi.get('fetch_status', '')).startswith('falha') else 'AVISO', f"{auditoria_cache_cdi.get('qtd_datas_serie_cdi', 0)} datas")
    imprimir_pares([
        ('data inicial da consulta', auditoria_cache_cdi.get('data_inicial_consulta')),
        ('data final da consulta', auditoria_cache_cdi.get('data_final_consulta')),
        ('última data com fator no cache', data_ultimo_fator_cdi),
        ('fonte da série', auditoria_cache_cdi.get('fonte_serie_cdi')),
        ('status do fetch', auditoria_cache_cdi.get('fetch_status')),
        ('cache atualizado para referência', 'sim' if auditoria_cache_cdi.get('cache_atualizado_para_referencia') else 'não'),
        ('data de atualização do cache', auditoria_cache_cdi.get('data_atualizacao_cache')),
        ('caminho do cache', auditoria_cache_cdi.get('caminho_cache')),
    ])
    imprimir_itens_severidade('avisos do cache CDI', (auditoria_cache_cdi.get('validacao') or {}).get('avisos') if isinstance(auditoria_cache_cdi.get('validacao'), dict) else None, 'AVISO')

    imprimir_titulo('ABAS ENCONTRADAS')
    for indice, nome_aba in enumerate(pacote_planilha.nomes_abas, start=1):
        print(f"- [{indice}] {nome_aba}")

    imprimir_titulo('RESUMO ESTRUTURAL DAS ABAS OPERACIONAIS CANÔNICAS')
    for _, nome_aba in abas_primarias_reais:
        info = resumo_por_aba.get(nome_aba)
        if not info:
            imprimir_linha_status(nome_aba, 'ERRO', 'aba ausente')
            continue
        imprimir_linha_status(nome_aba, 'OK', f"{info['n_linhas']} linhas, {info['n_colunas']} colunas")
        colunas = info.get('colunas', [])
        if colunas:
            print(f"  colunas (primeiras 8): {', '.join(colunas[:8])}")

    imprimir_titulo('ABAS OPERACIONAIS CANÔNICAS')
    imprimir_linha_status('Abas operacionais canônicas', 'OK', f"{len(abas_primarias_reais)} blocos esperados")
    for chave, nome_aba in abas_primarias_reais:
        presente = nome_aba in pacote_planilha.nomes_abas
        info = resumo_por_aba.get(nome_aba)
        linhas = info['n_linhas'] if info else '-'
        colunas = info['n_colunas'] if info else '-'
        sev = 'OK' if presente else 'ERRO'
        imprimir_linha_status(f'Bloco {chave}', sev, nome_aba)
        imprimir_pares([('presente', 'sim' if presente else 'não'), ('linhas', linhas), ('colunas', colunas)])
        print('')

    if abas_auxiliares:
        imprimir_titulo('ABAS AUXILIARES / FORA DO PACOTE CANÔNICO OPERACIONAL')
        imprimir_linha_status('Abas auxiliares identificadas', 'OK', f"{len(abas_auxiliares)} abas fora do pacote canônico operacional")
        for nome_aba in abas_auxiliares:
            info = resumo_por_aba.get(nome_aba)
            linhas = info['n_linhas'] if info else '-'
            colunas = info['n_colunas'] if info else '-'
            print(f"- {nome_aba}: {linhas} linhas, {colunas} colunas")
