from __future__ import annotations

import argparse
import ast
import csv
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


VERSAO_MICROETAPA = "V17-F0-V.4Z1"
ESCOPO = "nucleo/*.py + ContextoOperacionalCanonico"

SENTINELAS = ("Lote 3120 mai", "3120", "8500", "6630")
FORBIDDEN_CONTEXT_TERMS = ("shadow", "benchmark", "experimental", "sentinela", "3120", "8500", "6630")

IO_TERMS = (
    "open(", ".read_text(", ".write_text(", ".read_bytes(", ".write_bytes(",
    "read_csv(", "to_csv(", "read_excel(", "ExcelFile(", "Workbook(", ".save(",
    "requests.get(",
)
IO_AUTORIZADO = {
    "ambiente.py", "carregador_config.py", "leitor_planilha.py",
    "cache_cdi_bcb.py", "gerar_planilha_operacional.py", "identidade_baseline.py",
}

CLASS_CANONICO = {
    "__init__.py",
    "ambiente.py",
    "carregador_config.py",
    "config_utils.py",
    "leitor_planilha.py",
    "entrada_resolvida.py",
    "validacao_pre_execucao.py",
    "carteira_canonica.py",
    "dados_operacionais_canonicos.py",
    "calendario_financeiro.py",
    "fiscal_lotes.py",
    "nucleo_financeiro_minimo.py",
    "replay_passado_controlado.py",
    "caixa_recebidos_auditaveis.py",
    "ranking_carteira_estabilizado.py",
    "ledger_temporal_conjunto.py",
    "rotulagem_fechamento.py",
    "identidade_baseline.py",
    "utilitarios_neutros.py",
    "saida_canonica.py",
    "inventario_lotes_expandido_pos_switching.py",
    "contexto_baseline.py",
}
CLASS_AUXILIAR = {
    "avaliador_cenarios_conjuntos_v1.py",
    "comparador_hibrido_switching_v1.py",
    "triagem_motor.py",
    "pacote_orquestrado_pre_saida.py",
    "pacote_ledger_temporal_operacional.py",
    "pacote_replay_passado.py",
    "pacote_estado_temporal.py",
    "pacote_auditoria_temporal.py",
    "pacote_ledger_temporal.py",
}
CLASS_PENDENTE = {
    "cache_cdi_bcb.py",
    "saida_observavel.py",
    "pacote_saida_observavel_temporal.py",
    "gerar_planilha_operacional.py",
    "ledger_temporal_switching_canonico_v37r.py",
    "aportes_futuros_planejados.py",
    "motor_recomendacao_pagamentos_switching_v1.py",
    "matriz_pacotes_diarios.py",
    "matriz_elegibilidade_fontes_s7b.py",
    "pacotes_temporais_agregados_saida.py",
    "auditoria_temporal_decisao_local.py",
    "heuristica_conjunta_parcial_bloco_critico.py",
    "microplanejamento_conjunto_bloco_critico_v2.py",
    "planejador_switching_temporal_v1.py",
    "planejamento_conjunto_local_bloco_critico_v1.py",
    "recomputacao_sequencial_central_v1.py",
    "reescolha_dinamica_pos_quebra.py",
    "simulador_central_eventos_v1.py",
}
CLASS_HISTORICO = {
    "construir_saida_canonica_v17_c7.py",
    "saida_canonica_switching_v17_c7.py",
    "saida_canonica_controlada_v4l.py",
    "saida_canonica_temporal_shadow_v4k.py",
    "fluxo_pagamentos_terminal_v138.py",
    "fluxo_pagamentos_terminal_recorte_amplo_v142.py",
    "motor_diario_conjunto_experimental_v143.py",
    "runner_validacao_diaria_operacional_v175.py",
    "runner_validacao_diaria_operacional_v176.py",
    "runner_validacao_diaria_operacional_v177.py",
    "ledger_switching_estado_temporal_v17_f0_o2.py",
}
VERSION_RE = re.compile(
    r"(^|_)(v\d+[a-z]?\d*|v17|v37|s\d+[a-z]?|u\d+|q\d+|o\d+|c\d+|f0)(_|\.|$)",
    re.IGNORECASE,
)


@dataclass
class ModuloNucleo:
    arquivo: str
    classificacao: str
    subclasse: str
    risco_etapa5: str
    recomendacao: str
    importado_por: list[str] = field(default_factory=list)
    imports_nucleo: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    funcoes_publicas: list[str] = field(default_factory=list)
    tem_io: bool = False
    io_autorizado: bool = False
    sentinelas: list[str] = field(default_factory=list)
    tem_shadow_nome: bool = False
    tem_shadow_texto: bool = False
    tem_benchmark_nome: bool = False
    tem_experimental_nome: bool = False
    tem_versao_nome: bool = False
    tem_entrypoint: bool = False


