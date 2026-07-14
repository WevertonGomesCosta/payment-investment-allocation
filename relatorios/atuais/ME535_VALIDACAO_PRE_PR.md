# ME-535 — validação pré-PR

## Validações executadas neste ambiente

- compilação sintática dos quatro módulos canônicos novos com `python -m py_compile`;
- execução de harness sintético isolado cobrindo os pacotes normativos e a seleção por patrimônio terminal;
- resultado do harness: `synthetic motor tests: OK`;
- revisão do diff contra `main` sem alteração dos arquivos financeiros, cache BCB, console, XLSX ou `Situação Atual`;
- branch criada diretamente do commit `aa501a04ef5e8d76d387c8999f0e5d489a20e62f`.

## Validação ainda obrigatória antes do merge

Este ambiente não dispõe de checkout local do repositório nem de acesso de rede ao GitHub para executar a aplicação completa com os dados reais. Portanto, o PR deve permanecer em draft até a execução, no ambiente operacional do projeto, dos comandos:

```bash
python -m unittest tests.test_motor_temporal_funcional
python aplicacao/principal.py
```

A execução real deve confirmar simultaneamente:

- `ResultadoMotorTemporalConjunto.pronto_para_etapa6=True`;
- `gate_motor_funcional` aprovado;
- ausência de obrigação obrigatória sem cobertura, salvo inviabilidade comprovada;
- Etapas 9, 10 e 11 aprovadas;
- planilha oficial com as cinco abas contratuais;
- nenhuma alteração econômica produzida por renderização;
- matriz econômica por data contendo todos os pacotes permitidos e `argmax_comprovado=True`.

## Decisão pré-PR

A implementação está apta para revisão em PR draft, mas não está autorizada para merge até a validação integral com os dados reais.
