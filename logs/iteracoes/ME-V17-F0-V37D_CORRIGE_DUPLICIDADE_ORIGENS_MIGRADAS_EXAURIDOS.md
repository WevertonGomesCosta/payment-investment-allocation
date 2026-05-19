# ME-V17-F0-V37D — Corrige duplicidade residual de origens migradas em lotes_exauridos

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37D
- VERSAO_CANDIDATA: V17-F0-V.3.7D
- TIPO: DIAGNÓSTICO EXECUTÁVEL / CORREÇÃO CIRÚRGICA CONDICIONAL
- CLASSE: CORRIGE_DUPLICIDADE_RESIDUAL_ORIGENS_MIGRADAS_EXAURIDOS
- BASELINE_DE_ENTRADA: V17-F0-V.3.7C
- ALTERA_CODIGO: sim
- ALTERA_SAIDA_OBSERVAVEL: sim
- ALTERA_SAIDA_CANONICA: não
- ALTERA_APLICACAO_PRINCIPAL: não
- ALTERA_ETAPA_3: não
- ALTERA_REPLAY: não
- ALTERA_LEDGER: não
- ALTERA_MOTOR: não
- ALTERA_DADOS: não

---

## 2. Diagnóstico

A duplicidade residual das origens migradas em `lotes_exauridos` não foi classificada como problema de `aplicacao/principal.py`.

A origem corrigida está em `nucleo/saida_observavel.py`, onde as linhas consolidadas de exauridos eram combinadas com linhas específicas de origens migradas por switching.

## 3. Regra implementada

Para o bloco observável principal de `lotes_exauridos`:

- se o lote é origem migrada por switching, a linha consolidada é removida da renderização principal;
- permanece a linha específica com status `migrado_por_switching`;
- não há alteração em `saida_canonica.py`;
- não há alteração em `aplicacao/principal.py`;
- não há alteração em Etapa 3, replay, ledger, motor ou dados.

## 4. Evidência da auditoria funcional

A auditoria local retornou:

```text
Lote 3000 mar. B -> qtd_id = 1, status = migrado_por_switching, qtd_valores = 1
Lote 3000 mar. V -> qtd_id = 1, status = migrado_por_switching, qtd_valores = 1
Lote 8500 mar.   -> qtd_id = 1, status = migrado_por_switching, qtd_valores = 1

DUPLICADOS OBSERVAVEIS EM EXAURIDOS = {}
VALIDACAO_V37D_OK
```

## 5. Execução principal

A execução de `python -B aplicacao/principal.py` terminou com sucesso e gerou a saída operacional.

Trecho final da execução:

