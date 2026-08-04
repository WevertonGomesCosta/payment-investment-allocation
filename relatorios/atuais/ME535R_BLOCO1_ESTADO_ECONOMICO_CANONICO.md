# ME-535R — Bloco 1: estado econômico canônico e conservação patrimonial

## 1. Identificação

- **Branch:** `me535r-motor-economico-canonico`.
- **Natureza:** implementação estrutural pré-decisória.
- **Altera motor econômico:** não.
- **Altera função objetivo:** não.
- **Altera contrato ou modelo:** não.
- **Altera console ou XLSX:** não.
- **Cria rota shadow ou fallback:** não.
- **Novo artefato:** `EstadoEconomicoCanonico`.

## 2. Objetivo

Materializar uma fonte econômica única para cada unidade monetária observada no estado temporal, impedindo que representações duplicadas sejam somadas como patrimônio disponível.

O Bloco 1 trata exclusivamente:

1. identidade de recebidos e lotes;
2. ciclo de vida econômico;
3. saldo líquido atual;
4. disponibilidade na data de referência;
5. transferências internas por switching;
6. reconciliação das fontes declaradas;
7. conservação patrimonial.

A seleção de pacotes e o `argmax` permanecem fora desta alteração.

## 3. Problemas bloqueados

O novo artefato impede explicitamente:

- reutilização de recebido já aplicado;
- reutilização de recebido consumido ou vinculado sem residual explícito;
- recuperação do `valor_original` por lote com saldo atual zero;
- antecipação de snapshot futuro para a data de referência;
- soma de linhas repetidas da mesma fonte;
- permanência da origem de switching como fonte disponível;
- criação de valor em switching interno;
- uso de identidade econômica ambígua ou duplicada.

## 4. Regra de precedência de valores

### 4.1. Lotes

O saldo atual só pode vir de campos de saldo líquido atual:

```text
valor_liquido_disponivel_atual
saldo_disponivel_atual
valor_liquido_disponivel
saldo_disponivel
saldo_atual
```

É proibido usar como saldo atual:

```text
valor_original
investimento_bruto
```

Para lote sintético pós-switching ainda sem outro saldo materializado, o `valor_liquido_migrado` pode criar a posição inicial do destino.

### 4.2. Recebidos

A ordem é:

1. residual explícito, quando disponível;
2. zero para recebido aplicado, consumido ou vinculado sem residual explícito;
3. valor total somente para recebido materializado e explicitamente disponível.

## 5. Estados de ciclo de vida

### Lotes

- `futuro_nao_materializado`;
- `migrado_por_switching`;
- `exaurido_sem_saldo_atual`;
- `ativo_bloqueado_carencia`;
- `ativo_disponivel`;
- estados indisponíveis preservados da origem.

### Recebidos

- `futuro_nao_materializado`;
- `aplicado_em_lote`;
- `consumido_ou_vinculado`;
- `residual_disponivel`;
- `caixa_disponivel`;
- `exaurido_sem_saldo_atual`;
- `bloqueado_sem_disponibilidade_explicita`.

## 6. Conservação

O estado canônico exige:

```text
valor total das unidades disponíveis
=
valor total das fontes canônicas materializadas
```

com tolerância de R$ 0,01.

Switching materializado é registrado como transferência interna:

```text
valor de saída da origem
=
valor de entrada no destino
```

Impostos ou custos futuros deverão ser informados explicitamente; não podem aparecer como criação ou destruição implícita de patrimônio.

## 7. Artefatos

### Código

```text
nucleo/estado_economico_canonico.py
```

### Validação dos dados reais

```text
scripts/validacao/validar_bloco1_estado_economico_canonico.py
```

Comando:

```bash
python -B scripts/validacao/validar_bloco1_estado_economico_canonico.py
```

Saída diagnóstica:

```text
saidas/diagnostico/estado_economico_canonico_bloco1.json
```

### Testes

```text
tests/test_estado_economico_canonico.py
```

Comando:

```bash
python -m unittest -v tests.test_estado_economico_canonico
```

## 8. Casos adversariais cobertos

1. recebido aplicado e lote correspondente;
2. recebido usado antes da aplicação;
3. lote zerado com `valor_original` positivo;
4. snapshot futuro marcado como disponível;
5. switching com retirada da origem e criação do destino;
6. lote sintético pós-switching;
7. residual explícito de recebido;
8. identidade duplicada conflitante;
9. linhas repetidas da mesma fonte;
10. fechamento do total canônico com as fontes materializadas.

## 9. Limites preservados

Esta alteração não conecta o novo artefato ao motor da `main`. A conexão só será autorizada após:

- aprovação dos testes adversariais;
- aprovação da validação sobre os dados reais;
- inspeção do JSON diagnóstico;
- confirmação de que os bloqueios da PR #553 foram eliminados no estado econômico.

Assim, o Bloco 1 não muda silenciosamente pagamentos, switchings, ledger, console ou XLSX antes de a nova fonte de verdade ser comprovada.

## 10. Critérios de aprovação

- todos os testes passam;
- validador real retorna `ok=true`;
- diferença de conservação das fontes igual a zero dentro de R$ 0,01;
- nenhum recebido aplicado ou consumido permanece disponível sem residual explícito;
- nenhum lote zerado recupera `valor_original`;
- nenhum snapshot futuro é antecipado;
- nenhuma identidade conflitante permanece;
- diagnóstico físico é publicado para auditoria.

## 11. Próxima etapa após aprovação

A próxima alteração será a conexão controlada do `EstadoEconomicoCanonico` à entrada do motor, seguida da implementação do Bloco 2. Essa conexão não deverá reconstruir saldo, reintroduzir fontes legadas nem alterar o estado canônico na camada decisória.
