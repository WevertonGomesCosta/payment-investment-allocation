# MACRO-ETAPA5-B — Valoração e seleção do pacote temporal vencedor

## Baseline local usado
- Tentativa de atualização com `origin` não disponível no ambiente (fetch/pull falharam).
- `git checkout main` não foi possível neste ambiente (branch ausente localmente).
- Base local utilizada: branch atual com histórico local disponível.
- Histórico local (`git log -5 --oneline`) registrado para rastreabilidade.

## Objetivo
Valorar pacotes candidatos por data de forma referencial/heurística e selecionar um pacote vencedor por data no `ResultadoMotorTemporalConjunto`, sem executar pagamento/switching e sem ledger.

## Arquivos alterados
- `nucleo/motor_temporal_conjunto.py`
- `logs/iteracoes/MACRO-ETAPA5-B_VALORA_SELECIONA_PACOTE_VENCEDOR.md`

## Estruturas criadas/modificadas
- Dataclasses criadas:
  - `ValoracaoPacoteTemporal`
  - `PacoteTemporalValorado`
  - `JustificativaDecisaoTemporal`
  - `PacoteTemporalDescartado`
  - `DecisaoTemporalDia`
  - `AuditoriaDecisaoTemporalConjunto`
- `ResultadoMotorTemporalConjunto` expandido com:
  - `pacotes_temporais_valorados_por_data`
  - `pacote_vencedor_por_data`
  - `decisoes_temporais_por_data`
  - `pacotes_descartados_por_data`
  - `auditoria_decisao_temporal_conjunto`

## Funções criadas/modificadas
- `valorar_pacote_temporal_candidato`
- `valorar_pacotes_temporais_candidatos`
- `selecionar_pacote_temporal_vencedor_dia`
- `selecionar_pacotes_temporais_vencedores`
- `auditar_decisoes_temporais`
- `construir_resultado_motor_temporal_conjunto` atualizado para acoplar valoração, seleção e auditoria de decisão.

## Critérios de valoração
- Cálculo referencial de:
  - valor de obrigações;
  - valor de cobertura;
  - valor descoberto;
  - cobertura integral.
- Penalidades heurísticas para:
  - bloqueio estrutural;
  - status não avaliado/inválido;
  - complexidade de switching.
- Score referencial por combinação de cobertura, descoberto e penalidades.

## Critérios de seleção
- Se houver pacote `sem_obrigacao`, priorização direta para data sem obrigação.
- Caso geral, ordenação por:
  1. factível antes de bloqueado;
  2. cobertura integral antes de parcial;
  3. maior cobertura referencial;
  4. menor descoberto;
  5. tipo mais simples antes de combinação;
  6. maior score;
  7. ordem estável por `pacote_id`.

## Limites explícitos
- Não executa pagamento.
- Não promove/executa switching novo.
- Não cria ledger.
- Não altera console/XLSX/saída canônica/dados.

## Validações executadas
- `git diff --name-only origin/main...HEAD`
- `python -m py_compile nucleo/motor_temporal_conjunto.py`
- `python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py`
- `python -B aplicacao/principal.py`
- `git status --short`

## Falhas de validação
- `git diff --name-only origin/main...HEAD` falhou por ausência de `origin/main`.
- `python -B aplicacao/principal.py` executou com fallback de rede externo, sem bloquear.

## Confirmações de escopo
- Escopo restrito aos dois arquivos permitidos.
- Sem alterações fora do escopo funcional definido.

## Correções P2 (review Codex)
- Impedido vencedor `switching_integral_simples`/`switching_integral_agregado` em dia com obrigação aberta quando switching-only.
- `switching_mais_pagamento` agora calcula cobertura referencial por campos canônicos de switching (`valor_liquido_migrado`, `valor_migrado`, `valor`) e só marca factível com cobertura positiva; caso contrário, bloqueia com motivo explícito.
- `pagamento_com_recebido` agora filtra recebidos indisponíveis (`disponivel_na_referencia=False`, `aplicado=True`, `vinculado=True`, `futuro_indisponivel=True`); se todos indisponíveis, pacote fica bloqueado estruturalmente.
- Obrigações do dia agora ignoram pagamentos históricos já pagos ou sem necessidade de decisão (`pago=True` ou `fonte_a_decidir=False`).
- Auditoria de decisões ampliada para sinalizar: vencedor switching-only com obrigação aberta, vencedor com descoberto sem bloqueio, e `pagamento_com_recebido` factível com recebido indisponível.

## Ajustes P2 PR #414
- pagamento_fonte_unica: factível apenas com cobertura referencial suficiente; cobertura zero/insuficiente agora bloqueia com motivo explícito.
- pagamento_combinacao_fontes: factível apenas com cobertura integral referencial; parcial/zero bloqueia com motivo explícito.
- switching_mais_pagamento: exige cobertura referencial de switching >= obrigações; parcial/zero bloqueia com motivo explícito.

## Ajustes P2 PR #415
- pagamento_com_recebido bloqueado para cobertura parcial/zero mesmo com recebidos disponíveis.
- indices_pagamentos sincronizados com pagamentos_referenciados filtrados.
- fonte sem valor referencial agora bloqueia pagamento_fonte_unica.
- seleção consolidada com reserva referencial interdiária mínima por fonte_id para evitar sobrecompromisso.
- auditoria ampliada para cobertura parcial em pagamento_com_recebido, fonte sem valor/id e inconsistência de índices.

