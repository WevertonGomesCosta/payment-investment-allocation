# ME-535 — checklist de execução real

Execute na branch `me535-motor-temporal-funcional`:

```bash
python -m unittest tests.test_motor_temporal_funcional
python aplicacao/principal.py
```

## Etapa 5

- [ ] tipos sem pagamento exatamente `no_action` e `switch_only`;
- [ ] tipos com pagamento exatamente `pay_only`, `switch_then_pay` e `pay_then_switch`;
- [ ] todos os candidatos da data possuem o mesmo `estado_inicial_id`;
- [ ] `patrimonio_terminal_liquido` numérico para todo pacote factível;
- [ ] vencedor igual ao maior patrimônio terminal;
- [ ] `argmax_comprovado=True` em todas as datas;
- [ ] obrigações integralmente cobertas ou inviabilidade explicitamente demonstrada;
- [ ] `pronto_para_etapa6=True`.

## Etapas 6 e 7

- [ ] ledger preserva `evidencias_economicas_por_data`;
- [ ] `gate_motor_funcional` aprovado;
- [ ] nenhuma reotimização na Etapa 6;
- [ ] nenhum gate sem evidência mínima relevante;
- [ ] `pronto_para_etapa8=True`.

## Etapas 8–11

- [ ] saída derivada do ledger e gates;
- [ ] Etapa 9 aprovada;
- [ ] Etapa 10 aprovada, sem divergência material console/XLSX;
- [ ] Etapa 11 aprovada;
- [ ] cinco abas oficiais preservadas;
- [ ] nenhuma métrica auxiliar removida reaparece;
- [ ] nenhuma correção econômica ocorre em `Situação Atual`.

## Decisão

- [ ] aprovar merge;
- [ ] reprovar e registrar o primeiro gate causal que falhou.
