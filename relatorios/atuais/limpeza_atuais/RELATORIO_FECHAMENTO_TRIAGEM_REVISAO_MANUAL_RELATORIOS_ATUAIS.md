# Relatório de fechamento — triagem REVISAO_MANUAL em relatorios/atuais

## Objetivo

Encerrar a subfrente de triagem dos arquivos classificados como `REVISAO_MANUAL` em `relatorios/atuais/`, registrando as decisões documentais tomadas e preservando a regra de não remover arquivos sem cobertura explícita suficiente.

## Escopo

Esta etapa consolida as decisões derivadas dos seguintes documentos:

- `relatorios/atuais/limpeza_atuais/RELATORIO_DECISAO_REVISAO_MANUAL_RELATORIOS_ATUAIS.md`
- `relatorios/atuais/limpeza_atuais/RELATORIO_AUDITORIA_COBERTURA_CANDIDATOS_REMOCAO_RELATORIOS_ATUAIS.md`
- `relatorios/atuais/limpeza_atuais/RELATORIO_AUDITORIA_CONTEUDO_HOTFIX_CONSOLE_IMPORTS_V205.md`
- `relatorios/atuais/limpeza_atuais/RELATORIO_DECISAO_ATUALIZADA_CANDIDATOS_REMOCAO_RELATORIOS_ATUAIS.md`

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa é apenas documental.

## Resultado da triagem dos 17 REVISAO_MANUAL

| Decisão | Arquivos | Resultado |
|---|---:|---|
| `MANTER_COMO_DOCUMENTO_VIGENTE` | 4 | Mantidos |
| `MANTER_COMO_SUPORTE_TECNICO_RECENTE` | 5 | Mantidos |
| `MANTER_ATE_REVISAO_MOTOR_DIAS_LOTES` | 2 | Mantidos |
| `CANDIDATO_CONSOLIDACAO_OU_REMOCAO_FUTURA` | 6 | Auditados separadamente |

## Resultado dos 6 candidatos à consolidação ou remoção futura

Após auditoria de cobertura documental, os 6 arquivos foram classificados assim:

| Decisão atualizada | Arquivos | Resultado |
|---|---:|---|
| `MANTER_ATE_COBERTURA_SER_REFORCADA` | 3 | Retidos |
| `MANTER_E_REVISAR_MANUALMENTE` | 3 | Retidos |

## Caso especial — HOTFIX_CONSOLE_IMPORTS_V205

O arquivo `relatorios/atuais/HOTFIX_CONSOLE_IMPORTS_V205.md` havia sido inicialmente identificado como único caso com `COBERTURA_FORTE`.

Porém, a auditoria de conteúdo comparando o hotfix contra:

- `relatorios/atuais/GOVERNANCA_ESTRUTURAL_V206.md`
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`

concluiu `NAO_REMOVER_AINDA`, pois havia linhas operacionais de prioridade alta sem cobertura suficiente.

Decisão final atualizada:

~~~text
MANTER_ATE_COBERTURA_SER_REFORCADA
~~~

## Decisão final da subfrente

A subfrente `REVISAO_MANUAL` fica encerrada com a seguinte decisão:

1. todos os 17 arquivos foram classificados;
2. os 6 candidatos à remoção futura foram auditados;
3. nenhum arquivo ficou elegível para remoção imediata;
4. nenhuma remoção, movimentação ou renomeação foi executada;
5. qualquer limpeza futura desses arquivos deve exigir nova auditoria de cobertura ou reforço documental prévio.

## Próxima frente sugerida

Com `REVISAO_MANUAL` encerrada, a próxima frente deve revisar a classe `MATERIAL_LIMPEZA_AUDITORIA`, separando o que deve ser:

- mantido como evidência permanente de limpeza;
- consolidado em um relatório único;
- removido futuramente após consolidação.
