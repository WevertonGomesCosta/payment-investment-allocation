# ME-V17-F0-V36F — Corrige neutralizacao de origens migradas por switching

## 1. Identificacao

- MICROETAPA: ME-V17-F0-V36F
- VERSAO_CANDIDATA: V17-F0-V.3.6F
- TIPO: CODIGO / SAIDA CANONICA / CONSISTENCIA PATRIMONIAL
- CLASSE: CORRIGE_NEUTRALIZACAO_ORIGENS_MIGRADAS_SWITCHING
- ALTERA_CODIGO: sim
- ALTERA_SAIDA_CANONICA: sim
- ALTERA_ETAPA_3: nao
- ALTERA_MOTOR: nao
- ALTERA_LEDGER: nao
- ALTERA_PACOTE_ENTRADA_RESOLVIDA: nao
- ALTERA_GATE: nao
- ALTERA_DADOS: nao

## 2. Condicao de entrada

A microetapa foi executada apos a V3.6E, que diagnosticou que:

- Lote 3000 mar. B continuava em lotes_ativos;
- Lote 3000 mar. V continuava em lotes_ativos;
- Lote 8500 mar. continuava em lotes_ativos;
- havia risco de dupla contribuicao patrimonial;
- os destinos POS estavam coerentes apos a V3.6D.

## 3. Ponto alterado

Arquivo alterado:

- nucleo/saida_canonica.py

Ponto de alteracao:

- construir_saida_canonica(...), depois de _construir_origens_migradas_por_switching_auditoria(...)
- antes da montagem final da auditoria e do PacoteSaidaCanonica

Funcoes adicionadas:

- _valor_monetario_situacao(...)
- _neutralizar_origens_migradas_situacao(...)

## 4. Regra implementada

Quando um lote aparece em origens_migradas_por_switching e tambem em lotes_ativos, ele deixa de permanecer como ativo comum.

A neutralizacao:

- preserva auditoria;
- preserva extrato passado;
- preserva destinos POS;
- nao altera replay;
- nao altera ledger;
- nao altera Etapa 3;
- nao altera PacoteEntradaResolvida;
- remove da camada ativa o patrimonio de origem migrada.

## 5. Evidencias da execucao principal

```text

=== BASELINE ===
- versão: V225
- raiz do repositório: C:\Users\Weverton\OneDrive\GitHub\payment-investment-allocation
- config carregado: C:\Users\Weverton\OneDrive\GitHub\payment-investment-allocation\dados\config_atualizado.json
- planilha carregada: C:\Users\Weverton\OneDrive\GitHub\payment-investment-allocation\dados\dados_financeiros.xlsx

=== EXECUÇÃO ===
- timezone: America/Sao_Paulo
- data de referência: 2026-05-18
- warnings de rede configurados: sim

=== ORIGEM DOS DADOS ===
- dados financeiros: download
- status obtenção planilha: ok
- dados CDI/BCB: cache_local
- status obtenção CDI/BCB: cache_atualizado_sem_fetch

=== DEPENDÊNCIAS ===
[OK] Dependências essenciais da baseline — baseline mínima e auditoria estrutural
- instaladas: numpy, openpyxl, pandas, pulp, python-dateutil, requests, workalendar
- ausentes: nenhuma

=== CACHE CDI DIÁRIO (BCB) ===
[OK] Cache diário de CDI para auditoria e replay — 91 datas
- data inicial da consulta: 2026-01-01
- data final da consulta: 2026-05-18
- última data com fator no cache: 2026-05-15
- fonte da série: cache_local
- status do fetch: cache_atualizado_sem_fetch
- cache atualizado para referência: sim
- data de atualização do cache: 2026-05-18
- caminho do cache: C:\Users\Weverton\OneDrive\GitHub\payment-investment-allocation\dados\cache_bcb.json

=== ABAS ENCONTRADAS ===
- [1] Resumo Mensal
- [2] Salários
- [3] Todos os Gastos
- [4] Switching
- [5] Inventário de Lotes
- [6] Carteira

=== RESUMO ESTRUTURAL DAS ABAS OPERACIONAIS CANÔNICAS ===
[OK] Carteira — 85 linhas, 51 colunas
  colunas (primeiras 8): Nome, Taxa_Base_CDI, Taxa_Bonus_CDI, Dias_Bonus, Prazo_Dias, Carência_Dias, Isento_IR, Aplicação_Mínima
[OK] Salários — 42 linhas, 4 colunas
  colunas (primeiras 8): Nome, Data Recebimento, Origem, Valor
[OK] Todos os Gastos — 270 linhas, 5 colunas
  colunas (primeiras 8): Data, Descrição, Valor, Pago, Lote usado
[OK] Switching — 4 linhas, 6 colunas
  colunas (primeiras 8): Lote (ID) Antes, Lote (ID) Depois, Data Recebimento, Data Aplicação, Valor Líquido Migrado, Investimento
[OK] Inventário de Lotes — 14 linhas, 5 colunas
  colunas (primeiras 8): Lote (ID), Data Recebimento, Data Aplicação, Valor Original, Investimento

=== ABAS OPERACIONAIS CANÔNICAS ===
[OK] Abas operacionais canônicas — 5 blocos esperados
[OK] Bloco carteira — Carteira
- presente: sim
- linhas: 85
- colunas: 51

[OK] Bloco salarios — Salários
- presente: sim
- linhas: 42
- colunas: 4

[OK] Bloco despesas — Todos os Gastos
- presente: sim
- linhas: 270
- colunas: 5

[OK] Bloco switching — Switching
- presente: sim
- linhas: 4
- colunas: 6

[OK] Bloco lotes — Inventário de Lotes
- presente: sim
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
Lote 8500 mar.    | exaurido_por_saque    | CDB Sofisa 105%                        | 2026-03-06 | 2026-03-06  | 2026-05-06   | 73         | 48        
Lote 3000 mar. B  | exaurido_por_saque    | CDB XP 230%                            | 2026-03-04 | 2026-03-04  | n/d          | 75         | 50        
Lote 3000 mar. V  | exaurido_por_saque    | CDB XP 230%                            | 2026-03-03 | 2026-03-03  | n/d          | 76         | 51        
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
Lote 8500 mar.    | 8587.00  | 5557.02    | 5533.16   | 0.00        | 0.00       | 5533.16    | -3053.84  
Lote 3000 mar. B  | 3000.00  | 0.00       | 0.00      | 0.00        | 0.00       | 0.00       | -3000.00  
Lote 3000 mar. V  | 3000.00  | 0.00       | 0.00      | 0.00        | 0.00       | 0.00       | -3000.00  
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

## 6. Auditoria direcionada

```text
=== CAMPOS V3.6D ===
pos_canonico_ativo = True
ponte_passiva_pos_desativada_por_pos_canonico = True
destinos_pos_switching_passivos_para_situacao_total = 0
destinos_pos_switching_passivos_preservados_auditoria_total = 4

