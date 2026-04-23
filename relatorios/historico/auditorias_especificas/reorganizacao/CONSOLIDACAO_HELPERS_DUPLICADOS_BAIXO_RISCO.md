# Consolidação de helpers duplicados de baixo risco

## Escopo

Esta etapa consolida apenas helpers pequenos e neutros previamente mapeados na auditoria estrutural, sem alterar o motor financeiro, o replay, o `proxy v3` congelado ou os benchmarks shadow como regras decisórias.

## Consolidações aplicadas

1. **Normalização de valores exauridos na situação atual**
   - fonte única: `nucleo.utilitarios_neutros.normalizar_valores_situacao_atual_exaurida`
   - consumidores atualizados:
     - `aplicacao/console/principal.py`
     - `scripts/operacional/gerar_planilha_operacional.py`

2. **Leitura simples de configuração**
   - fonte única material: `nucleo.config_utils.obter_config`
   - consumidores atualizados:
     - `nucleo.triagem_motor`
     - `nucleo.resolver_hibrido_5p_shadow`
     - `nucleo.switching_economico_shadow`
   - `nucleo.carregador_config.obter_config` foi preservado apenas como compatibilidade delegando para a fonte única.

3. **Iteração de datas e simulação de lote em camadas shadow**
   - fonte única: `nucleo.helpers_shadow_compartilhados`
   - consumidores atualizados:
     - `nucleo.resolver_hibrido_5p_shadow`
     - `nucleo.switching_economico_shadow`

## O que permaneceu propositalmente

- `obter_config_obrigatorio` em `nucleo.carregador_config.py`.
- Helpers específicos de domínio que não eram claramente neutros ou que ainda não tinham equivalência segura.
- Wrappers, relatórios e benchmarks shadow já estabilizados nas versões anteriores.

## Resultado esperado

- menos risco de divergência futura entre camadas shadow e camada de apresentação;
- compatibilidade preservada;
- nenhuma mudança funcional intencional no motor ou nas decisões vigentes.
