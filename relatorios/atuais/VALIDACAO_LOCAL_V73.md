# Validação local V73

## Escopo validado

- identidade da baseline atualizada para V73;
- manutenção da `decisao_local_v1` com proxy econômico v3 como baseline vigente;
- recalculo reproduzível da decisão local com proxy v2 e v3 na mesma base;
- auditoria comparativa `v2 vs v3` com exportação de `.xlsx` e `.csv`;
- comandos canônicos, wrappers e release checker.

## Comandos executados

```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py
python scripts/diagnostico/inspecionar_decisao_local_v1.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```

## Evidências observáveis da V73

- `152` pagamentos comparados em `v2` e `v3`;
- `152` pagamentos continuam totalmente cobertos nas duas versões;
- houve `2` mudanças materiais de lote/fonte entre `v2` e `v3`;
- sob métrica comum `v3`, o proxy v3 melhora `2` casos e mantém `150` iguais;
- sob métrica comum `v2`, o proxy v3 piora `2` casos e mantém `150` iguais;
- a auditoria exportável é gerada em `saidas/operacional/auditoria_comparativa_proxy_v2_v3_v73.xlsx`.

## Resultado

A validação local da V73 foi concluída com sucesso. A baseline permanece em proxy econômico v3, e a auditoria comparativa passa a documentar o ganho observável real antes da abertura de multifonte.