=== CAMPOS V3.6F ===
origens_migradas_neutralizadas_situacao_total = 3
patrimonio_liquido_ativo_neutralizado_origens_migradas = 9505.61
origens_migradas_ativas_remanescentes_total = 0
origens_migradas_ativas_remanescentes = []

=== ORIGENS MIGRADAS ===
{'lote': 'Lote 3000 mar. B', 'qtd_ativos': 0, 'qtd_exauridos': 1, 'patrimonio_ativo': 0, 'status_exauridos': ['migrado_por_switching']}
{'lote': 'Lote 3000 mar. V', 'qtd_ativos': 0, 'qtd_exauridos': 1, 'patrimonio_ativo': 0, 'status_exauridos': ['migrado_por_switching']}
{'lote': 'Lote 8500 mar.', 'qtd_ativos': 0, 'qtd_exauridos': 1, 'patrimonio_ativo': 0, 'status_exauridos': ['migrado_por_switching']}

=== DESTINOS POS ===
{'lote': 'Lote 3120 mai', 'qtd_ativos': 1, 'qtd_exauridos': 0, 'patrimonio': 2823.62, 'duplicado': False, 'status': [None]}
{'lote': 'Lote 3000 mai Neon', 'qtd_ativos': 1, 'qtd_exauridos': 0, 'patrimonio': 3126.69, 'duplicado': False, 'status': [None]}
{'lote': 'Lote 3000 mai Genial', 'qtd_ativos': 1, 'qtd_exauridos': 0, 'patrimonio': 3008.78, 'duplicado': False, 'status': [None]}
{'lote': 'Lote 190 mai', 'qtd_ativos': 0, 'qtd_exauridos': 1, 'patrimonio': 0.0, 'duplicado': False, 'status': [None]}

VALIDACAO_V36F_OK
```

## 7. Auditoria XLSX

```text
xlsx_usado= saidas\oficial\relatorio_operacional_v225.xlsx
abas= ['Extrato Passado', 'Extrato Futuro', 'Switching', 'Carteira', 'Situação Atual', 'Saida Canonica', 'Tabela Operacional Pagamentos', 'Pagamentos Operacionais', 'Fontes Pagamento', 'Multifonte Resgates', 'Pendencias Pagamentos', 'Pagamentos Metadados', 'Auditoria Fontes']

ABA= Extrato Passado
qtd_origens= 9
qtd_pos= 3
ORIGEM: 2026-05-06 | Cemig SIM | despesa_auto_00100 | Lote 8500 mar. | 4582.51 | 419.23 | 2.13 | 417.1 | 4163.28
ORIGEM: 2026-05-06 | Faxina Rosa | despesa_auto_00101 | Lote 8500 mar. | 4163.28 | 954.85 | 4.85 | 950 | 3208.43
ORIGEM: 2026-04-30 | Biola | despesa_auto_00094 | Lote 8500 mar. | 5569.49 | 60.28 | 0.28 | 60 | 5509.21
ORIGEM: 2026-04-30 | Implante Velt | despesa_auto_00095 | Lote 8500 mar. | 5509.21 | 401.89 | 1.89 | 400 | 5107.32
ORIGEM: 2026-04-30 | Tratamento Lara | despesa_auto_00096 | Lote 8500 mar. | 5107.32 | 532.51 | 2.51 | 530 | 4574.81
ORIGEM: 2026-04-20 | Cartão Azul | despesa_auto_00089 | Lote 8500 mar. | 8735.64 | 2853.45 | 10.92 | 2842.53 | 5882.19
ORIGEM: 2026-04-20 | Cemig | despesa_auto_00090 | Lote 8500 mar. | 5882.19 | 99.36 | 0.38 | 98.98 | 5782.83
ORIGEM: 2026-04-20 | Concurso velt | despesa_auto_00091 | Lote 8500 mar. | 5782.83 | 121.21 | 0.46 | 120.75 | 5661.62
ORIGEM: 2026-04-20 | Condomínio | despesa_auto_00092 | Lote 8500 mar. | 5661.62 | 114.24 | 0.44 | 113.8 | 5547.38
POS: 2026-05-15 | Internet | despesa_auto_00112 | Lote 3120 mai | 2956.02 | 132.55 | 0.15 | 132.4 | 2823.62
POS: 2026-05-13 | Aluguel | despesa_auto_00107 | Lote 190 mai | 192.41 | 193.03 | 0.14 | 192.89 | 0
POS: 2026-05-13 | Pelada | despesa_auto_00111 | Lote 3120 mai | 2980.02 | 24.02 | 0.02 | 24 | 2956.02

