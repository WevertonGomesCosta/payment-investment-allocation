from __future__ import annotations

"""
V225 — Consolidar duplicidade simples de _slug_fonte.

Objetivo:
1. Confirmar equivalência entre:
   - nucleo/caixa_recebidos_auditaveis.py::_slug_fonte
   - nucleo/utilitarios_neutros.py::_slug_fonte
2. Manter nucleo.utilitarios_neutros._slug_fonte como fonte única.
3. Remover a definição local de _slug_fonte em nucleo/caixa_recebidos_auditaveis.py.
4. Importar _slug_fonte de nucleo.utilitarios_neutros.
5. Registrar relatório documental.
6. Não alterar motor econômico, replay, pagamentos, switching, ranking, cache
   nem dados/config_atualizado.json.

Execute na raiz do repositório:
    python consolidar_slug_fonte_v225.py

Depois valide:
    python aplicacao/principal.py
"""

from pathlib import Path
from datetime import datetime
import ast
import sys


REPO = Path(".").resolve()

ARQ_CAIXA = REPO / "nucleo" / "caixa_recebidos_auditaveis.py"
ARQ_UTIL = REPO / "nucleo" / "utilitarios_neutros.py"
ARQ_PRINCIPAL = REPO / "aplicacao" / "principal.py"

DIR_RELATORIOS = REPO / "relatorios" / "atuais" / "codex_ready"
ARQ_RELATORIO = DIR_RELATORIOS / "CONSOLIDACAO_SLUG_FONTE_V225.md"


def fail(msg: str) -> None:
    print(f"ERRO: {msg}", file=sys.stderr)
    raise SystemExit(1)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"Arquivo obrigatório ausente: {rel(path)}")
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_file(path: Path) -> ast.Module:
    text = read(path)
    try:
        return ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        fail(f"Erro de sintaxe em {rel(path)}: {exc}")


