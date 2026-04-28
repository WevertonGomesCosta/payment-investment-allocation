# Relatório consolidado das validações RD — 2026-04-28

## Objetivo

Este relatório consolida as informações relevantes das rodadas documentais, estruturais, numéricas e operacionais executadas em 2026-04-28 no projeto `payment-investment-allocation`.

Ele substitui os múltiplos artefatos intermediários da pasta `relatorios/atuais/framework_execucao/`, preservando apenas os achados importantes, decisões tomadas, falhas observadas e próximos pontos técnicos relevantes.

---

## 1. Síntese executiva

| Rodada | Tema | Resultado consolidado |
|---|---|---|
| RD-01 | Validação documental/estrutural | GO documental; controles estruturais principais passaram |
| RD-02 | Validação numérica inicial | Falhou por ausência de `scipy` no ambiente |
| RD-03 | Diagnóstico pós-falha | Causa identificada: dependência `scipy` não declarada e ambiente Codex bloqueado para instalação |
| RD-04 | Correção de dependência | `scipy` formalizado no `requirements.txt` |
| RD-04A | Rastreabilidade de comandos | Comandos frágeis/placeholder corrigidos em matrizes |
| RD-05 | Gate de ambiente | Ambiente Codex continuou bloqueado por proxy/rede |
| RD-06-LCI | Validação local/CI | Execução local com `.venv` validou console e planilha |
| RD-06B | Fechamento N4/N6/N7/N8 | Restrições fechadas com observações |
| RD-07 | Metadados `None` | Corrigido mapeamento de metadados da `SITUAÇÃO ATUAL` |
| RD-07-LOCAL | Validação local RD-07 | Metadados validados localmente sem `None` |
| RD-08 | Revisão de próximas alocações | 30 pagamentos revisados; cobertura integral 30/30; 13 com switching real |
| RD-09 | Monitoramento de lotes com menor folga | Identificados lotes com baixa folga operacional |
| RD-09A | Contrato de exaustão residual | Contrato aprovado com restrições, sem implementação |
| RD-09B/C/D | Protótipos diagnósticos | Produziram candidatos, mas o processo foi considerado excessivamente diagnóstico para a etapa atual |

---

## 2. Achados importantes

### 2.1 Dependência `scipy`

| Achado | Decisão |
|---|---|
| O projeto importava `scipy`, mas a dependência não estava declarada | `scipy` foi incluído em `requirements.txt` |
| O ambiente Codex falhou ao instalar por proxy/rede | Validação numérica passou a depender do ambiente local |
| Ambiente local `.venv` conseguiu executar | Console e planilha foram validados localmente |

### 2.2 Metadados da seção `SITUAÇÃO ATUAL`

| Campo | Situação corrigida |
|---|---|
| Data de referência | Exibida corretamente |
| Status do fechamento econômico | Exibido corretamente |
| Fonte do fechamento | Exibida corretamente |
| Último fator explícito CDI | Exibido corretamente |
| Data confirmada da série | Exibida corretamente |

Causa corrigida: a saída canônica usava rótulos humanos, enquanto o console esperava chaves técnicas. A correção mapeou os rótulos para as chaves esperadas.

### 2.3 Pagamentos e alocações futuras

| Indicador | Resultado |
|---|---:|
| Pagamentos revisados na RD-08 | 30 |
| Cobertura integral | 30/30 |
| Pagamentos sem switching real | 17 |
| Pagamentos com switching real | 13 |
| Alertas de cobertura parcial | 0 |
| Alertas de lote vazio | 0 |
| Alertas de saldo negativo | 0 |

### 2.4 Lotes com menor folga

| Lote | Achado |
|---|---|
| Lote 3600 mai. | Chegou a saldo remanescente baixo, com menor valor observado de R$ 18,05 |
| Lote 3000 mar. B | Exigiu cautela porque apareceu muitas vezes como reserva, não necessariamente como fonte efetivamente consumida |
| Lote 7000 mai. | Apareceu em protótipo posterior com residual muito pequeno de R$ 5,00 |

---

## 3. O que não funcionou ou não deve ser mantido

| Item | Motivo |
|---|---|
| Muitas rodadas documentais separadas | Geraram ruído e excesso de arquivos |
| Evidências zipadas locais | Úteis temporariamente, mas não devem permanecer no repositório |
| Matrizes intermediárias de diagnóstico | Cumpriram papel temporário; informação relevante foi consolidada aqui |
| Protótipos RD-09B/RD-09C/RD-09D | Ajudaram a entender o problema, mas viraram excesso diagnóstico |
| Busca por regra simples de limpeza residual | Foi abandonada por não respeitar plenamente o objetivo de implementação do motor final |
| Avaliação candidato a candidato para resíduos de poucos reais | Considerada pouco produtiva para a próxima etapa |

---

## 4. Contrato consolidado para remanescentes residuais

A exaustão de remanescentes baixos só deve existir como parte do motor final.

Regras consolidadas:

| Regra | Decisão |
|---|---|
| Exaustão manual/ad hoc | Proibida |
| Heurística paralela fora do motor | Proibida |
| Uso de remanescente baixo em conta futura | Permitido apenas como candidato formal |
| Uso com complemento de outro lote/fonte | Permitido se respeitar o modelo |
| Cobertura integral | Obrigatória |
| Saldo negativo | Proibido |
| Liquidez/carência/fiscalidade/cronologia | Devem ser respeitadas |
| Patrimônio líquido terminal | Continua sendo função objetivo principal |
| Redução de fragmentação | Apenas critério secundário em empate ou diferença materialmente irrelevante |
| Saída auditável | Obrigatória |

---

## 5. Estado final consolidado

| Frente | Estado |
|---|---|
| Motor econômico | Preservado |
| Lógica de pagamentos | Preservada |
| Lógica de switching | Preservada |
| Função objetivo | Preservada |
| Dados oficiais | Preservados |
| Cache BCB/CDI | Preservado |
| Saída canônica | Preservada, exceto melhoria de metadados no console |
| `requirements.txt` | Atualizado com `scipy` |
| Rodadas RD | Consolidadas neste relatório |

---

## 6. Próxima etapa recomendada em novo chat

Antes de implementar qualquer nova regra, iniciar o próximo chat com o objetivo de:

1. Revisar o contrato mestre e o modelo matemático-estatístico-financeiro oficial.
2. Criar testes executáveis de aceitação do motor final.
3. Só depois implementar a exaustão residual como parte do motor oficial.
4. Não criar heurística simples, paralela ou manual.
5. Garantir que a implementação respeite patrimônio líquido terminal, pagamentos, switching e auditabilidade.

---

## 7. Prompt resumido para continuidade futura

Continuar o projeto `payment-investment-allocation` a partir do estado pós-limpeza documental.

Estado consolidado:
- `scipy` está declarado em `requirements.txt`.
- Console e planilha executaram localmente.
- Metadados `None` da `SITUAÇÃO ATUAL` foram corrigidos e validados.
- RD-08 revisou 30 próximas alocações: 30/30 com cobertura integral, 17 sem switching real e 13 com switching real.
- Lotes com baixa folga foram identificados, mas a frente de remanescentes deve seguir apenas pelo motor final.
- Não implementar regra simples nem heurística paralela.
- Próxima etapa correta: criar testes executáveis de aceitação para a futura implementação oficial de `combinacao_exaustao_residual`.

