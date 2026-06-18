# ME-532 — auditoria de prontidão para retomada do modelo matemático e decisão econômica

## 1. Identificação formal

- **Frente:** ME-532.
- **Título:** auditoria de prontidão para retomada do modelo matemático e decisão econômica.
- **Repositório:** `WevertonGomesCosta/payment-investment-allocation`.
- **Base observada:** `2626650` (`Merge pull request #546 ... ME-531E`).
- **Branch do PR:** `codex/abrir-me-532-a-partir-da-main-atualizada`.
- **Número real do PR da ME-532:** #547.
- **Natureza da frente:** auditoria estática e operacional declarativa, sem alteração de modelo matemático, pagamentos, switching, ranking, gates, dados financeiros, cache BCB ou decisão econômica.

## 2. Conclusão executiva

**Recomendação objetiva: pronto com ressalva operacional não impeditiva.**

O pipeline está pronto para iniciar uma próxima frente de modelagem matemática/decisão econômica desde que essa nova frente preserve os contratos congelados de saída observável, paridade e governança pós-renderização. A ressalva é que a execução local usou planilha financeira por `fallback_local` e CDI por `cache_local` devido a bloqueio de rede para download da planilha; isso não altera o diagnóstico de separação decisória/renderização, mas deve ser registrado antes de qualquer validação econômica futura que dependa de dados remotos atualizados.

A sequência ME-531C/D/E fica considerada encerrada para fins desta auditoria: a saída oficial está normalizada, as métricas oficiais preservadas continuam presentes, métricas auxiliares removidas continuam ausentes, a aba temporária `Auditoria Replay` não existe na saída XLSX oficial e as Etapas 9, 10 e 11 seguem aprovadas na execução operacional.

## 3. Escopo negativo preservado

Esta ME não alterou e não autoriza alteração em:

- cálculo econômico;
- `Rend. líq.`;
- `Rend. líq. motor`;
- `Dif. teórica`;
- pagamentos ou datas de pagamento;
- lotes usados;
- switching;
- ranking;
- gates;
- decisão econômica;
- dados financeiros;
- cache BCB;
- contrato de abas XLSX;
- métricas auxiliares;
- estrutura `Auditoria Replay`;
- remoção automática de rotas, funções, resíduos ou artefatos.

## 4. Artefatos formais atuais do pipeline

| Camada | Artefato formal atual | Módulo/função observada | Natureza | Observação de prontidão |
|---|---|---|---|---|
| Entrada bruta | `dados/config_atualizado.json`, `dados/dados_financeiros.xlsx`, `dados/cache_bcb.json` como insumos físicos carregados pela aplicação | `aplicacao/principal.py` via contexto operacional | Insumo operacional bruto, não saída decisória | Não deve entrar no PR da ME-532. Na execução, planilha e cache foram consumidos localmente, não alterados por esta frente. |
| Contexto operacional | `ContextoOperacionalCanonico` | `carregar_contexto_operacional_canonico(...)` | Artefato estruturante pré-decisório | Organiza dados canônicos para formar estado temporal inicial. |
| Estado temporal inicial | `EstadoTemporalInicial` | `construir_estado_temporal_inicial(...)` | Artefato decisório preparatório | Não decide a trajetória final; fornece estado para o motor temporal conjunto. |
| Motor temporal conjunto | `ResultadoMotorTemporalConjunto` | `construir_resultado_motor_temporal_conjunto(...)` | **Decisório** | Ponto central atual de decisão temporal conjunta. Próxima modelagem pode atuar aqui, em frente própria. |
| Ledger canônico | `LedgerTemporalCanonico` | `construir_ledger_temporal_canonico(...)` | Materialização canônica de decisão já tomada | Não reotimiza; contabiliza a trajetória do motor. |
| Gates de validação | `ResultadoGatesValidacaoNucleo` | `validar_gates_nucleo(...)` | Validação decisória/contratual de núcleo | Bloqueia progressão observável se reprovado; é ponto possível de endurecimento futuro, sem renderização como fonte. |
| Saída canônica | `SaidaCanonicaOficial` | `construir_saida_canonica_oficial(...)` | Saída canônica pós-gates | Preserva decisões, eventos, bloqueios e avisos; não renderiza console/XLSX. |
| Pacote observável oficial | `PacoteSaidaObservavelOficial` | `construir_pacote_saida_observavel_oficial(...)` | **Observável oficial**, não decisório | Fonte oficial para console, XLSX e Etapa 10; não reotimiza nem revalora. |
| Console | renderização de `PacoteSaidaObservavelOficial` | `render_console(...)` | Observável | Não é fonte de verdade decisória nem entrada do cálculo. |
| XLSX | abas oficiais derivadas de `PacoteSaidaObservavelOficial` | `gerar_planilha_operacional(...)` | Observável/exportação | Não é fonte de verdade decisória nem entrada do cálculo. |
| Etapa 10 | `ResultadoParidadeRenderizacaoOficial` | `validar_paridade_renderizacao_oficial(...)` | Auditoria observável de paridade | Recebe `PacoteSaidaObservavelOficial`; audita console/XLSX como alvos renderizados. |
| Etapa 11 | `ResultadoGovernancaResiduosPipeline` na implementação atual | `construir_resultado_governanca_residuos_pipeline(...)` | Governança pós-paridade, não decisória | Recebe `ResultadoParidadeRenderizacaoOficial`; classifica/preserva sem remoção automática. |

