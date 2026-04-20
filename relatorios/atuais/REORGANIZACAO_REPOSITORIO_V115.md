# Reorganização do repositório V115

## Objetivo

Recolocar o repositório em direção explícita ao objetivo final do projeto, reduzindo ruído estrutural e documental sem alterar a regra econômica vigente da frente central.

## Ajustes aplicados

1. **Recentralização documental**
   - README reescrito para destacar o objetivo final conjunto do projeto.
   - índice oficial reestruturado separando frente central, camada operacional por conta e reorganização estrutural.
   - contrato atualizado para distinguir baseline central V108 de camadas auxiliares posteriores.

2. **Limpeza de histórico fora do lugar**
   - documentos antigos de baseline, validação e estrutura que ainda estavam em `relatorios/atuais/` foram movidos para `relatorios/historico/`.

3. **Limpeza de saídas redundantes**
   - saídas operacionais antigas e não referenciadas foram removidas de `saidas/operacional/`.

4. **Deduplicação leve de código**
   - scripts diagnósticos passaram a compartilhar um bootstrap único em `scripts/diagnostico/_bootstrap.py`.
   - wrappers raiz em `scripts/` foram preservados apenas como compatibilidade.

## Resultado esperado

- menos ruído para a próxima retomada da frente central;
- menor risco de drift documental;
- menor carga de manutenção em scripts diagnósticos;
- repositório mais alinhado ao objetivo final conjunto e auditável.
