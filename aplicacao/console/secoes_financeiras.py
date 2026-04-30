from __future__ import annotations

"""
LEGADO INATIVO — V225

Este módulo foi preservado apenas para rastreabilidade histórica.

A rota oficial não deve importar este arquivo. A apresentação compartilhada entre
console e planilha deve ser implementada em `nucleo/saida_observavel.py` e
renderizada por:

- `aplicacao/console/principal.py`
- `nucleo/gerar_planilha_operacional.py`

Não reativar funções antigas deste módulo sem nova auditoria.
"""


def render_secao_situacao_atual(*args, **kwargs):
    """Função legada neutralizada.

    Use `nucleo/saida_observavel.py` como fonte única para Situação Atual.
    """
    raise RuntimeError(
        "render_secao_situacao_atual está neutralizada. "
        "Use nucleo/saida_observavel.py como fonte única."
    )
