from __future__ import annotations

import ast
import csv
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "saidas" / "diagnostico" / "v17_e0"

SCOPES = [
    "aplicacao",
    "nucleo",
    "scripts/diagnostico",
    "scripts/operacional",
    "code",
    "relatorios/principais",
    "relatorios/atuais",
]

IGNORE_DIRS = {"__pycache__", ".git", ".pytest_cache", ".mypy_cache", ".venv", "venv"}

CAMADAS = {
    "entrada_configuracao",
    "validacao_pre_execucao",
    "dados_operacionais_canonicos",
    "ranking_universo_produtos",
    "estado_inicial_temporal",
    "motor_temporal_conjunto",
    "ledger_estado_decisoes",
    "validacao_estado_temporal",
    "construcao_saida_canonica",
    "validacao_saida_canonica",
    "renderizacao_console_planilha",
    "validacao_renderizacao",
    "artefatos_finais",
    "legado_experimental",
    "diagnostico_historico",
    "indefinida",
}

ACOES = {
    "manter",
    "manter_auditar",
    "refatorar_futuramente",
    "congelar_como_legado",
    "arquivar_futuramente",
    "auditar_dependencias",
    "consolidar_helper_futuramente",
    "bloquear_uso_operacional",
    "indefinido_requer_auditoria",
}


@dataclass
class Symbol:
    arquivo: str
    nome: str
    tipo: str
    linha: int
    camada: str
    termos: list[str]
    pode_decidir: bool
    pode_alterar_estado: bool
    pode_renderizar: bool
    pode_diagnosticar: bool


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_files() -> list[Path]:
    files: list[Path] = []
    for scope in SCOPES:
        p = ROOT / scope
        if not p.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(p):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            for fn in filenames:
                fp = Path(dirpath) / fn
                files.append(fp)
    return sorted(set(files))


def tokens(text: str) -> set[str]:
    raw = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    return set(raw.split())


def infer_camada(path: str, text_l: str) -> tuple[str, str, str]:
    keys = {
        "entrada_configuracao": ["config", "carregar_config", "leitor_planilha", "carregar_planilha", "ambiente", "bootstrap"],
        "dados_operacionais_canonicos": ["canonico", "canonica", "canonizacao", "normalizar", "resolver_coluna", "dados_operacionais"],
        "ranking_universo_produtos": ["ranking", "carteira", "score", "triagem", "produto", "destino"],
        "motor_temporal_conjunto": ["estado", "temporal", "motor", "pagamento", "switching", "resgate", "aporte", "saldo", "recomputacao", "reescolha", "alocador"],
        "ledger_estado_decisoes": ["ledger", "estado_final", "decisao", "trilha"],
        "construcao_saida_canonica": ["saida_canonica", "pacote_saida", "extrato", "fechamento", "situacao_atual"],
        "renderizacao_console_planilha": ["console", "planilha", "openpyxl", "workbook", "render", "imprimir", "aba"],
        "diagnostico_historico": ["auditar", "diagnostico", "validar", "verificar", "release", "csv", "matriz"],
        "legado_experimental": ["shadow", "benchmark", "experimental", "v138", "v142", "v143", "runner", "historico", "code/"],
        "validacao_renderizacao": ["validar_ponte_renderizacao", "comparar_pacote"],
        "validacao_pre_execucao": ["validar_canonizacao", "pre_execucao"],
        "validacao_estado_temporal": ["auditar_transicao_temporal", "invariantes", "matriz_pacotes"],
        "validacao_saida_canonica": ["auditar_saida_canonica", "fonte_verdade_saida"],
        "estado_inicial_temporal": ["contexto_baseline", "estado_inicial", "matriz_pacotes_diarios"],
        "artefatos_finais": ["relatorios/", "saidas/"],
    }
    if path.startswith("code/"):
        return "legado_experimental", "indefinida", "legacy path"
    if path.startswith("scripts/diagnostico/"):
        base = "diagnostico_historico"
    elif path.startswith("aplicacao/console/"):
        base = "renderizacao_console_planilha"
    elif path.startswith("relatorios/"):
        base = "artefatos_finais"
    else:
        base = "indefinida"

    scores = Counter()
    for camada, kws in keys.items():
        for kw in kws:
            if kw in path or kw in text_l:
                scores[camada] += 1
    top = scores.most_common(2)
    primary = top[0][0] if top else base
    secondary = top[1][0] if len(top) > 1 else "indefinida"
    if base != "indefinida" and primary == "indefinida":
        primary = base
    if primary not in CAMADAS:
        primary = "indefinida"
    if secondary not in CAMADAS:
        secondary = "indefinida"
    return primary, secondary, f"score={dict(top)}"


