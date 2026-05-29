# Contrato Individual — Etapa 1 — Entrada Resolvida

## 1. Identificação documental

- **Etapa:** 1
- **Nome:** Entrada Resolvida
- **Saída formal obrigatória:** `PacoteEntradaResolvida`
- **Natureza:** resolução física, estrutural e auditável da entrada bruta
- **Módulos centrais:** `nucleo/contexto_baseline.py`, `nucleo/ambiente.py`, `nucleo/carregador_config.py`, `nucleo/leitor_planilha.py`, `nucleo/cache_cdi_bcb.py`
- **Função orquestradora histórica:** `carregar_contexto_baseline(...)`

## 2. Status normativo

Este contrato formaliza a Etapa 1 como produtora de um artefato único, auditável e consumível pelas etapas posteriores: `PacoteEntradaResolvida`.

A Etapa 1 resolve a entrada bruta, mas não produz dados operacionais canônicos, não decide pagamentos, não calcula rendimento econômico e não gera saída observável.

## 3. Posição na cadeia macro

```text
Origem física/configuração/planilha/cache -> Etapa 1 -> PacoteEntradaResolvida -> Etapa 2
```

## 4. Função da etapa

A Etapa 1 resolve ambiente, configuração, planilha, abas, colunas, quadros estruturais e cache CDI/BCB em um pacote único.

Sua função é transformar entradas físicas dispersas em uma entrada resolvida, estruturalmente auditável e pronta para validação pré-execução pela Etapa 2.

## 5. Entrada formal obrigatória e exclusiva

A entrada da Etapa 1 é composta por insumos físicos e operacionais brutos:

- ambiente mínimo de execução;
- configuração operacional;
- planilha operacional bruta;
- aliases e regras de resolução estrutural;
- cache CDI/BCB local ou série CDI obtida externamente;
- data de referência operacional.

Esses insumos ainda não são artefatos canônicos de etapas posteriores.

## 6. Componentes consumíveis da entrada

A Etapa 1 pode consumir:

- `dados/config_atualizado.json`;
- planilha local ou fonte configurada da planilha;
- nomes físicos de abas;
- colunas físicas dos quadros brutos;
- aliases declarados para abas e colunas;
- cache CDI/BCB;
- série CDI/BCB para atualização do cache;
- ambiente e dependências mínimas.

## 7. Saída formal obrigatória

A saída formal obrigatória da Etapa 1 é:

```text
PacoteEntradaResolvida
```

## 8. Componentes mínimos da saída

`PacoteEntradaResolvida` deve conter, no mínimo:

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

O `PacotePlanilha`, dentro do `PacoteEntradaResolvida`, contém as cinco famílias operacionais em forma bruta e estruturalmente resolvida:

1. `Carteira`;
2. `Salários` / recebidos brutos;
3. `Todos os Gastos` / despesas;
4. `Inventário de Lotes`;
5. `Switching` / switchings já realizados brutos.

## 9. Processo interno da etapa

A Etapa 1 deve:

1. resolver ambiente mínimo;
2. carregar e validar configuração operacional;
3. definir ambiente final e data de referência;
4. localizar, baixar ou resolver a planilha operacional;
5. resolver abas físicas para blocos canônicos estruturais;
6. ler quadros brutos;
7. resolver colunas;
8. aplicar mecanicamente o mapa de colunas;
9. produzir quadros estruturalmente resolvidos;
10. derivar janela bruta para CDI/BCB;
11. carregar, auditar e atualizar cache CDI/BCB quando aplicável;
12. montar `PacotePlanilha`;
13. registrar auditorias;
14. emitir `PacoteEntradaResolvida`.

## 10. O que a etapa pode fazer

A Etapa 1 pode:

- resolver ambiente mínimo;
- carregar configuração;
- resolver data de referência definitiva;
- obter planilha;
- resolver abas;
- resolver colunas;
- produzir quadros estruturais resolvidos;
- derivar janela bruta CDI;
- carregar e atualizar cache CDI;
- registrar auditorias.

