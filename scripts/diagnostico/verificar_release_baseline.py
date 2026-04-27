from __future__ import annotations

from pathlib import Path

VERSAO_VIGENTE = "V218"
VERSAO_ANTERIOR = "V217"


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
        'relatorios/atuais/INTEGRACAO_FUNCIONAL_APORTES_FUTUROS_V216.md',
        'nucleo/aportes_futuros_planejados.py',
        'scripts/diagnostico/inspecionar_aportes_planejados_v216.py',
        'relatorios/atuais/AUDITORIA_CONSOLE_DIAGNOSTICO_V216.md',
        'relatorios/atuais/AUDITORIA_IMPACTO_CONTAS_FUTURAS_V217.md',
        'relatorios/atuais/VALIDACAO_LOCAL_V217.md',
        'scripts/diagnostico/auditar_impacto_contas_futuras_v217.py',
        'relatorios/atuais/CORRECAO_CALCULO_DIAS_LOTES_V218.md',
        'relatorios/atuais/VALIDACAO_LOCAL_V218.md',
        'scripts/diagnostico/auditar_calculo_dias_lotes_v218.py',
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


def validar_integracao_aportes_futuros_v216(base: Path) -> list[str]:
    erros: list[str] = []

    modulo = base / 'nucleo' / 'aportes_futuros_planejados.py'
    texto_modulo = modulo.read_text(encoding='utf-8') if modulo.exists() else ''
    for termo in [
        'def materializar_aportes_planejados_v216',
        'STATUS_PROMOVIVEL_V216',
        'valor_recebido = valor_pago_com_recebido + valor_aportado + saldo_caixa_remanescente',
        'recebido_id_origem',
    ]:
        if termo not in texto_modulo:
            erros.append(f'aportes_v216_modulo_sem_termo: {termo}')

    simulador = base / 'nucleo' / 'simulador_central_eventos_v1.py'
    texto_simulador = simulador.read_text(encoding='utf-8') if simulador.exists() else ''
    for termo in [
        'from nucleo.aportes_futuros_planejados import materializar_aportes_planejados_v216',
        'materializar_aportes_planejados_v216(estado, data_atual, config, historico)',
        'auditoria_aportes_planejados_v216',
        'integracao_integral_multidestino_v216',
    ]:
        if termo not in texto_simulador:
            erros.append(f'simulador_sem_integracao_aportes_v216: {termo}')

    alocador = base / 'nucleo' / 'alocador_pagamentos_terminal_v1.py'
    texto_alocador = alocador.read_text(encoding='utf-8') if alocador.exists() else ''
    for termo in [
        "liquidez_ate = _coerce_date",
        "origem_aporte_planejado_v216",
        "recebido_id_origem_v216",
        "'status': 'funcional_v216'",
    ]:
        if termo not in texto_alocador:
            erros.append(f'alocador_sem_consumo_aporte_v216: {termo}')

    builder = base / 'nucleo' / 'builders' / 'simulador_central_estado_v117.py'
    texto_builder = builder.read_text(encoding='utf-8') if builder.exists() else ''
    for termo in [
        'valor_recebido_original_v216',
        'valor_pago_com_recebido_v216',
        'saldo_caixa_remanescente_v216',
    ]:
        if termo not in texto_builder:
            erros.append(f'builder_sem_campos_invariante_v216: {termo}')

    diagnostico = base / 'scripts' / 'diagnostico' / 'inspecionar_aportes_planejados_v216.py'
    texto_diag = diagnostico.read_text(encoding='utf-8') if diagnostico.exists() else ''
    if 'simular_cenario_eventos_v1' not in texto_diag or 'to_csv' not in texto_diag:
        erros.append('diagnostico_aportes_v216_nao_executavel_ou_sem_saida_csv')

    for stub in [
        'scripts/auditoria/gerar_auditoria_recebidos_aportes_futuros.py',
        'scripts/auditoria/gerar_politica_elegibilidade_aportes_futuros.py',
        'scripts/auditoria/gerar_transicao_aportes_futuros_planejados.py',
        'scripts/auditoria/gerar_estado_temporal_aportes_planejados_v212.py',
        'scripts/auditoria/gerar_simulacao_cenarios_aportes_planejados_v213.py',
        'scripts/auditoria/gerar_auditoria_liquidez_carencia_aportes_planejados_v214.py',
        'scripts/auditoria/gerar_integracao_controlada_aportes_planejados_v215.py',
    ]:
        caminho = base / stub
        if caminho.exists():
            texto_stub = caminho.read_text(encoding='utf-8')
            if 'Use os CSVs e relatórios já materializados' in texto_stub or 'Script reconstruído' in texto_stub:
                erros.append(f'stub_reconstruido_v209_v215_presente: {stub}')

    return erros


def validar_calculo_dias_lotes_v218(base: Path) -> list[str]:
    erros: list[str] = []

    calendario = base / 'nucleo' / 'calendario_financeiro.py'
    texto_cal = calendario.read_text(encoding='utf-8') if calendario.exists() else ''
    for termo in [
        'def contar_dias_corridos_lote',
        'def contar_dias_uteis_lote',
        'def calcular_dias_lote',
        'data_aplicacao',
    ]:
        if termo not in texto_cal:
            erros.append(f'calendario_sem_calculo_dias_v218: {termo}')

    saida = base / 'nucleo' / 'saida_canonica.py'
    texto_saida = saida.read_text(encoding='utf-8') if saida.exists() else ''
    for termo in [
        'from nucleo.calendario_financeiro import calcular_dias_lote',
        'idade_lote_v218 = calcular_dias_lote',
        'lote.data_aplicacao',
        'data_base_tempo = data_referencia',
    ]:
        if termo not in texto_saida:
            erros.append(f'saida_canonica_sem_calculo_dias_v218: {termo}')
    if 'Dias corridos = max((data_base_tempo - lote.data_recebimento).days' in texto_saida:
        erros.append('saida_canonica_ainda_usa_recebimento_para_dias_corridos')

    replay = base / 'nucleo' / 'replay_passado_controlado.py'
    texto_replay = replay.read_text(encoding='utf-8') if replay.exists() else ''
    if 'idade_lote_log_v218 = calcular_dias_lote' not in texto_replay:
        erros.append('replay_sem_calculo_dias_v218')
    if "'Dias Corridos': max((data_atual - lote.data_base_fiscal).days" in texto_replay:
        erros.append('replay_ainda_usa_base_fiscal_para_dias_corridos')

    auditoria = base / 'scripts' / 'auditoria' / 'gerar_auditoria_diaria_lote.py'
    texto_auditoria = auditoria.read_text(encoding='utf-8') if auditoria.exists() else ''
    if 'idade_lote_v218 = calcular_dias_lote' not in texto_auditoria:
        erros.append('auditoria_diaria_lote_sem_calculo_dias_v218')
    if 'def _contar_dias_uteis_economicos_lote' in texto_auditoria:
        erros.append('auditoria_diaria_lote_ainda_tem_funcao_local_dias_uteis')

    diag = base / 'scripts' / 'diagnostico' / 'auditar_calculo_dias_lotes_v218.py'
    texto_diag = diag.read_text(encoding='utf-8') if diag.exists() else ''
    if 'auditoria_lote_5680_abr_v218_real.csv' not in texto_diag:
        erros.append('diagnostico_v218_sem_auditoria_lote_5680_abr')

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
    erros.extend(validar_integracao_aportes_futuros_v216(base))
    erros.extend(validar_calculo_dias_lotes_v218(base))
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
