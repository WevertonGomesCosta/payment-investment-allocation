"""Canonização estrutural da aba Carteira.

Este módulo mantém a aba `Carteira` como universo único de produtos do projeto.
Ele resolve colunas, constrói o cadastro canônico de produtos, deriva metadados
estruturais neutros (família, regimes e elegibilidade básica) e valida a
consistência mínima antes que o motor faça a triagem contextual.

Importante: parte desses metadados ainda é derivada em código como **ponte
transitória** até que a planilha carregue esses campos de forma mais
estruturada.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd

from nucleo.leitor_planilha import PacotePlanilha, resolver_coluna
from nucleo.utilitarios_neutros import limpar_texto, para_bool, para_float_monetario, para_int, normalizar_texto


@dataclass(slots=True)
class PacoteCarteiraCanonica:
    nome_aba: str
    quadro_bruto: pd.DataFrame
    quadro_canonico: pd.DataFrame
    mapa_produtos: dict[str, dict[str, Any]]
    auditoria: dict[str, Any]
    validacao: dict[str, Any]


def normalizar_nome_produto(valor: Any) -> str:
    return normalizar_texto(valor)


def gerar_produto_key(produto_id: Any, nome_norm: str) -> str:
    produto_id_txt = "" if produto_id is None else str(produto_id).strip()
    if produto_id_txt:
        return produto_id_txt
    return f"prod::{nome_norm}"


def _normalizar_taxa_cdi(valor: Any, *, default: float = 0.0, limite_percentual_vs_multiplicador: float = 10.0) -> float:
    taxa = para_float_monetario(valor, default)
    if taxa >= limite_percentual_vs_multiplicador:
        return taxa / 100.0
    return taxa


def _derivar_familia_produto(tipo: str, indexador: str, *, permite_combo: bool, produto_base: str, produto_bonus: str) -> str:
    tipo_norm = normalizar_texto(tipo)
    indexador_norm = normalizar_texto(indexador)
    if permite_combo or produto_base or produto_bonus or 'combo' in tipo_norm:
        return 'combo'
    if 'cdb' in tipo_norm and 'cdi escalonado' in indexador_norm:
        return 'cdb_cdi_escalonado'
    if 'cdb' in tipo_norm and 'selic' in indexador_norm:
        return 'cdb_selic'
    if 'cdb' in tipo_norm and 'ipca' in indexador_norm:
        return 'cdb_ipca'
    if 'cdb' in tipo_norm and 'prefix' in indexador_norm:
        return 'cdb_prefixado'
    if 'cdb' in tipo_norm and 'cdi' in indexador_norm:
        return 'cdb_cdi'
    if 'lci' in tipo_norm and 'cdi' in indexador_norm:
        return 'lci_cdi'
    if 'lca' in tipo_norm and 'cdi' in indexador_norm:
        return 'lca_cdi'
    if 'fundo prev' in tipo_norm and 'variavel' in indexador_norm:
        return 'fundo_prev_variavel'
    if 'fundo prev' in tipo_norm:
        return 'fundo_prev'
    if 'fundo' in tipo_norm and 'variavel' in indexador_norm:
        return 'fundo_variavel'
    if 'fundo' in tipo_norm and ('cdi' in indexador_norm or 'selic' in indexador_norm or 'ipca' in indexador_norm):
        return 'fundo_renda_fixa'
    if 'fundo' in tipo_norm:
        return 'fundo'
    if 'renda fixa' in tipo_norm:
        return 'renda_fixa'
    return tipo_norm or 'produto'


def _derivar_regime_taxa(indexador: str, taxa_base_cdi: float, taxa_bonus_cdi: float, dias_bonus: int, *, permite_combo: bool, produto_base: str, produto_bonus: str) -> str:
    indexador_norm = normalizar_texto(indexador)
    if permite_combo or produto_base or produto_bonus:
        return 'combo'
    if 'variavel' in indexador_norm:
        return 'variavel'
    if 'selic' in indexador_norm:
        return 'selic'
    if 'prefix' in indexador_norm:
        return 'prefixado'
    if 'ipca' in indexador_norm:
        return 'ipca'
    if 'escalonado' in indexador_norm:
        return 'cdi_escalonado'
    if dias_bonus > 0 and taxa_bonus_cdi > 0 and abs(taxa_bonus_cdi - taxa_base_cdi) > 1e-9:
        return 'cdi_bonus'
    if 'cdi' in indexador_norm or abs(taxa_base_cdi) > 0:
        return 'cdi_base'
    return 'desconhecido'


def _derivar_regime_liquidez(carencia_dias: int, liquidez_dias: int, prazo_dias: int, *, permite_combo: bool) -> str:
    if permite_combo:
        return 'combo'
    bloqueio = max(int(carencia_dias or 0), int(liquidez_dias or 0))
    if bloqueio <= 0:
        return 'liquidez_imediata'
    if prazo_dias > 0 and bloqueio >= prazo_dias:
        return 'vencimento'
    return 'carencia'


def _derivar_papel_produto(ativo: bool, elegivel_motor: bool) -> str:
    if ativo and elegivel_motor:
        return 'ativo_motor'
    if ativo and not elegivel_motor:
        return 'observacional'
    return 'historico_observado'


def _fonte_campo_estruturado(valor_original: Any) -> str:
    texto = limpar_texto(valor_original)
    return 'planilha' if texto else 'derivado'


def _normalizar_regra_iof(valor: Any) -> str:
    txt = normalizar_texto(valor)
    if not txt:
        return 'a_confirmar'
    if txt in {'nao incide', 'nao_incide', 'sem iof', 'isento iof'}:
        return 'nao_incide'
    if txt in {'regressiva 30d', 'regressiva_30d', 'regressivo 30d', 'tabela regressiva'}:
        return 'regressiva_30d'
    if txt in {'a confirmar', 'a_confirmar'}:
        return 'a_confirmar'
    return ''


def _normalizar_semantica_taxa_base(valor: Any) -> str:
    txt = normalizar_texto(valor)
    mapa = {
        'percentual cdi': 'percentual_cdi',
        'percentual_cdi': 'percentual_cdi',
        'percentual cdi escalonado': 'percentual_cdi_escalonado',
        'percentual_cdi_escalonado': 'percentual_cdi_escalonado',
        'percentual selic': 'percentual_selic',
        'percentual_selic': 'percentual_selic',
        'spread selic aa': 'spread_selic_aa',
        'spread_selic_aa': 'spread_selic_aa',
        'spread ipca aa': 'spread_ipca_aa',
        'spread_ipca_aa': 'spread_ipca_aa',
        'taxa prefixada aa': 'taxa_prefixada_aa',
        'taxa_prefixada_aa': 'taxa_prefixada_aa',
        'comparativo cdi historico': 'comparativo_cdi_historico',
        'comparativo_cdi_historico': 'comparativo_cdi_historico',
        'benchmark cdi fundo': 'benchmark_cdi_fundo',
        'benchmark_cdi_fundo': 'benchmark_cdi_fundo',
        'proxy variavel': 'proxy_variavel',
        'proxy_variavel': 'proxy_variavel',
        'hibrido cdi prefixado': 'hibrido_cdi_prefixado',
        'hibrido_cdi_prefixado': 'hibrido_cdi_prefixado',
        'a confirmar': 'a_confirmar',
        'a_confirmar': 'a_confirmar',
    }
    if not txt:
        return 'a_confirmar'
    return mapa.get(txt, '')


def normalizar_carteira_bruta(df_carteira: pd.DataFrame, config: Mapping[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    campos = {
        'produto_id': resolver_coluna(df_carteira, config, 'carteira', 'produto_id', obrigatoria=False),
        'nome': resolver_coluna(df_carteira, config, 'carteira', 'nome', obrigatoria=True),
        'tipo': resolver_coluna(df_carteira, config, 'carteira', 'tipo', obrigatoria=False),
        'indexador': resolver_coluna(df_carteira, config, 'carteira', 'indexador', obrigatoria=False),
        'taxa_base': resolver_coluna(df_carteira, config, 'carteira', 'taxa_base', obrigatoria=True),
        'taxa_bonus': resolver_coluna(df_carteira, config, 'carteira', 'taxa_bonus', obrigatoria=False),
        'dias_bonus': resolver_coluna(df_carteira, config, 'carteira', 'dias_bonus', obrigatoria=False),
        'prazo_dias': resolver_coluna(df_carteira, config, 'carteira', 'prazo_dias', obrigatoria=False),
        'carencia_dias': resolver_coluna(df_carteira, config, 'carteira', 'carencia_dias', obrigatoria=False),
        'liquidez_dias': resolver_coluna(df_carteira, config, 'carteira', 'liquidez_dias', obrigatoria=False),
        'isento_ir': resolver_coluna(df_carteira, config, 'carteira', 'isento_ir', obrigatoria=False),
        'aplicacao_minima': resolver_coluna(df_carteira, config, 'carteira', 'aplicacao_minima', obrigatoria=False),
        'aplicacao_maxima': resolver_coluna(df_carteira, config, 'carteira', 'aplicacao_maxima', obrigatoria=False),
        'ativo': resolver_coluna(df_carteira, config, 'carteira', 'ativo', obrigatoria=False),
        'fgc': resolver_coluna(df_carteira, config, 'carteira', 'fgc', obrigatoria=False),
        'banco_emissor': resolver_coluna(df_carteira, config, 'carteira', 'banco_emissor', obrigatoria=False),
        'risco_real': resolver_coluna(df_carteira, config, 'carteira', 'risco_real', obrigatoria=False),
        'somente_combo': resolver_coluna(df_carteira, config, 'carteira', 'somente_combo', obrigatoria=False),
        'permite_combo': resolver_coluna(df_carteira, config, 'carteira', 'permite_combo', obrigatoria=False),
        'produto_base': resolver_coluna(df_carteira, config, 'carteira', 'produto_base', obrigatoria=False),
        'produto_bonus': resolver_coluna(df_carteira, config, 'carteira', 'produto_bonus', obrigatoria=False),
        'ratio_base': resolver_coluna(df_carteira, config, 'carteira', 'ratio_base', obrigatoria=False),
        'ratio_bonus': resolver_coluna(df_carteira, config, 'carteira', 'ratio_bonus', obrigatoria=False),
        'max_usos': resolver_coluna(df_carteira, config, 'carteira', 'max_usos', obrigatoria=False),
        'observacoes': resolver_coluna(df_carteira, config, 'carteira', 'observacoes', obrigatoria=False),
        'produto_padrao': resolver_coluna(df_carteira, config, 'carteira', 'produto_padrao', obrigatoria=False),
        'camada': resolver_coluna(df_carteira, config, 'carteira', 'camada', obrigatoria=False),
        'status_confirmacao': resolver_coluna(df_carteira, config, 'carteira', 'status_confirmacao', obrigatoria=False),
        'campos_pendentes': resolver_coluna(df_carteira, config, 'carteira', 'campos_pendentes', obrigatoria=False),
        'score_banco': resolver_coluna(df_carteira, config, 'carteira', 'score_banco', obrigatoria=False),
        'familia_produto': resolver_coluna(df_carteira, config, 'carteira', 'familia_produto', obrigatoria=False),
        'regime_taxa': resolver_coluna(df_carteira, config, 'carteira', 'regime_taxa', obrigatoria=False),
        'regime_liquidez': resolver_coluna(df_carteira, config, 'carteira', 'regime_liquidez', obrigatoria=False),
        'papel_produto': resolver_coluna(df_carteira, config, 'carteira', 'papel_produto', obrigatoria=False),
        'elegivel_motor': resolver_coluna(df_carteira, config, 'carteira', 'elegivel_motor', obrigatoria=False),
        'elegivel_aporte_novo': resolver_coluna(df_carteira, config, 'carteira', 'elegivel_aporte_novo', obrigatoria=False),
        'elegivel_switch_in': resolver_coluna(df_carteira, config, 'carteira', 'elegivel_switch_in', obrigatoria=False),
        'elegivel_reconciliacao_historica': resolver_coluna(df_carteira, config, 'carteira', 'elegivel_reconciliacao_historica', obrigatoria=False),
        'regra_iof': resolver_coluna(df_carteira, config, 'carteira', 'regra_iof', obrigatoria=False),
        'semantica_taxa_base': resolver_coluna(df_carteira, config, 'carteira', 'semantica_taxa_base', obrigatoria=False),
    }

    limite = para_float_monetario((((config.get('politicas_taxa') or {}).get('limite_percentual_vs_multiplicador')) if isinstance(config, Mapping) else None), 10.0)
    metadados_transitorios = [
        'familia_produto',
        'regime_taxa',
        'regime_liquidez',
        'papel_produto',
        'elegivel_motor',
        'elegivel_aporte_novo',
        'elegivel_switch_in',
        'elegivel_reconciliacao_historica',
    ]
    auditoria = {
        'colunas_resolvidas': dict(campos),
        'linhas_descartadas': [],
        'sem_produto_id': 0,
        'produtos_total': 0,
        'limite_percentual_vs_multiplicador': limite,
        'metadados_derivados_transitorios': list(metadados_transitorios),
        'observacao_metadados_derivados': 'Campos derivados em código funcionam como ponte transitória até maior estruturação da aba Carteira.',
        'campos_estruturais_recomendados': list(metadados_transitorios),
        'campos_estruturais_sem_coluna_resolvida': [campo for campo in metadados_transitorios if not campos.get(campo)],
        'regra_iof_vazios': 0,
        'regra_iof_invalidos': 0,
        'semantica_taxa_base_vazios': 0,
        'semantica_taxa_base_invalidos': 0,
    }
    registros: list[dict[str, Any]] = []

    for idx, row in df_carteira.iterrows():
        nome = limpar_texto(row[campos['nome']]) if campos['nome'] in df_carteira.columns else ''
        if not nome:
            auditoria['linhas_descartadas'].append({'indice': int(idx), 'motivo': 'nome_vazio'})
            continue
        produto_id_raw = row[campos['produto_id']] if campos['produto_id'] and campos['produto_id'] in df_carteira.columns else None
        if produto_id_raw is None or str(produto_id_raw).strip() == '':
            auditoria['sem_produto_id'] += 1
        nome_norm = normalizar_nome_produto(nome)
        produto_key = gerar_produto_key(produto_id_raw, nome_norm)

        tipo = limpar_texto(row[campos['tipo']]) if campos['tipo'] else ''
        indexador = limpar_texto(row[campos['indexador']]) if campos['indexador'] else ''
        taxa_base_cdi = _normalizar_taxa_cdi(row[campos['taxa_base']], default=0.0, limite_percentual_vs_multiplicador=limite)
        taxa_bonus_cdi = _normalizar_taxa_cdi(row[campos['taxa_bonus']], default=0.0, limite_percentual_vs_multiplicador=limite) if campos['taxa_bonus'] else 0.0
        dias_bonus = para_int(row[campos['dias_bonus']], 0) if campos['dias_bonus'] else 0
        prazo_dias = para_int(row[campos['prazo_dias']], 0) if campos['prazo_dias'] else 0
        carencia_dias = para_int(row[campos['carencia_dias']], 0) if campos['carencia_dias'] else 0
        liquidez_dias = para_int(row[campos['liquidez_dias']], 0) if campos['liquidez_dias'] else 0
        isento_ir = para_bool(row[campos['isento_ir']], False) if campos['isento_ir'] else False
        aplicacao_minima = para_float_monetario(row[campos['aplicacao_minima']], 0.0) if campos['aplicacao_minima'] else 0.0
        aplicacao_maxima = para_float_monetario(row[campos['aplicacao_maxima']], 0.0) if campos['aplicacao_maxima'] else 0.0
        ativo = para_bool(row[campos['ativo']], True) if campos['ativo'] else True
        fgc = para_bool(row[campos['fgc']], False) if campos['fgc'] else False
        banco_emissor = limpar_texto(row[campos['banco_emissor']]) if campos['banco_emissor'] else ''
        risco_real = limpar_texto(row[campos['risco_real']]) if campos['risco_real'] else ''
        produto_base = limpar_texto(row[campos['produto_base']]) if campos['produto_base'] else ''
        produto_bonus = limpar_texto(row[campos['produto_bonus']]) if campos['produto_bonus'] else ''
        permite_combo_exp = para_bool(row[campos['permite_combo']], False) if campos['permite_combo'] else False
        permite_combo = bool(permite_combo_exp or produto_base or produto_bonus or 'combo' in normalizar_texto(tipo))
        somente_combo = para_bool(row[campos['somente_combo']], False) if campos['somente_combo'] else False
        camada = limpar_texto(row[campos['camada']]) if campos['camada'] else ''
        status_confirmacao = limpar_texto(row[campos['status_confirmacao']]) if campos['status_confirmacao'] else ''
        campos_pendentes = limpar_texto(row[campos['campos_pendentes']]) if campos['campos_pendentes'] else ''
        score_banco = limpar_texto(row[campos['score_banco']]) if campos['score_banco'] else ''
        regra_iof_raw = row[campos['regra_iof']] if campos['regra_iof'] else None
        semantica_taxa_base_raw = row[campos['semantica_taxa_base']] if campos['semantica_taxa_base'] else None
        regra_iof = _normalizar_regra_iof(regra_iof_raw)
        semantica_taxa_base = _normalizar_semantica_taxa_base(semantica_taxa_base_raw)
        if not limpar_texto(regra_iof_raw):
            auditoria['regra_iof_vazios'] += 1
        if not limpar_texto(semantica_taxa_base_raw):
            auditoria['semantica_taxa_base_vazios'] += 1
        if not regra_iof:
            regra_iof = 'a_confirmar'
            auditoria['regra_iof_invalidos'] += 1
        if not semantica_taxa_base:
            semantica_taxa_base = 'a_confirmar'
            auditoria['semantica_taxa_base_invalidos'] += 1

        elegivel_motor = para_bool(row[campos['elegivel_motor']], ativo) if campos['elegivel_motor'] else bool(ativo)
        elegivel_aporte_novo = para_bool(row[campos['elegivel_aporte_novo']], ativo) if campos['elegivel_aporte_novo'] else bool(ativo)
        elegivel_switch_in = para_bool(row[campos['elegivel_switch_in']], ativo) if campos['elegivel_switch_in'] else bool(ativo)
        elegivel_reconciliacao_historica = para_bool(row[campos['elegivel_reconciliacao_historica']], True) if campos['elegivel_reconciliacao_historica'] else True

        familia_produto = (limpar_texto(row[campos['familia_produto']]) if campos['familia_produto'] else '') or _derivar_familia_produto(tipo, indexador, permite_combo=permite_combo, produto_base=produto_base, produto_bonus=produto_bonus)
        regime_taxa = (limpar_texto(row[campos['regime_taxa']]) if campos['regime_taxa'] else '') or _derivar_regime_taxa(indexador, taxa_base_cdi, taxa_bonus_cdi, dias_bonus, permite_combo=permite_combo, produto_base=produto_base, produto_bonus=produto_bonus)
        regime_liquidez = (limpar_texto(row[campos['regime_liquidez']]) if campos['regime_liquidez'] else '') or _derivar_regime_liquidez(carencia_dias, liquidez_dias, prazo_dias, permite_combo=permite_combo)
        papel_produto = (limpar_texto(row[campos['papel_produto']]) if campos['papel_produto'] else '') or _derivar_papel_produto(ativo, elegivel_motor)

        registros.append({
            'produto_key': produto_key,
            'produto_id_raw': None if produto_id_raw is None else limpar_texto(produto_id_raw),
            'nome': nome,
            'nome_norm': nome_norm,
            'tipo': tipo,
            'indexador': indexador,
            'taxa_base_cdi': taxa_base_cdi,
            'taxa_bonus_cdi': taxa_bonus_cdi,
            'dias_bonus': dias_bonus,
            'prazo_dias': prazo_dias,
            'carencia_dias': carencia_dias,
            'liquidez_dias': liquidez_dias,
            'isento_ir': isento_ir,
            'aplicacao_minima': aplicacao_minima,
            'aplicacao_maxima': aplicacao_maxima,
            'ativo': ativo,
            'fgc': fgc,
            'banco_emissor': banco_emissor,
            'risco_real': risco_real,
            'somente_combo': somente_combo,
            'permite_combo': permite_combo,
            'produto_base': produto_base,
            'produto_bonus': produto_bonus,
            'ratio_base': para_float_monetario(row[campos['ratio_base']], 0.0) if campos['ratio_base'] else 0.0,
            'ratio_bonus': para_float_monetario(row[campos['ratio_bonus']], 0.0) if campos['ratio_bonus'] else 0.0,
            'max_usos': para_int(row[campos['max_usos']], 0) if campos['max_usos'] else 0,
            'observacoes': limpar_texto(row[campos['observacoes']]) if campos['observacoes'] else '',
            'produto_padrao': para_bool(row[campos['produto_padrao']], False) if campos['produto_padrao'] else False,
            'camada': camada,
            'status_confirmacao': status_confirmacao,
            'campos_pendentes': campos_pendentes,
            'score_banco': score_banco,
            'familia_produto': familia_produto,
            'regime_taxa': regime_taxa,
            'regime_liquidez': regime_liquidez,
            'papel_produto': papel_produto,
            'elegivel_motor': elegivel_motor,
            'elegivel_aporte_novo': elegivel_aporte_novo,
            'elegivel_switch_in': elegivel_switch_in,
            'elegivel_reconciliacao_historica': elegivel_reconciliacao_historica,
            'regra_iof': regra_iof,
            'semantica_taxa_base': semantica_taxa_base,
        })

    quadro_canonico = pd.DataFrame(registros)
    auditoria['produtos_total'] = int(len(quadro_canonico))
    if len(quadro_canonico) > 0:
        auditoria['resumo_familia_produto'] = {str(ch): int(v) for ch, v in quadro_canonico['familia_produto'].fillna('vazio').value_counts(dropna=False).to_dict().items()}
        auditoria['resumo_regime_taxa'] = {str(ch): int(v) for ch, v in quadro_canonico['regime_taxa'].fillna('vazio').value_counts(dropna=False).to_dict().items()}
        auditoria['resumo_papel_produto'] = {str(ch): int(v) for ch, v in quadro_canonico['papel_produto'].fillna('vazio').value_counts(dropna=False).to_dict().items()}
        auditoria['distribuicao_regra_iof'] = {str(ch): int(v) for ch, v in quadro_canonico['regra_iof'].fillna('vazio').value_counts(dropna=False).to_dict().items()}
        auditoria['distribuicao_semantica_taxa_base'] = {str(ch): int(v) for ch, v in quadro_canonico['semantica_taxa_base'].fillna('vazio').value_counts(dropna=False).to_dict().items()}
    return quadro_canonico, auditoria


def construir_mapa_produtos(quadro_canonico: pd.DataFrame) -> dict[str, dict[str, Any]]:
    mapa_by_key: dict[str, dict[str, Any]] = {}
    mapa_by_nome_norm: dict[str, str] = {}
    for _, row in quadro_canonico.iterrows():
        registro = row.to_dict()
        produto_key = str(registro['produto_key'])
        nome_norm = str(registro['nome_norm'])
        mapa_by_key[produto_key] = registro
        mapa_by_nome_norm[nome_norm] = produto_key
    return {'by_key': mapa_by_key, 'by_nome_norm': mapa_by_nome_norm}


def validar_carteira_canonica(quadro_canonico: pd.DataFrame) -> dict[str, Any]:
    validacao = {'ok': True, 'erros': [], 'avisos': []}
    if quadro_canonico is None or len(quadro_canonico) == 0:
        validacao['ok'] = False
        validacao['erros'].append('carteira_canonica_vazia')
        return validacao
    if quadro_canonico['produto_key'].isna().any():
        validacao['ok'] = False
        validacao['erros'].append('produto_key_nulo')
    if quadro_canonico['produto_key'].duplicated().any():
        validacao['ok'] = False
        validacao['erros'].append('produto_key_duplicado')
    if quadro_canonico['nome_norm'].isna().any():
        validacao['ok'] = False
        validacao['erros'].append('nome_norm_nulo')
    if quadro_canonico['nome_norm'].duplicated().any():
        validacao['ok'] = False
        validacao['erros'].append('nome_norm_duplicado')
    if quadro_canonico['taxa_base_cdi'].isna().any():
        validacao['ok'] = False
        validacao['erros'].append('taxa_base_cdi_nula')
    if (quadro_canonico['taxa_base_cdi'] <= 0).any():
        validacao['avisos'].append('existem_taxas_base_nao_positivas')
    for campo in ('dias_bonus', 'prazo_dias', 'carencia_dias', 'liquidez_dias', 'max_usos'):
        if (quadro_canonico[campo] < 0).any():
            validacao['avisos'].append(f'{campo}_negativo')
    if (quadro_canonico['aplicacao_minima'] < 0).any():
        validacao['avisos'].append('aplicacao_minima_negativa')
    if (quadro_canonico['aplicacao_maxima'] < 0).any():
        validacao['avisos'].append('aplicacao_maxima_negativa')
    aplic_max = quadro_canonico['aplicacao_maxima'].fillna(0.0)
    aplic_min = quadro_canonico['aplicacao_minima'].fillna(0.0)
    if ((aplic_max > 0) & (aplic_max < aplic_min)).any():
        validacao['avisos'].append('aplicacao_maxima_menor_que_minima')
    qtd_produto_padrao = int(quadro_canonico['produto_padrao'].sum())
    if qtd_produto_padrao == 0:
        validacao['avisos'].append('nenhum_produto_padrao_marcado')
    elif qtd_produto_padrao > 1:
        validacao['avisos'].append('mais_de_um_produto_padrao_marcado')
    if quadro_canonico['familia_produto'].fillna('').eq('').any():
        validacao['avisos'].append('familia_produto_vazia')
    if quadro_canonico['regime_taxa'].fillna('').eq('').any():
        validacao['avisos'].append('regime_taxa_vazio')
    if quadro_canonico['papel_produto'].fillna('').eq('').any():
        validacao['avisos'].append('papel_produto_vazio')
    return validacao


def carregar_carteira_canonica(pacote_planilha: PacotePlanilha, config: Mapping[str, Any]) -> PacoteCarteiraCanonica:
    abas_cfg = config.get('abas', {}) if isinstance(config.get('abas'), Mapping) else {}
    nome_cfg = abas_cfg.get('carteira', 'Carteira')

    candidatos: list[str] = []
    if isinstance(nome_cfg, list):
        candidatos.extend([str(x) for x in nome_cfg if str(x).strip()])
    else:
        candidatos.append(str(nome_cfg))

    for nome_padrao in ('Carteira', 'Carteiras'):
        if nome_padrao not in candidatos:
            candidatos.append(nome_padrao)

    nome_aba = next((nome for nome in candidatos if nome in pacote_planilha.quadros_brutos), None)
    if nome_aba is None:
        raise KeyError(
            f"Aba de carteira não encontrada. Tentadas: {candidatos}. "
            f"Disponíveis: {list(pacote_planilha.quadros_brutos.keys())}"
        )

    quadro_bruto = pacote_planilha.quadros_brutos[nome_aba]
    quadro_canonico, auditoria = normalizar_carteira_bruta(quadro_bruto, config)
    mapa_produtos = construir_mapa_produtos(quadro_canonico)
    validacao = validar_carteira_canonica(quadro_canonico)
    return PacoteCarteiraCanonica(
        nome_aba=nome_aba,
        quadro_bruto=quadro_bruto,
        quadro_canonico=quadro_canonico,
        mapa_produtos=mapa_produtos,
        auditoria=auditoria,
        validacao=validacao,
    )