def encontrar_funcao(arvore: ast.Module, nome: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in arvore.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == nome:
            return node
    return None


def normalizar_corpo_funcao(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Compara somente o corpo lógico, ignorando nome, assinatura e anotações."""
    corpo = list(node.body)

    if corpo and isinstance(corpo[0], ast.Expr) and isinstance(getattr(corpo[0], "value", None), ast.Constant):
        if isinstance(corpo[0].value.value, str):
            corpo = corpo[1:]

    pseudo = ast.Module(body=corpo, type_ignores=[])
    return ast.dump(pseudo, include_attributes=False)


def trecho_funcao(texto: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    linhas = texto.splitlines()
    ini = getattr(node, "lineno", None)
    fim = getattr(node, "end_lineno", None)

    if ini is None:
        return ""

    if fim is None:
        fim = ini

    return "\n".join(linhas[ini - 1:fim])


def import_slug_ja_existe(arvore: ast.Module) -> bool:
    for node in arvore.body:
        if isinstance(node, ast.ImportFrom) and node.module == "nucleo.utilitarios_neutros":
            for alias in node.names:
                if alias.name == "_slug_fonte":
                    return True
    return False


def inserir_import_slug(texto: str, arvore: ast.Module) -> str:
    if import_slug_ja_existe(arvore):
        return texto

    linhas = texto.splitlines()

    # Inserir depois do último import/from import inicial, preservando docstring e future import.
    ultima_linha_import = 0

    for node in arvore.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            ultima_linha_import = max(ultima_linha_import, getattr(node, "end_lineno", getattr(node, "lineno", 0)))
            continue

        # Ignora docstring inicial.
        if isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant):
            if isinstance(node.value.value, str):
                continue

        # Parar no primeiro nó que não é import/docstring.
        break

    import_line = "from nucleo.utilitarios_neutros import _slug_fonte"

    if ultima_linha_import > 0:
        linhas.insert(ultima_linha_import, import_line)
    else:
        linhas.insert(0, import_line)

    return "\n".join(linhas) + "\n"


def remover_funcao_local(texto: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    linhas = texto.splitlines()
    ini = getattr(node, "lineno", None)
    fim = getattr(node, "end_lineno", None)

    if ini is None or fim is None:
        fail("Não consegui determinar o intervalo de linhas da função local _slug_fonte.")

    # Remove linhas em índice Python [ini-1:fim].
    novas = linhas[:ini - 1] + linhas[fim:]

    # Compacta excesso de linhas em branco sem alterar demais o arquivo.
    texto_novo = "\n".join(novas) + "\n"
    while "\n\n\n\n" in texto_novo:
        texto_novo = texto_novo.replace("\n\n\n\n", "\n\n\n")

    return texto_novo


def contar_ocorrencias_slug(texto: str) -> int:
    return texto.count("_slug_fonte")


def validar_patch(texto: str) -> None:
    try:
        ast.parse(texto)
    except SyntaxError as exc:
        fail(f"O arquivo resultante teria erro de sintaxe: {exc}")

    if "def _slug_fonte" in texto:
        fail("A definição local de _slug_fonte ainda permanece em caixa_recebidos_auditaveis.py.")

    if "from nucleo.utilitarios_neutros import _slug_fonte" not in texto:
        fail("Import de _slug_fonte de nucleo.utilitarios_neutros não foi inserido.")


def criar_relatorio(
    equivalente: bool,
    trecho_caixa: str,
    trecho_util: str,
    ocorrencias_antes: int,
    ocorrencias_depois: int,
) -> str:
    return f"""# Consolidação de `_slug_fonte` — V225

## Identificação

- Baseline: V225 Codex-ready enxuta
- Data/hora local: {datetime.now().isoformat(timespec='seconds')}
- Arquivo alterado: `nucleo/caixa_recebidos_auditaveis.py`
- Fonte única mantida: `nucleo/utilitarios_neutros.py::_slug_fonte`
- Alteração de motor econômico: não
- Alteração de replay: não
- Alteração de pagamentos: não
- Alteração de switching: não
- Alteração de ranking: não
- Alteração de cache: não
- Alteração de `dados/config_atualizado.json`: não

## Objetivo

Remover uma duplicidade simples e estruturalmente equivalente de `_slug_fonte`, mantendo `nucleo.utilitarios_neutros._slug_fonte` como fonte única.

## Equivalência

Equivalência estrutural do corpo da função:

```text
{str(equivalente).upper()}
```

### Definição removida de `nucleo/caixa_recebidos_auditaveis.py`

```python
{trecho_caixa}
```

### Definição preservada em `nucleo/utilitarios_neutros.py`

```python
{trecho_util}
```

## Alteração aplicada

- Removida a definição local de `_slug_fonte` em `nucleo/caixa_recebidos_auditaveis.py`.
- Inserido import:

```python
from nucleo.utilitarios_neutros import _slug_fonte
```

## Contagem textual em `nucleo/caixa_recebidos_auditaveis.py`

| Momento | Ocorrências de `_slug_fonte` |
|---|---:|
| antes | {ocorrencias_antes} |
| depois | {ocorrencias_depois} |

## Validação necessária

Executar:

```bash
python aplicacao/principal.py
```

Critério esperado:

- execução sem erro;
- `saidas/oficial/relatorio_operacional_v225.xlsx` gerado;
- sem alteração econômica observável.

## Decisão

A consolidação é considerada de baixo risco porque a auditoria anterior classificou as implementações como equivalentes estruturalmente e a função atua apenas como normalização textual de identificador de fonte.
"""


def main() -> None:
    if not ARQ_PRINCIPAL.exists():
        fail("Entrada oficial não encontrada: aplicacao/principal.py")

    texto_caixa = read(ARQ_CAIXA)
    texto_util = read(ARQ_UTIL)

    arvore_caixa = parse_file(ARQ_CAIXA)
    arvore_util = parse_file(ARQ_UTIL)

    func_caixa = encontrar_funcao(arvore_caixa, "_slug_fonte")
    func_util = encontrar_funcao(arvore_util, "_slug_fonte")

    if func_caixa is None:
        print("A definição local de _slug_fonte já não existe em nucleo/caixa_recebidos_auditaveis.py.")
        print("Nenhuma alteração funcional aplicada.")
        return

    if func_util is None:
        fail("Fonte canônica nucleo/utilitarios_neutros.py::_slug_fonte não encontrada.")

    corpo_caixa = normalizar_corpo_funcao(func_caixa)
    corpo_util = normalizar_corpo_funcao(func_util)
    equivalente = corpo_caixa == corpo_util

    if not equivalente:
        fail(
            "As implementações de _slug_fonte não são estruturalmente equivalentes. "
            "Microetapa bloqueada para evitar alteração funcional."
        )

    trecho_caixa = trecho_funcao(texto_caixa, func_caixa)
    trecho_util = trecho_funcao(texto_util, func_util)
    ocorrencias_antes = contar_ocorrencias_slug(texto_caixa)

    texto_sem_funcao = remover_funcao_local(texto_caixa, func_caixa)

    # Reparse após remoção antes de inserir import, para preservar consistência.
    try:
        arvore_sem_funcao = ast.parse(texto_sem_funcao, filename=str(ARQ_CAIXA))
    except SyntaxError as exc:
        fail(f"Erro de sintaxe após remover _slug_fonte local: {exc}")

    texto_final = inserir_import_slug(texto_sem_funcao, arvore_sem_funcao)
    validar_patch(texto_final)

    ocorrencias_depois = contar_ocorrencias_slug(texto_final)

    write(ARQ_CAIXA, texto_final)
    write(
        ARQ_RELATORIO,
        criar_relatorio(
            equivalente=equivalente,
            trecho_caixa=trecho_caixa,
            trecho_util=trecho_util,
            ocorrencias_antes=ocorrencias_antes,
            ocorrencias_depois=ocorrencias_depois,
        ),
    )

    print("CONSOLIDAÇÃO DE _slug_fonte CONCLUÍDA")
    print("")
    print(f"- equivalência estrutural confirmada: {equivalente}")
    print(f"- definição local removida de: {rel(ARQ_CAIXA)}")
    print(f"- fonte única preservada em: {rel(ARQ_UTIL)}")
    print(f"- relatório: {rel(ARQ_RELATORIO)}")
    print("")
    print("Agora rode:")
    print("python aplicacao/principal.py")


if __name__ == "__main__":
    main()