def risco_flags(path: str, text_l: str, camada: str, linhas: int):
    terms_decisao = ["decidir", "recomendar", "escolher", "pagar", "switching", "resgate", "aporte", "materializar", "migrar"]
    terms_render = ["console", "planilha", "openpyxl", "workbook", "render"]
    terms_diag = ["auditar", "diagnostico", "validar", "csv", "matriz"]

    in_render = camada == "renderizacao_console_planilha" or path.startswith("aplicacao/console") or "planilha" in path
    in_saida = "saida_canonica" in path or "ponte_renderizacao" in path
    in_diag = path.startswith("scripts/diagnostico/")

    has_decisao = any(t in text_l for t in terms_decisao)
    has_render = any(t in text_l for t in terms_render)

    risco_dec_fora = "alto" if (in_render or in_saida) and has_decisao else ("medio" if has_decisao and camada not in {"motor_temporal_conjunto", "ledger_estado_decisoes", "estado_inicial_temporal"} else "baixo")
    risco_render_sem = "alto" if in_render and has_decisao else ("medio" if in_render and "ordenar" in text_l else "baixo")
    risco_diag_regra = "alto" if in_diag and has_decisao and ("reconstru" in text_l or "corrigir" in text_l) else ("medio" if in_diag and has_decisao else "baixo")
    risco_mistura = "alto" if linhas > 1200 else ("medio" if linhas > 600 or (has_decisao and has_render) else "baixo")
    risco_legado = "alto" if path.startswith("code/") or any(x in path for x in ["shadow", "benchmark"]) else "baixo"
    return risco_mistura, risco_dec_fora, risco_render_sem, risco_diag_regra, risco_legado


def acao_recomendada(camada: str, risco_legado: str, risco_mistura: str, risco_dec: str, path: str):
    if path.startswith("code/"):
        return "congelar_como_legado"
    if risco_dec == "alto":
        return "bloquear_uso_operacional"
    if risco_mistura == "alto":
        return "refatorar_futuramente"
    if risco_legado == "alto":
        return "manter_auditar"
    if path.startswith("scripts/diagnostico/"):
        return "manter_auditar"
    return "manter"


def parse_python(path: Path, camada: str, text: str) -> tuple[list[Symbol], list[dict]]:
    symbols: list[Symbol] = []
    imports: list[dict] = []
    try:
        tree = ast.parse(text)
    except Exception:
        return symbols, imports

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = node.name
            tl = name.lower()
            termos = [t for t in ["decidir", "pagar", "switch", "render", "auditar", "validar", "ledger", "estado", "saldo"] if t in tl]
            pode_decidir = any(t in tl for t in ["decid", "recom", "pagar", "switch", "alocar"])
            pode_alterar = any(t in tl for t in ["atual", "material", "migr", "sacar", "resgat", "aporte", "saldo"])
            pode_render = any(t in tl for t in ["render", "imprimir", "planilha", "console"])
            pode_diag = any(t in tl for t in ["auditar", "diagnost", "valid", "verificar"])
            symbols.append(Symbol(rel(path), name, "classe" if isinstance(node, ast.ClassDef) else "funcao", getattr(node, "lineno", 0), camada, termos, pode_decidir, pode_alterar, pode_render, pode_diag))
        elif isinstance(node, ast.Import):
            for n in node.names:
                imports.append({"arquivo": rel(path), "importado": n.name, "tipo_import": "import"})
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for n in node.names:
                imports.append({"arquivo": rel(path), "importado": f"{mod}.{n.name}".strip("."), "tipo_import": "from"})
    return symbols, imports


