# ME-V17-F0-V32C — Formaliza Etapa 3 como canonização operacional do PacoteEntradaResolvida validado

## 1. Identificação

- MICROETAPA: V17-F0-V.3.2C
- TIPO: DOCUMENTAL / ARQUITETURAL
- CLASSE: FORMALIZA_ETAPA3_COMO_CANONIZACAO_OPERACIONAL
- ALTERA CÓDIGO: NÃO
- ALTERA MOTOR: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA DADOS: NÃO
- ALTERA CACHE: NÃO
- ALTERA RENDERIZAÇÃO: NÃO

---

## 2. Problema motivador

Após a formalização da Etapa 1 como produtora do `PacoteEntradaResolvida` e da Etapa 2 como gate de validação desse pacote, a Etapa 3 deve ser formalizada como camada de transformação da entrada resolvida validada em artefatos operacionais canônicos.

Também era necessário eliminar ambiguidades conceituais sobre:

- resolução local de aliases e colunas na Etapa 3;
- distinção entre switchings já realizados e switchings candidatos do motor;
- duplicidade entre switching canônico e lotes destino de switching;
- uso normativo do termo `inventario_lotes_expandido`;
- risco de expor lotes destino de switching como fonte operacional paralela.

---

## 3. Decisão arquitetural

A Etapa 3 passa a ser formalizada como:

```text
Etapa 3 = canonização operacional do PacoteEntradaResolvida validado
```

A Etapa 3 recebe:

- `PacoteEntradaResolvida` validado;
- `PacoteValidacaoPreExecucao`.

A Etapa 3 produz:

- `PacoteDadosOperacionaisCanonicos`;
- `UniversoEconomicoCanonico`;
- `PacoteAuditoriaCanonizacaoOperacional`.

---

## 4. Entrada normativa da Etapa 3

A entrada da Etapa 3 é:

`PacoteEntradaResolvida validado`

Composto por:

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

A Etapa 3 também consome o `PacoteValidacaoPreExecucao` como evidência de validação pela Etapa 2.

---

## 5. Saída normativa da Etapa 3

As saídas normativas da Etapa 3 são:

- `PacoteDadosOperacionaisCanonicos`;
- `UniversoEconomicoCanonico`;
- `PacoteAuditoriaCanonizacaoOperacional`.

Composição normativa do `PacoteDadosOperacionaisCanonicos`:

- `carteira_canonica`;
- `universo_economico_canonico`;
- `gastos_canonicos`;
- `salarios_canonicos`;
- `recebidos_canonicos`;
- `switching_canonico`;
- `inventario_canonico_base`;
- `inventario_canonico_completo`;
- auditorias;
- validações.

O pacote final não deve expor como saída normativa independente:

`lotes_destino_switchings_realizados_normalizados`

Esse artefato pode existir internamente, mas apenas como artefato intermediário de construção e auditoria do `inventario_canonico_completo`.

---

## 6. Blocos normativos da Etapa 3

### 6.1. Confirmar entrada validada

A Etapa 3 consome as evidências do `PacoteValidacaoPreExecucao`.

A Etapa 3 não corrige a entrada. Ela apenas consome entrada validada.

---

### 6.2. Carteira canônica e universo econômico

A Etapa 3 transforma o quadro estrutural resolvido de `carteira` em:

- carteira canônica;
- produtos canônicos;
- mapa de produtos;
- universo econômico canônico;
- ranking da Carteira;
- auditoria da Carteira;
- validação da Carteira.

Funções atuais relacionadas:

- `normalizar_carteira_bruta(...)`;
- `normalizar_nome_produto(...)`;
- `gerar_produto_key(...)`.

Arquivo atual relacionado:

- `nucleo/carteira_canonica.py`.

A Etapa 3 não deve redescobrir colunas da Carteira quando `MapaColunasResolvidas["carteira"]` já existir.

---

### 6.3. Gastos / pagamentos canônicos

A Etapa 3 transforma o quadro estrutural resolvido de `despesas` em:

- gastos canônicos;
- pagamentos canônicos;
- auditoria de gastos.

Função atual relacionada:

- `carregar_gastos_canonicos(...)`.

Arquivo atual relacionado:

- `nucleo/dados_operacionais_canonicos.py`.

A Etapa 3 não decide fonte de pagamento, não executa pagamento e não calcula saldo temporal.

---

### 6.4. Salários / recebidos canônicos

