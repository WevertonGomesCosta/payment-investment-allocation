# CONTRATO DA ETAPA 5 — MOTOR TEMPORAL CONJUNTO

## 1. Status normativo

Este documento define o contrato específico mínimo da **Etapa 5 — Motor temporal conjunto** do projeto `payment-investment-allocation`.

Este contrato é subordinado ao contrato operacional mestre e ao modelo matemático-estatístico-financeiro oficial. Em caso de divergência, prevalecem:

1. contrato operacional mestre;
2. modelo matemático-estatístico-financeiro oficial;
3. este contrato específico da Etapa 5;
4. evidências de validação compatíveis;
5. logs históricos, sem autonomia normativa.

Este documento não implementa motor temporal, não altera decisão econômica, não cria ledger oficial e não altera saídas observáveis.

---

## 2. Nome da etapa

A etapa normatizada por este documento é:

**Etapa 5 — Motor temporal conjunto**.

Sua função é evoluir o `EstadoTemporalInicial` para uma estrutura temporal conjunta, auditável e preparada para futuras decisões econômicas completas, respeitando a separação entre estado, motor, ledger, saída canônica, console e XLSX.

---

## 3. Entrada formal obrigatória

A entrada formal obrigatória da Etapa 5 é:

`EstadoTemporalInicial`

A Etapa 5 deve consumir esse artefato diretamente.

É vedado reconstruir a entrada da Etapa 5 a partir de:

- console;
- XLSX;
- saída observável;
- markdowns renderizados;
- relatórios históricos;
- logs de iteração;
- scripts diagnósticos;
- CSVs auxiliares;
- artefatos de auditoria pós-saída;
- qualquer rota paralela ou compatível não normativa.

---

## 4. Componentes mínimos consumidos da entrada

A primeira abertura funcional da Etapa 5 deve reconhecer, no mínimo, os seguintes componentes do `EstadoTemporalInicial`:

- `pagamentos_temporais`;
- `recebidos_temporais`;
- `fontes_temporais`;
- `inventario_temporal`;
- `switching_temporal_realizado`;
- restrições temporais;
- elegibilidades temporais preliminares;
- auditoria temporal.

Esses componentes devem ser tratados como estruturas de estado e não como saída observável.

---

## 5. Separação obrigatória entre camadas

A Etapa 5 deve preservar separação estrita entre:

1. `EstadoTemporalInicial`;
2. motor temporal conjunto;
3. ledger canônico;
4. saída canônica;
5. console;
6. XLSX.

O `EstadoTemporalInicial` é entrada.

O motor temporal conjunto é camada de transformação e simulação temporal.

O ledger canônico será, em etapa funcional posterior e explicitamente contratada, a fonte oficial de eventos do pacote escolhido.

A saída canônica será derivada somente após ledger e estado temporal final validados.

Console e XLSX são renderizações finais de conferência e validação humana, nunca fontes de estado ou decisão.

---

## 6. Artefato mínimo de saída da primeira implementação funcional

A primeira implementação funcional da Etapa 5, quando aberta em microetapa posterior, deve produzir apenas um artefato mínimo de simulação temporal, denominado:

`ResultadoMotorTemporalMinimo`

Esse artefato é preparatório. Ele não é ledger oficial, não é saída canônica final e não representa decisão econômica completa.

---

## 7. Conteúdo permitido do `ResultadoMotorTemporalMinimo`

O `ResultadoMotorTemporalMinimo` poderá conter, no mínimo:

- data de referência;
- horizonte avaliado;
- obrigações temporais consideradas;
- fontes temporais disponíveis;
- fontes temporais indisponíveis;
- eventos temporais observados;
- estrutura inicial de dias simuláveis;
- bloqueios temporais básicos;
- status de cobertura preliminar;
- rastreabilidade mínima até o `EstadoTemporalInicial`;
- auditoria estrutural de consumo da entrada.

Esse artefato deve indicar explicitamente quando uma informação é:

- estado consumido;
- estrutura temporal organizada;
- bloqueio preliminar;
- evidência de auditoria;
- campo ainda não decisório.

---

## 8. Escopo permitido da primeira implementação funcional

A primeira implementação funcional da Etapa 5 poderá apenas:

