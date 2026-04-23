# Núcleo do motor diário

Reorganização estrutural de baixo risco da V153.

## Fronteiras
- `modelos.py`: dataclasses e contratos leves de serialização.
- `estado.py`: ordenação de pagamentos e montagem do estado de janela.
- `metricas.py`: composição de métricas e chaves de decisão.
- `planejamento.py`: geração e seleção do plano diário de switching.
- `avaliacao.py`: execução de pacote do dia e continuação neutra.

O arquivo histórico `motor_diario_conjunto_experimental_v143.py` permanece como fachada de compatibilidade.
