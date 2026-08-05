# ME-535R — Bloco 1: estado econômico canônico e conservação patrimonial

## 1. Identificação

- **Branch:** `me535r-motor-economico-canonico`.
- **Natureza:** implementação estrutural pré-decisória.
- **Altera motor econômico:** não.
- **Altera função objetivo:** não.
- **Altera contrato ou modelo:** não.
- **Altera ledger, console operacional ou XLSX:** não.
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

A seleção de pacotes, o `argmax`, o ledger decisório e a integração ao motor permanecem fora desta alteração.

## 3. Problemas bloqueados

O novo artefato impede explicitamente:

- reutilização de recebido já aplicado;
- reutilização de recebido consumido ou vinculado sem residual explícito;
- recuperação do `valor_original` por lote com saldo atual zero;
- antecipação de snapshot futuro para a data de referência;
- soma de linhas repetidas da mesma fonte;
- permanência da origem de switching como fonte disponível;
- criação de valor em switching interno;
- uso de identidade econômica ambígua ou duplicada;
- permanência de saldo atual em lotes migrados ou estados encerrados;
- duplicação do prefixo canônico de identidade de recebidos.

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

O fechamento complementar exige:

```text
valor total das unidades atuais
=
valor total disponível canônico
+
valor total bloqueado não disponível
+
valor dos estados encerrados
```

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

O validador publica separadamente:

- bloqueios e avisos do `EstadoEconomicoCanonico`;
- resultado da validação pré-execução;
- janela de consulta CDI;
- auditoria do cache CDI;
- proveniência Git e hashes dos arquivos de entrada.

Saída diagnóstica:

```text
saidas/diagnostico/estado_economico_canonico_bloco1.json
```

### Testes

```text
tests/test_estado_economico_canonico.py
tests/test_estado_economico_canonico_fechamento.py
```

Comando:

```bash
python -m unittest -v \
  tests.test_estado_economico_canonico \
  tests.test_estado_economico_canonico_fechamento
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
10. fechamento do total canônico com as fontes materializadas;
11. cadeia de switching conservando apenas o destino final;
12. lote migrado sem saldo líquido atual;
13. recebido aplicado e usado antes com evidências independentes;
14. identidade de recebido já prefixada sem duplicação do prefixo.

## 9. Homologação sobre os dados reais

### 9.1. Commit dos dados homologados

```text
72fbeacc9753f466a67eb537f36b46828bfe7cc1
```

### 9.2. Arquivos de entrada

```text
dados/dados_financeiros.xlsx
sha256 = 73951e210e272b9512d75fdd4e4bb1265cca11bb6a9a5a0a4dd179ff232d7ce5
tamanho = 170554 bytes

dados/cache_bcb.json
sha256 = b762dcb0069b39f19ce8e10b8f3e13aee5e62d73a1f5f60987321f28e9f6c559
tamanho = 15684 bytes
```

A validação registrou:

```text
dados_entrada_modificados_localmente = false
status_git_arquivos_entrada = []
```

### 9.3. Resultado dos testes

```text
Ran 14 tests
OK
```

### 9.4. Resultado econômico

```text
ok = true
bloqueios = []
avisos_estado_economico = []

diferenca_conservacao_fontes = 0.0
diferenca_conservacao_unidades_vivas = 0.0
valor_estados_encerrados = 0.0
valor_total_bloqueado_nao_disponivel = 0.0

