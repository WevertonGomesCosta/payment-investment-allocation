# ME-V17-F0-V4N — Promove parâmetro temporal shadow no construtor oficial de saída

## Objetivo
Promover o parâmetro opcional `incluir_temporal_shadow` para a assinatura oficial de `construir_saida_canonica`, mantendo comportamento padrão inalterado e ativação explícita do bloco `temporal_shadow_v4k` apenas quando solicitado.

## Alterações realizadas
- Atualizada a assinatura oficial para:
  - `def construir_saida_canonica(contexto: Any, *, versao: str = 'V203', incluir_temporal_shadow: bool = False) -> PacoteSaidaCanonica`
- Mantida toda a lógica padrão de construção de saída.
- Ajustado retorno para criação intermediária de `pacote = PacoteSaidaCanonica(...)`.
- Quando `incluir_temporal_shadow=True`:
  - Import local de `replace` (`dataclasses`) e dos símbolos de `nucleo.saida_canonica_temporal_shadow_v4k`.
  - Cópia de auditoria existente e acréscimo apenas da chave `temporal_shadow_v4k`.
  - Retorno via `replace(pacote, auditoria=auditoria_shadow)`.
- Quando `incluir_temporal_shadow=False`:
  - Retorno de `pacote` idêntico ao comportamento anterior.

## Diagnóstico criado
Arquivo:
- `scripts/diagnostico/auditar_saida_canonica_parametro_temporal_shadow_v4n.py`

O diagnóstico compara:
- `saida_padrao = construir_saida_canonica(contexto)`
- `saida_false = construir_saida_canonica(contexto, incluir_temporal_shadow=False)`
- `saida_true = construir_saida_canonica(contexto, incluir_temporal_shadow=True)`

E valida os critérios V4N esperados, incluindo preservação observável completa da saída padrão e presença exclusiva do bloco de auditoria temporal quando ativado.

## Execução local das validações
- `python -m py_compile nucleo/saida_canonica.py` ✅
- `python -m py_compile scripts/diagnostico/auditar_saida_canonica_parametro_temporal_shadow_v4n.py` ✅
- `python scripts/diagnostico/auditar_saida_canonica_parametro_temporal_shadow_v4n.py --sem-csv` ✅ (`validacao_v4n_ok=True`)
- `python -B aplicacao/principal.py` ⚠️ falhou por ausência de insumo externo esperado (`erro_csv_s6_ausente_sem_recomposicao_segura`), sem relação com a microetapa
- `git diff --check` ✅
- `git status -sb` ✅

## Resultado
Microetapa V17-F0-V.4N implementada com sucesso no escopo permitido.
