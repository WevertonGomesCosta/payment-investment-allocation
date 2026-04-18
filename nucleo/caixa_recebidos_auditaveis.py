from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

import pandas as pd

from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.utilitarios_neutros import limpar_texto, normalizar_identificador, normalizar_texto

STATUS_USO_PRE_APLICACAO_COM_APORTE_POSTERIOR = 'uso_pre_aplicacao_com_aporte_posterior'
DESTINO_PAGAMENTO_E_APLICACAO = 'pagamento_e_aplicacao'


@dataclass(frozen=True, slots=True)
class CampoContrato:
    nome: str
    tipo: str
    obrigatorio: bool
    descricao: str


@dataclass(frozen=True, slots=True)
class EstruturaContrato:
    nome: str
    descricao: str
    campos: tuple[CampoContrato, ...]

    def para_dict(self) -> dict[str, Any]:
        return {
            'nome': self.nome,
            'descricao': self.descricao,
            'campos': [asdict(campo) for campo in self.campos],
        }


@dataclass(slots=True)
class PacoteRecebidosAuditaveis:
    quadro_recebidos_auditaveis: pd.DataFrame
    auditoria: dict[str, Any]


@dataclass(slots=True)
class PacoteFontesElegiveisPagamento:
    quadro_fontes_elegiveis: pd.DataFrame
    auditoria: dict[str, Any]


@dataclass(slots=True)
class PacoteSaldoDisponivelGeral:
    quadro_saldo_disponivel: pd.DataFrame
    auditoria: dict[str, Any]


@dataclass(slots=True)
class PacoteDecisaoLocalV1:
    quadro_decisao_local_v1: pd.DataFrame
    auditoria: dict[str, Any]


def _campos_fonte_elegivel() -> tuple[CampoContrato, ...]:
    return (
        CampoContrato('fonte_pagamento_id', 'str', True, 'Identificador canônico e estável da linha fonte x pagamento.'),
        CampoContrato('fonte_id', 'str', True, 'Identificador canônico e estável da fonte elegível.'),
        CampoContrato('pagamento_id', 'str', True, 'Identificador canônico do pagamento alvo.'),
        CampoContrato('data_pagamento', 'date', True, 'Data econômica do pagamento alvo.'),
        CampoContrato('tipo_fonte', 'str', True, 'Categoria da fonte: saldo_disponivel, caixa_pre_aplicacao, lote_resgatavel ou recebido_disponivel.'),
        CampoContrato('data_evento', 'date', True, 'Data econômica em que a fonte pode financiar o pagamento.'),
        CampoContrato('lote_id', 'str|None', False, 'Identificador do lote quando a fonte deriva de um lote específico.'),
        CampoContrato('recebido_id', 'str|None', False, 'Identificador do recebido quando a fonte deriva de um recebido explícito.'),
        CampoContrato('produto_key', 'str|None', False, 'Produto canônico associado quando houver produto financeiro vinculado.'),
        CampoContrato('valor_pagamento', 'float', True, 'Valor bruto do pagamento alvo.'),
        CampoContrato('valor_bruto_disponivel', 'float', True, 'Valor bruto economicamente elegível ou observável para a fonte.'),
        CampoContrato('valor_liquido_disponivel', 'float', True, 'Valor líquido economicamente elegível ou observável para a fonte.'),
        CampoContrato('elegivel_na_data_pagamento', 'bool', True, 'Indica se a fonte está elegível na data específica do pagamento.'),
        CampoContrato('origem_status', 'str', True, 'Status operacional da origem: confirmado, estimado, parcial ou bloqueado.'),
        CampoContrato('motivo_bloqueio_temporal', 'str|None', False, 'Motivo auditável quando a fonte não está elegível na data do pagamento.'),
        CampoContrato('data_base_valor', 'date', True, 'Data-base da fotografia do valor disponível usada nesta etapa.'),
        CampoContrato('metodo_valor_disponivel', 'str', True, 'Método de leitura do valor disponível: nominal_origem, fotografia_data_referencia ou similar.'),
        CampoContrato('observacao_auditavel', 'str', False, 'Texto curto para explicar a elegibilidade ou restrição da fonte.'),
    )


def _campos_recebido_auditavel() -> tuple[CampoContrato, ...]:
    return (
        CampoContrato('recebido_id', 'str', True, 'Identificador canônico do recebido.'),
        CampoContrato('data_recebimento', 'date', True, 'Data em que o recurso passa a existir economicamente.'),
        CampoContrato('data_aplicacao', 'date|None', False, 'Data em que o recurso passa a render, se houver aplicação.'),
        CampoContrato('valor_bruto', 'float', True, 'Valor bruto do recebido.'),
        CampoContrato('valor_liquido', 'float', True, 'Valor líquido auditável do recebido na origem.'),
        CampoContrato('status_recebido', 'str', True, 'Situação operacional: futuro, disponivel, comprometido, aplicado, exaurido ou uso_pre_aplicacao_com_aporte_posterior.'),
        CampoContrato('destino_potencial', 'str', True, 'Destino potencial observado ou elegível: caixa, pagamento, aplicacao ou pagamento_e_aplicacao.'),
        CampoContrato('pagamento_vinculado_id', 'str|None', False, 'Pagamento explicitamente associado, quando já existir vínculo auditável.'),
        CampoContrato('lote_destino_id', 'str|None', False, 'Lote de destino, quando o recebido já foi ou será convertido em lote.'),
        CampoContrato('observacao_auditavel', 'str', False, 'Texto curto para registrar a leitura econômica do recebido.'),
    )


def _campos_saldo_disponivel_geral() -> tuple[CampoContrato, ...]:
    return (
        CampoContrato('saldo_disponivel_id', 'str', True, 'Identificador canônico e estável da linha de saldo disponível geral por pagamento.'),
        CampoContrato('pagamento_id', 'str', True, 'Identificador canônico do pagamento alvo.'),
        CampoContrato('data_pagamento', 'date', True, 'Data econômica do pagamento analisado.'),
        CampoContrato('valor_pagamento', 'float', True, 'Valor bruto do pagamento alvo.'),
        CampoContrato('saldo_disponivel_bruto', 'float', True, 'Valor bruto do caixa geral observável para a data do pagamento, sem projeção financeira adicional.'),
        CampoContrato('saldo_disponivel_liquido', 'float', True, 'Valor líquido do caixa geral observável para a data do pagamento.'),
        CampoContrato('saldo_disponivel_elegivel', 'bool', True, 'Indica se existe saldo disponível geral observável e economicamente elegível na data do pagamento.'),
        CampoContrato('origem_status', 'str', True, 'Status operacional do saldo geral: confirmado, parcial, estimado ou ausente.'),
        CampoContrato('origem_saldo', 'str', True, 'Origem auditável do saldo geral: agregado de recebidos disponíveis, caixa pré-aplicação ou ausência observável na base.'),
        CampoContrato('qtd_fontes_componentes', 'int', True, 'Quantidade de fontes explícitas agregadas para formar o saldo geral observado.'),
        CampoContrato('tipos_fontes_componentes', 'str', True, 'Lista textual dos tipos de fonte explícita agregados ao saldo geral.'),
        CampoContrato('regra_precedencia_intradiaria', 'str', True, 'Estado auditável da precedência intradiária aplicável nesta etapa.'),
        CampoContrato('restricao_duplicidade_recebidos', 'bool', True, 'Marca que o saldo geral é agregado de fontes explícitas e não deve ser somado novamente a elas.'),
        CampoContrato('data_base_saldo', 'date', True, 'Data-base do saldo observado usada na etapa atual.'),
        CampoContrato('metodo_saldo', 'str', True, 'Método de materialização do saldo geral nesta etapa.'),
        CampoContrato('observacao_auditavel', 'str', False, 'Texto curto para explicar o saldo geral observado ou sua ausência na base atual.'),
    )


def _campos_decisao_local_v1() -> tuple[CampoContrato, ...]:
    return (
        CampoContrato('pagamento_id', 'str', True, 'Identificador canônico do pagamento analisado.'),
        CampoContrato('data_pagamento', 'date', True, 'Data econômica do pagamento.'),
        CampoContrato('fonte_escolhida_id', 'str', True, 'Fonte escolhida pela regra local v1.'),
        CampoContrato('tipo_fonte_escolhida', 'str', True, 'Categoria da fonte escolhida.'),
        CampoContrato('criterio_decisao', 'str', True, 'Critério auditável aplicado na decisão local v1.'),
        CampoContrato('custo_economico_proxy', 'float|None', False, 'Score do proxy econômico v3 associado à escolha local, quanto menor melhor.'),
        CampoContrato('observacao_auditavel', 'str', False, 'Resumo curto da decisão local sem abrir solver ou switching.'),
    )


def obter_contrato_minimo_caixa_recebidos() -> dict[str, Any]:
    estruturas = (
        EstruturaContrato(
            nome='fonte_elegivel_pagamento',
            descricao='Estrutura canônica mínima para representar qualquer fonte economicamente elegível para um pagamento em uma data específica.',
            campos=_campos_fonte_elegivel(),
        ),
        EstruturaContrato(
            nome='recebido_auditavel',
            descricao='Estrutura canônica mínima para rastrear recebidos com valor, status e destino auditável.',
            campos=_campos_recebido_auditavel(),
        ),
        EstruturaContrato(
            nome='saldo_disponivel_geral',
            descricao='Estrutura canônica mínima para representar o saldo disponível geral observável por pagamento sem duplicar, nesta etapa, as fontes explícitas já materializadas.',
            campos=_campos_saldo_disponivel_geral(),
        ),
        EstruturaContrato(
            nome='decisao_local_v1',
            descricao='Estrutura canônica da decisão local entre saldo disponível, caixa pré-aplicação, recebidos e resgate, agora com proxy econômico v3 ainda sem solver e sem switching.',
            campos=_campos_decisao_local_v1(),
        ),
    )
    return {
        'frente': 'F1',
        'nome': 'caixa e recebidos auditáveis + decisão local v1 entre saldo disponível e resgate',
        'escopo_etapa_atual': 'Materialização da decisão local v1 com proxy econômico v3 por pagamento sobre a matriz temporal completa de fontes e saldo geral, ainda sem solver, sem switching e sem integração ao fluxo principal da baseline.',
        'implementado_nesta_etapa': [
            'Contrato mínimo documentado e observável da camada F1.',
            'Estruturas canônicas para fonte elegível de pagamento, recebido auditável e decisão local v1.',
            'Materialização executável de recebido_auditavel a partir do inventário canônico e dos vínculos históricos de gastos.',
            'Materialização executável de fonte_elegivel_pagamento por data de pagamento, usando os pagamentos futuros/pendentes, os recebidos auditáveis, o inventário canônico e o estado mínimo observável do replay.',
            'Materialização executável de saldo_disponivel geral por pagamento, agregando somente as fontes explícitas de caixa já observáveis na F1 sem somá-las novamente na decisão futura.',
            'Materialização executável de decisao_local_v1 por pagamento sobre a matriz temporal completa de fontes e saldo geral.',
            'Scripts diagnósticos para inspecionar o contrato mínimo e as estruturas reais abertas da F1 sem tocar no motor financeiro.',
        ],
        'fora_do_escopo_nesta_etapa': [
            'Alteração do motor financeiro.',
            'Abertura da decisão econômica real.',
            'Abertura de switching econômico.',
            'Integração da F1 ao fluxo principal do console ou da planilha operacional.',
            'Projeção financeira futura completa dos valores das fontes até cada data de pagamento.',
            'Decisão econômica real otimizada, com solver, switching ou alocação multi-fonte.',
        ],
        'estruturas': [estrutura.para_dict() for estrutura in estruturas],
    }


def validar_contrato_minimo_caixa_recebidos() -> list[str]:
    erros: list[str] = []
    contrato = obter_contrato_minimo_caixa_recebidos()
    nomes = set()
    for estrutura in contrato.get('estruturas', []):
        nome = str(estrutura.get('nome') or '').strip()
        if not nome:
            erros.append('estrutura_sem_nome')
            continue
        if nome in nomes:
            erros.append(f'estrutura_duplicada: {nome}')
        nomes.add(nome)
        campos = estrutura.get('campos') or []
        if not campos:
            erros.append(f'estrutura_sem_campos: {nome}')
            continue
        nomes_campos = set()
        for campo in campos:
            campo_nome = str(campo.get('nome') or '').strip()
            if not campo_nome:
                erros.append(f'campo_sem_nome: {nome}')
                continue
            if campo_nome in nomes_campos:
                erros.append(f'campo_duplicado: {nome}.{campo_nome}')
            nomes_campos.add(campo_nome)
            if not str(campo.get('tipo') or '').strip():
                erros.append(f'campo_sem_tipo: {nome}.{campo_nome}')
            if not str(campo.get('descricao') or '').strip():
                erros.append(f'campo_sem_descricao: {nome}.{campo_nome}')
    return erros


def _slug_recebido(lote_id: str) -> str:
    texto = normalizar_texto(lote_id).replace(' ', '_')
    return texto or 'recebido'