ABA= Extrato Futuro
qtd_origens= 133
qtd_pos= 18
ORIGEM: 2026-05-20 | Cartão Azul | despesa_auto_00113 | 5372 | Lote 3120 mai + Lote 3000 mai Neon | 6241.53 | 5372 | 0 | 5372 | 869.53 | sim | sem_switching | Lote 3000 mar. V | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-05-20 | Condomínio | despesa_auto_00114 | 113.31 | Lote 3000 mai Neon | 1119 | 113.31 | 0 | 113.31 | 1005.69 | sim | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-05-30 | Implante Velt | despesa_auto_00115 | 400 |  |  |  |  |  |  | não | sem_switching | Lote 3000 mar. V | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-02 | Cartão NU | despesa_auto_00116 | 580 |  |  |  |  |  |  | não | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-06 | Faxina Rosa | despesa_auto_00117 | 950 |  |  |  |  |  |  | não | sem_switching | Lote 3000 mar. V | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-07 | Claro | despesa_auto_00118 | 110 |  |  |  |  |  |  | não | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-10 | Ginástica Biola | despesa_auto_00119 | 65 |  |  |  |  |  |  | não | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-10 | Thayrine | despesa_auto_00120 | 120 |  |  |  |  |  |  | não | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-10 | Tratamento Lara | despesa_auto_00121 | 530 |  |  |  |  |  |  | não | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-11 | Cemig | despesa_auto_00122 | 95.12 |  |  |  |  |  |  | não | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-12 | Aluguel | despesa_auto_00123 | 981.95 |  |  |  |  |  |  | não | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-12 | Escola | despesa_auto_00124 | 2831.4 | Lote 3120 mai + Lote 3000 mai Neon | 5259.58 | 2831.4 | 0 | 2831.4 | 2428.18 | sim | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-12 | Pelada | despesa_auto_00125 | 50 | Lote 3000 mai Neon | 1005.69 | 50 | 0 | 50 | 955.69 | sim | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-19 | Churrasco pelada | despesa_auto_00127 | 40 | Lote 5680 abr. | 3705.69 | 40.7 | 0.7 | 40 | 3665.69 | sim | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 2653.57 | não | não | não determinado | ok | 3705.69 | 40 | 3665.69 | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-20 | Cartão Azul | despesa_auto_00128 | 7200 | Lote 5680 abr. + Lote 3120 mai | 7941.48 | 7200 | 0 | 7200 | 741.48 | sim | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-06-30 | Implante Velt | despesa_auto_00130 | 400 | Lote 5680 abr. | 3665.69 | 403.86 | 3.86 | 400 | 3265.69 | sim | sem_switching | Lote 3000 mar. V | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 2653.57 | não | não | não determinado | ok | 3665.69 | 400 | 3265.69 | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-07-02 | Cartão NU | despesa_auto_00131 | 930 |  |  |  |  |  |  | não | sem_switching | Lote 3000 mar. V | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 2653.57 | não | não | status_ok_sem_cobertura_corrigido_v17_f0a | sem_saldo_temporal_auditavel | 3265.69 | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-07-06 | Faxina Rosa | despesa_auto_00132 | 950 | Lote 5680 abr. | 3265.69 | 960.92 | 10.92 | 950 | 2315.69 | sim | sem_switching | Lote 3000 mar. V | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 2653.57 | não | não | não determinado | ok | 3265.69 | 950 | 2315.69 | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-07-12 | Escola | despesa_auto_00137 | 2831.4 |  |  |  |  |  |  | não | sem_switching | Lote 3000 mar. V | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 2653.57 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
ORIGEM: 2026-07-12 | Pelada | despesa_auto_00138 | 50 |  |  |  |  |  |  | não | sem_switching | Lote 3000 mar. V | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 1889.08 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-05-20 | Cartão Azul | despesa_auto_00113 | 5372 | Lote 3120 mai + Lote 3000 mai Neon | 6241.53 | 5372 | 0 | 5372 | 869.53 | sim | sem_switching | Lote 3000 mar. V | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-05-20 | Condomínio | despesa_auto_00114 | 113.31 | Lote 3000 mai Neon | 1119 | 113.31 | 0 | 113.31 | 1005.69 | sim | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-06-12 | Escola | despesa_auto_00124 | 2831.4 | Lote 3120 mai + Lote 3000 mai Neon | 5259.58 | 2831.4 | 0 | 2831.4 | 2428.18 | sim | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-06-12 | Pelada | despesa_auto_00125 | 50 | Lote 3000 mai Neon | 1005.69 | 50 | 0 | 50 | 955.69 | sim | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-06-20 | Cartão Azul | despesa_auto_00128 | 7200 | Lote 5680 abr. + Lote 3120 mai | 7941.48 | 7200 | 0 | 7200 | 741.48 | sim | sem_switching | Lote 8500 mar. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-09-20 | Cartão Azul | despesa_auto_00168 | 6850 | Lote 5680 abr. + Lote 3400 mai. | 8252.3 | 6850 | 0 | 6850 | 1402.3 | sim | sem_switching | Lote 3000 mai. + Lote 3000 mai Genial | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-10-12 | Escola | despesa_auto_00180 | 2831.4 |  |  |  |  |  |  | não | sem_switching | Lote 3000 mai Genial | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-10-20 | Cartão Azul | despesa_auto_00183 | 6000 | Lote 5680 abr. + Lote 3400 mai. | 8252.3 | 6000 | 0 | 6000 | 2252.3 | sim | sem_switching | Lote 3000 mai Genial + Lote 3000 mar. B | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-11-02 | Cartão NU | despesa_auto_00186 | 2200 |  |  |  |  |  |  | não | sem_switching | Lote 3000 mai Genial | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-11-20 | Cartão Azul | despesa_auto_00196 | 5750 | Lote 5680 abr. + Lote 3400 mai. | 8252.3 | 5750 | 0 | 5750 | 2502.3 | sim | sem_switching | Lote 3000 mai. + Lote 3000 mai Neon | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-12-11 | Rematricula | despesa_auto_00205 | 2900 |  |  |  |  |  |  | não | sem_switching | Lote 3000 mai Genial | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | saldo_temporal_insuficiente_cumulativo | sem_saldo_temporal_auditavel | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2026-12-20 | Cartão Azul | despesa_auto_00210 | 6250 | Lote 5680 abr. + Lote 3400 mai. | 8252.3 | 6250 | 0 | 6250 | 2002.3 | sim | sem_switching | Lote 3000 mai. + Lote 3120 mai + Lote 3000 mar. B + Lote 2800 mai. + Lote 5680 abr. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2027-01-20 | Cartão Azul | despesa_auto_00220 | 7796 | Lote 5680 abr. + Lote 3400 mai. | 8252.3 | 7796 | 0 | 7796 | 456.3 | sim | sem_switching | Lote 3000 mar. B + Lote 3000 mai. + Lote 3120 mai + Lote 2800 mai. + Lote 3400 mai. + Lote 3000 mar. V + Lote 5680 abr. + Lote 3000 mai Neon + Lote 3000 mai Genial | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2027-02-20 | Cartão Azul | despesa_auto_00234 | 6004.07 | Lote 5680 abr. + Lote 3400 mai. | 8252.3 | 6004.07 | 0 | 6004.07 | 2248.23 | sim | sem_switching | Lote 3000 mar. V + Lote 5680 abr. + Lote 3000 mai. + Lote 3400 mai. + Lote 3120 mai + Lote 2800 mai. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2027-03-20 | Cartão Azul | despesa_auto_00247 | 7494.55 | Lote 5680 abr. + Lote 3400 mai. | 8252.3 | 7494.55 | 0 | 7494.55 | 757.75 | sim | sem_switching | Lote 3000 mar. V + Lote 2800 mai. + Lote 3400 mai. + Lote 5680 abr. + Lote 3120 mai + Lote 3000 mai. + Lote 3000 mai Neon + Lote 3000 mar. B + Lote 3000 mai Genial | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2027-04-02 | Cartão NU | despesa_auto_00250 | 5310.25 | Lote 5680 abr. + Lote 3400 mai. | 8252.3 | 5310.25 | 0 | 5310.25 | 2942.05 | sim | sem_switching | Lote 3000 mar. V + Lote 3400 mai. + Lote 5680 abr. + Lote 3000 mai. + Lote 3120 mai + Lote 2800 mai. | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2027-04-20 | Cartão Azul | despesa_auto_00259 | 6350 | Lote 5680 abr. + Lote 3400 mai. | 8252.3 | 6350 | 0 | 6350 | 1902.3 | sim | sem_switching | Lote 3000 mai. + Lote 3000 mar. V + Lote 5680 abr. + Lote 3120 mai + Lote 3400 mai. + Lote 3000 mai Neon + Lote 3000 mar. B + Lote 2800 mai. + Lote 3000 mai Genial | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d
POS: 2027-05-20 | Cartão Azul | despesa_auto_00269 | 5372 | Lote 5680 abr. + Lote 3400 mai. | 8252.3 | 5372 | 0 | 5372 | 2880.3 | sim | sem_switching | Lote 3000 mar. V + Lote 3000 mai. + Lote 3000 mai Neon + Lote 3120 mai + Lote 5680 abr. + Lote 3000 mar. B + Lote 2800 mai. + Lote 3400 mai. + Lote 3000 mai Genial | não | pay_only | não determinado | não determinado | não determinado |  | n/d | 0 | não | não | n/d | ok | n/d | n/d | n/d | não | n/d | 0 | n/d | n/d | 0 | 0 | n/d | n/d

