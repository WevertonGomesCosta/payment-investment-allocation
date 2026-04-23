# Avaliação diária da data ótima de switching — V127

- Objetivo: testar diariamente, desde D0 até o fim do horizonte, qual é a melhor data de switching por lote e por agrupamento, mantendo a análise conjunta até o fim do período.
- Escopo: lotes já investidos e, quando existirem, lotes não aportados disponíveis, com comparação entre cenários individuais e agrupados, sempre em modo integral.
- Observação: a grade diária agora cobre todas as combinações integrais entre as melhores ações por fonte do dia, incluindo fontes não aportadas disponíveis quando existirem.
- Execução pesada: o código foi preparado para rodar em blocos e consolidar a grade diária por partes quando o ambiente interativo não suporta o horizonte completo em uma única passagem.

## Janela auditada

- Data de referência: 2026-04-21
- Janela total teórica do horizonte: 2026-04-21 → 2027-03-31
- Janela efetivamente consolidada nesta auditoria: 2026-04-21 → 2026-06-05
- Quantidade de dias consolidados: 46
- Quantidade de pagamentos futuros no horizonte: 149
- Comparação principal: em cada data, o switching é comparado contra o baseline condicional daquela própria data, após a trajetória sem switching até esse ponto.

## Top global de datas/cenários

- 2026-04-30 | individual_integral | Lote 3000 mar. V
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142855.58, 134.0, 8519.91, 10820.3, 0.0, 29.41, 3.0]
  - Δ perda terminal = 95.4
  - Δ déficit = -500.59
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 780.23
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 448.52}]
- 2026-05-01 | individual_integral | Lote 3000 mar. V
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142855.58, 134.0, 8522.52, 10820.3, 0.0, 29.41, 3.0]
  - Δ perda terminal = 98.01
  - Δ déficit = -500.59
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 775.01
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-01', 'fracao_lote': 1.0, 'ganho_planejador': 446.97}]
- 2026-05-02 | individual_integral | Lote 3000 mar. V
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142855.58, 134.0, 8525.14, 10820.3, 0.0, 29.41, 3.0]
  - Δ perda terminal = 100.63
  - Δ déficit = -500.59
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 769.77
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-02', 'fracao_lote': 1.0, 'ganho_planejador': 445.41}]
- 2026-05-03 | individual_integral | Lote 3000 mar. V
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142855.58, 134.0, 8527.75, 10820.3, 0.0, 29.41, 3.0]
  - Δ perda terminal = 103.24
  - Δ déficit = -500.59
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 764.55
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-03', 'fracao_lote': 1.0, 'ganho_planejador': 443.86}]
- 2026-05-04 | individual_integral | Lote 3000 mar. V
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142855.58, 134.0, 8530.36, 10820.3, 0.0, 29.41, 3.0]
  - Δ perda terminal = 105.85
  - Δ déficit = -500.59
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 759.33
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-04', 'fracao_lote': 1.0, 'ganho_planejador': 442.3}]
- 2026-04-30 | agrupado_integral | Lote 3000 mar. V + Lote 8500 mar.
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142877.53, 134.0, 8214.97, 10461.73, 0.0, 51.36, 4.0]
  - Δ perda terminal = -209.54
  - Δ déficit = -478.64
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 1085.17
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 448.52}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 289.27}]
- 2026-05-01 | agrupado_integral | Lote 3000 mar. V + Lote 8500 mar.
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142877.53, 134.0, 8217.58, 10461.73, 0.0, 51.36, 4.0]
  - Δ perda terminal = -206.93
  - Δ déficit = -478.64
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 1079.95
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-01', 'fracao_lote': 1.0, 'ganho_planejador': 446.97}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-01', 'fracao_lote': 1.0, 'ganho_planejador': 288.2}]
- 2026-05-02 | agrupado_integral | Lote 3000 mar. V + Lote 8500 mar.
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142877.53, 134.0, 8220.2, 10461.73, 0.0, 51.36, 4.0]
  - Δ perda terminal = -204.31
  - Δ déficit = -478.64
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 1074.71
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-02', 'fracao_lote': 1.0, 'ganho_planejador': 445.41}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-02', 'fracao_lote': 1.0, 'ganho_planejador': 287.13}]
- 2026-05-03 | agrupado_integral | Lote 3000 mar. V + Lote 8500 mar.
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142877.53, 134.0, 8222.81, 10461.73, 0.0, 51.36, 4.0]
  - Δ perda terminal = -201.7
  - Δ déficit = -478.64
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 1069.49
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-03', 'fracao_lote': 1.0, 'ganho_planejador': 443.86}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-03', 'fracao_lote': 1.0, 'ganho_planejador': 286.07}]
- 2026-05-04 | agrupado_integral | Lote 3000 mar. V + Lote 8500 mar.
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142877.53, 134.0, 8225.42, 10461.73, 0.0, 51.36, 4.0]
  - Δ perda terminal = -199.09
  - Δ déficit = -478.64
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 1064.27
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-04', 'fracao_lote': 1.0, 'ganho_planejador': 442.3}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-04', 'fracao_lote': 1.0, 'ganho_planejador': 285.0}]
- 2026-04-30 | agrupado_integral | Lote 3000 mar. B + Lote 3000 mar. V
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142884.1, 134.0, 8494.94, 11962.6, 0.0, 57.93, 4.0]
  - Δ perda terminal = 70.43
  - Δ déficit = -472.07
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 1862.57
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. B', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 548.64}, {'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 448.52}]
- 2026-05-01 | agrupado_integral | Lote 3000 mar. B + Lote 3000 mar. V
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142884.1, 134.0, 8500.71, 11962.6, 0.0, 57.93, 4.0]
  - Δ perda terminal = 76.2
  - Δ déficit = -472.07
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 1851.03
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. B', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-01', 'fracao_lote': 1.0, 'ganho_planejador': 546.76}, {'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-01', 'fracao_lote': 1.0, 'ganho_planejador': 446.97}]

