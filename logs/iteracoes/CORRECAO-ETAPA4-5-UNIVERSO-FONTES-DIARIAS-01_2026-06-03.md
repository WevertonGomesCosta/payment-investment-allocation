# CORRECAO-ETAPA4-5-UNIVERSO-FONTES-DIARIAS-01

## Objetivo
Corrigir a materialização e o consumo do universo diário de fontes disponíveis para a Etapa 5, sem alterar dados, console, exportador, contrato mestre, modelo oficial, ranking/carteira ou Etapas 6-11.

## Diagnóstico
- A construção de `recebidos_temporais` priorizava `recebidos_auditaveis` e, quando esse quadro existia, não complementava a linha temporal com salários canônicos futuros da aba **Salários**.
- O motor indexava recebidos apenas no dia exato de recebimento; depois da data, o recebido não continuava aparecendo no universo diário como fonte residual temporalmente elegível.
- As fontes derivadas de `fontes_elegiveis_pagamento` perdiam a data operacional do pagamento/evento e eram materializadas com `data_disponibilidade` igual à data de referência, achatando snapshots diários futuros no mesmo dia.

## Correção aplicada
- Salários canônicos com `data_recebimento >= data_referencia` passam a complementar `recebidos_temporais` com `data_disponibilidade` própria e origem oficial `salarios_canonicos`.
- Recebidos passam a compor o estado diário da Etapa 5 a partir da própria data de disponibilidade e permanecem elegíveis depois dela, salvo se `aplicado` ou `vinculado`.
- Fontes elegíveis de lotes preservam `data_pagamento`/`data_evento` como `data_disponibilidade`, além de metadados oficiais de elegibilidade, carência, pagamento e valores bruto/líquido disponíveis.

## Regras resultantes
### Salários / recebidos
- Antes da `data_recebimento`, o salário/recebido não entra no universo diário.
- Na `data_recebimento` ou depois, entra como recebido disponível se não estiver aplicado nem vinculado.
- Salários históricos anteriores à data de referência não foram reintroduzidos como caixa livre genérico; a complementação é limitada a recebidos atuais/futuros oficiais da aba Salários.

### Lotes
- Lotes vindos de `fontes_elegiveis_pagamento` preservam a data oficial de elegibilidade do pagamento/evento.
- A Etapa 5 enxerga por dia apenas snapshots com data menor ou igual ao dia simulado, preservando saldo residual via reservas acumuladas já existentes.
- Lotes indisponíveis por carência, exauridos ou migrados continuam bloqueados/fora da seleção conforme os campos oficiais existentes.

### Switching / vencimento
- A regra existente de materialização de switching foi preservada: origem materializada é marcada como migrada e destino pós-switching passa a existir como item temporal quando oficial/canônico.
- Não foi criado switching parcial, rota paralela, sentinela ou nova etapa.

## Contagens antes/depois
- Antes (baseline informado/confirmado no pipeline antes da correção): `qtd_obrigacoes_cobertas=47`, `qtd_obrigacoes_bloqueadas=111`.
- Depois: `qtd_obrigacoes_cobertas=158`, `qtd_obrigacoes_bloqueadas=0`.
- Gates da Etapa 5/6 permaneceram sem bloqueios após a correção (`qtd_bloqueios=0`).

## Evidências do pipeline real
Comando obrigatório executado:

```bash
python -B aplicacao/principal.py
```

Resumo oficial Etapa 9:

```text
qtd_obrigacoes_cobertas: 158
qtd_obrigacoes_bloqueadas: 0
qtd_fontes_utilizadas: 143
qtd_fontes_reservadas: 143
qtd_switchings_escolhidos: 0
```

Console — próximos 5 pagamentos (rota de console não alterada, ainda renderiza limitação observável legada):

