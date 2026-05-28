# MACRO-ETAPA5-FIX-PAGAMENTOS-FUTUROS

## Baseline

- Repositório: `WevertonGomesCosta/payment-investment-allocation`.
- Branch de trabalho: `work`.
- HEAD inicial esperado e confirmado localmente: `e49024b1a958fe229f46db78be02551d29edf6d0`.
- Frente: correção cirúrgica da Etapa 5 para pagamentos futuros.

## Arquivos alterados

- `nucleo/motor_temporal_conjunto.py`.
- `logs/iteracoes/MACRO-ETAPA5-FIX_PAGAMENTOS_FUTUROS.md`.

## Causa encontrada

- A geração de pacotes de pagamento consumia diretamente a lista temporal de fontes referenciadas por data, permitindo múltiplos snapshots do mesmo lote na lista de candidatas.
- O pacote `pagamento_combinacao_fontes` somava a cobertura referencial sobre essa lista com repetições, inflando artificialmente `valor_cobertura_referencial`.
- Quando a decisão diária terminava em `sem_pacote_valido` com `pacote is None`, a trajetória interna registrava o evento `sem_pacote_vencedor`, mas não materializava `ObrigacaoBloqueadaTemporalmente` por obrigação aberta do dia.
- A auditoria da trajetória não verificava de forma explícita o caso de obrigação aberta sem pacote vencedor com bloqueios individuais obrigatórios.

## Correções aplicadas

- Incluída chave estável de fonte temporal referencial priorizando `fonte_id`, `id`, `identificador` e `codigo`.
- Incluída deduplicação de fontes referenciadas por data, preservando uma fonte por chave estável e preferindo o registro temporal mais recente disponível até `data_motor` quando há campo temporal comparável.
- Aplicada deduplicação antes da geração de pacotes `pagamento_fonte_unica` e `pagamento_combinacao_fontes`.
- Ajustado o cálculo de `valor_cobertura_referencial` do pacote `pagamento_combinacao_fontes` para operar sobre fontes únicas.
- Alterada a aplicação do pacote vencedor diário para receber `obrigacoes_do_dia` quando disponível.
- Quando `pacote is None`, a trajetória passa a bloquear individualmente cada obrigação do dia com motivo `sem_pacote_valido_para_obrigacao_temporal`, `pacote_id=None`, `valor_cobertura_referencial=0.0` e preservação da referência original da obrigação.
- Auditoria interna da trajetória passou a exigir bloqueio individual para obrigação aberta em data sem pacote vencedor e a continuar bloqueando reservas indevidas sem pacote.
- Auditoria final passou a reconhecer o motivo explícito `sem_pacote_valido_para_obrigacao_temporal` como tratamento individual válido nesse cenário.

## Datas de auditoria direta

- `2026-06-02`: pacote vencedor `pagamento_combinacao_fontes`; fontes candidatas deduplicadas; cobertura referencial deixou de refletir repetições dos mesmos lotes; 2 obrigações cobertas; reservas coerentes nos lotes `Lote 3000 mai Genial` e `Lote 3000 mai Neon`.
- `2026-06-06`: decisão permanece `sem_pacote_valido`; 1 obrigação bloqueada individualmente com motivo explícito; sem reservas.
- `2026-06-07`: decisão permanece `sem_pacote_valido`; 1 obrigação bloqueada individualmente com motivo explícito; sem reservas.
- `2026-06-10`: decisão permanece `sem_pacote_valido`; 3 obrigações bloqueadas individualmente com motivo explícito; sem reservas.

## Validações executadas

- `git diff --name-only origin/main...HEAD`: não executável plenamente no ambiente porque não há remoto/ref `origin/main` configurado localmente.
- `python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py`: sucesso.
- `python -B aplicacao/principal.py`: sucesso; execução operacional manteve limitação ambiental já existente de download da planilha via Google Docs por `ProxyError`/403 e usou fallback/cache local.
- Auditoria direta inline sem criação de script diagnóstico: sucesso.
- `git status --short`: conferido durante a implementação; somente arquivos permitidos aparecem antes do commit.

## Limitações

- O ambiente local não possui remoto `origin`, portanto a validação `git diff --name-only origin/main...HEAD` retorna erro de referência inexistente.
- A execução de `python -B aplicacao/principal.py` reporta falha ambiental de download da planilha por proxy/403, mas conclui com fallback local conforme comportamento existente.
- A correção não altera o critério econômico geral nem a decisão de inexistência de pacote válido nas datas que permanecem sem pacote.

## Confirmação de escopo

- Não foram alterados console, XLSX, saída canônica, dados, scripts diagnósticos, planilha operacional, contratos das etapas, ranking da Carteira ou lógica das Etapas 6/7/8/9.
- Não foi criado script diagnóstico.
- Não foi introduzido fallback legado, shadow, wrapper transitório, rota paralela ou sentinela.
- Não foram reintroduzidos `ContextoBaseline` nem `ContextoSaidaCanonicaCompat`.