valor_lotes_disponiveis = 24481.45
valor_recebidos_disponiveis = 0.0
valor_total_disponivel_canonico = 24481.45
valor_total_fontes_materializadas = 24481.45
valor_total_unidades_atuais = 24481.45
```

Também foram confirmados:

```text
qtd_lotes_migrados_zerados = 8
qtd_lotes_zerados_nao_ressuscitados = 17
qtd_recebidos_aplicados_excluidos = 32
qtd_recebidos_usados_antes_aplicacao_excluidos = 2
qtd_recebidos_vinculados_excluidos = 19
qtd_snapshots_futuros_ignorados = 3916
```

## 10. Esclarecimento sobre o recebimento de R$ 5.680,00

A diferença entre o total anterior de R$ 30.161,45 e o total homologado de R$ 24.481,45 não representa desaparecimento patrimonial.

A data de recebimento de `recebido::salario_auto_00027` foi alterada na planilha para `2026-08-07`. Como a data de referência da homologação é `2026-08-05`, o recebido está corretamente classificado como futuro e não integra as fontes disponíveis.

As duas execuções utilizaram bases diferentes e não constituem comparação temporal válida.

## 11. Auditoria da janela e do cache CDI

A janela foi derivada dos dados operacionais, sem truncamento arbitrário:

```text
data_referencia = 2026-08-05
menor_data_identificada = 2026-01-02
maior_data_identificada = 2026-08-05
data_inicial_consulta = 2026-01-01
data_final_consulta = 2026-08-05
fontes_que_definiram_inicio = despesas.data, salarios.data_recebimento
```

A série efetivamente carregada contém:

```text
quantidade = 146
primeira_data = 2026-01-02
ultima_data = 2026-08-03
fonte_serie_cdi = cache_local
fetch_status = cache_atualizado_sem_fetch
cache_atualizado_para_referencia = true
```

A validação pré-execução retornou:

```text
ok = true
erros_bloqueantes = []
avisos =
- Última data da série CDI é anterior à data de referência.
- Série CDI começa após data_inicial_consulta da JanelaConsultaCDI.
```

Classificação para o Bloco 1:

1. o aviso inicial é esperado porque a janela é normalizada para o primeiro dia do mês, enquanto a primeira data operacional e a primeira observação da série são `2026-01-02`;
2. o aviso final registra a defasagem entre a data de referência e a última observação materializada no cache;
3. nenhum dos avisos invalida as invariantes econômicas do Bloco 1;
4. os avisos não devem ser ocultados nem confundidos com `avisos_estado_economico=[]`;
5. antes de o Bloco 2 depender de valoração diária prospectiva, a suficiência temporal do CDI deverá ter gate próprio para distinguir dias sem observação, defasagem admissível e ausência material de fator requerido.

## 12. Limites preservados

Esta alteração não conecta o novo artefato ao motor da `main`.

O Bloco 1 não altera silenciosamente:

- pagamentos;
- switchings;
- seleção de pacote;
- ledger;
- console operacional;
- XLSX;
- ranking;
- função objetivo.

A integração futura não poderá reconstruir saldo, reintroduzir fontes legadas nem alterar o estado canônico na camada decisória.

## 13. Critérios de aprovação

- 14 testes aprovados;
- validador real com `ok=true`;
- diferenças de conservação iguais a zero;
- estados encerrados com saldo atual zero;
- nenhum recebido aplicado ou vinculado disponível sem residual explícito;
- nenhum lote zerado recuperando `valor_original`;
- nenhum snapshot futuro antecipado;
- nenhuma identidade conflitante;
- dados e cache versionados com hashes;
- working tree dos arquivos de entrada limpo;
- janela CDI explicada por fontes operacionais identificadas;
- avisos da entrada separados dos avisos do estado econômico;
- diagnóstico físico publicado para auditoria.

## 14. Decisão de fechamento

O Bloco 1 está aprovado quanto a:

- identidade econômica;
- ciclo de vida;
- conservação patrimonial;
- fechamento de estados encerrados;
- switching conservativo;
- exclusão de recursos já usados;
- não antecipação de valores futuros;
- reprodutibilidade dos dados homologados.

A PR pode avançar para revisão após a reexecução do validador atualizado e a confirmação de que:

```text
avisos_estado_economico = []
validacao_pre_execucao.ok = true
validacao_pre_execucao.erros_bloqueantes = []
dados_entrada_modificados_localmente = false
```

## 15. Próxima etapa após o merge

A evolução deve ocorrer em blocos separados:

1. conectar controladamente `EstadoEconomicoCanonico` como entrada única do motor;
2. implementar o Bloco 2 — geração de pacotes factíveis, decisão econômica e verificador independente;
3. impedir que o motor reconstrua fontes a partir das estruturas legadas;
4. manter o Bloco 1 imutável como gate de entrada econômica;
5. somente depois avançar para ledger, gates finais e homologação de saída.