ABA= Switching
qtd_origens= 4
qtd_pos= 0
ORIGEM: 2026-05-05 | Lote 3000 mar. V | CDB XP 230% | Mercado Pago Cofrinho 120% CDI (Meli+) |  | 3122.53 | materializado_estado_temporal_v17_f0_o2
ORIGEM: 2026-05-05 | Lote 3000 mar. B | CDB XP 230% | CDB Neon Planejado 150% CDI - 60 dias |  | 3119 | materializado_estado_temporal_v17_f0_o2
ORIGEM: 2026-05-06 | Lote 8500 mar. | CDB Sofisa 105% | CDB Genial 220% CDI - 60 dias |  | 3000 | materializado_estado_temporal_v17_f0_o2
ORIGEM: 2026-05-06 | Lote 8500 mar. | CDB Sofisa 105% | Mercado Pago Cofrinho 120% CDI (Meli+) |  | 192.41 | materializado_estado_temporal_v17_f0_o2

ABA= Situação Atual
qtd_origens= 18
qtd_pos= 12
ORIGEM: Lote 8500 mar. | exaurido_por_saque | CDB Sofisa 105% | 2026-03-06 | 2026-03-06 | 2026-05-06 | 73 | 48 |  |  |  |  | 
ORIGEM: Lote 3000 mar. B | exaurido_por_saque | CDB XP 230% | 2026-03-04 | 2026-03-04 | n/d | 75 | 50 |  |  |  |  | 
ORIGEM: Lote 3000 mar. V | exaurido_por_saque | CDB XP 230% | 2026-03-03 | 2026-03-03 | n/d | 76 | 51 |  |  |  |  | 
ORIGEM: Lote 3000 mar. B | migrado_por_switching | CDB XP 230% | 2026-03-04 | 2026-03-04 | 2026-05-05 | 62 | 41 |  |  |  |  | 
ORIGEM: Lote 3000 mar. V | migrado_por_switching | CDB XP 230% | 2026-03-03 | 2026-03-03 | 2026-05-05 | 63 | 42 |  |  |  |  | 
ORIGEM: Lote 8500 mar. | migrado_por_switching | CDB Sofisa 105% | 2026-03-06 | 2026-03-06 | 2026-05-06 | 61 | 40 |  |  |  |  | 
ORIGEM: Lote 8500 mar. | 8587 | 5557.02 | 5533.16 | 0 | 0 | 5533.16 | -3053.84 |  |  |  |  | 
ORIGEM: Lote 3000 mar. B | 3000 | 0 | 0 | 0 | 0 | 0 | -3000 |  |  |  |  | 
ORIGEM: Lote 3000 mar. V | 3000 | 0 | 0 | 0 | 0 | 0 | -3000 |  |  |  |  | 
ORIGEM: Lote 3000 mar. B | 3000 | 0 | 0 | 0 | 0 | 3119 | 119 |  |  |  |  | 
ORIGEM: Lote 3000 mar. V | 3000 | 0 | 0 | 0 | 0 | 3122.53 | 122.53 |  |  |  |  | 
ORIGEM: Lote 8500 mar. | 8500 | 5557.02 | 5533.16 | 0 | 0 | 8725.57 | 225.57 |  |  |  |  | 
ORIGEM: Lote 3000 mar. B | migrado_por_switching | migrado_por_switching | 2026-05-05 | 62 | 41 | 3119 | 0 | 0 | 0 | 1 | True | True
ORIGEM: Lote 3000 mar. V | migrado_por_switching | migrado_por_switching | 2026-05-05 | 63 | 42 | 3122.53 | 0 | 0 | 0 | 1 | True | True
ORIGEM: Lote 8500 mar. | migrado_por_switching | migrado_por_switching | 2026-05-06 | 61 | 40 | 3192.41 | 5557.02 | 5533.16 | 9 | 2 | True | True
ORIGEM: recebido::lote_3000_mar._v | Lote 3000 mar. V | 2026-03-03 | 2026-03-03 | 3000 | 3000 | aplicado | aplicacao | 0 | 0 | 3000 | sim | recebido integralmente associado a lote aportado.
ORIGEM: recebido::lote_3000_mar._b | Lote 3000 mar. B | 2026-03-04 | 2026-03-04 | 3000 | 3000 | aplicado | aplicacao | 0 | 0 | 3000 | sim | recebido integralmente associado a lote aportado.
ORIGEM: recebido::lote_8500_mar. | Lote 8500 mar. | 2026-03-06 | 2026-03-06 | 8587 | 8587 | aplicado | aplicacao | 9 | 5533.16 | 8587 | sim | recebido integralmente associado a lote aportado.
POS: Lote 190 mai | exaurido_por_saque | Mercado Pago Cofrinho 120% CDI (Meli+) | 2026-05-06 | 2026-05-06 | 2026-05-13 | 7 | 5 |  |  |  |  | 
POS: Lote 190 mai | 192.41 | 193.03 | 192.89 | 0 | 0 | 192.89 | 0.48 |  |  |  |  | 
POS: Lote 3000 mai Genial | ativo_pos_switching | CDB Genial 220% CDI - 60 dias | 2026-05-06 | 2026-05-06 | 12 | 8 |  |  |  |  |  | 
POS: Lote 3120 mai | ativo_pos_switching | Mercado Pago Cofrinho 120% CDI (Meli+) | 2026-05-05 | 2026-05-05 | 13 | 9 |  |  |  |  |  | 
POS: Lote 3000 mai Neon | ativo_pos_switching | CDB Neon Planejado 150% CDI - 60 dias | 2026-05-05 | 2026-05-05 | 13 | 9 |  |  |  |  |  | 
POS: Lote 3000 mai Genial | 3000 | 0 | 0 | 3028.32 | 3008.78 | 3008.78 | 8.78 |  |  |  |  | 
POS: Lote 3120 mai | 3122.53 | 156.57 | 156.4 | 2827.28 | 2823.62 | 2980.02 | 0 |  |  |  |  | 
POS: Lote 3000 mai Neon | 3119 | 0 | 0 | 3141.56 | 3126.69 | 3126.69 | 7.69 |  |  |  |  | 
POS: recebido::lote_3000_mai_neon | Lote 3000 mai Neon | 2026-05-04 | 2026-05-05 | 3119 | 3119 | aplicado | aplicacao | 0 | 0 | 3119 | sim | recebido integralmente associado a lote aportado.
POS: recebido::lote_3120_mai | Lote 3120 mai | 2026-05-04 | 2026-05-05 | 3122.53 | 3122.53 | aplicado | aplicacao | 2 | 156.4 | 3122.53 | sim | recebido integralmente associado a lote aportado.
POS: recebido::lote_190_mai | Lote 190 mai | 2026-05-06 | 2026-05-06 | 192.41 | 192.41 | aplicado | aplicacao | 1 | 192.89 | 192.41 | sim | recebido integralmente associado a lote aportado.
POS: recebido::lote_3000_mai_genial | Lote 3000 mai Genial | 2026-05-06 | 2026-05-06 | 3000 | 3000 | aplicado | aplicacao | 0 | 0 | 3000 | sim | recebido integralmente associado a lote aportado.

