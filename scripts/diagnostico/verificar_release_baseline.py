from __future__ import annotations

from pathlib import Path


VERSAO_VIGENTE = 'V137'
VERSAO_ANTERIOR = 'V136'


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
        'relatorios/atuais/CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md',
        'relatorios/atuais/METRICA_CANONICA_MINIMA_CENTRAL.md',
        'relatorios/atuais/SANEAMENTO_CONTRATUAL_V106.md',
        'relatorios/atuais/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md',
        'relatorios/atuais/MOTOR_RECOMENDACAO_PAGAMENTOS_SWITCHING_V114.md',
        'relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md',
        f'relatorios/atuais/BASELINE_FIXA_{VERSAO_VIGENTE}.md',
        'relatorios/atuais/INTEGRACAO_FUNCIONAL_MINIMA_V117_RECORTE_CURTO.md',
        'relatorios/atuais/EXPANSAO_MULTIDESTINO_PLANEJADOR_SWITCHING_TEMPORAL_V121.md',
        'relatorios/atuais/TESTE_HORIZONTE_LONGO_PLANEJADOR_SWITCHING_TEMPORAL_V123.md',
        'relatorios/atuais/SIMULACAO_CENTRAL_CONTROLADA_HORIZONTE_LONGO_V124.md',
        'relatorios/atuais/AUDITORIA_MULTIHORIZONTE_CENARIOS_TEMPO_V125.md',
        'relatorios/atuais/AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V127.md',
        'relatorios/atuais/AUDITORIA_PARAMETROS_PRODUTOS_SWITCHING_V129.md',
        'relatorios/atuais/AVALIACAO_DIARIA_PARAMETRIZADA_JANELA_V130.md',
        'relatorios/atuais/AUDITORIA_CIRURGICA_BLOCO_8500_PICPAY_V131.md',
        'relatorios/atuais/COMPARADOR_HIBRIDO_SWITCHING_V132.md',
        'relatorios/atuais/GRADE_DIARIA_OFICIAL_HIBRIDA_V133.md',
        'relatorios/atuais/GRADE_DIARIA_OFICIAL_HIBRIDA_V134.md',
        'relatorios/atuais/AUDITORIA_FECHAMENTO_FRENTE_TEMPORAL_V135.md',
        'relatorios/atuais/AUDITORIA_ATIVACAO_LOTES_NAO_APORTADOS_FUTUROS_V136.md',
        'relatorios/atuais/AUDITORIA_ATIVACAO_E_EXPANSAO_FUTUROS_V136.md',
        'relatorios/atuais/ALOCADOR_PAGAMENTOS_TERMINAL_V137.md',
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
        'nucleo/planejador_switching_temporal_v1.py',
        'nucleo/alocador_pagamentos_terminal_v1.py',
        'nucleo/simulador_central_eventos_v1.py',
        'nucleo/avaliador_cenarios_conjuntos_v1.py',
    ]
    erros: list[str] = []
    for caminho in esperados:
        if not (base / caminho).exists():
            erros.append(f'caminho_canonico_ausente: {caminho}')
    return erros


def main() -> int:
    base = repo_root()
    erros = []
    erros.extend(validar_indice_documental(base))
    erros.extend(validar_referencias_ativas(base))
    erros.extend(validar_caminhos_canonicos(base))
    artefatos = coletar_artefatos_efemeros(base)
    if artefatos:
        erros.extend(f'artefato_efemero_presente: {item}' for item in artefatos)
    if erros:
        print('ERROS DE RELEASE:')
        for erro in erros:
            print(f'- {erro}')
        return 1
    print('OK - release baseline validado para', VERSAO_VIGENTE)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
