# ADENDO GOV-01 — Ciclo de vida obrigatório de scripts diagnósticos e artefatos temporários

## 1. Status normativo

Este adendo integra o Contrato Operacional Mestre do projeto `payment-investment-allocation` e deve ser interpretado em conjunto com:

- `relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md`;
- o modelo matemático-estatístico-financeiro oficial;
- os logs de microetapas e relatórios de auditoria compatíveis com ambos.

Em caso de conflito entre scripts diagnósticos, artefatos temporários, documentos históricos e o contrato mestre, prevalece o contrato mestre, complementado por este adendo.

## 2. Princípio geral

Scripts diagnósticos são artefatos transitórios. Eles podem ser usados para investigar, validar ou auditar uma microetapa, mas não constituem contrato operacional permanente.

Após a validação e aplicação da correção no núcleo, todo script diagnóstico deve receber uma decisão explícita de ciclo de vida:

1. removido;
2. arquivado fora da rota viva;
3. substituído por relatório estático;
4. ou promovido formalmente a gate permanente.

Na ausência de promoção explícita, o destino padrão é remoção.

## 3. Evidência oficial

Relatórios, logs de microetapa, saídas estáticas e registros de PR são as evidências oficiais de auditoria.

Scripts temporários não são evidência contratual permanente. Quando a evidência de uma etapa já estiver preservada em relatório, log, saída estática ou PR, o script diagnóstico usado para produzi-la deve ser removido ou arquivado, salvo promoção formal a gate permanente.

## 4. Vedação a compatibilidade artificial no núcleo vivo

É proibido manter compatibilidade no núcleo vivo apenas para preservar scripts diagnósticos históricos.

Quando um script diagnóstico depender de APIs, atributos, módulos, aliases, kwargs, sentinelas ou artefatos removidos do runtime, o script deve ser atualizado, removido ou arquivado. O núcleo vivo não deve ser contaminado novamente para acomodar scripts diagnósticos legados.

Em particular, é vedado reintroduzir em `aplicacao/*` ou `nucleo/*`:

- aliases `*_shadow`;
- kwargs `incluir_*_shadow`;
- stubs de módulos removidos;
- sentinelas específicas de lote, valor, data ou baseline;
- dependências de CSVs diagnósticos como insumo operacional;
- bridges, wrappers ou fallbacks criados apenas para manter scripts históricos executáveis.

## 5. Requisitos mínimos para novos scripts diagnósticos

Todo script criado em `scripts/diagnostico/` deve declarar, preferencialmente no cabeçalho ou no log da microetapa associada:

- objetivo;
- microetapa associada;
- entradas;
- saídas;
- condição de remoção;
- relatório ou evidência que substitui o script após validação;
- indicação explícita se é transitório ou gate permanente.

Scripts sem essa declaração devem ser tratados como transitórios e removíveis após a validação da microetapa.

## 6. Gates permanentes

A permanência de scripts em `scripts/diagnostico/` só é permitida para gates permanentes explicitamente classificados, estáveis e compatíveis com a rota canônica vigente.

Um gate permanente deve:

- ter escopo estável;
- não depender de módulos removidos;
- não depender de APIs `shadow` ou experimentais;
- não exigir sentinelas específicas;
- não usar `saidas/diagnostico/*` como fonte operacional;
- ser executável como validação de PR, release ou higiene estrutural.

A promoção de um script diagnóstico a gate permanente deve ser registrada em log ou PR.

## 7. Proibição de I/O diagnóstico como fonte operacional

Nenhum módulo em `aplicacao/*` ou `nucleo/*` pode depender de `saidas/diagnostico/*` como insumo operacional, salvo promoção contratual explícita do artefato para entrada canônica.

CSV, XLSX, JSON, Markdown ou qualquer outro artefato gerado por diagnóstico é evidência ou relatório, não fonte de decisão, salvo formalização contratual específica.

## 8. Fechamento obrigatório de microetapa

Ao final de cada microetapa que criar, usar ou alterar scripts diagnósticos ou artefatos temporários, deve existir uma seção de fechamento contendo:

- scripts diagnósticos criados;
- scripts diagnósticos removidos;
- scripts preservados como gate permanente;
- scripts arquivados ou substituídos por evidência estática;
- relatórios/evidências preservados;
- confirmação de que nenhum diagnóstico temporário permaneceu como dependência do runtime.

## 9. Motivação histórica

Este adendo decorre das frentes V17-F0 e V17-F0-DIAG1.

A frente V17-F0 removeu resíduos `shadow`, `benchmark`, sentinelas e I/O diagnóstico do núcleo vivo das Etapas 1–4. Em seguida, a DIAG1 removeu 61 scripts diagnósticos legados incompatíveis com a rota limpa, preservando apenas o gate permanente `scripts/diagnostico/auditar_nucleo_vivo_v4z.py`.

Essas frentes demonstraram que diagnósticos transitórios acumulados podem pressionar o projeto a manter compatibilidade artificial com APIs removidas. Este adendo impede que esse padrão volte a ocorrer.
