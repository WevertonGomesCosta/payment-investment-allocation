# Auditoria pós-push — planilha operacional configurável — V225

## Identificação

- Baseline operacional: V225
- Tipo: auditoria documental pós-push
- Classe: camada observável / planilha operacional
- Escopo: confirmar a conexão do `aplicacao/principal.py` com o wrapper configurável da planilha operacional
- Commit remoto consolidado: `41118b4`
- Commits relacionados:
  - `0cc169c`: criação de `scripts/operacional/gerar_planilha_operacional_configurada.py`
  - `41118b4`: conexão de `aplicacao/principal.py` ao wrapper configurável

## Restrições respeitadas

Esta auditoria confirma apenas a camada observável de saída. Não foram auditadas ou alteradas regras de:

- cálculo financeiro;
- replay passado;
- pagamentos;
- switching;
- ranqueamento da Carteira;
- cache CDI/BCB;
- motor econômico;
- identidade formal da baseline.

## Evidência 1 — `aplicacao/principal.py` chama o wrapper configurável

O arquivo `aplicacao/principal.py` passou a importar:

```python
from scripts.operacional.gerar_planilha_operacional_configurada import main as main_planilha
```

Com isso, o fluxo principal preserva a sequência original:

```python
main_console()
caminho_saida = main_planilha()
print(f"Saída operacional gerada em: {caminho_saida}")
```

Conclusão: o entrypoint principal continua executando console + geração de saída, mas agora a etapa de planilha passa pelo wrapper configurável.

## Evidência 2 — wrapper mantém fallback idêntico aos nomes atuais

O wrapper `scripts/operacional/gerar_planilha_operacional_configurada.py` declara explicitamente o mapa `ABAS_ATUAIS_PLANILHA_OPERACIONAL` com os nomes atuais da planilha:

```python
ABAS_ATUAIS_PLANILHA_OPERACIONAL = {
    'extrato_passado': 'Extrato Passado',
    'extrato_futuro': 'Extrato Futuro',
    'switching': 'Switching',
    'carteira': 'Carteira',
    'top30': 'Top30',
    'resumo_switching': 'Resumo Switching',
    'validacao': 'Validacao',
    'situacao_atual': 'Situação Atual',
    'saida_canonica': 'Saida Canonica',
}
```

A função `_nome_aba_configurado()` só troca o nome da aba se existir valor explícito em `saidas.planilha_operacional.abas`. Caso contrário, retorna o nome atual do mapa acima.

Conclusão: na ausência do novo bloco de config, a saída gerada mantém os nomes atuais das abas.

## Evidência 3 — `dados/config_atualizado.json` não precisa ser alterado obrigatoriamente

O arquivo `dados/config_atualizado.json` ainda contém o bloco legado `saidas`, com chaves como:

- `exportar_excel_final`
- `exportar_config_corrigido`
- `aba_extrato`
- `aba_auditoria_extrato`
- `aba_carteira_final`
- `aba_resumo`
- `aba_situacao_atual`
- `template_arquivo_resultado_estrategia`

O novo wrapper procura especificamente:

```text
saidas.planilha_operacional
```

Como esse bloco é opcional e possui fallback completo, não há necessidade obrigatória de alterar `dados/config_atualizado.json` nesta microetapa.

Conclusão: o config atual permanece válido e compatível.

## Contrato operacional criado pela microetapa

A partir desta auditoria, a camada observável da planilha operacional está preparada para aceitar, no futuro, um bloco opcional no seguinte formato:

```json
{
  "saidas": {
    "planilha_operacional": {
      "arquivo": "relatorio_operacional_{versao_slug}.xlsx",
      "abas": {
        "extrato_passado": "Extrato Passado",
        "extrato_futuro": "Extrato Futuro",
        "switching": "Switching",
        "carteira": "Carteira",
        "top30": "Top30",
        "resumo_switching": "Resumo Switching",
        "validacao": "Validacao",
        "situacao_atual": "Situação Atual",
        "saida_canonica": "Saida Canonica"
      }
    }
  }
}
```

Esse bloco não é obrigatório. Ele deve ser adicionado apenas se houver decisão explícita de parametrizar os nomes de arquivo/abas no config.

## Validação operacional reportada

Após a correção local e o push, foi reportado que:

- `python aplicacao/principal.py` executou sem erro;
- o config carregado continuou sendo `dados/config_atualizado.json`;
- a saída operacional continuou sendo gerada em `saidas/oficial/relatorio_operacional_v225.xlsx`;
- as seções de pagamentos, ranking, switching e situação atual foram impressas normalmente;
- o repositório remoto foi atualizado de `0cc169c` para `41118b4`.

## Conclusão da auditoria

A microetapa está aprovada como alteração observável e compatível:

1. `aplicacao/principal.py` chama `gerar_planilha_operacional_configurada`.
2. O wrapper mantém fallback idêntico aos nomes atuais.
3. `dados/config_atualizado.json` não precisa ser alterado obrigatoriamente.
4. A camada de planilha operacional agora está preparada para configuração futura via `saidas.planilha_operacional.*`.
5. Não houve mudança intencional em cálculo, replay, pagamentos, switching ou ranking.

## Próxima microetapa recomendada

A próxima etapa segura é apenas documental ou de parametrização controlada do config:

- opção A: adicionar explicitamente `saidas.planilha_operacional` ao `dados/config_atualizado.json` com valores iguais aos fallbacks atuais, sem alterar saída;
- opção B: manter o config sem esse bloco e avançar para outra auditoria de hardcoded observável, como cabeçalhos e estilos da planilha.

Recomendação: seguir pela opção A somente se for importante tornar o contrato visível no config; caso contrário, seguir para cabeçalhos/estilos da planilha operacional como nova camada observável.