```text
- linhas: 14
- colunas: 5


=== ABAS AUXILIARES / FORA DO PACOTE CANÔNICO OPERACIONAL ===
[OK] Abas auxiliares identificadas — 1 abas fora do pacote canônico operacional
- Resumo Mensal: 17 linhas, 12 colunas

=== PAGAMENTOS — AMOSTRAS OPERACIONAIS ===
- últimos 5 pagamentos já realizados:
Data       | Descrição | Valor   | Lotes usados   | Saldo Antes | Bruto   | Imposto | Líquido | Saldo Remanescente
-----------+-----------+---------+----------------+-------------+---------+---------+---------+-------------------
2026-05-15 | Internet  | 132.40  | Lote 3120 mai  | 2956.02     | 132.55  | 0.15    | 132.40  | 2823.62           
2026-05-13 | Aluguel   | 192.89  | Lote 190 mai   | 192.41      | 193.03  | 0.14    | 192.89  | 0.00              
2026-05-13 | Aluguel   | 787.11  | Lote 7500 mai. | 3648.19     | 787.90  | 0.79    | 787.11  | 2860.29           
2026-05-13 | Escola    | 2831.40 | Lote 7500 mai. | 2860.29     | 2834.25 | 2.85    | 2831.40 | 26.04             
2026-05-13 | Pelada    | 26.00   | Lote 7500 mai. | 26.04       | 26.03   | 0.03    | 26.00   | 0.00              

- próximos 5 pagamentos — switching/status:
Data       | Conta         | Lote                               | Pacote   | Sw. ant. | Sw. dep. | Status                       | Bloq.                                 
-----------+---------------+------------------------------------+----------+----------+----------+------------------------------+---------------------------------------
2026-05-20 | Cartão Azul   | Lote 3120 mai + Lote 3000 mai Neon | pay_only | não      | não      | ok                           | n/d                                   
2026-05-20 | Condomínio    | Lote 3000 mai Neon                 | pay_only | não      | não      | ok                           | n/d                                   
2026-05-30 | Implante Velt |                                    | pay_only | não      | não      | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
2026-06-02 | Cartão NU     |                                    | pay_only | não      | não      | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
2026-06-06 | Faxina Rosa   |                                    | pay_only | não      | não      | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo

- próximos 5 pagamentos — valores:
Data       | Conta         | Saldo ant. | Bruto   | IR   | Liq.    | Rem.   
-----------+---------------+------------+---------+------+---------+--------
2026-05-20 | Cartão Azul   | 6241.53    | 5372.00 | 0.00 | 5372.00 | 869.53 
2026-05-20 | Condomínio    | 1119.00    | 113.31  | 0.00 | 113.31  | 1005.69
2026-05-30 | Implante Velt |            |         |      |         |        
2026-06-02 | Cartão NU     |            |         |      |         |        
2026-06-06 | Faxina Rosa   |            |         |      |         |        

- alertas operacionais:
Data       | Conta           | problema                     | motivo                                
-----------+-----------------+------------------------------+---------------------------------------
2026-05-30 | Implante Velt   | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
2026-06-02 | Cartão NU       | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
2026-06-06 | Faxina Rosa     | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
2026-06-07 | Claro           | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
2026-06-10 | Ginástica Biola | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo

=== RANQUEAMENTO OFICIAL DA CARTEIRA ===
- produtos totais: 85
- produtos ativos ranqueados: 79
- destinos elegíveis de switching: 79
- destino top 1: Mercado Pago Cofrinho 120% CDI (Meli+)
- método: carteira_only_estabilizado_v3_3_adaptado
- origem da amostra: V225
- amostra do ranking relevante do dia:
Rank | Produto                                    | Score | Proxy terminal | Liquidez | Carência | Ticket mín.
-----+--------------------------------------------+-------+----------------+----------+----------+------------
1    | Mercado Pago Cofrinho 120% CDI (Meli+)     | 79.60 | 0.80           | 0        | 0        | 1.00       
2    | CDB Genial 220% CDI - 60 dias              | 77.60 | 0.78           | 0        | 60       | 100.00     
3    | CDB Neon Planejado 150% CDI - 60 dias      | 72.30 | 0.72           | 0        | 60       | 100.00     
4    | CDB Neon Planejado 160% CDI - 60 dias      | 72.30 | 0.72           | 0        | 60       | 100.00     
5    | Tesouro Selic 2029                         | 71.90 | 0.72           | 0        | 0        | 30.00      
6    | Mercado Pago Cofrinho 115% CDI             | 71.60 | 0.72           | 0        | 0        | 1.00       
7    | CDB BMG Escalonado - até 109% CDI - 5 anos | 70.80 | 0.71           | 0        | 0        | 50.00      
8    | CDB Sofisa 105%                            | 70.80 | 0.71           | 0        | 0        | 1.00       
9    | Combo PicPay 100-120 3m                    | 65.50 | 0.66           | 0        | 0        | 300.00     
10   | Combo PicPay 100-120 6m                    | 65.50 | 0.66           | 0        | 0        | 300.00     

=== SWITCHINGS CANDIDATOS / CLASSIFICADOS ===
- lotes avaliados para switching: 10
- candidatos avaliados para switching: 650
- destinos elegíveis de switching: 79
- switchings promovidos/executados: 4
- destino top 1 do ranking: Mercado Pago Cofrinho 120% CDI (Meli+)
- origem da amostra: V225
- amostra de switchings reais da janela (independente de pagamentos):
Data       | Lote origem      | Produto origem  | Destino                               
-----------+------------------+-----------------+---------------------------------------
2026-05-05 | Lote 3000 mar. V | CDB XP 230%     | Mercado Pago Cofrinho 120% CDI (Meli+)
2026-05-05 | Lote 3000 mar. B | CDB XP 230%     | CDB Neon Planejado 150% CDI - 60 dias 
2026-05-06 | Lote 8500 mar.   | CDB Sofisa 105% | CDB Genial 220% CDI - 60 dias         
2026-05-06 | Lote 8500 mar.   | CDB Sofisa 105% | Mercado Pago Cofrinho 120% CDI (Meli+)

- resumo operacional curto:
- total de switchings promovidos: 4
- total de lotes sintéticos pós-switching: 4
- total de aportes futuros: 18

=== SITUAÇÃO ATUAL ===
- data de referência: 2026-05-18
- status do fechamento econômico: estimado por fallback CDI
- fonte do fechamento: fallback_encadeado_ultimo_fator_cdi
- fechamentos com fallback CDI: 1
- último fator explícito CDI: 2026-05-15
- data confirmada da série: 2026-05-15
- leitura auditável: a situação atual usa o último fator explícito do CDI para fechar dias úteis consecutivos sem fator novo.

- lotes exauridos:
  identificação:
Lote              | Status ciclo          | Carteira                               | Aplic.     | Base fiscal | Data término | Dias corr. | Dias úteis
------------------+-----------------------+----------------------------------------+------------+-------------+--------------+------------+-----------
Lote 190 mai      | exaurido_por_saque    | Mercado Pago Cofrinho 120% CDI (Meli+) | 2026-05-06 | 2026-05-06  | 2026-05-13   | 7          | 5         
Lote 7500 mai.    | exaurido_por_saque    | Mercado Pago Cofrinho 120% CDI (Meli+) | 2026-05-04 | 2026-05-04  | 2026-05-13   | 9          | 7         
Lote 6630,64 fev. | exaurido_por_saque    | CDB Turbinado                          | 2026-02-04 | 2026-02-04  | 2026-04-20   | 75         | 50        
Lote 5400 fev.    | exaurido_por_saque    | CDB Turbinado                          | 2026-02-05 | 2026-02-05  | 2026-03-20   | 43         | 29        
Lote 4124,75 fev. | exaurido_por_saque    | CDB Turbinado                          | 2026-02-05 | 2026-02-05  | 2026-03-13   | 36         | 24        
Lote 10342 fev.   | exaurido_por_saque    | CDB Turbinado                          | 2026-02-05 | 2026-02-05  | 2026-03-13   | 36         | 24        
Lote 4000 fev.    | exaurido_por_saque    | CDB Turbinado                          | 2026-02-04 | 2026-02-04  | 2026-03-13   | 37         | 25        
Lote 2063,11 fev. | exaurido_por_saque    | CDB Turbinado                          | 2026-02-06 | 2026-02-06  | 2026-02-09   | 3          | 1         
Lote 3000 mar. B  | migrado_por_switching | CDB XP 230%                            | 2026-03-04 | 2026-03-04  | 2026-05-05   | 62         | 41        
Lote 3000 mar. V  | migrado_por_switching | CDB XP 230%                            | 2026-03-03 | 2026-03-03  | 2026-05-05   | 63         | 42        
Lote 8500 mar.    | migrado_por_switching | CDB Sofisa 105%                        | 2026-03-06 | 2026-03-06  | 2026-05-06   | 61         | 40        

  valores e patrimônio:
Lote              | Orig.    | Bruto sac. | Líq. sac. | Bruto atual | Líq. atual | Patr. líq. | Rend. líq.
------------------+----------+------------+-----------+-------------+------------+------------+-----------
Lote 190 mai      | 192.41   | 193.03     | 192.89    | 0.00        | 0.00       | 192.89     | 0.48      
Lote 7500 mai.    | 7536.72  | 7553.46    | 7549.69   | 0.00        | 0.00       | 7549.69    | 12.97     
Lote 6630,64 fev. | 6630.64  | 6797.78    | 6760.12   | 0.00        | 0.00       | 6760.12    | 129.48    
Lote 5400 fev.    | 5400.00  | 5503.31    | 5480.06   | 0.00        | 0.00       | 5480.06    | 80.06     
Lote 4124,75 fev. | 4124.75  | 4160.61    | 4145.58   | 0.00        | 0.00       | 4145.58    | 20.83     
Lote 10342 fev.   | 10342.00 | 10385.01   | 10363.17  | 0.00        | 0.00       | 10363.17   | 21.17     
Lote 4000 fev.    | 4000.00  | 4053.57    | 4039.06   | 0.00        | 0.00       | 4039.06    | 39.06     
Lote 2063,11 fev. | 2063.11  | 2064.59    | 2063.23   | 0.00        | 0.00       | 2063.23    | 0.12      
Lote 3000 mar. B  | 3000.00  | 0.00       | 0.00      | 0.00        | 0.00       | 3119.00    | 119.00    
Lote 3000 mar. V  | 3000.00  | 0.00       | 0.00      | 0.00        | 0.00       | 3122.53    | 122.53    
Lote 8500 mar.    | 8500.00  | 5557.02    | 5533.16   | 0.00        | 0.00       | 8725.57    | 225.57    

- lotes ativos:
  identificação:
Lote                 | Status ciclo        | Carteira                               | Aplic.     | Base fiscal | Dias corr. | Dias úteis
---------------------+---------------------+----------------------------------------+------------+-------------+------------+-----------
Lote 3400 mai.       | ativo               | CDB Neon Planejado 150% CDI - 60 dias  | 2026-05-08 | 2026-05-08  | 10         | 6         
Lote 3000 mai.       | ativo               | CDB Genial 220% CDI - 60 dias          | 2026-05-08 | 2026-05-08  | 10         | 6         
Lote 2800 mai.       | ativo               | Mercado Pago Cofrinho 120% CDI (Meli+) | 2026-05-08 | 2026-05-08  | 10         | 6         
Lote 5680 abr.       | ativo               | CDB Neon Planejado 150% CDI - 60 dias  | 2026-04-14 | 2026-04-14  | 34         | 22        
Lote 3000 mai Genial | ativo_pos_switching | CDB Genial 220% CDI - 60 dias          | 2026-05-06 | 2026-05-06  | 12         | 8         
Lote 3120 mai        | ativo_pos_switching | Mercado Pago Cofrinho 120% CDI (Meli+) | 2026-05-05 | 2026-05-05  | 13         | 9         
Lote 3000 mai Neon   | ativo_pos_switching | CDB Neon Planejado 150% CDI - 60 dias  | 2026-05-05 | 2026-05-05  | 13         | 9         

  valores e patrimônio:
Lote                 | Orig.   | Bruto sac. | Líq. sac. | Bruto atual | Líq. atual | Patr. líq. | Rend. líq.
---------------------+---------+------------+-----------+-------------+------------+------------+-----------
Lote 3400 mai.       | 3429.00 | 0.00       | 0.00      | 3445.52     | 3433.35    | 3433.35    | 4.35      
Lote 3000 mai.       | 3000.00 | 0.00       | 0.00      | 3021.22     | 3005.59    | 3005.59    | 5.59      
Lote 2800 mai.       | 2800.00 | 0.00       | 0.00      | 2810.78     | 2808.36    | 2808.36    | 8.36      
Lote 5680 abr.       | 5680.00 | 927.01     | 927.01    | 4838.09     | 4818.95    | 5745.96    | 65.96     
Lote 3000 mai Genial | 3000.00 | 0.00       | 0.00      | 3028.32     | 3008.78    | 3008.78    | 8.78      
Lote 3120 mai        | 3122.53 | 156.57     | 156.40    | 2827.28     | 2823.62    | 2980.02    | 0.00      
Lote 3000 mai Neon   | 3119.00 | 0.00       | 0.00      | 3141.56     | 3126.69    | 3126.69    | 7.69      

- patrimônio total dos lotes:
Métrica                                                                 | Valor   
------------------------------------------------------------------------+---------
Valor original total                                                    | 79027.16
Valor total investido em carteira                                       | 24150.53
Valor total bruto sacado                                                | 47351.96
Valor total líquido sacado                                              | 47210.37
Valor bruto atual                                                       | 23112.77
Valor líquido atual                                                     | 23025.34
Patrimônio líquido atual                                                | 70235.71
Rendimento líquido atual                                                | -8791.45
Valor original total — observado                                        | 79027.16
Valor original destinos pós-switching — sintético                       | 9241.53 
Valor original observado sem destinos pós-switching sintéticos          | 69785.63
Base econômica explícita — recebidos brutos                             | 79027.16
Valor líquido migrado para destinos pós-switching                       | 9433.94 
Valor bruto sacado — origens migradas                                   | 5557.02 
Valor líquido sacado — origens migradas                                 | 5533.16 
Patrimônio líquido atual — reconciliado com origens migradas            | 75768.87
Rendimento líquido atual — reconciliado contra recebidos                | -3258.29
Rendimento líquido atual — reconciliado contra valor original observado | -3258.29

- resumo de recebidos:
- Total de recebidos: 18
- Valor total bruto: 79027.16
- Status recebido: {'aplicado': 17, 'uso_pre_aplicacao_com_aporte_posterior': 1}
- Destino potencial: {'aplicacao': 17, 'pagamento_e_aplicacao': 1}
- Recebidos com pagamento vinculado: 11
- Recebidos em janela pré-aplicação: 0
- Recebidos usados antes da aplicação: 1
Saída operacional gerada em: C:\Users\Weverton\OneDrive\GitHub\payment-investment-allocation\saidas\oficial\relatorio_operacional_v225.xlsx
```

