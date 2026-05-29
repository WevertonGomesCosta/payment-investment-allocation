# Contrato Individual — Etapa 2 — Validação Pré-Execução

## 1. Identificação documental

- **Etapa:** 2
- **Nome:** Validação Pré-Execução
- **Entrada formal obrigatória e exclusiva:** `PacoteEntradaResolvida`
- **Saída formal obrigatória:** `PacoteValidacaoPreExecucao`
- **Natureza:** gate puro de validação estrutural pré-execução
- **Módulo central:** `nucleo/validacao_pre_execucao.py`
- **Função pública legada compatível:** `validar_pre_execucao(...)`
- **Função viva usada no runtime:** `validar_pre_execucao_pacote_entrada_resolvida(...)`

## 2. Status normativo

Este contrato formaliza a Etapa 2 como validação estrutural do `PacoteEntradaResolvida` produzido pela Etapa 1.

A Etapa 2 é gate puro: valida completude, coerência, auditabilidade e interpretabilidade mínima, mas não corrige dados, não transforma dados e não cria artefatos canônicos.

No runtime vivo, a validação da Etapa 2 é executada por `validar_pre_execucao_pacote_entrada_resolvida(...)`, consumindo diretamente `PacoteEntradaResolvida`. A função `validar_pre_execucao(...)` permanece documentada como rota compatível para os componentes físicos distribuídos (`PacoteConfig`, `ContextoExecucao`, `PacotePlanilha`), mas não é a função principal do runtime atual.

## 3. Posição na cadeia macro

```text
Etapa 1 -> PacoteEntradaResolvida -> Etapa 2 -> PacoteValidacaoPreExecucao -> Etapa 3
```

## 4. Função da etapa

A Etapa 2 valida se a entrada resolvida pela Etapa 1 está apta para ser consumida pela Etapa 3. Seu papel é bloquear a progressão quando a entrada não estiver completa, coerente ou minimamente interpretável.

## 5. Entrada formal obrigatória e exclusiva

A entrada formal obrigatória e exclusiva da Etapa 2 é:

```text
PacoteEntradaResolvida
```

No código histórico, essa entrada pode ainda aparecer fisicamente distribuída como `PacoteConfig`, `ContextoExecucao` e `PacotePlanilha`. Arquiteturalmente, esses elementos são tratados como componentes do `PacoteEntradaResolvida`.

## 6. Componentes consumíveis da entrada

A Etapa 2 pode consumir somente componentes materializados no `PacoteEntradaResolvida`, incluindo:

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

## 7. Saída formal obrigatória

A saída formal obrigatória da Etapa 2 é:

```text
PacoteValidacaoPreExecucao
```

## 8. Componentes mínimos da saída

`PacoteValidacaoPreExecucao` deve conter, no mínimo:

- `ok`;
- `erros_bloqueantes`;
- `avisos`;
- `evidencias`.

O pacote registra se o `PacoteEntradaResolvida` está apto para consumo pela Etapa 3.

## 9. Processo interno da etapa

A Etapa 2 deve:

1. receber `PacoteEntradaResolvida` como entrada formal;
2. verificar se o objeto recebido é `PacoteEntradaResolvida`;
3. validar estrutura mínima do pacote;
4. validar `PacoteConfig`;
5. validar `ContextoExecucao`;
6. validar `PacotePlanilha` sem reler workbook;
7. validar `MapaAbasResolvidas`;
8. validar `MapaColunasResolvidas`;
9. validar `quadros_estruturais_resolvidos`;
10. validar interpretabilidade mínima de datas;
11. validar interpretabilidade mínima de números;
12. validar `JanelaConsultaCDI`;
13. validar `PacoteCacheCDIDiario`;
14. validar auditorias da Etapa 1;
15. consolidar `ok`, erros, avisos e evidências;
16. emitir `PacoteValidacaoPreExecucao`.

## 10. O que a etapa pode fazer

A Etapa 2 pode:

- validar presença de artefatos;
- validar existência de caminhos;
- validar consistência de configuração;
- validar contexto de execução;
- validar presença das cinco famílias operacionais;
- validar mapas de abas resolvidas;
- validar mapas de colunas resolvidas;
- validar quadros estruturais resolvidos;
- validar interpretabilidade mínima de datas e números;
- validar janela CDI;
- validar pacote cache CDI;
- validar auditorias da Etapa 1;
- emitir erros;
- emitir avisos;
- registrar evidências.

## 11. O que a etapa não pode fazer

A Etapa 2 não pode:

- baixar planilha;
- abrir workbook;
- reler abas;
- resolver aliases;
- resolver colunas para uso operacional;
- canonizar colunas;
- criar quadros estruturais;
- carregar cache BCB;
- buscar BCB online;
- salvar cache;
- corrigir dados;
- limpar dados;
- normalizar dados operacionalmente;
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
- renderizar console;
- gerar XLSX.

## 12. Relação com a etapa anterior

A Etapa 2 consome exclusivamente o `PacoteEntradaResolvida` produzido pela Etapa 1. Ela não deve recriar a resolução estrutural da entrada já feita pela Etapa 1.

