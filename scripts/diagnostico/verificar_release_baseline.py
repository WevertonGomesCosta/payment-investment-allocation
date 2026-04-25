from __future__ import annotations

from pathlib import Path

VERSAO_VIGENTE = "V202"
VERSAO_ANTERIOR = "V201"


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
        'relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md',
        'relatorios/atuais/LEIA-ME_OPERACIONAL.md',
        'relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md',
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
        base / 'README.md',
        base / 'relatorios' / 'atuais',
        base / 'scripts' / 'README.md',
        base / 'saidas' / 'README.md',
    ]
    padroes_bloqueados = [
        'BASELINE_FIXA_V141.md',
        'VALIDACAO_LOCAL_V141.md',
        'ESTRUTURA_REPOSITORIO_V141.md',
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
        'scripts/diagnostico/verificar_release_baseline.py',
        'scripts/diagnostico/README.md',
        'scripts/operacional/README.md',
        'scripts/auditoria/README.md',
        'scripts/historico_raiz/README.md',
        'saidas/README.md',
        'saidas/oficial/README.md',
        'saidas/diagnostico/README.md',
        'saidas/historico/README.md',
        'saidas/operacional/README.md',
        'scripts/operacional/gerar_planilha_operacional.py',
        'nucleo/saida_canonica.py',
        'scripts/auditoria/gerar_auditoria_diaria_lote.py',
        'scripts/diagnostico/inspecionar_base.py',
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
