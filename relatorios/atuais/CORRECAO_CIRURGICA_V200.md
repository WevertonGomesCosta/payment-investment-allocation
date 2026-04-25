# Correção cirúrgica V200

Status: baseline operacional derivada da V199.

Escopo restrito:

1. Normalização operacional do resíduo do `Lote 6630,64 fev.` nas saídas de replay e extrato passado.
2. Recomputação temporal das recomendações futuras consumindo saldos residuais por lote após cada recomendação, inclusive quando há switching simples.
3. Cobertura multifonte para impedir recomendação de pagamento parcial quando uma fonte isolada não cobre o valor integral da conta.

Restrições preservadas:

- contrato mestre não alterado;
- modelo matemático-estatístico-financeiro oficial não alterado;
- estrutura diária congelada preservada;
- alteração concentrada nas camadas de replay/exportação, recomputação sequencial central e motor de recomendação.

Validação mínima esperada:

- `Lote 6630,64 fev.` deve aparecer com `Saldo Remanescente = 0.00` no Extrato Passado;
- contas futuras devem apresentar cobertura integral sempre que a soma sequencial das fontes elegíveis for suficiente;
- lotes consumidos ou exauridos não devem continuar sendo recomendados em pagamentos futuros por saldo temporal inexistente.