## 13. Relação com a etapa posterior

A Etapa 2 entrega `PacoteValidacaoPreExecucao` para a Etapa 3. A Etapa 3 só deve iniciar canonização operacional quando a validação pré-execução permitir progressão.

## 14. Schema/funções públicas previstas ou implementadas

Módulo funcional:

```text
nucleo/validacao_pre_execucao.py
```

Função viva usada no runtime:

```python
validar_pre_execucao_pacote_entrada_resolvida(
    pacote_entrada_resolvida: PacoteEntradaResolvida,
) -> PacoteValidacaoPreExecucao
```

Função legada compatível preservada:

```python
validar_pre_execucao(
    pacote_config: PacoteConfig,
    contexto_execucao: ContextoExecucao,
    pacote_planilha: PacotePlanilha,
) -> PacoteValidacaoPreExecucao
```

Funções ou blocos internos preservados no contrato:

```text
_validar_pacote_entrada_resolvida_estrutura(...)
_validar_pacote_config(...)
_validar_contexto_execucao(...)
_validar_pacote_planilha_basico_sem_alias(...)
_validar_pacote_planilha(...)
_validar_mapa_abas_resolvidas(...)
_validar_mapa_colunas_resolvidas(...)
_validar_quadros_estruturais_resolvidos(...)
_validar_janela_consulta_cdi(...)
_validar_pacote_cache_cdi(...)
_validar_auditorias_etapa1(...)
```

Artefato formal:

```python
PacoteValidacaoPreExecucao
```

## 15. Auditoria esperada

A auditoria da Etapa 2 deve registrar:

- status `ok`;
- erros bloqueantes;
- avisos;
- evidências de presença dos componentes do `PacoteEntradaResolvida`;
- evidências de mapas de abas e colunas;
- evidências de interpretabilidade de datas e números;
- evidências de janela/cache CDI;
- evidências das auditorias da Etapa 1;
- indicação de que a etapa não recriou aliases, não relê planilha e não cria dados canônicos.

## 16. Critérios de aceite

A Etapa 2 é aceita quando:

1. consome `PacoteEntradaResolvida`;
2. produz `PacoteValidacaoPreExecucao`;
3. bloqueia progressão quando houver erro estrutural;
4. registra avisos e evidências auditáveis;
5. não relê planilha;
6. não resolve aliases novamente;
7. não canoniza dados;
8. não cria artefatos da Etapa 3;
9. não gera motor, ledger, console, XLSX ou saída canônica.

## 17. Fluxograma operacional-explicativo completo

```mermaid
flowchart TD
    IN["Entrada formal<br/>PacoteEntradaResolvida"] --> ORQ["nucleo/validacao_pre_execucao.py<br/>validar_pre_execucao_pacote_entrada_resolvida(...)"]

    ORQ --> TIPO{"Objeto é PacoteEntradaResolvida?"}
    TIPO -->|não| FAIL["PacoteValidacaoPreExecucao<br/>ok=False<br/>erro: objeto inválido"]
    TIPO -->|sim| ESTR["_validar_pacote_entrada_resolvida_estrutura(...)"]

    ESTR --> CFG["_validar_pacote_config(...)"]
    ESTR --> CTX["_validar_contexto_execucao(...)"]
    ESTR --> PLN["_validar_pacote_planilha_basico_sem_alias(...)"]
    ESTR --> ABA["_validar_mapa_abas_resolvidas(...)"]
    ESTR --> COL["_validar_mapa_colunas_resolvidas(...)"]
    ESTR --> QDR["_validar_quadros_estruturais_resolvidos(...)"]
    ESTR --> CDI["_validar_janela_consulta_cdi(...)"]
    ESTR --> BCB["_validar_pacote_cache_cdi(...)"]
    ESTR --> AUD["_validar_auditorias_etapa1(...)"]

    CFG --> CONS["Consolidar erros, avisos e evidências"]
    CTX --> CONS
    PLN --> CONS
    ABA --> CONS
    COL --> CONS
    QDR --> CONS
    CDI --> CONS
    BCB --> CONS
    AUD --> CONS

    CONS --> OUT["Saída formal<br/>PacoteValidacaoPreExecucao"]
    OUT --> DEC{"ok?"}
    DEC -->|False| STOP["Bloqueia Etapa 3"]
    DEC -->|True| E3["Destino<br/>Etapa 3 — Dados Operacionais Canônicos"]
```

## 18. Condição de parada

A Etapa 2 deve bloquear a progressão para a Etapa 3 quando qualquer componente estrutural obrigatório do `PacoteEntradaResolvida` estiver ausente, inválido ou sem interpretabilidade mínima para canonização operacional.

## 19. Histórico documental / adendos funcionais consolidados

Este contrato foi originalmente derivado de:

```text
logs/iteracoes/ME-V17-F0-V32B_FORMALIZA_ETAPA2_VALIDACAO_PRE_EXECUCAO.md
```

A versão atual alinha a documentação ao script vivo, declarando `validar_pre_execucao_pacote_entrada_resolvida(...)` como função usada no runtime e preservando `validar_pre_execucao(...)` como função legada compatível.