def _recebido_id(lote_id: str) -> str:
    return f'recebido::{_slug_recebido(lote_id)}'


def _slug_fonte(chave: str) -> str:
    texto = normalizar_texto(chave).replace(' ', '_')
    return texto or 'fonte'


def _fonte_id(tipo_fonte: str, *, lote_id: str | None = None, recebido_id: str | None = None) -> str:
    base = lote_id or recebido_id or tipo_fonte
    return f"fonte::{_slug_fonte(tipo_fonte)}::{_slug_fonte(base)}"

def _fonte_pagamento_id(fonte_id: str, pagamento_id: str) -> str:
    return f"{fonte_id}::pagamento::{_slug_fonte(pagamento_id)}"


def _gastos_por_lote(gastos_canonicos: pd.DataFrame) -> pd.DataFrame:
    registros: list[dict[str, Any]] = []
    if len(gastos_canonicos) == 0:
        return pd.DataFrame(columns=['despesa_id', 'data', 'valor', 'lote_id'])

    for _, row in gastos_canonicos.iterrows():
        for coluna in ('lote_usado_1', 'lote_usado_2'):
            lote_id = normalizar_identificador(row.get(coluna))
            if not lote_id:
                continue
            registros.append({
                'despesa_id': limpar_texto(row.get('despesa_id')),
                'data': row.get('data'),
                'valor': float(row.get('valor') or 0.0),
                'lote_id': lote_id,
            })
    if not registros:
        return pd.DataFrame(columns=['despesa_id', 'data', 'valor', 'lote_id'])
    return pd.DataFrame(registros)


def _resumir_vinculos_pagamento(lote_id: str, data_aplicacao: date | None, gastos_por_lote: pd.DataFrame) -> dict[str, Any]:
    if len(gastos_por_lote) == 0:
        return {
            'qtd_pagamentos_vinculados': 0,
            'valor_total_vinculado': 0.0,
            'valor_pagamentos_pre_aplicacao': 0.0,
            'valor_pagamentos_pos_aplicacao': 0.0,
            'pagamento_vinculado_id': None,
        }

    quadro = gastos_por_lote[gastos_por_lote['lote_id'] == lote_id].copy()
    if len(quadro) == 0:
        return {
            'qtd_pagamentos_vinculados': 0,
            'valor_total_vinculado': 0.0,
            'valor_pagamentos_pre_aplicacao': 0.0,
            'valor_pagamentos_pos_aplicacao': 0.0,
            'pagamento_vinculado_id': None,
        }

    valor_total = round(float(quadro['valor'].sum()), 2)
    if data_aplicacao is None:
        valor_pre = 0.0
        valor_pos = valor_total
    else:
        mask_pre = quadro['data'].apply(lambda x: x is not None and x < data_aplicacao)
        valor_pre = round(float(quadro.loc[mask_pre, 'valor'].sum()), 2)
        valor_pos = round(valor_total - valor_pre, 2)

    despesas_unicas = sorted({limpar_texto(v) for v in quadro['despesa_id'].tolist() if limpar_texto(v)})
    return {
        'qtd_pagamentos_vinculados': int(len(quadro)),
        'valor_total_vinculado': valor_total,
        'valor_pagamentos_pre_aplicacao': valor_pre,
        'valor_pagamentos_pos_aplicacao': valor_pos,
        'pagamento_vinculado_id': despesas_unicas[0] if len(despesas_unicas) == 1 else None,
    }


def _classificar_recebido(row: pd.Series, data_referencia: date, resumo_pagamentos: dict[str, Any]) -> tuple[str, str, str | None, str]:
    situacao = limpar_texto(row.get('situacao_investimento'))
    data_recebimento = row.get('data_recebimento')
    data_aplicacao = row.get('data_aplicacao')
    lote_id = normalizar_identificador(row.get('lote_id'))

    qtd_pagamentos = int(resumo_pagamentos.get('qtd_pagamentos_vinculados', 0) or 0)
    valor_pre = float(resumo_pagamentos.get('valor_pagamentos_pre_aplicacao', 0.0) or 0.0)

    if situacao == 'recebido_futuro_nao_disponivel':
        return (
            'futuro',
            'caixa',
            None,
            'recebido futuro ainda não disponível na data de referência.',
        )

    if situacao == 'nao_aportado_disponivel':
        return (
            'disponivel',
            'caixa',
            None,
            'recebido disponível em caixa e ainda não aportado.',
        )

    if situacao == 'nao_aportado_exaurido':
        observacao = 'recebido já exaurido em pagamentos históricos.'
        if qtd_pagamentos > 0:
            observacao = f'recebido não aportado já exaurido em {qtd_pagamentos} pagamento(s) histórico(s).'
        return ('exaurido', 'pagamento', None, observacao)

    if situacao == 'aportado':
        if data_recebimento is not None and data_recebimento > data_referencia:
            return ('futuro', 'aplicacao', lote_id, 'recebido associado a lote aportado, mas ainda não disponível economicamente.')
        if data_aplicacao is not None and data_referencia < data_aplicacao:
            if qtd_pagamentos > 0:
                return (
                    STATUS_USO_PRE_APLICACAO_COM_APORTE_POSTERIOR,
                    DESTINO_PAGAMENTO_E_APLICACAO,
                    lote_id,
                    'recebido usado em pagamentos antes da aplicação, com aporte final posterior ainda pendente.',
                )
            return (
                'comprometido',
                'aplicacao',
                lote_id,
                'recebido disponível, porém comprometido para aplicação futura.',
            )
        if valor_pre > 0:
            return (
                STATUS_USO_PRE_APLICACAO_COM_APORTE_POSTERIOR,
                DESTINO_PAGAMENTO_E_APLICACAO,
                lote_id,
                'recebido usado em pagamentos antes da aplicação; o valor residual foi aportado posteriormente.',
            )
        return ('aplicado', 'aplicacao', lote_id, 'recebido integralmente associado a lote aportado.')

    return ('disponivel', 'caixa', lote_id or None, 'classificação econômica provisória para recebido não enquadrado nas regras principais.')


def materializar_recebidos_auditaveis(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    *,
    data_referencia: date,
) -> PacoteRecebidosAuditaveis:
    inventario = dados_operacionais.inventario_canonico.copy()
    gastos = dados_operacionais.gastos_canonicos.copy()
    gastos_por_lote = _gastos_por_lote(gastos)

    registros: list[dict[str, Any]] = []
    for _, row in inventario.iterrows():
        lote_id = normalizar_identificador(row.get('lote_id'))
        resumo_pagamentos = _resumir_vinculos_pagamento(lote_id, row.get('data_aplicacao'), gastos_por_lote)
        status_recebido, destino_potencial, lote_destino_id, observacao = _classificar_recebido(row, data_referencia, resumo_pagamentos)
        recebido_id = _recebido_id(lote_id)

        registros.append({
            'recebido_id': recebido_id,
            'lote_id_origem': lote_id,
            'data_recebimento': row.get('data_recebimento'),
            'data_aplicacao': row.get('data_aplicacao'),
            'valor_bruto': round(float(row.get('valor_original') or 0.0), 2),
            'valor_liquido': round(float(row.get('valor_original') or 0.0), 2),
            'status_recebido': status_recebido,
            'destino_potencial': destino_potencial,
            'pagamento_vinculado_id': resumo_pagamentos.get('pagamento_vinculado_id'),
            'lote_destino_id': lote_destino_id,
            'observacao_auditavel': observacao,
            'produto_key': row.get('produto_key'),
            'produto_nome_canonico': row.get('produto_nome_canonico'),
            'situacao_investimento_origem': row.get('situacao_investimento'),
            'disponivel_na_data_referencia': bool(row.get('disponivel_na_data_referencia', False)),
            'qtd_pagamentos_vinculados': int(resumo_pagamentos.get('qtd_pagamentos_vinculados', 0) or 0),
            'valor_total_vinculado': round(float(resumo_pagamentos.get('valor_total_vinculado', 0.0) or 0.0), 2),
            'valor_pagamentos_pre_aplicacao': round(float(resumo_pagamentos.get('valor_pagamentos_pre_aplicacao', 0.0) or 0.0), 2),
            'valor_pagamentos_pos_aplicacao': round(float(resumo_pagamentos.get('valor_pagamentos_pos_aplicacao', 0.0) or 0.0), 2),
            'valor_residual_para_aplicacao_origem': round(
                max(float(row.get('valor_original') or 0.0) - float(resumo_pagamentos.get('valor_pagamentos_pre_aplicacao', 0.0) or 0.0), 0.0),
                2,
            ) if lote_destino_id else 0.0,
            'em_janela_pre_aplicacao_na_referencia': bool(
                row.get('data_recebimento') is not None
                and row.get('data_aplicacao') is not None
                and row.get('data_recebimento') <= data_referencia < row.get('data_aplicacao')
            ),
        })

    quadro = pd.DataFrame(registros)
    if len(quadro) == 0:
        auditoria = {
            'validacao': {'ok': False, 'erros': ['recebidos_auditaveis_vazio'], 'avisos': []},
            'resumo': {},
        }
        return PacoteRecebidosAuditaveis(quadro_recebidos_auditaveis=quadro, auditoria=auditoria)

    quadro = quadro.sort_values(['data_recebimento', 'lote_id_origem'], kind='stable').reset_index(drop=True)
    erros: list[str] = []
    avisos: list[str] = []
    if quadro['recebido_id'].duplicated().any():
        erros.append('recebido_id_duplicado')
    if quadro['data_recebimento'].isna().any():
        erros.append('data_recebimento_nula')
    if (quadro['valor_bruto'] <= 0).any():
        erros.append('valor_bruto_nao_positivo')
    if (quadro['valor_liquido'] <= 0).any():
        erros.append('valor_liquido_nao_positivo')
    if (quadro['status_recebido'] == STATUS_USO_PRE_APLICACAO_COM_APORTE_POSTERIOR).any():
        avisos.append('existem_recebidos_usados_antes_da_aplicacao_com_aporte_posterior')
    if (quadro['status_recebido'] == 'comprometido').any():
        avisos.append('existem_recebidos_comprometidos_para_aplicacao_futura')
    if (quadro['status_recebido'] == 'futuro').any():
        avisos.append('existem_recebidos_futuros_nao_disponiveis')

    auditoria = {
        'validacao': {'ok': len(erros) == 0, 'erros': erros, 'avisos': avisos},
        'resumo': {
            'total_recebidos': int(len(quadro)),
            'status_recebido': {str(k): int(v) for k, v in quadro['status_recebido'].value_counts(dropna=False).to_dict().items()},
            'destino_potencial': {str(k): int(v) for k, v in quadro['destino_potencial'].value_counts(dropna=False).to_dict().items()},
            'valor_total_bruto': round(float(quadro['valor_bruto'].sum()), 2),
            'recebidos_com_pagamento_vinculado': int((quadro['qtd_pagamentos_vinculados'] > 0).sum()),
            'recebidos_em_janela_pre_aplicacao': int(quadro['em_janela_pre_aplicacao_na_referencia'].sum()),
            'recebidos_usados_antes_da_aplicacao_observado': int(((quadro['valor_pagamentos_pre_aplicacao'] > 0) & (quadro['lote_destino_id'].notna())).sum()),
        },
    }
    return PacoteRecebidosAuditaveis(quadro_recebidos_auditaveis=quadro, auditoria=auditoria)


def _indexar_inventario_por_lote(inventario: pd.DataFrame) -> dict[str, dict[str, Any]]:
    if len(inventario) == 0:
        return {}
    return {
        normalizar_identificador(row.get('lote_id')): row
        for row in inventario.to_dict(orient='records')
        if normalizar_identificador(row.get('lote_id'))
    }


def _pagamentos_alvo_f1_4(gastos_canonicos: pd.DataFrame, *, data_referencia: date) -> pd.DataFrame:
    if len(gastos_canonicos) == 0:
        return pd.DataFrame(columns=['despesa_id', 'data', 'descricao', 'valor', 'pago'])
    quadro = gastos_canonicos.copy()
    mask = quadro['futuro_ou_pendente_na_data_referencia'].eq(True) & quadro['data'].notna() & (quadro['data'] >= data_referencia)
    quadro = quadro.loc[mask, ['despesa_id', 'data', 'descricao', 'valor', 'pago']].copy()
    if len(quadro) == 0:
        return quadro
    quadro['descricao'] = quadro['descricao'].map(limpar_texto)
    quadro['despesa_id'] = quadro['despesa_id'].map(limpar_texto)
    quadro['valor'] = quadro['valor'].map(lambda v: round(float(v or 0.0), 2))
    quadro = quadro.sort_values(['data', 'despesa_id'], kind='stable').reset_index(drop=True)
    return quadro


