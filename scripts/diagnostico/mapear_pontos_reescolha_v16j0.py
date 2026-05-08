from __future__ import annotations
from pathlib import Path
import ast

RAIZ = Path(__file__).resolve().parents[2]

ARQUIVOS = [
    'nucleo/caixa_recebidos_auditaveis.py',
    'nucleo/auditoria_temporal_decisao_local.py',
    'nucleo/ledger_temporal_conjunto.py',
    'nucleo/saida_canonica.py',
]

CHAVES = [
    'lote_resgatavel', 'recebido_disponivel', 'sem_saldo_temporal_auditavel',
    'requer_reescolha_dinamica', 'saldo_temporal_insuficiente_cumulativo',
]


def funcoes(path: Path):
    src = path.read_text(encoding='utf-8')
    tree = ast.parse(src)
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef):
            out.append((n.name, n.lineno))
    return sorted(out, key=lambda x: x[1]), src.splitlines()


def main() -> int:
    print('versao_alvo=V16-J.0')
    print('numero_de_versoes_usadas=1')
    print('fase=mapeamento_do_motor')
    print('alteracao_funcional=nao')

    print('\narquivos_inspecionados:')
    for a in ARQUIVOS:
        print(f'- {a}')

    print('\nfuncoes_candidatas_por_responsabilidade:')
    print('1) escolha de fonte local (lote_resgatavel/recebido_disponivel)')
    print('   - caixa_recebidos_auditaveis._construir_candidatos_decisao_local_v1')
    print('   - caixa_recebidos_auditaveis._selecionar_candidato_decisao_local_v1')
    print('   - caixa_recebidos_auditaveis.materializar_decisao_local_v1')
    print('2) montagem de fontes elegiveis por pagamento')
    print('   - caixa_recebidos_auditaveis.materializar_fontes_elegiveis_pagamento')
    print('   - caixa_recebidos_auditaveis._materializar_fontes_de_recebidos_por_pagamento')
    print('3) validacao temporal cumulativa e sinal de reescolha')
    print('   - auditoria_temporal_decisao_local.carregar_auditoria_temporal_decisao_local')
    print('4) transformacao em evento e bloqueio no ledger')
    print('   - ledger_temporal_conjunto.construir_ledger_temporal_conjunto')
    print('   - ledger_temporal_conjunto._pagamentos_decisao_recebido_disponivel')
    print('5) propagacao para saida final/canonica')
    print('   - saida_canonica._mapa_fontes_elegiveis_auditaveis_por_pagamento')
    print('   - saida_canonica._pagamentos_decisao_recebido_disponivel_fallback_auditavel')

    print('\nfluxo_atual_resumido:')
    print('- fontes elegiveis sao materializadas por pagamento (incluindo recebido_disponivel).')
    print('- decisao local escolhe candidato (pode escolher lote_resgatavel).')
    print('- auditoria temporal calcula cobertura temporal e requer_reescolha_dinamica.')
    print('- ledger aplica validacao cumulativa; pode marcar sem_saldo_temporal_auditavel.')
    print('- saida canonica apenas propaga/normaliza status e fallback auditavel restrito pela decisao.')

    print('\nhipotese_principal_intervencao_v16j1:')
    print('- ponto seguro minimo: entre sinal temporal de quebra (requer_reescolha_dinamica) e commit do evento no ledger,')
    print('  introduzindo reescolha dinamica local por pagamento apenas quando houver recebido_disponivel elegivel+suficiente.')

    print('\nriscos_por_ponto:')
    print('- em decisao local: risco medio/alto (altera ranking de fontes em todos os pagamentos).')
    print('- em auditoria temporal: risco alto se virar decisor (camada deveria auditar, nao decidir).')
    print('- no ledger antes de status final: risco medio (escopo menor, mas sensivel a cronologia cumulativa).')
    print('- na saida canonica: risco alto/metodologico (mascararia causa sem corrigir motor).')

    print('\nrecomendacao_menor_ponto_seguro:')
    print('- aplicar V16-J.1 no ledger_temporal_conjunto, no trecho em que evento seria marcado como')
    print('  saldo_temporal_insuficiente_cumulativo, consultando fontes elegiveis do mesmo pagamento e')
    print('  tentando reescolha dinamica para recebido_disponivel elegivel+suficiente antes de finalizar status.')

    print('\nindicadores_textuais_por_arquivo:')
    for rel in ARQUIVOS:
        p = RAIZ / rel
        funcs, lines = funcoes(p)
        achados = {k: 0 for k in CHAVES}
        txt = '\n'.join(lines).lower()
        for k in CHAVES:
            achados[k] = txt.count(k)
        print(f'- {rel}: {achados}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