## 5. Artefatos decisórios versus observáveis

### Decisórios ou pré-decisórios

- `ContextoOperacionalCanonico`: estrutura a leitura canônica dos dados operacionais.
- `EstadoTemporalInicial`: prepara estado temporal para decisão.
- `ResultadoMotorTemporalConjunto`: concentra decisão temporal conjunta, seleção/uso/reserva de fontes e trajetória operacional.
- `LedgerTemporalCanonico`: materializa contabilmente a decisão já fechada, sem recalcular decisão.
- `ResultadoGatesValidacaoNucleo`: valida o núcleo antes da saída canônica e pode bloquear progressão.
- `SaidaCanonicaOficial`: artefato canônico pós-gates, preservando a decisão aprovada.

### Observáveis, auditoriais ou pós-decisórios

- `PacoteSaidaObservavelOficial`.
- Console oficial.
- XLSX oficial.
- `ResultadoParidadeRenderizacaoOficial`.
- `ResultadoGovernancaResiduosPipeline` / governança da Etapa 11.
- Manifests e saídas operacionais geradas em `saidas/oficial/`.
- Logs, relatórios e scripts diagnósticos.

## 6. Confirmações contratuais centrais

1. **Console e XLSX não são fonte de verdade decisória.** Eles são renderizações/artefatos observáveis derivados do pacote oficial.
2. **A Etapa 10 recebe `PacoteSaidaObservavelOficial`.** Essa é a entrada formal declarada no contrato e na implementação de paridade.
3. **A Etapa 11 recebe exclusivamente `ResultadoParidadeRenderizacaoOficial` como entrada formal de estado.** Evidências auxiliares de inventário podem existir apenas como material não decisório para classificação, sem substituir a entrada formal.
4. **Renderização não altera decisão.** A Etapa 9 apenas prepara blocos de console/XLSX e relatório observável preservando decisões anteriores.
5. **Diagnóstico e governança não alteram decisão econômica.** A Etapa 11 classifica, preserva e recomenda sem remoção automática e sem reabrir motor, ledger, gates, Etapa 9 ou Etapa 10.

## 7. Auditoria de dependências indevidas

| Relação auditada | Resultado | Justificativa |
|---|---|---|
| Renderização -> decisão | Sem dependência indevida encontrada | O fluxo constrói motor, ledger, gates e saída canônica antes de console/XLSX; renderização consome pacote observável posterior. |
| Console -> cálculo | Sem dependência indevida encontrada | Console é chamado depois da construção do pacote observável e não alimenta motor, ledger ou gates. |
| XLSX -> cálculo | Sem dependência indevida encontrada | XLSX é gerado depois da saída observável; a Etapa 10 lê XLSX apenas como alvo de auditoria de paridade. |
| Diagnóstico/governança -> decisão econômica | Sem dependência indevida encontrada | Etapa 11 opera após paridade, registra preservação e não autoriza remoção automática nem reotimização. |

## 8. Pontos seguros de entrada para próxima frente de modelo matemático

A próxima ME de modelagem pode propor mudanças somente em frente própria, com contrato explícito e bateria de validação antes/depois. Pontos candidatos:

1. **Função do motor temporal conjunto:** alterar heurística/otimização em `construir_resultado_motor_temporal_conjunto(...)`, preservando saída formal `ResultadoMotorTemporalConjunto` ou versionando-a explicitamente.
2. **Score/ranking:** revisar fórmula de ranking e score desde que não use console/XLSX como fonte e preserve rastreabilidade de carteira.
3. **Seleção de fontes para pagamento:** revisar critérios de escolha de lotes/fontes dentro do motor, com comparação determinística de efeitos em ledger.
4. **Decisão `pay_only` versus `switch_then_pay`:** reabrir apenas em frente decisória específica, com novos gates de consistência.
5. **Regras de liquidez:** ajustar elegibilidade temporal/liquidez no motor ou nos dados canônicos, sem remendar renderização.
6. **Carência:** revisar restrições de carência na camada de decisão/gates, não no XLSX.
7. **Imposto:** revisar cálculo fiscal em camada de núcleo, garantindo preservação ou versionamento das métricas oficiais.
8. **Patrimônio terminal:** revisar objetivo econômico no motor/score, não em Etapa 9/10/11.
9. **Gates de validação:** endurecer/expandir gates, desde que a saída canônica e observável permaneçam derivadas do núcleo validado.

