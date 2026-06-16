from __future__ import annotations

from typing import Iterable, Sequence


def imprimir_titulo(texto: str) -> None:
    print(f"\n=== {texto} ===")


def _suprimir_linha_saida_principal(linha: dict[str, object]) -> bool:
    metrica = formatar_valor_tabela(linha.get('Métrica') or linha.get('metrica')).strip().lower()
    return metrica == 'origem da amostra'


def imprimir_pares(pares: Iterable[tuple[str, object]]) -> None:
    for chave, valor in pares:
        if str(chave).strip().lower() == 'origem da amostra':
            continue
        print(f"- {chave}: {valor}")


def normalizar_lista(itens: Iterable[object] | None) -> list[str]:
    if not itens:
        return []
    return [str(item) for item in itens]


def severidade(*, erros: Iterable[object] | None = None, avisos: Iterable[object] | None = None, condicao_ok: bool = True) -> str:
    erros_norm = normalizar_lista(erros)
    avisos_norm = normalizar_lista(avisos)
    if erros_norm:
        return 'ERRO'
    if avisos_norm or not condicao_ok:
        return 'AVISO'
    return 'OK'


def imprimir_linha_status(rotulo: str, severidade_texto: str, detalhe: str = '') -> None:
    sufixo = f" — {detalhe}" if detalhe else ''
    print(f"[{severidade_texto}] {rotulo}{sufixo}")


def imprimir_itens_severidade(rotulo: str, itens: Iterable[object] | None, severidade_texto: str) -> None:
    itens_norm = normalizar_lista(itens)
    if not itens_norm:
        return
    print(f"- {rotulo}:")
    for item in itens_norm:
        print(f"  [{severidade_texto}] {item}")


def formatar_valor_tabela(valor: object) -> str:
    if valor is None:
        return ''
    if isinstance(valor, float):
        return f"{valor:.2f}"
    return str(valor)


def imprimir_tabela(colunas: Sequence[str], linhas: Sequence[dict[str, object]], *, limite: int | None = None) -> None:
    linhas_use = list(linhas[:limite] if limite is not None else linhas)
    linhas_use = [linha for linha in linhas_use if not _suprimir_linha_saida_principal(linha)]
    if not linhas_use:
        print('  [OK] sem linhas para exibir')
        return
    larguras = {}
    for col in colunas:
        larguras[col] = len(col)
        for linha in linhas_use:
            larguras[col] = max(larguras[col], len(formatar_valor_tabela(linha.get(col))))
    cab = ' | '.join(col.ljust(larguras[col]) for col in colunas)
    sep = '-+-'.join('-' * larguras[col] for col in colunas)
    print(cab)
    print(sep)
    for linha in linhas_use:
        print(' | '.join(formatar_valor_tabela(linha.get(col)).ljust(larguras[col]) for col in colunas))
