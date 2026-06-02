# ETAPA11-COMPLETA-01 — Implementa Limpeza e Depreciação Controlada

## Objetivo

Consolidar a implementação funcional da Etapa 11 por meio do artefato formal
`ResultadoLimpezaDepreciacaoControlada` e da função pública
`construir_resultado_limpeza_depreciacao_controlada(...)`, consumindo
exclusivamente `ResultadoParidadeRenderizacaoOficial` como entrada formal de
estado.

## Escopo material

- Implementado `nucleo/limpeza_depreciacao_controlada.py`.
- Integrada renderização resumida e observável da Etapa 11 em
  `aplicacao/principal.py` após a Etapa 10.
- Preservada a natureza auxiliar e não decisória do inventário estático.

## Comentários P2 resolvidos

1. **Dependência ativa com classificação excessivamente ampla**
   - A classificação `bloqueado_dependencia_ativa` agora diferencia bloqueios
     positivos de textos negativos como `não bloqueado`, `desbloqueado` e
     `sem bloqueio`.
   - Evidências como `sem uso` e `deprecated` não são convertidas em bloqueio
     por dependência ativa.

2. **Legado/deprecated sem bloqueio indevido**
   - Evidências auxiliares com `legacy`, `legado`, `deprecated` ou termos de
     depreciação passam a ser classificadas como
     `legado_candidato_depreciacao`, salvo evidência positiva de dependência
     ativa.

3. **Ausência de inventário auxiliar**
   - `None`, `{}` e `[]` geram item explícito
     `inventario_auxiliar_ausente`, marcam
     `classificacao_limitada_por_ausencia_inventario=True` e consolidam status
     `aprovado_com_ressalva` quando a paridade da Etapa 10 não está bloqueada
     ou reprovada.

4. **Remoção automática**
   - Todos os itens e resumos preservam
     `remocao_automatica_autorizada=False`, mantendo remoções reais fora da
     Etapa 11 e dependentes de frente posterior específica.

## Fronteiras preservadas

A implementação não altera motor, ledger, gates, Etapa 9, Etapa 10, contrato
mestre, modelo oficial, dados financeiros, cache BCB, console/XLSX econômico ou
lógica econômica.

## Evidências auxiliares validadas

Foram validados cenários materiais de classificação auxiliar:

- `{"rota_api": "dependencia ativa"}` → `bloqueado_dependencia_ativa`,
  `aprovado_com_ressalva`, remoção automática desautorizada.
- `{"rota_legacy": "deprecated"}` → `legado_candidato_depreciacao` sem
  bloqueio por dependência ativa.
- `{"rota_sem_uso": "sem uso"}` → não bloqueia por dependência ativa.
- `{"status": "não bloqueado", "tipo": "legado"}` → não bloqueia por
  dependência ativa e classifica legado.
- `{"status": "desbloqueado", "tipo": "legado"}` → não bloqueia por
  dependência ativa e classifica legado.
- `{"status": "bloqueado", "tipo": "legado"}` →
  `bloqueado_dependencia_ativa`, `aprovado_com_ressalva`, remoção automática
  desautorizada.
- `{}`, `[]`, `None` → `inventario_auxiliar_ausente`, classificação limitada e
  `aprovado_com_ressalva`.