```text
2026-06-03 | Faxina Rosa     | pendente_fonte_decisao_etapa5 | pendente_decisao_etapa5
2026-06-07 | Claro           | pendente_fonte_decisao_etapa5 | pendente_decisao_etapa5
2026-06-10 | Fran            | pendente_fonte_decisao_etapa5 | pendente_decisao_etapa5
2026-06-10 | Ginástica Biola | pendente_fonte_decisao_etapa5 | pendente_decisao_etapa5
2026-06-10 | Mari            | pendente_fonte_decisao_etapa5 | pendente_decisao_etapa5
```

Extrato Futuro oficial do XLSX (`saidas/oficial/relatorio_operacional_v225.xlsx`):

```text
2026-06-03 | Faxina Rosa     | Lote 3000 mar. V + Lote 3120 mai + Lote 6630,64 fev. + Lote 7600 jun. | cobertura integral=sim | pacote=2026-06-03::pagamento_combinacao_fontes::1
2026-06-07 | Claro           | Lote 7600 jun.                                                        | cobertura integral=sim | pacote=2026-06-07::pagamento_combinacao_fontes::1
2026-06-10 | Fran            | Lote 7600 jun.                                                        | cobertura integral=sim | pacote=2026-06-10::pagamento_combinacao_fontes::1
2026-06-10 | Ginástica Biola | Lote 7600 jun.                                                        | cobertura integral=sim | pacote=2026-06-10::pagamento_combinacao_fontes::1
2026-06-10 | Mari            | Lote 7600 jun.                                                        | cobertura integral=sim | pacote=2026-06-10::pagamento_combinacao_fontes::1
```

Paridade Etapa 10:

```text
status: aprovado_com_ressalva
xlsx status: aprovado
divergências materiais: 0
ressalva restante: CONSOLE_NAO_AUDITADO
```

Etapa 11:

```text
status: aprovado_com_ressalva
remoção automática autorizada: False
legados candidatos à depreciação: 0
legados bloqueados para remoção: 0
```

## Auditoria de escopo
- Arquivos alterados: `nucleo/estado_temporal_inicial.py`, `nucleo/motor_temporal_conjunto.py` e este log.
- Dados/cache/contratos/modelo/console/exportador/ranking/carteira não alterados.
- A auditoria de escopo confirmou ausência de promoção das rotas auxiliares proibidas.
- Nenhuma bloqueada virou coberta sem pacote válido: gates finais aprovaram com `qtd_bloqueios=0` e o Extrato Futuro exibe pacote e fonte oficial para os primeiros pagamentos.

## Correção adicional — PR #482 / comentário P2

### Problema procedente
A correção inicial permitiu que recebidos/salários entrassem no universo diário a partir da data de recebimento, mas a seleção de `pagamento_com_recebido` avaliava a cobertura com a soma do valor original cheio dos recebidos disponíveis no dia. Sem uma trava de saldo residual acumulado na seleção, o mesmo recebido poderia ser considerado factível em mais de um dia antes de a trajetória interna aplicar as reservas, criando risco de falsa cobertura por reutilização.

### Ajuste aplicado
- Foi adicionada avaliação residual específica para pacotes `pagamento_com_recebido`, análoga à avaliação já existente de lotes/fontes.
- A Etapa 5 agora mantém `reserva_por_recebido` durante a seleção temporal: para cada recebido, o saldo residual é `valor original - reservas planejadas anteriores`.
- Pacotes `pagamento_com_recebido` são descartados antes da seleção quando a soma dos saldos residuais não cobre a obrigação, com motivo auditável `saldo_residual_recebido_insuficiente` ou `saldo_residual_recebido_zerado`.
- A reserva planejada de recebido só é acumulada depois de o pacote ser escolhido como vencedor do dia; pacotes apenas candidatos não consomem saldo.

### Validação adicional
- A contagem oficial permaneceu economicamente válida em `qtd_obrigacoes_cobertas=158` e `qtd_obrigacoes_bloqueadas=0` após o controle residual de recebidos.
- Auditoria programática das reservas de recebidos mostrou `violacoes=[]`: nenhum `recebido:*` teve soma reservada maior que seu valor original.

