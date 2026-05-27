# CONTRATO INDIVIDUAL DA ETAPA 1 — PACOTEENTRADARESOLVIDA

> Cópia canônica derivada do documento-fonte já existente:
>
> `logs/iteracoes/ME-V17-F0-V32A_FORMALIZA_ETAPA1_PACOTE_ENTRADA_RESOLVIDA.md`
>
> O documento original permanece preservado como log histórico. Esta cópia organiza o mesmo contrato individual na pasta canônica `relatorios/principais/contratos_individuais/`.

## 1. Identificação do documento-fonte

- MICROETAPA: V17-F0-V.3.2A
- TIPO: DOCUMENTAL / ARQUITETURAL
- CLASSE: FORMALIZA_ETAPA1_COMO_PACOTE_ENTRADA_RESOLVIDA
- ALTERA CÓDIGO: NÃO
- ALTERA MOTOR: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA DADOS: NÃO
- ALTERA CACHE: NÃO
- ALTERA RENDERIZAÇÃO: NÃO

## 2. Problema motivador

A Etapa 1 ainda podia ser lida como um conjunto solto de configuração, ambiente e planilha.

Funções de aliases, resolução de abas, resolução de colunas e canonização estrutural estavam conceitualmente dispersas entre camadas. Como consequência, as Etapas 2 e 3 poderiam recriar resolução de entrada, aumentando duplicidade de funções, divergência semântica e dificuldade de continuidade do pipeline.

A microetapa formalizou a Etapa 1 como produtora de um artefato único e auditável:

`PacoteEntradaResolvida`

## 3. Decisão arquitetural

A Etapa 1 passa a ser formalizada como:

```text
ambiente mínimo
+ config operacional
+ ambiente final com data de referência
+ planilha
+ resolução estrutural de abas e colunas
+ janela bruta para CDI
+ cache BCB/CDI auditado
+ PacoteEntradaResolvida
```

O `PacoteEntradaResolvida` deve ser validado pela Etapa 2 e consumido pela Etapa 3.

## 4. Conteúdo conceitual do PacoteEntradaResolvida

O `PacoteEntradaResolvida` contém:

- `PacoteConfig`;
- `ContextoExecucao`;
- `PacotePlanilha`;
- `MapaAbasResolvidas`;
- `MapaColunasResolvidas`;
- `quadros_brutos`;
- `quadros_estruturais_resolvidos`;
- `JanelaConsultaCDI`;
- `PacoteCacheCDIDiario`;
- `AuditoriaEntradaBruta`;
- `AuditoriaResolucaoEntrada`;
- `AuditoriaCacheCDI`.

## 5. Conteúdo normativo do PacotePlanilha

O `PacotePlanilha`, dentro do `PacoteEntradaResolvida`, contém as cinco famílias operacionais em forma bruta e estruturalmente resolvida:

1. `Carteira`;
2. `Salários` / recebidos brutos;
3. `Todos os Gastos` / despesas;
4. `Inventário de Lotes`;
5. `Switching` / switchings já realizados brutos.

Esses quadros não são artefatos operacionais canônicos.

Eles são entradas estruturais validáveis pela Etapa 2 e transformáveis pela Etapa 3.

## 6. Distinção entre Etapa 1 e Etapa 3

Na Etapa 1, `quadros_canonicos`, quando esse nome aparecer no código existente, deve ser interpretado conceitualmente como:

`quadros_estruturais_resolvidos`

Dados operacionais canônicos pertencem à Etapa 3.

Não pertencem à Etapa 1:

- carteira canônica;
- gastos canônicos;
- salários canônicos;
- switching canônico;
- inventário canônico;
- integração entre `Inventário de Lotes` e switchings já realizados.

## 7. Cache BCB/CDI

O cache CDI/BCB entra na Etapa 1 como insumo externo bruto, cacheável e auditável.

A Etapa 1 deve:

- obter a série CDI;
- auditar origem;
- registrar fetch ou fallback;
- registrar janela de consulta;
- registrar status de atualização do cache.

A Etapa 1 não deve usar essa série para cálculo de rendimento, replay, valoração ou decisão econômica.

O uso econômico da série CDI pertence às etapas posteriores.

## 8. Fronteira da Etapa 1

A Etapa 1 pode:

- resolver ambiente mínimo;
- carregar config;
- resolver data de referência definitiva;
- obter planilha;
- resolver abas;
- resolver colunas;
- produzir quadros estruturais resolvidos;
- derivar janela bruta CDI;
- carregar cache CDI;
- registrar auditorias.

A Etapa 1 não pode:

- criar carteira canônica;
- criar gastos canônicos;
- criar salários canônicos;
- criar switching canônico;
- criar inventário canônico;
- integrar inventário com switching;
- calcular rendimento;
- executar replay;
- montar estado temporal;
- decidir pagamento;
- decidir switching;
- gerar ledger;
- gerar saída canônica;
- gerar console;
- gerar XLSX.

## 9. Relação com Etapa 2

A Etapa 2 valida o `PacoteEntradaResolvida`.

A Etapa 2 não deve:

- reler planilha;
- baixar planilha;
- abrir workbook;
- resolver aliases;
- resolver colunas;
- canonizar colunas;
- carregar cache BCB;
- corrigir dados;
- transformar dados.

A Etapa 2 deve retornar:

- status;
- erros;
- avisos;
- evidências.

## 10. Relação com Etapa 3

A Etapa 3 consome o `PacoteEntradaResolvida` validado e transforma os quadros estruturais resolvidos em artefatos operacionais canônicos.

A Etapa 3 deve criar, entre outros:

- carteira canônica;
- gastos canônicos;
- salários/recebidos canônicos;
- switching canônico de switchings já realizados;
- inventário canônico base;
- inventário canônico completo, integrando `Inventário de Lotes` e switchings já realizados.

