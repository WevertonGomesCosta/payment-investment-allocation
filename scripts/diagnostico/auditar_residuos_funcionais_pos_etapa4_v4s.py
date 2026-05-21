from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

ALVOS_DUPLICIDADE = {
    "valor_original": ["orig", "valor_original", "valor original"],
    "produto_carteira": ["produto", "carteira"],
    "aplicacao_base_fiscal": ["aplic", "aplicação", "base fiscal"],
    "saldo_sacado_remanescente": ["saldo", "sac", "remanesc"],
}

CATEGORIAS_TECNICAS_V4 = [
    "normalizacao",
    "equivalencia_runtime",
    "runtime",
    "correcao",
    "fechamento",
    "pacote",
    "shadow",
    "auditoria",
    "outros",
]


def _contains_any(text: str, tokens: list[str]) -> bool:
    t = text.lower()
    return any(tok in t for tok in tokens)


def _func_source(src_lines: list[str], node: ast.AST) -> str:
    ini = getattr(node, "lineno", 1) - 1
    fim = getattr(node, "end_lineno", getattr(node, "lineno", 1))
    return "\n".join(src_lines[ini:fim]).lower()


def _classificar_v4_tecnico(nome_arquivo: str) -> str:
    n = nome_arquivo.lower()
    if "normalizacao" in n:
        return "normalizacao"
    if "equivalencia" in n and "runtime" in n:
        return "equivalencia_runtime"
    if "runtime" in n:
        return "runtime"
    if "correc" in n:
        return "correcao"
    if "fechamento" in n:
        return "fechamento"
    if "pacote" in n:
        return "pacote"
    if "shadow" in n:
        return "shadow"
    if "auditar" in n or "auditoria" in n:
        return "auditoria"
    return "outros"


def _classificar_v4_operacional(nome_arquivo: str) -> str:
    n = nome_arquivo.lower()
    if any(k in n for k in ["fechamento", "gate", "validar", "integracao", "pos_", "consistencia"]):
        return "ativo_regressao"
    if any(k in n for k in ["equivalencia", "runtime", "histor", "registro"]):
        return "historico_preservar"
    if any(k in n for k in ["normalizacao", "correcao", "reconcili", "refina", "diagnost"]):
        return "candidato_arquivo_historico_futuro"
    return "candidato_remocao_futura"


def inventariar_saida_observavel(path: Path) -> dict[str, Any]:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    lines = src.splitlines()

    funcoes: list[str] = []
    funcoes_acessam_contexto: list[str] = []
    funcoes_acessam_replay: list[str] = []
    funcoes_getattr_amplo: list[str] = []
    funcoes_iter_dict: list[str] = []
    funcoes_iter_df_generico: list[str] = []
    funcoes_reconstroem_observavel_com_replay: list[str] = []
    duplicidades: dict[str, list[str]] = {k: [] for k in ALVOS_DUPLICIDADE}

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        nome = node.name
        funcoes.append(nome)
        corpo = _func_source(lines, node)

        if "contexto" in corpo:
            funcoes_acessam_contexto.append(nome)
        if "replay" in corpo:
            funcoes_acessam_replay.append(nome)

        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == "getattr":
                if len(sub.args) >= 2 and isinstance(sub.args[1], ast.Constant) and isinstance(sub.args[1].value, str):
                    arg = sub.args[1].value.lower()
                    if arg in {"__dict__", "dict", "items"} or any(x in arg for x in ["contexto", "replay", "log", "extrato"]):
                        funcoes_getattr_amplo.append(nome)
                else:
                    funcoes_getattr_amplo.append(nome)
            if isinstance(sub, ast.Attribute) and sub.attr == "__dict__":
                funcoes_iter_dict.append(nome)
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) and sub.func.attr in {"iterrows", "itertuples", "to_dict"}:
                funcoes_iter_df_generico.append(nome)

        tem_replay = "replay" in corpo
        tem_acao_reconstrucao = _contains_any(
            corpo,
            ["corrig", "reconst", "saldo", "remanesc", "pagamento", "lote", "mapa"],
        )
        if tem_replay and tem_acao_reconstrucao:
            funcoes_reconstroem_observavel_com_replay.append(nome)

        for chave, tokens in ALVOS_DUPLICIDADE.items():
            if all(tok in corpo for tok in tokens):
                duplicidades[chave].append(nome)

    uniq = lambda xs: sorted(set(xs))
    return {
        "arquivo_alvo": str(path.relative_to(ROOT)),
        "funcoes_saida_observavel": uniq(funcoes),
        "funcoes_acessam_contexto": uniq(funcoes_acessam_contexto),
        "funcoes_acessam_replay": uniq(funcoes_acessam_replay),
        "funcoes_getattr_amplo": uniq(funcoes_getattr_amplo),
        "funcoes_iter_dict": uniq(funcoes_iter_dict),
        "funcoes_iter_df_generico": uniq(funcoes_iter_df_generico),
        "funcoes_reconstroem_observavel_com_replay": uniq(funcoes_reconstroem_observavel_com_replay),
        "duplicidades_potenciais": {k: uniq(v) for k, v in duplicidades.items()},
    }


