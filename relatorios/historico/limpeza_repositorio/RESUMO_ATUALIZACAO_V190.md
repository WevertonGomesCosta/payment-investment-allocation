# Atualização V190

## Ajustes aplicados
- atualização de `dados/cache_bcb.json` com o arquivo enviado pelo usuário;
- limpeza da saída do console, removendo blocos históricos/poluídos e promovendo apenas:
  - execução/base;
  - amostras operacionais de pagamentos;
  - ranqueamento oficial da carteira;
  - switchings candidatos/classificados;
  - situação atual;
- normalização do relatório operacional `.xlsx` para manter apenas as abas principais da trilha oficial e incorporar as abas do ranking estabilizado;
- tratamento mais conservador do lote residual baixo na situação atual, passando a zerar operacionalmente também quando `saldo_liquido` ou `saldo_rem` estiverem dentro do limiar.

## Estrutura alvo do `.xlsx`
- Extrato Passado
- Extrato Futuro
- Switching
- Carteira
- Situação Atual
- Ranking_Completo
- Top30
- Destinos_Switch
- Resumo
- Validacao

## Observação de validação
A validação estrutural (`compileall` + release checker) foi concluída com sucesso. A execução completa do app não foi concluída neste ambiente dentro do tempo disponível, então a verificação final da nova forma do console e do `.xlsx` deve ser feita localmente pelo usuário ao rodar `python aplicacao/principal.py`.
