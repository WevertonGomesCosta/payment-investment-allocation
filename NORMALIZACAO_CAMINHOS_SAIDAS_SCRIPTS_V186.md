# Normalização final dos caminhos ativos de saída e scripts diagnósticos canônicos — V186

A V186 consolida:
- `saidas/oficial/` como caminho canônico de artefatos oficiais ativos;
- `saidas/operacional/` como compatibilidade residual de caminho, sem novos artefatos oficiais;
- `saidas/historico/compatibilidade_operacional/` como destino dos artefatos operacionais duplicados rebaixados;
- `saidas/historico/raiz_rebaixada/` como destino dos artefatos antigos antes misturados na raiz de `saidas/`;
- `scripts/diagnostico/` como caminho canônico do tooling de release e inspeção;
- `scripts/historico_raiz/` como destino das cópias antigas movidas da raiz de `scripts/`;
- atualização do `README`, `LEIA-ME_OPERACIONAL`, `INDICE_RELATORIOS`, `saidas/README.md` e `scripts/README.md`;
- remoção de resíduos efêmeros (`__pycache__`, `.pyc`) do pacote.

Nenhuma alteração foi feita no contrato mestre, no modelo oficial, no núcleo econômico ou na estrutura diária por pacotes congelada.
