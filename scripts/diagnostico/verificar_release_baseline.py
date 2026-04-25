from __future__ import annotations

from pathlib import Path

VERSAO_VIGENTE = "V208"
VERSAO_ANTERIOR = "V207"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def rel(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def coletar_artefatos_efemeros(base: Path) -> list[str]:
    itens: list[str] = []
    for path in base.rglob('__pycache__'):
        itens.append(rel(path, base))
    for path in base.rglob('*.pyc'):
        itens.append(rel(path, base))
    return sorted(set(itens))


def validar_indice_documental(base: Path) -> list[str]:
    erros: list[str] = []
    indice = base / 'relatorios' / 'INDICE_RELATORIOS.md'
    esperado = [
        'relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md',
        'relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md',
        'relatorios/atuais/LEIA-ME_OPERACIONAL.md',
        'relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md',
    ]
    if not indice.exists():
        return ['relatorios/INDICE_RELATORIOS.md ausente']
    conteudo = indice.read_text(encoding='utf-8')
    for item in esperado:
        if item not in conteudo:
            erros.append(f'indice_documental_sem_referencia: {item}')
    return erros


def validar_referencias_ativas(base: Path) -> list[str]:
    erros: list[str] = []
    alvos = [
        base / 'README.md',
        base / 'relatorios' / 'atuais',
        base / 'scripts' / 'README.md',
        base / 'saidas' / 'README.md',
    ]
    padroes_bloqueados = [
        'BASELINE_FIXA_V141.md',
        'VALIDACAO_LOCAL_V141.md',
        'ESTRUTURA_REPOSITORIO_V141.md',
    ]
    script_proprio = (base / 'scripts' / 'diagnostico' / 'verificar_release_baseline.py').resolve()
    ignorar = {script_proprio}
    for alvo in alvos:
        caminhos = [alvo] if alvo.is_file() else [p for p in alvo.rglob('*') if p.is_file() and p.suffix in {'.py', '.md'}]
        for caminho in caminhos:
            if caminho.resolve() in ignorar:
                continue
            texto = caminho.read_text(encoding='utf-8')
            for padrao in padroes_bloqueados:
                if padrao in texto:
                    erros.append(f'referencia_ativa_indevida: {rel(caminho, base)} -> {padrao}')
    return erros


def validar_caminhos_canonicos(base: Path) -> list[str]:
    esperados = [
        'scripts/diagnostico/verificar_release_baseline.py',
        'scripts/diagnostico/README.md',
        'scripts/operacional/README.md',
        'scripts/auditoria/README.md',
        'scripts/historico_raiz/README.md',
        'saidas/README.md',
        'saidas/oficial/README.md',
        'saidas/diagnostico/README.md',
        'saidas/historico/README.md',
        'saidas/operacional/README.md',
        'scripts/operacional/gerar_planilha_operacional.py',
        'nucleo/saida_canonica.py',
        'scripts/auditoria/gerar_auditoria_diaria_lote.py',
        'scripts/diagnostico/inspecionar_base.py',
        'scripts/diagnostico/_governanca_saida.py',
        'scripts/historico_saida_propria_v203/README.md',
        'relatorios/atuais/GOVERNANCA_SCRIPTS_V203.md',
        'relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv',
        'relatorios/atuais/GOVERNANCA_FINAL_SCRIPTS_V204.md',
        'relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv',
        'relatorios/atuais/HOTFIX_CONSOLE_IMPORTS_V205.md',
        'relatorios/atuais/GOVERNANCA_ESTRUTURAL_V206.md',
        'relatorios/atuais/MAPA_CENTRALIZACAO_HELPERS_V206.csv',
        'relatorios/atuais/HOTFIX_UTILITARIOS_SERIES_V207.md',
        'relatorios/atuais/CORRECAO_SALDOS_FUTUROS_LOTES_V208.md',
    ]
    erros: list[str] = []
    for caminho in esperados:
        if not (base / caminho).exists():
            erros.append(f'caminho_canonico_ausente: {caminho}')
    return erros



def validar_governanca_scripts_v203(base: Path) -> list[str]:
    erros: list[str] = []
    mapa = base / 'relatorios' / 'atuais' / 'MAPA_GOVERNANCA_SCRIPTS_V203.csv'
    if not mapa.exists():
        return ['mapa_governanca_scripts_v203_ausente']
    linhas = mapa.read_text(encoding='utf-8').splitlines()
    bloqueados = [linha.split(',', 1)[0] for linha in linhas[1:] if ',BLOQUEADO_COM_STUB,' in linha]
    for rel_path in bloqueados:
        caminho = base / rel_path
        if not caminho.exists():
            erros.append(f'script_bloqueado_ausente: {rel_path}')
            continue
        conteudo = caminho.read_text(encoding='utf-8')
        if 'BLOQUEADO_POR_GOVERNANCA_V203' not in conteudo and 'bloquear_script_legado' not in conteudo:
            erros.append(f'script_sem_bloqueio_v203: {rel_path}')
    for rel_path in [
        'scripts/diagnostico/inspecionar_motor_recomendacao_pagamentos_switching_v1.py',
        'scripts/diagnostico/inspecionar_recomputacao_sequencial_central_v1.py',
    ]:
        caminho = base / rel_path
        conteudo = caminho.read_text(encoding='utf-8') if caminho.exists() else ''
        if 'construir_saida_canonica' not in conteudo:
            erros.append(f'diagnostico_util_nao_canonico: {rel_path}')
    return erros


def validar_governanca_scripts_v204(base: Path) -> list[str]:
    erros: list[str] = []
    mapa = base / 'relatorios' / 'atuais' / 'MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv'
    if not mapa.exists():
        return ['mapa_governanca_scripts_v204_ausente']

    console = base / 'aplicacao' / 'console' / 'principal.py'
    texto_console = console.read_text(encoding='utf-8') if console.exists() else ''
    funcoes_mortas = [
        '_mapa_pagamentos_central',
        '_mapa_saldo_disponivel',
        '_mapa_saldos_correntes_lotes',
        '_mapa_resumos_futuros_operacionais',
        '_resumo_financeiro_futuro_console',
        '_montar_switchings_oficiais',
        '_preparar_amostras_pagamentos_console',
    ]
    for nome in funcoes_mortas:
        if f'def {nome}' in texto_console:
            erros.append(f'codigo_morto_console_presente: {nome}')

    ranking = base / 'scripts' / 'diagnostico' / 'inspecionar_ranking_carteira_estabilizado_v123.py'
    texto_ranking = ranking.read_text(encoding='utf-8') if ranking.exists() else ''
    if 'to_excel(' in texto_ranking or 'to_csv(' in texto_ranking or 'write_text(' in texto_ranking:
        erros.append('diagnostico_ranking_ainda_escreve_saida_propria')
    if 'construir_saida_canonica' not in texto_ranking:
        erros.append('diagnostico_ranking_nao_canonico')

    auditoria_lote = base / 'scripts' / 'auditoria' / 'gerar_auditoria_diaria_lote.py'
    texto_auditoria = auditoria_lote.read_text(encoding='utf-8') if auditoria_lote.exists() else ''
    if 'caminho_saida_operacional' in texto_auditoria:
        erros.append('auditoria_diaria_lote_ainda_usa_saida_operacional')
    if 'caminho_saida_diagnostico' not in texto_auditoria:
        erros.append('auditoria_diaria_lote_sem_saida_diagnostica')

    for raiz_hist in [
        base / 'scripts' / 'historico_raiz',
        base / 'scripts' / 'historico_saida_propria_v203',
    ]:
        if not raiz_hist.exists():
            continue
        for script in raiz_hist.rglob('*.py'):
            conteudo = script.read_text(encoding='utf-8')
            if 'BLOQUEADO_POR_GOVERNANCA_V204' not in conteudo:
                erros.append(f'historico_py_nao_bloqueado_v204: {rel(script, base)}')

    util = base / 'nucleo' / 'utilitarios_neutros.py'
    texto_util = util.read_text(encoding='utf-8') if util.exists() else ''
    for nome in ['_safe_float', '_coerce_date', '_split_fontes_compostas']:
        if f'def {nome}' not in texto_util:
            erros.append(f'helper_utilitario_nao_centralizado: {nome}')

    for modulo in [
        base / 'nucleo' / 'motor_recomendacao_pagamentos_switching_v1.py',
        base / 'nucleo' / 'recomputacao_sequencial_central_v1.py',
    ]:
        conteudo = modulo.read_text(encoding='utf-8') if modulo.exists() else ''
        if 'def _split_fontes_compostas' in conteudo:
            erros.append(f'split_fontes_compostas_duplicado: {rel(modulo, base)}')
        if 'from nucleo.utilitarios_neutros import' not in conteudo:
            erros.append(f'modulo_sem_utilitarios_centralizados: {rel(modulo, base)}')

    return erros



def validar_governanca_estrutural_v206(base: Path) -> list[str]:
    erros: list[str] = []
    util = base / 'nucleo' / 'utilitarios_neutros.py'
    texto_util = util.read_text(encoding='utf-8') if util.exists() else ''
    for nome in ['_rotulo_fonte', '_fonte_id', '_normalizar_proxy_terminal', '_aliquota_ir_estimada']:
        if f'def {nome}' not in texto_util:
            erros.append(f'helper_semantico_nao_centralizado_v206: {nome}')

    modulos = [
        base / 'nucleo' / 'alocador_pagamentos_terminal_v1.py',
        base / 'nucleo' / 'auditoria_temporal_decisao_local.py',
        base / 'nucleo' / 'caixa_recebidos_auditaveis.py',
        base / 'nucleo' / 'heuristica_conjunta_parcial_bloco_critico.py',
        base / 'nucleo' / 'microplanejamento_conjunto_bloco_critico_v2.py',
        base / 'nucleo' / 'planejador_switching_temporal_v1.py',
        base / 'nucleo' / 'planejamento_conjunto_local_bloco_critico_v1.py',
        base / 'nucleo' / 'recomputacao_sequencial_central_v1.py',
        base / 'nucleo' / 'reescolha_dinamica_pos_quebra.py',
        base / 'nucleo' / 'simulador_central_eventos_v1.py',
    ]
    duplicados = ['_rotulo_fonte', '_fonte_id', '_normalizar_proxy_terminal', '_aliquota_ir_estimada']
    for modulo in modulos:
        conteudo = modulo.read_text(encoding='utf-8') if modulo.exists() else ''
        for nome in duplicados:
            if f'def {nome}' in conteudo:
                erros.append(f'helper_semantico_duplicado_v206: {rel(modulo, base)}::{nome}')

    if (base / 'saidas' / 'oficial' / 'relatorio_operacional_v202.xlsx').exists():
        erros.append('relatorio_v202_ainda_em_saida_oficial')
    if not (base / 'saidas' / 'historico' / 'relatorios_operacionais' / 'relatorio_operacional_v202.xlsx').exists():
        erros.append('relatorio_v202_nao_movido_para_historico')
    return erros

def main() -> int:
    base = repo_root()
    erros = []
    erros.extend(validar_indice_documental(base))
    erros.extend(validar_referencias_ativas(base))
    erros.extend(validar_caminhos_canonicos(base))
    erros.extend(validar_governanca_scripts_v203(base))
    erros.extend(validar_governanca_scripts_v204(base))
    erros.extend(validar_governanca_estrutural_v206(base))
    artefatos = coletar_artefatos_efemeros(base)
    if artefatos:
        erros.extend(f'artefato_efemero_presente: {item}' for item in artefatos)
    if erros:
        print('ERROS DE RELEASE:')
        for erro in erros:
            print(f'- {erro}')
        return 1
    print('OK - release baseline validado para', VERSAO_VIGENTE)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
