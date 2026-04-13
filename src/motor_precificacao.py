from __future__ import annotations

import math

import pandas as pd

from tipos import ConfigProjeto, ResultadoAvaliacaoProduto, ResultadoPrecificacao


def obter_taxa_indexador_anual(indexador: str, config: ConfigProjeto) -> float:
    normalized = str(indexador).strip().lower()
    if normalized == "cdi":
        return config.premissas_mercado.cdi_anual_modelo
    if normalized == "selic":
        return config.premissas_mercado.selic_anual_modelo
    if normalized == "ipca":
        return config.premissas_mercado.ipca_anual_modelo
    if normalized == "prefixado":
        return 0.0
    raise ValueError(f"Indexador não suportado na fase v1: {indexador}")



def obter_base_dias(indexador: str, config: ConfigProjeto) -> int:
    normalized = str(indexador).strip().lower()
    convencao = config.execucao.convencao_dias_ano
    if normalized == "cdi":
        return convencao["cdi"]
    if normalized == "selic":
        return convencao["selic"]
    if normalized == "ipca":
        return convencao["ipca"]
    if normalized == "prefixado":
        return convencao["prefixado"]
    raise ValueError(f"Base de dias não suportada para indexador: {indexador}")



def calcular_taxa_efetiva_anual_produto(carteira: pd.Series, config: ConfigProjeto) -> float:
    indexador = str(carteira["indexador"]).strip()
    taxa_base = float(carteira["taxa_base"])
    taxa_bonus = float(carteira["taxa_bonus"])

    if indexador.lower() == "prefixado":
        return taxa_base + taxa_bonus

    taxa_indexador = obter_taxa_indexador_anual(indexador, config)
    return taxa_indexador * (taxa_base + taxa_bonus)


def calcular_taxa_efetiva_anual_produto_sem_bonus(carteira: pd.Series, config: ConfigProjeto) -> float:
    indexador = str(carteira["indexador"]).strip()
    taxa_base = float(carteira["taxa_base"])

    if indexador.lower() == "prefixado":
        return taxa_base

    taxa_indexador = obter_taxa_indexador_anual(indexador, config)
    return taxa_indexador * taxa_base


def calcular_taxa_efetiva_anual_vigente_produto(
    carteira: pd.Series,
    data_entrada_produto: pd.Timestamp,
    data_referencia: pd.Timestamp,
    config: ConfigProjeto,
) -> float:
    """Taxa vigente no instante de referência.

    Durante a janela de bônus, considera a taxa promocional (taxa_bonus) quando ela
    é positiva. Fora dessa janela, usa a taxa base do produto.
    """
    indexador = str(carteira["indexador"]).strip()
    taxa_base = float(carteira.get("taxa_base", 0.0) or 0.0)
    taxa_bonus = float(carteira.get("taxa_bonus", 0.0) or 0.0)
    dias_bonus_restantes = calcular_dias_bonus_restantes(data_entrada_produto, data_referencia, carteira)
    taxa_vigente = taxa_bonus if dias_bonus_restantes > 0 and taxa_bonus > 0 else taxa_base

    if indexador.lower() == "prefixado":
        return taxa_vigente

    taxa_indexador = obter_taxa_indexador_anual(indexador, config)
    return taxa_indexador * taxa_vigente


def calcular_taxa_efetiva_anual_bonus_puro(carteira: pd.Series, config: ConfigProjeto) -> float:
    """Taxa promocional pura usada em comparações estruturais.

    Aqui `taxa_bonus` é interpretada como a taxa vigente do período promocional,
    e não como incremento aditivo sobre a taxa base.
    """
    indexador = str(carteira["indexador"]).strip()
    taxa_bonus = float(carteira.get("taxa_bonus", 0.0) or 0.0)
    taxa_base = float(carteira.get("taxa_base", 0.0) or 0.0)
    taxa = taxa_bonus if taxa_bonus > 0 else taxa_base
    if indexador.lower() == "prefixado":
        return taxa
    return obter_taxa_indexador_anual(indexador, config) * taxa


