# ME-535 — implementação do motor temporal funcional

## 1. Objetivo

Substituir a heurística referencial da Etapa 5 por uma decisão diária executável e auditável, aderente ao contrato mestre e ao modelo matemático-estatístico-financeiro oficial.

## 2. Mudança decisória

A Etapa 5 passa a construir exatamente os pacotes normativos:

- dia sem pagamento: `no_action` e `switch_only`;
- dia com pagamento: `pay_only`, `switch_then_pay` e `pay_then_switch`.

Fonte única, multifonte e uso de recebido deixam de ser tipos concorrentes de pacote e passam a ser formas internas de alocação dentro da trajetória escolhida.

## 3. Função objetivo

Cada pacote parte de uma cópia do mesmo estado inicial e produz uma trajetória completa. O pacote vencedor é escolhido por:

```text
argmax patrimônio líquido terminal líquido
```

A projeção terminal considera:

- saldo líquido disponível por fonte;
- retorno anual proxy materializado no estado;
- vencimento da fonte;
- carência e disponibilidade;
- incidência de IR sobre ganho futuro;
- aproximação monotônica do IOF regressivo quando aplicável;
- ticket mínimo e máximo do destino;
- conservação do valor líquido migrado;
- cobertura integral das obrigações do dia.

O desempate determinístico usa, nesta ordem:

1. menor número de switchings;
2. menor número de fontes usadas no pagamento;
3. identificador estável do pacote.

## 4. Estado e trajetória

O motor é stateful entre datas. Recebidos e fontes futuras são ativados somente na data de disponibilidade. O saldo final do pacote vencedor torna-se o estado inicial da data seguinte.

Cada data registra:

- estado inicial identificável;
- pacotes permitidos e avaliados;
- patrimônio terminal de cada pacote factível;
- pacote vencedor;
- prova de `argmax`;
- alocações por obrigação e fonte;
- switchings materializados na trajetória;
- saldos finais.

## 5. Gates obrigatórios

A Etapa 7 passa a bloquear a progressão quando faltar qualquer uma das evidências abaixo:

- motor funcional declarado;
- conjunto normativo completo de pacotes;
- comparação a partir do mesmo estado;
- prova do `argmax`;
- cobertura integral das obrigações;
- resultado terminal numérico;
- matriz econômica por data e pacote;
- aderência terminal.

A ausência de evidência deixa de ser tratada apenas como aviso.

## 6. Compatibilidade controlada

Os módulos legados permanecem preservados como implementação histórica. Pacotes Python com os mesmos nomes públicos carregam as estruturas legadas e substituem apenas os construtores canônicos da Etapa 4, Etapa 5, Etapa 6 e Etapa 7. Essa ponte permite manter os contratos de tipos consumidos pelas Etapas 6–11 enquanto a decisão passa ao motor funcional.

## 7. Testes adicionados

A bateria mínima cobre:

1. `switch_only` vencedor em dia sem pagamento;
2. comparação dos três pacotes em dia com pagamento;
3. `pay_then_switch` vencedor quando há saldo residual e destino superior;
4. bloqueio quando não existe cobertura;
5. identidade comum do estado inicial entre os pacotes concorrentes.

## 8. Limites explícitos

- O motor não executa operações bancárias reais.
- O retorno dos produtos continua usando a proxy econômica oficial já materializada pelo ranking.
- Valores de resgate disponíveis entram como líquidos; o custo fiscal já realizado para obter esse líquido não é contado novamente.
- IR e IOF da projeção terminal incidem somente sobre o ganho futuro simulado.
- O IOF futuro usa uma aproximação monotônica nesta frente; a substituição pela tabela diária exata deve ocorrer em frente fiscal própria antes da homologação econômica final.
- Produtos com retorno proxy ausente são tratados com retorno zero, evitando ganho inventado.
- A saída observável continua não decisória; console e XLSX não participam da escolha do pacote.

## 9. Critério de aceite

A frente é aceita quando:

- todos os testes unitários passam;
- `py_compile` passa nos módulos novos;
- o runtime real produz `pronto_para_etapa6=True`;
- os gates aprovam `gate_motor_funcional`;
- Etapas 9, 10 e 11 permanecem aprovadas;
- diferenças econômicas são explicáveis pela matriz por data/pacote, sem calibração na renderização.

## 10. Regra de merge

O PR deve permanecer em draft até a execução completa abaixo ser aprovada no ambiente com os dados reais:

```bash
python -m unittest tests/test_motor_temporal_funcional.py
python aplicacao/principal.py
```

O merge é proibido se qualquer uma das condições abaixo ocorrer:

- pacote normativo ausente em qualquer data;
- `argmax_comprovado=False`;
- obrigação obrigatória bloqueada sem prova de inviabilidade;
- `gate_motor_funcional` reprovado;
- Etapa 9, 10 ou 11 reprovada;
- alteração econômica originada em console, XLSX ou `Situação Atual`.