def infer_layer_from_import(name: str) -> str:
    n = name.lower()
    if n.startswith("nucleo"):
        return "motor_temporal_conjunto"
    if n.startswith("aplicacao.console"):
        return "renderizacao_console_planilha"
    if "diagnost" in n or "auditar" in n or "validar" in n:
        return "diagnostico_historico"
    if "saida_canonica" in n:
        return "construcao_saida_canonica"
    if "ranking" in n or "carteira" in n:
        return "ranking_universo_produtos"
    return "indefinida"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = iter_files()

    rows_arquivos = []
    symbols: list[Symbol] = []
    imports_rows = []
    risco_rows = []

    for fp in files:
        path = rel(fp)
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""
        lines = text.count("\n") + 1 if text else 0
        size = fp.stat().st_size
        tl = text.lower()
        camada, camada2, justificativa_base = infer_camada(path, tl)
        risco_m, risco_d, risco_r, risco_diag, risco_leg = risco_flags(path, tl, camada, lines)
        tipo = "python" if fp.suffix == ".py" else ("markdown" if fp.suffix == ".md" else "outro")
        participa = "sim" if path.startswith("aplicacao/") or path.startswith("nucleo/") else "nao"
        acao = acao_recomendada(camada, risco_leg, risco_m, risco_d, path)
        if acao not in ACOES:
            acao = "indefinido_requer_auditoria"

        rows_arquivos.append({
            "arquivo": path,
            "extensao": fp.suffix,
            "linhas": lines,
            "tamanho_bytes": size,
            "camada_7e_inferida": camada,
            "camada_7e_secundaria": camada2,
            "tipo_arquivo": tipo,
            "participa_rota_principal_inferida": participa,
            "risco_mistura_responsabilidades": risco_m,
            "risco_decisao_fora_motor": risco_d,
            "risco_renderizacao_com_semantica": risco_r,
            "risco_diagnostico_com_regra_economica": risco_diag,
            "risco_codigo_legado": risco_leg,
            "acao_recomendada": acao,
            "justificativa": justificativa_base,
        })

        if risco_d == "alto":
            risco_rows.append({"arquivo": path, "linha": 1, "tipo_risco": "decisao_em_saida" if "saida" in path else "decisao_em_renderizacao", "trecho_resumido": "heuristica: termos decisorios fora do motor", "camada_esperada": "motor_temporal_conjunto", "camada_observada": camada, "severidade": "alta", "recomendacao": "bloquear_uso_operacional"})
        if "ponte_renderizacao" in path and "switch" in tl:
            risco_rows.append({"arquivo": path, "linha": 1, "tipo_risco": "switching_em_ponte_saida", "trecho_resumido": "ponte com termos de switching", "camada_esperada": "motor_temporal_conjunto", "camada_observada": camada, "severidade": "alta", "recomendacao": "auditar_dependencias"})
        if "saldo" in tl and ("saida" in path or "console" in path):
            risco_rows.append({"arquivo": path, "linha": 1, "tipo_risco": "recalculo_saldo_em_saida", "trecho_resumido": "termo saldo em camada de saida/render", "camada_esperada": "ledger_estado_decisoes", "camada_observada": camada, "severidade": "media", "recomendacao": "manter_auditar"})
        if "material" in tl and ("saida" in path or "console" in path):
            risco_rows.append({"arquivo": path, "linha": 1, "tipo_risco": "materializacao_em_saida", "trecho_resumido": "termo materializacao em camada nao-motor", "camada_esperada": "motor_temporal_conjunto", "camada_observada": camada, "severidade": "alta", "recomendacao": "auditar_dependencias"})
        if path.startswith("scripts/diagnostico/") and "planilha" in tl and "estado" in tl:
            risco_rows.append({"arquivo": path, "linha": 1, "tipo_risco": "diagnostico_reconstruindo_estado_por_planilha", "trecho_resumido": "diagnostico menciona planilha+estado", "camada_esperada": "validacao_estado_temporal", "camada_observada": camada, "severidade": "media", "recomendacao": "manter_auditar"})
        if any(x in path for x in ["v138", "v142", "v143"]):
            risco_rows.append({"arquivo": path, "linha": 1, "tipo_risco": "script_versionado_transitorio", "trecho_resumido": "arquivo com sufixo de versao transitoria", "camada_esperada": "indefinida", "camada_observada": camada, "severidade": "media", "recomendacao": "auditar_dependencias"})
        if any(x in path for x in ["shadow", "benchmark"]):
            risco_rows.append({"arquivo": path, "linha": 1, "tipo_risco": "shadow_ou_benchmark", "trecho_resumido": "arquivo shadow/benchmark", "camada_esperada": "legado_experimental", "camada_observada": camada, "severidade": "media", "recomendacao": "congelar_como_legado"})
        if path.startswith("code/"):
            risco_rows.append({"arquivo": path, "linha": 1, "tipo_risco": "legado_code", "trecho_resumido": "arquivo em code/", "camada_esperada": "legado_experimental", "camada_observada": camada, "severidade": "alta", "recomendacao": "congelar_como_legado"})
        if lines > 1200:
            risco_rows.append({"arquivo": path, "linha": 1, "tipo_risco": "arquivo_grande_multirresponsabilidade", "trecho_resumido": f"arquivo com {lines} linhas", "camada_esperada": camada, "camada_observada": camada, "severidade": "media", "recomendacao": "refatorar_futuramente"})

        if fp.suffix == ".py":
            s, imp = parse_python(fp, camada, text)
            symbols.extend(s)
            imports_rows.extend(imp)

    name_count = Counter(s.nome for s in symbols)
    helper_dup_names = {n for n, c in name_count.items() if c > 1}
    for n in helper_dup_names:
        for s in symbols:
            if s.nome == n:
                risco_rows.append({"arquivo": s.arquivo, "linha": s.linha, "tipo_risco": "helper_repetido", "trecho_resumido": f"nome duplicado: {n}", "camada_esperada": s.camada, "camada_observada": s.camada, "severidade": "baixa" if name_count[n] < 4 else "media", "recomendacao": "consolidar_helper_futuramente"})

    fc_rows = []
    for s in symbols:
        risco_dup = "alto" if name_count[s.nome] >= 4 else ("medio" if name_count[s.nome] > 1 else "baixo")
        risco_front = "alto" if (s.pode_decidir and (s.pode_renderizar or s.pode_diagnosticar)) else ("medio" if s.pode_decidir and s.camada not in {"motor_temporal_conjunto", "ledger_estado_decisoes"} else "baixo")
        acao = "manter_auditar" if risco_front != "baixo" else "manter"
        fc_rows.append({
            "arquivo": s.arquivo,
            "funcao_ou_classe": s.nome,
            "tipo": s.tipo,
            "linha_inicio": s.linha,
            "camada_7e_inferida": s.camada,
            "termos_detectados": "|".join(s.termos),
            "pode_decidir": "sim" if s.pode_decidir else "nao",
            "pode_alterar_estado": "sim" if s.pode_alterar_estado else "nao",
            "pode_renderizar": "sim" if s.pode_renderizar else "nao",
            "pode_diagnosticar": "sim" if s.pode_diagnosticar else "nao",
            "risco_duplicacao_nome": risco_dup,
            "risco_fronteira": risco_front,
            "acao_recomendada": acao,
        })

    for imp in imports_rows:
        origem = next((r["camada_7e_inferida"] for r in rows_arquivos if r["arquivo"] == imp["arquivo"]), "indefinida")
        destino = infer_layer_from_import(imp["importado"])
        invertida = "alto" if origem == "renderizacao_console_planilha" and destino in {"motor_temporal_conjunto", "ledger_estado_decisoes"} else ("medio" if origem == "diagnostico_historico" and destino == "renderizacao_console_planilha" else "baixo")
        imp["camada_origem_inferida"] = origem
        imp["camada_destino_inferida"] = destino
        imp["risco_dependencia_invertida"] = invertida
        imp["observacao"] = "heuristica"
        if invertida in {"alto", "medio"}:
            risco_rows.append({"arquivo": imp["arquivo"], "linha": 1, "tipo_risco": "dependencia_invertida", "trecho_resumido": f"import {imp['importado']}", "camada_esperada": origem, "camada_observada": destino, "severidade": "alta" if invertida == "alto" else "media", "recomendacao": "auditar_dependencias"})

    dup_rows = []
    for name, qtd in sorted(name_count.items(), key=lambda kv: (-kv[1], kv[0])):
        if qtd <= 1:
            continue
        occ = [s for s in symbols if s.nome == name]
        cams = sorted(set(s.camada for s in occ))
        risco = "alto" if qtd >= 5 else ("medio" if qtd >= 3 else "baixo")
        dup_rows.append({
            "nome_funcao_ou_classe": name,
            "quantidade_ocorrencias": qtd,
            "arquivos": "|".join(sorted(set(s.arquivo for s in occ))),
            "camadas": "|".join(cams),
            "risco": risco,
            "acao_recomendada": "consolidar_helper_futuramente" if risco != "baixo" else "manter_auditar",
        })

    # Matriz recomendacao
    matriz = []
    for rr in sorted(risco_rows, key=lambda x: {"alta": 0, "media": 1, "baixa": 2}.get(x["severidade"], 3))[:200]:
        matriz.append({
            "prioridade": "P0" if rr["severidade"] == "alta" else ("P1" if rr["severidade"] == "media" else "P2"),
            "alvo": rr["arquivo"],
            "tipo_alvo": "arquivo",
            "problema": rr["tipo_risco"],
            "evidencia": rr["trecho_resumido"],
            "camada_correta_7e": rr["camada_esperada"],
            "acao_recomendada": rr["recomendacao"],
            "pode_alterar_agora": "nao",
            "validacao_necessaria": "sim",
            "risco_se_nao_corrigir": rr["severidade"],
        })

    por_camada = Counter(r["camada_7e_inferida"] for r in rows_arquivos)
    risco_alto = sum(1 for r in rows_arquivos if "alto" in [r["risco_mistura_responsabilidades"], r["risco_decisao_fora_motor"], r["risco_renderizacao_com_semantica"], r["risco_diagnostico_com_regra_economica"], r["risco_codigo_legado"]])
    risco_medio = sum(1 for r in rows_arquivos if "medio" in [r["risco_mistura_responsabilidades"], r["risco_decisao_fora_motor"], r["risco_renderizacao_com_semantica"], r["risco_diagnostico_com_regra_economica"], r["risco_codigo_legado"]])
    resumo = [
        {"metrica": "arquivos_mapeados", "valor": len(rows_arquivos)},
        {"metrica": "arquivos_python_mapeados", "valor": sum(1 for r in rows_arquivos if r["extensao"] == ".py")},
        {"metrica": "funcoes_classes_mapeadas", "valor": len(fc_rows)},
        {"metrica": "arquivos_por_camada", "valor": ";".join(f"{k}:{v}" for k, v in sorted(por_camada.items()))},
        {"metrica": "arquivos_com_risco_alto", "valor": risco_alto},
        {"metrica": "arquivos_com_risco_medio", "valor": risco_medio},
        {"metrica": "duplicidades_funcoes_total", "valor": len(dup_rows)},
        {"metrica": "arquivos_legado_experimental", "valor": por_camada.get("legado_experimental", 0)},
        {"metrica": "arquivos_diagnostico_historico", "valor": por_camada.get("diagnostico_historico", 0)},
        {"metrica": "arquivos_renderizacao_com_risco_semantico", "valor": sum(1 for r in rows_arquivos if r["camada_7e_inferida"] == "renderizacao_console_planilha" and r["risco_renderizacao_com_semantica"] != "baixo")},
        {"metrica": "arquivos_saida_com_risco_decisorio", "valor": sum(1 for r in rows_arquivos if "saida" in r["arquivo"] and r["risco_decisao_fora_motor"] != "baixo")},
        {"metrica": "status_global_v17_e0", "valor": "atencao" if risco_alto > 0 else "ok"},
        {"metrica": "recomendacao_proxima_microetapa", "valor": "auditar fronteiras motor_saida_render e consolidar helpers duplicados"},
    ]

    def write_csv(name: str, headers: list[str], rows: list[dict]):
        out = OUT_DIR / name
        with out.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in headers})

    write_csv("v17_e0_arquivos_por_camada.csv", [
        "arquivo", "extensao", "linhas", "tamanho_bytes", "camada_7e_inferida", "camada_7e_secundaria", "tipo_arquivo", "participa_rota_principal_inferida", "risco_mistura_responsabilidades", "risco_decisao_fora_motor", "risco_renderizacao_com_semantica", "risco_diagnostico_com_regra_economica", "risco_codigo_legado", "acao_recomendada", "justificativa"
    ], rows_arquivos)

    write_csv("v17_e0_funcoes_classes.csv", [
        "arquivo", "funcao_ou_classe", "tipo", "linha_inicio", "camada_7e_inferida", "termos_detectados", "pode_decidir", "pode_alterar_estado", "pode_renderizar", "pode_diagnosticar", "risco_duplicacao_nome", "risco_fronteira", "acao_recomendada"
    ], fc_rows)

    write_csv("v17_e0_imports_dependencias.csv", [
        "arquivo", "importado", "tipo_import", "camada_origem_inferida", "camada_destino_inferida", "risco_dependencia_invertida", "observacao"
    ], imports_rows)

    write_csv("v17_e0_duplicidades_funcoes.csv", [
        "nome_funcao_ou_classe", "quantidade_ocorrencias", "arquivos", "camadas", "risco", "acao_recomendada"
    ], dup_rows)

    write_csv("v17_e0_pontos_risco_arquitetural.csv", [
        "arquivo", "linha", "tipo_risco", "trecho_resumido", "camada_esperada", "camada_observada", "severidade", "recomendacao"
    ], risco_rows)

    write_csv("v17_e0_resumo.csv", ["metrica", "valor"], resumo)

    write_csv("v17_e0_matriz_recomendacao.csv", [
        "prioridade", "alvo", "tipo_alvo", "problema", "evidencia", "camada_correta_7e", "acao_recomendada", "pode_alterar_agora", "validacao_necessaria", "risco_se_nao_corrigir"
    ], matriz)

    print(f"Arquivos mapeados: {len(rows_arquivos)}")
    print(f"Funções/classes: {len(fc_rows)}")
    print(f"Duplicidades nome: {len(dup_rows)}")
    print(f"Saída: {OUT_DIR}")


if __name__ == "__main__":
    main()
