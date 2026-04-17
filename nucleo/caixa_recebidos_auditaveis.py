from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


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
        'escopo_etapa_atual': 'Definição do contrato mínimo canônico da camada de caixa/recebidos auditáveis, sem integrar ainda essa camada ao fluxo principal da baseline.',
        'implementado_nesta_etapa': [
            'Contrato mínimo documentado e observável da camada F1.',
            'Estruturas canônicas para fonte elegível de pagamento, recebido auditável e decisão local v1.',
            'Script diagnóstico para inspecionar o contrato mínimo sem tocar no motor financeiro.',
        ],
        'fora_do_escopo_nesta_etapa': [
            'Alteração do motor financeiro.',
            'Abertura da decisão econômica real.',
            'Abertura de switching econômico.',
            'Integração da F1 ao fluxo principal do console ou da planilha operacional.',
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
