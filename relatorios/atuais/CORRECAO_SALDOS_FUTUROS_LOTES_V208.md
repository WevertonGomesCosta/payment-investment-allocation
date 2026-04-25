# CORREÇÃO SALDOS FUTUROS DE LOTES — V208

Status: IMPLEMENTADO COMO CORREÇÃO CONTROLADA SOBRE A V207

## Escopo

A V208 atualiza os arquivos operacionais enviados pelo usuário e corrige o cálculo dos saldos dos lotes usados em pagamentos futuros.

## Arquivos de dados atualizados

- `dados/dados_financeiros.xlsx`
- `dados/cache_bcb.json`

## Correção funcional

Antes da V208, parte da cadeia de pagamentos futuros ainda usava a fotografia do saldo do lote na data de referência para avaliar pagamentos futuros. Isso podia subestimar ou distorcer:

- saldo antes do pagamento;
- valor bruto disponível;
- valor líquido disponível;
- imposto estimado;
- saldo remanescente após resgate futuro.

Na V208, a valoração dos lotes para pagamentos futuros passa a projetar o lote até a data efetiva de cada pagamento antes de simular o resgate.

## Arquivos alterados

- `nucleo/nucleo_financeiro_minimo.py`
- `nucleo/caixa_recebidos_auditaveis.py`
- `nucleo/reescolha_dinamica_pos_quebra.py`
- `nucleo/recomputacao_sequencial_central_v1.py`
- `nucleo/contexto_baseline.py`
- `nucleo/identidade_baseline.py`
- `scripts/diagnostico/verificar_release_baseline.py`

## Restrições preservadas

- não altera o contrato mestre;
- não altera o modelo matemático-estatístico-financeiro;
- não abre a frente de aportes/recebidos futuros;
- não altera a governança de scripts;
- não altera a camada canônica de saída, apenas alimenta a recomputação com saldos temporalmente corrigidos.

## Validação mínima

- projeção direta de `Lote.valor_bruto_em_data(...)` para data futura;
- avanço temporal de lote em `_ajustar_candidatos_dinamicos(...)`;
- compilação sintática dos módulos alterados;
- release checker atualizado para V208.