## 6. Conclusão

A V3.7D corrige a duplicidade residual observável de origens migradas em `lotes_exauridos`, mantendo a alteração restrita à saída observável.

Próxima microetapa recomendada:

```text
V17-F0-V.3.7E — Especifica contratos mínimos entre Etapa 3, replay, ledger e saída canônica
```

---

## 7. Ajuste complementar no resumo patrimonial

Após a correção da duplicidade visual em `lotes_exauridos`, foi identificado que o bloco `patrimônio total dos lotes` ainda calculava métricas sobre a base consolidada antiga.

Esse comportamento fazia o resumo patrimonial continuar capturando uma perda artificial associada às origens migradas por switching.

A correção complementar fez `construir_resumo_patrimonio_total_lotes(...)` usar a mesma base observável filtrada das tabelas principais.

Ajustes realizados:

- remove as origens migradas da base consolidada de exauridos;
- acrescenta as linhas observáveis específicas de `migrado_por_switching`;
- evita que `Rendimento líquido atual` capture perda artificial de:
  - `Lote 3000 mar. B`;
  - `Lote 3000 mar. V`;
  - `Lote 8500 mar.`;
- evita dupla reconciliação quando as origens migradas já estão incluídas no resumo.

## 8. Evidência da auditoria complementar

A auditoria complementar retornou:

