from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

IN_DIR = RAIZ / "saidas" / "diagnostico" / "v17_a0_2"
OUT_DIR = RAIZ / "saidas" / "diagnostico" / "v17_a0_3"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARQ_IN_ABAS = IN_DIR / "v17_a0_2_classificacao_abas.csv"
ARQ_IN_CAMPOS = IN_DIR / "v17_a0_2_classificacao_campos.csv"
ARQ_IN_FONTES_ANTIGAS = IN_DIR / "v17_a0_2_classificacao_fontes_antigas.csv"
ARQ_IN_FONTES_V17 = IN_DIR / "v17_a0_2_classificacao_fontes_v17.csv"
ARQ_IN_SALDO = IN_DIR / "v17_a0_2_classificacao_saldo_gastos.csv"
ARQ_IN_LOTES_CAIXA = IN_DIR / "v17_a0_2_classificacao_lotes_caixa_disponivel.csv"
ARQ_IN_SWITCHING = IN_DIR / "v17_a0_2_classificacao_switching.csv"
ARQ_IN_SAIDA = IN_DIR / "v17_a0_2_classificacao_saida.csv"
ARQ_IN_MATRIZ = IN_DIR / "v17_a0_2_matriz_final_decisao.csv"

ARQ_OUT_MATRIZ = OUT_DIR / "v17_a0_3_matriz_cirurgica_implementacao_futura.csv"
ARQ_OUT_SEQUENCIA = OUT_DIR / "v17_a0_3_sequencia_recomendada.csv"
ARQ_OUT_GUARDRAILS = OUT_DIR / "v17_a0_3_guardrails_nao_funcionais.csv"
ARQ_OUT_RESUMO = OUT_DIR / "v17_a0_3_resumo.csv"

SEVERIDADE_ORDEM = {
    "ok": 0,
    "baixo": 1,
    "medio": 2,
    "alto": 3,
    "bloqueante": 4,
}

GRUPO_CONFIG = "Grupo 1 — pré-requisitos de config/canonização"
GRUPO_DADOS = "Grupo 2 — semântica de dados"
GRUPO_SAIDA = "Grupo 3 — arquitetura de saída"


def _ler_csv(caminho: Path, colunas: list[str]) -> pd.DataFrame:
    if not caminho.exists():
        return pd.DataFrame(columns=colunas)
    try:
        df = pd.read_csv(caminho)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    return df


def _gravar_csv(df: pd.DataFrame, caminho: Path, colunas: list[str]) -> None:
    if df is None or df.empty:
        df = pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    df[colunas].to_csv(caminho, index=False)


def _txt(v: Any) -> str:
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass
    return str(v).strip()


def _bool(v: Any) -> bool:
    s = _txt(v).lower()
    return s in {"true", "1", "1.0", "sim", "s", "yes", "y"}


def _num(v: Any) -> float:
    if v is None:
        return 0.0
    try:
        if pd.isna(v):
            return 0.0
    except Exception:
        pass
    try:
        return float(v)
    except Exception:
        return 0.0


def _max_severidade(valores: list[str]) -> str:
    if not valores:
        return "ok"
    return max(valores, key=lambda v: SEVERIDADE_ORDEM.get(v, 0))


def _prioridade(severidade: str, bloqueia: bool, impacto: str) -> str:
    sev = SEVERIDADE_ORDEM.get(severidade, 0)
    if bloqueia and sev >= 4:
        return "P0"
    if bloqueia and sev >= 3:
        return "P1"
    if impacto == "alto" or sev >= 3:
        return "P2"
    if sev == 2:
        return "P3"
    return "P4"


def _adicionar_linha(
    linhas: list[dict[str, Any]],
    grupo: str,
    eixo: str,
    item: str,
    classe: str,
    severidade: str,
    bloqueia: bool,
    acao: str,
    dependencia: str,
    regra_execucao: str,
    risco_se_ignorado: str,
    criterio_conclusao: str,
    origem_csv: str,
    impacto: str = "alto",
) -> None:
    linhas.append({
        "grupo_priorizacao": grupo,
        "eixo": eixo,
        "item": item,
        "classe_bloqueio": classe,
        "severidade": severidade,
        "bloqueia_v17_a_funcional": bool(bloqueia),
        "prioridade": _prioridade(severidade, bool(bloqueia), impacto),
        "acao_cirurgica_futura": acao,
        "dependencia_previa": dependencia,
        "regra_execucao_futura": regra_execucao,
        "risco_se_ignorado": risco_se_ignorado,
        "criterio_conclusao": criterio_conclusao,
        "origem_csv": origem_csv,
    })


