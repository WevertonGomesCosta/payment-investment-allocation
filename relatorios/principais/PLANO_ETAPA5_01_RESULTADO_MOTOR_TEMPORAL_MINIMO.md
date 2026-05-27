# PLANO DA ME-ETAPA5-01 — RESULTADO MOTOR TEMPORAL MÍNIMO

## 1. Status

Este documento planeja a primeira implementação funcional mínima da **Etapa 5 — Motor temporal conjunto**, limitada ao artefato `ResultadoMotorTemporalMinimo`.

Esta microetapa é **DOCUMENTAL / PLANEJAMENTO**.

Não implementa código funcional.

Não altera motor temporal, ledger, saída canônica, console, XLSX, dados ou regras econômicas.

---

## 2. Baseline normativa

A ME-ETAPA5-01 parte da `main` após merge da PR #402, que criou o contrato específico:

`relatorios/principais/CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md`

Esse contrato definiu:

- `EstadoTemporalInicial` como entrada formal obrigatória da Etapa 5;
- `ResultadoMotorTemporalMinimo` como artefato mínimo futuro da primeira implementação funcional;
- proibição de ledger oficial, decisão econômica completa, console e XLSX nessa primeira abertura funcional.

---

## 3. Objetivo da próxima implementação funcional

A próxima microetapa funcional, posterior a este planejamento, deve criar apenas a estrutura mínima necessária para consumir `EstadoTemporalInicial` e retornar um `ResultadoMotorTemporalMinimo` auditável.

O objetivo não é decidir pagamentos, escolher fontes, promover switchings ou gerar saídas finais.

O objetivo é organizar a primeira representação temporal conjunta mínima, com rastreabilidade suficiente para validar a entrada da Etapa 5 e preparar o motor decisório futuro.

---

## 4. Escopo funcional permitido para a próxima microetapa

A próxima microetapa funcional poderá:

1. criar um tipo, classe, dataclass ou estrutura equivalente para `ResultadoMotorTemporalMinimo`;
2. criar uma função mínima de construção do resultado a partir de `EstadoTemporalInicial`;
3. validar presença dos componentes mínimos do `EstadoTemporalInicial`;
4. organizar pagamentos temporais por data;
5. organizar recebidos temporais por data;
6. organizar fontes temporais por disponibilidade preliminar;
7. preservar inventário temporal como estrutura de estado;
8. preservar switchings temporais realizados como eventos observados;
9. registrar bloqueios temporais básicos sem decisão econômica final;
10. registrar status de cobertura preliminar sem consumo de fonte;
11. retornar uma estrutura auditável em memória;
12. manter rastreabilidade dos campos consumidos da entrada.

---

## 5. Escopo funcional proibido

A próxima microetapa funcional não poderá:

- escolher fonte ótima final;
- selecionar lote de pagamento;
- selecionar combinação mínima de fontes;
- executar pagamento;
- liquidar conta;
- escolher pacote vencedor;
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
- alterar ranking da Carteira;
- alterar regras econômicas;
- usar saída observável como fonte de estado;
- usar log histórico como norma viva;
- usar diagnóstico como motor auxiliar;
- criar fallback legado;
- criar wrapper transitório;
- criar rota paralela;
- criar sentinela;
- criar script diagnóstico;
- reintroduzir `ContextoBaseline`;
- reintroduzir `ContextoSaidaCanonicaCompat`.

---

## 6. Arquivos preferenciais para a próxima microetapa funcional

A próxima microetapa funcional deve alterar o menor número possível de arquivos.

Arquivos ou áreas candidatos, sujeitos a inspeção prévia:

- `nucleo/estado_temporal_inicial.py`, apenas se for necessário importar ou tipar a entrada já existente;
- novo módulo em `nucleo/`, com nome claro associado ao motor temporal mínimo, se não houver módulo canônico existente;
- testes ou validações existentes, se já houver estrutura de teste compatível.

Antes de criar arquivo novo, deve-se verificar se já existe módulo canônico para motor temporal ou resultado temporal mínimo.

É proibido criar script diagnóstico em `scripts/diagnostico/`.

---

## 7. Estrutura mínima recomendada do artefato

O `ResultadoMotorTemporalMinimo` deve conter, no mínimo:

- `data_referencia`;
- `horizonte_avaliado`;
- `pagamentos_por_data`;
- `recebidos_por_data`;
- `fontes_disponiveis_preliminares`;
- `fontes_indisponiveis_preliminares`;
- `inventario_temporal_resumido`;
- `switchings_realizados_observados`;
- `dias_simulaveis`;
- `bloqueios_temporais_basicos`;
- `status_cobertura_preliminar`;
- `auditoria_consumo_estado_temporal_inicial`;
- `avisos_nao_decisorios`.

Os nomes finais podem ser ajustados na implementação, desde que a semântica contratual seja preservada.

---

## 8. Status de cobertura preliminar

O status de cobertura preliminar deve ser estrutural.

Ele pode indicar, por data, se há obrigações e se existem fontes temporalmente disponíveis em sentido preliminar.

Ele não pode indicar fonte escolhida, lote usado, combinação ótima, pacote vencedor ou pagamento executado.

---

## 9. Tratamento de switchings na primeira implementação funcional

Na próxima microetapa funcional, switchings só podem ser preservados como eventos observados quando já presentes em `switching_temporal_realizado` dentro do `EstadoTemporalInicial`.

Não se deve gerar, ranquear, promover ou executar novo switching.

---

## 10. Tratamento de pagamentos na primeira implementação funcional

Pagamentos devem permanecer como obrigações temporais.

A implementação pode agrupá-los por data e registrar cobertura preliminar estrutural.

A implementação não pode executar pagamento, consumir fonte, calcular imposto de saque decisório ou gerar saldo remanescente por decisão do motor.

---

## 11. Tratamento de fontes na primeira implementação funcional

Fontes podem ser classificadas preliminarmente como disponíveis ou indisponíveis conforme campos já presentes no `EstadoTemporalInicial`.

Essa classificação não autoriza consumo, seleção ótima ou alteração de saldo.

---

## 12. Validação mínima esperada da próxima microetapa funcional

A próxima microetapa funcional deverá validar, no mínimo:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
```

Se houver testes automatizados já existentes compatíveis, eles poderão ser executados sem criar nova infraestrutura paralela.

O diff deverá ser restrito ao menor conjunto de arquivos funcionais necessários e ao log da microetapa.

---

## 13. Critério de parada

A implementação funcional mínima deve parar se surgir necessidade de:

- decidir pagamento;
- escolher fonte;
- promover switching;
- criar ledger;
- alterar saída canônica;
- alterar console;
- alterar XLSX;
- criar diagnóstico auxiliar;
- reconstruir estado a partir de renderização.

Nesses casos, uma nova microetapa contratual ou funcional específica deverá ser aberta antes de continuar.

---

## 14. Resultado esperado deste planejamento

Este planejamento autoriza apenas a preparação da próxima microetapa funcional mínima, com escopo controlado e sem abertura de decisão econômica completa.
