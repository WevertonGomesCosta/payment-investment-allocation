# BASELINE FIXA V34

Derivada da V33 para aplicar a correção cirúrgica aprovada apenas à classe de lotes históricos `nao_aportado_exaurido`, sem abrir solver, switching econômico, score econômico final, relatório financeiro atual ou engine completa.

## Ajuste desta derivação

- correção da criação de lotes para **preservar taxa explícita igual a `0.0`**, em vez de convertê-la implicitamente para `1.0`;
- efeito prático esperado: lotes históricos `nao_aportado_exaurido` deixam de acumular rendimento indevido no replay;
- nenhuma mudança de regra foi aplicada aos lotes aportados ativos nem à lógica geral de saque.

## Causa raiz encontrada

Os lotes históricos `nao_aportado_exaurido` já eram materializados com `taxa_base_cdi = 0.0`, mas esse zero era perdido na criação do objeto `Lote`, sendo tratado como falsy e substituído por `1.0`.

Isso fazia com que alguns lotes históricos marcados com `Investimento = '-'` ainda rendessem durante o replay, produzindo micro-saldos artificiais.

## Resultado consolidado após a correção

### Casos estruturalmente resolvidos

- `Lote 3600 abr.` → deixou de aparecer como micro-saldo residual de `R$ 3,19`;
- `Lote 7800 abr.` → deixou de aparecer como micro-saldo residual de `R$ 0,09`.

Leitura: os dois casos foram eliminados na origem, sem uso de limiar operacional adicional.

### Resíduos remanescentes após a correção

#### Resolvido por limiar (`<= R$ 0,20`)
- `Lote 2063,11 fev.` → `R$ 0,04`

#### Pendentes para validação (`> R$ 0,20`)
- `2026-03-20` | conta `Cartão Azul` | lote `Lote 5400 fev.` | referência `despesa_auto_00037` | resíduo `R$ 0,71` | classe causal: `teto líquido do lote no esgotamento`
- `2026-03-13` | conta `Escola` | lote `Lote 10342 fev.` | referência `despesa_auto_00014` | resíduo `R$ 0,68` | classe causal: `teto líquido do lote no esgotamento`
- `2026-03-13` | conta `Aluguel` | lote `Lote 4000 fev.` | resíduo `R$ 0,49` | classe causal: `saldo residual após saque líquido-alvo`
- `2026-03-13` | conta `Escola` | lote `Lote 4124,75 fev.` | resíduo `R$ 0,38` | classe causal: `saldo residual após saque líquido-alvo`

## Implicação operacional desta etapa

A auditoria residual ficou mais limpa e semanticamente consistente:

- os resíduos artificiais de lotes históricos `-` foram removidos;
- permanecem apenas quatro casos acima do limiar, todos já interpretáveis sem evidência de erro temporal global.
