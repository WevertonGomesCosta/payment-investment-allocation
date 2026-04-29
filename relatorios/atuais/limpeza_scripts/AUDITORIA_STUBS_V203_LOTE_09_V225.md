# Auditoria de limpeza de stubs V203 — lote 09 — V225

## Identificação

- Baseline: V225
- Escopo: stubs V203 proxy/híbrido shadow na raiz de `scripts/diagnostico/`
- Resultado: lote concluído

## Arquivos auditados e removidos

```text
scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py
scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py
scripts/diagnostico/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py
```

## Critério aplicado

Os três arquivos foram selecionados porque:

1. eram stubs V203 sem lógica operacional própria no caminho atual;
2. indicavam preservação do conteúdo original em `scripts/historico_saida_propria_v203/diagnostico_original/`;
3. a busca por referências localizou apenas registros documentais/históricos;
4. não havia dependência ativa na rota `aplicacao/principal.py`.

## Evidência pós-limpeza

A consulta direta aos três caminhos no `main` retornou ausência dos arquivos (`404`).

## Commits da microetapa

```text
674ebafb8e28a930e57eaa08fe2f62c5acb0365f
3bfa025db6db4c83b647a0837b2ae7e9b20949fd
1430925dad094642d8a2c861f54fcc61efd9048d
```

## Restrições respeitadas

Não houve alteração em:

- código funcional;
- config;
- cálculo;
- replay;
- pagamentos;
- switching;
- ranking;
- identidade da baseline.

## Validação local necessária

Executar:

```bash
cd ~/OneDrive/GitHub/payment-investment-allocation
git pull
python aplicacao/principal.py
```

Critérios esperados:

- execução sem erro;
- saída em `saidas/oficial/relatorio_operacional_v225.xlsx`;
- sem alteração econômica observável.

## Próxima etapa sugerida

Após validação local, atualizar o inventário pós-lotes 06–09 ou auditar outro lote pequeno de stubs V203 ainda físicos na raiz de `scripts/diagnostico/`.
