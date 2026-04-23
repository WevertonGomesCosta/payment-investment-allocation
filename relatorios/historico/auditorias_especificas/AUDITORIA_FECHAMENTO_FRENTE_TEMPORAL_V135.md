# Auditoria de fechamento da frente temporal — V135

## Pergunta de decisão

Decidir se a evidência atual já permite encerrar a frente temporal com a única subjanela vencedora oficial `2026-04-30` a `2026-05-04`, ou se ainda existe justificativa técnica para estender a grade diária oficial híbrida até `2027-03-31`.

## Evidência já consolidada no fluxo oficial híbrido

### Subjanela oficialmente vencedora já confirmada

- `2026-04-30` a `2026-05-04`
- promoção oficial: `vencedor_terminal`
- cenário promovido: `Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150%`

### Período ampliado já auditado

- `2026-05-21` a `2026-08-18`
- dias auditados: `90`
- dias promovidos com switching: `0`
- dias promovidos com baseline: `90`
- a partir de `2026-06-03`, a origem oficial passa majoritariamente para `sem_cenarios_gerados`

## Evidência estrutural da base que impede encerrar a frente agora

A planilha-base ainda contém um bloco grande de **lotes futuros não aportados** e um volume material de **pagamentos futuros após `2026-08-18`**.

### Lotes futuros não aportados ainda fora do trecho auditado

- quantidade: `24`
- valor total: `R$ 144.880,00`
- distribuição mensal de recebidos não aportados:
  - `2026-05`: `R$ 16.280,00`
  - `2026-06`: `R$ 14.480,00`
  - `2026-07`: `R$ 12.680,00`
  - `2026-08`: `R$ 12.680,00`
  - `2026-09` a `2027-03`: `R$ 12.680,00` por mês

Exemplos explícitos ainda fora do recorte ampliado já consolidado:
- `Lote 7000 set.` — `2026-09-01`
- `Lote 5680 set.` — `2026-09-04`
- `Lote 7000 out.` — `2026-10-02`
- `Lote 5680 out.` — `2026-10-05`
- ...
- `Lote 7000 mar.` — `2027-03-03`
- `Lote 5680 mar.` — `2027-03-06`

### Pagamentos futuros ainda fora do trecho auditado

- pagamentos após `2026-08-18`: `99`
- valor total: `R$ 109.528,22`
- distribuição mensal:
  - `2026-08`: `R$ 5.913,31`
  - `2026-09`: `R$ 14.474,18`
  - `2026-10`: `R$ 14.073,98`
  - `2026-11`: `R$ 13.574,18`
  - `2026-12`: `R$ 17.094,18`
  - `2027-01`: `R$ 12.588,85`
  - `2027-02`: `R$ 15.735,95`
  - `2027-03`: `R$ 16.073,59`

## Interpretação técnica

A evidência atual **não é suficiente para encerrar a frente temporal** por dois motivos:

1. o horizonte oficial híbrido consolidado termina em `2026-08-18`, mas a base ainda contém um volume material de fluxo de caixa e de lotes novos até `2027-03-31`;
2. o fato de o fluxo oficial passar a registrar `sem_cenarios_gerados` já a partir de `2026-06-03` não pode ser interpretado, sozinho, como prova de inexistência de oportunidade estrutural até `2027-03-31`, porque a própria base ainda ganha novos lotes não aportados depois disso.

Em outras palavras:

- **o baseline domina o trecho já auditado**;
- mas **isso não basta para concluir que dominará o restante do horizonte**, porque o universo de fontes muda materialmente com a entrada dos lotes futuros não aportados.

## Decisão de fechamento

### Decisão recomendada

**Não encerrar ainda a frente temporal.**

### Justificativa

A extensão até `2027-03-31` ainda vale a pena, mas com uma restrição metodológica clara:

- ela deve ser executada no **fluxo oficial híbrido**;
- e deve verificar explicitamente se os **lotes não aportados futuros passam a entrar como fontes elegíveis** a partir da data de recebimento.

Sem essa checagem, uma expansão cega do horizonte corre o risco de apenas repetir `baseline_sem_switching` por ausência artificial de cenários.

## Conclusão operacional

Até aqui, a única subjanela oficialmente vencedora continua sendo:

- `2026-04-30` a `2026-05-04`

Mas a frente temporal **não deve ser encerrada ainda**, porque o trecho `2026-08-19` a `2027-03-31` permanece economicamente relevante e estruturalmente incompleto do ponto de vista da entrada de novas fontes não aportadas.

## Próxima ação correta

A próxima etapa deve ser:

1. auditar a ativação dos lotes não aportados futuros no fluxo oficial híbrido a partir da data de recebimento;
2. só então estender a grade diária oficial híbrida até `2027-03-31`.