A Etapa 3 transforma o quadro estrutural resolvido de `salarios` em:

- salários canônicos;
- recebidos canônicos;
- auditoria de salários.

Função atual relacionada:

- `carregar_salarios_canonicos(...)`.

Arquivo atual relacionado:

- `nucleo/dados_operacionais_canonicos.py`.

A Etapa 3 não decide uso do recebido, aporte, pagamento, saldo livre ou estado temporal.

---

### 6.5. Switchings já realizados canônicos

A Etapa 3 transforma o quadro estrutural resolvido de `switching` em:

- `switching_canonico`;
- auditoria de switching.

Funções atuais relacionadas:

- `carregar_switching_canonico(...)`;
- `normalizar_lotes_pos_switching_para_schema_inventario(...)`.

Arquivos atuais relacionados:

- `nucleo/dados_operacionais_canonicos.py`;
- `nucleo/inventario_lotes_expandido_pos_switching.py`.

A aba `Switching` representa switchings já realizados/declarados na entrada operacional.

Ela não representa switchings candidatos, recomendados, promovidos ou simulados pelo motor.

A Etapa 3 pode gerar internamente lotes destino derivados desses switchings já realizados, mas esses lotes são apenas artefato intermediário de construção do `inventario_canonico_completo`.

---

### 6.6. Inventário de Lotes canônico completo

A Etapa 3 transforma o quadro estrutural resolvido de `lotes`, em conjunto com os switchings já realizados canônicos, em:

- `inventario_canonico_base`;
- `inventario_canonico_completo`;
- auditoria de inventário;
- auditoria do inventário canônico completo.

Funções atuais relacionadas:

- `carregar_inventario_canonico(...)`;
- `construir_inventario_lotes_expandido(...)`.

Arquivos atuais relacionados:

- `nucleo/dados_operacionais_canonicos.py`;
- `nucleo/inventario_lotes_expandido_pos_switching.py`.

O nome técnico transitório atual `inventario_lotes_expandido` deve ser interpretado conceitualmente como:

`inventario_canonico_completo`

O inventário operacional entregue às etapas posteriores é único.

Nenhuma etapa posterior deve consumir uma lista paralela de lotes destino de switching como fonte operacional independente.

---

### 6.7. Universo econômico canônico

A Etapa 3 consolida:

- produtos canônicos;
- mapa de produtos;
- elegibilidade básica;
- ranking da Carteira;
- auditoria do universo econômico.

O ranking estrutura produtos e destinos, mas não decide pacote do dia, não materializa switching candidato e não liquida pagamento.

---

### 6.8. Auditorias e validações da Etapa 3

A Etapa 3 deve registrar auditorias de:

- carteira;
- gastos;
- salários;
- recebidos;
- switching;
- inventário;
- inventário canônico completo;
- universo econômico.

As auditorias e validações da Etapa 3 são consolidadas em:

`PacoteAuditoriaCanonizacaoOperacional`

A auditoria do inventário canônico completo deve registrar, quando aplicável:

- quantidade de lotes no inventário base;
- quantidade de lotes destino de switchings já realizados integrados;
- quantidade de lotes no inventário canônico completo;
- lotes destino com schema válido;
- lotes destino sem produto;
- lotes destino sem valor;
- duplicidades detectadas;
- risco de dupla contagem de origem de switching;
- neutralização temporal de origem de switching.

---

## 7. Fronteira da Etapa 3

A Etapa 3 pode:

- criar carteira canônica;
- criar produtos canônicos;
- criar universo econômico canônico;
- criar ranking da Carteira;
- criar gastos/pagamentos canônicos;
- criar salários/recebidos canônicos;
- criar switching canônico de switchings já realizados;
- criar inventário canônico base;
- gerar internamente lotes destino de switchings já realizados;
- integrar esses lotes ao inventário canônico base;
- criar inventário canônico completo;
- resolver `produto_key` usando a Carteira canônica;
- classificar minimamente lotes;
- registrar auditorias e validações de canonização.

A Etapa 3 não pode:

- baixar planilha;
- abrir workbook;
- resolver abas físicas;
- resolver aliases de colunas;
- canonizar colunas estruturais;
- buscar BCB online;
- salvar cache BCB;
- calcular rendimento;
- executar replay passado;
- montar estado temporal inicial;
- normalizar vencimentos temporalmente;
- decidir pagamento;
- decidir switching candidato;
- promover switching do motor;
- materializar switching candidato;
- executar pacote do dia;
- gerar ledger;
- aplicar gates de núcleo;
- gerar saída canônica;
- renderizar console;
- gerar XLSX;
- expor lotes destino de switching como fonte operacional paralela ao `inventario_canonico_completo`.

