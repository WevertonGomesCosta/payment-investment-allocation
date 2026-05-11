#!/usr/bin/env python3
"""V17-E1-A — Auditoria de fronteiras motor ↔ saída ↔ renderização."""
from __future__ import annotations

import ast
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
V17_E0_DIR = ROOT / "saidas" / "diagnostico" / "v17_e0"
OUT_DIR = ROOT / "saidas" / "diagnostico" / "v17_e1_a"

REQUIRED_V17_E0 = [
    "v17_e0_arquivos_por_camada.csv",
    "v17_e0_funcoes_classes.csv",
    "v17_e0_imports_dependencias.csv",
    "v17_e0_pontos_risco_arquitetural.csv",
    "v17_e0_matriz_recomendacao.csv",
]

TARGET_FILES = [
    "aplicacao/principal.py",
    "aplicacao/console/principal.py",
    "aplicacao/console/secoes_execucao.py",
    "nucleo/contexto_baseline.py",
    "nucleo/saida_canonica.py",
    "nucleo/construir_saida_canonica_v17_c7.py",
    "nucleo/saida_canonica_switching_v17_c7.py",
    "nucleo/ponte_renderizacao_switching_v17_c6.py",
    "nucleo/saida_observavel.py",
    "nucleo/gerar_planilha_operacional.py",
    "nucleo/ledger_temporal_conjunto.py",
    "nucleo/motor_recomendacao_pagamentos_switching_v1.py",
    "nucleo/recomputacao_sequencial_central_v1.py",
    "nucleo/alocador_pagamentos_terminal_v1.py",
    "nucleo/planejador_switching_temporal_v1.py",
    "nucleo/reescolha_dinamica_pos_quebra.py",
]

DECISAO = {"decidir","decisao","escolher","recomendar","promover","alocar","pagar","resgatar","sacar","switching","materializar","migrar","refactibilizar"}
ESTADO = {"estado","ledger","saldo","fonte","lote","residual","exaurido","ativo","migrado","materializado","temporal"}
SAIDA = {"saida_canonica","pacote_saida","extrato","situacao_atual","auditoria","fechamento"}
RENDER = {"console","planilha","openpyxl","workbook","aba","render","imprimir","formatar"}

ROLES = {"motor_temporal","ledger_estado","construtor_saida","saida_canonica","render_console","render_planilha","ponte_saida","orquestrador","diagnostico","indefinido"}
ACTIONS = {"manter","manter_auditar","refatorar_futuramente","migrar_para_motor_futuramente","migrar_para_saida_futuramente","migrar_para_renderizacao_futuramente","congelar_como_ponte_transitoria","bloquear_expansao","indefinido_requer_auditoria"}

@dataclass
class FileAudit:
    path: str
    text: str
    imports: list[str]
    funcs: list[tuple[str,int,str]]


def norm_path_key(value: str) -> str:
    return str(value or "").replace("\\", "/")


def must_exist_v17_e0() -> None:
    missing = [f for f in REQUIRED_V17_E0 if not (V17_E0_DIR / f).exists()]
    if missing:
        raise RuntimeError(f"CSVs V17-E0 ausentes: {', '.join(missing)}")


def read_layer_map() -> dict[str, str]:
    mapping = {}
    p = V17_E0_DIR / "v17_e0_arquivos_por_camada.csv"
    with p.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            arq = norm_path_key(row.get("arquivo") or row.get("file") or "")
            camada = (
                row.get("camada_7e_inferida")
                or row.get("camada_7e")
                or row.get("camada")
                or "indefinido"
            )
            if arq:
                mapping[arq] = camada
    return mapping


