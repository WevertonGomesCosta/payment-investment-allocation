# Preparação para absorção dos modelos do Script 1 — V139

Esta etapa não reimplementa ainda os modelos do Script 1. Ela apenas prepara a base do repositório para recebê-los na próxima frente sem aumentar acoplamento estrutural.

## Decisão
Os modelos do Script 1 devem entrar **depois** da reorganização documental/operacional da V139 e **antes** da expansão do fluxo real de pagamentos para blocos maiores.

## Camada alvo
A absorção futura deve ocorrer na trilha:
- `nucleo/pagamentos/`
- `nucleo/pagamentos/modelos_script1/`

## Escopo sugerido da próxima frente
1. formalizar o contrato dos modelos do Script 1 ainda úteis para alocação de pagamentos;
2. criar adapters para o estado canônico atual;
3. integrar essas heurísticas ao `alocador_pagamentos_terminal_v1`.

## O que não fazer nesta etapa
- não reabrir auditoria ampla de switching;
- não mover ainda módulos de negócio entre diretórios;
- não expandir o bloco de pagamentos antes de absorver os modelos úteis do Script 1.
