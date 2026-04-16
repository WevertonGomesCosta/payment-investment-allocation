"""Núcleo financeiro mínimo do projeto.

Esta camada abre apenas as primitivas irreduzíveis do bloco 07:
- helpers fiscais/liquidez de baixo nível;
- classe `Lote`;
- criação de lote;
- atualização de saldo por dia de rendimento;
- fator líquido;
- execução de saque.

Ela NÃO implementa:
- vetorização/numba;
- solvers Pulp;
- scoring econômico final;
- engine completa de simulação;
- switching econômico;
- relatório financeiro atual.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Mapping, Optional

from nucleo.calendario_financeiro import (
    PacoteCalendarioFinanceiro,
    eh_dia_util_bancario,
    obter_taxa_dia_rendimento,
    proximo_dia_util_bancario_em_ou_apos,
)
from nucleo.carteira_canonica import PacoteCarteiraCanonica
from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.utilitarios_neutros import arredondar_monetario, limpar_texto, para_bool, para_float_monetario, para_int


@dataclass(slots=True)
class PacoteNucleoFinanceiroMinimo:
    lotes_financeiros: list['Lote']
    auditoria: dict[str, Any]
    validacao: dict[str, Any]


class Lote:
    def __init__(
        self,
        id_lote: str,
        data_aplicacao: date,
        valor_inicial: float,
        *,
        investimento: str = '',
        produto_key: Optional[str] = None,
        data_base_fiscal: Optional[date] = None,
        fator_acumulado_inicial: float = 1.0,
        principal_remanescente_inicial: Optional[float] = None,
        taxa_base_cdi: Optional[float] = None,
        taxa_bonus_cdi: Optional[float] = None,
        dias_bonus: Optional[int] = None,
        produto_isento_ir: bool = False,
        carencia_ate: Optional[date] = None,
        nao_disponivel_para_aporte: bool = False,
        situacao_investimento: str = '',
    ):
        self.id = str(id_lote).strip()
        self.data_aplicacao = data_aplicacao
        self.data_base_fiscal = data_base_fiscal if data_base_fiscal is not None else data_aplicacao
        self.valor_inicial = float(valor_inicial)
        self.saldo_bruto = float(valor_inicial)
        self.fator_acumulado = max(1.0, float(fator_acumulado_inicial))
        self.principal_remanescente = float(self.valor_inicial if principal_remanescente_inicial is None else principal_remanescente_inicial)
        self.esgotado = False
        self.vezes_usado = 0
        self.total_bruto_sacado = 0.0
        self.total_imposto_pago = 0.0
        self.total_liquido_sacado = 0.0
        self.taxa_base_cdi = float(1.0 if taxa_base_cdi is None else taxa_base_cdi)
        self.taxa_bonus_cdi = float(0.0 if taxa_bonus_cdi is None else taxa_bonus_cdi)
        self.dias_bonus = int(0 if dias_bonus is None else dias_bonus)
        self.investimento = str(investimento or '').strip()
        self.produto_key = produto_key
        self.produto_isento_ir = bool(produto_isento_ir)
        self.carencia_ate = carencia_ate
        self.nao_disponivel_para_aporte = bool(nao_disponivel_para_aporte)
        self.situacao_investimento = str(situacao_investimento or '').strip()

    def get_taxa_dia(self, data_atual: date, pacote_calendario: Optional[PacoteCalendarioFinanceiro] = None) -> float:
        idade = (data_atual - self.data_base_fiscal).days
        if self.taxa_bonus_cdi <= 0.0 or self.dias_bonus <= 0:
            return float(self.taxa_base_cdi)
        if idade < self.dias_bonus:
            return float(self.taxa_bonus_cdi)

        if pacote_calendario is not None:
            data_limite_bonus = self.data_base_fiscal + timedelta(days=self.dias_bonus)
            if not eh_dia_util_bancario(data_limite_bonus, pacote_calendario):
                data_fechamento_bonus = proximo_dia_util_bancario_em_ou_apos(data_limite_bonus, pacote_calendario)
                if data_atual == data_fechamento_bonus:
                    return float(self.taxa_bonus_cdi)

        return float(self.taxa_base_cdi)

    def atualizar_juros(self, data_atual: date, taxa_diaria_decimal: float, pacote_calendario: Optional[PacoteCalendarioFinanceiro] = None) -> None:
        if self.esgotado or data_atual <= self.data_aplicacao:
            return
        mult = self.get_taxa_dia(data_atual, pacote_calendario)
        if mult <= 0.0:
            return
        fator_dia = (1.0 + float(taxa_diaria_decimal)) ** mult
        # Mantém precisão interna ao longo do tempo; arredondamento monetário
        # fica restrito à exibição e aos movimentos financeiros.
        self.saldo_bruto = float(self.saldo_bruto) * fator_dia
        self.fator_acumulado *= fator_dia

    def get_fator_liquido(self, data_resgate: date, *, tabela_iof: Optional[list[float]] = None, faixas_ir: Optional[list[dict[str, Any]]] = None) -> float:
        dias_vida = (data_resgate - self.data_base_fiscal).days
        if dias_vida < 0:
            return 0.0
        return _fator_liquido(self.fator_acumulado, dias_vida, self.produto_isento_ir, tabela_iof=tabela_iof, faixas_ir=faixas_ir)

    def valor_liquido_hoje(self, data_hoje: date, *, tabela_iof: Optional[list[float]] = None, faixas_ir: Optional[list[dict[str, Any]]] = None) -> float:
        return arredondar_monetario(self.saldo_bruto * self.get_fator_liquido(data_hoje, tabela_iof=tabela_iof, faixas_ir=faixas_ir))

    def sacar(self, valor_bruto: float, *, tolerancia_monetaria: float = 0.01) -> float:
        if valor_bruto >= self.saldo_bruto - float(tolerancia_monetaria):
            sacado = arredondar_monetario(self.saldo_bruto)
            self.saldo_bruto = 0.0
            self.principal_remanescente = 0.0
            self.esgotado = True
            self.vezes_usado += 1
            self.total_bruto_sacado += sacado
            return sacado
        if self.saldo_bruto <= 0.0:
            return 0.0
        valor_bruto = arredondar_monetario(float(valor_bruto))
        saldo_antes = max(float(self.saldo_bruto), 0.0)
        proporcao_sacada = min(max((valor_bruto / saldo_antes), 0.0), 1.0) if saldo_antes > 0.0 else 1.0
        principal_sacado = round(self.principal_remanescente * proporcao_sacada, 10)
        self.principal_remanescente = max(round(self.principal_remanescente - principal_sacado, 10), 0.0)
        self.saldo_bruto = float(self.saldo_bruto) - float(valor_bruto)
        if self.saldo_bruto <= float(tolerancia_monetaria):
            self.saldo_bruto = 0.0
            self.principal_remanescente = 0.0
            self.esgotado = True
        self.vezes_usado += 1
        self.total_bruto_sacado += valor_bruto
        return valor_bruto


def _cfg_get(config: Mapping[str, Any], *caminho: str, padrao: Any = None) -> Any:
    atual: Any = config
    for chave in caminho:
        if not isinstance(atual, Mapping) or chave not in atual:
            return padrao
        atual = atual[chave]
    return atual


def _money_round_half_up(valor: float) -> float:
    return float(Decimal(str(float(valor or 0.0))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def construir_tabela_iof(config: Mapping[str, Any]) -> list[float]:
    tabela_cfg = list(_cfg_get(config, 'iof', 'tabela', padrao=[] ) or [])
    tabela: list[float] = []
    for item in tabela_cfg:
        tabela.append(float(para_float_monetario(item, 0.0)))
    if not tabela:
        return [0.0] * 30
    while len(tabela) < 30:
        tabela.append(tabela[-1])
    return tabela[:30]


def construir_faixas_ir(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    faixas = []
    for item in list(_cfg_get(config, 'ir', 'faixas', padrao=[]) or []):
        if not isinstance(item, Mapping):
            continue
        dias_max = item.get('dias_max')
        faixas.append({
            'dias_max': None if dias_max in (None, '') else int(dias_max),
            'aliquota': float(para_float_monetario(item.get('aliquota'), 0.0)),
        })
    if not faixas:
        faixas = [
            {'dias_max': 180, 'aliquota': 0.225},
            {'dias_max': 360, 'aliquota': 0.20},
            {'dias_max': 720, 'aliquota': 0.175},
            {'dias_max': None, 'aliquota': 0.15},
        ]
    return faixas


def _taxa_ir(dias: int, isento: bool = False, *, faixas_ir: Optional[list[dict[str, Any]]] = None) -> float:
    if isento:
        return 0.0
    faixas = faixas_ir or []
    for faixa in faixas:
        dias_max = faixa.get('dias_max')
        aliquota = float(faixa.get('aliquota', 0.0) or 0.0)
        if dias_max is None or dias <= int(dias_max):
            return aliquota
    return 0.15


def _taxa_iof(dias: int, *, tabela_iof: Optional[list[float]] = None) -> float:
    if dias < 0:
        return 0.0
    if dias >= 30:
        return 0.0
    tabela = tabela_iof or []
    if not tabela:
        return 0.0
    # A tabela regressiva do IOF é indexada por dia de vida começando em 1.
    # Como dias_vida aqui é contado em dias corridos inteiros (ex.: 7 dias ->
    # sétima linha da tabela), o índice correto é dias - 1. O mapeamento
    # anterior usava o próprio valor de dias e subestimava o IOF em resgates
    # curtos, especialmente nos lotes com poucos dias de vida.
    idx = min(max(int(dias) - 1, 0), len(tabela) - 1)
    return float(tabela[idx])


def _fator_liquido(
    fator_acumulado: float,
    dias_vida: int,
    isento: bool = False,
    *,
    tabela_iof: Optional[list[float]] = None,
    faixas_ir: Optional[list[dict[str, Any]]] = None,
) -> float:
    if fator_acumulado <= 1.0:
        return 1.0
    iof = _taxa_iof(dias_vida, tabela_iof=tabela_iof)
    ir = _taxa_ir(dias_vida, isento=isento, faixas_ir=faixas_ir)
    ratio_lucro = 1.0 - (1.0 / float(fator_acumulado))
    taxa_efetiva = iof + (1.0 - iof) * ir
    return max(1.0 - ratio_lucro * taxa_efetiva, 0.0)


def criar_lote_de_aporte(dt: date, val: float, id_l: str, meta: Optional[Mapping[str, Any]] = None) -> Lote:
    meta = dict(meta or {})
    return Lote(
        id_l,
        dt,
        val,
        investimento=limpar_texto(meta.get('investimento')),
        produto_key=limpar_texto(meta.get('produto_key')) or None,
        data_base_fiscal=meta.get('data_base_fiscal', dt),
        fator_acumulado_inicial=float(meta.get('fator_acumulado_inicial', 1.0) or 1.0),
        taxa_base_cdi=(1.0 if meta.get('taxa_base_cdi', 1.0) in (None, '') else float(meta.get('taxa_base_cdi', 1.0))),
        taxa_bonus_cdi=(0.0 if meta.get('taxa_bonus_cdi', 0.0) in (None, '') else float(meta.get('taxa_bonus_cdi', 0.0))),
        dias_bonus=(0 if meta.get('dias_bonus', 0) in (None, '') else int(meta.get('dias_bonus', 0))),
        principal_remanescente_inicial=float(meta.get('principal_remanescente', meta.get('principal_remanescente_inicial', float(val))) or float(val)),
        produto_isento_ir=bool(meta.get('produto_isento_ir', False)),
        carencia_ate=meta.get('carencia_ate'),
        nao_disponivel_para_aporte=bool(meta.get('nao_disponivel_para_aporte', False)),
        situacao_investimento=limpar_texto(meta.get('situacao_investimento')),
    )


def atualizar_saldo_lotes_no_dia(
    lotes_ativos: list[Lote],
    data_atual: date,
    pacote_calendario: PacoteCalendarioFinanceiro,
    *,
    serie_cdi: Optional[Mapping[date, Any]] = None,
    taxa_proj: Optional[float] = None,
    data_fechamento_referencia: Optional[date] = None,
) -> dict[str, Any]:
    if not lotes_ativos:
        return {'aplicado': False, 'fonte': 'sem_lotes', 'fallback': False, 'qtd_lotes_atualizados': 0}

    if taxa_proj is None:
        taxa_proj = float(pacote_calendario.taxa_dia_base)

    aplicar, taxa_dia, meta = obter_taxa_dia_rendimento(
        data_atual,
        pacote_calendario,
        serie_cdi=serie_cdi,
        taxa_proj=taxa_proj,
        data_fechamento_referencia=data_fechamento_referencia,
    )
    if not aplicar or taxa_dia is None:
        return {'aplicado': False, 'qtd_lotes_atualizados': 0, **meta}

    qtd_lotes_atualizados = 0
    for lote in lotes_ativos:
        if lote.esgotado or float(lote.saldo_bruto or 0.0) <= 0.0:
            continue
        lote.atualizar_juros(data_atual, taxa_dia, pacote_calendario)
        qtd_lotes_atualizados += 1

    return {
        'aplicado': True,
        'taxa_dia_decimal': float(taxa_dia),
        'qtd_lotes_atualizados': int(qtd_lotes_atualizados),
        **meta,
    }


def executar_saque_lote(
    lote: Lote,
    valor_liquido_alvo: float,
    data_atual: date,
    *,
    tabela_iof: Optional[list[float]] = None,
    faixas_ir: Optional[list[dict[str, Any]]] = None,
    tolerancia_monetaria: float = 0.01,
) -> Optional[dict[str, Any]]:
    saldo_antes = float(lote.saldo_bruto)
    fator = lote.get_fator_liquido(data_atual, tabela_iof=tabela_iof, faixas_ir=faixas_ir)
    if fator <= 0.0:
        return None
    liquido_total_disponivel = float(lote.valor_liquido_hoje(data_atual, tabela_iof=tabela_iof, faixas_ir=faixas_ir))
    if float(valor_liquido_alvo) >= max(liquido_total_disponivel - float(tolerancia_monetaria), 0.0):
        uso_bruto = float(lote.saldo_bruto)
    else:
        bruto_necessario = float(valor_liquido_alvo) / fator
        uso_bruto = min(bruto_necessario, float(lote.saldo_bruto))
    efetivo = _money_round_half_up(lote.sacar(uso_bruto, tolerancia_monetaria=tolerancia_monetaria))
    liquido = _money_round_half_up(efetivo * fator)
    imposto = _money_round_half_up(efetivo - liquido)
    lote.total_imposto_pago += imposto
    lote.total_liquido_sacado += liquido
    return {
        'lote': lote,
        'saldo_antes': saldo_antes,
        'fator_liquido': float(fator),
        'bruto': efetivo,
        'liquido': liquido,
        'imposto': imposto,
        'saldo_remanescente': float(lote.saldo_bruto),
    }


def _obter_meta_produto(produto_key: Optional[str], carteira_canonica: Optional[PacoteCarteiraCanonica]) -> dict[str, Any]:
    if not produto_key or carteira_canonica is None:
        return {}
    return dict((carteira_canonica.mapa_produtos.get('by_key', {}) or {}).get(produto_key) or {})


def carregar_nucleo_financeiro_minimo(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    carteira_canonica: PacoteCarteiraCanonica,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
    serie_cdi: Optional[Mapping[date, Any]] = None,
) -> PacoteNucleoFinanceiroMinimo:
    tabela_iof = construir_tabela_iof(config)
    faixas_ir = construir_faixas_ir(config)
    tolerancia = float(_cfg_get(config, 'replay', 'tolerancia_monetaria', padrao=0.01) or 0.01)
    valor_min_lote_ativo = float(_cfg_get(config, 'replay', 'valor_minimo_lote_ativo', padrao=0.01) or 0.01)

    registros = dados_operacionais.inventario_canonico.copy()
    lotes_financeiros: list[Lote] = []
    lotes_preview: list[Lote] = []
    linhas_ignoradas: list[dict[str, Any]] = []
    qtd_lotes_com_taxa_default = 0
    qtd_lotes_sem_produto = 0
    qtd_lotes_com_carencia = 0
    qtd_lotes_produto_mapeado = 0

    for _, row in registros.iterrows():
        lote_id = limpar_texto(row.get('lote_id'))
        data_aplicacao = row.get('data_aplicacao')
        valor_original = float(para_float_monetario(row.get('valor_original'), 0.0))
        situacao = limpar_texto(row.get('situacao_investimento'))
        if not lote_id or data_aplicacao is None or valor_original <= 0.0:
            linhas_ignoradas.append({'lote_id': lote_id, 'motivo': 'registro_invalido'})
            continue
        if situacao == 'nao_aportado_exaurido':
            linhas_ignoradas.append({'lote_id': lote_id, 'motivo': 'lote_exaurido'})
            continue

        produto_key = row.get('produto_key') if bool(row.get('produto_encontrado', False)) else None
        meta_produto = _obter_meta_produto(produto_key, carteira_canonica)
        investimento = limpar_texto(row.get('produto_nome_canonico') or row.get('investimento_bruto') or row.get('produto_informado'))
        nao_disponivel = bool(row.get('recebido_futuro_nao_disponivel', False))
        taxa_base = float(meta_produto.get('taxa_base_cdi', _cfg_get(config, 'defaults_lote', 'taxa_base_cdi', padrao=1.0)) or 1.0)
        taxa_bonus = float(meta_produto.get('taxa_bonus_cdi', _cfg_get(config, 'defaults_lote', 'taxa_bonus_cdi', padrao=0.0)) or 0.0)
        dias_bonus = int(meta_produto.get('dias_bonus', _cfg_get(config, 'defaults_lote', 'dias_bonus', padrao=0)) or 0)
        if produto_key is None:
            qtd_lotes_sem_produto += 1
            taxa_base = 0.0 if not bool(row.get('aportado', False)) else float(_cfg_get(config, 'defaults_lote', 'taxa_base_cdi', padrao=1.0) or 1.0)
            taxa_bonus = 0.0
            dias_bonus = 0
            if bool(row.get('aportado', False)):
                qtd_lotes_com_taxa_default += 1
        else:
            qtd_lotes_produto_mapeado += 1

        data_base_fiscal = row.get('data_base_fiscal') or data_aplicacao
        carencia_dias = int(para_int(meta_produto.get('carencia_dias'), 0))
        carencia_ate = data_aplicacao + timedelta(days=carencia_dias) if carencia_dias > 0 else None
        if carencia_ate is not None:
            qtd_lotes_com_carencia += 1

        meta = {
            'investimento': investimento,
            'produto_key': produto_key,
            'data_base_fiscal': data_base_fiscal,
            'fator_acumulado_inicial': 1.0,
            'taxa_base_cdi': taxa_base,
            'taxa_bonus_cdi': taxa_bonus,
            'dias_bonus': dias_bonus,
            'principal_remanescente': float(valor_original),
            'produto_isento_ir': bool(meta_produto.get('isento_ir', False)),
            'carencia_ate': carencia_ate,
            'nao_disponivel_para_aporte': nao_disponivel,
            'situacao_investimento': situacao,
        }
        lote = criar_lote_de_aporte(data_aplicacao, valor_original, lote_id, meta)
        lotes_financeiros.append(lote)
        # preview mutável independente para auditoria sem contaminar o lote base
        lotes_preview.append(criar_lote_de_aporte(data_aplicacao, valor_original, lote_id, meta))

    # Atualização apenas para auditoria do núcleo mínimo, sem replay.
    data_inicial = min((l.data_aplicacao for l in lotes_preview), default=data_referencia)
    data_atual = data_inicial
    auditoria_fechamento_referencia: list[dict[str, Any]] = []
    qtd_fechamentos_referencia_com_fallback = 0
    while data_atual <= data_referencia:
        info_capitalizacao = atualizar_saldo_lotes_no_dia(
            lotes_preview,
            data_atual,
            calendario_financeiro,
            serie_cdi=serie_cdi,
            taxa_proj=calendario_financeiro.taxa_dia_base,
            data_fechamento_referencia=data_referencia,
        )
        if info_capitalizacao.get('fallback'):
            qtd_fechamentos_referencia_com_fallback += 1
            auditoria_fechamento_referencia.append({
                'data_valuation': data_atual,
                'data_fator_utilizado': info_capitalizacao.get('data_fator'),
                'fonte': info_capitalizacao.get('fonte'),
                'qtd_lotes_atualizados': info_capitalizacao.get('qtd_lotes_atualizados'),
            })
        data_atual += timedelta(days=1)

    saldo_bruto_total_referencia = sum(float(l.saldo_bruto) for l in lotes_preview if not l.esgotado and float(l.saldo_bruto) > valor_min_lote_ativo)
    saldo_liquido_total_referencia = sum(float(l.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir)) for l in lotes_preview if not l.esgotado and float(l.saldo_bruto) > valor_min_lote_ativo)

    amostra_movimento = None
    lote_exemplo = next((l for l in lotes_preview if not l.esgotado and float(l.saldo_bruto) > max(valor_min_lote_ativo, 100.0)), None)
    if lote_exemplo is not None:
        alvo = min(100.0, max(1.0, lote_exemplo.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) * 0.1))
        amostra_movimento = executar_saque_lote(lote_exemplo, alvo, data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir, tolerancia_monetaria=tolerancia)

    auditoria = {
        'qtd_lotes_financeiros': len(lotes_financeiros),
        'qtd_lotes_aportados': int(sum(1 for l in lotes_financeiros if l.situacao_investimento == 'aportado')),
        'qtd_caixa_disponivel': int(sum(1 for l in lotes_financeiros if l.situacao_investimento == 'nao_aportado_disponivel')),
        'qtd_recebidos_futuros': int(sum(1 for l in lotes_financeiros if l.situacao_investimento == 'recebido_futuro_nao_disponivel')),
        'qtd_lotes_nao_disponiveis_para_aporte': int(sum(1 for l in lotes_financeiros if l.nao_disponivel_para_aporte)),
        'qtd_lotes_produto_mapeado': qtd_lotes_produto_mapeado,
        'qtd_lotes_sem_produto': qtd_lotes_sem_produto,
        'qtd_lotes_com_taxa_default': qtd_lotes_com_taxa_default,
        'qtd_lotes_com_carencia': qtd_lotes_com_carencia,
        'qtd_lotes_ignorados_exauridos': int(sum(1 for x in linhas_ignoradas if x.get('motivo') == 'lote_exaurido')),
        'qtd_linhas_ignoradas': len(linhas_ignoradas),
        'saldo_bruto_total_referencia_sem_replay': arredondar_monetario(saldo_bruto_total_referencia),
        'saldo_liquido_total_referencia_sem_replay': arredondar_monetario(saldo_liquido_total_referencia),
        'fonte_rendimento_referencia': 'serie_cdi_bcb' if serie_cdi else 'taxa_modelo',
        'qtd_datas_serie_cdi': int(len(serie_cdi or {})),
        'data_final_valuation_referencia': data_referencia,
        'qtd_fechamentos_referencia_com_fallback_cdi': int(qtd_fechamentos_referencia_com_fallback),
        'amostra_fechamento_referencia': auditoria_fechamento_referencia[0] if auditoria_fechamento_referencia else None,
        'amostra_movimento_saque': None if amostra_movimento is None else {
            'lote_id': amostra_movimento['lote'].id,
            'bruto': amostra_movimento['bruto'],
            'liquido': amostra_movimento['liquido'],
            'imposto': amostra_movimento['imposto'],
            'saldo_remanescente': amostra_movimento['saldo_remanescente'],
        },
    }

    avisos = []
    if qtd_lotes_com_taxa_default > 0:
        avisos.append('existem_lotes_aportados_sem_produto_mapeado_usando_taxa_default')
    if qtd_lotes_sem_produto > 0:
        avisos.append('existem_lotes_financeiros_sem_produto_associado')
    validacao = {
        'ok': len(lotes_financeiros) > 0,
        'erros': [] if len(lotes_financeiros) > 0 else ['nenhum_lote_financeiro_criado'],
        'avisos': avisos,
    }
    return PacoteNucleoFinanceiroMinimo(lotes_financeiros=lotes_financeiros, auditoria=auditoria, validacao=validacao)
