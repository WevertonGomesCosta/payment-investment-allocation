# Contrato Individual — Etapa 5 — Motor Temporal Conjunto

## 1. Identificação documental

- **Etapa:** 5
- **Nome:** Motor Temporal Conjunto
- **Entrada formal exclusiva:** `EstadoTemporalInicial`
- **Saída formal exclusiva:** `ResultadoMotorTemporalConjunto`
- **Módulo funcional:** `nucleo/motor_temporal_conjunto.py`
- **Função pública implementada:** `construir_resultado_motor_temporal_conjunto(...)`

## 2. Status normativo

Este contrato consolida o corpo principal da Etapa 5 e incorpora o fechamento funcional da etapa. Notas históricas anteriores permanecem apenas como referência documental e não prevalecem sobre este texto normativo.

## 3. Posição na cadeia macro

```text
Etapa 4 -> EstadoTemporalInicial -> Etapa 5 -> ResultadoMotorTemporalConjunto -> Etapa 6
```

## 4. Função da etapa

A Etapa 5 executa o motor temporal conjunto sobre o `EstadoTemporalInicial`, gerando uma trajetória temporal referencial com pacotes candidatos, valoração, seleção por data, obrigações cobertas e bloqueadas, fontes/reservas referenciais, switchings escolhidos, auditoria final e prontidão para a Etapa 6.

A Etapa 5 é a etapa responsável por decidir, no nível referencial interno, os pacotes vencedores e a trajetória temporal conjunta. Etapas posteriores não devem reotimizar nem revalorar essas decisões.

## 5. Entrada formal obrigatória e exclusiva

A entrada formal exclusiva da Etapa 5 é:

```text
EstadoTemporalInicial
```

## 6. Componentes consumíveis da entrada

A Etapa 5 pode consumir apenas componentes do `EstadoTemporalInicial`, incluindo:

- inventário temporal;
- pagamentos temporais;
- recebidos temporais;
- fontes temporais;
- switching temporal realizado;
- restrições temporais;
- elegibilidades preliminares;
- auditoria temporal;
- metadados formais preservados no estado.

## 7. Saída formal obrigatória

A saída formal obrigatória da Etapa 5 é:

```text
ResultadoMotorTemporalConjunto
```

## 8. Componentes mínimos da saída

`ResultadoMotorTemporalConjunto` deve conter, no mínimo:

- data de referência;
- horizonte temporal;
- estrutura diária referencial;
- pacotes candidatos conjuntos;
- pacotes valorados;
- pacote vencedor por data;
- trajetória temporal interna;
- eventos internos referenciais;
- obrigações cobertas temporalmente;
- obrigações bloqueadas temporalmente;
- fontes e reservas referenciais;
- switchings escolhidos temporalmente;
- auditoria final;
- `pronto_para_etapa6`.

## 9. Processo interno da etapa

A Etapa 5 deve:

1. verificar a interface contratual do `EstadoTemporalInicial`;
2. definir horizonte e índice temporal;
3. montar estrutura diária referencial;
4. gerar pacotes candidatos conjuntos;
5. valorar pacotes;
6. selecionar pacote vencedor por data;
7. aplicar trajetória temporal interna;
8. registrar eventos internos referenciais;
9. registrar obrigações cobertas;
10. registrar obrigações bloqueadas;
11. registrar fontes e reservas referenciais;
12. registrar switchings escolhidos;
13. produzir auditoria final;
14. executar fechamento funcional;
15. definir `pronto_para_etapa6`;
16. emitir `ResultadoMotorTemporalConjunto`.

## 10. O que a etapa pode fazer

A Etapa 5 pode:

- simular e valorar pacotes referenciais;
- escolher pacote vencedor por data dentro do motor temporal;
- materializar trajetória temporal interna;
- registrar decisões referenciais;
- preservar bloqueios e incompletudes;
- produzir auditoria final da trajetória.

## 11. O que a etapa não pode fazer

A Etapa 5 não pode:

