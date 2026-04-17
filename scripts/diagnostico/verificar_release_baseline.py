from __future__ import annotations

from pathlib import Path


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
        'relatorios/atuais/BASELINE_FIXA_V60.md',
        'relatorios/atuais/VALIDACAO_LOCAL_V60.md',
        'relatorios/atuais/ESTRUTURA_REPOSITORIO_V60.md',
        'relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md',
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
        'BASELINE_FIXA_V59.md',
        'VALIDACAO_LOCAL_V59.md',
        'ESTRUTURA_REPOSITORIO_V59.md',
    ]
    script_proprio = (base / 'scripts' / 'diagnostico' / 'verificar_release_baseline.py').resolve()
    ignorar = {
        script_proprio,
        (base / 'relatorios' / 'historico' / 'baselines' / 'BASELINE_FIXA_V59.md').resolve(),
        (base / 'relatorios' / 'historico' / 'validacoes' / 'VALIDACAO_LOCAL_V59.md').resolve(),
        (base / 'relatorios' / 'historico' / 'estruturas' / 'ESTRUTURA_REPOSITORIO_V59.md').resolve(),
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
        'scripts/gerar_planilha_operacional.py',
        'scripts/gerar_auditoria_diaria_lote.py',
        'scripts/inspecionar_base.py',
        'scripts/verificar_release_baseline.py',
        'scripts/inspecionar_contrato_f1.py',
        'nucleo/caixa_recebidos_auditaveis.py',
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
    if problemas:
        print(f'status: FALHA ({len(problemas)} problema(s))')
        for item in problemas:
            print(f'- {item}')
        return 1
    print('status: OK')
    print('- sem artefatos efêmeros')
    print('- índice documental vigente consistente')
    print('- sem referências ativas indevidas ao fluxo removido ou à documentação corrente anterior')
    print('- caminhos canônicos, wrappers e contrato mínimo da F1 presentes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