---

## 8. Relação com Etapa 4

A Etapa 4 deve receber:

- `PacoteDadosOperacionaisCanonicos`;
- `inventario_canonico_completo`;
- `gastos_canonicos`;
- `salarios_canonicos`;
- `switching_canonico`;
- `carteira_canonica`;
- `universo_economico_canonico`;
- `PacoteCacheCDIDiario`;
- `data_referencia`.

A Etapa 4 deve construir o estado temporal inicial.

A Etapa 3 não deve montar o estado temporal inicial.

---

## 9. Arquivos alterados

- `relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md`
- `logs/iteracoes/ME-V17-F0-V32C_FORMALIZA_ETAPA3_CANONIZACAO_OPERACIONAL.md`

---

## 10. Arquivos preservados

Nenhum arquivo de código foi alterado.

Foram preservados:

- `nucleo/ambiente.py`;
- `nucleo/carregador_config.py`;
- `nucleo/leitor_planilha.py`;
- `nucleo/cache_cdi_bcb.py`;
- `nucleo/validacao_pre_execucao.py`;
- `nucleo/dados_operacionais_canonicos.py`;
- `nucleo/inventario_lotes_expandido_pos_switching.py`;
- `nucleo/nucleo_financeiro_minimo.py`;
- `nucleo/saida_canonica.py`;
- `nucleo/saida_observavel.py`;
- `aplicacao/principal.py`;
- `README.md`;
- `dados/`;
- `saidas/`;
- `cache/`;
- modelo matemático oficial;
- scripts de execução;
- motor temporal;
- regras econômicas;
- renderização;
- arquivos XLSX.

---

## 11. Consequências para etapas futuras

Futuras microetapas poderão:

- adaptar `carregar_dados_operacionais_canonicos(...)` para consumir `PacoteEntradaResolvida` validado;
- remover resolvedores locais duplicados da Etapa 3;
- substituir `inventario_lotes_expandido` por `inventario_canonico_completo` como nomenclatura normativa;
- deixar `lotes_destino_switchings_realizados_normalizados` como artefato interno ou auditoria, não como saída operacional paralela;
- consolidar resolvedores de produto duplicados;
- preparar a Etapa 4 para consumir o inventário canônico completo único.

Esta microetapa não implementa nenhuma dessas refatorações.

---

## 12. Fluxograma da Etapa 3 — Canonização operacional final

O fluxograma abaixo descreve a Etapa 3 normativa final. Os nomes de funções e scripts representam interfaces finais desejadas da canonização operacional e podem ser implementados por adaptação, renomeação ou encapsulamento das funções atualmente existentes.