ABA= Tabela Operacional Pagamentos
qtd_origens= 0
qtd_pos= 14
POS: 2026-05-15 | Internet | 132.4 | Lote 3120 mai | Lote 3120 mai | 1 | Lote 3120 mai |  | ok | aprovado_para_pagamento | pagar_com_lote_sugerido | Lote 3120 mai:ativo_pos_switching | 3110.96 | 132.4 | 2895.01 | extrato_futuro_saldo_remanescente | Lote 3120 mai:3110.96 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-05-20 | Cartão Azul | 5372 | Lote 3120 mai + Lote 3000 mai Neon | Lote 3120 mai + Lote 3000 mai Neon | 2 | Lote 3120 mai | Lote 3000 mai Neon | ok | aprovado_multifonte | pagar_com_fontes_componentes | Lote 3120 mai:ativo_pos_switching | Lote 3000 mai Neon:ativo_pos_switching | 6235.24 | 5372 | 869.53 | extrato_futuro_saldo_remanescente | Lote 3120 mai:3110.96 | Lote 3000 mai Neon:3124.28 | sim | 2 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-05-20 | Condomínio | 113.31 | Lote 3000 mai Neon | Lote 3000 mai Neon | 1 | Lote 3000 mai Neon |  | ok | aprovado_para_pagamento | pagar_com_lote_sugerido | Lote 3000 mai Neon:ativo_pos_switching | 3124.28 | 113.31 | 1205.69 | extrato_futuro_saldo_remanescente | Lote 3000 mai Neon:3124.28 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-05-30 | Implante Velt | 400 | Lote 3120 mai | Lote 3120 mai | 1 | Lote 3120 mai |  | ok | aprovado_para_pagamento | pagar_com_lote_sugerido | Lote 3120 mai:ativo_pos_switching | 3110.96 | 400 | 2495.01 | extrato_futuro_saldo_remanescente | Lote 3120 mai:3110.96 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-06-02 | Cartão NU | 580 | Lote 3120 mai | Lote 3120 mai | 1 | Lote 3120 mai |  | ok | aprovado_para_pagamento | pagar_com_lote_sugerido | Lote 3120 mai:ativo_pos_switching | 3110.96 | 580 | 1915.01 | extrato_futuro_saldo_remanescente | Lote 3120 mai:3110.96 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-06-06 | Faxina Rosa | 950 | Lote 3120 mai | Lote 3120 mai | 1 | Lote 3120 mai |  | ok | aprovado_para_pagamento | pagar_com_lote_sugerido | Lote 3120 mai:ativo_pos_switching | 3110.96 | 950 | 965.01 | extrato_futuro_saldo_remanescente | Lote 3120 mai:3110.96 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-06-07 | Claro | 110 | Lote 3120 mai | Lote 3120 mai | 1 | Lote 3120 mai |  | ok | aprovado_para_pagamento | pagar_com_lote_sugerido | Lote 3120 mai:ativo_pos_switching | 3110.96 | 110 | 855.01 | extrato_futuro_saldo_remanescente | Lote 3120 mai:3110.96 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-06-10 | Ginástica Biola | 65 | Lote 3120 mai | Lote 3120 mai | 1 | Lote 3120 mai |  | ok | aprovado_para_pagamento | pagar_com_lote_sugerido | Lote 3120 mai:ativo_pos_switching | 3110.96 | 65 | 790.01 | extrato_futuro_saldo_remanescente | Lote 3120 mai:3110.96 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-06-10 | Thayrine | 120 | Lote 3120 mai | Lote 3120 mai | 1 | Lote 3120 mai |  | ok | aprovado_para_pagamento | pagar_com_lote_sugerido | Lote 3120 mai:ativo_pos_switching | 3110.96 | 120 | 670.01 | extrato_futuro_saldo_remanescente | Lote 3120 mai:3110.96 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-06-10 | Tratamento Lara | 530 | Lote 3120 mai | Lote 3120 mai | 1 | Lote 3120 mai |  | ok | aprovado_para_pagamento | pagar_com_lote_sugerido | Lote 3120 mai:ativo_pos_switching | 3110.96 | 530 | 140.01 | extrato_futuro_saldo_remanescente | Lote 3120 mai:3110.96 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-06-11 | Cemig | 95.12 | Lote 3120 mai | Lote 3120 mai | 1 | Lote 3120 mai |  | ok | aprovado_para_pagamento | pagar_com_lote_sugerido | Lote 3120 mai:ativo_pos_switching | 3110.96 | 95.12 | 44.89 | extrato_futuro_saldo_remanescente | Lote 3120 mai:3110.96 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-06-12 | Escola | 2831.4 | Lote 3120 mai + Lote 3000 mai Neon | Lote 3120 mai + Lote 3000 mai Neon | 2 | Lote 3120 mai | Lote 3000 mai Neon | ok | aprovado_multifonte | pagar_com_fontes_componentes | Lote 3120 mai:ativo_pos_switching | Lote 3000 mai Neon:ativo_pos_switching | 6235.24 | 2831.4 | 2428.18 | extrato_futuro_saldo_remanescente | Lote 3120 mai:3110.96 | Lote 3000 mai Neon:3124.28 | sim | 2 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-06-12 | Pelada | 50 | Lote 3000 mai Neon | Lote 3000 mai Neon | 1 | Lote 3000 mai Neon |  | ok | aprovado_para_pagamento | pagar_com_lote_sugerido | Lote 3000 mai Neon:ativo_pos_switching | 3124.28 | 50 | 1155.69 | extrato_futuro_saldo_remanescente | Lote 3000 mai Neon:3124.28 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim
POS: 2026-06-20 | Cartão Azul | 7200 | Lote 5680 abr. + Lote 3120 mai | Lote 5680 abr. + Lote 3120 mai | 2 | Lote 5680 abr. | Lote 3120 mai | ok | aprovado_multifonte | pagar_com_fontes_componentes | Lote 5680 abr.:nan | Lote 3120 mai:ativo_pos_switching | 7926.9 | 7200 | 738.47 | extrato_futuro_saldo_remanescente | Lote 5680 abr.:4815.94 | Lote 3120 mai:3110.96 | sim | 1 | nao | sem_alerta |  |  | nao_aplicavel | nao | sim

