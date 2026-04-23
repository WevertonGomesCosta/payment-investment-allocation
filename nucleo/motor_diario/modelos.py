from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class PacoteDiaResumoV143:
    data: str
    tipo_pacote: str
    possui_pagamentos_no_dia: bool
    pagamentos_dia: int
    pagamentos_ids: list[str]
    switching_considerado: bool
    switching_executado: bool
    rotulo_switching: str | None
    classe_switching: str | None
    eventos_switching: int
    metrica_dia: dict[str, float]
    metrica_total_estimada: dict[str, float]
    vetor_total_estimado: tuple[float, float, float, float, float, float, float, float]
    patrimonio_terminal_proxy_estimado: float
    resultados_pagamento: list[dict[str, Any]]

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DecisaoDiaV143:
    data: str
    tipo_dia: str
    quantidade_pagamentos: int
    pagamentos_ids: list[str]
    descricao_pagamentos: list[str]
    pacote_vencedor: str
    justificativa_vencedor: str
    patrimonio_terminal_proxy_estimado_vencedor: float
    vetor_total_estimado_vencedor: tuple[float, float, float, float, float, float, float, float]
    candidatos: list[dict[str, Any]]

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ResumoMotorV143:
    data_inicio: str
    data_fim: str
    dias_no_horizonte: int
    dias_com_pagamento: int
    pagamentos_no_horizonte: int
    decisoes_switch_then_pay: int
    decisoes_pay_only: int
    decisoes_switch_only: int
    decisoes_no_action: int
    patrimonio_liquido_terminal_proxy_final: float
    metrica_central_final: dict[str, float]
    contagem_fontes_pagamento: dict[str, int]

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)