def _processar_abas(df: pd.DataFrame, linhas: list[dict[str, Any]]) -> None:
    for _, r in df.iterrows():
        if not _bool(r.get("bloqueia_v17_a_funcional")):
            continue
        aba = _txt(r.get("aba_normativa")) or _txt(r.get("familia_v17"))
        _adicionar_linha(
            linhas,
            GRUPO_CONFIG,
            "abas_config",
            aba,
            _txt(r.get("classe_bloqueio_v17_a0_2")),
            _txt(r.get("severidade")),
            True,
            "incluir familia no config apenas como leitura/canonizacao, sem acionar motor",
            "nenhuma; primeiro pre-requisito estrutural",
            "alterar somente config/aliases em etapa futura controlada; nao mudar decisao economica",
            "aba existente continuara lida fisicamente mas invisivel para a semantica V17",
            "aba aparece como reconhecida no config e preserva nome normativo",
            ARQ_IN_ABAS.name,
            impacto="alto",
        )


def _processar_campos(df: pd.DataFrame, linhas: list[dict[str, Any]]) -> None:
    for _, r in df.iterrows():
        if not _bool(r.get("bloqueia_v17_a_funcional")):
            continue
        familia = _txt(r.get("familia_v17"))
        campo = _txt(r.get("campo_normativo"))
        _adicionar_linha(
            linhas,
            GRUPO_CONFIG,
            "campos_aliases",
            f"{familia}.{campo}",
            _txt(r.get("classe_bloqueio_v17_a0_2")),
            _txt(r.get("severidade")),
            True,
            "mapear alias no config ou confirmar ausencia real da coluna antes de qualquer uso funcional",
            "abas_config reconhecidas",
            "somente mapeamento declarativo; nao preencher valores nem inferir regra economica",
            "campo critico pode ser tratado por posicao/nome implicito e gerar classificacao incorreta",
            "campo critico fica reconhecido ou documentado como ausente real com decisao explicita",
            ARQ_IN_CAMPOS.name,
            impacto="alto",
        )


def _processar_fontes_v17(df: pd.DataFrame, linhas: list[dict[str, Any]]) -> None:
    for _, r in df.iterrows():
        if not _bool(r.get("bloqueia_v17_a_funcional")):
            continue
        fonte = _txt(r.get("fonte_v17"))
        grupo = GRUPO_CONFIG
        dependencia = "abas_config e campos_aliases"
        if fonte in {"pagamento_por_saldo", "pagamento_por_lote", "lote_caixa_disponivel", "switching_origem", "switching_destino_materializado", "entrada_externa_salario"}:
            grupo = GRUPO_DADOS
            dependencia = "config/canonizacao minima concluida"
        _adicionar_linha(
            linhas,
            grupo,
            "tipos_v17_explicitos",
            fonte,
            _txt(r.get("classe_bloqueio_v17_a0_2")),
            _txt(r.get("severidade")),
            True,
            "criar tipo canonico explicito em camada diagnostica/adaptadora antes de usar no motor",
            dependencia,
            "introduzir tipo sem alterar escolha de fonte, ranking, switching funcional ou saida canonica",
            "motor continuara operando com taxonomia antiga sem contrato semantico V17",
            "tipo V17 aparece em matriz canonica e pode ser auditado sem acionar decisao funcional",
            ARQ_IN_FONTES_V17.name,
            impacto="alto",
        )


