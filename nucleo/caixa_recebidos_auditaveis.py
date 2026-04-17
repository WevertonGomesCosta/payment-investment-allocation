from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

import pandas as pd

from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.utilitarios_neutros import limpar_texto, normalizar_identificador, normalizar_texto


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


def _campos_fonte_elegivel() -> tuple[CampoContrato, ...]:
    return (
        CampoContrato('fonte_id', 'str', True, 'Identificador canônico e estável da fonte elegível.'),
        CampoContrato('tipo_fonte', 'str', True, 'Categoria da fonte: saldo_disponivel, caixa_pre_aplicacao, lote_resgatavel ou recebido_disponivel.'),
        CampoContrato('data_evento', 'date', True, 'Data econômica em que a fonte pode financiar o pagamento.'),
        CampoContrato('lote_id', 'str|None', False, 'Identificador do lote quando a fonte deriva de um lote específico.'),
        CampoContrato('recebido_id', 'str|None', False, 'Identificador do recebido quando a fonte deriva de um recebido explícito.'),
        CampoContrato('produto_key', 'str|None', False, 'Produto canônico associado quando houver produto financeiro vinculado.'),
        CampoContrato('valor_bruto_disponivel', 'float', True, 'Valor bruto economicamente elegível na data do evento.'),
        CampoContrato('valor_liquido_disponivel', 'float', True, 'Valor líquido economicamente elegível na data do evento.'),
        CampoContrato('origem_status', 'str', True, 'Status operacional da origem: confirmado, estimado, parcial ou bloqueado.'),
        CampoContrato('observacao_auditavel', 'str', False, 'Texto curto para explicar a elegibilidade ou restrição da fonte.'),
    )


def _campos_recebido_auditavel() -> tuple[CampoContrato, ...]:
    return (
        CampoContrato('recebido_id', 'str', True, 'Identificador canônico do recebido.'),
        CampoContrato('data_recebimento', 'date', True, 'Data em que o recurso passa a existir economicamente.'),
        CampoContrato('data_aplicacao', 'date|None', False, 'Data em que o recurso passa a render, se houver aplicação.'),
        CampoContrato('valor_bruto', 'float', True, 'Valor bruto do recebido.'),
        CampoContrato('valor_liquido', 'float', True, 'Valor líquido auditável do recebido na origem.'),
        CampoContrato('status_recebido', 'str', True, 'Situação operacional: futuro, disponivel, comprometido, aplicado, exaurido ou misto.'),
        CampoContrato('destino_potencial', 'str', True, 'Destino potencial observado ou elegível: caixa, pagamento, aplicacao ou misto.'),
        CampoContrato('pagamento_vinculado_id', 'str|None', False, 'Pagamento explicitamente associado, quando já existir vínculo auditável.'),
        CampoContrato('lote_destino_id', 'str|None', False, 'Lote de destino, quando o recebido já foi ou será convertido em lote.'),
        CampoContrato('observacao_auditavel', 'str', False, 'Texto curto para registrar a leitura econômica do recebido.'),
    )


