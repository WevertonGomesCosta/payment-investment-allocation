# ME-V17-F0-V31 — Integra Switching ao inventario_canonico operacional

## 1. Identificação

- MICROETAPA: ME-V17-F0-V31
- VERSAO_CANDIDATA: V17-F0-V.3.1
- TIPO: CÓDIGO / ETAPA 3 / CANONIZAÇÃO OPERACIONAL
- CLASSE: INTEGRA_SWITCHING_AO_INVENTARIO_CANONICO_OPERACIONAL
- STATUS: CONCLUÍDA
- ALTERA_CODIGO: sim
- ALTERA_ETAPA_3: sim
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_MOTOR: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_RENDERIZACAO: não
- ALTERA_DADOS: não

---

## 2. Objetivo

Implementar a decisão registrada na V17-F0-V.3.0: fazer o `inventario_canonico` nascer completo na Etapa 3, incorporando os lotes derivados da aba `Switching`.

---

## 3. Alterações realizadas

Foram alterados apenas:

- `nucleo/dados_operacionais_canonicos.py`
- `nucleo/inventario_lotes_expandido_pos_switching.py`

A implementação:

1. Corrige a leitura temporal da aba `Switching`:
   - `Data Recebimento` -> `data_recebimento`;
   - `Data Aplicação` -> `data_aplicacao`;
   - `data_switching` é mantida por compatibilidade, usando preferencialmente `data_aplicacao`.

2. Converte cada switching válido em linha compatível com o schema do inventário.

3. Retorna `inventario_canonico` já expandido operacionalmente:

```text
inventario_canonico =
inventario_canonico_base
+
lotes_pos_switching_normalizados
Mantém inventario_lotes_expandido como espelho compatível do inventario_canonico operacional.
Registra risco de dupla contagem dos lotes origem migrados, sem neutralização temporal agressiva nesta etapa.
```

4. Arquivos não alterados
nucleo/validacao_pre_execucao.py
nucleo/leitor_planilha.py
nucleo/nucleo_financeiro_minimo.py
nucleo/saida_canonica.py
nucleo/saida_observavel.py
aplicacao/principal.py
contrato operacional
modelo oficial
README
dados financeiros
cache BCB
5. Critérios de aceite

A V3.1 é aceita se:

switching_canonico contém data_recebimento, data_aplicacao e data_switching preenchidas;
lotes_pos_switching_normalizados contém Lote 3120 mai com:
data_recebimento = 2026-05-04;
data_aplicacao = 2026-05-05;
data_base_fiscal = 2026-05-05;
valor_original = 3122.53;
produto resolvido;
inventario_canonico contém Lote 3120 mai;
inventario_lotes_expandido é compatível com o inventario_canonico operacional;
o núcleo financeiro consegue enxergar o lote POS sem alteração em nucleo_financeiro_minimo.py.
6. Status final
V3_1_INTEGRA_SWITCHING_INVENTARIO_CANONICO=concluida
INVENTARIO_CANONICO_OPERACIONAL_EXPANDIDO=sim
NOVO_ARTEFATO_DOMINANTE=nao
NUCLEO_FINANCEIRO_ALTERADO=nao
SAIDA_CANONICA_ALTERADA=nao
CLAMP_V2_2_AINDA_NAO_REMOVIDO=sim
PROXIMA_AUDITORIA=verificar_nucleo_financeiro_enxerga_lotes_pos_switching