- consumir diretamente o `EstadoTemporalInicial`;
- validar presença estrutural dos componentes mínimos de entrada;
- construir esqueleto temporal conjunto;
- organizar dias simuláveis;
- organizar obrigações temporais por data;
- organizar fontes temporais por disponibilidade preliminar;
- preservar switchings já realizados como eventos observados quando presentes na entrada;
- preservar rastreabilidade dos componentes consumidos;
- registrar bloqueios temporais básicos;
- retornar o `ResultadoMotorTemporalMinimo` como estrutura mínima auditável.

Essa primeira implementação não poderá ser promovida como motor decisório completo.

---

## 9. Proibições explícitas da primeira implementação funcional

A primeira implementação funcional da Etapa 5 não pode:

- escolher fonte ótima final;
- executar pagamento;
- liquidar conta;
- escolher pacote vencedor do dia;
- decidir switching candidato;
- promover switching candidato;
- executar switching novo;
- materializar novo lote pós-switching;
- recalcular saldos como decisão econômica final;
- criar ledger oficial;
- criar saída canônica final;
- alterar console;
- alterar XLSX;
- alterar dados;
- alterar planilha operacional;
- alterar regras econômicas;
- usar saída observável como fonte de estado;
- usar log histórico como norma viva;
- usar diagnóstico como motor auxiliar;
- criar fallback legado;
- criar wrapper transitório;
- criar rota paralela;
- reintroduzir `ContextoBaseline`;
- reintroduzir `ContextoSaidaCanonicaCompat`.

---

## 10. Relação com switching

Na primeira implementação funcional, switchings devem ser tratados apenas quando já constarem no `EstadoTemporalInicial` como switchings temporais realizados ou eventos observados.

É vedado, nessa primeira abertura funcional:

- gerar novo candidato de switching;
- ranquear destino de switching como decisão final;
- promover candidato;
- converter oportunidade em lote operacional;
- usar produto destino como fonte de pagamento;
- inferir switching a partir de console, XLSX ou saída observável.

A avaliação econômica de novos switchings pertence a microetapa funcional posterior e deve ser contratada explicitamente.

---

## 11. Relação com pagamentos

Na primeira implementação funcional, pagamentos devem ser tratados como obrigações temporais organizadas por data.

É vedado, nessa primeira abertura funcional:

- selecionar lote de pagamento;
- selecionar combinação mínima de fontes;
- executar pagamento;
- marcar conta como liquidada por decisão do motor;
- produzir ledger de pagamento;
- alterar saldo remanescente por consumo de fonte.

O status de cobertura permitido nessa fase é preliminar e estrutural, sem decisão econômica final.

---

## 12. Relação com ledger, saída canônica, console e XLSX

A primeira implementação funcional da Etapa 5 não cria ledger oficial.

A primeira implementação funcional da Etapa 5 não cria saída canônica final.

A primeira implementação funcional da Etapa 5 não altera console.

A primeira implementação funcional da Etapa 5 não altera XLSX.

Console, XLSX e saída observável permanecem renderizações ou conferências humanas, não fontes de estado, decisão ou reconstrução temporal.

---

## 13. Critério mínimo de aceite da primeira implementação funcional futura

Uma implementação funcional posterior baseada neste contrato só poderá ser aceita se:

1. consumir `EstadoTemporalInicial` diretamente;
2. não reconstruir estado a partir de renderizações;
3. preservar os componentes mínimos de entrada;
4. produzir `ResultadoMotorTemporalMinimo`;
5. manter pagamentos como obrigações temporais ainda não executadas;
6. manter fontes como estrutura temporal ainda não consumida por decisão final;
7. manter switchings realizados apenas como eventos observados quando já constarem na entrada;
8. não criar ledger oficial;
9. não criar saída canônica final;
10. não alterar console;
11. não alterar XLSX;
12. não alterar dados;
13. não promover decisão econômica completa.

---

## 14. Condição de parada

Qualquer necessidade de escolher fonte ótima, executar pagamento, promover switching, criar ledger oficial, gerar saída canônica final, alterar console ou alterar XLSX deve interromper a microetapa funcional mínima e exigir novo contrato específico antes de implementação.

---

## 15. Status deste contrato

Este contrato abre apenas a base normativa mínima da Etapa 5.

Ele autoriza uma próxima microetapa funcional limitada ao `ResultadoMotorTemporalMinimo`, desde que a implementação respeite integralmente as proibições acima.
