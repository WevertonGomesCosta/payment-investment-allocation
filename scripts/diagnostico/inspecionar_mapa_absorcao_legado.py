from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    base = repo_root()
    path = base / 'relatorios' / 'atuais' / 'MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md'
    print('=== MAPA DE ABSORÇÃO LEGADO ===')
    print(f'arquivo: {path}')
    if not path.exists():
        print('status: AUSENTE')
        return 1
    texto = path.read_text(encoding='utf-8')
    for marcador in [
        '## Script 1 — otimização e validação',
        '### Migrar já',
        '## Script 2 — switching e diagnósticos',
        '## Prioridade imediata pós-V75',
    ]:
        if marcador not in texto:
            print(f'status: FALHA -> marcador ausente: {marcador}')
            return 1
    print('status: OK')
    print('- mapa vigente encontrado')
    print('- Script 1 classificado')
    print('- Script 2 classificado')
    print('- prioridades imediatas registradas')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