## Correção adicional — elegibilidade de lotes e switching antes do merge do PR #482

### Problema identificado
A lista `fontes_temporais` era montada antes da materialização final dos switchings no `inventario_temporal`. Assim, origens já migradas por switching podiam continuar presentes como fontes futuras em `fontes_temporais`, enquanto destinos pós-switching eram atualizados no inventário sem reconciliação posterior das fontes. Além disso, a checagem de disponibilidade no motor rejeitava apenas `disponivel_na_referencia=False` ou `status_temporal=indisponivel`, deixando risco de aceitar lotes exauridos/migrados ou saldos operacionalmente nulos.

### Regra corrigida
- Após aplicar switchings materializados ao inventário final, `fontes_temporais` é reconciliada contra esse inventário.
- Fontes cujo lote esteja `exaurido`, `exaurido_por_saque`, `migrado_por_switching`, `exaurido_por_switching` ou `indisponivel` são marcadas como indisponíveis, com motivo auditável.
- Origens de switching materializado recebem `migrado_por_switching=True` e deixam de ser elegíveis como fonte futura.
- Destinos pós-switching materializados preservam `status_inventario_temporal=ativo_pos_switching`, `sintetico_pos_switching=True`, `origem_switching` e `valor_liquido_migrado`, e só permanecem elegíveis quando há saldo líquido operacional positivo.
- Saldos líquidos operacionalmente imateriais (`< 1,00`) são bloqueados para evitar cobertura por sobras residuais que não representam lote utilizável no Extrato Futuro.
- `_fonte_disponivel_referencialmente` passou a rejeitar explicitamente status/motivos de indisponibilidade, origem migrada/exaurida, `migrado_por_switching=True` e valor/saldo disponível insuficiente.
- Obrigações vencidas antes da data de referência podem enxergar fontes já disponíveis na data de referência, evitando bloqueio estrutural quando há fonte oficial atual para liquidar atraso.
- A atualização de saldo interno de fontes passa a observar o maior saldo líquido oficial já disponível na data, preservando reservas acumuladas e alinhando a aplicação interna à seleção temporal projetada.

### Resultado após a reconciliação
- A contagem caiu de `158/0` para `157/1`. A queda foi aceita como bloqueio econômico legítimo após remover fontes inválidas/imateriais.
- Obrigação bloqueada restante: `despesa_auto_00267` em `2027-05-02`, valor `3452.50`, motivo `sem_pacote_valido_para_obrigacao_temporal`.
- Auditoria XLSX com `openpyxl`: `qtd_cobertas=157`, `qtd_bloqueadas=1`, `cobertas_sem_fonte_pacote=0`.
- Lotes exauridos encontrados no Extrato Futuro: `[]`.
- Origens migradas por switching encontradas no Extrato Futuro: `[]`.
- Destinos pós-switching usados como fonte: `Lote 3120 mai`, `Lote 3000 mai Genial`, `Lote 3000 mai Neon`; todos materializados e com saldo positivo.
- P2 de recebidos preservado: auditoria programática manteve `violacoes_recebidos=0`.
- Etapa 10 preservada: `divergências materiais=0`.
- Etapa 11 preservada: `remoção automática autorizada=False`.
- A auditoria de escopo continua sem promoção das rotas auxiliares proibidas.

## Correção adicional — paridade console ↔ XLSX / saída oficial única

### Divergência corrigida
O console integrado ainda chamava `_render_amostras_pagamentos_operacionais(...)`, que constrói amostras a partir da rota observável legada/V17-C7 (`construir_amostras_pagamentos_operacionais` + `construir_pacote_saida_observavel_temporal`). Essa rota era útil como fallback, mas contradizia o `PacoteSaidaObservavelOficial`: próximos pagamentos cobertos no XLSX apareciam no console como `pendente_fonte_decisao_etapa5`, `pendente_decisao_etapa5` e `pendencia_runtime_obrigacao_futura_sem_decisao_etapa5`.