ABA= Fontes Pagamento
qtd_origens= 0
qtd_pos= 16
POS: 0 | 2026-05-15|internet|132.40 | 2026-05-15 | Internet | 132.4 | aprovado_para_pagamento | monofonte_aprovado | fonte_monofonte_aprovada_u0_u1 | 1 | Lote 3120 mai | lote | 132.4 | 132.4 | 0 | pagamento_monofonte_coberto_por_fonte_aprovada | sim | nao | sem_bloqueio_operacional_u3 | fonte_aprovada_sem_violacao_dura | n/d | n/d | sim | nao | nao | Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.
POS: 1 | 2026-05-20|cartao azul|5372.00 | 2026-05-20 | Cartão Azul | 5372 | aprovado_multifonte | multifonte_decomposto_diagnostico | fonte_multifonte_decomposta_u2 | 1 | Lote 3120 mai | lote | 3110.96 | 5372 | 0 | pagamento_multifonte_executavel | sim | nao | sem_bloqueio_operacional_u2 | pendencia_multifonte_sem_valor_resgate_explicito | resgate_multifonte_explicitado | pagamento_multifonte_executavel | sim | nao | nao | Linha multifonte decomposta pela U.2 em caráter diagnóstico. Não altera recomendador oficial.
POS: 1 | 2026-05-20|cartao azul|5372.00 | 2026-05-20 | Cartão Azul | 5372 | aprovado_multifonte | multifonte_decomposto_diagnostico | fonte_multifonte_decomposta_u2 | 2 | Lote 3000 mai Neon | lote | 2261.04 | 5372 | 0 | pagamento_multifonte_executavel | sim | nao | sem_bloqueio_operacional_u2 | pendencia_multifonte_sem_valor_resgate_explicito | resgate_multifonte_explicitado | pagamento_multifonte_executavel | sim | nao | nao | Linha multifonte decomposta pela U.2 em caráter diagnóstico. Não altera recomendador oficial.
POS: 2 | 2026-05-20|condominio|113.31 | 2026-05-20 | Condomínio | 113.31 | aprovado_para_pagamento | monofonte_aprovado | fonte_monofonte_aprovada_u0_u1 | 1 | Lote 3000 mai Neon | lote | 113.31 | 113.31 | 0 | pagamento_monofonte_coberto_por_fonte_aprovada | sim | nao | sem_bloqueio_operacional_u3 | fonte_aprovada_sem_violacao_dura | n/d | n/d | sim | nao | nao | Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.
POS: 3 | 2026-05-30|implante velt|400.00 | 2026-05-30 | Implante Velt | 400 | aprovado_para_pagamento | monofonte_aprovado | fonte_monofonte_aprovada_u0_u1 | 1 | Lote 3120 mai | lote | 400 | 400 | 0 | pagamento_monofonte_coberto_por_fonte_aprovada | sim | nao | sem_bloqueio_operacional_u3 | fonte_aprovada_sem_violacao_dura | n/d | n/d | sim | nao | nao | Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.
POS: 4 | 2026-06-02|cartao nu|580.00 | 2026-06-02 | Cartão NU | 580 | aprovado_para_pagamento | monofonte_aprovado | fonte_monofonte_aprovada_u0_u1 | 1 | Lote 3120 mai | lote | 580 | 580 | 0 | pagamento_monofonte_coberto_por_fonte_aprovada | sim | nao | sem_bloqueio_operacional_u3 | fonte_aprovada_sem_violacao_dura | n/d | n/d | sim | nao | nao | Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.
POS: 5 | 2026-06-06|faxina rosa|950.00 | 2026-06-06 | Faxina Rosa | 950 | aprovado_para_pagamento | monofonte_aprovado | fonte_monofonte_aprovada_u0_u1 | 1 | Lote 3120 mai | lote | 950 | 950 | 0 | pagamento_monofonte_coberto_por_fonte_aprovada | sim | nao | sem_bloqueio_operacional_u3 | fonte_aprovada_sem_violacao_dura | n/d | n/d | sim | nao | nao | Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.
POS: 6 | 2026-06-07|claro|110.00 | 2026-06-07 | Claro | 110 | aprovado_para_pagamento | monofonte_aprovado | fonte_monofonte_aprovada_u0_u1 | 1 | Lote 3120 mai | lote | 110 | 110 | 0 | pagamento_monofonte_coberto_por_fonte_aprovada | sim | nao | sem_bloqueio_operacional_u3 | fonte_aprovada_sem_violacao_dura | n/d | n/d | sim | nao | nao | Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.
POS: 7 | 2026-06-10|ginastica biola|65.00 | 2026-06-10 | Ginástica Biola | 65 | aprovado_para_pagamento | monofonte_aprovado | fonte_monofonte_aprovada_u0_u1 | 1 | Lote 3120 mai | lote | 65 | 65 | 0 | pagamento_monofonte_coberto_por_fonte_aprovada | sim | nao | sem_bloqueio_operacional_u3 | fonte_aprovada_sem_violacao_dura | n/d | n/d | sim | nao | nao | Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.
POS: 8 | 2026-06-10|thayrine|120.00 | 2026-06-10 | Thayrine | 120 | aprovado_para_pagamento | monofonte_aprovado | fonte_monofonte_aprovada_u0_u1 | 1 | Lote 3120 mai | lote | 120 | 120 | 0 | pagamento_monofonte_coberto_por_fonte_aprovada | sim | nao | sem_bloqueio_operacional_u3 | fonte_aprovada_sem_violacao_dura | n/d | n/d | sim | nao | nao | Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.
POS: 9 | 2026-06-10|tratamento lara|530.00 | 2026-06-10 | Tratamento Lara | 530 | aprovado_para_pagamento | monofonte_aprovado | fonte_monofonte_aprovada_u0_u1 | 1 | Lote 3120 mai | lote | 530 | 530 | 0 | pagamento_monofonte_coberto_por_fonte_aprovada | sim | nao | sem_bloqueio_operacional_u3 | fonte_aprovada_sem_violacao_dura | n/d | n/d | sim | nao | nao | Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.
POS: 10 | 2026-06-11|cemig|95.12 | 2026-06-11 | Cemig | 95.12 | aprovado_para_pagamento | monofonte_aprovado | fonte_monofonte_aprovada_u0_u1 | 1 | Lote 3120 mai | lote | 95.12 | 95.12 | 0 | pagamento_monofonte_coberto_por_fonte_aprovada | sim | nao | sem_bloqueio_operacional_u3 | fonte_aprovada_sem_violacao_dura | n/d | n/d | sim | nao | nao | Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.
POS: 12 | 2026-06-12|escola|2831.40 | 2026-06-12 | Escola | 2831.4 | aprovado_multifonte | multifonte_decomposto_diagnostico | fonte_multifonte_decomposta_u2 | 1 | Lote 3120 mai | lote | 2831.4 | 2831.4 | 0 | pagamento_multifonte_executavel | sim | nao | sem_bloqueio_operacional_u2 | pendencia_multifonte_sem_valor_resgate_explicito | resgate_multifonte_explicitado | pagamento_multifonte_executavel | sim | nao | nao | Linha multifonte decomposta pela U.2 em caráter diagnóstico. Não altera recomendador oficial.
POS: 12 | 2026-06-12|escola|2831.40 | 2026-06-12 | Escola | 2831.4 | aprovado_multifonte | multifonte_decomposto_diagnostico | fonte_multifonte_decomposta_u2 | 2 | Lote 3000 mai Neon | lote | 0 | 2831.4 | 0 | pagamento_multifonte_executavel | sim | nao | sem_bloqueio_operacional_u2 | pendencia_multifonte_sem_valor_resgate_explicito | resgate_multifonte_explicitado | pagamento_multifonte_executavel | sim | nao | nao | Linha multifonte decomposta pela U.2 em caráter diagnóstico. Não altera recomendador oficial.
POS: 13 | 2026-06-12|pelada|50.00 | 2026-06-12 | Pelada | 50 | aprovado_para_pagamento | monofonte_aprovado | fonte_monofonte_aprovada_u0_u1 | 1 | Lote 3000 mai Neon | lote | 50 | 50 | 0 | pagamento_monofonte_coberto_por_fonte_aprovada | sim | nao | sem_bloqueio_operacional_u3 | fonte_aprovada_sem_violacao_dura | n/d | n/d | sim | nao | nao | Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.
POS: 16 | 2026-06-20|cartao azul|7200.00 | 2026-06-20 | Cartão Azul | 7200 | aprovado_multifonte | multifonte_decomposto_diagnostico | fonte_multifonte_decomposta_u2 | 2 | Lote 3120 mai | lote | 2384.06 | 7200 | 0 | pagamento_multifonte_executavel | sim | nao | sem_bloqueio_operacional_u2 | pendencia_multifonte_sem_valor_resgate_explicito | resgate_multifonte_explicitado | pagamento_multifonte_executavel | sim | nao | nao | Linha multifonte decomposta pela U.2 em caráter diagnóstico. Não altera recomendador oficial.