def projetar_valor_bruto_com_regime_promocional(
    valor_inicial_centavos: int,
    carteira: pd.Series,
    data_inicio: pd.Timestamp,
    data_fim: pd.Timestamp,
    data_entrada_produto: pd.Timestamp,
    config: ConfigProjeto,
) -> int:
    """Projeção segmentada usando bônus como taxa promocional pura.

    Esta rotina é reservada para checagens estruturais de dominância da origem.
    """
    data_inicio = pd.Timestamp(data_inicio).normalize()
    data_fim = pd.Timestamp(data_fim).normalize()
    data_entrada_produto = pd.Timestamp(data_entrada_produto).normalize()
    if data_fim <= data_inicio:
        return int(valor_inicial_centavos)

    indexador = str(carteira["indexador"])
    base_dias = obter_base_dias(indexador, config)
    dias_bonus = int(carteira.get("dias_bonus", 0) or 0)
    if dias_bonus <= 0:
        taxa = calcular_taxa_efetiva_anual_produto_sem_bonus(carteira, config)
        return projetar_valor_bruto(valor_inicial_centavos, taxa, data_inicio, data_fim, base_dias)

    fim_bonus = data_entrada_produto + pd.Timedelta(days=dias_bonus)
    fim_trecho_bonus = min(data_fim, fim_bonus)
    valor = int(valor_inicial_centavos)

    if fim_trecho_bonus > data_inicio:
        taxa_bonus_pura = calcular_taxa_efetiva_anual_bonus_puro(carteira, config)
        valor = projetar_valor_bruto(valor, taxa_bonus_pura, data_inicio, fim_trecho_bonus, base_dias)

    if data_fim > fim_trecho_bonus:
        taxa_base = calcular_taxa_efetiva_anual_produto_sem_bonus(carteira, config)
        valor = projetar_valor_bruto(valor, taxa_base, fim_trecho_bonus, data_fim, base_dias)

    return int(valor)


def calcular_dias_bonus_restantes(
    data_entrada_produto: pd.Timestamp,
    data_referencia: pd.Timestamp,
    carteira: pd.Series,
) -> int:
    dias_bonus = int(carteira.get("dias_bonus", 0) or 0)
    if dias_bonus <= 0:
        return 0
    inicio = pd.Timestamp(data_entrada_produto).normalize()
    referencia = pd.Timestamp(data_referencia).normalize()
    dias_decorridos = max((referencia - inicio).days, 0)
    return max(dias_bonus - dias_decorridos, 0)


def projetar_valor_bruto_com_bonus_segmentado(
    valor_inicial_centavos: int,
    carteira: pd.Series,
    data_inicio: pd.Timestamp,
    data_fim: pd.Timestamp,
    data_entrada_produto: pd.Timestamp,
    config: ConfigProjeto,
) -> int:
    data_inicio = pd.Timestamp(data_inicio).normalize()
    data_fim = pd.Timestamp(data_fim).normalize()
    data_entrada_produto = pd.Timestamp(data_entrada_produto).normalize()
    if data_fim <= data_inicio:
        return int(valor_inicial_centavos)

    indexador = str(carteira["indexador"])
    base_dias = obter_base_dias(indexador, config)
    dias_bonus = int(carteira.get("dias_bonus", 0) or 0)
    if dias_bonus <= 0:
        taxa = calcular_taxa_efetiva_anual_produto_sem_bonus(carteira, config)
        return projetar_valor_bruto(valor_inicial_centavos, taxa, data_inicio, data_fim, base_dias)

    fim_bonus = data_entrada_produto + pd.Timedelta(days=dias_bonus)
    fim_trecho_bonus = min(data_fim, fim_bonus)
    valor = int(valor_inicial_centavos)

    if fim_trecho_bonus > data_inicio:
        taxa_bonus_total = calcular_taxa_efetiva_anual_produto(carteira, config)
        valor = projetar_valor_bruto(valor, taxa_bonus_total, data_inicio, fim_trecho_bonus, base_dias)

    if data_fim > fim_trecho_bonus:
        taxa_base = calcular_taxa_efetiva_anual_produto_sem_bonus(carteira, config)
        valor = projetar_valor_bruto(valor, taxa_base, fim_trecho_bonus, data_fim, base_dias)

    return int(valor)


