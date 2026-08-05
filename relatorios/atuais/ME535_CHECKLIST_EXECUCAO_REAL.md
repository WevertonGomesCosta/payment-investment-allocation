# ME-535 — checklist de execução real

Validação automatizada concluída no workflow `ME-535 motor temporal funcional`, execução #12.

## Etapa 5

- [x] tipos sem pagamento exatamente `no_action` e `switch_only`;
- [x] tipos com pagamento exatamente `pay_only`, `switch_then_pay` e `pay_then_switch`;
- [x] todos os candidatos da data possuem o mesmo `estado_inicial_id`;
- [x] `patrimonio_terminal_liquido` numérico para todo pacote factível;
- [x] vencedor igual ao maior patrimônio terminal;
- [x] `argmax_comprovado=True` nas 372 datas auditadas;
- [x] obrigações integralmente cobertas ou inviabilidade explicitamente demonstrada;
- [x] `pronto_para_etapa6=True`.

## Etapas 6 e 7

- [x] ledger preserva `evidencias_economicas_por_data`;
- [x] lastro consolidado por fonte, data e pacote;
- [x] migração residual de `pay_then_switch` materializada separadamente;
- [x] `gate_motor_funcional` aprovado;
- [x] nenhuma reotimização na Etapa 6;
- [x] nenhum gate impeditivo remanescente;
- [x] `pronto_para_etapa8=True`.

## Etapas 8–11

- [x] saída canônica posterior aos gates;
- [x] Etapa 9 aprovada;
- [x] Etapa 10 aprovada, sem divergência material console/XLSX;
- [x] Etapa 11 aprovada;
- [x] cinco abas físicas oficiais preservadas;
- [x] nenhuma métrica auxiliar removida reaparece;
- [x] nenhuma correção econômica foi introduzida em `Situação Atual`.

## Decisão

- [x] aprovar tecnicamente o merge por squash;
- [ ] merge efetivo, dependente de ação explícita no PR.