## 9. Invariantes congelados para a próxima fase

- Contrato de abas XLSX: exatamente `Extrato Passado`, `Extrato Futuro`, `Switching`, `Carteira`, `Situação Atual`.
- Métricas oficiais preservadas: `Rend. líq.`, `Rend. líq. motor`, `Dif. teórica`.
- Métricas auxiliares removidas: `Rend. aux. calibrado`, `Dif. aux. calibrada`.
- Ausência de aba/estrutura `Auditoria Replay` na saída oficial.
- Identidade dos artefatos: `ResultadoMotorTemporalConjunto`, `LedgerTemporalCanonico`, `ResultadoGatesValidacaoNucleo`, `SaidaCanonicaOficial`, `PacoteSaidaObservavelOficial`, `ResultadoParidadeRenderizacaoOficial` e artefato de governança da Etapa 11.
- Paridade console/XLSX auditada pela Etapa 10.
- Governança da Etapa 11 sem remoção automática e com entrada formal `ResultadoParidadeRenderizacaoOficial`.
- Console e XLSX como consumidores/observáveis, nunca como fonte de cálculo ou decisão.
- Dados financeiros, cache BCB e saídas operacionais `.xlsx` fora do PR desta auditoria.

## 10. Validação operacional executada

Comando executado:

```bash
python3 aplicacao/principal.py
```

Resultado observado em 2026-06-18:

- Etapa 9: `status=preparado`, `ok=True`.
- Etapa 10: `status=aprovado`, `ok=True`.
- Etapa 11: `status=aprovado`, `ok=True`.
- XLSX gerado localmente em `saidas/oficial/relatorio_operacional_pr546_me531e_2626650bf7d9_20260618T222152Z.xlsx`.
- Abas XLSX observadas: `Extrato Passado`, `Extrato Futuro`, `Switching`, `Carteira`, `Situação Atual`.
- `Auditoria Replay` ausente das abas e ausente do console capturado.
- Métricas `Rend. líq.`, `Rend. líq. motor` e `Dif. teórica` presentes no console.
- Métricas `Rend. aux. calibrado` e `Dif. aux. calibrada` ausentes no console.
- Manifest operacional gerado apenas em área de saída ignorada/versionamento operacional local, não como artefato a entrar no PR.

## 11. Riscos para a próxima fase

| Risco | Severidade | Mitigação recomendada |
|---|---:|---|
| Reabrir modelo usando console/XLSX como fonte de dados | Alta | Proibir no contrato da próxima ME; exigir entrada no núcleo decisório. |
| Alterar nomes de métricas oficiais durante modelagem | Alta | Congelar cabeçalhos e versionar qualquer nova métrica fora do contrato oficial. |
| Reintroduzir métrica auxiliar ou `Auditoria Replay` em saída oficial | Alta | Validar ausência em console/XLSX em toda execução de regressão. |
| Mudar motor sem atualizar gates | Média/Alta | Criar gates de comparação e invariantes econômicos antes/depois. |
| Usar diagnósticos da Etapa 11 como autorização de remoção | Média | Manter remoção automática proibida; abrir frente própria para qualquer limpeza. |
| Validação econômica com dados remotos indisponíveis | Média | Registrar origem dos dados e exigir execução com insumos esperados quando a frente for econômica. |

## 12. Parecer final

A ME-532 aprova a prontidão arquitetural do pipeline para a próxima fase de modelo matemático/decisão econômica **com ressalva operacional não impeditiva de origem local dos dados na execução auditada**.

A próxima ME pode iniciar desenho/implementação de modelagem desde que:

1. atue antes ou dentro das camadas decisórias adequadas, principalmente motor temporal conjunto, ranking, seleção de fontes e gates;
2. não use console, XLSX, Etapa 10 ou Etapa 11 como fonte de verdade econômica;
3. preserve os invariantes de saída oficial congelados pela ME-531C/D/E;
4. declare explicitamente qualquer alteração econômica pretendida em contrato próprio;
5. execute regressões que comprovem Etapas 9/10/11 aprovadas após a mudança.

## 13. Confirmação de ausência de alteração econômica nesta ME

Esta frente alterou apenas documentação técnica de auditoria. Não houve alteração de código executável, cálculo, dados financeiros, cache BCB, pagamentos, datas, lotes, switching, ranking, gates ou decisão econômica.