def _processar_fontes_antigas(df: pd.DataFrame, linhas: list[dict[str, Any]]) -> None:
    for _, r in df.iterrows():
        if not _bool(r.get("bloqueia_v17_a_funcional")):
            continue
        fonte = _txt(r.get("fonte_antiga"))
        alvo = _txt(r.get("tipo_v17_alvo"))
        _adicionar_linha(
            linhas,
            GRUPO_CONFIG,
            "traducao_taxonomia_antiga",
            fonte,
            _txt(r.get("classe_bloqueio_v17_a0_2")),
            _txt(r.get("severidade")),
            True,
            f"definir adapter diagnostico {fonte} -> {alvo}, sem substituir ainda o motor",
            "tipos_v17_explicitos criados",
            "mapear de forma auditavel; proibido apagar fonte antiga antes de validar equivalencia",
            "substituicao direta pode quebrar pagamentos, recebidos ou switching sem rastreabilidade",
            "cada fonte antiga tem destino V17 declarado, contagem de ocorrencias e status de migracao",
            ARQ_IN_FONTES_ANTIGAS.name,
            impacto="alto",
        )


def _processar_saldo(df: pd.DataFrame, linhas: list[dict[str, Any]]) -> None:
    total = len(df)
    bloqueantes = int(df["bloqueia_v17_a_funcional"].astype(bool).sum()) if "bloqueia_v17_a_funcional" in df.columns else 0
    if total == 0:
        return
    severidade = _max_severidade([_txt(v) for v in df.get("severidade", pd.Series(dtype=str)).tolist()])
    _adicionar_linha(
        linhas,
        GRUPO_DADOS,
        "saldo_em_gastos",
        f"{total} ocorrencias; {bloqueantes} bloqueantes",
        "pagamento_por_saldo_historico",
        severidade,
        bloqueantes > 0,
        "criar classificacao unica Saldo = pagamento_por_saldo antes de qualquer replay funcional V17",
        "tipos_v17_explicitos e aliases de Todos os Gastos",
        "resolver por regra semantica geral, nunca por correcao manual dos 51 registros",
        "Saldo pode ser tratado como produto/lote/fonte indevida e contaminar estado temporal",
        "todas as ocorrencias de Saldo aparecem como pagamento_por_saldo sem busca na Carteira/Inventario",
        ARQ_IN_SALDO.name,
        impacto="alto",
    )


def _processar_lotes_caixa(df: pd.DataFrame, linhas: list[dict[str, Any]]) -> None:
    total = len(df)
    if total == 0:
        return
    bloqueantes = int(df["bloqueia_v17_a_funcional"].astype(bool).sum()) if "bloqueia_v17_a_funcional" in df.columns else 0
    severidade = _max_severidade([_txt(v) for v in df.get("severidade", pd.Series(dtype=str)).tolist()])
    _adicionar_linha(
        linhas,
        GRUPO_DADOS,
        "lote_caixa_disponivel",
        f"{total} candidato(s); {bloqueantes} bloqueante(s)",
        "lote_caixa_disponivel_valido_ou_ambiguo",
        severidade,
        bloqueantes > 0,
        "preservar lote caixa com Data Aplicacao/Investimento vazios e classificar como lote_caixa_disponivel",
        "tipos_v17_explicitos e aliases de Inventario de Lotes",
        "proibido preencher Data Aplicacao artificialmente para esses casos",
        "caixa disponivel pode virar lote investido ficticio e alterar elegibilidade/rendimento",
        "candidato classificado sem mutar Data Aplicacao nem Investimento",
        ARQ_IN_LOTES_CAIXA.name,
        impacto="alto",
    )


def _processar_switching(df: pd.DataFrame, linhas: list[dict[str, Any]]) -> None:
    total = len(df)
    if total == 0:
        return
    bloqueantes = int(df["bloqueia_v17_a_funcional"].astype(bool).sum()) if "bloqueia_v17_a_funcional" in df.columns else 0
    severidade = _max_severidade([_txt(v) for v in df.get("severidade", pd.Series(dtype=str)).tolist()])
    _adicionar_linha(
        linhas,
        GRUPO_DADOS,
        "switching_entrada",
        f"{total} candidato(s); {bloqueantes} bloqueante(s)",
        "switching_destino_materializavel_ou_risco_dupla_contagem",
        severidade,
        bloqueantes > 0,
        "materializar diagnostico switching_origem/switching_destino_materializado e reconciliar com Inventario",
        "config/aliases de Switching e tipos V17 explicitos",
        "usar Valor Liquido Migrado como campo financeiro canonico; nao usar shadow como fonte primaria V17",
        "destino de switching pode ser ignorado ou contado duas vezes",
        "cada Lote ID Depois tem status materializavel/reconciliado/insuficiente",
        ARQ_IN_SWITCHING.name,
        impacto="alto",
    )