A Etapa 3 não deve recriar resolvedores locais de aliases e colunas quando o mapa resolvido da Etapa 1 já existir.

## 11. Fluxograma da Etapa 1 — PacoteEntradaResolvida

```mermaid
flowchart TD

    START["Orquestrador físico<br/>nucleo/contexto_baseline.py<br/>carregar_contexto_baseline(...)"] --> E1["ETAPA 1<br/>Ambiente, configuração,<br/>entrada bruta e insumos externos resolvidos"]

    E1 --> AMB0["1A. Ambiente mínimo<br/>nucleo/ambiente.py"]
    AMB0 --> AMB1["detectar_raiz_repositorio(...)"]
    AMB0 --> AMB2["verificar_dependencias(...)"]
    AMB0 --> AMB3["configurar_warnings_rede(...)"]
    AMB1 --> AMB4["ContextoAmbienteMinimo<br/>raiz_repositorio<br/>diretorio_dados<br/>dependências<br/>warnings"]
    AMB2 --> AMB4
    AMB3 --> AMB4

    AMB4 --> CFG0["1B. Config operacional único<br/>dados/config_atualizado.json"]
    CFG0 --> CFG1["nucleo/carregador_config.py<br/>resolver_caminho_config(...)"]
    CFG1 --> CFG2["carregar_config(...)"]
    CFG2 --> CFG3["validar_config_nucleo(...)"]
    CFG3 --> OUT_CFG["PacoteConfig"]

    OUT_CFG --> AMBF0["1C. Ambiente final parametrizado<br/>nucleo/ambiente.py"]
    AMBF0 --> AMBF1["obter_data_referencia(config, timezone)"]
    AMBF1 --> AMBF2["bootstrap_ambiente(config)"]
    AMBF2 --> OUT_AMB["ContextoExecucao<br/>data_referencia definitiva"]

    OUT_CFG --> PLN0["1D. Origem da planilha<br/>nucleo/leitor_planilha.py<br/>carregar_planilha(...)"]
    PLN0 --> PLN1["_montar_url_download_planilha(...)"]
    PLN1 --> PLN2["_tentar_baixar_planilha(...)<br/>download ou fallback local"]
    PLN2 --> PLN3["resolver_caminho_planilha(...)"]
    PLN3 --> PLN4["pd.ExcelFile(...)<br/>nomes_abas físicas"]

    PLN4 --> ABA0["1E. Resolução única de abas"]
    ABA0 --> ABA1["Resolver bloco canônico → aba física<br/>carteira, salarios, despesas, lotes, switching"]
    ABA1 --> ABA2["MapaAbasResolvidas"]

    ABA2 --> RAW0["1F. Leitura bruta das cinco famílias"]
    RAW0 --> RAW1["pd.read_excel(..., sheet_name=aba_física)"]
    RAW1 --> RAW2["quadros_brutos<br/>Carteira<br/>Salários<br/>Todos os Gastos<br/>Inventário de Lotes<br/>Switching"]

    RAW2 --> COL0["1G. Resolução única de colunas"]
    COL0 --> COL1["construir_mapa_alias(...)"]
    COL1 --> COL2["resolver_coluna(...)<br/>ou resolvedor central equivalente"]
    COL2 --> COL3["MapaColunasResolvidas"]

    COL3 --> STR0["1H. Aplicação mecânica do mapa"]
    STR0 --> STR1["canonizar_colunas(...)<br/>ou aplicar_mapa_colunas_resolvidas(...)"]
    STR1 --> STR2["quadros_estruturais_resolvidos<br/>carteira<br/>salarios<br/>despesas<br/>lotes<br/>switching"]

    STR2 --> CDI0["1I. Janela bruta para CDI/BCB"]
    OUT_AMB --> CDI0
    CDI0 --> CDI1["Derivar datas estruturais mínimas<br/>lotes, despesas, switching, salarios<br/>+ data_referencia"]
    CDI1 --> CDI2["JanelaConsultaCDI"]

    CDI2 --> BCB0["1J. Cache BCB/CDI<br/>nucleo/cache_cdi_bcb.py"]
    BCB0 --> BCB1["_ler_payload_cache(...)<br/>_ler_cache(...)"]
    BCB0 --> BCB2["_cache_atualizado_para_referencia(...)"]
    BCB0 --> BCB3["_buscar_bcb(...)"]
    BCB3 --> BCB4["_salvar_cache(...)"]
    BCB1 --> BCB5["PacoteCacheCDIDiario"]
    BCB2 --> BCB5
    BCB3 --> BCB5
    BCB4 --> BCB5

    RAW2 --> PP0["1K. PacotePlanilha"]
    STR2 --> PP0
    ABA2 --> PP0
    COL3 --> PP0
    PP0 --> PP1["PacotePlanilha<br/>quadros_brutos<br/>quadros_estruturais_resolvidos<br/>mapas<br/>auditoria<br/>validacao_inicial"]

    PLN2 --> AUD0["1L. Auditorias da Etapa 1"]
    ABA2 --> AUD0
    COL3 --> AUD0
    BCB5 --> AUD0
    AUD0 --> AUD1["AuditoriaEntradaBruta"]
    AUD0 --> AUD2["AuditoriaResolucaoEntrada"]
    AUD0 --> AUD3["AuditoriaCacheCDI"]

    OUT_CFG --> PACK["Saída final<br/>PacoteEntradaResolvida"]
    OUT_AMB --> PACK
    PP1 --> PACK
    CDI2 --> PACK
    BCB5 --> PACK
    AUD1 --> PACK
    AUD2 --> PACK
    AUD3 --> PACK

    PACK --> E2["Destino<br/>Etapa 2 — validar_pre_execucao(...)"]
```
