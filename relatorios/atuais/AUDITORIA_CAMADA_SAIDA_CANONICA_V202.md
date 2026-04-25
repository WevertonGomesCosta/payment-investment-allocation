# AUDITORIA E IMPLEMENTAÇÃO — CAMADA ÚNICA DE SAÍDA CANÔNICA V202

## 1. Decisão aplicada

A V202 deriva da V201 e cria a primeira camada única de saída canônica do repositório, sem alterar o motor econômico, o contrato mestre ou o modelo matemático-estatístico-financeiro.

## 2. Escopo implementado

- Criação de `nucleo/saida_canonica.py`.
- Materialização única de:
  - Extrato Passado;
  - Extrato Futuro;
  - Switching;
  - amostra do ranking;
  - Situação Atual;
  - auditoria mínima da própria camada de saída.
- Refatoração do console para consumir `PacoteSaidaCanonica`.
- Refatoração da geração da planilha operacional para consumir `PacoteSaidaCanonica`.
- Restauração dos caminhos canônicos de `scripts/` e `saidas/oficial/` que estavam documentados na V201, mas não vieram íntegros no pacote recebido.
- Atualização da identidade operacional para V202.

## 3. Regra arquitetural consolidada

A partir da V202, renderizadores não devem recalcular saldos, líquidos, impostos, residuais, switchings ou amostras financeiras.

A regra operacional passa a ser:

```text
motor/contexto → nucleo.saida_canonica.construir_saida_canonica(...) → console/.xlsx/JSON/CSV/Markdown
```

Qualquer nova saída deve consumir a camada canônica ou ser explicitamente classificada como diagnóstico histórico sem autoridade operacional.

## 4. O que não foi alterado

- Contrato mestre.
- Modelo matemático-estatístico-financeiro.
- Núcleo econômico.
- Regras de pagamentos.
- Regras de switching.
- Tratamento metodológico dos aportes/recebidos futuros ainda não aplicados em carteira.

## 5. Limite da V202

A V202 não resolve o problema metodológico pendente dos aportes/recebidos futuros não aportados. Esse ponto permanece reservado para etapa posterior, porque altera o estado econômico prospectivo e deve ser implementado depois da estabilização da observabilidade.

## 6. Validações mínimas esperadas

- `python aplicacao/principal.py`
- `python scripts/verificar_release_baseline.py`

Critérios mínimos:

- console executa consumindo `saida_canonica_v202`;
- planilha oficial `relatorio_operacional_v202.xlsx` é gerada;
- aba `Saida Canonica` registra contagens e cobertura;
- `Extrato Futuro` e console usam a mesma origem materializada;
- release checker valida a presença da camada canônica.


## 7. Validação executada nesta entrega

Validação executada com rede desabilitada em memória para forçar fallback local de planilha e CDI, sem alterar configuração do repositório.

Resultados observados:

| Item | Resultado |
|---|---:|
| `relatorio_operacional_v202.xlsx` gerado | sim |
| Abas oficiais geradas | 9 |
| Linhas em `Extrato Passado` | 49 |
| Linhas em `Extrato Futuro` | 149 |
| Linhas em `Switching` | 4 |
| Contas futuras sem cobertura integral | 0 |
| Linhas futuras multifonte | 3 |
| Lotes ativos na Situação Atual | 4 |
| Lotes exauridos na Situação Atual | 12 |
| Console contém marcador `saida_canonica_v202` | sim |
| Release checker | OK |

## 8. Observação sobre a V201 empacotada

Durante a abertura da V202, foi identificado que o pacote V201 recebido continha documentação sobre `scripts/` e `saidas/oficial/`, mas esses caminhos não estavam íntegros no `.zip`.

A V202 restaura os caminhos canônicos compatíveis com o manifesto V201 antes de aplicar a camada única de saída. Essa restauração é estrutural e não altera o motor econômico.
