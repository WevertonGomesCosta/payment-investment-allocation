from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida_shadow
from nucleo.saida_canonica import construir_saida_canonica


def _normalizar_texto(valor: Any) -> str:
    texto = str(valor or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"\s+", " ", texto)
    return texto


def _termo_lote(termo: str) -> str:
    return _normalizar_texto(termo)


def _row_contem_lote(row: Mapping[str, Any], termo: str) -> bool:
    alvo = _termo_lote(termo)
    for valor in row.values():
        if alvo in _normalizar_texto(valor):
            return True
    return False


def _as_list_dict(valor: Any) -> list[dict[str, Any]]:
    if valor is None:
        return []
    if isinstance(valor, pd.DataFrame):
        return list(valor.to_dict(orient="records"))
    if isinstance(valor, list):
        return [dict(x) for x in valor if isinstance(x, Mapping)]
    if isinstance(valor, tuple):
        return [dict(x) for x in valor if isinstance(x, Mapping)]
    if isinstance(valor, Mapping):
        return [dict(valor)]
    return []


def _normalizar(obj: Any) -> Any:
    if isinstance(obj, pd.DataFrame):
        return [_normalizar(x) for x in obj.to_dict(orient="records")]
    if isinstance(obj, Mapping):
        return {str(k): _normalizar(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}
    if isinstance(obj, list):
        return [_normalizar(v) for v in obj]
    if isinstance(obj, tuple):
        return [_normalizar(v) for v in obj]
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return obj


def _serializar(obj: Any) -> str:
    return json.dumps(_normalizar(obj), ensure_ascii=False, sort_keys=True, default=str)


def _iguais(a: Any, b: Any) -> bool:
    return _serializar(a) == _serializar(b)


def _to_float(valor: Any) -> float | None:
    if valor is None:
        return None
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        if math.isnan(float(valor)):
            return None
        return float(valor)
    texto = str(valor).strip()
    if not texto:
        return None
    texto = texto.replace("R$", "").replace(" ", "")
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except Exception:
        return None


def _campo_eh_saldo(nome: str) -> bool:
    n = _normalizar_texto(nome)
    return "saldo" in n or n in {"rem", "remanescente"}


def _campo_eh_rendimento(nome: str) -> bool:
    n = _normalizar_texto(nome)
    return "rend" in n or "rendimento" in n


def _campo_eh_liquido_atual(nome: str) -> bool:
    n = _normalizar_texto(nome)
    return ("liq" in n or "liquido" in n) and "atual" in n


def _campo_eh_bruto_atual(nome: str) -> bool:
    n = _normalizar_texto(nome)
    return "bruto" in n and "atual" in n


def _filtrar_rows_lote(rows: Any, termo: str) -> list[dict[str, Any]]:
    return [row for row in _as_list_dict(rows) if _row_contem_lote(row, termo)]


def _linhas_resumo(resultado: dict[str, Any]) -> list[dict[str, Any]]:
    linhas = []
    for chave, valor in resultado.items():
        if isinstance(valor, (dict, list)):
            valor = json.dumps(valor, ensure_ascii=False, sort_keys=True, default=str)
        linhas.append({"metrica": chave, "valor": valor})
    return linhas


def _buscar_campo_negativo(rows_por_origem: dict[str, list[dict[str, Any]]], predicado_campo) -> dict[str, Any] | None:
    for origem, rows in rows_por_origem.items():
        for idx, row in enumerate(rows, start=1):
            for chave, valor in row.items():
                if predicado_campo(str(chave)):
                    numero = _to_float(valor)
                    if numero is not None and numero < 0:
                        return {
                            "origem": origem,
                            "indice": idx,
                            "campo": str(chave),
                            "valor": numero,
                            "linha": row,
                        }
    return None


def _buscar_saldo_atual_saida(lotes_saida: list[dict[str, Any]]) -> dict[str, Any] | None:
    for row in lotes_saida:
        for chave, valor in row.items():
            if _campo_eh_liquido_atual(str(chave)) or _campo_eh_bruto_atual(str(chave)):
                numero = _to_float(valor)
                if numero is not None:
                    return {"campo": str(chave), "valor": numero, "linha": row}
    return None


def _classificar_origem_saldo_negativo(evidencia: dict[str, Any] | None) -> str:
    if not evidencia:
        return "nao_identificada"
    origem = evidencia.get("origem", "")
    if "extrato_passado" in origem:
        return "extrato_passado_saida_ja_exibe_saldo_negativo"
    if "replay" in origem:
        return "replay_passado_ja_exibe_saldo_negativo"
    if "ledger" in origem:
        return "ledger_temporal_ja_exibe_saldo_negativo"
    if "estado" in origem:
        return "estado_temporal_ja_exibe_saldo_negativo"
    return "saldo_negativo_em_origem_nao_classificada"


def _classificar_origem_exaustao(row_exaurido: dict[str, Any] | None, estado_final: list[dict[str, Any]]) -> str:
    if row_exaurido:
        status = " ".join(str(v) for v in row_exaurido.values())
        if "exaurido" in _normalizar_texto(status):
            return "saida_situacao_atual_classifica_como_exaurido"
    for row in estado_final:
        status = " ".join(str(v) for v in row.values())
        if "exaurido" in _normalizar_texto(status) or "saldo" in _normalizar_texto(status):
            return "estado_temporal_contem_registro_de_exaustao_ou_saldo_final"
    return "nao_identificada"


def _classificar_origem_rendimento_negativo(evidencia: dict[str, Any] | None) -> str:
    if not evidencia:
        return "nao_identificada"
    origem = evidencia.get("origem", "")
    if "saida_lotes" in origem:
        return "situacao_atual_saida_calcula_rendimento_negativo"
    if "estado" in origem:
        return "estado_temporal_carrega_rendimento_negativo"
    return "rendimento_negativo_em_origem_nao_classificada"


def _coletar_origens(contexto: Any, saida: Any, agregados: Any, termo_lote: str) -> dict[str, list[dict[str, Any]]]:
    replay = agregados.pacote_replay_passado
    ledger = agregados.pacote_ledger_temporal_operacional
    estado = agregados.pacote_estado_temporal

    origens = {
        "saida_extrato_passado": _filtrar_rows_lote(getattr(saida, "extrato_passado", []), termo_lote),
        "saida_extrato_futuro": _filtrar_rows_lote(getattr(saida, "extrato_futuro", []), termo_lote),
        "saida_lotes_ativos": _filtrar_rows_lote(getattr(saida, "lotes_ativos", []), termo_lote),
        "saida_lotes_exauridos": _filtrar_rows_lote(getattr(saida, "lotes_exauridos", []), termo_lote),
        "replay_log_movimentos_passados": _filtrar_rows_lote(getattr(replay, "log_movimentos_passados", []), termo_lote),
        "replay_estado_lotes_passado": _filtrar_rows_lote(getattr(replay, "estado_lotes_passado", []), termo_lote),
        "replay_audit_trilha_pagamentos_passados": _filtrar_rows_lote(getattr(replay, "audit_trilha_pagamentos_passados", []), termo_lote),
        "ledger_eventos_temporais": _filtrar_rows_lote(getattr(ledger, "eventos_temporais", []), termo_lote),
        "ledger_fifo_candidatos_avaliados": _filtrar_rows_lote(getattr(ledger, "fifo_candidatos_avaliados", []), termo_lote),
        "ledger_saldos_por_lote": _filtrar_rows_lote(getattr(ledger, "saldos_por_lote", []), termo_lote),
        "ledger_fontes_elegiveis_por_pagamento": _filtrar_rows_lote(getattr(ledger, "fontes_elegiveis_por_pagamento", []), termo_lote),
        "estado_lotes_por_data": _filtrar_rows_lote(getattr(estado, "estado_lotes_por_data", []), termo_lote),
        "estado_lotes_final": _filtrar_rows_lote(getattr(estado, "estado_lotes_final", []), termo_lote),
        "estado_saldos_por_lote": _filtrar_rows_lote(getattr(estado, "saldos_por_lote", []), termo_lote),
        "estado_fontes_disponiveis_por_data": _filtrar_rows_lote(getattr(estado, "fontes_disponiveis_por_data", []), termo_lote),
    }

    dados_operacionais = getattr(contexto, "dados_operacionais", None)
    for nome in ["inventario_canonico", "inventario_lotes_expandido", "lotes_canonicos", "recebidos_canonicos"]:
        valor = getattr(dados_operacionais, nome, None) if dados_operacionais is not None else None
        origens[f"dados_operacionais_{nome}"] = _filtrar_rows_lote(valor, termo_lote)

    return origens


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita saldo, exaustão e rendimento do Lote 3120 mai na Etapa 4.")
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--lote", default="Lote 3120 mai")
    parser.add_argument("--saldo-app", type=float, default=50.0, help="Saldo aproximado informado pelo app para comparação diagnóstica.")
    parser.add_argument("--sem-csv", action="store_true")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )

    saida_antes = construir_saida_canonica(contexto)
    agregados = construir_pacotes_temporais_agregados_saida_shadow(contexto)
    saida_depois = construir_saida_canonica(contexto)

    origens = _coletar_origens(contexto, saida_antes, agregados, args.lote)
    contagens = {origem: len(rows) for origem, rows in origens.items()}

    evid_saldo_negativo = _buscar_campo_negativo(origens, _campo_eh_saldo)
    evid_rendimento_negativo = _buscar_campo_negativo(origens, _campo_eh_rendimento)

    lotes_saida = origens["saida_lotes_ativos"] + origens["saida_lotes_exauridos"]
    row_exaurido = origens["saida_lotes_exauridos"][0] if origens["saida_lotes_exauridos"] else None
    saldo_atual_saida = _buscar_saldo_atual_saida(lotes_saida)

    pagamentos_lote = origens["saida_extrato_passado"] + origens["replay_log_movimentos_passados"] + origens["ledger_eventos_temporais"]
    saldo_modelo = saldo_atual_saida["valor"] if saldo_atual_saida else None
    diferenca_app_modelo = None if saldo_modelo is None else round(float(args.saldo_app) - float(saldo_modelo), 2)

    origem_saldo = _classificar_origem_saldo_negativo(evid_saldo_negativo)
    origem_exaustao = _classificar_origem_exaustao(row_exaurido, origens["estado_lotes_final"])
    origem_rendimento = _classificar_origem_rendimento_negativo(evid_rendimento_negativo)

    causa_classificada = all([
        origem_saldo != "nao_identificada",
        origem_exaustao != "nao_identificada",
        origem_rendimento != "nao_identificada",
    ])

    resultado = {
        "adaptador": "auditar_lote_3120_mai_estado_temporal_v4o",
        "lote_alvo": args.lote,
        "saldo_app_referencia": args.saldo_app,
        "lote_3120_encontrado_inventario_canonico": contagens.get("dados_operacionais_inventario_canonico", 0) > 0,
        "lote_3120_encontrado_replay": contagens.get("replay_log_movimentos_passados", 0) > 0 or contagens.get("replay_estado_lotes_passado", 0) > 0,
        "lote_3120_encontrado_ledger": contagens.get("ledger_eventos_temporais", 0) > 0 or contagens.get("ledger_saldos_por_lote", 0) > 0 or contagens.get("ledger_fifo_candidatos_avaliados", 0) > 0,
        "lote_3120_encontrado_estado_temporal": contagens.get("estado_lotes_por_data", 0) > 0 or contagens.get("estado_lotes_final", 0) > 0,
        "lote_3120_encontrado_saida": bool(lotes_saida) or contagens.get("saida_extrato_passado", 0) > 0,
        "origem_do_saldo_negativo_identificada": origem_saldo != "nao_identificada",
        "origem_do_saldo_negativo": origem_saldo,
        "saldo_negativo_evidencia": evid_saldo_negativo,
        "origem_da_exaustao_incorreta_identificada": origem_exaustao != "nao_identificada",
        "origem_da_exaustao_incorreta": origem_exaustao,
        "linha_saida_exaurido": row_exaurido,
        "origem_do_rendimento_negativo_identificada": origem_rendimento != "nao_identificada",
        "origem_do_rendimento_negativo": origem_rendimento,
        "rendimento_negativo_evidencia": evid_rendimento_negativo,
        "pagamentos_que_consumiram_lote_listados": len(pagamentos_lote) > 0,
        "qtd_pagamentos_ou_eventos_lote": len(pagamentos_lote),
        "pagamentos_ou_eventos_lote_amostra": pagamentos_lote[:20],
        "saldo_modelo_vs_saldo_app_comparado": saldo_modelo is not None,
        "saldo_modelo_atual_saida": saldo_modelo,
        "diferenca_saldo_app_menos_modelo": diferenca_app_modelo,
        "contagens_por_origem": contagens,
        "causa_classificada": causa_classificada,
        "hipotese_causa_principal": "replay_extrato_passado_consumo_excessivo_ou_ordem_intradiaria" if origem_saldo in {"extrato_passado_saida_ja_exibe_saldo_negativo", "replay_passado_ja_exibe_saldo_negativo"} else "pendente_classificacao_manual",
        "sem_alteracao_observavel": _iguais(saida_antes, saida_depois),
    }

    resultado["validacao_v4o_ok"] = all([
        resultado["lote_3120_encontrado_saida"],
        resultado["origem_do_saldo_negativo_identificada"],
        resultado["origem_da_exaustao_incorreta_identificada"],
        resultado["origem_do_rendimento_negativo_identificada"],
        resultado["pagamentos_que_consumiram_lote_listados"],
        resultado["saldo_modelo_vs_saldo_app_comparado"],
        resultado["sem_alteracao_observavel"],
    ])

    print("=== AUDITORIA LOTE 3120 MAI ESTADO TEMPORAL V4O ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_lote_3120_mai_estado_temporal_v4o_resumo.csv",
            index=False,
        )
        pd.DataFrame([
            {"origem": origem, "qtd": qtd}
            for origem, qtd in contagens.items()
        ]).to_csv(saida_dir / "auditoria_lote_3120_mai_estado_temporal_v4o_contagens.csv", index=False)
        detalhado = []
        for origem, rows in origens.items():
            for row in rows:
                item = {"origem": origem}
                item.update(row)
                detalhado.append(item)
        pd.DataFrame(detalhado).to_csv(
            saida_dir / "auditoria_lote_3120_mai_estado_temporal_v4o_linhas.csv",
            index=False,
        )

    return 0 if resultado["validacao_v4o_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
