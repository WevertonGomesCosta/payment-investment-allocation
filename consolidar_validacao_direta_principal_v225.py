from __future__ import annotations

"""
V225 — Consolidar validação direta pelo arquivo principal.

Contexto:
- A pasta scripts/ foi removida.
- A validação oficial passa a ser:
    python aplicacao/principal.py

Este script:
1. Atualiza AGENTS.md e relatórios Codex-ready para remover referências a
   scripts/validacao/validar_rota_oficial_v225.py.
2. Registra relatório documental da decisão.
3. Não altera motor econômico, replay, pagamentos, switching, ranking, cache
   nem dados/config_atualizado.json.

Execute na raiz do repositório:
    python consolidar_validacao_direta_principal_v225.py

Depois valide:
    python aplicacao/principal.py
    git status
"""

from pathlib import Path
from datetime import datetime
import sys


REPO = Path(".").resolve()

ARQUIVOS_DOCUMENTAIS = [
    REPO / "AGENTS.md",
    REPO / "relatorios" / "atuais" / "codex_ready" / "CODEX_READY_V225.md",
    REPO / "relatorios" / "atuais" / "codex_ready" / "INVENTARIO_LEGADO_INATIVO_V225.md",
    REPO / "relatorios" / "atuais" / "codex_ready" / "AUDITORIA_RESIDUAIS_APLICACAO_NUCLEO_V225.md",
    REPO / "relatorios" / "atuais" / "codex_ready" / "REMOCAO_SECOES_TRIAGEM_PRE_CODEX_V225.md",
    REPO / "relatorios" / "atuais" / "codex_ready" / "ENXUGAMENTO_FINAL_REPOSITORIO_PRE_CODEX_V225.md",
]

ARQ_RELATORIO = (
    REPO
    / "relatorios"
    / "atuais"
    / "codex_ready"
    / "VALIDACAO_DIRETA_PELO_PRINCIPAL_V225.md"
)

ARQ_PRINCIPAL = REPO / "aplicacao" / "principal.py"

SUBSTITUICOES = [
    (
        "python scripts/validacao/validar_rota_oficial_v225.py",
        "python aplicacao/principal.py",
    ),
    (
        "`python scripts/validacao/validar_rota_oficial_v225.py`",
        "`python aplicacao/principal.py`",
    ),
    (
        "scripts/validacao/validar_rota_oficial_v225.py",
        "aplicacao/principal.py",
    ),
    (
        "validação oficial: `scripts/validacao/validar_rota_oficial_v225.py`",
        "validação oficial: `aplicacao/principal.py`",
    ),
    (
        "validacao oficial: `scripts/validacao/validar_rota_oficial_v225.py`",
        "validacao oficial: `aplicacao/principal.py`",
    ),
    (
        "Comando oficial de validação",
        "Comando oficial de validação operacional",
    ),
]


def falhar(msg: str) -> None:
    print(f"ERRO: {msg}", file=sys.stderr)
    raise SystemExit(1)


def relativo(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def ler(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def escrever(path: Path, texto: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(texto, encoding="utf-8")


def atualizar_agents(texto: str) -> str:
    novo = texto

    # Reescreve o bloco do comando oficial para evitar duplicações textuais.
    inicio = "## Comando oficial de validação operacional"
    if inicio in novo:
        partes = novo.split(inicio, 1)
        antes = partes[0]
        resto = partes[1]

        proximo = resto.find("\n## ")
        if proximo >= 0:
            depois = resto[proximo:]
        else:
            depois = ""

        bloco = """## Comando oficial de validação operacional

```bash
python aplicacao/principal.py
```

A validação oficial deve ser feita diretamente pela entrada principal. Não recriar pasta `scripts/` nem comandos paralelos de validação.
"""
        novo = antes.rstrip() + "\n\n" + bloco.rstrip() + "\n" + depois
    else:
        marcador = "## Arquitetura operacional obrigatória"
        bloco = """## Comando oficial de validação operacional

```bash
python aplicacao/principal.py
```

A validação oficial deve ser feita diretamente pela entrada principal. Não recriar pasta `scripts/` nem comandos paralelos de validação.
"""
        if marcador in novo:
            novo = novo.replace(marcador, bloco + "\n\n" + marcador, 1)
        else:
            novo = novo.rstrip() + "\n\n" + bloco

    return novo


def aplicar_substituicoes(texto: str) -> str:
    novo = texto
    for antigo, substituto in SUBSTITUICOES:
        novo = novo.replace(antigo, substituto)
    return novo


def main() -> None:
    if not ARQ_PRINCIPAL.exists():
        falhar("Entrada oficial não encontrada: aplicacao/principal.py")

    alterados: list[str] = []

    for path in ARQUIVOS_DOCUMENTAIS:
        if not path.exists():
            continue

        texto = ler(path)
        original = texto

        texto = aplicar_substituicoes(texto)

        if path.name == "AGENTS.md":
            texto = atualizar_agents(texto)

        if texto != original:
            escrever(path, texto)
            alterados.append(relativo(path))

    if alterados:
        alterados_txt = "\n".join(alterados)
    else:
        alterados_txt = "nenhum arquivo documental precisou de ajuste"

    relatorio = f"""# Validação direta pelo arquivo principal — V225

## Identificação

- Data/hora local: {datetime.now().isoformat(timespec='seconds')}
- Baseline: V225 Codex-ready enxuta

## Decisão

A pasta `scripts/` foi removida do repositório.

A validação oficial passa a ser feita diretamente por:

```bash
python aplicacao/principal.py
```

## Arquivos documentais atualizados

```text
{alterados_txt}
```

## Regra para Codex

Não recriar `scripts/validacao/`.

Qualquer alteração futura deve ser validada executando:

```bash
python aplicacao/principal.py
```

Critério esperado:

- execução sem erro;
- saída oficial gerada em `saidas/oficial/relatorio_operacional_v225.xlsx`;
- sem alteração econômica observável quando a tarefa for estrutural/documental.
"""

    escrever(ARQ_RELATORIO, relatorio)

    print("VALIDAÇÃO DIRETA PELO PRINCIPAL CONSOLIDADA")
    print("")
    print("Arquivos documentais atualizados:")
    if alterados:
        for item in alterados:
            print(f"- {item}")
    else:
        print("- nenhum arquivo documental precisou de ajuste")
    print(f"- {relativo(ARQ_RELATORIO)}")
    print("")
    print("Agora rode:")
    print("python aplicacao/principal.py")
    print("git status")


if __name__ == "__main__":
    main()