def _processar_saida(df: pd.DataFrame, linhas: list[dict[str, Any]]) -> None:
    if df.empty:
        return
    grupos = df.groupby("classe_bloqueio_v17_a0_2", dropna=False)
    for classe, sub in grupos:
        total = len(sub)
        bloqueantes = int(sub["bloqueia_v17_a_funcional"].astype(bool).sum()) if "bloqueia_v17_a_funcional" in sub.columns else 0
        severidade = _max_severidade([_txt(v) for v in sub.get("severidade", pd.Series(dtype=str)).tolist()])
        classe_txt = _txt(classe)
        if classe_txt == "inferencia_ou_complementacao_operacional_na_saida":
            acao = "mover inferencia/complementacao para estado temporal ou motor antes da V17-A funcional"
            criterio = "nenhum fallback/complementacao operacional permanece necessario na saida"
        elif classe_txt == "campo_operacional_financeiro_alteravel_na_saida":
            acao = "separar renderizacao legitima de alteracao operacional de valores financeiros"
            criterio = "campos financeiros da saida derivam diretamente de estado ja decidido"
        elif classe_txt == "normalizacao_de_status_na_saida":
            acao = "validar se normalizacao apenas renderiza status ou se corrige falha operacional"
            criterio = "normalizacao vira formatacao ou migra para estado temporal"
        elif classe_txt == "representacao_sintetica_de_switching_na_saida":
            acao = "mover representacao sintetica de switching para estado temporal canonico"
            criterio = "saida apenas exibe switching ja materializado/reconciliado"
        else:
            acao = "triagem manual para classificar como visual, transitorio aceitavel ou proibido"
            criterio = "todos os pontos ficam classificados em permitido/transitorio/migrar/proibido"
        _adicionar_linha(
            linhas,
            GRUPO_SAIDA,
            "saida_canonica",
            f"{classe_txt}: {total} ponto(s); {bloqueantes} bloqueante(s)",
            classe_txt,
            severidade,
            bloqueantes > 0,
            acao,
            "estado temporal/canonizacao V17 definidos como fonte de verdade",
            "nao alterar saida_canonica nesta fase; apenas priorizar pontos para refatoracao futura",
            "saida pode continuar corrigindo/inferindo decisao operacional fora do motor",
            criterio,
            ARQ_IN_SAIDA.name,
            impacto="alto" if bloqueantes > 0 else "medio",
        )


def _gerar_sequencia(matriz: pd.DataFrame) -> pd.DataFrame:
    linhas = [
        {
            "ordem": 1,
            "microetapa_futura": "V17-A1",
            "grupo_priorizacao": GRUPO_CONFIG,
            "objetivo": "canonizar config e aliases das cinco familias de entrada",
            "pre_condicao": "V17-A0.3 aprovada",
            "escopo_permitido": "config/aliases e testes diagnosticos de leitura",
            "escopo_proibido": "motor, ranking, switching funcional, saida_canonica, contrato e modelo",
            "criterio_saida": "Salarios e Switching reconhecidos; campos criticos classificados",
        },
        {
            "ordem": 2,
            "microetapa_futura": "V17-A2",
            "grupo_priorizacao": GRUPO_DADOS,
            "objetivo": "criar taxonomia V17 diagnostica e adapters nao funcionais",
            "pre_condicao": "config/aliases canonizados",
            "escopo_permitido": "classificadores/adapters diagnosticos sem consumo pelo motor",
            "escopo_proibido": "substituir decisao_local_v1 ou recomputacao temporal",
            "criterio_saida": "tipos V17 explicitos auditaveis e mapeamento antigo->V17",
        },
        {
            "ordem": 3,
            "microetapa_futura": "V17-A3",
            "grupo_priorizacao": GRUPO_DADOS,
            "objetivo": "classificar Saldo, lote_caixa_disponivel e Switching de entrada",
            "pre_condicao": "taxonomia V17 diagnostica existente",
            "escopo_permitido": "matrizes canonicas de dados e reconciliacao diagnostica",
            "escopo_proibido": "aplicar recomendacao funcional ou alterar pagamentos",
            "criterio_saida": "Saldo nao busca Carteira/Inventario; lote caixa preservado; switching reconciliado",
        },
        {
            "ordem": 4,
            "microetapa_futura": "V17-A4",
            "grupo_priorizacao": GRUPO_SAIDA,
            "objetivo": "triagem fina de saida_canonica por tipo de risco",
            "pre_condicao": "estado/canonizacao V17 diagnosticos definidos",
            "escopo_permitido": "classificacao de pontos de saida e desenho de migracao futura",
            "escopo_proibido": "limpar, corrigir ou completar saida em producao",
            "criterio_saida": "cada ponto de saida classificado como visual/transitorio/migrar/proibido",
        },
        {
            "ordem": 5,
            "microetapa_futura": "V17-B0",
            "grupo_priorizacao": "ponte para implementacao funcional futura",
            "objetivo": "decidir se ha base suficiente para abrir primeira integracao funcional controlada",
            "pre_condicao": "V17-A1 a V17-A4 aprovadas por diagnostico",
            "escopo_permitido": "planejamento da primeira mudanca funcional minima",
            "escopo_proibido": "mudar motor sem matriz de equivalencia e rollback",
            "criterio_saida": "bloqueios P0/P1 zerados ou justificados com guardrail explicito",
        },
    ]
    return pd.DataFrame(linhas)