```text
Lote 3000 mar. B -> qtd_id = 1, status = migrado_por_switching, qtd_valores = 1, patrimônio = 3119.00, rendimento = 119.00
Lote 3000 mar. V -> qtd_id = 1, status = migrado_por_switching, qtd_valores = 1, patrimônio = 3122.53, rendimento = 122.53
Lote 8500 mar.   -> qtd_id = 1, status = migrado_por_switching, qtd_valores = 1, patrimônio = 8725.57, rendimento = 225.57

Valor original total = 78940.16
Patrimônio líquido atual = 79669.65
Rendimento líquido atual = 729.49
Patrimônio líquido atual — reconciliado com origens migradas = 79669.65
Rendimento líquido atual — reconciliado contra valor original observado = 729.49

VALIDACAO_RESUMO_V37D_OK
9. Conclusão final da V3.7D

A V3.7D corrige:

a duplicidade observável das origens migradas em lotes_exauridos;
a contaminação do resumo patrimonial causada pela base consolidada antiga.

A alteração permanece restrita a nucleo/saida_observavel.py.

Não houve alteração em:

saida_canonica.py;
aplicacao/principal.py;
Etapa 3;
replay;
ledger;
motor;
dados.

Status final:

V37D_CORRIGE_DUPLICIDADE_ORIGENS_MIGRADAS_EXAURIDOS=aprovada
VALIDACAO_V37D_OK=sim
VALIDACAO_RESUMO_V37D_OK=sim

