from __future__ import annotations

"""
V225 — Auditoria documental das duplicidades econômicas.

Funções auditadas:
- _projetar_valor_terminal
- _patrimonio_terminal_proxy

Objetivo:
- Mapear definições, chamadas, assinaturas, contexto de uso e diferenças estruturais.
- Comparar fórmulas, parâmetros e dependências internas.
- Decidir se as duplicidades são semanticamente distintas ou candidatas futuras a fonte única.
- Não alterar código funcional.

Execute na raiz do repositório:
    python auditar_duplicidades_economicas_v225.py

Depois valide:
    python aplicacao/principal.py

Saídas:
    relatorios/atuais/codex_ready/AUDITORIA_DUPLICIDADES_ECONOMICAS_V225.md
    relatorios/atuais/codex_ready/auditoria_duplicidades_economicas_definicoes_v225.csv
    relatorios/atuais/codex_ready/auditoria_duplicidades_economicas_chamadas_v225.csv
    relatorios/atuais/codex_ready/auditoria_duplicidades_economicas_comparacao_v225.csv
"""

from pathlib import Path
from datetime import datetime
import ast
import csv
import hashlib
import re
import sys
from collections import defaultdict
from typing import Any


REPO = Path(".").resolve()

DIRS_AUDITAR = [
    REPO / "aplicacao",
    REPO / "nucleo",
]

ARQ_PRINCIPAL = REPO / "aplicacao" / "principal.py"

DIR_RELATORIOS = REPO / "relatorios" / "atuais" / "codex_ready"
ARQ_RELATORIO = DIR_RELATORIOS / "AUDITORIA_DUPLICIDADES_ECONOMICAS_V225.md"
ARQ_DEFINICOES = DIR_RELATORIOS / "auditoria_duplicidades_economicas_definicoes_v225.csv"
ARQ_CHAMADAS = DIR_RELATORIOS / "auditoria_duplicidades_economicas_chamadas_v225.csv"
ARQ_COMPARACAO = DIR_RELATORIOS / "auditoria_duplicidades_economicas_comparacao_v225.csv"

FUNCOES_ALVO = [
    "_projetar_valor_terminal",
    "_patrimonio_terminal_proxy",
]

ARQUIVOS_ESPERADOS = {
    "_projetar_valor_terminal": [
        "nucleo/planejador_switching_temporal_v1.py",
        "nucleo/simulador_central_eventos_v1.py",
    ],
    "_patrimonio_terminal_proxy": [
        "nucleo/recomputacao_sequencial_central_v1.py",
        "nucleo/simulador_central_eventos_v1.py",
    ],
}


def fail(msg: str) -> None:
    print(f"ERRO: {msg}", file=sys.stderr)
    raise SystemExit(1)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def module_name(path: Path) -> str:
    return ".".join(path.relative_to(REPO).with_suffix("").parts)


def listar_py() -> list[Path]:
    arquivos: list[Path] = []
    for base in DIRS_AUDITAR:
        if base.exists():
            arquivos.extend(p for p in base.rglob("*.py") if p.is_file())
    return sorted(arquivos)


