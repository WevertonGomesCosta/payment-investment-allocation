# AUDITORIA POS-VENCIMENTO V145

## Escopo

Baseline usada: **V144**.

Janela crítica auditada: **2026-05-03 a 2026-05-06**.

Objetivo: verificar se o gate atual do motor diário está escondendo um caso realmente vencedor de `switch_then_pay` quando os lotes **Lote 3000 mar. V** e **Lote 3000 mar. B** entram em vencimento em **2026-05-04**, com rollover obrigatório no próprio dia ou, no máximo, em **2026-05-05**.

## Achado estrutural principal

A política operacional já existe no config:

- `politicas.pos_vencimento.rendimento = "parar"`
- `politicas.pos_vencimento.acao = "disponivel_para_resgate"`

Mas essa política **não está implementada no planejador temporal nem no motor diário experimental** nesta baseline. Na auditoria do código, não há uso de `pos_vencimento` em:

- `nucleo/planejador_switching_temporal_v1.py`
- `nucleo/motor_diario_conjunto_experimental_v143.py`

Além disso, o planejador atual avalia lotes aportados como se ainda fossem fontes normais de switching, descontando custo fiscal na migração e projetando continuidade econômica do produto de origem após a data da ação. Os pontos centrais estão em `nucleo/planejador_switching_temporal_v1.py`:

- linhas **230-232**: estima imposto e subtrai custo fiscal do valor migrado
- linhas **237-243**: projeta o patrimônio terminal da origem a partir do retorno do produto atual
- linhas **303-309**: só promove candidato se o ganho econômico líquido for positivo frente a esse baseline

Isso cria um viés exatamente no caso dos lotes 3k mar: no pós-vencimento, o correto é tratar o lote como **caixa líquido disponível**, não como produto que ainda continua rendendo no estado de origem.

## Evidência a partir da V144 já auditada

No diagnóstico existente da V144 para a janela maior 2026-05-03 a 2026-05-12:

- em **2026-05-04**, o motor registra:
  - `acoes_elegiveis = 10`
  - `cenarios_gerados = 8`
  - `cenarios_promoviveis = 0`
- o melhor switching bruto do dia foi:
  - **`Lote 7000 mai. -> Mercado Pago Cofrinho 120% CDI (Meli+)`**
- portanto, os lotes **3k mar** não entraram como caso promovível relevante no dia crítico do vencimento.

Isso é consistente com o viés estrutural acima: o gate atual não está operacionalizando o pós-vencimento dos lotes 3k mar.

## Dados críticos usados na auditoria

Da planilha-base `dados/dados_financeiros.xlsx`:

- `Lote 3000 mar. V`
  - data aplicação: **2026-03-03**
  - valor original: **3000,00**
  - investimento: **CDB XP 230%**
- `Lote 3000 mar. B`
  - data aplicação: **2026-03-04**
  - valor original: **3000,00**
  - investimento: **CDB XP 230%**
- `Lote 7000 mai.`
  - data recebimento: **2026-05-03**
  - valor original: **7000,00**
  - ainda não aportado

Valores líquidos monitorados já usados na trilha do projeto para os lotes 3k mar:

- `Lote 3000 mar. V`: **R$ 3.101,29**
- `Lote 3000 mar. B`: **R$ 3.098,22**
- total líquido conjunto: **R$ 6.199,51**

## Correção conceitual mínima aplicada na auditoria

Para responder à pergunta do usuário, a auditoria considerou a regra operacional correta:

1. em **2026-05-04**, os lotes 3k mar deixam de ser avaliados como “produto XP 230% ainda rendendo”
2. passam a ser tratados como **caixa líquido disponível** no vencimento
3. o rollover deve acontecer em **2026-05-04** ou, no máximo, em **2026-05-05**
4. a comparação relevante deixa de ser “resgatar ou não resgatar” e passa a ser:
   - **rollover em 2026-05-04**
   - **adiar rollover para 2026-05-05**

## Destino mais plausível e economicamente viável

Na shortlist auditada:

- `CDB XP 150%` tem **aplicação mínima de R$ 10.000,00**, então não é viável para o rollover individual dos lotes 3k mar e também não fecha para o total conjunto de R$ 6.199,51.
- `Mercado Pago Cofrinho 120% CDI (Meli+)` é viável:
  - aplicação mínima: **R$ 1,00**
  - aplicação máxima: **R$ 10.000,00**
  - carência: **0 dias**
  - liquidez: **0 dias**

Por isso, ele é o melhor proxy de destino viável para o rollover obrigatório nesta janela curta.

## Cálculo econômico mínimo do atraso de um dia

Usando o total líquido conjunto dos lotes 3k mar:

- base: **R$ 6.199,51**
- retorno anual proxy do destino de 120% CDI com CDI-modelo de 14,9% a.a.:
  - **16,8% a.a.**

Ganho terminal aproximado de **um dia adicional** de reinvestimento:

- `6199,51 * ((1 + 0,168)^(1/365) - 1) ≈ R$ 2,64`

Portanto:

- **rollover em 2026-05-04** domina **adiar para 2026-05-05** por aproximadamente **R$ 2,64** de patrimônio líquido terminal proxy até o fim da microjanela auditada.

## Conclusão

**Sim. O gate atual está escondendo um caso realmente vencedor.**

Mas não porque exista um switching genérico qualquer que o comparador não percebeu. O problema é mais específico:

- o motor/planner atual **não transforma o vencimento dos lotes 3k mar em caixa disponível** antes de comparar as ações do dia
- por isso, o comparador do switching trabalha contra um baseline economicamente inválido no pós-vencimento
- quando a semântica correta de pós-vencimento é aplicada, o caso vencedor aparece:
  - **fazer o rollover obrigatório já em 2026-05-04**
  - em vez de adiar para **2026-05-05**

## Decisão recomendada

Para a próxima etapa do projeto:

1. promover uma regra explícita de **normalização pós-vencimento** no estado diário
2. na data de vencimento, converter lotes vencidos em **caixa líquido disponível**
3. comparar os pacotes do dia usando esse estado normalizado
4. só depois decidir entre:
   - `pay_only`
   - `switch_then_pay`
   - `switch_only`

Ou seja: antes de recalibrar o gate, é preciso **corrigir a semântica do estado no pós-vencimento**.
