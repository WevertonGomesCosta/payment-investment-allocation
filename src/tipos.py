from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional

import pandas as pd


class FaseTemporal(str, Enum):
    HISTORICO = "HISTORICO"
    FUTURO = "FUTURO"


class ClasseBrutaLote(str, Enum):
    INVESTIDO = "INVESTIDO"
    BLOQUEADO = "BLOQUEADO"
    LIVRE = "LIVRE"


class StatusLote(str, Enum):
    HISTORICO_EXECUTADO = "HISTORICO_EXECUTADO"
    INVESTIDO_ATUAL = "INVESTIDO_ATUAL"
    LIVRE_FUTURO = "LIVRE_FUTURO"
    LIVRE_DISPONIVEL = "LIVRE_DISPONIVEL"
    BLOQUEADO_MODELO = "BLOQUEADO_MODELO"
    RESGATE_AGENDADO = "RESGATE_AGENDADO"
    SWITCHING_AGENDADO = "SWITCHING_AGENDADO"
    ENCERRADO = "ENCERRADO"


class StatusGastoModelo(str, Enum):
    EXECUTADO = "EXECUTADO"
    PENDENTE = "PENDENTE"
    ALOCADO = "ALOCADO"
    PAGO_MODELO = "PAGO_MODELO"
    INVIAVEL = "INVIAVEL"


class TipoProduto(str, Enum):
    CDB = "CDB"
    LCA = "LCA"
    LCI = "LCI"
    TESOURO = "Tesouro"
    COMBO = "Combo"
    OUTRO = "Outro"


class TipoIndexador(str, Enum):
    CDI = "CDI"
    SELIC = "Selic"
    IPCA = "IPCA"
    PREFIXADO = "Prefixado"
    OUTRO = "Outro"


class TipoSwitching(str, Enum):
    INDIVIDUAL_TOTAL = "INDIVIDUAL_TOTAL"
    INDIVIDUAL_PARCIAL = "INDIVIDUAL_PARCIAL"


class StatusContratoSwitching(str, Enum):
    RASCUNHO = "RASCUNHO"
    ELEGIVEL = "ELEGIVEL"
    INVALIDO = "INVALIDO"
    AVALIADO = "AVALIADO"


class ResultadoComparacaoSwitching(str, Enum):
    MANTER = "MANTER"
    RESGATAR = "RESGATAR"
    SWITCHAR = "SWITCHAR"
    INDETERMINADO = "INDETERMINADO"


@dataclass(frozen=True)
class ConfigArquivos:
    planilha: str


@dataclass(frozen=True)
class ConfigAbas:
    gastos: str
    lotes: str
    carteiras: str


@dataclass(frozen=True)
class ConfigColunasGastos:
    data: str
    descricao: str
    valor: str
    pago: str
    lote_usado_1: str
    lote_usado_2: str


@dataclass(frozen=True)
class ConfigColunasLotes:
    id_lote: str
    data_entrada: str
    valor_original: str
    investimento: str


@dataclass(frozen=True)
class ConfigColunasCarteiras:
    nome: str
    tipo: str
    indexador: str
    taxa_base: str
    taxa_bonus: str
    dias_bonus: str
    prazo_dias: str
    carencia_dias: str
    isento_ir: str
    aplicacao_minima: str
    aplicacao_maxima: str
    ativo: str
    somente_combo: str
    produto_base: str
    produto_bonus: str
    ratio_base: str
    ratio_bonus: str
    banco_emissor: str
    score_banco: str
    risco_real: str
    max_usos: str


@dataclass(frozen=True)
class ConfigExecucao:
    timezone: str
    data_referencia_simulacao: Optional[str]
    convencao_dias_ano: dict[str, int]


@dataclass(frozen=True)
class ConfigPremissasMercado:
    cdi_anual_modelo: float
    selic_anual_modelo: float
    ipca_anual_modelo: float


@dataclass(frozen=True)
class ConfigTributacao:
    usar_ir: bool
    usar_iof: bool
    criterio_limite_ir: str
    faixas_ir: list[dict]
    tabela_iof: list[float]


@dataclass(frozen=True)
class ConfigPoliticasModelo:
    tratar_pago_nulo_como_nao: bool
    aceitar_multiplos_lotes_por_gasto: bool
    permitir_split_resgate: bool
    produto_inativo_em_novo_aporte: str
    produto_somente_combo_sem_decomposicao: str
    falha_reconciliacao_financeira: str


@dataclass(frozen=True)
class ConfigEscopoV1:
    reconstruir_historico: bool
    precificar_posicoes: bool
    diagnosticar_pagamentos_futuros: bool
    avaliar_aportes: bool
    avaliar_switching: bool
    buscar_cenario_otimo: bool


@dataclass(frozen=True)
class ConfigProjeto:
    arquivos: ConfigArquivos
    abas: ConfigAbas
    colunas_gastos: ConfigColunasGastos
    colunas_lotes: ConfigColunasLotes
    colunas_carteiras: ConfigColunasCarteiras
    execucao: ConfigExecucao
    premissas_mercado: ConfigPremissasMercado
    tributacao: ConfigTributacao
    politicas_modelo: ConfigPoliticasModelo
    escopo_v1: ConfigEscopoV1


@dataclass
class ValidationIssue:
    severity: Literal["ERROR", "WARNING"]
    table_name: str
    row_id: str
    field_name: str
    code: str
    message: str


@dataclass
class ValidationReport:
    ok: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)
        if issue.severity == "ERROR":
            self.ok = False

    def extend(self, issues: list[ValidationIssue]) -> None:
        for issue in issues:
            self.add_issue(issue)


@dataclass(frozen=True)
class ResultadoPrecificacao:
    id_lote: str
    data_referencia: pd.Timestamp
    valor_bruto_centavos: int
    valor_liquido_centavos: int
    rendimento_bruto_centavos: int
    imposto_centavos: int
    iof_centavos: int
    custo_operacional_centavos: int
    elegivel_resgate: bool
    elegivel_switching: bool


@dataclass(frozen=True)
class ResultadoAvaliacaoProduto:
    id_carteira: str
    data_inicio: pd.Timestamp
    data_fim: pd.Timestamp
    valor_inicial_centavos: int
    valor_bruto_projetado_centavos: int
    valor_liquido_projetado_centavos: int
    imposto_centavos: int
    iof_centavos: int
    custo_operacional_centavos: int
    detalhe_formula: str


@dataclass(frozen=True)
class InvarianteSwitching:
    code: str
    description: str
    severity: Literal["ERROR", "WARNING"] = "ERROR"


@dataclass(frozen=True)
class ContratoSwitching:
    id_lote_origem: str
    id_carteira_origem: str
    id_carteira_destino: str
    data_switching: pd.Timestamp
    tipo_switching: TipoSwitching
    valor_liquido_transferido_centavos: int
    valor_bruto_origem_centavos: int
    valor_liquido_origem_centavos: int
    status: StatusContratoSwitching
    motivo_economico: str = ""
    id_lote_destino_previsto: str = ""


@dataclass(frozen=True)
class AvaliacaoSwitching:
    contrato: ContratoSwitching
    valor_terminal_manter_centavos: int
    valor_terminal_resgatar_centavos: int
    valor_terminal_switchar_centavos: int
    custo_oportunidade_resgate_centavos: int
    custo_oportunidade_switching_centavos: int
    ganho_incremental_switching_vs_manter_centavos: int
    melhor_acao: ResultadoComparacaoSwitching
    observacoes: tuple[str, ...] = ()
