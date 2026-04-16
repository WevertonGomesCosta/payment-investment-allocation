# BASELINE FIXA V31

Derivada da V30 para corrigir a convenção de valuation da baseline.

## Escopo aberto nesta versão

- fechamento completo da posição na data de referência;
- fallback controlado do último fator CDI disponível quando o cache não contém o próprio dia da referência;
- extensão dos lotes remanescentes do replay até a data de referência completa;
- reauditoria dos lotes críticos contra os apps;
- reauditoria dos lotes residuais;
- teste de `-1 dia de rendimento` após a correção temporal.

## Ajustes implementados

1. A capitalização diária passou a aceitar fechamento controlado da data de referência com reaproveitamento do último fator CDI disponível.
2. A contagem de dias de rendimento passou a aceitar a mesma convenção de fechamento da referência.
3. O núcleo financeiro mínimo passou a auditar explicitamente o fechamento da referência completa.
4. O replay controlado do passado passou a carregar os lotes remanescentes até a data de referência completa, sem truncar no último evento histórico.
5. O console passou a mostrar:
   - auditoria crítica vs. app com deltas consolidados;
   - amostra do fechamento da referência via fallback CDI;
   - reauditoria dos lotes residuais;
   - teste de `-1 dia de rendimento` com observação quando houver saque na própria data de referência.

## Resultado consolidado da reauditoria crítica em 15/04/2026

- `Lote 6630,64 fev.`: bruto `2852,53` vs app `2852,42` (`+0,11`); líquido `2833,98` vs app `2833,77` (`+0,21`)
- `Lote 3000 mar. V`: bruto `3115,11` vs app `3115,13` (`-0,02`); líquido `3089,21` vs app `3089,22` (`-0,01`)
- `Lote 3000 mar. B`: bruto `3111,16` vs app `3111,24` (`-0,08`); líquido `3086,15` vs app `3086,21` (`-0,06`)
- `Lote 8500 mar.`: bruto `8720,72` vs app `8720,80` (`-0,08`); líquido `8690,64` vs app `8690,70` (`-0,06`)

## Leitura operacional desta versão

A divergência principal de rendimento/convenção temporal foi praticamente absorvida. O resíduo remanescente ficou pequeno e compatível com ajuste fino de rendimento e/ou efeitos de saque/arredondamento, sem abrir solver, switching econômico, score econômico final ou relatório financeiro atual.
