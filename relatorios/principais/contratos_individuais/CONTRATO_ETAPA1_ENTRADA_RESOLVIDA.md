# Contrato Individual — Etapa 1 — Entrada Resolvida

## 1. Identificação documental

- **Etapa:** 1
- **Nome:** Entrada Resolvida
- **Saída formal obrigatória:** `PacoteEntradaResolvida`
- **Natureza:** resolução física, estrutural e auditável da entrada bruta
- **Módulo formal do artefato:** `nucleo/entrada_resolvida.py`
- **Funções formais do artefato:** `montar_pacote_entrada_resolvida(...)`, `auditar_pacote_entrada_resolvida(...)`
- **Wrapper vivo atual do runtime:** `nucleo/contexto_operacional_canonico.py` / `carregar_contexto_operacional_canonico(...)`
- **Módulos produtores preservados:** `nucleo/ambiente.py`, `nucleo/carregador_config.py`, `nucleo/leitor_planilha.py`, `nucleo/cache_cdi_bcb.py`
- **Orquestração histórica preservada apenas como referência:** `nucleo/contexto_baseline.py` / `carregar_contexto_baseline(...)`

## 2. Status normativo

Este contrato formaliza a Etapa 1 como produtora de um artefato único, auditável e consumível pelas etapas posteriores: `PacoteEntradaResolvida`.

A Etapa 1 resolve a entrada bruta, mas não produz dados operacionais canônicos, não decide pagamentos, não calcula rendimento econômico e não gera saída observável.

No runtime vivo, a Etapa 1 é materializada dentro de `carregar_contexto_operacional_canonico(...)`, que preserva `PacoteEntradaResolvida` como artefato formal e apenas encapsula sua montagem para consumo pelas etapas posteriores.

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
13. registrar auditorias de entrada, resolução e cache;
14. montar `PacoteEntradaResolvida` por `montar_pacote_entrada_resolvida(...)`;
15. auditar o pacote por `auditar_pacote_entrada_resolvida(...)`;
16. disponibilizar o artefato dentro de `ContextoOperacionalCanonico` quando executado pelo runtime vivo.

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
- registrar auditorias;
- montar `PacoteEntradaResolvida`;
- expor `PacoteEntradaResolvida` dentro do wrapper vivo `ContextoOperacionalCanonico`.

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

No runtime vivo, `carregar_contexto_operacional_canonico(...)` monta `PacoteEntradaResolvida`, executa sua auditoria e o disponibiliza para `validar_pre_execucao_pacote_entrada_resolvida(...)`.

## 14. Schema/funções públicas previstas ou implementadas

Módulo formal do artefato:

```text
nucleo/entrada_resolvida.py
```

Funções formais implementadas:

```text
montar_pacote_entrada_resolvida(...)
auditar_pacote_entrada_resolvida(...)
montar_auditoria_entrada_bruta(...)
montar_auditoria_resolucao_entrada(...)
montar_auditoria_cache_cdi(...)
```

Wrapper vivo atual:

```text
nucleo/contexto_operacional_canonico.py
carregar_contexto_operacional_canonico(...)
```

Módulos produtores preservados:

```text
nucleo/ambiente.py
bootstrap_ambiente(...)
obter_data_referencia(...)

nucleo/carregador_config.py
carregar_config(...)

nucleo/leitor_planilha.py
carregar_planilha(...)

nucleo/cache_cdi_bcb.py
carregar_cache_cdi_diario(...)
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
- avisos e inconsistências estruturais iniciais;
- resultado de `auditar_pacote_entrada_resolvida(...)`.

## 16. Critérios de aceite

A Etapa 1 é aceita quando:

1. produz `PacoteEntradaResolvida`;
2. contém config, contexto, planilha, mapas, quadros estruturais, CDI/cache e auditorias;
3. resolve as cinco famílias operacionais mínimas;
4. registra auditoria do pacote resolvido;
5. não cria dados operacionais canônicos;
6. não calcula rendimento econômico;
7. não executa decisão de pagamento ou switching;
8. não gera ledger, saída canônica, console ou XLSX.

## 17. Fluxograma operacional-explicativo completo

```mermaid
flowchart TD
    START["Wrapper vivo do runtime<br/>nucleo/contexto_operacional_canonico.py<br/>carregar_contexto_operacional_canonico(...)"] --> E1["ETAPA 1<br/>Entrada física resolvida"]

    E1 --> CFG0["Configuração<br/>nucleo/carregador_config.py<br/>carregar_config(...)"]
    E1 --> AMB0["Ambiente<br/>nucleo/ambiente.py<br/>bootstrap_ambiente(...)"]
    E1 --> PLN0["Planilha<br/>nucleo/leitor_planilha.py<br/>carregar_planilha(...)"]

    CFG0 --> CFG1["PacoteConfig"]
    AMB0 --> AMB1["ContextoExecucao<br/>data_referencia"]
    PLN0 --> ABA0["MapaAbasResolvidas"]
    PLN0 --> COL0["MapaColunasResolvidas"]
    PLN0 --> RAW0["quadros_brutos"]
    PLN0 --> STR0["quadros_estruturais_resolvidos"]
    PLN0 --> PP0["PacotePlanilha"]

    STR0 --> CDI0["JanelaConsultaCDI"]
    AMB1 --> CDI0
    CDI0 --> BCB0["Cache CDI/BCB<br/>nucleo/cache_cdi_bcb.py<br/>carregar_cache_cdi_diario(...)"]
    BCB0 --> BCB1["PacoteCacheCDIDiario"]

    PP0 --> AUD0["Auditorias da Etapa 1"]
    ABA0 --> AUD0
    COL0 --> AUD0
    BCB1 --> AUD0
    AUD0 --> AUD1["AuditoriaEntradaBruta"]
    AUD0 --> AUD2["AuditoriaResolucaoEntrada"]
    AUD0 --> AUD3["AuditoriaCacheCDI"]

    CFG1 --> PACK0["nucleo/entrada_resolvida.py<br/>montar_pacote_entrada_resolvida(...)"]
    AMB1 --> PACK0
    PP0 --> PACK0
    CDI0 --> PACK0
    BCB1 --> PACK0
    AUD1 --> PACK0
    AUD2 --> PACK0
    AUD3 --> PACK0

    PACK0 --> PACK["Saída formal<br/>PacoteEntradaResolvida"]
    PACK --> AUDPACK["auditar_pacote_entrada_resolvida(...)"]
    AUDPACK --> E2["Destino<br/>Etapa 2 — Validação Pré-Execução"]
```

## 18. Condição de parada

A Etapa 1 deve parar com erro auditado quando não for possível resolver configuração mínima, ambiente mínimo, planilha operacional ou componentes estruturais obrigatórios para formar `PacoteEntradaResolvida`.

## 19. Histórico documental / adendos funcionais consolidados

Este contrato foi originalmente derivado de:

```text
logs/iteracoes/ME-V17-F0-V32A_FORMALIZA_ETAPA1_PACOTE_ENTRADA_RESOLVIDA.md
```

A versão atual alinha a documentação aos scripts vivos, preservando `PacoteEntradaResolvida` como artefato formal e registrando `ContextoOperacionalCanonico` / `carregar_contexto_operacional_canonico(...)` como wrapper vivo atual do runtime.
