# Consolidação de `_slug_fonte` — V225

## Identificação

- Baseline: V225 Codex-ready enxuta
- Data/hora local: 2026-04-30T14:29:54
- Arquivo alterado: `nucleo/caixa_recebidos_auditaveis.py`
- Fonte única mantida: `nucleo/utilitarios_neutros.py::_slug_fonte`
- Alteração de motor econômico: não
- Alteração de replay: não
- Alteração de pagamentos: não
- Alteração de switching: não
- Alteração de ranking: não
- Alteração de cache: não
- Alteração de `dados/config_atualizado.json`: não

## Objetivo

Remover uma duplicidade simples e estruturalmente equivalente de `_slug_fonte`, mantendo `nucleo.utilitarios_neutros._slug_fonte` como fonte única.

## Equivalência

Equivalência estrutural do corpo da função:

```text
TRUE
```

### Definição removida de `nucleo/caixa_recebidos_auditaveis.py`

```python
def _slug_fonte(chave: str) -> str:
    texto = normalizar_texto(chave).replace(' ', '_')
    return texto or 'fonte'
```

### Definição preservada em `nucleo/utilitarios_neutros.py`

```python
def _slug_fonte(chave: Any) -> str:
    texto = normalizar_texto(chave).replace(' ', '_')
    return texto or 'fonte'
```

## Alteração aplicada

- Removida a definição local de `_slug_fonte` em `nucleo/caixa_recebidos_auditaveis.py`.
- Inserido import:

```python
from nucleo.utilitarios_neutros import _slug_fonte
```

## Contagem textual em `nucleo/caixa_recebidos_auditaveis.py`

| Momento | Ocorrências de `_slug_fonte` |
|---|---:|
| antes | 3 |
| depois | 3 |

## Validação necessária

Executar:

```bash
python aplicacao/principal.py
```

Critério esperado:

- execução sem erro;
- `saidas/oficial/relatorio_operacional_v225.xlsx` gerado;
- sem alteração econômica observável.

## Decisão

A consolidação é considerada de baixo risco porque a auditoria anterior classificou as implementações como equivalentes estruturalmente e a função atua apenas como normalização textual de identificador de fonte.