def _campos_decisao_local_v1() -> tuple[CampoContrato, ...]:
    return (
        CampoContrato('pagamento_id', 'str', True, 'Identificador canônico do pagamento analisado.'),
        CampoContrato('data_pagamento', 'date', True, 'Data econômica do pagamento.'),
        CampoContrato('fonte_escolhida_id', 'str', True, 'Fonte escolhida pela regra local v1.'),
        CampoContrato('tipo_fonte_escolhida', 'str', True, 'Categoria da fonte escolhida.'),
        CampoContrato('criterio_decisao', 'str', True, 'Critério auditável aplicado na decisão local v1.'),
        CampoContrato('custo_economico_proxy', 'float|None', False, 'Custo econômico proxy associado à escolha, quando a etapa correspondente for aberta.'),
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
            nome='decisao_local_v1',
            descricao='Estrutura reservada para a futura decisão local entre saldo disponível, caixa pré-aplicação, recebidos e resgate, ainda sem solver e sem switching.',
            campos=_campos_decisao_local_v1(),
        ),
    )
    return {
        'frente': 'F1',
        'nome': 'caixa e recebidos auditáveis + decisão local v1 entre saldo disponível e resgate',
        'escopo_etapa_atual': 'Materialização inicial de recebido_auditavel e fonte_elegivel_pagamento a partir dos dados canônicos, da data de referência corrente e do estado mínimo observável do replay, sem integrar ainda essa camada ao fluxo principal da baseline.',
        'implementado_nesta_etapa': [
            'Contrato mínimo documentado e observável da camada F1.',
            'Estruturas canônicas para fonte elegível de pagamento, recebido auditável e decisão local v1.',
            'Materialização executável de recebido_auditavel a partir do inventário canônico e dos vínculos históricos de gastos.',
            'Materialização executável de fonte_elegivel_pagamento a partir dos recebidos auditáveis, do inventário canônico, da data de referência e do estado mínimo observável do replay.',
            'Scripts diagnósticos para inspecionar o contrato mínimo e as duas estruturas reais da F1 sem tocar no motor financeiro.',
        ],
        'fora_do_escopo_nesta_etapa': [
            'Alteração do motor financeiro.',
            'Abertura da decisão econômica real.',
            'Abertura de switching econômico.',
            'Integração da F1 ao fluxo principal do console ou da planilha operacional.',
            'Materialização robusta de saldo_disponivel geral independente da origem explícita do recebido.',
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
                    'misto',
                    'misto',
                    lote_id,
                    'recebido em janela pré-aplicação com pagamentos já vinculados antes do aporte final.',
                )
            return (
                'comprometido',
                'aplicacao',
                lote_id,
                'recebido disponível, porém comprometido para aplicação futura.',
            )
        if valor_pre > 0:
            return (
                'misto',
                'misto',
                lote_id,
                'recebido com uso misto: parte financiou pagamentos antes da aplicação e o residual foi aportado.',
            )
        return ('aplicado', 'aplicacao', lote_id, 'recebido integralmente associado a lote aportado.')

    return ('disponivel', 'misto', lote_id or None, 'classificação econômica provisória para recebido não enquadrado nas regras principais.')


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
    if (quadro['status_recebido'] == 'misto').any():
        avisos.append('existem_recebidos_com_destino_misto')
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
            'recebidos_com_uso_misto_observado': int(((quadro['valor_pagamentos_pre_aplicacao'] > 0) & (quadro['lote_destino_id'].notna())).sum()),
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


def _materializar_fontes_de_recebidos(
    quadro_recebidos: pd.DataFrame,
    *,
    data_referencia: date,
    limiar_valor: float,
) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = []
    if len(quadro_recebidos) == 0:
        return registros

    for _, row in quadro_recebidos.iterrows():
        recebido_id = limpar_texto(row.get('recebido_id'))
        lote_id = normalizar_identificador(row.get('lote_id_origem'))
        produto_key = row.get('produto_key')
        produto_nome = row.get('produto_nome_canonico')
        status_recebido = limpar_texto(row.get('status_recebido'))
        observacao_origem = limpar_texto(row.get('observacao_auditavel'))

        if status_recebido == 'disponivel':
            valor = round(float(row.get('valor_liquido') or row.get('valor_bruto') or 0.0), 2)
            if valor > limiar_valor:
                registros.append({
                    'fonte_id': _fonte_id('recebido_disponivel', recebido_id=recebido_id),
                    'tipo_fonte': 'recebido_disponivel',
                    'data_evento': data_referencia,
                    'lote_id': lote_id or None,
                    'recebido_id': recebido_id,
                    'produto_key': produto_key,
                    'valor_bruto_disponivel': valor,
                    'valor_liquido_disponivel': valor,
                    'origem_status': 'confirmado',
                    'observacao_auditavel': observacao_origem or 'recebido disponível em caixa na data de referência.',
                    'produto_nome_canonico': produto_nome,
                    'data_recebimento_origem': row.get('data_recebimento'),
                    'data_aplicacao_origem': row.get('data_aplicacao'),
                    'carencia_ate_origem': None,
                    'origem_estrutura': 'recebido_auditavel',
                })

        if bool(row.get('em_janela_pre_aplicacao_na_referencia')):
            valor_residual = round(float(row.get('valor_residual_para_aplicacao_origem') or 0.0), 2)
            if valor_residual > limiar_valor:
                origem_status = 'parcial' if status_recebido == 'misto' else 'confirmado'
                observacao = observacao_origem or 'valor disponível em caixa pré-aplicação na data de referência.'
                if origem_status == 'parcial':
                    observacao = f'{observacao} Residual remanescente após uso parcial em pagamentos antes da aplicação.'
                registros.append({
                    'fonte_id': _fonte_id('caixa_pre_aplicacao', lote_id=lote_id or None, recebido_id=recebido_id),
                    'tipo_fonte': 'caixa_pre_aplicacao',
                    'data_evento': data_referencia,
                    'lote_id': lote_id or None,
                    'recebido_id': recebido_id,
                    'produto_key': produto_key,
                    'valor_bruto_disponivel': valor_residual,
                    'valor_liquido_disponivel': valor_residual,
                    'origem_status': origem_status,
                    'observacao_auditavel': observacao,
                    'produto_nome_canonico': produto_nome,
                    'data_recebimento_origem': row.get('data_recebimento'),
                    'data_aplicacao_origem': row.get('data_aplicacao'),
                    'carencia_ate_origem': None,
                    'origem_estrutura': 'recebido_auditavel',
                })

    return registros


def _materializar_fontes_de_replay(
    lotes_replay: list[Any],
    inventario_por_lote: dict[str, dict[str, Any]],
    *,
    data_referencia: date,
    tabela_iof: list[float] | None,
    faixas_ir: list[dict[str, Any]] | None,
    limiar_valor: float,
) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = []
    for lote in lotes_replay or []:
        lote_id = normalizar_identificador(getattr(lote, 'id', None))
        if not lote_id:
            continue
        saldo_bruto = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
        if saldo_bruto <= limiar_valor:
            continue

        data_aplicacao = getattr(lote, 'data_aplicacao', None)
        if data_aplicacao is not None and data_referencia < data_aplicacao:
            continue

        data_recebimento = getattr(lote, 'data_recebimento', None)
        carencia_ate = getattr(lote, 'carencia_ate', None)
        linha_inventario = inventario_por_lote.get(lote_id, {})
        produto_key = getattr(lote, 'produto_key', None) or linha_inventario.get('produto_key')
        produto_nome = limpar_texto(getattr(lote, 'investimento', None)) or linha_inventario.get('produto_nome_canonico')
        recebido_id = _recebido_id(lote_id)

        try:
            valor_liquido = round(float(lote.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir)), 2)
        except Exception:
            valor_liquido = saldo_bruto

        if carencia_ate is not None and data_referencia < carencia_ate:
            origem_status = 'bloqueado'
            observacao = f'lote ativo após o replay, mas ainda bloqueado por carência até {carencia_ate.isoformat()}.'
        else:
            origem_status = 'confirmado'
            observacao = 'lote ativo com saldo remanescente após o replay e elegível para resgate na data de referência.'

        registros.append({
            'fonte_id': _fonte_id('lote_resgatavel', lote_id=lote_id),
            'tipo_fonte': 'lote_resgatavel',
            'data_evento': data_referencia,
            'lote_id': lote_id,
            'recebido_id': recebido_id,
            'produto_key': produto_key,
            'valor_bruto_disponivel': saldo_bruto,
            'valor_liquido_disponivel': valor_liquido,
            'origem_status': origem_status,
            'observacao_auditavel': observacao,
            'produto_nome_canonico': produto_nome,
            'data_recebimento_origem': data_recebimento,
            'data_aplicacao_origem': data_aplicacao,
            'carencia_ate_origem': carencia_ate,
            'origem_estrutura': 'replay_passado_controlado',
        })
    return registros


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

    registros: list[dict[str, Any]] = []
    registros.extend(_materializar_fontes_de_recebidos(quadro_recebidos, data_referencia=data_referencia, limiar_valor=limiar_valor))
    registros.extend(
        _materializar_fontes_de_replay(
            getattr(replay_passado, 'lotes_apos_replay', []) if replay_passado is not None else [],
            inventario_por_lote,
            data_referencia=data_referencia,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            limiar_valor=limiar_valor,
        )
    )

    quadro = pd.DataFrame(registros)
    if len(quadro) == 0:
        auditoria = {
            'validacao': {'ok': False, 'erros': ['fontes_elegiveis_vazio'], 'avisos': ['saldo_disponivel_ainda_nao_materializado']},
            'resumo': {},
        }
        return PacoteFontesElegiveisPagamento(quadro_fontes_elegiveis=quadro, auditoria=auditoria)

    quadro = quadro.sort_values(['tipo_fonte', 'origem_status', 'lote_id', 'recebido_id'], kind='stable').reset_index(drop=True)
    erros: list[str] = []
    avisos: list[str] = []
    if quadro['fonte_id'].duplicated().any():
        erros.append('fonte_id_duplicado')
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

    resumo_tipos = {str(k): int(v) for k, v in quadro['tipo_fonte'].value_counts(dropna=False).to_dict().items()}
    resumo_status = {str(k): int(v) for k, v in quadro['origem_status'].value_counts(dropna=False).to_dict().items()}
    auditoria = {
        'validacao': {'ok': len(erros) == 0, 'erros': erros, 'avisos': avisos},
        'resumo': {
            'total_fontes': int(len(quadro)),
            'tipo_fonte': resumo_tipos,
            'origem_status': resumo_status,
            'valor_total_bruto_disponivel': round(float(quadro['valor_bruto_disponivel'].sum()), 2),
            'valor_total_liquido_disponivel': round(float(quadro['valor_liquido_disponivel'].sum()), 2),
            'fontes_confirmadas': int((quadro['origem_status'] == 'confirmado').sum()),
            'fontes_parciais': int((quadro['origem_status'] == 'parcial').sum()),
            'fontes_bloqueadas': int((quadro['origem_status'] == 'bloqueado').sum()),
            'fontes_lote_resgatavel': int((quadro['tipo_fonte'] == 'lote_resgatavel').sum()),
            'fontes_recebido_disponivel': int((quadro['tipo_fonte'] == 'recebido_disponivel').sum()),
            'fontes_caixa_pre_aplicacao': int((quadro['tipo_fonte'] == 'caixa_pre_aplicacao').sum()),
            'saldo_disponivel_materializado': bool((quadro['tipo_fonte'] == 'saldo_disponivel').any()),
        },
    }
    return PacoteFontesElegiveisPagamento(quadro_fontes_elegiveis=quadro, auditoria=auditoria)
