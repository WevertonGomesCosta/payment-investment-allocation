from __future__ import annotations

from pathlib import Path


VERSAO_VIGENTE = 'V100'
VERSAO_ANTERIOR = 'V99'


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def rel(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def coletar_artefatos_efemeros(base: Path) -> list[str]:
    itens: list[str] = []
    for path in base.rglob('__pycache__'):
        itens.append(rel(path, base))
    for path in base.rglob('*.pyc'):
        itens.append(rel(path, base))
    return sorted(set(itens))


def validar_indice_documental(base: Path) -> list[str]:
    erros: list[str] = []
    indice = base / 'relatorios' / 'INDICE_RELATORIOS.md'
    esperado = [
        'relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md',
        'relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md',
        f'relatorios/atuais/BASELINE_FIXA_{VERSAO_VIGENTE}.md',
        f'relatorios/atuais/VALIDACAO_LOCAL_{VERSAO_VIGENTE}.md',
        f'relatorios/atuais/ESTRUTURA_REPOSITORIO_{VERSAO_VIGENTE}.md',
        'relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md',
        'relatorios/atuais/MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md',
        'relatorios/atuais/MAPA_ABSORCAO_EXECUCAO_PRINCIPAL_SCRIPT_2.md',
        'relatorios/atuais/BENCHMARK_SHADOW_AGRUPADO_VS_INDIVIDUAL_SCRIPT1.md',
        'relatorios/atuais/BENCHMARK_SHADOW_RUNNER_SIMULACAO_FUTURA_SCRIPT2.md',
        'relatorios/atuais/AUDITORIA_RESIDUAL_DIVERGENCIAS_PROXY_V3_VS_HIBRIDO.md',
        'relatorios/atuais/AUDITORIA_CIRURGICA_42_CASOS_REAPROVEITAVEIS.md',
        'relatorios/atuais/AUDITORIA_FINA_TRANSICAO_DOMINANTE_3000B_8500MAR.md',
        'relatorios/atuais/AUDITORIA_ESTRUTURAL_REDUNDANCIA_COMPATIBILIDADE.md',
        'relatorios/atuais/CONSOLIDACAO_HELPERS_DUPLICADOS_BAIXO_RISCO.md',
        'relatorios/atuais/AUDITORIA_CASOS_CRITICOS_RUNNER_FUTURO_SHADOW.md',
        'relatorios/atuais/AUDITORIA_PRIMEIRA_QUEBRA_RUNNER_FUTURO_SHADOW.md',
    ]
    if not indice.exists():
        return ['relatorios/INDICE_RELATORIOS.md ausente']
    conteudo = indice.read_text(encoding='utf-8')
    for item in esperado:
        if item not in conteudo:
            erros.append(f'indice_documental_sem_referencia: {item}')
    return erros


def validar_referencias_ativas(base: Path) -> list[str]:
    erros: list[str] = []
    alvos = [
        base / 'nucleo',
        base / 'aplicacao',
        base / 'scripts',
        base / 'README.md',
        base / 'relatorios' / 'atuais',
    ]
    padroes_bloqueados = [
        'ContextoBaselineMenos1Dia',
        'carregar_contexto_baseline_menos_1_dia',
        f'BASELINE_FIXA_{VERSAO_ANTERIOR}.md',
        f'VALIDACAO_LOCAL_{VERSAO_ANTERIOR}.md',
        f'ESTRUTURA_REPOSITORIO_{VERSAO_ANTERIOR}.md',
    ]
    script_proprio = (base / 'scripts' / 'diagnostico' / 'verificar_release_baseline.py').resolve()
    ignorar = {
        script_proprio,
        (base / 'relatorios' / 'historico' / 'baselines' / f'BASELINE_FIXA_{VERSAO_ANTERIOR}.md').resolve(),
        (base / 'relatorios' / 'historico' / 'validacoes' / f'VALIDACAO_LOCAL_{VERSAO_ANTERIOR}.md').resolve(),
        (base / 'relatorios' / 'historico' / 'estruturas' / f'ESTRUTURA_REPOSITORIO_{VERSAO_ANTERIOR}.md').resolve(),
    }
    for alvo in alvos:
        caminhos = [alvo] if alvo.is_file() else [p for p in alvo.rglob('*') if p.is_file() and p.suffix in {'.py', '.md'}]
        for caminho in caminhos:
            if caminho.resolve() in ignorar:
                continue
            texto = caminho.read_text(encoding='utf-8')
            for padrao in padroes_bloqueados:
                if padrao in texto:
                    erros.append(f'referencia_ativa_indevida: {rel(caminho, base)} -> {padrao}')
    return erros


def validar_caminhos_canonicos(base: Path) -> list[str]:
    esperados = [
        'aplicacao/console/principal.py',
        'aplicacao/principal.py',
        'scripts/operacional/gerar_planilha_operacional.py',
        'scripts/auditoria/gerar_auditoria_diaria_lote.py',
        'scripts/diagnostico/inspecionar_base.py',
        'scripts/diagnostico/verificar_release_baseline.py',
        'scripts/diagnostico/inspecionar_contrato_f1.py',
        'scripts/diagnostico/inspecionar_recebidos_auditaveis.py',
        'scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py',
        'scripts/diagnostico/inspecionar_saldo_disponivel_geral.py',
        'scripts/diagnostico/inspecionar_decisao_local_v1.py',
        'scripts/diagnostico/inspecionar_auditoria_temporal_decisao_local.py',
        'scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py',
        'scripts/diagnostico/inspecionar_mapa_absorcao_legado.py',
        'scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py',
        'scripts/diagnostico/inspecionar_benchmark_agrupado_individual_shadow.py',
        'scripts/diagnostico/inspecionar_benchmark_runner_futuro_shadow.py',
        'scripts/diagnostico/inspecionar_auditoria_runner_futuro_shadow.py',
        'scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py',
        'scripts/diagnostico/inspecionar_switching_economico_shadow.py',
        'scripts/diagnostico/inspecionar_resolver_hibrido_5p_shadow.py',
        'scripts/diagnostico/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py',
        'scripts/diagnostico/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py',
        'scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py',
        'scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py',
        'scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py',
        'scripts/diagnostico/inspecionar_consolidacao_helpers_baixo_risco.py',
        'scripts/gerar_planilha_operacional.py',
        'scripts/gerar_auditoria_diaria_lote.py',
        'scripts/inspecionar_base.py',
        'scripts/verificar_release_baseline.py',
        'scripts/inspecionar_contrato_f1.py',
        'scripts/inspecionar_recebidos_auditaveis.py',
        'scripts/inspecionar_fontes_elegiveis_pagamento.py',
        'scripts/inspecionar_saldo_disponivel_geral.py',
        'scripts/inspecionar_decisao_local_v1.py',
        'scripts/inspecionar_auditoria_temporal_decisao_local.py',
        'scripts/inspecionar_comparativo_proxy_v2_v3.py',
        'scripts/inspecionar_mapa_absorcao_legado.py',
        'scripts/inspecionar_mapa_execucao_principal_script2.py',
        'scripts/inspecionar_benchmark_agrupado_individual_shadow.py',
        'scripts/inspecionar_benchmark_runner_futuro_shadow.py',
        'scripts/inspecionar_auditoria_runner_futuro_shadow.py',
        'scripts/inspecionar_primeira_quebra_runner_futuro_shadow.py',
        'scripts/inspecionar_switching_economico_shadow.py',
        'scripts/inspecionar_resolver_hibrido_5p_shadow.py',
        'scripts/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py',
        'scripts/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py',
        'scripts/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py',
        'scripts/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py',
        'scripts/inspecionar_auditoria_estrutural_redundancia.py',
        'scripts/inspecionar_consolidacao_helpers_baixo_risco.py',
        'nucleo/caixa_recebidos_auditaveis.py',
        'nucleo/auditoria_temporal_decisao_local.py',
        'nucleo/switching_economico_shadow.py',
        'nucleo/resolver_hibrido_5p_shadow.py',
        'nucleo/benchmark_agrupado_individual_shadow.py',
        'nucleo/benchmark_runner_futuro_shadow.py',
        'nucleo/auditoria_runner_futuro_shadow.py',
        'nucleo/auditoria_primeira_quebra_runner_futuro_shadow.py',
    ]
    erros: list[str] = []
    for item in esperados:
        if not (base / item).exists():
            erros.append(f'caminho_canonico_ausente: {item}')
    return erros


def main() -> int:
    base = repo_root()
    problemas: list[str] = []
    efemeros = coletar_artefatos_efemeros(base)
    problemas.extend([f'artefato_efemero_presente: {item}' for item in efemeros])
    problemas.extend(validar_indice_documental(base))
    problemas.extend(validar_referencias_ativas(base))
    problemas.extend(validar_caminhos_canonicos(base))

    print('=== CHECAGEM MÍNIMA DE RELEASE ===')
    print(f'raiz: {base}')
    print(f'versao_vigente_esperada: {VERSAO_VIGENTE}')
    if problemas:
        print(f'status: FALHA ({len(problemas)} problema(s))')
        for item in problemas:
            print(f'- {item}')
        return 1
    print('status: OK')
    print('- sem artefatos efêmeros')
    print('- índice documental vigente consistente')
    print('- sem referências ativas indevidas ao fluxo removido ou à documentação corrente anterior')
    print('- caminhos canônicos, wrappers e estruturas da F1 presentes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
