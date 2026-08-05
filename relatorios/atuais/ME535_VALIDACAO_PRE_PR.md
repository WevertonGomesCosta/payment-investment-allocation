# ME-535 — validação integral da implementação

## 1. Ambiente de validação

A validação foi executada pelo GitHub Actions na branch `me535-motor-temporal-funcional`, sobre a base `aa501a04ef5e8d76d387c8999f0e5d489a20e62f`.

Workflow:

```text
ME-535 motor temporal funcional — execução #12
```

## 2. Validações executadas

- compilação sintática dos quatro módulos canônicos e do validador de runtime;
- testes unitários dos pacotes normativos;
- carregamento dos dados operacionais reais versionados no repositório;
- execução das Etapas 4–11;
- geração do console oficial;
- geração do XLSX oficial;
- auditoria de paridade da Etapa 10;
- governança da Etapa 11;
- inspeção física das abas do workbook.

## 3. Resultado

```text
ME535_RUNTIME_APROVADO={
  "argmax_comprovado": true,
  "datas_auditadas": 372,
  "etapa5_pronta": true,
  "etapa6_pronta": true,
  "etapa7_pronta": true,
  "gate_motor_funcional": true,
  "etapa9_ok": true,
  "etapa10_ok": true,
  "etapa11_ok": true
}
```

## 4. Abas físicas validadas

O XLSX gerado contém exatamente:

1. `Extrato Passado`;
2. `Extrato Futuro`;
3. `Switching`;
4. `Carteira`;
5. `Situação Atual`.

## 5. Correções causais realizadas durante a validação

1. consolidação do lastro por fonte, data e pacote;
2. materialização da migração integral do saldo residual em `pay_then_switch`;
3. eliminação da duplicidade entre fonte utilizada e reserva já consumida;
4. validação das abas físicas, sem confundir blocos internos do pacote observável com worksheets.

## 6. Decisão

**Aprovado tecnicamente.**

A implementação satisfaz o contrato da ME-535 e está pronta para revisão e merge por squash.