def bonus_remanescente_domina_destino(
    lote: pd.Series,
    carteira_origem: pd.Series,
    carteira_destino: pd.Series,
    data_switching: pd.Timestamp,
    valor_transferido_centavos: int,
    config: ConfigProjeto,
) -> bool:
    data_switching = pd.Timestamp(data_switching).normalize()
    valor_transferido_centavos = int(valor_transferido_centavos)
    if valor_transferido_centavos <= 0:
        return False

    dias_bonus_restantes = calcular_dias_bonus_restantes(
        data_entrada_produto=pd.Timestamp(lote["data_entrada_lote"]).normalize(),
        data_referencia=data_switching,
        carteira=carteira_origem,
    )
    if dias_bonus_restantes <= 0:
        return False

    data_fim_comparacao = data_switching + pd.Timedelta(days=dias_bonus_restantes)
    valor_origem = projetar_valor_bruto_com_bonus_segmentado(
        valor_inicial_centavos=valor_transferido_centavos,
        carteira=carteira_origem,
        data_inicio=data_switching,
        data_fim=data_fim_comparacao,
        data_entrada_produto=pd.Timestamp(lote["data_entrada_lote"]).normalize(),
        config=config,
    )
    valor_destino = projetar_valor_bruto_com_bonus_segmentado(
        valor_inicial_centavos=valor_transferido_centavos,
        carteira=carteira_destino,
        data_inicio=data_switching,
        data_fim=data_fim_comparacao,
        data_entrada_produto=data_switching,
        config=config,
    )
    return int(valor_origem) > int(valor_destino)


def calcular_janela_dominancia_estrutural_dias(
    lote: pd.Series,
    carteira_origem: pd.Series,
    carteira_destino: pd.Series,
    data_switching: pd.Timestamp,
    config: ConfigProjeto,
) -> int:
    data_switching = pd.Timestamp(data_switching).normalize()
    dias_bonus_origem = calcular_dias_bonus_restantes(
        data_entrada_produto=pd.Timestamp(lote["data_entrada_lote"]).normalize(),
        data_referencia=data_switching,
        carteira=carteira_origem,
    )
    dias_bonus_destino = int(carteira_destino.get("dias_bonus", 0) or 0)
    janela_minima = int(config.politicas_modelo.janela_minima_dominancia_dias)
    return max(janela_minima, dias_bonus_origem, dias_bonus_destino)



def origem_domina_destino_estruturalmente(
    lote: pd.Series,
    carteira_origem: pd.Series,
    carteira_destino: pd.Series,
    data_switching: pd.Timestamp,
    valor_transferido_centavos: int,
    config: ConfigProjeto,
) -> bool:
    if not bool(config.politicas_modelo.bloquear_switch_se_origem_domina_destino):
        return False

    valor_transferido_centavos = int(valor_transferido_centavos)
    if valor_transferido_centavos <= 0:
        return False

    data_switching = pd.Timestamp(data_switching).normalize()
    data_entrada_origem = pd.Timestamp(lote["data_entrada_lote"]).normalize()
    janela_dias = calcular_janela_dominancia_estrutural_dias(
        lote=lote,
        carteira_origem=carteira_origem,
        carteira_destino=carteira_destino,
        data_switching=data_switching,
        config=config,
    )
    data_fim = data_switching + pd.Timedelta(days=janela_dias)

    taxa_origem_vigente = calcular_taxa_efetiva_anual_vigente_produto(
        carteira=carteira_origem,
        data_entrada_produto=data_entrada_origem,
        data_referencia=data_switching,
        config=config,
    )
    taxa_destino_vigente = calcular_taxa_efetiva_anual_vigente_produto(
        carteira=carteira_destino,
        data_entrada_produto=data_switching,
        data_referencia=data_switching,
        config=config,
    )
    spread_min = float(config.politicas_modelo.spread_minimo_dominancia_estrutural)
    if (taxa_origem_vigente - taxa_destino_vigente) < spread_min:
        return False

    valor_origem = projetar_valor_bruto_com_regime_promocional(
        valor_inicial_centavos=valor_transferido_centavos,
        carteira=carteira_origem,
        data_inicio=data_switching,
        data_fim=data_fim,
        data_entrada_produto=data_entrada_origem,
        config=config,
    )
    valor_destino = projetar_valor_bruto_com_regime_promocional(
        valor_inicial_centavos=valor_transferido_centavos,
        carteira=carteira_destino,
        data_inicio=data_switching,
        data_fim=data_fim,
        data_entrada_produto=data_switching,
        config=config,
    )
    return int(valor_origem) >= int(valor_destino)



