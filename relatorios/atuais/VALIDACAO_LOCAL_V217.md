# VALIDAÇÃO LOCAL V217

## Validação executada nesta entrega

- `python scripts/diagnostico/verificar_release_baseline.py`
  - Resultado: `OK - release baseline validado para V217`.

## Auditoria usada como gatilho

A auditoria dos CSVs reais da V216 foi incorporada em:

- `relatorios/atuais/AUDITORIA_CONSOLE_DIAGNOSTICO_V216.md`
- `saidas/diagnostico/matriz_auditoria_console_diagnostico_v216.csv`
- `saidas/diagnostico/resumo_auditoria_console_diagnostico_v216.json`

Resultado: V216 aprovada como candidata funcional para abrir a V217.

## Validação pendente localmente

A auditoria real de impacto da V217 deve ser executada localmente com:

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v217.py --real
```

Em ambiente de geração do pacote, a validação completa da V217 não foi promovida como baseline. O objetivo da V217 é justamente gerar os CSVs comparativos de impacto antes de qualquer promoção.

## Critério de avanço

A próxima versão só deve considerar promoção formal se:

- `impacto_contas_futuras_v217_alertas_real.csv` sair vazio;
- o cenário com aportes planejados não aumentar déficit total;
- pagamentos que usam lote planejado continuarem com cobertura integral;
- não houver invariante inválida em lote promovido;
- a comparação com/sem aporte for economicamente aceitável.
