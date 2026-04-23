from __future__ import annotations

from pathlib import Path


VERSAO_VIGENTE = "V139"
VERSAO_ANTERIOR = "V138"


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
        'relatorios/atuais/CONTRATO_V117_ALOCADOR_PAGAMENTOS_TERMINAL_E_PLANEJADOR_SWITCHING_TEMPORAL.md',
        'relatorios/atuais/CONTRATO_RANKING_CARTEIRA_V123.md',
        'relatorios/atuais/METRICA_CANONICA_MINIMA_CENTRAL.md',
        'relatorios/atuais/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md',
        'relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md',
        'relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md',
        'relatorios/atuais/MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md',
        'relatorios/atuais/COMPARADOR_HIBRIDO_SWITCHING_V132.md',
        'relatorios/atuais/GRADE_DIARIA_OFICIAL_HIBRIDA_V134.md',
        'relatorios/atuais/AUDITORIA_ATIVACAO_LOTES_NAO_APORTADOS_FUTUROS_V136.md',
        'relatorios/atuais/AUDITORIA_ATIVACAO_E_EXPANSAO_FUTUROS_V136.md',
        'relatorios/atuais/AUDITORIA_FECHAMENTO_FRENTE_TEMPORAL_V135.md',
        'relatorios/atuais/ALOCADOR_PAGAMENTOS_TERMINAL_V137.md',
        'relatorios/atuais/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138.md',
        'relatorios/atuais/LEIA-ME_OPERACIONAL.md',
        'relatorios/atuais/PREPARACAO_MODELOS_SCRIPT1_PAGAMENTOS_V139.md',
        'relatorios/atuais/BASELINE_FIXA_V139.md',
        'relatorios/atuais/VALIDACAO_LOCAL_V139.md',
        'relatorios/atuais/ESTRUTURA_REPOSITORIO_V139.md',
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
    ignorar = {script_proprio}
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
        'nucleo/pagamentos/modelos_script1/README.md',
        'saidas/oficial/README.md',
        'saidas/diagnostico/README.md',
        'saidas/historico/README.md',
        'saidas/operacional/README_COMPATIBILIDADE.md',
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