def _linha_base_fonte_pagamento(
    *,
    pagamento: dict[str, Any],
    fonte_id: str,
    tipo_fonte: str,
    data_evento: date,
    lote_id: str | None,
    recebido_id: str | None,
    produto_key: Any,
    produto_nome: Any,
    valor_bruto_disponivel: float,
    valor_liquido_disponivel: float,
    elegivel_na_data_pagamento: bool,
    origem_status: str,
    motivo_bloqueio_temporal: str | None,
    observacao_auditavel: str,
    data_base_valor: date,
    metodo_valor_disponivel: str,
    data_recebimento_origem: date | None,
    data_aplicacao_origem: date | None,
    carencia_ate_origem: date | None,
    origem_estrutura: str,
) -> dict[str, Any]:
    pagamento_id = limpar_texto(pagamento.get('despesa_id'))
    return {
        'fonte_pagamento_id': _fonte_pagamento_id(fonte_id, pagamento_id),
        'fonte_id': fonte_id,
        'pagamento_id': pagamento_id,
        'data_pagamento': pagamento.get('data'),
        'descricao_pagamento': limpar_texto(pagamento.get('descricao')),
        'valor_pagamento': round(float(pagamento.get('valor') or 0.0), 2),
        'tipo_fonte': tipo_fonte,
        'data_evento': data_evento,
        'lote_id': lote_id,
        'recebido_id': recebido_id,
        'produto_key': produto_key,
        'produto_nome_canonico': produto_nome,
        'valor_bruto_disponivel': round(float(valor_bruto_disponivel or 0.0), 2),
        'valor_liquido_disponivel': round(float(valor_liquido_disponivel or 0.0), 2),
        'elegivel_na_data_pagamento': bool(elegivel_na_data_pagamento),
        'origem_status': origem_status,
        'motivo_bloqueio_temporal': limpar_texto(motivo_bloqueio_temporal) or None,
        'data_base_valor': data_base_valor,
        'metodo_valor_disponivel': metodo_valor_disponivel,
        'observacao_auditavel': observacao_auditavel,
        'data_recebimento_origem': data_recebimento_origem,
        'data_aplicacao_origem': data_aplicacao_origem,
        'carencia_ate_origem': carencia_ate_origem,
        'origem_estrutura': origem_estrutura,
    }


def _materializar_fontes_de_recebidos_por_pagamento(
    quadro_recebidos: pd.DataFrame,
    pagamentos_alvo: pd.DataFrame,
    *,
    data_referencia: date,
    limiar_valor: float,
) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = []
    if len(quadro_recebidos) == 0 or len(pagamentos_alvo) == 0:
        return registros

    pagamentos = pagamentos_alvo.to_dict(orient='records')
    for _, row in quadro_recebidos.iterrows():
        recebido_id = limpar_texto(row.get('recebido_id'))
        lote_id = normalizar_identificador(row.get('lote_id_origem'))
        produto_key = row.get('produto_key')
        produto_nome = row.get('produto_nome_canonico')
        status_recebido = limpar_texto(row.get('status_recebido'))
        observacao_origem = limpar_texto(row.get('observacao_auditavel'))
        data_recebimento = row.get('data_recebimento')
        data_aplicacao = row.get('data_aplicacao')
        lote_destino_id = normalizar_identificador(row.get('lote_destino_id'))
        valor_nominal = round(float(row.get('valor_liquido') or row.get('valor_bruto') or 0.0), 2)
        valor_residual = round(float(row.get('valor_residual_para_aplicacao_origem') or 0.0), 2)
        valor_pre_aplicacao = valor_residual if lote_destino_id else valor_nominal

        if status_recebido == 'exaurido':
            continue

        for pagamento in pagamentos:
            data_pagamento = pagamento.get('data')
            if data_pagamento is None:
                continue

            if lote_destino_id:
                if data_aplicacao is not None and data_pagamento >= data_aplicacao:
                    continue
                if valor_pre_aplicacao <= limiar_valor:
                    continue

                fonte_id = _fonte_id('caixa_pre_aplicacao', lote_id=lote_id or None, recebido_id=recebido_id)
                mesmo_dia_recebimento = data_recebimento is not None and data_pagamento == data_recebimento
                if data_recebimento is not None and data_pagamento < data_recebimento:
                    origem_status = 'bloqueado'
                    elegivel = False
                    motivo = 'recebido_ainda_nao_existente_na_data_do_pagamento'
                    observacao = 'recebido/lote ainda não existe economicamente na data do pagamento.'
                elif data_aplicacao is not None and data_pagamento == data_aplicacao:
                    origem_status = 'estimado'
                    elegivel = True
                    motivo = None
                    observacao = 'pagamento na mesma data da aplicação; precedência intradiária entre pagar e aplicar ainda não foi materializada.'
                else:
                    elegivel = True
                    motivo = None
                    if mesmo_dia_recebimento:
                        origem_status = 'estimado'
                        observacao = 'pagamento na mesma data do recebimento; precedência intradiária ainda não foi materializada para esta fonte pré-aplicação.'
                    else:
                        origem_status = 'parcial' if status_recebido == STATUS_USO_PRE_APLICACAO_COM_APORTE_POSTERIOR else 'confirmado'
                        observacao = observacao_origem or 'valor disponível em caixa pré-aplicação na data do pagamento.'
                        if origem_status == 'parcial':
                            observacao = f'{observacao} Residual remanescente após uso parcial em pagamentos antes da aplicação.'

                registros.append(_linha_base_fonte_pagamento(
                    pagamento=pagamento,
                    fonte_id=fonte_id,
                    tipo_fonte='caixa_pre_aplicacao',
                    data_evento=data_pagamento,
                    lote_id=lote_id or None,
                    recebido_id=recebido_id,
                    produto_key=produto_key,
                    produto_nome=produto_nome,
                    valor_bruto_disponivel=valor_pre_aplicacao,
                    valor_liquido_disponivel=valor_pre_aplicacao,
                    elegivel_na_data_pagamento=elegivel,
                    origem_status=origem_status,
                    motivo_bloqueio_temporal=motivo,
                    observacao_auditavel=observacao,
                    data_base_valor=data_referencia if data_pagamento > data_referencia else data_pagamento,
                    metodo_valor_disponivel='nominal_origem',
                    data_recebimento_origem=data_recebimento,
                    data_aplicacao_origem=data_aplicacao,
                    carencia_ate_origem=None,
                    origem_estrutura='recebido_auditavel',
                ))
                continue

            if valor_nominal <= limiar_valor:
                continue

            fonte_id = _fonte_id('recebido_disponivel', recebido_id=recebido_id)
            mesmo_dia_recebimento = data_recebimento is not None and data_pagamento == data_recebimento
            if data_recebimento is not None and data_pagamento < data_recebimento:
                origem_status = 'bloqueado'
                elegivel = False
                motivo = 'recebido_ainda_nao_existente_na_data_do_pagamento'
                observacao = 'recebido futuro ainda não existente economicamente na data do pagamento.'
            else:
                elegivel = True
                motivo = None
                if mesmo_dia_recebimento:
                    origem_status = 'estimado'
                    observacao = 'pagamento na mesma data do recebimento; precedência intradiária ainda não foi materializada para o caixa disponível.'
                else:
                    origem_status = 'confirmado'
                    observacao = observacao_origem or 'recebido disponível em caixa na data do pagamento.'

            registros.append(_linha_base_fonte_pagamento(
                pagamento=pagamento,
                fonte_id=fonte_id,
                tipo_fonte='recebido_disponivel',
                data_evento=data_pagamento,
                lote_id=lote_id or None,
                recebido_id=recebido_id,
                produto_key=produto_key,
                produto_nome=produto_nome,
                valor_bruto_disponivel=valor_nominal,
                valor_liquido_disponivel=valor_nominal,
                elegivel_na_data_pagamento=elegivel,
                origem_status=origem_status,
                motivo_bloqueio_temporal=motivo,
                observacao_auditavel=observacao,
                data_base_valor=data_referencia if data_pagamento > data_referencia else data_pagamento,
                metodo_valor_disponivel='nominal_origem',
                data_recebimento_origem=data_recebimento,
                data_aplicacao_origem=data_aplicacao,
                carencia_ate_origem=None,
                origem_estrutura='recebido_auditavel',
            ))

    return registros


def _materializar_fontes_de_replay_por_pagamento(
    lotes_replay: list[Any],
    inventario_por_lote: dict[str, dict[str, Any]],
    pagamentos_alvo: pd.DataFrame,
    *,
    data_referencia: date,
    tabela_iof: list[float] | None,
    faixas_ir: list[dict[str, Any]] | None,
    limiar_valor: float,
) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = []
    if len(pagamentos_alvo) == 0:
        return registros

    pagamentos = pagamentos_alvo.to_dict(orient='records')
    for lote in lotes_replay or []:
        lote_id = normalizar_identificador(getattr(lote, 'id', None))
        if not lote_id:
            continue
        saldo_bruto = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
        if saldo_bruto <= limiar_valor:
            continue

        data_aplicacao = getattr(lote, 'data_aplicacao', None)
        data_recebimento = getattr(lote, 'data_recebimento', None)
        carencia_ate = getattr(lote, 'carencia_ate', None)
        linha_inventario = inventario_por_lote.get(lote_id, {})
        produto_key = getattr(lote, 'produto_key', None) or linha_inventario.get('produto_key')
        produto_nome = limpar_texto(getattr(lote, 'investimento', None)) or linha_inventario.get('produto_nome_canonico')
        recebido_id = _recebido_id(lote_id)

        try:
            valor_liquido_referencia = round(float(lote.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir)), 2)
        except Exception:
            valor_liquido_referencia = saldo_bruto

        fonte_id = _fonte_id('lote_resgatavel', lote_id=lote_id)
        for pagamento in pagamentos:
            data_pagamento = pagamento.get('data')
            if data_pagamento is None:
                continue
            if data_aplicacao is not None and data_pagamento < data_aplicacao:
                continue

            mesmo_dia_aplicacao = data_aplicacao is not None and data_pagamento == data_aplicacao
            if carencia_ate is not None and data_pagamento < carencia_ate:
                origem_status = 'bloqueado'
                elegivel = False
                motivo = 'carencia_ativa_na_data_do_pagamento'
                observacao = f'lote com saldo remanescente após o replay, mas ainda bloqueado por carência até {carencia_ate.isoformat()}.'
            elif mesmo_dia_aplicacao:
                origem_status = 'estimado'
                elegivel = True
                motivo = None
                observacao = 'pagamento na mesma data da aplicação; precedência intradiária entre pagar e aplicar ainda não foi materializada para este lote.'
            else:
                origem_status = 'confirmado'
                elegivel = True
                motivo = None
                observacao = 'lote com saldo remanescente após o replay e elegível para resgate na data do pagamento.'
                if data_pagamento > data_referencia:
                    observacao += ' Valor mantido como fotografia da data de referência; a projeção futura da fonte ainda não foi aberta nesta etapa.'

            registros.append(_linha_base_fonte_pagamento(
                pagamento=pagamento,
                fonte_id=fonte_id,
                tipo_fonte='lote_resgatavel',
                data_evento=data_pagamento,
                lote_id=lote_id,
                recebido_id=recebido_id,
                produto_key=produto_key,
                produto_nome=produto_nome,
                valor_bruto_disponivel=saldo_bruto,
                valor_liquido_disponivel=valor_liquido_referencia,
                elegivel_na_data_pagamento=elegivel,
                origem_status=origem_status,
                motivo_bloqueio_temporal=motivo,
                observacao_auditavel=observacao,
                data_base_valor=data_referencia,
                metodo_valor_disponivel='fotografia_data_referencia',
                data_recebimento_origem=data_recebimento,
                data_aplicacao_origem=data_aplicacao,
                carencia_ate_origem=carencia_ate,
                origem_estrutura='replay_passado_controlado',
            ))
    return registros