def calcular_fator_acumulacao(
    taxa_anual: float,
    data_inicio: pd.Timestamp,
    data_fim: pd.Timestamp,
    base_dias: int,
) -> float:
    if data_fim <= data_inicio:
        return 1.0
    dias = max((data_fim - data_inicio).days, 0)
    return math.pow(1.0 + taxa_anual, dias / base_dias)



def projetar_valor_bruto(
    valor_inicial_centavos: int,
    taxa_efetiva_anual: float,
    data_inicio: pd.Timestamp,
    data_fim: pd.Timestamp,
    base_dias: int,
) -> int:
    fator = calcular_fator_acumulacao(taxa_efetiva_anual, data_inicio, data_fim, base_dias)
    return int(round(valor_inicial_centavos * fator))



def calcular_imposto_renda(
    valor_inicial_centavos: int,
    valor_bruto_centavos: int,
    data_inicio: pd.Timestamp,
    data_fim: pd.Timestamp,
    carteira: pd.Series,
    config: ConfigProjeto,
) -> int:
    if not config.tributacao.usar_ir or bool(carteira["flag_isento_ir"]):
        return 0

    rendimento = max(valor_bruto_centavos - valor_inicial_centavos, 0)
    if rendimento == 0:
        return 0

    dias_corridos = max((data_fim - data_inicio).days, 0)
    aliquota = 0.0
    for faixa in config.tributacao.faixas_ir:
        dias_max = faixa["dias_max"]
        if dias_max is None or dias_corridos <= dias_max:
            aliquota = float(faixa["aliquota"])
            break
    return int(round(rendimento * aliquota))



def calcular_iof(
    rendimento_centavos: int,
    dias_corridos: int,
    config: ConfigProjeto,
) -> int:
    if not config.tributacao.usar_iof or rendimento_centavos <= 0:
        return 0
    if dias_corridos <= 0 or dias_corridos > len(config.tributacao.tabela_iof):
        return 0
    aliquota = float(config.tributacao.tabela_iof[dias_corridos - 1])
    return int(round(rendimento_centavos * aliquota))



def calcular_custo_operacional(valor_movimento_centavos: int, carteira: pd.Series) -> int:
    _ = valor_movimento_centavos
    _ = carteira
    return 0



def calcular_data_elegivel_resgate(data_inicio: pd.Timestamp, carteira: pd.Series) -> pd.Timestamp:
    carencia_dias = int(carteira["carencia_dias"])
    return pd.Timestamp(data_inicio).normalize() + pd.Timedelta(days=carencia_dias)



def eh_elegivel_resgate(
    data_inicio: pd.Timestamp,
    data_referencia: pd.Timestamp,
    carteira: pd.Series,
) -> bool:
    return data_referencia >= calcular_data_elegivel_resgate(data_inicio, carteira)



def eh_elegivel_switching(
    data_inicio: pd.Timestamp,
    data_referencia: pd.Timestamp,
    carteira_origem: pd.Series,
) -> bool:
    return eh_elegivel_resgate(data_inicio, data_referencia, carteira_origem)



def projetar_saldo_bruto_lote_ate_data(
    valor_bruto_atual_centavos: int,
    carteira: pd.Series,
    data_inicio: pd.Timestamp,
    data_fim: pd.Timestamp,
    config: ConfigProjeto,
) -> int:
    taxa_efetiva = calcular_taxa_efetiva_anual_produto(carteira, config)
    base_dias = obter_base_dias(str(carteira["indexador"]), config)
    return projetar_valor_bruto(
        valor_inicial_centavos=valor_bruto_atual_centavos,
        taxa_efetiva_anual=taxa_efetiva,
        data_inicio=pd.Timestamp(data_inicio).normalize(),
        data_fim=pd.Timestamp(data_fim).normalize(),
        base_dias=base_dias,
    )



def calcular_valor_liquido_lote_bruto(
    valor_principal_centavos: int,
    valor_bruto_centavos: int,
    data_entrada_original: pd.Timestamp,
    data_referencia: pd.Timestamp,
    carteira: pd.Series,
    config: ConfigProjeto,
) -> tuple[int, int, int, int]:
    rendimento = max(valor_bruto_centavos - valor_principal_centavos, 0)
    dias_corridos = max((pd.Timestamp(data_referencia).normalize() - pd.Timestamp(data_entrada_original).normalize()).days, 0)
    ir = calcular_imposto_renda(
        valor_inicial_centavos=valor_principal_centavos,
        valor_bruto_centavos=valor_bruto_centavos,
        data_inicio=pd.Timestamp(data_entrada_original).normalize(),
        data_fim=pd.Timestamp(data_referencia).normalize(),
        carteira=carteira,
        config=config,
    )
    iof = calcular_iof(rendimento, dias_corridos, config)
    custo = calcular_custo_operacional(valor_bruto_centavos, carteira)
    valor_liquido = max(valor_bruto_centavos - ir - iof - custo, 0)
    return valor_liquido, ir, iof, custo



