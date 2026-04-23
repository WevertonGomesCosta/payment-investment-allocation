from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True, slots=True)
class HeuristicaScript1Contratada:
    codigo: str
    nome: str
    fase_absorcao: int
    papel_inicial: str
    origem_legado: str
    objetivo_economico: str
    ativo_para_implementacao: bool
    usar_como_score_auxiliar: bool = False
    usar_como_filtro_triagem: bool = False
    usar_como_desempate: bool = False
    abrir_combinacao_minima: bool = False
    observacao: str = ''

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)