def _modulo_local_de_import(module: str) -> str | None:
    if not module.startswith("nucleo."):
        return None
    partes = module.split(".")
    if len(partes) < 2:
        return None
    return f"{partes[1]}.py"


def _classificar(nome: str, texto: str) -> tuple[str, str]:
    nome_lower = nome.lower()
    texto_lower = texto.lower()

    if "shadow" in nome_lower:
        return "shadow", "shadow_explicito"
    if "benchmark" in nome_lower:
        return "experimental", "benchmark_ou_comparativo"
    if "experimental" in nome_lower:
        return "experimental", "experimental_explicito"
    if nome in CLASS_HISTORICO:
        return "historico", "historico_versionado"
    if nome in CLASS_CANONICO:
        return "canonico", "contrato_vivo"
    if nome in CLASS_AUXILIAR:
        return "auxiliar", "auxiliar_transicional"
    if nome in CLASS_PENDENTE:
        return "pendente", "exige_decisao"
    if VERSION_RE.search(nome):
        return "pendente", "versionado_nao_mapeado"
    if any(t in texto_lower for t in ("shadow", "benchmark", "experimental")):
        return "pendente", "termo_residual_no_texto"
    return "pendente", "nao_mapeado"


def _risco(classificacao: str, importado_por: list[str], tem_io: bool, io_autorizado: bool, sentinelas: list[str]) -> str:
    if classificacao in {"shadow", "experimental", "historico"}:
        return "alto" if importado_por else "medio"
    if tem_io and not io_autorizado:
        return "alto"
    if classificacao == "pendente":
        return "medio"
    if sentinelas:
        return "medio"
    return "baixo"


def _recomendacao(classificacao: str) -> str:
    if classificacao == "canonico":
        return "manter no contrato vivo"
    if classificacao == "auxiliar":
        return "manter se houver consumidor canonico"
    if classificacao == "shadow":
        return "isolar fora do contexto operacional canonico"
    if classificacao == "experimental":
        return "isolar como experimental ou benchmark"
    if classificacao == "historico":
        return "arquivar ou manter fora da Etapa 5"
    return "decidir entre canonizar, isolar ou arquivar antes da Etapa 5"