## Melhor data por lote ou agrupamento

### individual_integral | Lote 3000 mar. V
- melhor data solicitada: 2026-04-30
- vencedor central: True
- vitória material: True
- vetor: [64.0, 142855.58, 134.0, 8519.91, 10820.3, 0.0, 29.41, 3.0]
- Δ perda terminal: 95.4
- Δ déficit: -500.59
- Δ protegida: 0.0
- Δ patrimônio proxy: 780.23
- eventos: [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 448.52}]

### agrupado_integral | Lote 3000 mar. V + Lote 8500 mar.
- melhor data solicitada: 2026-04-30
- vencedor central: True
- vitória material: True
- vetor: [64.0, 142877.53, 134.0, 8214.97, 10461.73, 0.0, 51.36, 4.0]
- Δ perda terminal: -209.54
- Δ déficit: -478.64
- Δ protegida: 0.0
- Δ patrimônio proxy: 1085.17
- eventos: [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 448.52}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 289.27}]

### agrupado_integral | Lote 3000 mar. B + Lote 3000 mar. V
- melhor data solicitada: 2026-04-30
- vencedor central: True
- vitória material: True
- vetor: [64.0, 142884.1, 134.0, 8494.94, 11962.6, 0.0, 57.93, 4.0]
- Δ perda terminal: 70.43
- Δ déficit: -472.07
- Δ protegida: 0.0
- Δ patrimônio proxy: 1862.57
- eventos: [{'lote_origem_id': 'Lote 3000 mar. B', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 548.64}, {'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 448.52}]

### agrupado_integral | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar.
- melhor data solicitada: 2026-04-30
- vencedor central: True
- vitória material: True
- vetor: [64.0, 142906.05, 134.0, 8189.95, 11604.03, 0.0, 79.88, 4.0]
- Δ perda terminal: -234.56
- Δ déficit: -450.12
- Δ protegida: 0.0
- Δ patrimônio proxy: 2167.56
- eventos: [{'lote_origem_id': 'Lote 3000 mar. B', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 548.64}, {'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 448.52}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 289.27}]

### agrupado_integral | Lote 3000 mar. B + Lote 8500 mar. + Lote 3000 mar. V
- melhor data solicitada: 2026-05-05
- vencedor central: True
- vitória material: True
- vetor: [64.0, 142906.05, 134.0, 8217.26, 11041.08, 0.0, 79.88, 4.0]
- Δ perda terminal: 186.86
- Δ déficit: -1950.12
- Δ protegida: -1.0
- Δ patrimônio proxy: 1208.32
- eventos: [{'lote_origem_id': 'Lote 3000 mar. B', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-05', 'fracao_lote': 1.0, 'ganho_planejador': 539.24}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-05', 'fracao_lote': 1.0, 'ganho_planejador': 283.93}, {'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-05', 'fracao_lote': 1.0, 'ganho_planejador': 163.27}]

### individual_integral | Lote 3000 mar. B
- melhor data solicitada: 2026-05-05
- vencedor central: True
- vitória material: True
- vetor: [64.0, 143384.69, 135.0, 8399.65, 10837.0, 0.0, 28.52, 4.0]
- Δ perda terminal: 369.25
- Δ déficit: -1471.48
- Δ protegida: -1.0
- Δ patrimônio proxy: 672.34
- eventos: [{'lote_origem_id': 'Lote 3000 mar. B', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-05', 'fracao_lote': 1.0, 'ganho_planejador': 539.24}]

### agrupado_integral | Lote 3000 mar. B + Lote 8500 mar.
- melhor data solicitada: 2026-05-05
- vencedor central: True
- vitória material: True
- vetor: [64.0, 143406.64, 135.0, 8093.36, 10478.44, 0.0, 50.47, 4.0]
- Δ perda terminal: 62.96
- Δ déficit: -1449.53
- Δ protegida: -1.0
- Δ patrimônio proxy: 978.63
- eventos: [{'lote_origem_id': 'Lote 3000 mar. B', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-05', 'fracao_lote': 1.0, 'ganho_planejador': 539.24}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-05', 'fracao_lote': 1.0, 'ganho_planejador': 283.93}]

### agrupado_integral | Lote 8500 mar. + Lote 3000 mar. V
- melhor data solicitada: 2026-05-05
- vencedor central: True
- vitória material: True
- vetor: [64.0, 144377.53, 136.0, 7852.66, 9384.73, 0.0, 51.36, 4.0]
- Δ perda terminal: -177.74
- Δ déficit: -478.64
- Δ protegida: -1.0
- Δ patrimônio proxy: 531.33
- eventos: [{'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-05', 'fracao_lote': 1.0, 'ganho_planejador': 283.93}, {'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-05', 'fracao_lote': 1.0, 'ganho_planejador': 163.27}]

### individual_integral | Lote 8500 mar.
- melhor data solicitada: 2026-05-16
- vencedor central: True
- vitória material: True
- vetor: [65.0, 146353.63, 138.0, 8430.1, 9565.92, 0.0, 21.95, 2.0]
- Δ perda terminal: 2346.33
- Δ déficit: -3923.34
- Δ protegida: 0.0
- Δ patrimônio proxy: -2346.33
- eventos: [{'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-05-16', 'fracao_lote': 1.0, 'ganho_planejador': 272.27}]

### individual_integral | Lote 6630,64 fev.
- melhor data solicitada: 2026-04-21
- vencedor central: False
- vitória material: False
- vetor: [64.0, 142826.17, 134.0, 8558.68, 9876.42, 0.0, 0.0, 3.0]
- Δ perda terminal: 0.0
- Δ déficit: 0.0
- Δ protegida: 0.0
- Δ patrimônio proxy: 0.1
- eventos: [{'lote_origem_id': 'Lote 6630,64 fev.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 0.04}]

### agrupado_integral | Lote 8500 mar. + Lote 6630,64 fev.
- melhor data solicitada: 2026-04-21
- vencedor central: False
- vitória material: False
- vetor: [64.0, 142848.12, 134.0, 8253.84, 9517.84, 0.0, 21.95, 4.0]
- Δ perda terminal: -304.84
- Δ déficit: 21.95
- Δ protegida: 0.0
- Δ patrimônio proxy: 304.94
- eventos: [{'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 298.94}, {'lote_origem_id': 'Lote 6630,64 fev.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 0.04}]

### agrupado_integral | Lote 3000 mar. B + Lote 6630,64 fev.
- melhor data solicitada: 2026-04-21
- vencedor central: False
- vitória material: False
- vetor: [64.0, 142854.69, 134.0, 8486.38, 11018.7, 0.0, 28.52, 5.0]
- Δ perda terminal: -72.3
- Δ déficit: 28.52
- Δ protegida: 0.0
- Δ patrimônio proxy: 1158.18
- eventos: [{'lote_origem_id': 'Lote 3000 mar. B', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 565.59}, {'lote_origem_id': 'Lote 6630,64 fev.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 0.04}]

### agrupado_integral | Lote 3000 mar. V + Lote 6630,64 fev.
- melhor data solicitada: 2026-04-21
- vencedor central: False
- vitória material: False
- vetor: [64.0, 142855.58, 134.0, 8486.12, 11019.22, 0.0, 29.41, 5.0]
- Δ perda terminal: -72.56
- Δ déficit: 29.41
- Δ protegida: 0.0
- Δ patrimônio proxy: 1159.21
- eventos: [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 565.12}, {'lote_origem_id': 'Lote 6630,64 fev.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 0.04}]

### agrupado_integral | Lote 3000 mar. B + Lote 8500 mar. + Lote 6630,64 fev.
- melhor data solicitada: 2026-04-21
- vencedor central: False
- vitória material: False
- vetor: [64.0, 142876.64, 134.0, 8181.46, 10660.14, 0.0, 50.47, 5.0]
- Δ perda terminal: -377.22
- Δ déficit: 50.47
- Δ protegida: 0.0
- Δ patrimônio proxy: 1463.1
- eventos: [{'lote_origem_id': 'Lote 3000 mar. B', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 565.59}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 298.94}, {'lote_origem_id': 'Lote 6630,64 fev.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 0.04}]

### agrupado_integral | Lote 3000 mar. V + Lote 8500 mar. + Lote 6630,64 fev.
- melhor data solicitada: 2026-04-21
- vencedor central: False
- vitória material: False
- vetor: [64.0, 142877.53, 134.0, 8181.19, 10660.65, 0.0, 51.36, 5.0]
- Δ perda terminal: -377.49
- Δ déficit: 51.36
- Δ protegida: 0.0
- Δ patrimônio proxy: 1464.14
- eventos: [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 565.12}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 298.94}, {'lote_origem_id': 'Lote 6630,64 fev.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 0.04}]

### agrupado_integral | Lote 3000 mar. B + Lote 3000 mar. V + Lote 6630,64 fev.
- melhor data solicitada: 2026-04-21
- vencedor central: False
- vitória material: False
- vetor: [64.0, 142884.1, 134.0, 8438.62, 12161.51, 0.0, 57.93, 5.0]
- Δ perda terminal: -120.06
- Δ déficit: 57.93
- Δ protegida: 0.0
- Δ patrimônio proxy: 2292.49
- eventos: [{'lote_origem_id': 'Lote 3000 mar. B', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 565.59}, {'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 565.12}, {'lote_origem_id': 'Lote 6630,64 fev.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 0.04}]

### agrupado_integral | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. + Lote 6630,64 fev.
- melhor data solicitada: 2026-04-21
- vencedor central: False
- vitória material: False
- vetor: [64.0, 142906.05, 134.0, 8133.63, 11802.94, 0.0, 79.88, 5.0]
- Δ perda terminal: -425.05
- Δ déficit: 79.88
- Δ protegida: 0.0
- Δ patrimônio proxy: 2597.48
- eventos: [{'lote_origem_id': 'Lote 3000 mar. B', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 565.59}, {'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 565.12}, {'lote_origem_id': 'Lote 8500 mar.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 298.94}, {'lote_origem_id': 'Lote 6630,64 fev.', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-21', 'fracao_lote': 1.0, 'ganho_planejador': 0.04}]

## Leitura operacional

- Quantidade de cenários diários vencedores em D0: 0
- Quantidade de cenários diários vencedores em D+1: 0
- A decisão correta deixa de ser um único horizonte e passa a ser uma grade diária de datas possíveis, mantendo a trajetória conjunta após o switching integral individual ou agrupado.
- O simulador continua após a data escolhida até o fim do horizonte, já com o switching/aporte realizado e impactando pagamentos futuros.
- Cada delta do relatório é calculado contra o baseline condicional do mesmo dia, e não contra um único baseline fixo de D0.