## 11. O que a etapa não pode fazer

A Etapa 1 não pode:

- criar carteira canônica;
- criar gastos canônicos;
- criar salários canônicos;
- criar switching canônico;
- criar inventário canônico;
- integrar inventário com switching como decisão operacional;
- calcular rendimento econômico;
- executar replay;
- montar estado temporal;
- decidir pagamento;
- decidir switching;
- gerar ledger;
- gerar saída canônica;
- renderizar console;
- gerar XLSX.

## 12. Relação com a etapa anterior

A Etapa 1 é a primeira etapa da cadeia operacional. Ela não consome artefato formal de etapa anterior; consome apenas insumos físicos e configuracionais brutos.

## 13. Relação com a etapa posterior

A Etapa 1 entrega `PacoteEntradaResolvida` para a Etapa 2 — Validação Pré-Execução. A Etapa 2 deve validar esse pacote sem reler planilha, baixar planilha, resolver aliases, resolver colunas ou atualizar cache.

## 14. Schema/funções públicas previstas ou implementadas

Módulos e funções centrais preservados no contrato:

```text
nucleo/contexto_baseline.py
carregar_contexto_baseline(...)

nucleo/ambiente.py
detectar_raiz_repositorio(...)
verificar_dependencias(...)
configurar_warnings_rede(...)
obter_data_referencia(...)
bootstrap_ambiente(...)

nucleo/carregador_config.py
resolver_caminho_config(...)
carregar_config(...)
validar_config_nucleo(...)

nucleo/leitor_planilha.py
carregar_planilha(...)
_montar_url_download_planilha(...)
_tentar_baixar_planilha(...)
resolver_caminho_planilha(...)

nucleo/cache_cdi_bcb.py
_ler_payload_cache(...)
_cache_atualizado_para_referencia(...)
_buscar_bcb(...)
_salvar_cache(...)
```

Artefato formal:

```python
PacoteEntradaResolvida
```

## 15. Auditoria esperada

A auditoria da Etapa 1 deve registrar:

- origem da planilha;
- status de download ou fallback;
- abas resolvidas;
- colunas resolvidas;
- quadros brutos lidos;
- quadros estruturais resolvidos;
- janela CDI/BCB;
- origem do cache CDI/BCB;
- status de atualização do cache;
- avisos e inconsistências estruturais iniciais.

## 16. Critérios de aceite

A Etapa 1 é aceita quando:

1. produz `PacoteEntradaResolvida`;
2. contém config, contexto, planilha, mapas, quadros estruturais, CDI/cache e auditorias;
3. resolve as cinco famílias operacionais mínimas;
4. não cria dados operacionais canônicos;
5. não calcula rendimento econômico;
6. não executa decisão de pagamento ou switching;
7. não gera ledger, saída canônica, console ou XLSX.

## 17. Fluxograma operacional-explicativo completo

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

    OUT_CFG --> PACK["Saída formal<br/>PacoteEntradaResolvida"]
    OUT_AMB --> PACK
    PP1 --> PACK
    CDI2 --> PACK
    BCB5 --> PACK
    AUD1 --> PACK
    AUD2 --> PACK
    AUD3 --> PACK

    PACK --> E2["Destino<br/>Etapa 2 — nucleo/validacao_pre_execucao.py<br/>validar_pre_execucao(...)"]
```

## 18. Condição de parada

A Etapa 1 deve parar com erro auditado quando não for possível resolver configuração mínima, ambiente mínimo, planilha operacional ou componentes estruturais obrigatórios para formar `PacoteEntradaResolvida`.

## 19. Histórico documental / adendos funcionais consolidados

Este contrato foi originalmente derivado de:

```text
logs/iteracoes/ME-V17-F0-V32A_FORMALIZA_ETAPA1_PACOTE_ENTRADA_RESOLVIDA.md
```

A versão atual apenas reorganiza o conteúdo no padrão estrutural único dos contratos individuais das Etapas 1–7, sem alterar a semântica da Etapa 1.
