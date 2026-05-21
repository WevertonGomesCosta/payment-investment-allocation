# Adendo normativo ao Contrato Operacional — Fechamento de etapas e resíduos

## Identificação

- DOCUMENTO: ADENDO_CONTRATO_FECHAMENTO_ETAPAS_RESIDUOS
- VINCULAÇÃO: Contrato Operacional Mestre do projeto `payment-investment-allocation`
- ARQUIVO MESTRE RELACIONADO: `relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md`
- NATUREZA: ADENDO NORMATIVO / GOVERNANÇA DE FECHAMENTO DE ETAPAS
- ESCOPO: todas as etapas sequenciais do projeto

## Finalidade

Este adendo registra regra normativa obrigatória para fechamento de etapas, promoção de baselines e abertura de etapas subsequentes.

A regra decorre da necessidade de impedir que uma etapa seja declarada fechada apenas por executar funcionalmente, quando ainda depende de resíduos incompatíveis com a arquitetura recém-definida.

## Regra normativa de fechamento de etapa

Uma etapa não pode ser promovida como fechada se qualquer saída, pacote, motor ou adaptador ainda depender de caminho legado incompatível com a arquitetura recém-definida.

Para fins deste contrato, uma etapa só pode ser considerada fechada quando cumprir simultaneamente:

1. funcionamento operacional validado;
2. ausência de dependência runtime de resíduos incompatíveis com o contrato da etapa;
3. saída contratual limpa, auditável e adequada como entrada da etapa seguinte;
4. resíduos remanescentes classificados como permitidos ao fechamento, conforme este adendo.

Funcionamento isolado não equivale a fechamento arquitetural.

## Resíduos permitidos ao fechamento

São permitidos ao fechamento de uma etapa, desde que explicitamente identificados e sem impacto indevido no runtime:

- logs históricos;
- diagnósticos arquivados fora do namespace ativo;
- compatibilidade explicitamente contratada;
- caminhos opcionais desligados por padrão e sem impacto no runtime.

Esses resíduos não podem assumir função decisória, corretiva ou substitutiva de pacote, motor, saída ou contrato vigente.

## Resíduos proibidos ao fechamento

São proibidos ao fechamento de uma etapa:

- funções runtime duplicando responsabilidade do contrato novo;
- fallback ativo não formalizado;
- recomposição paralela de estado;
- saída reconstruindo dados que deveriam vir de pacote canônico;
- scripts históricos misturados com diagnósticos ativos;
- etapa seguinte dependendo de comportamento residual da etapa anterior.

A presença de qualquer desses resíduos impede a promoção plena da etapa como fechada.

## Consequência operacional

Quando resíduo proibido for identificado, a etapa pode ser classificada, no máximo, como:

```text
ETAPA_FUNCIONA=True
ETAPA_SANEADA=False
ETAPA_APTA_COMO_ENTRADA_DA_PROXIMA=False
```

A etapa subsequente não deve ser aberta enquanto o resíduo proibido não for:

1. removido;
2. migrado para contrato explícito;
3. substituído por pacote canônico;
4. ou formalmente reclassificado como compatibilidade permitida, sem impacto no runtime padrão.

## Implicação para a Etapa 4

No contexto da frente V17-F0, a Etapa 4 não deve ser tratada como plenamente fechada enquanto a saída observável, pacotes, adaptadores ou diagnósticos ativos ainda dependerem de resíduos incompatíveis com a arquitetura temporal recém-definida.

As microetapas V4T, V4U, V4V, V4W e V4X devem ser entendidas como fechamento arquitetural obrigatório da Etapa 4, não como abertura da Etapa 5.

## Regra para etapas futuras

Para etapas futuras, toda microetapa de fechamento deve produzir declaração explícita:

```text
etapa_funciona=<True/False>
etapa_saneada=<True/False>
saida_apta_para_etapa_seguinte=<True/False>
residuos_permitidos_ao_fechamento=<lista>
residuos_proibidos_ao_fechamento=<lista>
etapa_pode_ser_promovida=<True/False>
```

A promoção só é permitida quando:

```text
etapa_funciona=True
etapa_saneada=True
saida_apta_para_etapa_seguinte=True
residuos_proibidos_ao_fechamento=[]
etapa_pode_ser_promovida=True
```

## Incorporação futura ao contrato mestre

Este adendo deve ser incorporado ao corpo do `CONTRATO_OPERACIONAL_PROJETO.md` na próxima consolidação documental controlada, preferencialmente como cláusula da seção `7-E. Arquitetura macro obrigatória do pipeline operacional`.
