from __future__ import annotations

import ast
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ler_texto(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def contar_scripts_raiz(base: Path) -> int:
    return len([p for p in (base / 'scripts').glob('*.py') if p.name != '__init__.py'])


def contar_diagnosticos(base: Path) -> int:
    return len([p for p in (base / 'scripts' / 'diagnostico').glob('*.py') if p.name != '__init__.py'])


def wrappers_com_bootstrap_ausente(base: Path) -> list[str]:
    alvos = []
    for path in (base / 'scripts').glob('*.py'):
        if path.name == '__init__.py':
            continue
        texto = ler_texto(path)
        if 'from scripts.diagnostico' in texto and 'sys.path.insert' not in texto:
            alvos.append(path.relative_to(base).as_posix())
    return sorted(alvos)


def wrappers_com_bootstrap_inconsistente(base: Path) -> list[str]:
    alvos = []
    for path in (base / 'scripts').glob('*.py'):
        if path.name == '__init__.py':
            continue
        texto = ler_texto(path)
        if 'from scripts.diagnostico' in texto and '.resolve().parent' in texto and 'parents[1]' not in texto and 'sys.path.insert' in texto:
            alvos.append(path.relative_to(base).as_posix())
    return sorted(alvos)


def contar_funcoes_duplicadas(base: Path, nomes: list[str]) -> dict[str, list[str]]:
    achados: dict[str, list[str]] = {n: [] for n in nomes}
    for path in base.rglob('*.py'):
        try:
            tree = ast.parse(path.read_text(encoding='utf-8'))
        except Exception:
            continue
        funcoes = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        for nome in nomes:
            if nome in funcoes:
                achados[nome].append(path.relative_to(base).as_posix())
    return {k: v for k, v in achados.items() if len(v) > 1}


def main() -> int:
    base = repo_root()
    relatorio = base / 'relatorios' / 'atuais' / 'AUDITORIA_ESTRUTURAL_REDUNDANCIA_COMPATIBILIDADE.md'
    print('=== AUDITORIA ESTRUTURAL DE REDUNDÂNCIA/COMPATIBILIDADE ===')
    print(f'arquivo: {relatorio}')
    if not relatorio.exists():
        print('status: AUSENTE')
        return 1

    texto = relatorio.read_text(encoding='utf-8')
    for marcador in [
        '## Achados principais',
        '### 1. Wrappers de compatibilidade',
        '### 2. Helpers duplicados',
        '### 3. Superfície diagnóstica',
    ]:
        if marcador not in texto:
            print(f'status: FALHA -> marcador ausente: {marcador}')
            return 1

    wrappers_raiz = contar_scripts_raiz(base)
    diagnosticos = contar_diagnosticos(base)
    ausentes = wrappers_com_bootstrap_ausente(base)
    inconsistentes = wrappers_com_bootstrap_inconsistente(base)
    duplicadas = contar_funcoes_duplicadas(base, [
        '_cfg',
        '_iterar_datas',
        '_simular_lote_ate_data',
        '_normalizar_valores_situacao_atual_exaurida',
        'obter_config',
    ])

    print('status: OK')
    print(f'- scripts raiz auditados: {wrappers_raiz}')
    print(f'- diagnósticos canônicos: {diagnosticos}')
    print(f'- wrappers com bootstrap ausente: {len(ausentes)}')
    for item in ausentes:
        print(f'  * {item}')
    print(f'- wrappers com bootstrap inconsistente: {len(inconsistentes)}')
    for item in inconsistentes:
        print(f'  * {item}')
    print(f'- grupos de helpers duplicados rastreados: {len(duplicadas)}')
    for nome, caminhos in sorted(duplicadas.items()):
        print(f'  * {nome}: {len(caminhos)} arquivo(s)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