### Regra corrigida
- Na execução oficial integrada, quando `PacoteSaidaObservavelOficial` está presente e preparado, o console renderiza a seção de pagamentos diretamente a partir de `pacote_saida_observavel_oficial.bloco_console`.
- A rota legada/V17-C7 permanece apenas como fallback quando o pacote oficial está ausente.
- Próximos pagamentos cobertos passam a mostrar `Lote`/recebido, `Pacote` e `Status=coberta_oficial` vindos da saída oficial.
- Obrigações bloqueadas oficiais passam a aparecer em tabela explícita com o motivo oficial.

### Evidência do console após a correção
```text
- próximos 5 pagamentos — saída oficial:
2026-06-03 | Faxina Rosa     | Lote 7600 jun.                        | 2026-06-03::pagamento_combinacao_fontes::1 | coberta_oficial | n/d
2026-06-07 | Claro           | recebido:recebido::salario_auto_00019 | 2026-06-07::pagamento_com_recebido::1      | coberta_oficial | n/d
2026-06-10 | Fran            | recebido:recebido::salario_auto_00019 | 2026-06-10::pagamento_com_recebido::1      | coberta_oficial | n/d
2026-06-10 | Ginástica Biola | recebido:recebido::salario_auto_00019 | 2026-06-10::pagamento_com_recebido::1      | coberta_oficial | n/d
2026-06-10 | Mari            | recebido:recebido::salario_auto_00019 | 2026-06-10::pagamento_com_recebido::1      | coberta_oficial | n/d

- obrigações bloqueadas oficiais:
2027-05-02 | Cartão NU | n/d | bloqueada_oficial | sem_pacote_valido_para_obrigacao_temporal
```

### Auditorias finais desta rodada
- Console: `pendente_fonte_decisao_etapa5=0`, `pendente_decisao_etapa5=0`, `pendencia_runtime_obrigacao_futura_sem_decisao_etapa5=0` na seção de pagamentos oficiais.
- Etapa 9: `qtd_obrigacoes_cobertas=157`, `qtd_obrigacoes_bloqueadas=1`, `qtd_fontes_utilizadas=152`, `qtd_fontes_reservadas=152`, `qtd_switchings_escolhidos=0`.
- XLSX/Extrato Futuro: `linhas=158`, `cobertas=157`, `bloqueadas=1`, coerente com Etapa 9.
- `exauridos_no_extrato=0`.
- `migrados_no_extrato=0`.
- `cobertas_sem_fonte_pacote=0`.
- `violacoes_recebidos=0`.
- Destinos pós-switching usados corretamente: `Lote 3120 mai`, `Lote 3000 mai Genial`, `Lote 3000 mai Neon`.
- Etapa 10: `xlsx status=aprovado`, `divergências materiais=0`.
- Etapa 11: `remoção automática autorizada=False`.
- `dados/cache_bcb.json` não aparece em `git status --short` e fica fora do commit.

### Pendências registradas sem rota paralela
- A limpeza/redução de abas diagnósticas do XLSX permanece frente posterior para não aumentar risco neste fechamento.
- A modelagem completa de sobras de recebidos futuros como aportes/lotes futuros permanece pendência econômica explícita para frente própria; nesta rodada foi preservado o saldo residual e impedida reutilização indevida, sem criar etapa, rota paralela ou sentinela.

## Correção adicional — P2 finais antes do merge: saldo futuro e indisponibilidade explícita

### P2 A — não retrodatAR saldo futuro projetado
Regra anterior: `_materializar_fontes_data_referencia_de_lotes_ativos(...)` podia escolher a primeira fonte futura disponível de um lote e clonar essa linha para `data_referencia`, mantendo `valor_bruto_disponivel`, `valor_liquido_disponivel` e `valor_estimado` calculados para a data futura do pagamento. Isso abria risco de cobrir obrigação atual/vencida com rendimento projetado futuro.