def _gerar_guardrails() -> pd.DataFrame:
    linhas = [
        {
            "id_guardrail": "G1",
            "regra": "Nao alterar motor economico durante V17-A0.x",
            "motivo": "os bloqueios ainda sao de leitura, canonizacao, semantica de dados e arquitetura de saida",
        },
        {
            "id_guardrail": "G2",
            "regra": "Nao tratar Saldo como produto, lote investido ou fonte resgatavel",
            "motivo": "Saldo em Todos os Gastos representa pagamento_por_saldo historico/operacional",
        },
        {
            "id_guardrail": "G3",
            "regra": "Nao preencher Data Aplicacao artificialmente para lote_caixa_disponivel",
            "motivo": "essa mutacao apaga a diferenca entre caixa disponivel e lote investido",
        },
        {
            "id_guardrail": "G4",
            "regra": "Nao usar shadow/recomendacao como fonte primaria da aba Switching V17",
            "motivo": "Switching deve ser canonizado a partir da entrada e reconciliado com Inventario",
        },
        {
            "id_guardrail": "G5",
            "regra": "Nao corrigir decisao operacional em saida_canonica",
            "motivo": "a saida deve renderizar estado decidido, nao inferir, limpar ou completar regra economica",
        },
        {
            "id_guardrail": "G6",
            "regra": "Nao substituir taxonomia antiga diretamente no motor sem adapter auditavel",
            "motivo": "substituicao direta pode quebrar decisao_local_v1, ledger e recomputacao temporal",
        },
    ]
    return pd.DataFrame(linhas)


