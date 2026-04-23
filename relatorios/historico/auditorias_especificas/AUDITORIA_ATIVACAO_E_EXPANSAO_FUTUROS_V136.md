# Auditoria da ativação dos lotes futuros e expansão da grade oficial híbrida — V136

## Resultado da auditoria de ativação

- lotes futuros não aportados auditados: **24**
- ativações corretas na própria data de recebimento: **24**
- ativações incorretas: **0**

Isso confirma que, a partir desta versão, os lotes futuros não aportados entram como fontes elegíveis exatamente na data de recebimento.

## Evidência de ativação ao longo do horizonte

Exemplos confirmados:
- `Lote 7000 mai.` entra em `2026-05-03`
- `Lote 7000 set.` entra em `2026-09-01`
- `Lote 7000 mar.` entra em `2027-03-03`
- `Lote 5680 mar.` entra em `2027-03-06`

## Expansão da grade oficial híbrida até 2027-03-31

A expansão completa com combinações agrupadas no horizonte inteiro ficou computacionalmente pesada neste ambiente interativo depois da entrada dos lotes futuros. O bloqueio não é mais estrutural da base, e sim combinatório:

- em `2026-09-01`, já com os futuros ativados, o planejador reduzido por fonte/destino gerou **95 ações**;
- mesmo após capar para **3 fontes por destino** apenas para fins de prova de execução tardia, ainda restaram **58 cenários** num único dia;
- com cap **6**, um único dia já sobe para **513 cenários**.

Por isso, nesta entrega a expansão ficou preparada no script até `2027-03-31`, mas a validação executada no ambiente foi feita por **provas tardias representativas**, não por varredura diária completa do horizonte inteiro.

## Provas tardias executadas

### 2026-09-01
- recebidos não aportados já disponíveis: **11**
- futuros restantes: **13**
- cenários avaliados na prova oficial híbrida: **58**
- promoção oficial: **baseline_sem_switching**

### 2027-03-03
- recebidos não aportados já disponíveis: **23**
- futuros restantes: **1**
- cenários avaliados na prova oficial híbrida: **8**
- promoção oficial: **baseline_sem_switching**

## Conclusão operacional da V136

- a falha anterior de ativação dos lotes futuros foi corrigida;
- a frente temporal tardia agora está **estruturalmente pronta** para considerar esses lotes;
- nas provas tardias executadas, **o baseline continuou vencendo oficialmente**;
- porém a grade diária oficial híbrida **não foi consolidada integralmente até 2027-03-31 neste ambiente** porque a expansão agrupada diária com múltiplas fontes futuras ficou pesada demais para uma varredura completa aqui.

## Próxima ação correta

- manter a V136 como baseline estrutural da ativação correta dos lotes futuros;
- se quisermos fechar o horizonte completo até `2027-03-31`, a próxima etapa correta é reduzir o custo combinatório da grade oficial híbrida tardia sem perder coerência econômica/auditabilidade.