def materializar_saldo_disponivel_geral(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    fontes_elegiveis_pagamento: PacoteFontesElegiveisPagamento,
    *,
    data_referencia: date,
    limiar_valor: float = 0.01,
) -> PacoteSaldoDisponivelGeral:
    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()

    colunas_vazias = [
        'saldo_disponivel_id', 'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
        'saldo_disponivel_bruto', 'saldo_disponivel_liquido', 'saldo_disponivel_elegivel', 'origem_status',
        'origem_saldo', 'qtd_fontes_componentes', 'tipos_fontes_componentes', 'regra_precedencia_intradiaria',
        'restricao_duplicidade_recebidos', 'data_base_saldo', 'metodo_saldo', 'observacao_auditavel',
    ]

    if len(pagamentos_alvo) == 0:
        quadro_vazio = pd.DataFrame(columns=colunas_vazias)
        auditoria = {
            'validacao': {'ok': False, 'erros': ['saldo_disponivel_sem_pagamentos_alvo'], 'avisos': []},
            'resumo': {'total_pagamentos_alvo': 0},
        }
        return PacoteSaldoDisponivelGeral(quadro_saldo_disponivel=quadro_vazio, auditoria=auditoria)

    tipos_caixa = {'recebido_disponivel', 'caixa_pre_aplicacao'}
    quadro_componentes = quadro_fontes[
        quadro_fontes['tipo_fonte'].isin(tipos_caixa)
        & quadro_fontes['elegivel_na_data_pagamento'].eq(True)
    ].copy() if len(quadro_fontes) else pd.DataFrame()

    agregados: dict[str, dict[str, Any]] = {}
    if len(quadro_componentes):
        for pagamento_id, grupo in quadro_componentes.groupby('pagamento_id', sort=False):
            tipos = sorted({limpar_texto(v) for v in grupo['tipo_fonte'].tolist() if limpar_texto(v)})
            status_origem = set(grupo['origem_status'].astype(str).tolist())
            if 'estimado' in status_origem:
                origem_status = 'estimado'
            elif 'parcial' in status_origem:
                origem_status = 'parcial'
            else:
                origem_status = 'confirmado'
            agregados[pagamento_id] = {
                'saldo_disponivel_bruto': round(float(grupo['valor_bruto_disponivel'].sum()), 2),
                'saldo_disponivel_liquido': round(float(grupo['valor_liquido_disponivel'].sum()), 2),
                'qtd_fontes_componentes': int(grupo['fonte_id'].nunique()),
                'tipos_fontes_componentes': ', '.join(tipos),
                'origem_status': origem_status,
                'data_base_saldo': grupo['data_base_valor'].max(),
                'componentes': sorted({limpar_texto(v) for v in grupo['fonte_id'].tolist() if limpar_texto(v)}),
            }

    registros: list[dict[str, Any]] = []
    for pagamento in pagamentos_alvo.to_dict(orient='records'):
        pagamento_id = limpar_texto(pagamento.get('despesa_id'))
        agregado = agregados.get(pagamento_id)
        if agregado is None:
            saldo_bruto = 0.0
            saldo_liquido = 0.0
            elegivel = False
            origem_status = 'ausente'
            origem_saldo = 'sem_caixa_geral_observavel_na_base'
            qtd_componentes = 0
            tipos_componentes = ''
            restricao_duplicidade = False
            data_base_saldo = pagamento.get('data') if pagamento.get('data') is not None and pagamento.get('data') <= data_referencia else data_referencia
            observacao = 'não há saldo disponível geral observável na base atual sem duplicar recebidos ou fontes explícitas já materializadas.'
        else:
            saldo_bruto = agregado['saldo_disponivel_bruto']
            saldo_liquido = agregado['saldo_disponivel_liquido']
            elegivel = saldo_liquido > limiar_valor
            origem_status = agregado['origem_status']
            origem_saldo = 'agregado_fontes_explicitas_observaveis'
            qtd_componentes = agregado['qtd_fontes_componentes']
            tipos_componentes = agregado['tipos_fontes_componentes']
            restricao_duplicidade = True
            data_base_saldo = agregado['data_base_saldo']
            observacao = 'saldo disponível geral agregado apenas de fontes explícitas de caixa já observáveis; não é aditivo com as linhas componentes.'

        registros.append({
            'saldo_disponivel_id': f"saldo_disponivel::{_slug_fonte(pagamento_id)}",
            'pagamento_id': pagamento_id,
            'data_pagamento': pagamento.get('data'),
            'descricao_pagamento': limpar_texto(pagamento.get('descricao')),
            'valor_pagamento': round(float(pagamento.get('valor') or 0.0), 2),
            'saldo_disponivel_bruto': saldo_bruto,
            'saldo_disponivel_liquido': saldo_liquido,
            'saldo_disponivel_elegivel': bool(elegivel),
            'origem_status': origem_status,
            'origem_saldo': origem_saldo,
            'qtd_fontes_componentes': int(qtd_componentes),
            'tipos_fontes_componentes': tipos_componentes,
            'regra_precedencia_intradiaria': 'nao_materializada',
            'restricao_duplicidade_recebidos': bool(restricao_duplicidade),
            'data_base_saldo': data_base_saldo,
            'metodo_saldo': 'agregado_fontes_explicitas_por_pagamento',
            'observacao_auditavel': observacao,
        })

    quadro = pd.DataFrame(registros, columns=colunas_vazias)
    quadro = quadro.sort_values(['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)
    erros: list[str] = []
    avisos: list[str] = []
    if quadro['saldo_disponivel_id'].duplicated().any():
        erros.append('saldo_disponivel_id_duplicado')
    if len(quadro) != len(pagamentos_alvo):
        erros.append('saldo_disponivel_nao_cobre_todos_os_pagamentos_alvo')
    if (quadro['saldo_disponivel_bruto'] < 0).any():
        erros.append('saldo_disponivel_bruto_negativo')
    if (quadro['saldo_disponivel_liquido'] < 0).any():
        erros.append('saldo_disponivel_liquido_negativo')
    if (quadro['origem_status'] == 'ausente').any():
        avisos.append('existem_pagamentos_sem_saldo_disponivel_geral_observavel')
    if (quadro['restricao_duplicidade_recebidos'] == True).any():
        avisos.append('saldo_disponivel_geral_agrega_fontes_explicitas_e_nao_deve_ser_somado_novamente')
    if (quadro['origem_status'] == 'estimado').any():
        avisos.append('existem_saldos_dependentes_de_precedencia_intradiaria_nao_materializada')
    if not quadro['saldo_disponivel_elegivel'].any():
        avisos.append('saldo_disponivel_geral_materializado_sem_valor_elegivel_na_base_atual')

    auditoria = {
        'validacao': {'ok': len(erros) == 0, 'erros': erros, 'avisos': avisos},
        'resumo': {
            'total_pagamentos_alvo': int(len(quadro)),
            'pagamentos_com_saldo_disponivel': int(quadro['saldo_disponivel_elegivel'].sum()),
            'pagamentos_sem_saldo_disponivel': int((~quadro['saldo_disponivel_elegivel']).sum()),
            'valor_total_bruto_disponivel': round(float(quadro.loc[quadro['saldo_disponivel_elegivel'] == True, 'saldo_disponivel_bruto'].sum()), 2),
            'valor_total_liquido_disponivel': round(float(quadro.loc[quadro['saldo_disponivel_elegivel'] == True, 'saldo_disponivel_liquido'].sum()), 2),
            'origem_status': {str(k): int(v) for k, v in quadro['origem_status'].value_counts(dropna=False).to_dict().items()},
            'origem_saldo': {str(k): int(v) for k, v in quadro['origem_saldo'].value_counts(dropna=False).to_dict().items()},
            'saldo_disponivel_materializado': True,
            'saldo_disponivel_componente_fontes_explicitas': int((quadro['qtd_fontes_componentes'] > 0).sum()),
        },
    }
    return PacoteSaldoDisponivelGeral(quadro_saldo_disponivel=quadro, auditoria=auditoria)





def _construir_mapa_produtos_proxy(carteira_canonica: Any | None) -> dict[str, dict[str, Any]]:
    quadro = getattr(carteira_canonica, 'quadro_canonico', None) if carteira_canonica is not None else None
    if quadro is None or len(quadro) == 0:
        return {}

    mapa: dict[str, dict[str, Any]] = {}
    colunas = {
        'produto_key', 'taxa_base_cdi', 'taxa_bonus_cdi', 'prazo_dias', 'carencia_dias', 'liquidez_dias',
        'risco_real', 'familia_produto', 'regime_liquidez', 'papel_produto',
    }
    disponiveis = [c for c in quadro.columns if c in colunas]
    for row in quadro[disponiveis].to_dict(orient='records'):
        produto_key = limpar_texto(row.get('produto_key'))
        if not produto_key:
            continue
        mapa[produto_key] = row
    return mapa


def _valor_float(valor: Any) -> float:
    try:
        return float(valor or 0.0)
    except Exception:
        return 0.0


def _janela_excesso_proxy_v2(valor_pagamento: float) -> float:
    return round(max(500.0, valor_pagamento * 0.25), 2)


def _score_proxy_economico_v2(candidato: dict[str, Any], *, valor_pagamento: float) -> tuple[float, dict[str, float]]:
    tipo_fonte = limpar_texto(candidato.get('tipo_fonte_escolhida'))
    origem_status = limpar_texto(candidato.get('origem_status'))
    valor_disponivel = round(_valor_float(candidato.get('valor_disponivel')), 2)
    produto = candidato.get('produto_proxy') or {}

    base_tipo = {
        'saldo_disponivel_geral': 0.0,
        'saldo_disponivel': 0.0,
        'caixa_pre_aplicacao': 6.0,
        'recebido_disponivel': 9.0,
        'lote_resgatavel': 20.0,
        'nenhuma': 999.0,
    }.get(tipo_fonte, 50.0)
    penalidade_status = {
        'confirmado': 0.0,
        'parcial': 8.0,
        'estimado': 15.0,
        'ausente': 150.0,
        'bloqueado': 200.0,
    }.get(origem_status, 25.0)

    gap = max(valor_pagamento - valor_disponivel, 0.0)
    excesso = max(valor_disponivel - valor_pagamento, 0.0)
    penalidade_gap = 0.0
    if gap > 0:
        penalidade_gap = 120.0 + min((gap / max(valor_pagamento, 1.0)) * 100.0, 200.0)
    penalidade_excesso = min((excesso / max(valor_pagamento, 1.0)) * 12.0, 60.0)

    taxa_base = max(_valor_float(produto.get('taxa_base_cdi')), 0.0)
    taxa_bonus = max(_valor_float(produto.get('taxa_bonus_cdi')), 0.0)
    taxa_total = taxa_base + taxa_bonus
    prazo_dias = max(_valor_float(produto.get('prazo_dias')), 0.0)
    carencia_dias = max(_valor_float(produto.get('carencia_dias')), 0.0)
    liquidez_dias = max(_valor_float(produto.get('liquidez_dias')), 0.0)
    regime_liquidez = limpar_texto(produto.get('regime_liquidez'))

    penalidade_taxa = taxa_total * 10.0 if tipo_fonte == 'lote_resgatavel' else 0.0
    penalidade_prazo = min(prazo_dias / 365.0, 6.0) if tipo_fonte == 'lote_resgatavel' else 0.0
    penalidade_carencia = min(carencia_dias / 180.0, 4.0) if tipo_fonte == 'lote_resgatavel' else 0.0
    penalidade_liquidez = min(liquidez_dias / 30.0, 4.0) if tipo_fonte == 'lote_resgatavel' else 0.0
    penalidade_regime = 3.0 if tipo_fonte == 'lote_resgatavel' and regime_liquidez == 'vencimento' else 0.0

    data_pagamento = candidato.get('data_pagamento')
    data_base_valor = candidato.get('data_base_valor')
    penalidade_fotografia = 2.0 if (
        tipo_fonte == 'lote_resgatavel'
        and limpar_texto(candidato.get('metodo_valor')) == 'fotografia_data_referencia'
        and data_pagamento is not None
        and data_base_valor is not None
        and data_pagamento > data_base_valor
    ) else 0.0

    score = round(
        base_tipo + penalidade_status + penalidade_gap + penalidade_excesso + penalidade_taxa
        + penalidade_prazo + penalidade_carencia + penalidade_liquidez + penalidade_regime + penalidade_fotografia,
        4,
    )
    detalhes = {
        'base_tipo': round(base_tipo, 4),
        'penalidade_status': round(penalidade_status, 4),
        'penalidade_gap': round(penalidade_gap, 4),
        'penalidade_excesso': round(penalidade_excesso, 4),
        'penalidade_taxa': round(penalidade_taxa, 4),
        'penalidade_prazo': round(penalidade_prazo, 4),
        'penalidade_carencia': round(penalidade_carencia, 4),
        'penalidade_liquidez': round(penalidade_liquidez, 4),
        'penalidade_regime': round(penalidade_regime, 4),
        'penalidade_fotografia': round(penalidade_fotografia, 4),
    }
    return score, detalhes


def _janela_excesso_proxy_v3(valor_pagamento: float) -> float:
    return round(max(300.0, valor_pagamento * 0.18), 2)


def _score_proxy_economico_v3(candidato: dict[str, Any], *, valor_pagamento: float) -> tuple[float, dict[str, float]]:
    tipo_fonte = limpar_texto(candidato.get('tipo_fonte_escolhida'))
    origem_status = limpar_texto(candidato.get('origem_status'))
    valor_disponivel = round(_valor_float(candidato.get('valor_disponivel')), 2)
    produto = candidato.get('produto_proxy') or {}

    base_tipo = {
        'saldo_disponivel_geral': 0.0,
        'saldo_disponivel': 0.0,
        'caixa_pre_aplicacao': 5.0,
        'recebido_disponivel': 8.0,
        'lote_resgatavel': 18.0,
        'nenhuma': 999.0,
    }.get(tipo_fonte, 50.0)
    penalidade_status = {
        'confirmado': 0.0,
        'parcial': 10.0,
        'estimado': 18.0,
        'ausente': 150.0,
        'bloqueado': 220.0,
    }.get(origem_status, 30.0)

    gap = max(valor_pagamento - valor_disponivel, 0.0)
    excesso = max(valor_disponivel - valor_pagamento, 0.0)
    cobertura_ratio = min(valor_pagamento / max(valor_disponivel, 1.0), 1.0)
    residual = max(valor_disponivel - valor_pagamento, 0.0)

    penalidade_gap = 0.0
    if gap > 0:
        penalidade_gap = 160.0 + min((gap / max(valor_pagamento, 1.0)) * 220.0, 260.0)

    penalidade_excesso_rel = min((excesso / max(valor_pagamento, 1.0)) * 16.0, 90.0)
    penalidade_excesso_abs = min(excesso / max(valor_pagamento, 1.0) * 4.0, 24.0)

    taxa_base = max(_valor_float(produto.get('taxa_base_cdi')), 0.0)
    taxa_bonus = max(_valor_float(produto.get('taxa_bonus_cdi')), 0.0)
    taxa_total = taxa_base + taxa_bonus
    prazo_dias = max(_valor_float(produto.get('prazo_dias')), 0.0)
    carencia_dias = max(_valor_float(produto.get('carencia_dias')), 0.0)
    liquidez_dias = max(_valor_float(produto.get('liquidez_dias')), 0.0)
    regime_liquidez = limpar_texto(produto.get('regime_liquidez'))
    risco_real = limpar_texto(produto.get('risco_real'))
    papel_produto = limpar_texto(produto.get('papel_produto'))

    penalidade_taxa = taxa_total * 8.0 if tipo_fonte == 'lote_resgatavel' else 0.0
    penalidade_prazo = (min(prazo_dias / 365.0, 8.0) * 0.9) if tipo_fonte == 'lote_resgatavel' else 0.0
    penalidade_carencia = (min(carencia_dias / 180.0, 5.0) * 1.2) if tipo_fonte == 'lote_resgatavel' else 0.0
    penalidade_liquidez = (min(liquidez_dias / 30.0, 5.0) * 1.0) if tipo_fonte == 'lote_resgatavel' else 0.0
    penalidade_regime = 2.0 if tipo_fonte == 'lote_resgatavel' and regime_liquidez == 'vencimento' else 0.0

    ajuste_risco = 0.0
    if tipo_fonte == 'lote_resgatavel':
        ajuste_risco = {
            'baixo': 2.0,
            'médio': 0.0,
            'medio': 0.0,
            'alto': -2.0,
        }.get(risco_real, 0.5)

    penalidade_papel_estrategico = 0.0
    if tipo_fonte == 'lote_resgatavel' and papel_produto in {'ativo_motor', 'núcleo_estrutural', 'nucleo_estrutural'}:
        penalidade_papel_estrategico = 4.0

    indice_estrategico = 0.0
    if tipo_fonte == 'lote_resgatavel':
        indice_estrategico = (
            max(taxa_total - 1.0, 0.0) * 6.0
            + min(prazo_dias / 365.0, 8.0) * 1.5
            + min(carencia_dias / 180.0, 5.0) * 1.3
            + (2.0 if regime_liquidez == 'vencimento' else 0.0)
            + (2.5 if papel_produto in {'ativo_motor', 'núcleo_estrutural', 'nucleo_estrutural'} else 0.0)
        )
    penalidade_destruicao_estrategica = indice_estrategico * max(1.0 - cobertura_ratio, 0.0) * 2.6

    penalidade_fragmentacao_residual = 0.0
    if tipo_fonte == 'lote_resgatavel' and residual > 0:
        limiar_fragmento = max(200.0, valor_pagamento * 0.15)
        if residual < limiar_fragmento:
            penalidade_fragmentacao_residual = 8.0

    data_pagamento = candidato.get('data_pagamento')
    data_base_valor = candidato.get('data_base_valor')
    penalidade_fotografia = 0.0
    if (
        tipo_fonte == 'lote_resgatavel'
        and limpar_texto(candidato.get('metodo_valor')) == 'fotografia_data_referencia'
        and data_pagamento is not None
        and data_base_valor is not None
        and data_pagamento > data_base_valor
    ):
        delta_dias = max((data_pagamento - data_base_valor).days, 0)
        penalidade_fotografia = min(delta_dias * 0.04, 15.0)

    penalidade_horizonte_curto = 0.0
    if tipo_fonte == 'lote_resgatavel' and data_pagamento is not None and data_base_valor is not None:
        delta_dias = max((data_pagamento - data_base_valor).days, 0)
        if delta_dias <= 45 and prazo_dias >= 365:
            penalidade_horizonte_curto = 6.0

    score = round(
        base_tipo
        + penalidade_status
        + penalidade_gap
        + penalidade_excesso_rel
        + penalidade_excesso_abs
        + penalidade_taxa
        + penalidade_prazo
        + penalidade_carencia
        + penalidade_liquidez
        + penalidade_regime
        + ajuste_risco
        + penalidade_papel_estrategico
        + penalidade_destruicao_estrategica
        + penalidade_fragmentacao_residual
        + penalidade_fotografia
        + penalidade_horizonte_curto,
        4,
    )
    detalhes = {
        'base_tipo': round(base_tipo, 4),
        'penalidade_status': round(penalidade_status, 4),
        'penalidade_gap': round(penalidade_gap, 4),
        'penalidade_excesso_rel': round(penalidade_excesso_rel, 4),
        'penalidade_excesso_abs': round(penalidade_excesso_abs, 4),
        'penalidade_taxa': round(penalidade_taxa, 4),
        'penalidade_prazo': round(penalidade_prazo, 4),
        'penalidade_carencia': round(penalidade_carencia, 4),
        'penalidade_liquidez': round(penalidade_liquidez, 4),
        'penalidade_regime': round(penalidade_regime, 4),
        'ajuste_risco': round(ajuste_risco, 4),
        'penalidade_papel_estrategico': round(penalidade_papel_estrategico, 4),
        'penalidade_destruicao_estrategica': round(penalidade_destruicao_estrategica, 4),
        'penalidade_fragmentacao_residual': round(penalidade_fragmentacao_residual, 4),
        'penalidade_fotografia': round(penalidade_fotografia, 4),
        'penalidade_horizonte_curto': round(penalidade_horizonte_curto, 4),
    }
    return score, detalhes


def _prioridade_tipo_fonte(tipo_fonte: str) -> int:
    prioridades = {
        'saldo_disponivel_geral': 0,
        'saldo_disponivel': 0,
        'caixa_pre_aplicacao': 1,
        'recebido_disponivel': 2,
        'lote_resgatavel': 3,
    }
    return prioridades.get(limpar_texto(tipo_fonte), 99)


def _prioridade_status_origem(status: str) -> int:
    prioridades = {
        'confirmado': 0,
        'parcial': 1,
        'estimado': 2,
        'ausente': 98,
        'bloqueado': 99,
    }
    return prioridades.get(limpar_texto(status), 50)


def _janela_excesso_por_proxy(proxy_version: str, valor_pagamento: float) -> float:
    versao = limpar_texto(proxy_version).lower()
    if versao == 'v2':
        return _janela_excesso_proxy_v2(valor_pagamento)
    return _janela_excesso_proxy_v3(valor_pagamento)


def _score_proxy_economico_por_versao(proxy_version: str, candidato: dict[str, Any], *, valor_pagamento: float) -> tuple[float, dict[str, float]]:
    versao = limpar_texto(proxy_version).lower()
    if versao == 'v2':
        return _score_proxy_economico_v2(candidato, valor_pagamento=valor_pagamento)
    return _score_proxy_economico_v3(candidato, valor_pagamento=valor_pagamento)


def _label_proxy_version(proxy_version: str) -> str:
    versao = limpar_texto(proxy_version).lower()
    return 'v2' if versao == 'v2' else 'v3'


def _construir_candidatos_decisao_local_v1(
    pagamento: dict[str, Any],
    quadro_saldo: pd.DataFrame,
    quadro_fontes: pd.DataFrame,
    mapa_produtos_proxy: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    pagamento_id = limpar_texto(pagamento.get('despesa_id'))
    valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)
    candidatos: list[dict[str, Any]] = []

    saldo_pagamento = quadro_saldo[quadro_saldo['pagamento_id'] == pagamento_id].copy() if len(quadro_saldo) else pd.DataFrame()
    for _, row in saldo_pagamento.iterrows():
        valor_disponivel = round(float(row.get('saldo_disponivel_liquido') or row.get('saldo_disponivel_bruto') or 0.0), 2)
        candidatos.append({
            'fonte_escolhida_id': limpar_texto(row.get('saldo_disponivel_id')),
            'tipo_fonte_escolhida': 'saldo_disponivel_geral',
            'valor_disponivel': valor_disponivel,
            'pagamento_totalmente_coberto': bool(valor_disponivel >= valor_pagamento and bool(row.get('saldo_disponivel_elegivel', False))),
            'elegivel': bool(row.get('saldo_disponivel_elegivel', False)),
            'origem_status': limpar_texto(row.get('origem_status')),
            'data_base_valor': row.get('data_base_saldo'),
            'data_pagamento': pagamento.get('data'),
            'motivo_bloqueio': None if bool(row.get('saldo_disponivel_elegivel', False)) else limpar_texto(row.get('origem_saldo')) or 'saldo_disponivel_inexistente_ou_nao_elegivel',
            'observacao': limpar_texto(row.get('observacao_auditavel')),
            'custo_economico_proxy': 0.0,
            'produto_key': None,
            'produto_proxy': {},
            'lote_id': None,
            'recebido_id': None,
            'metodo_valor': limpar_texto(row.get('metodo_saldo')),
            'fonte_base_escolhida': 'saldo_disponivel_geral',
            'lote_id': None,
            'recebido_id': None,
        })

    fontes_pagamento = quadro_fontes[quadro_fontes['pagamento_id'] == pagamento_id].copy() if len(quadro_fontes) else pd.DataFrame()
    for _, row in fontes_pagamento.iterrows():
        elegivel = bool(row.get('elegivel_na_data_pagamento', False))
        valor_disponivel = round(float(row.get('valor_liquido_disponivel') or row.get('valor_bruto_disponivel') or 0.0), 2)
        tipo_fonte = limpar_texto(row.get('tipo_fonte'))
        produto_key = limpar_texto(row.get('produto_key')) or None
        candidatos.append({
            'fonte_escolhida_id': limpar_texto(row.get('fonte_pagamento_id')),
            'tipo_fonte_escolhida': tipo_fonte,
            'valor_disponivel': valor_disponivel,
            'pagamento_totalmente_coberto': bool(elegivel and valor_disponivel >= valor_pagamento),
            'elegivel': elegivel,
            'origem_status': limpar_texto(row.get('origem_status')),
            'data_base_valor': row.get('data_base_valor'),
            'data_pagamento': pagamento.get('data'),
            'motivo_bloqueio': limpar_texto(row.get('motivo_bloqueio_temporal')) or None,
            'observacao': limpar_texto(row.get('observacao_auditavel')),
            'custo_economico_proxy': None,
            'produto_key': produto_key,
            'produto_proxy': mapa_produtos_proxy.get(produto_key or '', {}),
            'lote_id': normalizar_identificador(row.get('lote_id')) or None,
            'recebido_id': limpar_texto(row.get('recebido_id')) or None,
            'metodo_valor': limpar_texto(row.get('metodo_valor_disponivel')),
            'fonte_base_escolhida': limpar_texto(row.get('fonte_id')) or tipo_fonte,
        })
    return candidatos


def _selecionar_candidato_decisao_local_v1(
    candidatos: list[dict[str, Any]],
    *,
    valor_pagamento: float,
    proxy_version: str = 'v3',
) -> tuple[dict[str, Any], str, str]:
    label_proxy = _label_proxy_version(proxy_version)
    if not candidatos:
        return ({
            'fonte_escolhida_id': 'sem_fonte_elegivel',
            'tipo_fonte_escolhida': 'nenhuma',
            'valor_disponivel': 0.0,
            'pagamento_totalmente_coberto': False,
            'elegivel': False,
            'origem_status': 'ausente',
            'data_base_valor': None,
            'motivo_bloqueio': 'nao_ha_fontes_materializadas_para_o_pagamento',
            'observacao': 'não há fontes materializadas para o pagamento nesta etapa.',
            'custo_economico_proxy': None,
        }, 'sem_fonte_elegivel', 'não há fontes materializadas para o pagamento nesta etapa.')

    elegiveis = [c for c in candidatos if c.get('elegivel')]
    if not elegiveis:
        escolhido = sorted(
            candidatos,
            key=lambda c: (
                _prioridade_status_origem(c.get('origem_status', 'ausente')),
                _prioridade_tipo_fonte(c.get('tipo_fonte_escolhida', 'nenhuma')),
                -float(c.get('valor_disponivel') or 0.0),
                limpar_texto(c.get('fonte_escolhida_id')),
            ),
        )[0]
        return escolhido, 'sem_fonte_elegivel_na_data', 'todas as fontes materializadas para o pagamento estão bloqueadas ou ausentes na data.'

    elegiveis_cobertura_total = [c for c in elegiveis if c.get('pagamento_totalmente_coberto')]
    janela_excesso = _janela_excesso_por_proxy(label_proxy, valor_pagamento)
    if elegiveis_cobertura_total:
        min_excesso = min(max(float(c.get('valor_disponivel') or 0.0) - valor_pagamento, 0.0) for c in elegiveis_cobertura_total)
        pool = [
            c for c in elegiveis_cobertura_total
            if max(float(c.get('valor_disponivel') or 0.0) - valor_pagamento, 0.0) <= min_excesso + janela_excesso
        ]
        criterio = f'proxy_economico_{label_proxy}_com_cobertura_total'
    else:
        pool = list(elegiveis)
        criterio = f'proxy_economico_{label_proxy}_com_cobertura_parcial'

    melhor_score = None
    escolhido = None
    melhor_detalhe: dict[str, float] = {}
    for candidato in pool:
        score, detalhes = _score_proxy_economico_por_versao(label_proxy, candidato, valor_pagamento=valor_pagamento)
        candidato['custo_economico_proxy'] = score
        candidato['proxy_componentes'] = detalhes
        candidato['excesso_relativo'] = round(max(float(candidato.get('valor_disponivel') or 0.0) - valor_pagamento, 0.0), 2)
        chave = (
            score,
            max(float(candidato.get('valor_disponivel') or 0.0) - valor_pagamento, 0.0),
            _prioridade_status_origem(candidato.get('origem_status', 'ausente')),
            limpar_texto(candidato.get('fonte_escolhida_id')),
        )
        if melhor_score is None or chave < melhor_score:
            melhor_score = chave
            escolhido = candidato
            melhor_detalhe = detalhes

    assert escolhido is not None
    if escolhido.get('tipo_fonte_escolhida') == 'saldo_disponivel_geral':
        criterio += '__caixa_geral'
    elif escolhido.get('tipo_fonte_escolhida') in {'caixa_pre_aplicacao', 'recebido_disponivel'}:
        criterio += '__caixa_explicito'
    elif escolhido.get('tipo_fonte_escolhida') == 'lote_resgatavel':
        criterio += '__resgate_otimizado_proxy'

    score_txt = f"score={float(escolhido.get('custo_economico_proxy') or 0.0):.4f}"
    if bool(escolhido.get('pagamento_totalmente_coberto')):
        observacao = (
            f'fonte escolhida cobre integralmente o pagamento e foi selecionada pelo proxy econômico {label_proxy} '
            f'dentro de uma janela de excesso de até {janela_excesso:.2f}. {score_txt}.'
        )
    else:
        observacao = (
            f'fonte escolhida é a melhor elegível observável pelo proxy econômico {label_proxy}, mas não cobre integralmente o pagamento nesta etapa. '
            f'{score_txt}.'
        )
    if melhor_detalhe:
        componentes = ', '.join([f"{k}={v:.2f}" for k, v in melhor_detalhe.items() if v])
        if componentes:
            observacao += f' Componentes relevantes: {componentes}.'
    return escolhido, criterio, observacao


def materializar_decisao_local_v1(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    fontes_elegiveis_pagamento: PacoteFontesElegiveisPagamento,
    saldo_disponivel_geral: PacoteSaldoDisponivelGeral,
    *,
    data_referencia: date,
    carteira_canonica: Any | None = None,
    proxy_version: str = 'v3',
) -> PacoteDecisaoLocalV1:
    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    colunas = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'fonte_escolhida_id', 'fonte_base_escolhida', 'lote_id_escolhido', 'recebido_id_escolhido', 'tipo_fonte_escolhida', 'criterio_decisao',
        'custo_economico_proxy', 'observacao_auditavel', 'valor_disponivel_escolhido', 'pagamento_totalmente_coberto', 'fonte_origem_status',
        'fonte_elegivel_na_data', 'data_base_valor_escolhido', 'motivo_bloqueio_ou_restricao',
    ]
    if len(pagamentos_alvo) == 0:
        quadro_vazio = pd.DataFrame(columns=colunas)
        auditoria = {'validacao': {'ok': False, 'erros': ['decisao_local_v1_sem_pagamentos_alvo'], 'avisos': []}, 'resumo': {'total_pagamentos_alvo': 0}}
        return PacoteDecisaoLocalV1(quadro_decisao_local_v1=quadro_vazio, auditoria=auditoria)

    label_proxy = _label_proxy_version(proxy_version)
    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    quadro_saldo = saldo_disponivel_geral.quadro_saldo_disponivel.copy()
    mapa_produtos_proxy = _construir_mapa_produtos_proxy(carteira_canonica)
    registros=[]
    for pagamento in pagamentos_alvo.to_dict(orient='records'):
        pagamento_id = limpar_texto(pagamento.get('despesa_id'))
        candidatos = _construir_candidatos_decisao_local_v1(pagamento, quadro_saldo, quadro_fontes, mapa_produtos_proxy)
        escolhido, criterio_decisao, observacao_base = _selecionar_candidato_decisao_local_v1(candidatos, valor_pagamento=round(float(pagamento.get('valor') or 0.0), 2), proxy_version=label_proxy)
        obs=[observacao_base]
        if limpar_texto(escolhido.get('observacao')):
            obs.append(limpar_texto(escolhido.get('observacao')))
        if escolhido.get('tipo_fonte_escolhida') == 'saldo_disponivel_geral':
            obs.append('saldo disponível geral é uma síntese de fontes explícitas observáveis e não deve ser somado novamente às suas componentes.')
        registros.append({
            'pagamento_id': pagamento_id,
            'data_pagamento': pagamento.get('data'),
            'descricao_pagamento': limpar_texto(pagamento.get('descricao')),
            'valor_pagamento': round(float(pagamento.get('valor') or 0.0),2),
            'fonte_escolhida_id': limpar_texto(escolhido.get('fonte_escolhida_id')),
            'fonte_base_escolhida': limpar_texto(escolhido.get('fonte_base_escolhida')),
            'lote_id_escolhido': normalizar_identificador(escolhido.get('lote_id')) or None,
            'recebido_id_escolhido': limpar_texto(escolhido.get('recebido_id')) or None,
            'tipo_fonte_escolhida': limpar_texto(escolhido.get('tipo_fonte_escolhida')),
            'criterio_decisao': criterio_decisao,
            'custo_economico_proxy': round(float(escolhido.get('custo_economico_proxy') or 0.0), 4) if escolhido.get('custo_economico_proxy') is not None else None,
            'observacao_auditavel': ' '.join([o for o in obs if o]).strip(),
            'valor_disponivel_escolhido': round(float(escolhido.get('valor_disponivel') or 0.0),2),
            'pagamento_totalmente_coberto': bool(escolhido.get('pagamento_totalmente_coberto', False)),
            'fonte_origem_status': limpar_texto(escolhido.get('origem_status')),
            'fonte_elegivel_na_data': bool(escolhido.get('elegivel', False)),
            'data_base_valor_escolhido': escolhido.get('data_base_valor'),
            'motivo_bloqueio_ou_restricao': limpar_texto(escolhido.get('motivo_bloqueio')) or None,
        })

    quadro = pd.DataFrame(registros, columns=colunas).sort_values(['data_pagamento','pagamento_id'], kind='stable').reset_index(drop=True)
    erros=[]
    avisos=[]
    if quadro['pagamento_id'].duplicated().any():
        erros.append('decisao_local_v1_pagamento_duplicado')
    if len(quadro) != len(pagamentos_alvo):
        erros.append('decisao_local_v1_nao_cobre_todos_os_pagamentos_alvo')
    if quadro['fonte_escolhida_id'].isna().any() or (quadro['fonte_escolhida_id'].astype(str).str.strip()=='').any():
        erros.append('decisao_local_v1_sem_fonte_escolhida_id')
    if (quadro['valor_disponivel_escolhido'] < 0).any():
        erros.append('decisao_local_v1_valor_disponivel_negativo')
    if (~quadro['pagamento_totalmente_coberto']).any():
        avisos.append('existem_pagamentos_sem_cobertura_integral_na_decisao_local_v1')
    if (quadro['tipo_fonte_escolhida'] == 'lote_resgatavel').any():
        avisos.append('existem_pagamentos_em_que_a_decisao_local_v1_precisou_resgatar_lote')
    if (quadro['tipo_fonte_escolhida'] == 'saldo_disponivel_geral').any():
        avisos.append('existem_pagamentos_em_que_a_decisao_local_v1_escolheu_caixa_geral_aggregado')
    if (quadro['fonte_origem_status'] == 'estimado').any():
        avisos.append('existem_decisoes_dependentes_de_precedencia_intradiaria_nao_materializada')
    if (quadro['tipo_fonte_escolhida'] == 'nenhuma').any() or (quadro['fonte_origem_status'] == 'ausente').any():
        avisos.append('existem_pagamentos_sem_fonte_elegivel_observavel_na_decisao_local_v1')

    auditoria={
        'validacao': {'ok': len(erros)==0, 'erros': erros, 'avisos': avisos},
        'resumo': {
            'total_pagamentos_alvo': int(len(quadro)),
            'pagamentos_totalmente_cobertos': int(quadro['pagamento_totalmente_coberto'].sum()),
            'pagamentos_parcialmente_cobertos_ou_sem_fonte': int((~quadro['pagamento_totalmente_coberto']).sum()),
            'tipo_fonte_escolhida': {str(k): int(v) for k,v in quadro['tipo_fonte_escolhida'].value_counts(dropna=False).to_dict().items()},
            'criterio_decisao': {str(k): int(v) for k,v in quadro['criterio_decisao'].value_counts(dropna=False).to_dict().items()},
            'fonte_origem_status': {str(k): int(v) for k,v in quadro['fonte_origem_status'].value_counts(dropna=False).to_dict().items()},
            'fonte_base_escolhida': {str(k): int(v) for k,v in quadro['fonte_base_escolhida'].value_counts(dropna=False).to_dict().items()},
            'lote_id_escolhido': {str(k): int(v) for k,v in quadro['lote_id_escolhido'].dropna().value_counts(dropna=False).to_dict().items()},
            'valor_total_pagamentos': round(float(quadro['valor_pagamento'].sum()),2),
            'valor_total_coberto_pelas_fontes_escolhidas': round(float(quadro[['valor_pagamento','valor_disponivel_escolhido']].min(axis=1).sum()),2),
            'decisao_local_v1_materializada': True,
            'proxy_version': label_proxy,
            'proxy_economico_v2_ativo': label_proxy == 'v2',
            'proxy_economico_v3_ativo': label_proxy == 'v3',
        },
    }
    return PacoteDecisaoLocalV1(quadro_decisao_local_v1=quadro, auditoria=auditoria)


def auditar_comparativo_proxy_v2_v3(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    fontes_elegiveis_pagamento: PacoteFontesElegiveisPagamento,
    saldo_disponivel_geral: PacoteSaldoDisponivelGeral,
    *,
    data_referencia: date,
    carteira_canonica: Any | None = None,
) -> dict[str, Any]:
    pacote_v2 = materializar_decisao_local_v1(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        saldo_disponivel_geral,
        data_referencia=data_referencia,
        carteira_canonica=carteira_canonica,
        proxy_version='v2',
    )
    pacote_v3 = materializar_decisao_local_v1(
        dados_operacionais,
        fontes_elegiveis_pagamento,
        saldo_disponivel_geral,
        data_referencia=data_referencia,
        carteira_canonica=carteira_canonica,
        proxy_version='v3',
    )
    q2 = pacote_v2.quadro_decisao_local_v1.copy().rename(columns={
        'fonte_escolhida_id': 'fonte_escolhida_id_v2',
        'fonte_base_escolhida': 'fonte_base_escolhida_v2',
        'lote_id_escolhido': 'lote_id_escolhido_v2',
        'recebido_id_escolhido': 'recebido_id_escolhido_v2',
        'tipo_fonte_escolhida': 'tipo_fonte_escolhida_v2',
        'criterio_decisao': 'criterio_decisao_v2',
        'custo_economico_proxy': 'custo_economico_proxy_v2',
        'observacao_auditavel': 'observacao_auditavel_v2',
        'valor_disponivel_escolhido': 'valor_disponivel_escolhido_v2',
        'pagamento_totalmente_coberto': 'pagamento_totalmente_coberto_v2',
        'fonte_origem_status': 'fonte_origem_status_v2',
        'fonte_elegivel_na_data': 'fonte_elegivel_na_data_v2',
        'data_base_valor_escolhido': 'data_base_valor_escolhido_v2',
        'motivo_bloqueio_ou_restricao': 'motivo_bloqueio_ou_restricao_v2',
    })
    q3 = pacote_v3.quadro_decisao_local_v1.copy().rename(columns={
        'fonte_escolhida_id': 'fonte_escolhida_id_v3',
        'fonte_base_escolhida': 'fonte_base_escolhida_v3',
        'lote_id_escolhido': 'lote_id_escolhido_v3',
        'recebido_id_escolhido': 'recebido_id_escolhido_v3',
        'tipo_fonte_escolhida': 'tipo_fonte_escolhida_v3',
        'criterio_decisao': 'criterio_decisao_v3',
        'custo_economico_proxy': 'custo_economico_proxy_v3',
        'observacao_auditavel': 'observacao_auditavel_v3',
        'valor_disponivel_escolhido': 'valor_disponivel_escolhido_v3',
        'pagamento_totalmente_coberto': 'pagamento_totalmente_coberto_v3',
        'fonte_origem_status': 'fonte_origem_status_v3',
        'fonte_elegivel_na_data': 'fonte_elegivel_na_data_v3',
        'data_base_valor_escolhido': 'data_base_valor_escolhido_v3',
        'motivo_bloqueio_ou_restricao': 'motivo_bloqueio_ou_restricao_v3',
    })
    comparativo = q2.merge(q3, on=['pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento'], how='outer', validate='one_to_one')
    comparativo['mudou_fonte'] = comparativo['fonte_escolhida_id_v2'].fillna('') != comparativo['fonte_escolhida_id_v3'].fillna('')
    comparativo['mudou_lote'] = comparativo['lote_id_escolhido_v2'].fillna('') != comparativo['lote_id_escolhido_v3'].fillna('')
    comparativo['mudou_criterio'] = comparativo['criterio_decisao_v2'].fillna('') != comparativo['criterio_decisao_v3'].fillna('')
    comparativo['delta_score_bruto_incomparavel'] = (comparativo['custo_economico_proxy_v3'].fillna(0.0) - comparativo['custo_economico_proxy_v2'].fillna(0.0)).round(4)
    comparativo['delta_valor_disponivel_escolhido'] = (comparativo['valor_disponivel_escolhido_v3'].fillna(0.0) - comparativo['valor_disponivel_escolhido_v2'].fillna(0.0)).round(2)

    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    quadro_saldo = saldo_disponivel_geral.quadro_saldo_disponivel.copy()
    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    mapa_produtos_proxy = _construir_mapa_produtos_proxy(carteira_canonica)
    score_comum_v2_escolha_v2 = []
    score_comum_v2_escolha_v3 = []
    score_comum_v3_escolha_v2 = []
    score_comum_v3_escolha_v3 = []
    for linha in comparativo.to_dict(orient='records'):
        pagamento_id = limpar_texto(linha.get('pagamento_id'))
        pagamento_row = pagamentos_alvo.loc[pagamentos_alvo['despesa_id'] == pagamento_id]
        if len(pagamento_row) == 0:
            score_comum_v2_escolha_v2.append(None)
            score_comum_v2_escolha_v3.append(None)
            score_comum_v3_escolha_v2.append(None)
            score_comum_v3_escolha_v3.append(None)
            continue
        pagamento = pagamento_row.iloc[0].to_dict()
        candidatos = _construir_candidatos_decisao_local_v1(pagamento, quadro_saldo, quadro_fontes, mapa_produtos_proxy)
        mapa_candidatos = {limpar_texto(c.get('fonte_escolhida_id')): c for c in candidatos}
        valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)

        candidato_v2 = mapa_candidatos.get(limpar_texto(linha.get('fonte_escolhida_id_v2')))
        candidato_v3 = mapa_candidatos.get(limpar_texto(linha.get('fonte_escolhida_id_v3')))

        if candidato_v2 is not None:
            score_v2_v2, _ = _score_proxy_economico_v2(candidato_v2, valor_pagamento=valor_pagamento)
            score_v3_v2, _ = _score_proxy_economico_v3(candidato_v2, valor_pagamento=valor_pagamento)
        else:
            score_v2_v2 = None
            score_v3_v2 = None
        if candidato_v3 is not None:
            score_v2_v3, _ = _score_proxy_economico_v2(candidato_v3, valor_pagamento=valor_pagamento)
            score_v3_v3, _ = _score_proxy_economico_v3(candidato_v3, valor_pagamento=valor_pagamento)
        else:
            score_v2_v3 = None
            score_v3_v3 = None

        score_comum_v2_escolha_v2.append(score_v2_v2)
        score_comum_v2_escolha_v3.append(score_v2_v3)
        score_comum_v3_escolha_v2.append(score_v3_v2)
        score_comum_v3_escolha_v3.append(score_v3_v3)

    comparativo['score_comum_v2_escolha_v2'] = score_comum_v2_escolha_v2
    comparativo['score_comum_v2_escolha_v3'] = score_comum_v2_escolha_v3
    comparativo['delta_score_comum_v2'] = (comparativo['score_comum_v2_escolha_v3'].fillna(0.0) - comparativo['score_comum_v2_escolha_v2'].fillna(0.0)).round(4)
    comparativo['classificacao_delta_score_comum_v2'] = comparativo['delta_score_comum_v2'].map(lambda x: 'v3_melhor' if x < 0 else ('v3_pior' if x > 0 else 'igual'))
    comparativo['score_comum_v3_escolha_v2'] = score_comum_v3_escolha_v2
    comparativo['score_comum_v3_escolha_v3'] = score_comum_v3_escolha_v3
    comparativo['delta_score_comum_v3'] = (comparativo['score_comum_v3_escolha_v3'].fillna(0.0) - comparativo['score_comum_v3_escolha_v2'].fillna(0.0)).round(4)
    comparativo['classificacao_delta_score_comum_v3'] = comparativo['delta_score_comum_v3'].map(lambda x: 'v3_melhor' if x < 0 else ('v3_pior' if x > 0 else 'igual'))

    comparativo = comparativo.sort_values(['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)
    mudancas = comparativo.loc[comparativo['mudou_fonte'] | comparativo['mudou_lote'] | comparativo['mudou_criterio']].copy()
    resumo = {
        'total_pagamentos': int(len(comparativo)),
        'pagamentos_com_mesma_fonte': int((~comparativo['mudou_fonte']).sum()),
        'pagamentos_com_fonte_alterada': int(comparativo['mudou_fonte'].sum()),
        'pagamentos_com_lote_alterado': int(comparativo['mudou_lote'].sum()),
        'pagamentos_com_criterio_alterado': int(comparativo['mudou_criterio'].sum()),
        'delta_score_comum_v2_total': round(float(comparativo['delta_score_comum_v2'].sum()), 4),
        'delta_score_comum_v2_medio': round(float(comparativo['delta_score_comum_v2'].mean()), 4) if len(comparativo) else 0.0,
        'delta_score_comum_v3_total': round(float(comparativo['delta_score_comum_v3'].sum()), 4),
        'delta_score_comum_v3_medio': round(float(comparativo['delta_score_comum_v3'].mean()), 4) if len(comparativo) else 0.0,
        'classificacao_delta_score_comum_v2': {str(k): int(v) for k, v in comparativo['classificacao_delta_score_comum_v2'].value_counts(dropna=False).to_dict().items()},
        'classificacao_delta_score_comum_v3': {str(k): int(v) for k, v in comparativo['classificacao_delta_score_comum_v3'].value_counts(dropna=False).to_dict().items()},
        'lote_id_escolhido_v2': {str(k): int(v) for k, v in comparativo['lote_id_escolhido_v2'].dropna().value_counts(dropna=False).to_dict().items()},
        'lote_id_escolhido_v3': {str(k): int(v) for k, v in comparativo['lote_id_escolhido_v3'].dropna().value_counts(dropna=False).to_dict().items()},
        'criterio_decisao_v2': {str(k): int(v) for k, v in comparativo['criterio_decisao_v2'].value_counts(dropna=False).to_dict().items()},
        'criterio_decisao_v3': {str(k): int(v) for k, v in comparativo['criterio_decisao_v3'].value_counts(dropna=False).to_dict().items()},
        'pagamentos_totalmente_cobertos_v2': int(comparativo['pagamento_totalmente_coberto_v2'].fillna(False).sum()),
        'pagamentos_totalmente_cobertos_v3': int(comparativo['pagamento_totalmente_coberto_v3'].fillna(False).sum()),
    }
    return {
        'pacote_v2': pacote_v2,
        'pacote_v3': pacote_v3,
        'quadro_comparativo': comparativo,
        'quadro_mudancas': mudancas,
        'auditoria': {'validacao': {'ok': True, 'erros': [], 'avisos': []}, 'resumo': resumo},
    }


def materializar_fontes_elegiveis_pagamento(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    recebidos_auditaveis: PacoteRecebidosAuditaveis,
    replay_passado: Any,
    *,
    data_referencia: date,
    tabela_iof: list[float] | None = None,
    faixas_ir: list[dict[str, Any]] | None = None,
    limiar_valor: float = 0.01,
) -> PacoteFontesElegiveisPagamento:
    inventario = dados_operacionais.inventario_canonico.copy()
    inventario_por_lote = _indexar_inventario_por_lote(inventario)
    quadro_recebidos = recebidos_auditaveis.quadro_recebidos_auditaveis.copy()
    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)

    registros: list[dict[str, Any]] = []
    registros.extend(
        _materializar_fontes_de_recebidos_por_pagamento(
            quadro_recebidos,
            pagamentos_alvo,
            data_referencia=data_referencia,
            limiar_valor=limiar_valor,
        )
    )
    registros.extend(
        _materializar_fontes_de_replay_por_pagamento(
            getattr(replay_passado, 'lotes_apos_replay', []) if replay_passado is not None else [],
            inventario_por_lote,
            pagamentos_alvo,
            data_referencia=data_referencia,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            limiar_valor=limiar_valor,
        )
    )

    quadro = pd.DataFrame(registros)
    avisos_base = ['saldo_disponivel_ainda_nao_materializado']
    if len(pagamentos_alvo) == 0:
        avisos_base.append('nao_ha_pagamentos_futuros_ou_pendentes_para_f1_4')
    if len(quadro) == 0:
        auditoria = {
            'validacao': {'ok': False, 'erros': ['fontes_elegiveis_vazio'], 'avisos': avisos_base},
            'resumo': {
                'total_pagamentos_alvo': int(len(pagamentos_alvo)),
            },
        }
        return PacoteFontesElegiveisPagamento(quadro_fontes_elegiveis=quadro, auditoria=auditoria)

    quadro = quadro.sort_values(['data_pagamento', 'pagamento_id', 'tipo_fonte', 'origem_status', 'lote_id', 'recebido_id'], kind='stable').reset_index(drop=True)
    erros: list[str] = []
    avisos: list[str] = list(avisos_base)
    if quadro['fonte_pagamento_id'].duplicated().any():
        erros.append('fonte_pagamento_id_duplicado')
    if quadro['pagamento_id'].isna().any() or (quadro['pagamento_id'].astype(str).str.strip() == '').any():
        erros.append('pagamento_id_nulo_ou_vazio')
    if quadro['data_pagamento'].isna().any():
        erros.append('data_pagamento_nula')
    if quadro['data_evento'].isna().any():
        erros.append('data_evento_nula')
    if (quadro['valor_bruto_disponivel'] <= 0).any():
        erros.append('valor_bruto_disponivel_nao_positivo')
    if (quadro['valor_liquido_disponivel'] <= 0).any():
        erros.append('valor_liquido_disponivel_nao_positivo')
    if 'saldo_disponivel' not in set(quadro['tipo_fonte'].tolist()):
        avisos.append('saldo_disponivel_ainda_nao_materializado')
    if (quadro['origem_status'] == 'bloqueado').any():
        avisos.append('existem_fontes_bloqueadas_por_restricao_operacional')
    if (quadro['origem_status'] == 'parcial').any():
        avisos.append('existem_fontes_parciais_em_janela_pre_aplicacao')
    if (quadro['origem_status'] == 'estimado').any():
        avisos.append('existem_fontes_dependentes_de_precedencia_intradiaria_nao_materializada')
    if (quadro['metodo_valor_disponivel'] == 'fotografia_data_referencia').any():
        avisos.append('valores_de_lotes_futuros_ainda_em_fotografia_da_data_de_referencia')

    resumo_tipos = {str(k): int(v) for k, v in quadro['tipo_fonte'].value_counts(dropna=False).to_dict().items()}
    resumo_status = {str(k): int(v) for k, v in quadro['origem_status'].value_counts(dropna=False).to_dict().items()}
    resumo_elegibilidade = {str(k): int(v) for k, v in quadro['elegivel_na_data_pagamento'].value_counts(dropna=False).to_dict().items()}
    pagamentos_com_fonte = quadro.groupby('pagamento_id', sort=False)['elegivel_na_data_pagamento'].any()
    auditoria = {
        'validacao': {'ok': len(erros) == 0, 'erros': erros, 'avisos': sorted(set(avisos))},
        'resumo': {
            'total_pagamentos_alvo': int(len(pagamentos_alvo)),
            'total_fontes_pagamento': int(len(quadro)),
            'datas_pagamento_mapeadas': int(quadro['data_pagamento'].nunique()),
            'data_primeiro_pagamento': pagamentos_alvo['data'].min() if len(pagamentos_alvo) else None,
            'data_ultimo_pagamento': pagamentos_alvo['data'].max() if len(pagamentos_alvo) else None,
            'tipo_fonte': resumo_tipos,
            'origem_status': resumo_status,
            'elegivel_na_data_pagamento': resumo_elegibilidade,
            'valor_total_bruto_disponivel': round(float(quadro.loc[quadro['elegivel_na_data_pagamento'] == True, 'valor_bruto_disponivel'].sum()), 2),
            'valor_total_liquido_disponivel': round(float(quadro.loc[quadro['elegivel_na_data_pagamento'] == True, 'valor_liquido_disponivel'].sum()), 2),
            'pagamentos_com_alguma_fonte_elegivel': int(pagamentos_com_fonte.sum()),
            'pagamentos_sem_fonte_elegivel': int((~pagamentos_com_fonte).sum()),
            'fontes_confirmadas': int((quadro['origem_status'] == 'confirmado').sum()),
            'fontes_parciais': int((quadro['origem_status'] == 'parcial').sum()),
            'fontes_estimadas': int((quadro['origem_status'] == 'estimado').sum()),
            'fontes_bloqueadas': int((quadro['origem_status'] == 'bloqueado').sum()),
            'fontes_lote_resgatavel': int((quadro['tipo_fonte'] == 'lote_resgatavel').sum()),
            'fontes_recebido_disponivel': int((quadro['tipo_fonte'] == 'recebido_disponivel').sum()),
            'fontes_caixa_pre_aplicacao': int((quadro['tipo_fonte'] == 'caixa_pre_aplicacao').sum()),
            'saldo_disponivel_materializado': bool((quadro['tipo_fonte'] == 'saldo_disponivel').any()),
        },
    }
    return PacoteFontesElegiveisPagamento(quadro_fontes_elegiveis=quadro, auditoria=auditoria)


def auditar_comparativo_proxy_v3_vs_hibrido_shadow(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    fontes_elegiveis_pagamento: PacoteFontesElegiveisPagamento,
    saldo_disponivel_geral: PacoteSaldoDisponivelGeral,
    decisao_local_v1: PacoteDecisaoLocalV1,
    resolver_hibrido_5p_shadow: Any,
    *,
    data_referencia: date,
    carteira_canonica: Any | None = None,
) -> dict[str, Any]:
    quadro_local = decisao_local_v1.quadro_decisao_local_v1.copy().rename(columns={
        'fonte_escolhida_id': 'fonte_escolhida_id_local_v3',
        'fonte_base_escolhida': 'fonte_base_escolhida_local_v3',
        'lote_id_escolhido': 'lote_id_escolhido_local_v3',
        'recebido_id_escolhido': 'recebido_id_escolhido_local_v3',
        'tipo_fonte_escolhida': 'tipo_fonte_escolhida_local_v3',
        'criterio_decisao': 'criterio_decisao_local_v3',
        'custo_economico_proxy': 'custo_economico_proxy_local_v3',
        'observacao_auditavel': 'observacao_auditavel_local_v3',
        'valor_disponivel_escolhido': 'valor_disponivel_escolhido_local_v3',
        'pagamento_totalmente_coberto': 'pagamento_totalmente_coberto_local_v3',
        'fonte_origem_status': 'fonte_origem_status_local_v3',
        'fonte_elegivel_na_data': 'fonte_elegivel_na_data_local_v3',
        'data_base_valor_escolhido': 'data_base_valor_escolhido_local_v3',
        'motivo_bloqueio_ou_restricao': 'motivo_bloqueio_ou_restricao_local_v3',
    })
    quadro_bench = resolver_hibrido_5p_shadow.quadro_pagamentos_benchmark.copy().rename(columns={
        'status_benchmark': 'status_benchmark_shadow',
        'motivo_status': 'motivo_status_shadow',
        'qtd_lotes_candidatos': 'qtd_lotes_candidatos_shadow',
        'qtd_lotes_usados_hibrido': 'qtd_lotes_usados_hibrido_shadow',
        'valor_bruto_total_hibrido': 'valor_bruto_total_hibrido_shadow',
        'valor_liquido_total_hibrido': 'valor_liquido_total_hibrido_shadow',
        'custo_total_proxy_hibrido': 'custo_total_proxy_hibrido_shadow',
        'benchmark_totalmente_coberto': 'benchmark_totalmente_coberto_shadow',
        'lote_principal_hibrido': 'lote_principal_hibrido_shadow',
        'lote_principal_local_v1': 'lote_principal_local_v1_shadow',
        'tipo_fonte_local_v1': 'tipo_fonte_local_v1_shadow',
        'diverge_decisao_local_v1': 'diverge_decisao_local_v1_shadow',
        'bruto_monofonte_local_estimado': 'bruto_monofonte_local_estimado_shadow',
        'delta_bruto_hibrido_vs_local': 'delta_bruto_hibrido_vs_local_shadow',
        'observacao_auditavel': 'observacao_auditavel_shadow',
    })
    comparativo = quadro_local.merge(
        quadro_bench,
        on=['pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento'],
        how='outer',
        validate='one_to_one',
    )

    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    quadro_saldo = saldo_disponivel_geral.quadro_saldo_disponivel.copy()
    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    mapa_produtos_proxy = _construir_mapa_produtos_proxy(carteira_canonica)

    score_local_comum = []
    score_benchmark_principal = []
    delta_score_principal = []
    classif_score = []
    excesso_local = []
    excesso_bench = []
    delta_excesso = []
    classif_excesso = []
    mudou_lote_principal = []
    divergencia_material = []

    for linha in comparativo.to_dict(orient='records'):
        pagamento_id = limpar_texto(linha.get('pagamento_id'))
        pagamento_row = pagamentos_alvo.loc[pagamentos_alvo['despesa_id'] == pagamento_id]
        if len(pagamento_row) == 0:
            score_local_comum.append(None)
            score_benchmark_principal.append(None)
            delta_score_principal.append(None)
            classif_score.append('indisponivel')
            excesso_local.append(None)
            excesso_bench.append(None)
            delta_excesso.append(None)
            classif_excesso.append('indisponivel')
            lote_local = normalizar_identificador(linha.get('lote_id_escolhido_local_v3')) or ''
            lote_bench = normalizar_identificador(linha.get('lote_principal_hibrido_shadow')) or ''
            mudou = lote_local != lote_bench
            mudou_lote_principal.append(bool(mudou))
            divergencia_material.append(bool(mudou or bool(linha.get('qtd_lotes_usados_hibrido_shadow') or 0) > 1))
            continue

        pagamento = pagamento_row.iloc[0].to_dict()
        valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)
        candidatos = _construir_candidatos_decisao_local_v1(pagamento, quadro_saldo, quadro_fontes, mapa_produtos_proxy)
        mapa_candidatos_fonte = {limpar_texto(c.get('fonte_escolhida_id')): c for c in candidatos}
        mapa_candidatos_lote = {normalizar_identificador(c.get('lote_id')): c for c in candidatos if normalizar_identificador(c.get('lote_id'))}

        candidato_local = mapa_candidatos_fonte.get(limpar_texto(linha.get('fonte_escolhida_id_local_v3')))
        candidato_bench = mapa_candidatos_lote.get(normalizar_identificador(linha.get('lote_principal_hibrido_shadow')))

        if candidato_local is not None:
            score_loc, _ = _score_proxy_economico_v3(candidato_local, valor_pagamento=valor_pagamento)
        else:
            score_loc = linha.get('custo_economico_proxy_local_v3')
        if candidato_bench is not None:
            score_bench, _ = _score_proxy_economico_v3(candidato_bench, valor_pagamento=valor_pagamento)
        else:
            score_bench = None

        score_local_comum.append(round(float(score_loc), 4) if score_loc is not None else None)
        score_benchmark_principal.append(round(float(score_bench), 4) if score_bench is not None else None)
        if score_loc is None or score_bench is None:
            delta_score_principal.append(None)
            classif_score.append('indisponivel')
        else:
            delta = round(float(score_bench) - float(score_loc), 4)
            delta_score_principal.append(delta)
            classif_score.append('benchmark_principal_melhor' if delta < 0 else ('benchmark_principal_pior' if delta > 0 else 'igual'))

        valor_local = round(float(linha.get('valor_disponivel_escolhido_local_v3') or 0.0), 2)
        valor_bench = round(float(linha.get('valor_liquido_total_hibrido_shadow') or 0.0), 2)
        exc_local = round(max(valor_local - valor_pagamento, 0.0), 2)
        exc_bench = round(max(valor_bench - valor_pagamento, 0.0), 2)
        excesso_local.append(exc_local)
        excesso_bench.append(exc_bench)
        delta_exc = round(exc_bench - exc_local, 2)
        delta_excesso.append(delta_exc)
        classif_excesso.append('benchmark_menor_excesso' if delta_exc < 0 else ('benchmark_maior_excesso' if delta_exc > 0 else 'igual'))

        lote_local = normalizar_identificador(linha.get('lote_id_escolhido_local_v3')) or ''
        lote_bench = normalizar_identificador(linha.get('lote_principal_hibrido_shadow')) or ''
        mudou = lote_local != lote_bench
        mudou_lote_principal.append(bool(mudou))
        divergencia_material.append(bool(mudou or bool(linha.get('qtd_lotes_usados_hibrido_shadow') or 0) > 1 or limpar_texto(linha.get('tipo_fonte_escolhida_local_v3')) != 'lote_resgatavel'))

    comparativo['score_proxy_v3_local_comum'] = score_local_comum
    comparativo['score_proxy_v3_lote_principal_benchmark'] = score_benchmark_principal
    comparativo['delta_score_proxy_v3_principal_benchmark_vs_local'] = delta_score_principal
    comparativo['classificacao_score_proxy_v3_principal'] = classif_score
    comparativo['excesso_liquido_local_v3'] = excesso_local
    comparativo['excesso_liquido_benchmark_shadow'] = excesso_bench
    comparativo['delta_excesso_liquido_benchmark_vs_local'] = delta_excesso
    comparativo['classificacao_excesso_liquido'] = classif_excesso
    comparativo['mudou_lote_principal'] = mudou_lote_principal
    comparativo['divergencia_material'] = divergencia_material
    comparativo['benchmark_multifonte_shadow'] = comparativo['qtd_lotes_usados_hibrido_shadow'].fillna(0).map(lambda x: bool(float(x) > 1))

    comparativo = comparativo.sort_values(['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)
    divergencias = comparativo.loc[comparativo['divergencia_material']].copy()

    serie_score = pd.Series([x for x in comparativo['delta_score_proxy_v3_principal_benchmark_vs_local'].tolist() if x is not None], dtype='float64')
    serie_excesso = pd.Series([x for x in comparativo['delta_excesso_liquido_benchmark_vs_local'].tolist() if x is not None], dtype='float64')

    resumo = {
        'total_pagamentos': int(len(comparativo)),
        'pagamentos_totalmente_cobertos_local_v3': int(comparativo['pagamento_totalmente_coberto_local_v3'].fillna(False).sum()),
        'pagamentos_totalmente_cobertos_benchmark_shadow': int(comparativo['benchmark_totalmente_coberto_shadow'].fillna(False).sum()),
        'pagamentos_com_lote_principal_alterado': int(comparativo['mudou_lote_principal'].fillna(False).sum()),
        'pagamentos_multifonte_shadow': int(comparativo['benchmark_multifonte_shadow'].fillna(False).sum()),
        'pagamentos_com_divergencia_material': int(comparativo['divergencia_material'].fillna(False).sum()),
        'delta_score_proxy_v3_principal_total': round(float(serie_score.sum()), 4) if len(serie_score) else 0.0,
        'delta_score_proxy_v3_principal_medio': round(float(serie_score.mean()), 4) if len(serie_score) else 0.0,
        'classificacao_score_proxy_v3_principal': {str(k): int(v) for k, v in comparativo['classificacao_score_proxy_v3_principal'].value_counts(dropna=False).to_dict().items()},
        'delta_excesso_liquido_total': round(float(serie_excesso.sum()), 2) if len(serie_excesso) else 0.0,
        'delta_excesso_liquido_medio': round(float(serie_excesso.mean()), 2) if len(serie_excesso) else 0.0,
        'classificacao_excesso_liquido': {str(k): int(v) for k, v in comparativo['classificacao_excesso_liquido'].value_counts(dropna=False).to_dict().items()},
        'lote_id_escolhido_local_v3': {str(k): int(v) for k, v in comparativo['lote_id_escolhido_local_v3'].fillna('sem_lote').value_counts(dropna=False).to_dict().items()},
        'lote_principal_hibrido_shadow': {str(k): int(v) for k, v in comparativo['lote_principal_hibrido_shadow'].fillna('sem_lote').value_counts(dropna=False).to_dict().items()},
    }
    auditoria = {
        'resumo': resumo,
        'validacao': {
            'ok': len(comparativo) == len(quadro_local) == len(quadro_bench),
            'erros': [] if len(comparativo) == len(quadro_local) == len(quadro_bench) else ['comparativo_incompleto_proxy_v3_vs_hibrido_shadow'],
            'avisos': ['benchmark_shadow_permanece_diagnostico_e_desacoplado_do_fluxo_principal'],
        },
    }
    return {
        'quadro_comparativo': comparativo,
        'quadro_divergencias': divergencias,
        'pacote_local_v3': decisao_local_v1,
        'pacote_benchmark_shadow': resolver_hibrido_5p_shadow,
        'auditoria': auditoria,
    }