ABA= Multifonte Resgates
qtd_origens= 0
qtd_pos= 5
POS: 1 | 2026-05-20|cartao azul|5372.00 | 2026-05-20 | Cartão Azul | 5372 | aprovado_multifonte | multifonte_decomposto_diagnostico | fonte_multifonte_decomposta_u2 | 1 | Lote 3120 mai | lote | 3110.96 | 5372 | 0 | pagamento_multifonte_executavel | sim | nao | sem_bloqueio_operacional_u2 | pendencia_multifonte_sem_valor_resgate_explicito | resgate_multifonte_explicitado | pagamento_multifonte_executavel | sim | nao | nao | Linha multifonte decomposta pela U.2 em caráter diagnóstico. Não altera recomendador oficial.
POS: 1 | 2026-05-20|cartao azul|5372.00 | 2026-05-20 | Cartão Azul | 5372 | aprovado_multifonte | multifonte_decomposto_diagnostico | fonte_multifonte_decomposta_u2 | 2 | Lote 3000 mai Neon | lote | 2261.04 | 5372 | 0 | pagamento_multifonte_executavel | sim | nao | sem_bloqueio_operacional_u2 | pendencia_multifonte_sem_valor_resgate_explicito | resgate_multifonte_explicitado | pagamento_multifonte_executavel | sim | nao | nao | Linha multifonte decomposta pela U.2 em caráter diagnóstico. Não altera recomendador oficial.
POS: 12 | 2026-06-12|escola|2831.40 | 2026-06-12 | Escola | 2831.4 | aprovado_multifonte | multifonte_decomposto_diagnostico | fonte_multifonte_decomposta_u2 | 1 | Lote 3120 mai | lote | 2831.4 | 2831.4 | 0 | pagamento_multifonte_executavel | sim | nao | sem_bloqueio_operacional_u2 | pendencia_multifonte_sem_valor_resgate_explicito | resgate_multifonte_explicitado | pagamento_multifonte_executavel | sim | nao | nao | Linha multifonte decomposta pela U.2 em caráter diagnóstico. Não altera recomendador oficial.
POS: 12 | 2026-06-12|escola|2831.40 | 2026-06-12 | Escola | 2831.4 | aprovado_multifonte | multifonte_decomposto_diagnostico | fonte_multifonte_decomposta_u2 | 2 | Lote 3000 mai Neon | lote | 0 | 2831.4 | 0 | pagamento_multifonte_executavel | sim | nao | sem_bloqueio_operacional_u2 | pendencia_multifonte_sem_valor_resgate_explicito | resgate_multifonte_explicitado | pagamento_multifonte_executavel | sim | nao | nao | Linha multifonte decomposta pela U.2 em caráter diagnóstico. Não altera recomendador oficial.
POS: 16 | 2026-06-20|cartao azul|7200.00 | 2026-06-20 | Cartão Azul | 7200 | aprovado_multifonte | multifonte_decomposto_diagnostico | fonte_multifonte_decomposta_u2 | 2 | Lote 3120 mai | lote | 2384.06 | 7200 | 0 | pagamento_multifonte_executavel | sim | nao | sem_bloqueio_operacional_u2 | pendencia_multifonte_sem_valor_resgate_explicito | resgate_multifonte_explicitado | pagamento_multifonte_executavel | sim | nao | nao | Linha multifonte decomposta pela U.2 em caráter diagnóstico. Não altera recomendador oficial.

