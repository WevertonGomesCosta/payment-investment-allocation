from __future__ import annotations

from dataclasses import dataclass, asdict
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
        'escopo_etapa_atual': 'Materialização inicial de recebido_auditavel a partir dos dados canônicos e dos vínculos históricos de gastos, sem integrar ainda essa camada ao fluxo principal da baseline.',
        'implementado_nesta_etapa': [
            'Contrato mínimo documentado e observável da camada F1.',
            'Estruturas canônicas para fonte elegível de pagamento, recebido auditável e decisão local v1.',
            'Materialização executável de recebido_auditavel a partir do inventário canônico e dos vínculos históricos de gastos.',
            'Script diagnóstico para inspecionar o contrato mínimo e a primeira estrutura real da F1 sem tocar no motor financeiro.',
        ],
        'fora_do_escopo_nesta_etapa': [
            'Alteração do motor financeiro.',
            'Abertura da decisão econômica real.',
            'Abertura de switching econômico.',
            'Integração da F1 ao fluxo principal do console ou da planilha operacional.',
            'Materialização de fonte_elegivel_pagamento.',
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