def _analisar_modulo(path: Path, raiz: Path) -> tuple[ModuloNucleo, list[str]]:
    texto = path.read_text(encoding="utf-8", errors="replace")
    nome = path.name
    try:
        tree = ast.parse(texto)
    except SyntaxError:
        return ModuloNucleo(
            arquivo=path.relative_to(raiz).as_posix(),
            classificacao="pendente",
            subclasse="erro_parse_ast",
            risco_etapa5="alto",
            recomendacao="corrigir parse antes de qualquer promocao",
        ), []

    classes: list[str] = []
    funcoes_publicas: list[str] = []
    imports_nucleo: list[str] = []
    imports_locais: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                funcoes_publicas.append(node.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "nucleo" or module.startswith("nucleo."):
                imports_nucleo.append(module)
                local = _modulo_local_de_import(module)
                if local:
                    imports_locais.append(local)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                if module == "nucleo" or module.startswith("nucleo."):
                    imports_nucleo.append(module)
                    local = _modulo_local_de_import(module)
                    if local:
                        imports_locais.append(local)

    classificacao, subclasse = _classificar(nome, texto)
    sentinelas = sorted({s for s in SENTINELAS if s in texto})
    tem_io = any(t in texto for t in IO_TERMS)
    io_autorizado = nome in IO_AUTORIZADO
    mod = ModuloNucleo(
        arquivo=path.relative_to(raiz).as_posix(),
        classificacao=classificacao,
        subclasse=subclasse,
        risco_etapa5="baixo",
        recomendacao="",
        imports_nucleo=sorted(set(imports_nucleo)),
        classes=sorted(classes),
        funcoes_publicas=sorted(funcoes_publicas),
        tem_io=tem_io,
        io_autorizado=io_autorizado,
        sentinelas=sentinelas,
        tem_shadow_nome="shadow" in nome.lower(),
        tem_shadow_texto="shadow" in texto.lower(),
        tem_benchmark_nome="benchmark" in nome.lower(),
        tem_experimental_nome="experimental" in nome.lower(),
        tem_versao_nome=bool(VERSION_RE.search(nome)),
        tem_entrypoint=("if __name__ == \"__main__\"" in texto or "if __name__ == '__main__'" in texto),
    )
    return mod, sorted(set(imports_locais))


def _auditar_contexto_operacional_canonico(path: Path) -> dict[str, Any]:
    texto = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(texto)

    campos: list[str] = []
    funcao_presente = False
    chamadas_proibidas: list[str] = []
    chamadas_versionadas: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ContextoOperacionalCanonico":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    campos.append(item.target.id)

        if isinstance(node, ast.FunctionDef) and node.name == "carregar_contexto_operacional_canonico":
            funcao_presente = True
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    nome = ""
                    if isinstance(sub.func, ast.Name):
                        nome = sub.func.id
                    elif isinstance(sub.func, ast.Attribute):
                        nome = sub.func.attr
                    nome_lower = nome.lower()
                    if any(t in nome_lower for t in ("shadow", "benchmark", "experimental")):
                        chamadas_proibidas.append(nome)
                    if VERSION_RE.search(nome):
                        chamadas_versionadas.append(nome)

    campos_proibidos = [
        campo for campo in campos
        if any(t in campo.lower() for t in FORBIDDEN_CONTEXT_TERMS) or VERSION_RE.search(campo)
    ]

    return {
        "classe_contexto_operacional_canonico_presente": bool(campos),
        "funcao_carregar_contexto_operacional_canonico_presente": funcao_presente,
        "campos_contexto_operacional_canonico": sorted(campos),
        "campos_proibidos_contexto_operacional_canonico": sorted(campos_proibidos),
        "chamadas_proibidas_contexto_operacional_canonico": sorted(set(chamadas_proibidas)),
        "chamadas_versionadas_contexto_operacional_canonico": sorted(set(chamadas_versionadas)),
        "contexto_operacional_canonico_limpo": bool(campos)
        and funcao_presente
        and not campos_proibidos
        and not chamadas_proibidas
        and not chamadas_versionadas,
    }


def auditar(raiz: Path) -> dict[str, Any]:
    nucleo = raiz / "nucleo"
    arquivos = sorted(nucleo.glob("*.py"))

    modulos: dict[str, ModuloNucleo] = {}
    imports_por_origem: dict[str, list[str]] = {}

    for path in arquivos:
        mod, imports_locais = _analisar_modulo(path, raiz)
        modulos[path.name] = mod
        imports_por_origem[path.name] = imports_locais

    for origem, destinos in imports_por_origem.items():
        for destino in destinos:
            if destino in modulos:
                modulos[destino].importado_por.append(f"nucleo/{origem}")

    for mod in modulos.values():
        mod.importado_por = sorted(set(mod.importado_por))
        mod.risco_etapa5 = _risco(mod.classificacao, mod.importado_por, mod.tem_io, mod.io_autorizado, mod.sentinelas)
        mod.recomendacao = _recomendacao(mod.classificacao)

    itens = sorted((asdict(m) for m in modulos.values()), key=lambda x: x["arquivo"])
    contexto = _auditar_contexto_operacional_canonico(nucleo / "contexto_baseline.py")

    resumo_classificacao: dict[str, int] = {}
    resumo_risco: dict[str, int] = {}
    for item in itens:
        resumo_classificacao[item["classificacao"]] = resumo_classificacao.get(item["classificacao"], 0) + 1
        resumo_risco[item["risco_etapa5"]] = resumo_risco.get(item["risco_etapa5"], 0) + 1

    listas_decisao = {
        "canonizar": [i["arquivo"] for i in itens if i["classificacao"] == "canonico"],
        "auxiliar": [i["arquivo"] for i in itens if i["classificacao"] == "auxiliar"],
        "isolar": [i["arquivo"] for i in itens if i["classificacao"] in {"shadow", "experimental"}],
        "arquivar": [i["arquivo"] for i in itens if i["classificacao"] == "historico"],
        "pendente": [i["arquivo"] for i in itens if i["classificacao"] == "pendente"],
    }

    bloqueios = {
        "contexto_operacional_canonico_limpo": contexto["contexto_operacional_canonico_limpo"],
        "campos_proibidos_contexto_operacional_canonico": contexto["campos_proibidos_contexto_operacional_canonico"],
        "chamadas_proibidas_contexto_operacional_canonico": contexto["chamadas_proibidas_contexto_operacional_canonico"],
        "chamadas_versionadas_contexto_operacional_canonico": contexto["chamadas_versionadas_contexto_operacional_canonico"],
        "io_incompativel": [i["arquivo"] for i in itens if i["tem_io"] and not i["io_autorizado"]],
        "sentinelas_no_nucleo": {i["arquivo"]: i["sentinelas"] for i in itens if i["sentinelas"]},
    }

    entrada_limpa_etapa5_ok = bool(contexto["contexto_operacional_canonico_limpo"])

    return {
        "microetapa": VERSAO_MICROETAPA,
        "escopo": ESCOPO,
        "qtd_modulos": len(itens),
        "resumo_classificacao": dict(sorted(resumo_classificacao.items())),
        "resumo_risco_etapa5": dict(sorted(resumo_risco.items())),
        "entrada_limpa_etapa5_ok": entrada_limpa_etapa5_ok,
        "contexto_operacional_canonico": contexto,
        "bloqueios_etapa5": bloqueios,
        "listas_decisao": listas_decisao,
        "itens": itens,
    }


def _salvar_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _salvar_csv(path: Path, itens: list[dict[str, Any]]) -> None:
    campos = [
        "arquivo", "classificacao", "subclasse", "risco_etapa5", "recomendacao",
        "importado_por", "imports_nucleo", "classes", "funcoes_publicas",
        "tem_io", "io_autorizado", "sentinelas", "tem_shadow_nome",
        "tem_shadow_texto", "tem_benchmark_nome", "tem_experimental_nome",
        "tem_versao_nome", "tem_entrypoint",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for item in itens:
            row = {campo: item.get(campo) for campo in campos}
            for campo, valor in list(row.items()):
                if isinstance(valor, (list, dict)):
                    row[campo] = json.dumps(valor, ensure_ascii=False, sort_keys=True)
            writer.writerow(row)


def _salvar_md(path: Path, payload: dict[str, Any]) -> None:
    linhas = [
        "# V17-F0-V.4Z1 — Auditoria do contexto operacional canônico",
        "",
        f"- entrada_limpa_etapa5_ok: `{payload['entrada_limpa_etapa5_ok']}`",
        f"- módulos auditados: `{payload['qtd_modulos']}`",
        f"- classificação: `{payload['resumo_classificacao']}`",
        "",
        "## Contexto operacional canônico",
        "",
        "```json",
        json.dumps(payload["contexto_operacional_canonico"], ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
        "## Bloqueios da Etapa 5",
        "",
        "```json",
        json.dumps(payload["bloqueios_etapa5"], ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
        "## Listas de decisão",
        "",
        "```json",
        json.dumps(payload["listas_decisao"], ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
    ]
    path.write_text("\n".join(linhas), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Auditoria V4Z1 do núcleo vivo e do ContextoOperacionalCanonico.")
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--sem-arquivos", action="store_true")
    parser.add_argument("--falhar-se-bloqueante", action="store_true")
    args = parser.parse_args()

    raiz = args.raiz.resolve()
    payload = auditar(raiz)

    print("=== AUDITORIA NUCLEO VIVO V4Z1 ===")
    print("microetapa=", payload["microetapa"])
    print("escopo=", payload["escopo"])
    print("qtd_modulos=", payload["qtd_modulos"])
    print("entrada_limpa_etapa5_ok=", payload["entrada_limpa_etapa5_ok"])
    print("resumo_classificacao=", json.dumps(payload["resumo_classificacao"], ensure_ascii=False, sort_keys=True))
    print("resumo_risco_etapa5=", json.dumps(payload["resumo_risco_etapa5"], ensure_ascii=False, sort_keys=True))
    print("contexto_operacional_canonico=", json.dumps(payload["contexto_operacional_canonico"], ensure_ascii=False, sort_keys=True))
    print("bloqueios_etapa5=", json.dumps(payload["bloqueios_etapa5"], ensure_ascii=False, sort_keys=True))

    if not args.sem_arquivos:
        out_dir = raiz / "relatorios" / "atuais" / "auditoria_nucleo_vivo_v4z"
        out_dir.mkdir(parents=True, exist_ok=True)
        _salvar_json(out_dir / "inventario_nucleo_vivo_v4z1.json", payload)
        _salvar_csv(out_dir / "inventario_nucleo_vivo_v4z1.csv", payload["itens"])
        _salvar_md(out_dir / "classificacao_nucleo_vivo_v4z1.md", payload)
        print("saida_dir=", out_dir)

    if args.falhar_se_bloqueante and not payload["entrada_limpa_etapa5_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
