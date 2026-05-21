# ME-V17-F0-V4T0 — Adendo contratual de fechamento de etapas e resíduos

## Identificação

- MICROETAPA: ME-V17-F0-V4T0
- TIPO: DOCUMENTAL / GOVERNANÇA CONTRATUAL / SEM ALTERAÇÃO DE CÓDIGO
- BASELINE: main após V4S
- ALTERA_CODIGO: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não
- ALTERA_SAIDAS: não

## Objetivo

Registrar regra normativa para impedir que etapas futuras sejam promovidas como fechadas quando ainda dependem de resíduos incompatíveis com a arquitetura recém-definida.

## Artefato criado

- `relatorios/principais/ADENDO_CONTRATO_FECHAMENTO_ETAPAS_RESIDUOS.md`

## Decisão registrada

Uma etapa não pode ser promovida como fechada se qualquer saída, pacote, motor ou adaptador ainda depender de caminho legado incompatível com a arquitetura recém-definida.

## Resíduos permitidos ao fechamento

- logs históricos;
- diagnósticos arquivados fora do namespace ativo;
- compatibilidade explicitamente contratada;
- caminhos opcionais desligados por padrão e sem impacto no runtime.

## Resíduos proibidos ao fechamento

- funções runtime duplicando responsabilidade do contrato novo;
- fallback ativo não formalizado;
- recomposição paralela de estado;
- saída reconstruindo dados que deveriam vir de pacote canônico;
- scripts históricos misturados com diagnósticos ativos;
- etapa seguinte dependendo de comportamento residual da etapa anterior.

## Consequência operacional

Uma etapa pode ser considerada funcionalmente executável sem estar arquiteturalmente saneada.

Nessa situação, a etapa deve ser classificada como:

```text
ETAPA_FUNCIONA=True
ETAPA_SANEADA=False
ETAPA_APTA_COMO_ENTRADA_DA_PROXIMA=False
```

A próxima etapa não deve ser aberta até o saneamento, migração, remoção ou formalização dos resíduos proibidos.

## Aplicação imediata à Etapa 4

A Etapa 4 deve continuar em fechamento arquitetural obrigatório até que V4T/V4U/V4V/V4W/V4X eliminem ou formalizem os resíduos incompatíveis com a arquitetura temporal.

A Etapa 5 permanece fechada até validação explícita da saída saneada da Etapa 4 como entrada contratual da Etapa 5.

## Observação

Este adendo deve ser incorporado ao corpo do `CONTRATO_OPERACIONAL_PROJETO.md` em consolidação documental posterior, preferencialmente na seção `7-E. Arquitetura macro obrigatória do pipeline operacional`.