Regra corrigida: a materialização na `data_referencia` não usa mais valor calculado para `data_pagamento` futuro. Se não existir snapshot real na data, a função consulta o inventário final reconciliado e só cria snapshot quando há valor atual auditável do próprio inventário/estado (`valor_liquido_disponivel_atual`, `saldo_disponivel_atual`, `valor_original`, `investimento_bruto` ou `valor_liquido_migrado`) com data real não posterior à referência e status economicamente elegível. Se não houver valor atual auditável positivo, nenhum snapshot artificial é criado.

Evidência auditada: após a correção, a auditoria estrutural dos snapshots adicionados na data de referência retornou `snapshots_data_ref_sem_retrodatacao_futura=[]`, ou seja, nenhuma fonte futura projetada foi retrodatada para cobrir pagamento atual/vencido nesta execução.

### P2 B — preservar indisponibilidade explícita de recebidos
Regra anterior: `montar_recebidos_temporais_dia(...)` reabilitava recebidos quando `data_rec <= data_motor`, marcando `disponivel_na_referencia=True` sempre que não estivessem `aplicado` ou `vinculado`. Isso podia ignorar status/motivos explícitos como `exaurido`, `indisponivel`, `comprometido`, `bloqueado`, `consumido` ou `encerrado`.

Regra corrigida: recebidos só são reabilitados automaticamente quando a indisponibilidade é exclusivamente temporal (`futuro`/`futuro_indisponivel`) e a data de disponibilidade já foi alcançada. Qualquer indisponibilidade material explícita em `status_recebido`, `status_temporal`, `status`, `motivo`, `motivo_indisponibilidade` ou `motivo_bloqueio`, bem como flags `aplicado`/`vinculado`, permanece bloqueante. `_recebido_disponivel_referencialmente(...)` aplica a mesma regra antes de formar pacote `pagamento_com_recebido`, preservando o controle residual acumulado já implementado.

Evidência auditada: a auditoria programática pós-pipeline retornou `recebidos_indisponiveis_usados=0` e `violacoes_recebidos=0`, confirmando que recebidos explicitamente indisponíveis/exauridos/comprometidos não foram usados e que nenhum recebido foi reservado acima do valor original.

### Resultado após os P2 finais
- Etapa 9 preservada: `qtd_obrigacoes_cobertas=157`, `qtd_obrigacoes_bloqueadas=1`, `qtd_fontes_utilizadas=152`, `qtd_fontes_reservadas=152`, `qtd_switchings_escolhidos=0`.
- Console oficial preservado: próximos pagamentos cobertos continuam sem `pendente_fonte_decisao_etapa5`, `pendente_decisao_etapa5` ou `pendencia_runtime_obrigacao_futura_sem_decisao_etapa5`.
- XLSX/Extrato Futuro preservado: `linhas=158`, `cobertas=157`, `bloqueadas=1`, coerente com Etapa 9.
- Abas observáveis auditadas: `Obs Resumo Operacional`, `Obs Obrigacoes Cobertas`, `Obs Obrigacoes Bloqueadas`, `Obs Proximos Pagamentos` e `Extrato Futuro` presentes.
- `exauridos_no_extrato=0`.
- `migrados_no_extrato=0`.
- `cobertas_sem_fonte_pacote=0`.
- Destinos pós-switching usados corretamente: `Lote 3120 mai`, `Lote 3000 mai Genial`, `Lote 3000 mai Neon`, sem dupla contagem com origens migradas no Extrato Futuro.
- Etapa 10 preservada: `xlsx status=aprovado`, `divergências materiais=0`.
- Etapa 11 preservada: `remoção automática autorizada=False`.
- `dados/cache_bcb.json` permaneceu fora do diff/commit.
