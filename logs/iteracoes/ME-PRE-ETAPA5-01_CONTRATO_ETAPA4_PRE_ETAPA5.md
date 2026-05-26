# ME-PRE-ETAPA5-01 - Contrato da Etapa 4 antes da Etapa 5

## Objetivo

Atualizar documentalmente o contrato mestre antes da abertura funcional da Etapa 5, reforcando a Etapa 4 como construcao do estado temporal inicial e removendo ambiguidade normativa sobre artefatos transitorios, diagnosticos ou compativeis.

## Baseline de entrada

9036c79d8af0f81e7597cb7deb2b379efe805535

## Escopo permitido

- relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md
- logs/iteracoes/ME-PRE-ETAPA5-01_CONTRATO_ETAPA4_PRE_ETAPA5.md

## Escopo proibido

Nao alterar aplicacao, nucleo, dados, scripts/diagnostico, saidas, motor, replay, saida canonica, console, XLSX, regra economica ou dados/cache_bcb.json.

## Diagnostico contratual

A secao 7-E.5 do contrato mestre ja estabelecia a existencia do estado temporal inicial antes do motor temporal conjunto, mas ainda estava sintetica e nao explicitava suficientemente as fronteiras pre-Etapa 5.

O contrato historico ME-V17-F0-V4B contem elementos uteis sobre replay, ledger temporal, estado temporal e auditoria temporal. Contudo, tambem contem linguagem de transicao que nao deve ser promovida como norma viva neste momento, especialmente shadow, adaptador shadow, integracao shadow, contexto amplo, fallback legado, pontes de compatibilidade e orquestracao da Etapa 4 pela saida canonica.

## Alteracoes no contrato mestre

A secao 7-E.5 deve ser reforcada para declarar que a Etapa 4 recebe dados operacionais canonicos da Etapa 3, consome o inventario canonico completo, constroi o estado temporal inicial, normaliza lotes ativos, vencidos, exauridos, futuros e disponiveis, materializa recebidos ja disponiveis, mantem recebidos futuros como indisponiveis, preserva pagamentos vencidos e futuros como obrigacoes temporais sem decidir pagamento, registra switchings ja declarados/materializados quando aplicavel e prepara elegibilidades temporais e restricoes de liquidez, carencia, vencimento e disponibilidade.

A mesma secao deve proibir que a Etapa 4 decida pagamento, decida switching candidato, promova switching, execute pacote do dia, gere ledger canonico do pacote escolhido, gere saida canonica, corrija saida, renderize console ou XLSX, substitua ContextoBaseline por adaptador, promova ContextoSaidaCanonicaCompat, use fallback legado como regra normativa ou use pontes shadow/compativeis como rota viva.

## Decisoes arquiteturais

ContextoBaseline permanece runtime legado/transitorio, aceito apenas enquanto a rota oficial ainda depender dele.

ContextoOperacionalCanonico e o alvo canonico das Etapas 1-4.

ContextoSaidaCanonicaCompat fica classificado como artefato diagnostico de equivalencia observavel concluida. Ele nao e camada normativa, runtime oficial ou arquitetura viva. Nao deve ser promovido nem mantido como ponte canonica antes da Etapa 5.

Qualquer remocao fisica de ContextoSaidaCanonicaCompat e comparadores associados deve ocorrer em microetapa propria posterior, fora desta ME-PRE-ETAPA5-01.

## Etapa 5

A Etapa 5 funcional ainda nao foi iniciada nesta microetapa.

## Validacoes esperadas

Validar que o diff fique restrito ao contrato mestre e a este log. Rodar tambem py_compile, aplicacao/principal.py e auditar_nucleo_vivo_v4z.py --sem-arquivos.

## Proxima etapa recomendada

ME-PRE-ETAPA5-02 - remover ou arquivar fisicamente os artefatos compat transitorios pos-equivalencia, especialmente ContextoSaidaCanonicaCompat e comparadores associados, se confirmado que nao sao importados pela rota oficial.
