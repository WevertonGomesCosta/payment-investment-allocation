# ME-V17-F0-V36D — Reaplica desativacao da ponte passiva POS sobre main atual

## Identificacao

- MICROETAPA: ME-V17-F0-V36D
- VERSAO_CANDIDATA: V17-F0-V.3.6D
- TIPO: CODIGO / SAIDA CANONICA / CORRECAO DE DUPLICIDADE
- CLASSE: REAPLICA_DESATIVACAO_PONTE_PASSIVA_POS_MAIN_ATUAL
- ALTERA_CODIGO: sim
- ALTERA_ETAPA_1: nao
- ALTERA_ETAPA_2: nao
- ALTERA_ETAPA_3: nao
- ALTERA_MOTOR: nao
- ALTERA_SAIDA_CANONICA: sim
- ALTERA_RENDERIZACAO: nao
- ALTERA_DADOS: nao

## Objetivo

Reaplicar sobre o main atual a correcao originalmente planejada como V17-F0-V.3.2.

A correcao desativa a materializacao passiva duplicada de POS pos-switching na Situacao Atual quando esses POS ja existem no inventario_canonico operacional.

## Contexto

A V17-F0-V.3.1 integrou lotes pos-switching ao inventario_canonico.

A V17-F0-V.3.6C diagnosticou que a V3.2 original nao existia no main atual e que nucleo/saida_canonica.py ainda passava destinos_pos_switching_passivos diretamente para _construir_lotes_situacao(...).

## Alteracao realizada

Arquivo alterado:

- nucleo/saida_canonica.py

Foi adicionada a funcao _pos_canonico_ativo(contexto).

Essa funcao detecta origem_registro == lote_pos_switching_normalizado em contexto.dados_operacionais.inventario_canonico.

Em construir_saida_canonica(...), destinos_pos_switching_passivos continua preservado para auditoria.

Foi criada a lista destinos_pos_switching_passivos_para_situacao.

Quando pos_canonico_ativo=True, essa lista e vazia e a ponte passiva POS nao e reenviada para _construir_lotes_situacao(...).

## Auditoria adicionada

Campos adicionados em saida.auditoria:

- pos_canonico_ativo
- ponte_passiva_pos_desativada_por_pos_canonico
- destinos_pos_switching_passivos_para_situacao_total
- destinos_pos_switching_passivos_preservados_auditoria_total

## Decisoes preservadas

- Etapa 3 nao alterada.
- Motor nao alterado.
- PacoteEntradaResolvida nao alterado.
- Gate nao alterado.
- Renderizacao nao alterada.
- Dados nao alterados.
- _aplicar_consumo_pagamentos_passados_lotes_pos_switching(...) preservada.
- Clamp invalido da V2.2 nao tratado nesta microetapa.

## Validacoes esperadas

- python -m py_compile nucleo/saida_canonica.py
- python -B aplicacao/principal.py
- git diff --check
- git status --short