def extract(path: Path) -> FileAudit:
    txt = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(txt)
    except SyntaxError:
        tree = ast.parse("")
    imports, funcs = [], []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imports.extend(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            imports.append((n.module or ""))
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            seg = ast.get_source_segment(txt, n) or ""
            funcs.append((n.name, n.lineno, seg.lower()))
    return FileAudit(str(path.relative_to(ROOT).as_posix()), txt.lower(), sorted(set(imports)), funcs)


def count_terms(text: str, terms: set[str]) -> int:
    return sum(text.count(t) for t in terms)


def infer_role(path: str, t_m: int, t_s: int, t_r: int) -> str:
    p = path.lower()
    if "diagnostico" in p:
        return "diagnostico"
    if p.startswith("aplicacao/console/") or "console" in p:
        return "render_console"
    if p == "aplicacao/principal.py":
        return "orquestrador"
    if "ponte_" in p:
        return "ponte_saida"
    if "planilha" in p:
        return "render_planilha"
    if "construir_saida" in p:
        return "construtor_saida"
    if "saida_canonica" in p:
        return "saida_canonica"
    if "ledger" in p:
        return "ledger_estado"
    if "motor" in p or "planejador" in p or "alocador" in p or "recomputacao" in p:
        return "motor_temporal"
    if t_m > t_s and t_m >= t_r:
        return "motor_temporal"
    return "indefinido"


def main() -> None:
    must_exist_v17_e0()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    layer = read_layer_map()
    audits = [extract(ROOT / p) for p in TARGET_FILES if (ROOT / p).exists()]

    fronteiras, funcoes, pontes, fluxo, riscos = [], [], [], [], []
    ordem_fluxo = 1
    principal_audit = next((a for a in audits if a.path == "aplicacao/principal.py"), None)
    for a in audits:
        tm, ts, tr, td, te = count_terms(a.text, ESTADO), count_terms(a.text, SAIDA), count_terms(a.text, RENDER), count_terms(a.text, DECISAO), count_terms(a.text, ESTADO)
        role = infer_role(a.path, tm, ts, tr)
        mixed = sum(int(x>0) for x in [tm, ts, tr, td]) >= 3
        risk = "alto" if mixed else "medio" if (td>0 and role in {"saida_canonica","construtor_saida","render_console","render_planilha","ponte_saida"}) else "baixo"
        tipo = "responsabilidade_mista" if mixed else ("renderizacao_com_regra_semantica" if role.startswith("render") and td>0 else "evidencia_fronteira")
        action = "indefinido_requer_auditoria" if risk=="alto" else ("congelar_como_ponte_transitoria" if role=="ponte_saida" else "manter_auditar")
        fronteiras.append({"arquivo":norm_path_key(a.path),"camada_7e_v17_e0":layer.get(norm_path_key(a.path),"indefinido"),"papel_inferido_v17_e1_a":role,"linhas":a.text.count("\n")+1,"imports_relevantes":";".join(a.imports[:12]),"termos_motor":tm,"termos_saida":ts,"termos_renderizacao":tr,"termos_decisao":td,"risco_fronteira":risk,"tipo_risco_principal":tipo,"acao_recomendada":action,"justificativa":"Heurística de fronteira sem inferência de bug funcional."})
        if role=="ponte_saida" or any(x in a.path for x in ["construir_saida_canonica_v17_c7","saida_canonica_switching_v17_c7","ponte_renderizacao_switching_v17_c6"]):
            pontes.append({"arquivo":norm_path_key(a.path),"funcao_ou_classe":"arquivo","tipo_ponte":"wrapper_versionado","alvo_chamado":"indeterminado","altera_estado":"sim" if tm>0 and td>0 else "nao","altera_saida":"sim" if ts>0 else "nao","altera_apenas_renderizacao":"sim" if tr>0 and ts==0 and tm==0 else "nao","risco":risk,"acao_recomendada":"congelar_como_ponte_transitoria","observacao":"Ponte C6/C7 tratada como transição, não erro automático."})
        for n,lin,seg in a.funcs:
            d,e,s,r = count_terms(seg,DECISAO), count_terms(seg,ESTADO), count_terms(seg,SAIDA), count_terms(seg,RENDER)
            obs = role
            if d>0 and role in {"saida_canonica","construtor_saida"}: obs = "responsabilidade_mista"
            funcoes.append({"arquivo":norm_path_key(a.path),"funcao_ou_classe":n,"linha_inicio":lin,"papel_esperado":role,"papel_observado":obs,"termos_detectados":f"decisao={d};estado={e};saida={s};render={r}","pode_decidir":"sim" if d>0 else "nao","pode_alterar_estado":"sim" if e>0 else "nao","pode_materializar_switching":"sim" if "switching" in seg else "nao","pode_recalcular_saldo":"sim" if "saldo" in seg else "nao","pode_renderizar":"sim" if r>0 else "nao","risco_fronteira":"alto" if obs=="responsabilidade_mista" else "medio" if d>0 else "baixo","acao_recomendada":"indefinido_requer_auditoria" if obs=="responsabilidade_mista" else "manter_auditar","justificativa":"Classificação heurística com viés para falso positivo controlado."})

    principal_text = principal_audit.text if principal_audit else ""
    principal_path = norm_path_key(principal_audit.path) if principal_audit else "aplicacao/principal.py"
    calls = ["contexto", "saida_canonica", "console", "planilha"]
    for c in calls:
        fluxo.append(
            {
                "ordem": ordem_fluxo,
                "arquivo": principal_path,
                "funcao_ou_chamada": c,
                "camada_7e": layer.get(norm_path_key(principal_path), "indefinido"),
                "tipo_fluxo": "inferido_estatico" if c in principal_text else "indeterminado",
                "observacao": "Mapeamento de fluxo principal para contexto→saída→renderizações.",
                "risco": "medio" if c not in principal_text else "baixo",
            }
        )
        ordem_fluxo += 1

    for f in fronteiras:
        if f["tipo_risco_principal"] in {"responsabilidade_mista","renderizacao_com_regra_semantica"}:
            prio = "P0" if f["risco_fronteira"]=="alto" else "P1"
            riscos.append({"prioridade":prio,"arquivo":f["arquivo"],"funcao_ou_classe":"arquivo","tipo_risco":f["tipo_risco_principal"],"evidencia":f"decisao={f['termos_decisao']};estado={f['termos_motor']};saida={f['termos_saida']};render={f['termos_renderizacao']}","camada_correta_7e":f["papel_inferido_v17_e1_a"],"impacto_potencial":"Acoplamento de fronteira e regressão difícil de detectar.","recomendacao":f["acao_recomendada"],"pode_corrigir_agora":"nao"})
    if pontes:
        riscos.append({"prioridade":"P1","arquivo":pontes[0]["arquivo"],"funcao_ou_classe":pontes[0]["funcao_ou_classe"],"tipo_risco":"wrapper_versionado_na_rota_principal","evidencia":"Presença de ponte/wrapper versionado C6/C7 na trilha de saída.","camada_correta_7e":"ponte_saida","impacto_potencial":"Persistência de integração transitória.","recomendacao":"congelar_como_ponte_transitoria","pode_corrigir_agora":"nao"})

    matriz = [
        {"prioridade":"P0","frente":"fronteira_saida_vs_motor","problema":"Responsabilidade mista em construção/saída com sinais de decisão/estado.","evidencia":"CSV de fronteiras e funções com risco alto.","arquivos_envolvidos":";".join(sorted({r['arquivo'] for r in riscos if r['prioridade']=='P0'})) or "indeterminado","acao_recomendada":"migrar_para_motor_futuramente","tipo_microetapa_sugerida":"V17-E1-B principal","risco_se_nao_fizer":"Evolução de saída reintroduzindo semântica decisória.","validacao_necessaria":"Reexecutar auditoria de fronteiras e invariantes de saída."},
        {"prioridade":"P1","frente":"pontes_versionadas_c6_c7","problema":"Pontes transitórias podem expandir escopo funcional.","evidencia":"Detecção explícita de wrappers C6/C7.","arquivos_envolvidos":";".join(sorted({p['arquivo'] for p in pontes})) or "indeterminado","acao_recomendada":"bloquear_expansao","tipo_microetapa_sugerida":"V17-E1-B alternativa","risco_se_nao_fizer":"Acoplamento legado na rota principal.","validacao_necessaria":"Checklist de não expansão em PRs."}
    ]

    resumo = [
        ("arquivos_auditados", len(audits)), ("funcoes_classes_auditadas", len(funcoes)), ("pontes_wrappers_detectados", len(pontes)),
        ("riscos_prioritarios_total", len(riscos)), ("riscos_p0", sum(1 for r in riscos if r['prioridade']=='P0')), ("riscos_p1", sum(1 for r in riscos if r['prioridade']=='P1')),
        ("arquivos_saida_com_decisao_potencial", sum(1 for f in fronteiras if f['papel_inferido_v17_e1_a'] in {'saida_canonica','construtor_saida'} and int(f['termos_decisao'])>0)),
        ("arquivos_renderizacao_com_semantica_potencial", sum(1 for f in fronteiras if str(f['papel_inferido_v17_e1_a']).startswith('render') and int(f['termos_decisao'])>0)),
        ("wrappers_versionados_na_rota", len(pontes)), ("status_global_v17_e1_a", "atencao" if any(r['prioridade']=='P0' for r in riscos) else "monitorar"),
        ("recomendacao_proxima_microetapa", "V17-E1-B: migrar semântica decisória residual de saída para motor temporal e congelar pontes C6/C7")
    ]

    def w(name:str, rows:list[dict], headers:Iterable[str]):
        with (OUT_DIR/name).open('w',encoding='utf-8',newline='') as f:
            dw=csv.DictWriter(f,fieldnames=list(headers)); dw.writeheader(); dw.writerows(rows)

    w("v17_e1_a_fronteiras_arquivos.csv", fronteiras, ["arquivo","camada_7e_v17_e0","papel_inferido_v17_e1_a","linhas","imports_relevantes","termos_motor","termos_saida","termos_renderizacao","termos_decisao","risco_fronteira","tipo_risco_principal","acao_recomendada","justificativa"])
    w("v17_e1_a_funcoes_fronteira.csv", funcoes, ["arquivo","funcao_ou_classe","linha_inicio","papel_esperado","papel_observado","termos_detectados","pode_decidir","pode_alterar_estado","pode_materializar_switching","pode_recalcular_saldo","pode_renderizar","risco_fronteira","acao_recomendada","justificativa"])
    w("v17_e1_a_pontes_wrappers.csv", pontes, ["arquivo","funcao_ou_classe","tipo_ponte","alvo_chamado","altera_estado","altera_saida","altera_apenas_renderizacao","risco","acao_recomendada","observacao"])
    w("v17_e1_a_fluxo_principal.csv", fluxo, ["ordem","arquivo","funcao_ou_chamada","camada_7e","tipo_fluxo","observacao","risco"])
    w("v17_e1_a_riscos_prioritarios.csv", riscos, ["prioridade","arquivo","funcao_ou_classe","tipo_risco","evidencia","camada_correta_7e","impacto_potencial","recomendacao","pode_corrigir_agora"])
    w("v17_e1_a_matriz_decisao_proxima_etapa.csv", matriz, ["prioridade","frente","problema","evidencia","arquivos_envolvidos","acao_recomendada","tipo_microetapa_sugerida","risco_se_nao_fizer","validacao_necessaria"])
    with (OUT_DIR/"v17_e1_a_resumo.csv").open('w',encoding='utf-8',newline='') as f:
        dw=csv.writer(f); dw.writerow(["metrica","valor"]); dw.writerows(resumo)


if __name__ == "__main__":
    main()
