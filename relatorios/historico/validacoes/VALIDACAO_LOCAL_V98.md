# Validação local V98

## Comandos executados

- `python aplicacao/console/principal.py`
- `python scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`

## Resultado

- baseline V98 compilando e executando;
- console exibindo a seção `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra dos últimos 5 pagamentos realizados e dos próximos 5 pagamentos visível sem alterar a lógica operacional;
- release checker aprovado em estado limpo.

- amostra curta de pagamentos futuros sem coluna de lotes informados;
- leitura técnica curta sem referência à janela de excesso;