def main() -> int:
    df_abas = _ler_csv(ARQ_IN_ABAS, ["familia_v17", "aba_normativa", "aba_encontrada_planilha", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    df_campos = _ler_csv(ARQ_IN_CAMPOS, ["familia_v17", "aba_normativa", "campo_normativo", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    df_fontes_antigas = _ler_csv(ARQ_IN_FONTES_ANTIGAS, ["fonte_antiga", "ocorrencias_codigo", "classe_bloqueio_v17_a0_2", "tipo_v17_alvo", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    df_fontes_v17 = _ler_csv(ARQ_IN_FONTES_V17, ["fonte_v17", "ocorrencias_codigo", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    df_saldo = _ler_csv(ARQ_IN_SALDO, ["despesa_id", "data", "valor", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    df_lotes_caixa = _ler_csv(ARQ_IN_LOTES_CAIXA, ["lote_id", "data_recebimento", "valor_original", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    df_switching = _ler_csv(ARQ_IN_SWITCHING, ["lote_id_antes", "lote_id_depois", "valor_liquido_migrado", "destino_tambem_no_inventario", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])
    df_saida = _ler_csv(ARQ_IN_SAIDA, ["arquivo", "linha", "termo_detectado", "tipo_ponto", "trecho", "classe_bloqueio_v17_a0_2", "severidade", "bloqueia_v17_a_funcional", "acao_recomendada"])

    linhas: list[dict[str, Any]] = []
    _processar_abas(df_abas, linhas)
    _processar_campos(df_campos, linhas)
    _processar_fontes_v17(df_fontes_v17, linhas)
    _processar_fontes_antigas(df_fontes_antigas, linhas)
    _processar_saldo(df_saldo, linhas)
    _processar_lotes_caixa(df_lotes_caixa, linhas)
    _processar_switching(df_switching, linhas)
    _processar_saida(df_saida, linhas)

    matriz = pd.DataFrame(linhas)
    if not matriz.empty:
        matriz["prioridade_ordem"] = matriz["prioridade"].map({"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}).fillna(9).astype(int)
        matriz["severidade_ordem"] = matriz["severidade"].map(SEVERIDADE_ORDEM).fillna(0).astype(int)
        matriz = matriz.sort_values(["prioridade_ordem", "severidade_ordem", "grupo_priorizacao", "eixo", "item"], ascending=[True, False, True, True, True])
        matriz = matriz.drop(columns=["prioridade_ordem", "severidade_ordem"])

    colunas_matriz = [
        "grupo_priorizacao", "eixo", "item", "classe_bloqueio", "severidade",
        "bloqueia_v17_a_funcional", "prioridade", "acao_cirurgica_futura",
        "dependencia_previa", "regra_execucao_futura", "risco_se_ignorado",
        "criterio_conclusao", "origem_csv",
    ]
    _gravar_csv(matriz, ARQ_OUT_MATRIZ, colunas_matriz)

    sequencia = _gerar_sequencia(matriz)
    _gravar_csv(sequencia, ARQ_OUT_SEQUENCIA, [
        "ordem", "microetapa_futura", "grupo_priorizacao", "objetivo", "pre_condicao",
        "escopo_permitido", "escopo_proibido", "criterio_saida",
    ])

    guardrails = _gerar_guardrails()
    _gravar_csv(guardrails, ARQ_OUT_GUARDRAILS, ["id_guardrail", "regra", "motivo"])

    if matriz.empty:
        resumo_linhas = [
            {"metrica": "decisao_global_v17_a0_3", "valor": "sem_bloqueios_priorizados", "status": "revisar_entrada", "observacao": "nenhuma linha gerada a partir da V17-A0.2"},
        ]
    else:
        resumo_base = matriz.groupby(["grupo_priorizacao", "prioridade"], dropna=False).size().reset_index(name="qtd")
        resumo_linhas = []
        for _, r in resumo_base.iterrows():
            resumo_linhas.append({
                "metrica": f"{r['grupo_priorizacao']}|{r['prioridade']}",
                "valor": int(r["qtd"]),
                "status": "priorizado",
                "observacao": "contagem por grupo e prioridade",
            })
        resumo_linhas.append({
            "metrica": "decisao_global_v17_a0_3",
            "valor": "manter_bloqueio_da_v17_a_funcional",
            "status": "bloqueio_preventivo_confirmado",
            "observacao": "abrir primeiro V17-A1 de config/canonizacao, nao V17-A funcional",
        })
        resumo_linhas.append({
            "metrica": "total_itens_priorizados",
            "valor": int(len(matriz)),
            "status": "info",
            "observacao": "matriz cirurgica gerada a partir da V17-A0.2",
        })
    resumo = pd.DataFrame(resumo_linhas)
    _gravar_csv(resumo, ARQ_OUT_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-A0.3 — PRIORIZACAO CIRURGICA DOS BLOQUEIOS ===")
    print(f"input_dir={IN_DIR}")
    print(f"output_dir={OUT_DIR}")
    print("decisao_global_v17_a0_3=manter_bloqueio_da_v17_a_funcional")
    print(f"total_itens_priorizados={len(matriz)}")
    if not matriz.empty:
        for grupo, sub in matriz.groupby("grupo_priorizacao", dropna=False):
            contagens = sub["prioridade"].value_counts().sort_index().to_dict()
            print(f"{grupo}: total={len(sub)}; prioridades={contagens}")
    print("proxima_microetapa_recomendada=V17-A1_config_canonizacao_sem_motor")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
