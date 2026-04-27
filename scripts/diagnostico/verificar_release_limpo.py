"""Release checker com limpeza prévia de artefatos efêmeros.

Uso:
    python scripts/diagnostico/verificar_release_limpo.py
"""
from __future__ import annotations

try:
    from scripts.diagnostico.limpar_artefatos_efemeros import limpar_artefatos_efemeros
    from scripts.diagnostico.verificar_release_baseline import main as release_main
except ModuleNotFoundError:
    from limpar_artefatos_efemeros import limpar_artefatos_efemeros
    from verificar_release_baseline import main as release_main


def main() -> int:
    resumo = limpar_artefatos_efemeros()
    print("=== PRE-RELEASE CLEAN ===")
    print(f"diretorios_pycache_removidos: {resumo['diretorios_pycache_removidos']}")
    print(f"arquivos_bytecode_removidos: {resumo['arquivos_bytecode_removidos']}")
    return release_main()


if __name__ == "__main__":
    raise SystemExit(main())
