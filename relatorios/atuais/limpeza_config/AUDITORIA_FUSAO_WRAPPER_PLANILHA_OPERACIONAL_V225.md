# Auditoria da fusão progressiva do wrapper da planilha operacional — V225

## Identificação

- Baseline operacional: V225
- Tipo: microetapa estrutural/organizacional
- Classe: camada observável / planilha operacional
- Escopo:
  - `scripts/operacional/gerar_planilha_operacional.py`
  - `scripts/operacional/gerar_planilha_operacional_configurada.py`
  - `aplicacao/principal.py`

## Objetivo

Fundir progressivamente o wrapper `gerar_planilha_operacional_configurada.py` dentro do gerador base `gerar_planilha_operacional.py`, sem alterar a saída observável e sem remover ainda o wrapper.

## Estado anterior

A cadeia de execução era:

```text
aplicacao/principal.py
→ scripts/operacional/gerar_planilha_operacional_configurada.py
→ scripts/operacional/gerar_planilha_operacional.py
```

O wrapper lia `dados/config_atualizado.json` para resolver:

- nome final do arquivo;
- nomes configuráveis das abas;
- cópia para artifact.

O gerador base era responsável por:

- carregar o contexto;
- construir a saída canônica;
- montar o workbook;
- criar abas;
- aplicar estilos;
- salvar o arquivo.

## Alterações aplicadas

### 1. `gerar_planilha_operacional.py`

O gerador base passou a concentrar também a lógica antes mantida no wrapper:

- leitura de `saidas.planilha_operacional` a partir de `contexto.pacote_config.conteudo`;
- resolução do nome do arquivo por `arquivo` ou `nome_arquivo`;
- suporte a `{versao}` e `{versao_slug}` no nome do arquivo;
- resolução configurável de nomes de abas;
- fallback local idêntico aos nomes atuais;
- salvamento no caminho final calculado por `caminho_saida_operacional(...)`;
- cópia para artifact calculada por `caminho_artifact(...)`.

### 2. `aplicacao/principal.py`

O entrypoint voltou a chamar diretamente o gerador base:

```python
from scripts.operacional.gerar_planilha_operacional import main as main_planilha
```

Com isso, a rota principal fica:

```text
aplicacao/principal.py
→ scripts/operacional/gerar_planilha_operacional.py
```

### 3. `gerar_planilha_operacional_configurada.py`

O wrapper foi preservado temporariamente como compatibilidade para chamadas antigas, mas agora apenas delega ao gerador base:

```python
from scripts.operacional.gerar_planilha_operacional import main as gerar_planilha_operacional


def main():
    return gerar_planilha_operacional()
```

## Restrições respeitadas

Esta microetapa não alterou:

- cálculo;
- replay;
- pagamentos;
- switching;
- ranking;
- estilos visuais;
- cabeçalhos;
- estrutura lógica das abas;
- identidade da baseline.

## Estado após a fusão

A partir desta microetapa:

1. `gerar_planilha_operacional.py` é novamente o gerador operacional completo da planilha.
2. `gerar_planilha_operacional_configurada.py` deixa de ter lógica própria e vira compatibilidade temporária.
3. A duplicidade entre wrapper e gerador base foi reduzida.
4. A remoção definitiva do wrapper ainda não deve ocorrer antes de validação local e busca por referências.

## Validação local necessária

Executar no ambiente local:

```bash
cd ~/OneDrive/GitHub/payment-investment-allocation
git pull
python aplicacao/principal.py
python scripts/operacional/gerar_planilha_operacional_configurada.py
```

Critérios de aceite:

1. ambos os comandos executam sem erro;
2. a saída operacional permanece em `saidas/oficial/relatorio_operacional_v225.xlsx`;
3. abas e cabeçalhos permanecem iguais;
4. aba `Situação Atual` permanece visualmente igual;
5. console não apresenta alteração econômica observável.

## Próxima decisão

Se a validação local for aprovada, abrir uma microetapa separada para auditar referências restantes a:

```text
gerar_planilha_operacional_configurada
```

Se não houver dependência externa relevante, o wrapper poderá ser removido em etapa posterior.
