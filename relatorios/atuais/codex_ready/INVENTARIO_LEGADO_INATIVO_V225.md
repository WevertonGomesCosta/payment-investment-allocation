# Inventário de legado inativo — V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T13:43:03
- Escopo: enxugamento final do repositório pré-Codex

## Helpers locais renomeados para evitar falso positivo

```text
nenhum helper local precisou ser renomeado
```

## Arquivos legados removidos

```text
nenhum stub encontrado para remoção
```

## Arquivos/diretórios auxiliares removidos

```text
relatorios/atuais/codex_ready/legado_preservado/: removido
relatorios/atuais/codex_ready/scripts_temporarios_removidos/: removido
enxugar_repositorio_pre_codex_v225.py
enxugar_repositorio_pre_codex_v225_v2.py
```

## Avisos de remoção

```text
aplicacao/console/secoes_financeiras.py: já ausente
aplicacao/console/secoes_canonicas.py: já ausente
```

## Estado atual

- entrada oficial: `aplicacao/principal.py`
- console oficial: `aplicacao/console/principal.py`
- planilha oficial: `nucleo/gerar_planilha_operacional.py`
- saída canônica: `nucleo/saida_canonica.py`
- saída observável: `nucleo/saida_observavel.py`
- validação oficial: `aplicacao/principal.py`

## Regra para Codex

Qualquer alteração que afete dados mostrados simultaneamente no console e na planilha deve seguir esta ordem:

```text
1. alterar ou criar contrato em nucleo/saida_observavel.py
2. renderizar no console sem recalcular
3. renderizar na planilha sem recalcular
4. validar python aplicacao/principal.py
```
