# Baseline fixa V67

## Objetivo desta versão

Derivar a V66 de forma cirúrgica para ajustar apenas a semântica da camada F1 ligada aos recebidos/lotes usados antes da aplicação, substituindo o rótulo `misto` por uma classificação operacional mais explicativa, sem alterar o motor financeiro nem a lógica econômica já implementada.

## Ajustes aplicados

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- remoção da tabela `situação atual de todos os recebidos (inclui exauridos)` do console e da aba `Situação atual`;
- criação da aba separada `Fechamento econômico atual` no `.xlsx`;
- normalização pós-replay de lotes com saldo bruto residual menor ou igual ao limiar operacional, zerando `saldo_bruto` e `principal_remanescente` e marcando o lote como esgotado;
- ajuste do script de auditoria diária para gerar nomes de arquivo coerentes com o lote informado.

## Garantia de compatibilidade

Os comandos canônicos e antigos continuam executáveis na V67. O motor financeiro, a lógica de valuation e a etapa funcional já aberta da F1 continuam preservados; a correção desta versão atua apenas na normalização operacional final de resíduos sub-limiar e na camada de exibição dos artefatos.

## Critério desta baseline

A V67 preserva a baseline funcional da V66 e melhora a auditabilidade semântica da F1 ao substituir o rótulo `misto` por uma classificação explícita para os casos em que o recebido financiou pagamentos antes da aplicação e foi aportado depois.

## Atualização V67

- manutenção da V66 como baseline oficial de partida;
- substituição do status `misto` por `uso_pre_aplicacao_com_aporte_posterior`;
- substituição do destino `misto` por `pagamento_e_aplicacao`;
- preservação integral da lógica econômica já implementada;
- manutenção do release checker como gate obrigatório;
- preservação do motor financeiro, do replay histórico e da F1 fora do fluxo decisório principal.
