from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execucao direta
    from _bootstrap import RAIZ

from pprint import pprint

from nucleo.alocador_pagamentos_terminal_v1 import DecisaoPagamentoTerminal, alocar_pagamentos_terminal_v1
from nucleo.planejador_switching_temporal_v1 import AcaoSwitchingTemporalCandidata, planejar_switching_temporal_v1


def main() -> int:
    print('=== INSPECAO DO CONTRATO V117 ===')
    print(f'raiz: {RAIZ}')
    print('modulos encontrados:')
    print('- planejador_switching_temporal_v1')
    print('- alocador_pagamentos_terminal_v1')
    print('tipos exportados:')
    print(f'- {AcaoSwitchingTemporalCandidata.__name__}')
    print(f'- {DecisaoPagamentoTerminal.__name__}')
    print('chamada_stub_planejador:')
    pprint(planejar_switching_temporal_v1(estado_global={}))
    print('chamada_stub_alocador:')
    pprint(alocar_pagamentos_terminal_v1(estado_global={}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
