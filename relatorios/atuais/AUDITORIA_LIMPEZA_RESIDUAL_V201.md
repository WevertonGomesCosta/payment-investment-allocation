# AUDITORIA E LIMPEZA RESIDUAL — V201

## 1. Decisão aplicada

A V201 aplica a limpeza segura aprovada sobre a V200, sem alterar o motor principal, o contrato mestre ou o modelo matemático-estatístico-financeiro.

## 2. Escopo executado

- Rebaixamento de documentos versionados antigos que estavam na raiz.
- Rebaixamento de relatórios operacionais antigos que estavam em `saidas/oficial/`.
- Rebaixamento de artefatos JSON/MD antigos que competiam visualmente com a saída operacional vigente.
- Atualização da documentação de navegação para indicar V201 como pacote operacional de limpeza.
- Criação do manifesto de scripts `MAPA_SCRIPTS_V201.md`.
- Preservação integral do núcleo econômico e dos módulos funcionais do motor.

## 3. Movimentações realizadas

- moved: `RESUMO_ATUALIZACAO_V190.md` → `relatorios/historico/limpeza_repositorio/RESUMO_ATUALIZACAO_V190.md`
- moved: `CORRECAO_SAIDA_OFICIAL_V192.md` → `relatorios/historico/limpeza_repositorio/CORRECAO_SAIDA_OFICIAL_V192.md`
- moved: `CORRECAO_COMPATIBILIDADE_PANDAS_V199.md` → `relatorios/historico/limpeza_repositorio/CORRECAO_COMPATIBILIDADE_PANDAS_V199.md`
- moved: `saidas/oficial/relatorio_operacional_v192.xlsx` → `saidas/historico/relatorios_operacionais/relatorio_operacional_v192.xlsx`
- moved: `saidas/oficial/relatorio_operacional_v199.xlsx` → `saidas/historico/relatorios_operacionais/relatorio_operacional_v199.xlsx`
- moved: `saidas/oficial/ALOCADOR_PAGAMENTOS_TERMINAL_V137.md` → `saidas/historico/compatibilidade_operacional/ALOCADOR_PAGAMENTOS_TERMINAL_V137.md`
- moved: `saidas/oficial/alocador_pagamentos_terminal_v137.json` → `saidas/historico/compatibilidade_operacional/alocador_pagamentos_terminal_v137.json`
- moved: `saidas/oficial/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138.md` → `saidas/historico/compatibilidade_operacional/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138_origem_oficial_1.md`
- moved: `saidas/oficial/fluxo_pagamentos_terminal_recorte_curto_v138.json` → `saidas/historico/compatibilidade_operacional/fluxo_pagamentos_terminal_recorte_curto_v138_origem_oficial_1.json`
- moved: `saidas/oficial/fluxo_pagamentos_terminal_recorte_amplo_v142.json` → `saidas/historico/compatibilidade_operacional/fluxo_pagamentos_terminal_recorte_amplo_v142.json`

## 4. Arquivos mantidos como oficiais ativos

- `saidas/oficial/README.md`
- `saidas/oficial/relatorio_operacional_v200.xlsx`

## 5. Garantias da V201

- `nucleo/` não foi reorganizado nem limpo por nome versionado; a única alteração nesse bloco foi a identidade operacional `VERSAO_BASELINE = "V201"`.
- A lógica econômica do motor não foi alterada.
- A V200 permanece como referência funcional imediatamente anterior.
- `relatorio_operacional_v200.xlsx` permanece como saída operacional oficial ativa enquanto não houver nova geração econômica.
- Scripts históricos foram preservados, mas continuam sem autoridade operacional.
- A frente de aportes/recebidos futuros ainda não alocados em carteira permanece registrada como etapa futura.

## 6. Risco residual preservado para próxima etapa

A duplicação funcional entre console e planilha ainda existe. A V201 apenas documenta e organiza o repositório; ela não cria a camada única de saída. A etapa seguinte deve criar uma camada canônica de observabilidade para impedir divergências entre console, `.xlsx`, JSON/CSV e markdown.

## 7. Próxima frente recomendada

**V202 — contrato e implementação inicial da camada única de saída canônica**, sem alteração do motor econômico.

Critério mínimo da V202:

1. console e `.xlsx` devem ler o mesmo pacote de dados materializados;
2. nenhum renderizador deve recalcular saldo, líquido, imposto, switching, residual ou data sugerida;
3. o release checker deve validar não divergência entre saída tabular e console.
