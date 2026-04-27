# LEIA-ME operacional — V208

## Baseline vigente da camada documental e de navegação
- Pacote operacional atual: **V208**
- Baseline pós-hotfix imediatamente anterior: **V205**
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
- `GOVERNANCA_FINAL_SCRIPTS_V204.md`
- `HOTFIX_CONSOLE_IMPORTS_V205.md`
- `GOVERNANCA_ESTRUTURAL_V208.md`
- `MAPA_CENTRALIZACAO_HELPERS_V208.csv`

## Regra de leitura desta etapa
1. Interpretar o projeto pela V183 como contrato mestre vigente e pela V182 como modelo oficial vigente.
2. Tratar a V208 como baseline documental/estrutural derivada da V205.
3. Tratar a V205 como baseline pós-hotfix de console.
4. Tratar a V202 como baseline da camada única de saída canônica.
5. Não usar documentos históricos como base normativa principal para novas implementações.
6. Tratar `saidas/oficial/` como caminho canônico de artefatos oficiais ativos, sem relatórios congelados de versões anteriores.
7. Tratar `scripts/historico_raiz/` e `scripts/historico_saida_propria_v203/` como acervos históricos sem autoridade operacional.
8. Exigir que console, `.xlsx`, JSON/CSV e Markdown observáveis dependam de `nucleo.saida_canonica`.

## Camada única de saída

A saída observável oficial é materializada por:

```text
nucleo/saida_canonica.py
```

Console e planilha operacional devem consumir `construir_saida_canonica(...)`, evitando recálculo paralelo de saldo, líquido, imposto, residual, switching e amostras financeiras.

## Centralização estrutural V208

A V208 centraliza em `nucleo/utilitarios_neutros.py` helpers semânticos que estavam duplicados entre módulos:

```text
_rotulo_fonte
_fonte_id
_normalizar_proxy_terminal
_aliquota_ir_estimada
```

Essa centralização é estrutural. Ela não altera regra econômica, motor, contrato, modelo oficial nem recebidos/aportes futuros.

## Próxima frente preservada
Corrigir a modelagem dos recebidos/aportes futuros ainda não aportados em carteira. Essa frente não foi alterada pela V208.

## V216 — frente funcional de aportes futuros

Consulte `INTEGRACAO_FUNCIONAL_APORTES_FUTUROS_V216.md` para a implementação funcional da transição `recebido_futuro → caixa/reserva → aporte_planejado` no motor.