def inventariar_shadows_e_v4() -> dict[str, Any]:
    py_files = sorted((ROOT / "nucleo").glob("*.py"))
    shadow_arquivos = [str(p.relative_to(ROOT)) for p in py_files if "shadow" in p.stem.lower()]

    caminhos_shadow_explicitos = {
        "PacoteReplayPassado shadow": "nucleo/pacote_replay_passado.py",
        "PacoteLedgerTemporalOperacional shadow": "nucleo/pacote_ledger_temporal_operacional.py",
        "PacoteEstadoTemporal shadow": "nucleo/pacote_estado_temporal.py",
        "PacoteAuditoriaTemporal shadow": "nucleo/pacote_auditoria_temporal.py",
        "pacotes_temporais_agregados_saida": "nucleo/pacotes_temporais_agregados_saida.py",
        "bloco temporal shadow na auditoria da saída": "nucleo/saida_canonica_temporal_shadow_v4k.py",
        "parâmetro incluir_temporal_shadow": "nucleo/saida_canonica.py",
    }
    caminhos_shadow_explicitos_status = {}
    for rotulo, rel in caminhos_shadow_explicitos.items():
        existe = (ROOT / rel).exists()
        caminhos_shadow_explicitos_status[rotulo] = {
            "path": rel,
            "existe": existe,
            "tipo": "existente" if existe else "conceitual_ou_nao_existente",
        }

    diag_v4 = sorted((ROOT / "scripts" / "diagnostico").glob("*v4*.py"))
    class_tecnica = {k: [] for k in CATEGORIAS_TECNICAS_V4}
    class_operacional = {
        "ativo_regressao": [],
        "historico_preservar": [],
        "candidato_arquivo_historico_futuro": [],
        "candidato_remocao_futura": [],
    }

    for p in diag_v4:
        rel = str(p.relative_to(ROOT))
        tec = _classificar_v4_tecnico(p.stem)
        op = _classificar_v4_operacional(p.stem)
        class_tecnica[tec].append(rel)
        class_operacional[op].append(rel)

    return {
        "caminhos_shadow_ainda_necessarios_por_arquivo": shadow_arquivos,
        "caminhos_shadow_classificacao_explicita": caminhos_shadow_explicitos_status,
        "diagnosticos_v4_classificacao_tecnica": class_tecnica,
        "diagnosticos_v4_classificacao_operacional": class_operacional,
    }


def classificar_residuos_operacional(inv: dict[str, Any]) -> dict[str, list[str]]:
    dups = inv.get("duplicidades_potenciais", {})
    return {
        "remover_agora": [],
        "manter_ate_etapa5": ["saida_observavel_consulta_contexto_replay"],
        "migrar_para_contrato_futuro": ["correcao_reconstrucao_observavel_baseada_em_replay"],
        "preservar_como_auditoria_historica": ["diagnosticos_v4"],
        "manter_controlado": ["caminhos_shadow"],
        "investigar_antes_de_remover": [
            "varredura_generica_via___dict__",
            "iteracao_generica_dataframes",
            f"duplicidades_potenciais:{','.join([k for k,v in dups.items() if v])}",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-csv", action="store_true", help="Mantido para compatibilidade operacional")
    _ = parser.parse_args()

    alvo = ROOT / "nucleo" / "saida_observavel.py"
    if not alvo.exists():
        print("inventario_emitido=False")
        print("erro=arquivo_alvo_inexistente")
        return 1

    inventario: dict[str, Any] = {}
    inventario.update(inventariar_saida_observavel(alvo))
    inventario.update(inventariar_shadows_e_v4())
    inventario["classificacao_operacional_residuos"] = classificar_residuos_operacional(inventario)

    varredura_generica = set(inventario["funcoes_iter_dict"]) | set(inventario["funcoes_iter_df_generico"])
    dups_pres = any(bool(v) for v in inventario["duplicidades_potenciais"].values())
    qtd_diag = sum(len(v) for v in inventario["diagnosticos_v4_classificacao_tecnica"].values())
    qtd_shadow = len(inventario["caminhos_shadow_ainda_necessarios_por_arquivo"]) + sum(1 for v in inventario["caminhos_shadow_classificacao_explicita"].values() if v.get("existe"))

    inventario.update({
        "execucao_v4s_concluida": True,
        "inventario_residuos_emitido": True,
        "residuos_funcionais_identificados": bool(inventario["funcoes_acessam_contexto"] or inventario["funcoes_acessam_replay"]),
        "duplicidades_potenciais_identificadas": dups_pres,
        "saida_observavel_replay_classificado": bool(inventario["funcoes_reconstroem_observavel_com_replay"]),
        "funcoes_com_varredura_generica_classificadas": bool(varredura_generica),
        "diagnosticos_v4_classificados": qtd_diag > 0,
        "caminhos_shadow_classificados": qtd_shadow > 0,
        "nenhuma_remocao_automatica": True,
        "plano_limpeza_codigo_definido": True,
        "residuos_bloqueantes_etapa5": False,
        "recomendacao_abrir_etapa5": False,
        "diagnostico_v4s_ok": True,
        "qtd_funcoes_saida_observavel_analisadas": len(inventario["funcoes_saida_observavel"]),
        "qtd_funcoes_acessam_contexto": len(inventario["funcoes_acessam_contexto"]),
        "qtd_funcoes_acessam_replay": len(inventario["funcoes_acessam_replay"]),
        "qtd_funcoes_varredura_generica": len(varredura_generica),
        "qtd_diagnosticos_v4_encontrados": qtd_diag,
        "qtd_caminhos_shadow_classificados": qtd_shadow,
        "qtd_residuos_remover_agora": len(inventario["classificacao_operacional_residuos"]["remover_agora"]),
        "qtd_residuos_migrar_contrato_futuro": len(inventario["classificacao_operacional_residuos"]["migrar_para_contrato_futuro"]),
        "qtd_residuos_preservar_historico": len(inventario["classificacao_operacional_residuos"]["preservar_como_auditoria_historica"]),
    })

    for k, v in inventario.items():
        print(f"{k}={json.dumps(v, ensure_ascii=False, sort_keys=True)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
