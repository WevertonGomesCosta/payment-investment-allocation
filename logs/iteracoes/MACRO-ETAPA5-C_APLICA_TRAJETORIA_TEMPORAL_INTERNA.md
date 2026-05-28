# MACRO-ETAPA5-C — Aplicação da trajetória temporal interna escolhida

## Baseline local usado

- Branch inicial local: `work`.
- Branch de implementação criada: `macro-etapa5-c-aplica-trajetoria-temporal-interna`.
- Topo local usado: `a2d363b update dados cache bcb`.
- Histórico local imediatamente anterior continha `fd6530c Merge pull request #416 from WevertonGomesCosta/codex/implementar-macroetapa-5-pacotes-candidatos-ppaywb`.
- Limitação: o remoto `origin` não estava configurado/acessível no ambiente; `git fetch origin`, `git pull --ff-only origin main` e `git diff --name-only origin/main...HEAD` não puderam usar `origin/main`.

## Objetivo

Aplicar internamente, de forma referencial e sem efeitos colaterais externos, a sequência de pacotes temporais vencedores por data já escolhida pela MACRO-ETAPA5-B, enriquecendo `ResultadoMotorTemporalConjunto` com a trajetória temporal interna escolhida.

## Arquivos alterados

- `nucleo/motor_temporal_conjunto.py`
- `logs/iteracoes/MACRO-ETAPA5-C_APLICA_TRAJETORIA_TEMPORAL_INTERNA.md`

## Estruturas criadas/modificadas

### Criadas

- `EventoTrajetoriaTemporalInterna`
- `FonteReservadaTemporalmente`
- `ObrigacaoCobertaTemporalmente`
- `ObrigacaoBloqueadaTemporalmente`
- `SwitchingEscolhidoTemporalmente`
- `SaldoReferencialFonteTemporal`
- `EstadoTemporalInternoDia`
- `TrajetoriaTemporalInternaEscolhida`
- `AuditoriaTrajetoriaTemporalInterna`

### Modificadas

- `ResultadoMotorTemporalConjunto`, enriquecido com:
  - `trajetoria_temporal_interna_escolhida`
  - `eventos_trajetoria_temporal`
  - `estado_temporal_interno_por_data`
  - `fontes_reservadas_temporalmente`
  - `obrigacoes_cobertas_temporalmente`
  - `obrigacoes_bloqueadas_temporalmente`
  - `switchings_escolhidos_temporalmente`
  - `auditoria_trajetoria_temporal_interna`

## Funções criadas/modificadas

### Criadas

- `extrair_identificador_fonte_pacote`
- `extrair_valor_reservavel_fonte_pacote`
- `extrair_identificador_obrigacao_pacote`
- `aplicar_pacote_temporal_vencedor_dia`
- `aplicar_trajetoria_temporal_interna`
- `auditar_trajetoria_temporal_interna`
- Funções auxiliares internas para normalização de valores, extração de recebidos, reservas referenciais e síntese de saldos.

### Modificadas

- `construir_resultado_motor_temporal_conjunto`, que agora chama a aplicação da trajetória interna depois da seleção dos vencedores e anexa as novas estruturas ao `ResultadoMotorTemporalConjunto`.
- `__all__`, atualizado para exportar as novas estruturas e funções públicas da macroetapa.

## Tipos de eventos internos gerados

- `pacote_temporal_vencedor_aplicado_internamente`
- `dia_sem_obrigacao_referencial`
- `pagamento_coberto_referencialmente`
- `obrigacao_bloqueada_referencialmente`
- `switching_escolhido_referencialmente`
- `sem_pacote_vencedor`

## Limites explícitos preservados

- Não executa pagamento real.
- Não consome saldo oficial.
- Não liquida obrigação oficialmente.
- Não executa switching novo.
- Não materializa lote pós-switching oficial.
- Não cria ledger oficial.
- Não altera console.
- Não altera XLSX.
- Não altera saída canônica.
- Não altera dados.
- Não cria scripts diagnósticos.
- Não usa console, XLSX, saída canônica, logs ou diagnósticos como fonte de estado.

## Validações executadas

- `git diff --name-only origin/main...HEAD` — falhou por ausência de `origin/main` no ambiente.
- `python -m py_compile nucleo/motor_temporal_conjunto.py` — passou.
- `python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py` — passou.
- `python -B aplicacao/principal.py` — passou; usou fallback local para a planilha por bloqueio de proxy no download externo e cache local do BCB.
- `git status --short` — executado após validação.

## Falhas ou limitações de validação

- Remoto `origin` ausente/inacessível.
- Branch `main` local não existia como branch ativa/checável; a base local disponível já estava no commit `a2d363b` com PR #416 mergeada.
- Download externo da planilha falhou por proxy `403 Forbidden`; a aplicação continuou com fallback local.
- `python -B aplicacao/principal.py` não deixou alteração rastreada em `dados/cache_bcb.json`.

## Confirmações

- Ledger oficial não foi criado.
- Console não foi alterado.
- XLSX não foi alterado por este diff.
- Saída canônica não foi alterada por este diff.
- Dados não foram alterados por este diff.