ABA= Auditoria Fontes
qtd_origens= 133
qtd_pos= 73
ORIGEM: 2026-05-20 | Cartão Azul | despesa_auto_00113 | 5372 | Lote 3120 mai + Lote 3000 mai Neon | Lote 3000 mar. V | Lote 3120 mai + Lote 3000 mai Neon | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 5372 | True | True |  |  |  |  |  | pay_only | ok | n/d
ORIGEM: 2026-05-20 | Condomínio | despesa_auto_00114 | 113.31 | Lote 3000 mai Neon | Lote 8500 mar. | Lote 3000 mai Neon | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 113.31 | True | True |  |  |  |  |  | pay_only | ok | n/d
ORIGEM: 2026-05-30 | Implante Velt | despesa_auto_00115 | 400 |  | Lote 3000 mar. V | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 400 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
ORIGEM: 2026-06-02 | Cartão NU | despesa_auto_00116 | 580 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 580 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
ORIGEM: 2026-06-06 | Faxina Rosa | despesa_auto_00117 | 950 |  | Lote 3000 mar. V | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 950 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
ORIGEM: 2026-06-07 | Claro | despesa_auto_00118 | 110 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 110 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
ORIGEM: 2026-06-10 | Ginástica Biola | despesa_auto_00119 | 65 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 65 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
ORIGEM: 2026-06-10 | Thayrine | despesa_auto_00120 | 120 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 120 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
ORIGEM: 2026-06-10 | Tratamento Lara | despesa_auto_00121 | 530 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 530 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
ORIGEM: 2026-06-11 | Cemig | despesa_auto_00122 | 95.12 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 95.12 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
ORIGEM: 2026-06-12 | Aluguel | despesa_auto_00123 | 981.95 |  | Lote 8500 mar. | Lote 3120 mai | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 981.95 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
ORIGEM: 2026-06-12 | Escola | despesa_auto_00124 | 2831.4 | Lote 3120 mai + Lote 3000 mai Neon | Lote 8500 mar. | Lote 3120 mai + Lote 3000 mai Neon | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 2831.4 | True | True |  |  |  |  |  | pay_only | ok | n/d
ORIGEM: 2026-06-12 | Pelada | despesa_auto_00125 | 50 | Lote 3000 mai Neon | Lote 8500 mar. | Lote 3000 mai Neon | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 50 | True | True |  |  |  |  |  | pay_only | ok | n/d
ORIGEM: 2026-06-19 | Churrasco pelada | despesa_auto_00127 | 40 | Lote 5680 abr. | Lote 8500 mar. | Lote 5680 abr. | lote | motor_recomendacao | True | 40 | True | False |  |  |  |  |  | pay_only | ok | não determinado
ORIGEM: 2026-06-20 | Cartão Azul | despesa_auto_00128 | 7200 | Lote 5680 abr. + Lote 3120 mai | Lote 8500 mar. | Lote 5680 abr. + Lote 3120 mai | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 7200 | True | True |  |  |  |  |  | pay_only | ok | n/d
ORIGEM: 2026-06-30 | Implante Velt | despesa_auto_00130 | 400 | Lote 5680 abr. | Lote 3000 mar. V | Lote 5680 abr. | lote | motor_recomendacao | True | 400 | True | False |  |  |  |  |  | pay_only | ok | não determinado
ORIGEM: 2026-07-02 | Cartão NU | despesa_auto_00131 | 930 |  | Lote 3000 mar. V | Lote 5680 abr. | lote | motor_recomendacao | True | 243.95 | True | False |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | status_ok_sem_cobertura_corrigido_v17_f0a
ORIGEM: 2026-07-06 | Faxina Rosa | despesa_auto_00132 | 950 | Lote 5680 abr. | Lote 3000 mar. V | Lote 5680 abr. | lote | motor_recomendacao | True | 950 | True | False |  |  |  |  |  | pay_only | ok | não determinado
ORIGEM: 2026-07-12 | Escola | despesa_auto_00137 | 2831.4 |  | Lote 3000 mar. V | Lote 5680 abr. | lote | motor_recomendacao | True | 2831.4 | True | False |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
ORIGEM: 2026-07-12 | Pelada | despesa_auto_00138 | 50 |  | Lote 3000 mar. V | Lote 3120 mai | lote | motor_recomendacao | True | 50 | True | False |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-05-20 | Cartão Azul | despesa_auto_00113 | 5372 | Lote 3120 mai + Lote 3000 mai Neon | Lote 3000 mar. V | Lote 3120 mai + Lote 3000 mai Neon | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 5372 | True | True |  |  |  |  |  | pay_only | ok | n/d
POS: 2026-05-20 | Condomínio | despesa_auto_00114 | 113.31 | Lote 3000 mai Neon | Lote 8500 mar. | Lote 3000 mai Neon | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 113.31 | True | True |  |  |  |  |  | pay_only | ok | n/d
POS: 2026-05-30 | Implante Velt | despesa_auto_00115 | 400 |  | Lote 3000 mar. V | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 400 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-06-02 | Cartão NU | despesa_auto_00116 | 580 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 580 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-06-06 | Faxina Rosa | despesa_auto_00117 | 950 |  | Lote 3000 mar. V | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 950 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-06-07 | Claro | despesa_auto_00118 | 110 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 110 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-06-10 | Ginástica Biola | despesa_auto_00119 | 65 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 65 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-06-10 | Thayrine | despesa_auto_00120 | 120 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 120 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-06-10 | Tratamento Lara | despesa_auto_00121 | 530 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 530 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-06-11 | Cemig | despesa_auto_00122 | 95.12 |  | Lote 8500 mar. | Lote 3120 mai | lote_aportado | pay_only_diario_v1 | True | 95.12 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-06-12 | Aluguel | despesa_auto_00123 | 981.95 |  | Lote 8500 mar. | Lote 3120 mai | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 981.95 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-06-12 | Escola | despesa_auto_00124 | 2831.4 | Lote 3120 mai + Lote 3000 mai Neon | Lote 8500 mar. | Lote 3120 mai + Lote 3000 mai Neon | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 2831.4 | True | True |  |  |  |  |  | pay_only | ok | n/d
POS: 2026-06-12 | Pelada | despesa_auto_00125 | 50 | Lote 3000 mai Neon | Lote 8500 mar. | Lote 3000 mai Neon | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 50 | True | True |  |  |  |  |  | pay_only | ok | n/d
POS: 2026-06-20 | Cartão Azul | despesa_auto_00128 | 7200 | Lote 5680 abr. + Lote 3120 mai | Lote 8500 mar. | Lote 5680 abr. + Lote 3120 mai | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 7200 | True | True |  |  |  |  |  | pay_only | ok | n/d
POS: 2026-06-20 | Condomínio | despesa_auto_00129 | 113.31 |  | Lote 5680 abr. | Lote 3120 mai | combinacao_minima_fontes | pay_only_diario_v1_combinacao_minima | True | 113.31 | True | True |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-07-12 | Pelada | despesa_auto_00138 | 50 |  | Lote 3000 mar. V | Lote 3120 mai | lote | motor_recomendacao | True | 50 | True | False |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-07-15 | Internet | despesa_auto_00139 | 132.4 |  | Lote 3000 mar. V | Lote 3120 mai | lote | motor_recomendacao | True | 132.4 | True | False |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-07-20 | Condomínio | despesa_auto_00141 | 113.31 |  | Lote 3000 mar. V | Lote 3120 mai | lote | motor_recomendacao | True | 113.31 | True | False |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-07-30 | Implante Velt | despesa_auto_00142 | 400 |  | Lote 3000 mar. V | Lote 3120 mai | lote | motor_recomendacao | True | 400 | True | False |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | saldo_temporal_insuficiente_cumulativo
POS: 2026-08-02 | Cartão NU | despesa_auto_00143 | 1500 |  | Lote 3000 mar. V | Lote 3000 mai Neon | lote | motor_recomendacao | True | 517.44 | True | False |  |  |  |  |  | pay_only | sem_saldo_temporal_auditavel | status_ok_sem_cobertura_corrigido_v17_f0a

AUDITORIA_XLSX_V36F_CONCLUIDA
```

## 8. Conclusao

A V3.6F neutraliza observavelmente as origens migradas que ainda apareciam como ativos comuns.

A V3.6D foi preservada.

Os destinos POS foram preservados.

Se ainda houver divergencia patrimonial em abas derivadas do XLSX ou em ledger interno, abrir V3.6G diagnostica antes de qualquer nova correcao.

