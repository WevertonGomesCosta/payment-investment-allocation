# MACRO-ETAPA8-SAIDA-06 — Define plano de equivalência observável entre saída legada e pacote renderizável

## 1. Identificação

- **Macrofrente:** MACRO-ETAPA8-SAIDA-06
- **Tipo:** documental / plano de equivalência observável
- **Baseline de entrada:** `7b9c96e53b70342b84c31a81fca31d651fa694aa`
- **Branch:** `docs/macro-etapa8-saida-06`

## 2. Objetivo

Definir o plano de equivalência observável entre a saída legada consumida por console/XLSX e o `PacoteRenderizacaoSaidaCanonica`, sem migrar consumidores, sem gerar nova saída e sem alterar runtime funcional.

## 3. Estado consolidado

A cadeia pós-gates atual está formalizada como:

```text
LedgerTemporalCanonico validado
ResultadoGatesValidacaoNucleo aprovado
        -> SaidaCanonicaOficial
        -> PacoteRenderizacaoSaidaCanonica
        -> console/XLSX em frente futura
```

Atualmente, `aplicacao/principal.py` constrói internamente `PacoteRenderizacaoSaidaCanonica`, mas console e XLSX ainda consomem a saída legada `saida_canonica`.

## 4. Componentes já disponíveis no pacote renderizável

O pacote renderizável consolidado já expõe:

- `situacao_atual_renderizavel`;
- `auditoria_renderizavel`;
- `switchings_renderizaveis`;
- `obrigacoes_cobertas_renderizaveis`;
- `obrigacoes_bloqueadas_renderizaveis`;
- `fontes_utilizadas_renderizaveis`;
- `fontes_reservadas_renderizaveis`;
- `saldos_referenciais_renderizaveis`;
- `bloqueios_renderizaveis`;
- `avisos_renderizaveis`;
- `evidencias_gates_renderizaveis`.

## 5. Componentes ainda indisponíveis

Ainda permanecem indisponíveis no pacote renderizável, por não serem diretamente deriváveis do schema atual de `SaidaCanonicaOficial`:

- `extrato_passado_renderizavel`;
- `extrato_futuro_renderizavel`;
- `resumo_recebidos_renderizavel`;
- `fechamento_atual_renderizavel`;
- `ranking_renderizavel`.

Esses componentes não devem ser preenchidos por consulta a dados brutos, planilhas, contexto operacional ou reconstrução de saída legada.

## 6. Mapeamento de equivalência por consumidor

### 6.1 Console

| Bloco observável atual | Fonte legada atual | Candidato no pacote renderizável | Status |
|---|---|---|---|
| Situação atual | `saida_canonica.fechamento_atual` e blocos auxiliares | `situacao_atual_renderizavel` + saldos/fontes | Parcial |
| Switchings | métodos e campos legados de switching | `switchings_renderizaveis` | Parcial |
| Amostras de pagamentos | extratos e amostras operacionais legadas | não disponível diretamente | Indisponível |
| Ranking | `ranking_amostra` legado | `ranking_renderizavel` | Indisponível |
| Alertas/auditoria | auditoria legada e mensagens | `auditoria_renderizavel`, `bloqueios_renderizaveis`, `avisos_renderizaveis` | Parcial |

### 6.2 XLSX

| Aba atual | Fonte legada atual | Candidato no pacote renderizável | Status |
|---|---|---|---|
| Extrato Passado | `saida.extrato_passado` | `extrato_passado_renderizavel` | Indisponível |
| Extrato Futuro | `saida.extrato_futuro` | `extrato_futuro_renderizavel` | Indisponível |
| Switching | saída legada + funções observáveis | `switchings_renderizaveis` | Parcial |
| Situação Atual | blocos legados de situação | `situacao_atual_renderizavel` + fontes/saldos | Parcial |
| Saida Canonica | auditoria e switchings legados | `auditoria_renderizavel` + evidências | Parcial |
| Auditoria Fontes | extrato futuro e auditoria legada | `fontes_utilizadas_renderizaveis` + `fontes_reservadas_renderizaveis` | Parcial |
| Auditoria FIFO | extrato futuro + auditoria FIFO legada | não disponível diretamente | Indisponível |

## 7. Critérios de equivalência observável

A equivalência futura deve ser avaliada em três níveis.

### 7.1 Equivalência estrutural

Cada componente renderizável deve declarar:

- nome;
- disponibilidade;
- origem formal;
- cabeçalhos;
- linhas;
- motivo de indisponibilidade, quando aplicável.

### 7.2 Equivalência semântica

Para campos disponíveis, a semântica deve preservar:

- identificação da obrigação;
- status coberta/bloqueada;
- fonte utilizada/reservada;
- switching escolhido;
- saldos referenciais;
- bloqueios/avisos/evidências.

### 7.3 Equivalência operacional

A camada futura só poderá substituir bloco legado se:

- o componente renderizável tiver origem em `SaidaCanonicaOficial`;
- não depender de dados brutos;
- não reexecutar motor, ledger ou gates;
- não alterar decisão econômica;
- tiver saída comparável lado a lado contra o bloco legado.

## 8. Plano de comparação lado a lado

A futura frente de comparação deve:

1. manter console/XLSX legados como saída principal;
2. produzir, se autorizado, uma estrutura diagnóstica em memória ou arquivo controlado separado;
3. comparar contagens, chaves e totais agregados entre blocos legados e renderizáveis;
4. registrar divergências por componente;
5. classificar divergências como:
   - schema ausente;
   - campo semanticamente diferente;
   - componente não derivável;
   - diferença esperada de apresentação;
   - erro de mapeamento;
6. bloquear substituição se houver divergência econômica.

## 9. Proibições para a próxima fase

A próxima fase não deve:

- migrar console diretamente;
- migrar XLSX diretamente;
- substituir `saida_canonica` sem comparação lado a lado;
- consultar dados brutos;
- consultar planilha;
- reprocessar motor;
- reprocessar ledger;
- reprocessar gates;
- corrigir decisão econômica em camada de saída;
- gerar saída oficial nova sem autorização macro específica.

## 10. Sequência macro recomendada

### MACRO-ETAPA8-SAIDA-07 — Implementa comparador diagnóstico lado a lado sem substituir consumidores

Objetivo:

- comparar saída legada e pacote renderizável;
- produzir relatório diagnóstico controlado;
- não alterar console/XLSX oficiais.

### MACRO-ETAPA8-SAIDA-08 — Expande schema renderizável para componentes parcialmente equivalentes

Objetivo:

- melhorar componentes parciais;
- manter indisponíveis os campos não deriváveis;
- não gerar saída oficial nova.

### MACRO-ETAPA8-SAIDA-09 — Decide primeira migração observável controlada

Objetivo:

- escolher console ou XLSX como primeiro consumidor migrável;
- migrar apenas blocos com equivalência aprovada;
- manter rollback simples.

## 11. Critérios de aceite desta macrofrente

Esta macrofrente é aceita se:

1. mapear componentes disponíveis e indisponíveis;
2. definir critérios de equivalência estrutural, semântica e operacional;
3. definir plano de comparação lado a lado;
4. não alterar código funcional;
5. não migrar consumidores;
6. não gerar saída nova.

## 12. Conclusão

A camada pós-gates já existe internamente, mas ainda não possui equivalência observável suficiente para substituir console/XLSX.

A próxima ação tecnicamente segura é implementar um comparador diagnóstico lado a lado, preservando consumidores legados até que equivalência suficiente seja demonstrada.