```mermaid
flowchart TD

    %% =====================================================
    %% ENTRADA FORMAL DA ETAPA 3
    %% =====================================================

    IN["Entrada formal da Etapa 3<br/>PacoteEntradaResolvida validado<br/>PacoteValidacaoPreExecucao aprovado"]

    %% =====================================================
    %% FUNÇÕES FINAIS DA ETAPA 3
    %% =====================================================

    subgraph E3["Etapa 3 — Canonização operacional"]

        F0["construir_pacote_canonizacao_operacional(...)<br/><br/>Função orquestradora final da Etapa 3"]

        F1["canonizar_carteira(...)<br/><br/>Entrada:<br/>quadros_estruturais_resolvidos/carteira<br/><br/>Saída:<br/>carteira_canonica<br/>mapa_produtos<br/>auditoria_carteira"]

        F2["canonizar_recebidos(...)<br/><br/>Entrada:<br/>quadros_estruturais_resolvidos/salarios<br/><br/>Saída:<br/>recebidos_canonicos<br/>salarios_canonicos<br/>auditoria_recebidos"]

        F3["canonizar_gastos(...)<br/><br/>Entrada:<br/>quadros_estruturais_resolvidos/despesas<br/><br/>Saída:<br/>gastos_canonicos<br/>contas_pagas_canonicas<br/>contas_futuras_canonicas<br/>auditoria_gastos"]

        F4["canonizar_switching(...)<br/><br/>Entrada:<br/>quadros_estruturais_resolvidos/switching<br/><br/>Saída:<br/>switching_canonico<br/>vinculos_origem_destino<br/>auditoria_switching"]

        F5["canonizar_inventario_base(...)<br/><br/>Entrada:<br/>quadros_estruturais_resolvidos/lotes<br/>carteira_canonica<br/><br/>Saída:<br/>inventario_canonico_base<br/>auditoria_inventario_base"]

        F6["normalizar_destinos_pos_switching(...)<br/><br/>Entrada:<br/>switching_canonico<br/>carteira_canonica<br/><br/>Saída:<br/>lotes_pos_switching_normalizados<br/>auditoria_pos_switching"]

        F7["classificar_origens_migradas_switching(...)<br/><br/>Entrada:<br/>inventario_canonico_base<br/>switching_canonico<br/>vinculos_origem_destino<br/><br/>Saída:<br/>origens_migradas_canonicas<br/>auditoria_origens_migradas"]

        F8["construir_inventario_canonico_completo(...)<br/><br/>Entrada:<br/>inventario_canonico_base<br/>lotes_pos_switching_normalizados<br/>origens_migradas_canonicas<br/><br/>Saída:<br/>inventario_canonico<br/>inventario_lotes_expandido<br/>auditoria_inventario_completo"]

        F9["construir_universo_economico_canonico(...)<br/><br/>Entrada:<br/>carteira_canonica<br/>recebidos_canonicos<br/>gastos_canonicos<br/>switching_canonico<br/>inventario_canonico<br/><br/>Saída:<br/>UniversoEconomicoCanonico"]

        F10["auditar_canonizacao_operacional(...)<br/><br/>Entrada:<br/>todos os artefatos canônicos da Etapa 3<br/><br/>Saída:<br/>PacoteAuditoriaCanonizacaoOperacional"]

        F11["montar_pacote_dados_operacionais_canonicos(...)<br/><br/>Entrada:<br/>artefatos canônicos auditados<br/><br/>Saída:<br/>PacoteDadosOperacionaisCanonicos"]

        F0 --> F1
        F0 --> F2
        F0 --> F3
        F0 --> F4
        F0 --> F5

        F1 --> F5
        F1 --> F6

        F4 --> F6
        F4 --> F7

        F5 --> F7
        F5 --> F8
        F6 --> F8
        F7 --> F8

        F1 --> F9
        F2 --> F9
        F3 --> F9
        F4 --> F9
        F8 --> F9

        F1 --> F10
        F2 --> F10
        F3 --> F10
        F4 --> F10
        F8 --> F10
        F9 --> F10

        F10 --> F11
    end

    %% =====================================================
    %% SCRIPTS FINAIS DE AUDITORIA DA ETAPA 3
    %% =====================================================

    subgraph SCRIPTS["Scripts finais de auditoria da Etapa 3"]

        S1["scripts/diagnostico/auditar_etapa3_canonizacao_operacional.py<br/><br/>Verifica:<br/>presença dos artefatos canônicos<br/>shapes mínimos<br/>IDs obrigatórios<br/>datas obrigatórias<br/>valores monetários<br/>auditorias da Etapa 3"]

        S2["scripts/diagnostico/auditar_fluxograma_etapa3_canonizacao_operacional.py<br/><br/>Verifica:<br/>entrada formal<br/>funções finais<br/>saídas formais<br/>ausência de replay/ledger/saída no interior da Etapa 3"]

        S3["scripts/diagnostico/auditar_pos_switching_etapa3.py<br/><br/>Verifica:<br/>destinos POS<br/>origens migradas<br/>vínculos origem-destino<br/>inventário base vs inventário completo"]

        S4["scripts/diagnostico/auditar_contrato_universo_economico_canonico.py<br/><br/>Verifica:<br/>fontes canônicas<br/>produtos canônicos<br/>lotes canônicos<br/>eventos estruturais<br/>relações origem-destino"]

        S1 --> S2
        S2 --> S3
        S3 --> S4
    end

    %% =====================================================
    %% SAÍDAS FORMAIS DA ETAPA 3
    %% =====================================================

    OUT["Saída formal da Etapa 3<br/>PacoteDadosOperacionaisCanonicos<br/>UniversoEconomicoCanonico<br/>PacoteAuditoriaCanonizacaoOperacional"]

    IN --> F0
    F11 --> OUT
    OUT -. "auditado por" .-> S1
```
