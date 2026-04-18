from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    base = repo_root()
    path = base / 'relatorios' / 'atuais' / 'MAPA_ABSORCAO_EXECUCAO_PRINCIPAL_SCRIPT_2.md'
    print('=== MAPA DE ABSORÇÃO — EXECUÇÃO PRINCIPAL DO SCRIPT 2 ===')
    print(f'arquivo: {path}')
    if not path.exists():
        print('status: AUSENTE')
        return 1
    texto = path.read_text(encoding='utf-8')
    for marcador in [
        '## Escopo',
        '### Absorver já (em shadow/diagnóstico)',
        '### Absorver depois',
        '### Não absorver agora',
        '### Já substituído pela baseline atual',
        '## Prioridade pós-V87',
    ]:
        if marcador not in texto:
            print(f'status: FALHA -> marcador ausente: {marcador}')
            return 1
    print('status: OK')
    print('- mapa da execução principal do Script 2 encontrado')
    print('- absorção imediata classificada')
    print('- partes adiadas e não absorvíveis registradas')
    print('- prioridade pós-V87 registrada')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