- consultar planilha diretamente;
- renderizar console;
- exportar XLSX;
- produzir saída canônica final;
- executar pagamento real;
- executar switching real;
- alterar artefatos da Etapa 4;
- consultar Etapas 1–3 fora do que já estiver materializado no `EstadoTemporalInicial`;
- produzir o ledger da Etapa 6;
- produzir gates de validação da Etapa 7.

## 12. Relação com a etapa anterior

A Etapa 5 consome exclusivamente `EstadoTemporalInicial` produzido pela Etapa 4. Qualquer informação necessária deve estar materializada nesse artefato.

## 13. Relação com a etapa posterior

A Etapa 5 entrega `ResultadoMotorTemporalConjunto` para a Etapa 6 — Ledger Temporal Canônico. A Etapa 6 deve consumir o resultado sem reotimizar ou revalorar decisões.

## 14. Schema/funções públicas previstas ou implementadas

Módulo funcional:

```text
nucleo/motor_temporal_conjunto.py
```

Função pública implementada:

```python
construir_resultado_motor_temporal_conjunto(
    estado_temporal_inicial: EstadoTemporalInicial,
) -> ResultadoMotorTemporalConjunto
```

Artefato formal:

```python
ResultadoMotorTemporalConjunto
```

## 15. Auditoria esperada

A auditoria da Etapa 5 deve registrar:

- validade da interface de entrada;
- horizonte temporal utilizado;
- consistência da estrutura diária;
- pacotes candidatos e vencedores;
- obrigações cobertas e bloqueadas;
- fontes e reservas referenciais;
- switchings escolhidos;
- bloqueios finais;
- `pronto_para_etapa6`.

## 16. Critérios de aceite

A Etapa 5 é aceita quando:

1. consome somente `EstadoTemporalInicial`;
2. monta estrutura diária;
3. gera pacotes candidatos;
4. valora pacotes;
5. escolhe pacote vencedor por data;
6. materializa trajetória temporal interna;
7. registra obrigações cobertas e bloqueadas;
8. registra fontes, reservas e switchings referenciais;
9. produz auditoria final;
10. define `pronto_para_etapa6`;
11. emite `ResultadoMotorTemporalConjunto`.

## 17. Fluxograma operacional-explicativo completo

```mermaid
flowchart TD
    IN["Entrada formal<br/>EstadoTemporalInicial"] --> ORQ["nucleo/motor_temporal_conjunto.py<br/>construir_resultado_motor_temporal_conjunto(...)"]

    ORQ --> A["5A. Verificar interface contratual<br/>EstadoTemporalInicial"]
    A --> B["5B. Definir horizonte e índice temporal"]
    B --> C["5C. Montar estrutura diária referencial"]
    C --> D["5D. Gerar pacotes candidatos conjuntos"]
    D --> E["5E. Valorar pacotes referenciais"]
    E --> F["5F. Selecionar pacote vencedor por data"]
    F --> G["5G. Aplicar trajetória temporal interna"]
    G --> H["5H. Registrar eventos internos referenciais"]
    H --> I["5I. Registrar obrigações cobertas e bloqueadas"]
    I --> J["5J. Registrar fontes, reservas e switchings referenciais"]
    J --> K["5K. Auditoria final e fechamento funcional"]
    K --> L["Saída formal<br/>ResultadoMotorTemporalConjunto"]
    L --> E6["Destino<br/>Etapa 6 — nucleo/ledger_temporal_canonico.py<br/>construir_ledger_temporal_canonico(...)"]
```

## 18. Condição de parada

A Etapa 5 deve parar com bloqueio auditado quando o `EstadoTemporalInicial` não permitir montar a estrutura temporal mínima ou quando a trajetória não puder ser fechada de forma funcional.

## 19. Adendos funcionais consolidados

O fechamento funcional da Etapa 5 está incorporado ao corpo principal deste contrato. Histórico anterior deve ser lido apenas como nota documental, sem contrariar a entrada exclusiva `EstadoTemporalInicial` e a saída exclusiva `ResultadoMotorTemporalConjunto`.
