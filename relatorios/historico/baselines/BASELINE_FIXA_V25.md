# BASELINE FIXA V25

A V25 preserva a V24 como base estrutural do replay controlado do passado e corrige o modelo base em três pontos: (1) remove arredondamento monetário diário do saldo bruto interno dos lotes, preservando precisão interna; (2) melhora a exaustão do lote no saque quando o alvo líquido praticamente consome todo o valor disponível; (3) adiciona cache diário do CDI do BCB para auditoria e replay, com fallback controlado para taxa de modelo quando a série não puder ser obtida.

A V25 não abre switching econômico, score econômico final, solver, engine completa ou relatório financeiro atual.
