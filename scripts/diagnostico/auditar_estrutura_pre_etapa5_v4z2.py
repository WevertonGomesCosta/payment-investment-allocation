from __future__ import annotations

import argparse
import ast
import csv
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


MICROETAPA = "V17-F0-V.4Z2"
ESCOPO = (
    "aplicacao/principal.py, aplicacao/console/*.py, nucleo/*.py; "
    "diagnostico estrutural sem alterar motor/replay/ledger/ranking/XLSX/ContextoBaseline"
)

TERMOS_RESIDUO = (
    "shadow",
    "benchmark",
    "experimental",
    "legado",
    "legacy",
    "fallback",
    "diagnostico",
    "auditoria",
    "sentinela",
)
SENTINELAS = ("Lote 3120 mai", "3120", "8500", "6630")
IO_TERMS = (
    "open(",
    ".read_text(",
    ".write_text(",
    ".read_bytes(",
    ".write_bytes(",
    "read_csv(",
    "to_csv(",
    "read_excel(",
    "ExcelFile(",
    "Workbook(",
    ".save(",
    "requests.get(",
)
VERSION_RE = re.compile(
    r"(^|_)(v\d+[a-z]?\d*|v17|v37|s\d+[a-z]?|u\d+|q\d+|o\d+|c\d+|f0)(_|\.|$)",
    re.IGNORECASE,
)
PROJECT_PREFIXES = ("nucleo", "aplicacao", "scripts")


@dataclass
class FuncaoInventario:
    etapa_inferida: str
    arquivo: str
    qualname: str
    nome: str
    tipo: str
    assinatura: str
    entradas_parametros: list[str]
    saida_anotada: str
    retorna_valor: bool
    funcionalidade: str
    imports_projeto_arquivo: list[str]
    chamadas_projeto_inferidas: list[str]
    chamadas_todas_resumo: list[str]
    consumidores_arquivo: list[str] = field(default_factory=list)
    consumidores_funcao: list[str] = field(default_factory=list)
    residuos: list[str] = field(default_factory=list)
    decisao_preliminar: str = "pendente"


@dataclass
class ModuloInventario:
    etapa_inferida: str
    arquivo: str
    tipo_modulo: str
    imports_projeto: list[str]
    importado_por: list[str]
    funcoes_publicas: list[str]
    funcoes_internas: list[str]
    classes: list[str]
    metodos: list[str]
    tem_entrypoint: bool
    tem_io: bool
    sentinelas: list[str]
    termos_residuo: list[str]
    nome_versionado: bool
    chamadas_projeto_inferidas: list[str]
    decisao_preliminar: str
    justificativa_decisao: str


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _parse(path: Path) -> ast.Module:
    return ast.parse(_read(path))


def _ann(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Call):
        return _call_name(node.func)
    return ""


def _args_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, list[str]]:
    parts: list[str] = []
    params: list[str] = []

    pos_defaults = [None] * (len(node.args.args) - len(node.args.defaults)) + list(node.args.defaults)
    for arg, default in zip(node.args.args, pos_defaults):
        txt = arg.arg
        if arg.annotation is not None:
            txt += f": {_ann(arg.annotation)}"
        if default is not None:
            txt += f"={_ann(default)}"
        parts.append(txt)
        params.append(arg.arg)

    if node.args.vararg is not None:
        txt = f"*{node.args.vararg.arg}"
        if node.args.vararg.annotation is not None:
            txt += f": {_ann(node.args.vararg.annotation)}"
        parts.append(txt)
        params.append(node.args.vararg.arg)
    elif node.args.kwonlyargs:
        parts.append("*")

    for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        txt = arg.arg
        if arg.annotation is not None:
            txt += f": {_ann(arg.annotation)}"
        if default is not None:
            txt += f"={_ann(default)}"
        parts.append(txt)
        params.append(arg.arg)

    if node.args.kwarg is not None:
        txt = f"**{node.args.kwarg.arg}"
        if node.args.kwarg.annotation is not None:
            txt += f": {_ann(node.args.kwarg.annotation)}"
        parts.append(txt)
        params.append(node.args.kwarg.arg)

    ret = _ann(node.returns)
    signature = f"({', '.join(parts)})"
    if ret:
        signature += f" -> {ret}"
    return signature, params


