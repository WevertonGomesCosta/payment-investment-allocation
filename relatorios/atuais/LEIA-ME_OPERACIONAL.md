# LEIA-ME operacional — V203

## Baseline vigente da camada documental e de navegação
- Pacote operacional atual: **V203**
- Base funcional fixa de origem: **V200**
- Contrato mestre vigente: **CONTRATO_OPERACIONAL_PROJETO.md**
- Modelo oficial vigente: **MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md**
- Baseline contratual/metodológica preservada: **V183/V182**

## Leitura obrigatória inicial

### Núcleo normativo vigente
- `CONTRATO_OPERACIONAL_PROJETO.md`
- `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `ESPECIFICACAO_SAIDA_OFICIAL.md`

### Documentos operacionais recentes
- `AUDITORIA_LIMPEZA_RESIDUAL_V201.md`
- `AUDITORIA_CAMADA_SAIDA_CANONICA_V202.md`
- `GOVERNANCA_SCRIPTS_V203.md`
- `MAPA_GOVERNANCA_SCRIPTS_V203.csv`

## Regra de leitura desta etapa
1. Interpretar o projeto pela V183 como contrato mestre vigente e pela V182 como modelo oficial vigente.
2. Tratar a V203 como baseline de governança de scripts, derivada da V202.
3. Tratar a V202 como baseline da camada única de saída canônica.
4. Não usar documentos históricos como base normativa principal para novas implementações.
5. Tratar `saidas/oficial/` como caminho canônico de artefatos oficiais ativos.
6. Tratar `scripts/historico_raiz/` e `scripts/historico_saida_propria_v203/` como acervos históricos sem autoridade operacional.
7. Exigir que console, `.xlsx`, JSON/CSV e Markdown observáveis dependam de `nucleo.saida_canonica`.

## Camada única de saída

A saída observável oficial é materializada por:

```text
nucleo/saida_canonica.py
```

Console e planilha operacional devem consumir `construir_saida_canonica(...)`, evitando recálculo paralelo de saldo, líquido, imposto, residual, switching e amostras financeiras.

## Próxima frente preservada
Corrigir a modelagem dos recebidos/aportes futuros ainda não aportados em carteira. Essa frente não foi alterada pela V203.


## Governança V204

A V204 aplica limpeza final de governança sem alteração econômica: código morto do console foi removido,
scripts históricos `.py` foram bloqueados, auditorias auxiliares foram separadas de saídas oficiais e
helpers utilitários de baixo risco foram centralizados em `nucleo/utilitarios_neutros.py`.

A camada oficial de saída permanece `nucleo.saida_canonica`.


## V205 — hotfix de console

Correção restrita de importação em `aplicacao/console/principal.py`, restaurando dependências necessárias à auditoria detalhada de resíduos. Sem alteração econômica.