def ler(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse(path: Path, texto: str) -> ast.Module | None:
    try:
        return ast.parse(texto, filename=str(path))
    except SyntaxError:
        return None


def linhas_do_no(texto: str, node: ast.AST) -> str:
    linhas = texto.splitlines()
    ini = getattr(node, "lineno", None)
    fim = getattr(node, "end_lineno", None)
    if ini is None:
        return ""
    if fim is None:
        fim = ini
    return "\n".join(linhas[ini - 1:fim])


def hash_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def assinatura_funcao(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = node.args
    partes: list[str] = []

    total_pos = list(args.posonlyargs) + list(args.args)
    defaults = list(args.defaults)
    default_offset = len(total_pos) - len(defaults)

    for i, arg in enumerate(total_pos):
        nome = arg.arg
        if i >= default_offset:
            nome += "=..."
        partes.append(nome)

    if args.posonlyargs:
        partes.insert(len(args.posonlyargs), "/")

    if args.vararg:
        partes.append("*" + args.vararg.arg)
    elif args.kwonlyargs:
        partes.append("*")

    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        nome = arg.arg
        if default is not None:
            nome += "=..."
        partes.append(nome)

    if args.kwarg:
        partes.append("**" + args.kwarg.arg)

    return "(" + ", ".join(partes) + ")"


def normalizar_ast_funcao(node: ast.AST) -> str:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        corpo = list(node.body)
        if corpo and isinstance(corpo[0], ast.Expr) and isinstance(getattr(corpo[0], "value", None), ast.Constant):
            if isinstance(corpo[0].value.value, str):
                corpo = corpo[1:]
        pseudo = ast.Module(body=corpo, type_ignores=[])
        return ast.dump(pseudo, include_attributes=False)
    return ast.dump(node, include_attributes=False)


def resumo_corpo(codigo: str, limite: int = 320) -> str:
    compacto = " ".join(l.strip() for l in codigo.splitlines() if l.strip())
    compacto = re.sub(r"\s+", " ", compacto)
    if len(compacto) > limite:
        compacto = compacto[: limite - 3] + "..."
    return compacto


def coletar_nomes(node: ast.AST) -> list[str]:
    nomes = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            nomes.add(n.id)
    return sorted(nomes)


def coletar_chaves_get(node: ast.AST) -> list[str]:
    chaves = set()

    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get":
            if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                chaves.add(n.args[0].value)

    return sorted(chaves)


def coletar_operadores(node: ast.AST) -> list[str]:
    operadores = set()

    for n in ast.walk(node):
        if isinstance(n, ast.BinOp):
            operadores.add(type(n.op).__name__)
        elif isinstance(n, ast.UnaryOp):
            operadores.add(type(n.op).__name__)
        elif isinstance(n, ast.BoolOp):
            operadores.add(type(n.op).__name__)
        elif isinstance(n, ast.Compare):
            operadores.update(type(op).__name__ for op in n.ops)

    return sorted(operadores)


def coletar_constantes_numericas(node: ast.AST) -> list[str]:
    valores = set()

    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            valores.add(repr(n.value))

    return sorted(valores)


def coletar_chamadas_internas(node: ast.AST) -> list[str]:
    chamadas = set()

    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                chamadas.add(n.func.id)
            elif isinstance(n.func, ast.Attribute):
                chamadas.add(n.func.attr)

    return sorted(chamadas)


def encontrar_funcoes(path: Path, texto: str, arvore: ast.Module | None) -> list[dict]:
    if arvore is None:
        return []

    defs: list[dict] = []

    for node in ast.walk(arvore):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in FUNCOES_ALVO:
            codigo = linhas_do_no(texto, node)
            ast_norm = normalizar_ast_funcao(node)
            defs.append({
                "funcao": node.name,
                "arquivo": rel(path),
                "modulo": module_name(path),
                "linha_inicio": getattr(node, "lineno", ""),
                "linha_fim": getattr(node, "end_lineno", ""),
                "assinatura": assinatura_funcao(node),
                "hash_codigo": hash_texto(codigo),
                "hash_ast": hash_texto(ast_norm),
                "linhas_codigo": len(codigo.splitlines()),
                "nomes_referenciados": "; ".join(coletar_nomes(node)),
                "chaves_get": "; ".join(coletar_chaves_get(node)),
                "operadores": "; ".join(coletar_operadores(node)),
                "constantes_numericas": "; ".join(coletar_constantes_numericas(node)),
                "chamadas_internas": "; ".join(coletar_chamadas_internas(node)),
                "corpo_resumo": resumo_corpo(codigo),
            })

    return defs


class CallCollector(ast.NodeVisitor):
    def __init__(self, path: Path, texto: str):
        self.path = path
        self.texto = texto
        self.stack: list[str] = []
        self.calls: list[dict] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        nome = ""

        if isinstance(node.func, ast.Name):
            nome = node.func.id
        elif isinstance(node.func, ast.Attribute):
            nome = node.func.attr

        if nome in FUNCOES_ALVO:
            linhas = self.texto.splitlines()
            lineno = getattr(node, "lineno", "")
            conteudo = ""
            if isinstance(lineno, int) and 1 <= lineno <= len(linhas):
                conteudo = linhas[lineno - 1].strip()

            self.calls.append({
                "funcao": nome,
                "arquivo": rel(self.path),
                "modulo": module_name(self.path),
                "escopo": ".".join(self.stack),
                "linha": lineno,
                "conteudo": conteudo,
            })

        self.generic_visit(node)


def coletar_chamadas(path: Path, texto: str, arvore: ast.Module | None) -> list[dict]:
    if arvore is None:
        return []

    collector = CallCollector(path, texto)
    collector.visit(arvore)
    return collector.calls


def comparar_definicoes(defs_por_funcao: dict[str, list[dict]]) -> list[dict]:
    comparacoes: list[dict] = []

    for funcao in FUNCOES_ALVO:
        defs = defs_por_funcao.get(funcao, [])
        hashes = sorted(set(d["hash_ast"] for d in defs))
        assinaturas = sorted(set(d["assinatura"] for d in defs))
        arquivos = sorted(d["arquivo"] for d in defs)

        if len(defs) == 0:
            status = "ausente"
            decisao = "inspecionar manualmente; função alvo não encontrada"
            fonte_unica = "nenhuma"
            risco = "alto"
        elif len(defs) == 1:
            status = "sem_duplicidade"
            decisao = "manter"
            fonte_unica = defs[0]["arquivo"]
            risco = "baixo"
        else:
            identicas = len(hashes) == 1
            mesmas_assinaturas = len(assinaturas) == 1

            if identicas and mesmas_assinaturas:
                status = "duplicidade_equivalente"
                decisao = "pode ser candidata futura a fonte única, com validação"
                fonte_unica = "avaliar menor acoplamento"
                risco = "medio"
            else:
                status = "duplicidade_semantica_distinta_ou_nao_comprovada"

                if funcao == "_projetar_valor_terminal":
                    decisao = (
                        "manter separadas nesta etapa; funções têm assinaturas/contextos distintos "
                        "e podem aplicar convenções econômicas diferentes entre planejamento de switching "
                        "e simulação central"
                    )
                    fonte_unica = "não definida"
                    risco = "alto"
                elif funcao == "_patrimonio_terminal_proxy":
                    decisao = (
                        "manter separadas nesta etapa; funções operam sobre estruturas de entrada diferentes "
                        "e provavelmente representam proxies distintos de patrimônio terminal"
                    )
                    fonte_unica = "não definida"
                    risco = "alto"
                else:
                    decisao = "auditar manualmente"
                    fonte_unica = "não definida"
                    risco = "alto"

            chaves_por_def = [set((d.get("chaves_get") or "").split("; ")) if d.get("chaves_get") else set() for d in defs]
            chamadas_por_def = [set((d.get("chamadas_internas") or "").split("; ")) if d.get("chamadas_internas") else set() for d in defs]
            operadores_por_def = [set((d.get("operadores") or "").split("; ")) if d.get("operadores") else set() for d in defs]

            intersec_chaves = set.intersection(*chaves_por_def) if chaves_por_def and all(chaves_por_def) else set()
            union_chaves = set.union(*chaves_por_def) if chaves_por_def else set()

            intersec_chamadas = set.intersection(*chamadas_por_def) if chamadas_por_def and all(chamadas_por_def) else set()
            union_chamadas = set.union(*chamadas_por_def) if chamadas_por_def else set()

            intersec_ops = set.intersection(*operadores_por_def) if operadores_por_def and all(operadores_por_def) else set()
            union_ops = set.union(*operadores_por_def) if operadores_por_def else set()

            comparacoes.append({
                "funcao": funcao,
                "qtd_definicoes": len(defs),
                "arquivos": "; ".join(arquivos),
                "qtd_hashes_ast": len(hashes),
                "hashes_ast": "; ".join(hashes),
                "qtd_assinaturas": len(assinaturas),
                "assinaturas": "; ".join(assinaturas),
                "status_semantico": status,
                "risco_consolidacao": risco,
                "fonte_unica_recomendada": fonte_unica,
                "decisao": decisao,
                "chaves_get_comuns": "; ".join(sorted(intersec_chaves)),
                "chaves_get_uniao": "; ".join(sorted(union_chaves)),
                "chamadas_internas_comuns": "; ".join(sorted(intersec_chamadas)),
                "chamadas_internas_uniao": "; ".join(sorted(union_chamadas)),
                "operadores_comuns": "; ".join(sorted(intersec_ops)),
                "operadores_uniao": "; ".join(sorted(union_ops)),
            })

    return comparacoes


def escrever_csv(path: Path, linhas: list[dict], campos: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for linha in linhas:
            writer.writerow({campo: linha.get(campo, "") for campo in campos})


def criar_relatorio(definicoes: list[dict], chamadas: list[dict], comparacoes: list[dict]) -> str:
    defs_por_funcao = defaultdict(list)
    calls_por_funcao = defaultdict(list)

    for d in definicoes:
        defs_por_funcao[d["funcao"]].append(d)

    for c in chamadas:
        calls_por_funcao[c["funcao"]].append(c)

    def tabela_comparacoes() -> str:
        linhas = [
            "| Função | Definições | Status semântico | Risco | Fonte única recomendada | Decisão |",
            "|---|---:|---|---:|---|---|",
        ]
        for c in comparacoes:
            decisao = c["decisao"].replace("|", "\\|")
            linhas.append(
                f"| `{c['funcao']}` | {c['qtd_definicoes']} | {c['status_semantico']} | "
                f"{c['risco_consolidacao']} | {c['fonte_unica_recomendada']} | {decisao} |"
            )
        return "\n".join(linhas)

    def bloco_funcao(funcao: str) -> str:
        defs = defs_por_funcao.get(funcao, [])
        calls = calls_por_funcao.get(funcao, [])

        linhas = [f"### `{funcao}`", ""]

        if defs:
            linhas.append("| Arquivo | Linha | Assinatura | Hash AST | Chaves `.get()` | Chamadas internas | Resumo |")
            linhas.append("|---|---:|---|---|---|---|---|")
            for d in defs:
                resumo = d["corpo_resumo"].replace("|", "\\|")
                linhas.append(
                    f"| `{d['arquivo']}` | {d['linha_inicio']} | `{d['assinatura']}` | "
                    f"`{d['hash_ast']}` | {d['chaves_get']} | {d['chamadas_internas']} | {resumo} |"
                )
        else:
            linhas.append("nenhuma definição encontrada")

        linhas.append("")
        linhas.append(f"Chamadas AST detectadas: {len(calls)}")

        if calls:
            linhas.append("")
            linhas.append("| Arquivo | Linha | Escopo | Conteúdo |")
            linhas.append("|---|---:|---|---|")
            for c in calls:
                conteudo = c["conteudo"].replace("|", "\\|")
                linhas.append(f"| `{c['arquivo']}` | {c['linha']} | `{c['escopo']}` | {conteudo} |")

        return "\n".join(linhas)

    texto_funcoes = "\n\n".join(bloco_funcao(f) for f in FUNCOES_ALVO)

    return f"""# Auditoria de duplicidades econômicas — V225

## Identificação

- Data/hora local: {datetime.now().isoformat(timespec='seconds')}
- Diretórios auditados:
  - `aplicacao/`
  - `nucleo/`
- Alteração de código funcional: não

## Funções auditadas

```text
{chr(10).join(FUNCOES_ALVO)}
```

## Resumo decisório

{tabela_comparacoes()}

## Interpretação técnica

### `_projetar_valor_terminal`

A duplicidade deve ser tratada como potencialmente semântica. Uma implementação pertence ao planejamento de switching temporal e outra à simulação central de eventos. Mesmo que as fórmulas pareçam próximas, as assinaturas e convenções de entrada podem refletir contextos diferentes.

Decisão recomendada: **manter separadas nesta etapa**. Abrir consolidação somente se uma microetapa econômica futura definir um contrato único de projeção terminal.

### `_patrimonio_terminal_proxy`

A duplicidade deve ser tratada como semanticamente distinta até prova em contrário. Uma versão trabalha com candidatos ajustados/movimento simulado/mapa de lotes/tabelas fiscais; outra trabalha com estado/métrica/ganho de switching. São estruturas de entrada diferentes e provavelmente proxies em níveis distintos do motor.

Decisão recomendada: **manter separadas nesta etapa**. Não criar fonte única agora.

## Detalhamento por função

{texto_funcoes}

## Arquivos gerados

```text
relatorios/atuais/codex_ready/AUDITORIA_DUPLICIDADES_ECONOMICAS_V225.md
relatorios/atuais/codex_ready/auditoria_duplicidades_economicas_definicoes_v225.csv
relatorios/atuais/codex_ready/auditoria_duplicidades_economicas_chamadas_v225.csv
relatorios/atuais/codex_ready/auditoria_duplicidades_economicas_comparacao_v225.csv
```

## Decisão final

As duplicidades econômicas **não devem ser removidas como limpeza técnica**.

Elas devem permanecer separadas até que uma frente econômica futura defina:

1. contrato matemático único de projeção terminal;
2. entradas e saídas canônicas;
3. convenções de retorno, horizonte, impostos, liquidez e switching;
4. testes de equivalência econômica;
5. validação com `python aplicacao/principal.py`.

## Validação operacional recomendada

```bash
python aplicacao/principal.py
```
"""


def main() -> None:
    if not ARQ_PRINCIPAL.exists():
        fail("Entrada oficial não encontrada: aplicacao/principal.py")

    arquivos = listar_py()
    if not arquivos:
        fail("Nenhum arquivo .py encontrado em aplicacao/ ou nucleo/.")

    definicoes: list[dict] = []
    chamadas: list[dict] = []

    for path in arquivos:
        texto = ler(path)
        arvore = parse(path, texto)
        definicoes.extend(encontrar_funcoes(path, texto, arvore))
        chamadas.extend(coletar_chamadas(path, texto, arvore))

    defs_por_funcao = defaultdict(list)
    for d in definicoes:
        defs_por_funcao[d["funcao"]].append(d)

    comparacoes = comparar_definicoes(defs_por_funcao)

    DIR_RELATORIOS.mkdir(parents=True, exist_ok=True)

    escrever_csv(
        ARQ_DEFINICOES,
        definicoes,
        [
            "funcao",
            "arquivo",
            "modulo",
            "linha_inicio",
            "linha_fim",
            "assinatura",
            "hash_codigo",
            "hash_ast",
            "linhas_codigo",
            "nomes_referenciados",
            "chaves_get",
            "operadores",
            "constantes_numericas",
            "chamadas_internas",
            "corpo_resumo",
        ],
    )

    escrever_csv(
        ARQ_CHAMADAS,
        chamadas,
        [
            "funcao",
            "arquivo",
            "modulo",
            "escopo",
            "linha",
            "conteudo",
        ],
    )

    escrever_csv(
        ARQ_COMPARACAO,
        comparacoes,
        [
            "funcao",
            "qtd_definicoes",
            "arquivos",
            "qtd_hashes_ast",
            "hashes_ast",
            "qtd_assinaturas",
            "assinaturas",
            "status_semantico",
            "risco_consolidacao",
            "fonte_unica_recomendada",
            "decisao",
            "chaves_get_comuns",
            "chaves_get_uniao",
            "chamadas_internas_comuns",
            "chamadas_internas_uniao",
            "operadores_comuns",
            "operadores_uniao",
        ],
    )

    relatorio = criar_relatorio(definicoes, chamadas, comparacoes)
    ARQ_RELATORIO.write_text(relatorio, encoding="utf-8")

    print("AUDITORIA DE DUPLICIDADES ECONÔMICAS CONCLUÍDA")
    print("")
    for c in comparacoes:
        print(
            f"- {c['funcao']}: defs={c['qtd_definicoes']}, "
            f"assinaturas={c['qtd_assinaturas']}, "
            f"status={c['status_semantico']}, "
            f"risco={c['risco_consolidacao']}"
        )
    print("")
    print("Decisão: manter separadas nesta etapa; não consolidar como limpeza técnica.")
    print("")
    print(f"Relatório: {ARQ_RELATORIO}")
    print(f"CSV definições: {ARQ_DEFINICOES}")
    print(f"CSV chamadas: {ARQ_CHAMADAS}")
    print(f"CSV comparação: {ARQ_COMPARACAO}")
    print("")
    print("Validação operacional recomendada:")
    print("python aplicacao/principal.py")


if __name__ == "__main__":
    main()