def _project_imports(tree: ast.Module) -> tuple[list[str], dict[str, str]]:
    imports: list[str] = []
    alias_map: dict[str, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in PROJECT_PREFIXES:
                    imports.append(alias.name)
                    alias_map[alias.asname or alias.name.split(".")[-1]] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.split(".")[0] in PROJECT_PREFIXES:
                imports.append(module)
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    alias_map[alias.asname or alias.name] = f"{module}.{alias.name}"
    return sorted(set(imports)), alias_map


def _calls(node: ast.AST, alias_map: dict[str, str]) -> tuple[list[str], list[str]]:
    todas: list[str] = []
    projeto: list[str] = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            nome = _call_name(sub.func)
            if not nome:
                continue
            todas.append(nome)
            raiz = nome.split(".")[0]
            if raiz in alias_map:
                destino = alias_map[raiz]
                resto = ".".join(nome.split(".")[1:])
                projeto.append(f"{destino}.{resto}" if resto else destino)
            elif raiz in PROJECT_PREFIXES:
                projeto.append(nome)
    return sorted(set(projeto)), sorted(set(todas))[:80]


def _file_stage(path: Path) -> str:
    p = path.as_posix()
    nome = path.name.lower()
    if p == "aplicacao/principal.py":
        return "runtime_principal"
    if p.startswith("aplicacao/console/"):
        return "runtime_console"
    if p.startswith("nucleo/"):
        if "entrada_resolvida" in nome or "leitor_planilha" in nome:
            return "etapa_1_entrada"
        if "validacao_pre_execucao" in nome:
            return "etapa_2_validacao"
        if "dados_operacionais_canonicos" in nome or "carteira_canonica" in nome:
            return "etapa_3_canonizacao"
        if "saida" in nome or "planilha" in nome or "pacote_saida" in nome:
            return "etapa_4_saida"
        if "shadow" in nome:
            return "shadow_historico"
        if "benchmark" in nome or "experimental" in nome:
            return "experimental_historico"
        return "nucleo_operacional_ou_pendente"
    return "fora_escopo"


def _module_type(path: Path, text: str) -> str:
    name = path.name.lower()
    if path.as_posix() == "aplicacao/principal.py":
        return "entrypoint_runtime"
    if path.as_posix().startswith("aplicacao/console/"):
        return "renderizacao_console"
    if "shadow" in name:
        return "shadow"
    if "benchmark" in name:
        return "benchmark"
    if "experimental" in name:
        return "experimental"
    if VERSION_RE.search(name):
        return "versionado"
    if "auditoria" in name or "diagnostico" in name:
        return "auditoria_no_nucleo"
    if "saida" in name:
        return "saida"
    return "nucleo"


def _residues(path: Path, text: str) -> tuple[list[str], list[str], bool, bool, bool]:
    lower = text.lower()
    name = path.name.lower()
    terms = sorted({t for t in TERMOS_RESIDUO if t in lower or t in name})
    sent = sorted({s for s in SENTINELAS if s in text})
    versioned = bool(VERSION_RE.search(path.name))
    entrypoint = "if __name__ == \"__main__\"" in text or "if __name__ == '__main__'" in text
    io = any(t in text for t in IO_TERMS)
    return terms, sent, versioned, entrypoint, io


def _decision(path: Path, module_type: str, terms: list[str], sent: list[str], versioned: bool, imported_by: list[str]) -> tuple[str, str]:
    if path.as_posix() == "aplicacao/principal.py":
        return "auditar_runtime_antes_etapa5", "entrypoint principal ainda define a rota executavel"
    if module_type in {"shadow", "benchmark", "experimental"}:
        if imported_by:
            return "isolar_bloqueante_se_consumido", "modulo residual possui consumidores"
        return "isolar_historico", "modulo residual sem consumidor direto detectado"
    if module_type == "versionado":
        if imported_by:
            return "canonizar_ou_substituir", "modulo versionado e consumido"
        return "arquivar_ou_renomear", "modulo versionado sem consumidor direto detectado"
    if sent:
        return "remover_sentinelas_ou_rebaixar_regressao", "sentinelas encontradas no arquivo"
    if "diagnostico" in terms or "auditoria" in terms:
        return "separar_diagnostico_do_contrato", "termo diagnostico/auditoria dentro da rota analisada"
    return "manter_ou_validar", "sem residuo estrutural forte detectado"


def _target_files(root: Path) -> list[Path]:
    files = [root / "aplicacao" / "principal.py"]
    files.extend(sorted((root / "aplicacao" / "console").glob("*.py")))
    files.extend(sorted((root / "nucleo").glob("*.py")))
    return [p for p in files if p.exists()]


def _module_name(root: Path, path: Path) -> str:
    rel = path.relative_to(root).with_suffix("").as_posix()
    return rel.replace("/", ".")


def _build_consumers(root: Path, files: list[Path]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    module_consumers: dict[str, set[str]] = {}
    function_consumers: dict[str, set[str]] = {}
    module_by_file = {_module_name(root, p): p.relative_to(root).as_posix() for p in files}

    for path in files:
        rel = path.relative_to(root).as_posix()
        try:
            tree = _parse(path)
        except SyntaxError:
            continue
        imports, alias_map = _project_imports(tree)
        for imp in imports:
            for mod in module_by_file:
                if imp == mod or imp.startswith(mod + "."):
                    module_consumers.setdefault(mod, set()).add(rel)
        projeto, _ = _calls(tree, alias_map)
        for call in projeto:
            function_consumers.setdefault(call, set()).add(rel)

    return (
        {k: sorted(v) for k, v in module_consumers.items()},
        {k: sorted(v) for k, v in function_consumers.items()},
    )


def _function_records(root: Path, path: Path, module_consumers: dict[str, list[str]], function_consumers: dict[str, list[str]]) -> list[FuncaoInventario]:
    text = _read(path)
    tree = ast.parse(text)
    imports, alias_map = _project_imports(tree)
    rel = path.relative_to(root).as_posix()
    mod_name = _module_name(root, path)
    records: list[FuncaoInventario] = []

    def add_record(node: ast.FunctionDef | ast.AsyncFunctionDef, qualname: str, tipo: str) -> None:
        sig, params = _args_signature(node)
        doc = ast.get_docstring(node) or ""
        proj_calls, all_calls = _calls(node, alias_map)
        retorna_valor = any(
            isinstance(sub, ast.Return) and sub.value is not None
            for sub in ast.walk(node)
        )
        local_text = ast.get_source_segment(text, node) or ""
        terms, sent, versioned, _entry, io = _residues(path, local_text)
        residuos = sorted(set(terms + sent + (["nome_versionado"] if versioned else []) + (["io"] if io else [])))
        consumidores_funcao = []
        for call_name, consumers in function_consumers.items():
            if call_name.endswith("." + node.name) or call_name == node.name:
                consumidores_funcao.extend(consumers)
        decisao = "manter_ou_validar"
        if residuos:
            decisao = "auditar_residuo_funcional"
        if tipo == "main":
            decisao = "validar_runtime_local"
        records.append(
            FuncaoInventario(
                etapa_inferida=_file_stage(path.relative_to(root)),
                arquivo=rel,
                qualname=qualname,
                nome=node.name,
                tipo=tipo,
                assinatura=sig,
                entradas_parametros=params,
                saida_anotada=_ann(node.returns),
                retorna_valor=retorna_valor,
                funcionalidade=doc.strip().replace("\n", " | ")[:500] if doc else "sem_docstring_explicitada",
                imports_projeto_arquivo=imports,
                chamadas_projeto_inferidas=proj_calls,
                chamadas_todas_resumo=all_calls,
                consumidores_arquivo=module_consumers.get(mod_name, []),
                consumidores_funcao=sorted(set(consumidores_funcao)),
                residuos=residuos,
                decisao_preliminar=decisao,
            )
        )

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add_record(node, node.name, "main" if node.name == "main" else ("interna" if node.name.startswith("_") else "publica"))
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    add_record(item, f"{node.name}.{item.name}", "metodo")
    return records


def auditar(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files = _target_files(root)
    module_consumers, function_consumers = _build_consumers(root, files)

    modules: list[ModuloInventario] = []
    functions: list[FuncaoInventario] = []

    for path in files:
        rel = path.relative_to(root).as_posix()
        text = _read(path)
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            modules.append(
                ModuloInventario(
                    etapa_inferida=_file_stage(path.relative_to(root)),
                    arquivo=rel,
                    tipo_modulo="erro_parse_ast",
                    imports_projeto=[],
                    importado_por=[],
                    funcoes_publicas=[],
                    funcoes_internas=[],
                    classes=[],
                    metodos=[],
                    tem_entrypoint=False,
                    tem_io=False,
                    sentinelas=[],
                    termos_residuo=[str(exc)],
                    nome_versionado=False,
                    chamadas_projeto_inferidas=[],
                    decisao_preliminar="corrigir_parse",
                    justificativa_decisao="arquivo nao parseavel por AST",
                )
            )
            continue

        imports, alias_map = _project_imports(tree)
        proj_calls, _all_calls = _calls(tree, alias_map)
        terms, sent, versioned, entrypoint, io = _residues(path, text)
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        all_funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        public = sorted({n.name for n in all_funcs if not n.name.startswith("_")})
        internal = sorted({n.name for n in all_funcs if n.name.startswith("_")})
        methods = []
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for item in cls.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(f"{cls.name}.{item.name}")
        mod_name = _module_name(root, path)
        module_type = _module_type(path.relative_to(root), text)
        decision, justification = _decision(path.relative_to(root), module_type, terms, sent, versioned, module_consumers.get(mod_name, []))
        modules.append(
            ModuloInventario(
                etapa_inferida=_file_stage(path.relative_to(root)),
                arquivo=rel,
                tipo_modulo=module_type,
                imports_projeto=imports,
                importado_por=module_consumers.get(mod_name, []),
                funcoes_publicas=public,
                funcoes_internas=internal,
                classes=sorted(classes),
                metodos=sorted(methods),
                tem_entrypoint=entrypoint,
                tem_io=io,
                sentinelas=sent,
                termos_residuo=terms,
                nome_versionado=versioned,
                chamadas_projeto_inferidas=proj_calls,
                decisao_preliminar=decision,
                justificativa_decisao=justification,
            )
        )
        functions.extend(_function_records(root, path, module_consumers, function_consumers))

    residuos_modulos = [asdict(m) for m in modules if m.sentinelas or m.termos_residuo or m.nome_versionado or m.tem_io or m.tipo_modulo in {"shadow", "benchmark", "experimental", "versionado"}]
    runtime_principal = [asdict(m) for m in modules if m.arquivo == "aplicacao/principal.py"]
    main_ok_local_precisa_ser_anexado = True

    return {
        "microetapa": MICROETAPA,
        "escopo": ESCOPO,
        "qtd_arquivos": len(files),
        "qtd_modulos": len(modules),
        "qtd_funcoes": len(functions),
        "runtime_principal": runtime_principal,
        "resumo": {
            "modulos_com_residuos": len(residuos_modulos),
            "funcoes_com_residuos": sum(1 for f in functions if f.residuos),
            "sentinelas_em_modulos": sorted({m.arquivo for m in modules if m.sentinelas}),
            "modulos_versionados": sorted({m.arquivo for m in modules if m.nome_versionado}),
            "modulos_shadow_ou_experimentais": sorted({m.arquivo for m in modules if m.tipo_modulo in {"shadow", "benchmark", "experimental"}}),
        },
        "gate_pre_etapa5": {
            "principal_py_deve_ser_executado_localmente": main_ok_local_precisa_ser_anexado,
            "nao_iniciar_etapa5_se_houver_residuos_na_rota_runtime": True,
            "este_auditor_nao_altera_runtime": True,
        },
        "modulos": [asdict(m) for m in modules],
        "funcoes": [asdict(f) for f in functions],
        "residuos_modulos": residuos_modulos,
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({k for row in rows for k in row})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            converted = {}
            for k in fields:
                v = row.get(k)
                if isinstance(v, (list, dict)):
                    converted[k] = json.dumps(v, ensure_ascii=False, sort_keys=True)
                else:
                    converted[k] = v
            writer.writerow(converted)


def _write_md(path: Path, payload: dict[str, Any]) -> None:
    linhas = [
        "# V17-F0-V.4Z2 — Auditoria estrutural pré-Etapa 5",
        "",
        f"- arquivos auditados: `{payload['qtd_arquivos']}`",
        f"- módulos inventariados: `{payload['qtd_modulos']}`",
        f"- funções inventariadas: `{payload['qtd_funcoes']}`",
        "",
        "## Resumo",
        "",
        "```json",
        json.dumps(payload["resumo"], ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
        "## Runtime principal",
        "",
        "```json",
        json.dumps(payload["runtime_principal"], ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
        "## Gate pré-Etapa 5",
        "",
        "```json",
        json.dumps(payload["gate_pre_etapa5"], ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
        "## Módulos com resíduos",
        "",
    ]
    for item in payload["residuos_modulos"]:
        linhas.append(f"- `{item['arquivo']}` — decisão: `{item['decisao_preliminar']}`; resíduos: `{item['termos_residuo'] + item['sentinelas']}`")
    path.write_text("\n".join(linhas), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="V17-F0-V.4Z2 — inventário estrutural pré-Etapa 5.")
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--sem-arquivos", action="store_true")
    args = parser.parse_args()

    payload = auditar(args.raiz)
    print("=== AUDITORIA ESTRUTURAL PRE-ETAPA5 V4Z2 ===")
    print("microetapa=", payload["microetapa"])
    print("qtd_arquivos=", payload["qtd_arquivos"])
    print("qtd_funcoes=", payload["qtd_funcoes"])
    print("resumo=", json.dumps(payload["resumo"], ensure_ascii=False, sort_keys=True))
    print("runtime_principal=", json.dumps(payload["runtime_principal"], ensure_ascii=False, sort_keys=True))
    print("gate_pre_etapa5=", json.dumps(payload["gate_pre_etapa5"], ensure_ascii=False, sort_keys=True))

    if not args.sem_arquivos:
        out = args.raiz / "relatorios" / "atuais" / "auditoria_pre_etapa5_v4z2"
        out.mkdir(parents=True, exist_ok=True)
        _write_json(out / "inventario_estrutura_pre_etapa5_v4z2.json", payload)
        _write_csv(out / "inventario_modulos_pre_etapa5_v4z2.csv", payload["modulos"])
        _write_csv(out / "inventario_funcoes_pre_etapa5_v4z2.csv", payload["funcoes"])
        _write_csv(out / "residuos_modulos_pre_etapa5_v4z2.csv", payload["residuos_modulos"])
        _write_md(out / "resumo_auditoria_pre_etapa5_v4z2.md", payload)
        print("saida_dir=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
