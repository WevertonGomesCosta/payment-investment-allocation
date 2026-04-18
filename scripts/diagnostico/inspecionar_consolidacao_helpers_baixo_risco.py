from __future__ import annotations

from pathlib import Path


ALVOS = {
    'normalizar_valores_situacao_atual_exaurida': [
        'nucleo/utilitarios_neutros.py',
        'aplicacao/console/principal.py',
        'scripts/operacional/gerar_planilha_operacional.py',
    ],
    'simular_lote_ate_data_shadow': [
        'nucleo/helpers_shadow_compartilhados.py',
        'nucleo/resolver_hibrido_5p_shadow.py',
        'nucleo/switching_economico_shadow.py',
    ],
    'iterar_datas_intervalo_exclusivo': [
        'nucleo/helpers_shadow_compartilhados.py',
        'nucleo/resolver_hibrido_5p_shadow.py',
        'nucleo/switching_economico_shadow.py',
    ],
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _contar_ocorrencias(base: Path, termo: str, caminho: str) -> int:
    texto = (base / caminho).read_text(encoding='utf-8')
    return texto.count(termo)


def main() -> int:
    base = repo_root()
    print('=== CONSOLIDAÇÃO DE HELPERS DE BAIXO RISCO ===')
    for termo, caminhos in ALVOS.items():
        print(f"\n[{termo}]")
        for caminho in caminhos:
            qtd = _contar_ocorrencias(base, termo, caminho)
            print(f'- {caminho}: {qtd}')
    print('\nstatus: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