def precificar_lote_investido_na_data(
    lote: pd.Series,
    carteira: pd.Series,
    data_referencia: pd.Timestamp,
    config: ConfigProjeto,
) -> ResultadoPrecificacao:
    valor_bruto_atual = int(lote.get("valor_bruto_remanescente_centavos", lote["valor_saldo_centavos"]))
    valor_principal = int(lote.get("valor_principal_remanescente_centavos", lote["valor_saldo_centavos"]))
    data_inicio_projecao = pd.Timestamp(lote.get("data_ultima_atualizacao", lote["data_entrada_lote"])).normalize()
    data_entrada_original = pd.Timestamp(lote["data_entrada_lote"]).normalize()
    data_referencia = pd.Timestamp(data_referencia).normalize()

    valor_bruto = projetar_saldo_bruto_lote_ate_data(
        valor_bruto_atual_centavos=valor_bruto_atual,
        carteira=carteira,
        data_inicio=data_inicio_projecao,
        data_fim=data_referencia,
        config=config,
    )
    valor_liquido, ir, iof, custo = calcular_valor_liquido_lote_bruto(
        valor_principal_centavos=valor_principal,
        valor_bruto_centavos=valor_bruto,
        data_entrada_original=data_entrada_original,
        data_referencia=data_referencia,
        carteira=carteira,
        config=config,
    )
    rendimento = max(valor_bruto - valor_principal, 0)

    return ResultadoPrecificacao(
        id_lote=str(lote["id_lote"]),
        data_referencia=data_referencia,
        valor_bruto_centavos=valor_bruto,
        valor_liquido_centavos=valor_liquido,
        rendimento_bruto_centavos=rendimento,
        imposto_centavos=ir,
        iof_centavos=iof,
        custo_operacional_centavos=custo,
        elegivel_resgate=eh_elegivel_resgate(data_entrada_original, data_referencia, carteira),
        elegivel_switching=eh_elegivel_switching(data_entrada_original, data_referencia, carteira),
    )



def avaliar_aporte_em_carteira(
    valor_inicial_centavos: int,
    carteira_destino: pd.Series,
    data_aporte: pd.Timestamp,
    horizonte_final: pd.Timestamp,
    config: ConfigProjeto,
) -> ResultadoAvaliacaoProduto:
    taxa_efetiva = calcular_taxa_efetiva_anual_produto(carteira_destino, config)
    base_dias = obter_base_dias(str(carteira_destino["indexador"]), config)
    valor_bruto = projetar_valor_bruto(
        valor_inicial_centavos,
        taxa_efetiva,
        data_aporte,
        horizonte_final,
        base_dias,
    )
    ir = calcular_imposto_renda(
        valor_inicial_centavos,
        valor_bruto,
        data_aporte,
        horizonte_final,
        carteira_destino,
        config,
    )
    iof = calcular_iof(max(valor_bruto - valor_inicial_centavos, 0), max((horizonte_final - data_aporte).days, 0), config)
    custo = calcular_custo_operacional(valor_inicial_centavos, carteira_destino)
    valor_liquido = max(valor_bruto - ir - iof - custo, 0)

    return ResultadoAvaliacaoProduto(
        id_carteira=str(carteira_destino["id_carteira"]),
        data_inicio=pd.Timestamp(data_aporte).normalize(),
        data_fim=pd.Timestamp(horizonte_final).normalize(),
        valor_inicial_centavos=valor_inicial_centavos,
        valor_bruto_projetado_centavos=valor_bruto,
        valor_liquido_projetado_centavos=valor_liquido,
        imposto_centavos=ir,
        iof_centavos=iof,
        custo_operacional_centavos=custo,
        detalhe_formula="Fase v1: projeção simples por taxa efetiva anual e base de dias do indexador.",
    )
