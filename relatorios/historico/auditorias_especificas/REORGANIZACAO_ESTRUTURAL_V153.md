# Reorganização estrutural V153

## Objetivo
Executar uma primeira reorganização arquitetural **sem alterar o contrato funcional**, começando pelo mapeamento de responsabilidades reais e depois pela redistribuição de funções de menor risco.

## Limitação de baseline no ambiente
O artefato zip rotulado como V152 não estava disponível no ambiente de execução no momento desta etapa. A reorganização foi aplicada sobre a baseline acessível mais recente (`payment-investment-allocation_v151.zip`), preservando o contrato funcional observável do motor diário e sem introduzir mudanças de regra de negócio.

## Mapa de responsabilidades reais

### 1. Aplicação e console
- `aplicacao/principal.py`: ponto de entrada operacional.
- `aplicacao/console/*`: formatação e seções do console.

### 2. Configuração e dados
- `config/*`: contratos de carteira e parâmetros de heurísticas.
- `dados/*`: entrada bruta, cache CDI e planilha operacional.

### 3. Núcleo financeiro canônico
- `nucleo/nucleo_financeiro_minimo.py`: primitivas financeiras centrais.
- `nucleo/calendario_financeiro.py`: calendário e regras de dia útil.
- `nucleo/cache_cdi_bcb.py`: cache e fallback CDI.
- `nucleo/caixa_recebidos_auditaveis.py`: contrato detalhado de recebidos.

### 4. Estado operacional e leitura da base
- `nucleo/leitor_planilha.py`
- `nucleo/dados_operacionais_canonicos.py`
- `nucleo/replay_passado_controlado.py`
- `nucleo/contexto_baseline.py`

### 5. Pagamentos e switching
- `nucleo/alocador_pagamentos_terminal_v1.py`
- `nucleo/planejador_switching_temporal_v1.py`
- `nucleo/comparador_hibrido_switching_v1.py`
- `nucleo/simulador_central_eventos_v1.py`

### 6. Orquestração diária e bloco crítico
- `nucleo/motor_diario_conjunto_experimental_v143.py`
- `nucleo/planejamento_conjunto_local_bloco_critico_v1.py`
- `nucleo/microplanejamento_conjunto_bloco_critico_v2.py`
- `nucleo/heuristica_conjunta_parcial_bloco_critico.py`

### 7. Auditorias, benchmarks e shadow runners
- arquivos `nucleo/*shadow*.py`
- arquivos `nucleo/auditoria_*.py`
- `scripts/diagnostico/*`

## Problema estrutural identificado
O arquivo `nucleo/motor_diario_conjunto_experimental_v143.py` acumulava cinco responsabilidades simultâneas:
1. contratos de dados (dataclasses)
2. preparação de estado
3. composição de métricas e chaves de decisão
4. planejamento diário de switching
5. orquestração do runner

Isso elevava o risco de regressão porque qualquer ajuste local exigia editar o mesmo arquivo de ponta a ponta.

## Redistribuição de baixo risco executada
Foi criado o pacote `nucleo/motor_diario/` com a seguinte divisão:
- `modelos.py`
- `estado.py`
- `metricas.py`
- `planejamento.py`
- `avaliacao.py`
- `README.md`

### Funções movidas
#### Para `modelos.py`
- `PacoteDiaResumoV143`
- `DecisaoDiaV143`
- `ResumoMotorV143`

#### Para `estado.py`
- `_ordenar_pagamentos`
- `_remover_pagamentos_ate_dia`
- `_carregar_estado_janela`

#### Para `metricas.py`
- `_combinar_metricas`
- `_chave_pacote`
- `_chave_pacote_tau`
- `_selecionar_vencedor_pacote`

#### Para `planejamento.py`
- `_cenarios_switching_diario_v143`
- `_melhor_plano_switching_diario_v143`

#### Para `avaliacao.py`
- `_avaliar_continuacao_neutra`
- `_executar_pacote_dia`

## Compatibilidade preservada
O arquivo histórico `nucleo/motor_diario_conjunto_experimental_v143.py` foi mantido como **fachada de compatibilidade**. Ele continua exportando os nomes conhecidos e preserva o ponto de entrada `rodar_motor_diario_conjunto_experimental_v143`.

## Itens intencionalmente não movidos nesta etapa
Para reduzir risco, **não** foram redistribuídos ainda:
- `nucleo/simulador_central_eventos_v1.py`
- `nucleo/alocador_pagamentos_terminal_v1.py`
- `nucleo/planejador_switching_temporal_v1.py`
- módulos do bloco crítico

Esses arquivos seguem como candidatos para uma etapa posterior, porque concentram regras de negócio mais sensíveis.

## Validação mínima executada
- remoção de `__pycache__` do pacote final
- `compileall` de `nucleo/`, `aplicacao/` e `scripts/`
- smoke import de `rodar_motor_diario_conjunto_experimental_v143`

## Próximo recorte recomendado
Próxima micro-etapa de baixo risco:
1. consolidar helpers de cenário bruto/promovível no pacote `nucleo/motor_diario/`
2. mover apenas wrappers de auditoria duplicados entre `scripts/` e `scripts/diagnostico/`
3. só depois abrir a reorganização de `simulador_central_eventos_v1.py`
