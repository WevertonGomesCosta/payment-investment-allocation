# HOTFIX_CONSOLE_IMPORTS_V205

Status: APLICADO

Base fixa: V204  
Nova versão: V205

## Motivo

Ao executar:

```bash
python aplicacao/principal.py
```

a V204 falhava com:

```text
NameError: name 'construir_tabela_iof' is not defined
```

## Causa

Durante a limpeza final de governança da V204, o console teve código morto removido e imports foram reduzidos. Porém, a função ativa:

```text
_preparar_auditoria_detalhada_residuos(...)
```

continua usando:

```text
construir_tabela_iof(...)
construir_faixas_ir(...)
```

Essas funções não estavam mais importadas em:

```text
aplicacao/console/principal.py
```

## Correção aplicada

Foi restaurado somente o import explícito:

```python
from nucleo.nucleo_financeiro_minimo import construir_faixas_ir, construir_tabela_iof
```

## Escopo preservado

Não foi alterado:

- motor principal;
- contrato mestre;
- modelo matemático-estatístico-financeiro;
- regra de pagamentos;
- regra de switching;
- regra de recebidos/aportes futuros;
- camada canônica de saída.

## Validação

- análise estática da função: sem nomes globais indefinidos;
- sintaxe Python dos arquivos `.py`: OK;
- release checker: OK — V205.

## Classificação

```text
HOTFIX_SEM_ALTERACAO_ECONOMICA
```
