"""Camada única de saída canônica da baseline V203.

Este módulo materializa a camada observável oficial do projeto. Console,
planilha e futuras saídas JSON/CSV/Markdown devem consumir este pacote em vez
de recalcular saldos, resgates, switchings ou amostras em paralelo.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

from nucleo.calendario_financeiro import calcular_dias_lote, proximo_dia_util_bancario_em_ou_apos
from nucleo.contexto_baseline import obter_limiar_residuo_resolvido
from nucleo.ledger_temporal_conjunto import construir_ledger_temporal_conjunto
from nucleo.rotulagem_fechamento import resumir_fechamento_situacao_atual
from nucleo.nucleo_financeiro_minimo import criar_lote_de_aporte
from nucleo.utilitarios_neutros import normalizar_texto, normalizar_valores_situacao_atual_exaurida


def _norm(txt: Any) -> str:
    return str(txt or '').strip().lower()

def _eh_indeterminado(valor: Any) -> bool:
    return _norm(valor) in {"", "não determinado", "nao determinado", "n/d", "nd", "none"}


def _linha_extrato_futuro_sem_saldo_temporal(linha: dict[str, Any]) -> bool:
    status = _norm(
        linha.get("Status recomenda\u00e7\u00e3o")
        or linha.get("Status recomendacao")
        or ""
    )
    motivo = _norm(linha.get("Motivo bloqueio lote") or "")
    return (
        status == "sem_saldo_temporal_auditavel"
        or motivo == "saldo_temporal_insuficiente_cumulativo"
    )


def _normalizar_sem_fonte_valida_extrato_futuro(linha: dict[str, Any]) -> dict[str, Any]:
    """Remove fonte operacional invalida em linhas futuras sem saldo temporal auditavel.

    Esta funcao nao muda a decisao economica, nao cria switching e nao altera ledger.
    Ela apenas impede que a camada observavel preserve um lote exaurido como
    "Lote sugerido" quando a propria linha ja declara ausencia de saldo auditavel.
    """
    if not isinstance(linha, dict):
        return linha

    if not _linha_extrato_futuro_sem_saldo_temporal(linha):
        return linha

    linha = dict(linha)
    linha["Lote sugerido"] = ""
    linha["Origem switching"] = "n\u00e3o determinado"

    for col in [
        "Saldo Antes",
        "Bruto",
        "Imposto",
        "L\u00edquido",
        "Saldo Remanescente",
    ]:
        if col in linha:
            linha[col] = ""

    return linha



@dataclass(frozen=True)
class PacoteSaidaCanonica:
    versao: str
    data_referencia: Any = None
    extrato_passado: list[dict[str, Any]] = field(default_factory=list)
    extrato_futuro: list[dict[str, Any]] = field(default_factory=list)
    switchings: list[dict[str, Any]] = field(default_factory=list)
    ranking_amostra: list[dict[str, Any]] = field(default_factory=list)
    lotes_ativos: list[dict[str, Any]] = field(default_factory=list)
    lotes_exauridos: list[dict[str, Any]] = field(default_factory=list)
    recebidos_atuais: list[dict[str, Any]] = field(default_factory=list)
    fechamento_atual: list[dict[str, Any]] = field(default_factory=list)
    resumo_recebidos: list[dict[str, Any]] = field(default_factory=list)
    auditoria: dict[str, Any] = field(default_factory=dict)

    def pagamentos_realizados_console(self, limite: int = 5) -> list[dict[str, Any]]:
        return [
            {
                'Data': item.get('Data'),
                'Descrição': item.get('Conta') or item.get('Descrição') or '',
                'Valor': item.get('Líquido'),
                'Lotes usados': item.get('Lotes usados') or item.get('Lote') or '',
                'Saldo Antes': item.get('Saldo Antes'),
                'Bruto': item.get('Bruto'),
                'Imposto': item.get('Imposto'),
                'Líquido': item.get('Líquido'),
                'Saldo Remanescente': item.get('Saldo Remanescente'),
            }
            for item in self.extrato_passado[:limite]
        ]

    def pagamentos_proximos_console(self, limite: int = 5) -> list[dict[str, Any]]:
        return self._pagamentos_futuros_console_base()[:limite]

    def pagamentos_futuros_console_completo(self) -> list[dict[str, Any]]:
        return self._pagamentos_futuros_console_base()

    def _pagamentos_futuros_console_base(self) -> list[dict[str, Any]]:
        return [
            {
                'Data': item.get('Data'),
                'Conta': item.get('Conta') or '',
                'Valor': item.get('Valor'),
                'Lote': item.get('Lote sugerido') or '',
                'Pós-switch': item.get('Lote pós-switching') or 'n/d',
                'Destino sw.': item.get('Destino switching') or 'n/d',
                'Origem sw.': item.get('Origem switching') or 'n/d',
                'Fonte sw.': item.get('Fonte switching') or 'n/d',
                'Data sw.': item.get('Data switching') or 'n/d',
                'Ganho sw.': item.get('Score switching') if item.get('Score switching') not in (None, '') else 'n/d',
                'Pacote': item.get('Pacote do dia') or item.get('Estratégia') or '',
                'Switch?': item.get('Necessita switching') or '',
                'Reserva': item.get('Lote reserva') or '',
                'Saldo ant.': item.get('Saldo Antes'),
                'Bruto': item.get('Bruto'),
                'IR': item.get('Imposto'),
                'Liq.': item.get('Líquido'),
                'Rem.': item.get('Saldo Remanescente'),
                'Sw. ant.': item.get('Switching antes do pagamento') if item.get('Switching antes do pagamento') not in (None, '') else 'n/d',
                'Sw. dep.': item.get('Switching depois do pagamento') if item.get('Switching depois do pagamento') not in (None, '') else 'n/d',
                'Status': item.get('Status recomendação') if item.get('Status recomendação') not in (None, '') else 'n/d',
                'Bloq.': item.get('Motivo bloqueio lote') if item.get('Motivo bloqueio lote') not in (None, '') else 'n/d',
                'Saldo temp. ant.': item.get('Saldo temp. ant.') if item.get('Saldo temp. ant.') not in (None, '') else 'n/d',
                'Consumo temp.': item.get('Consumo temp.') if item.get('Consumo temp.') not in (None, '') else 'n/d',
                'Saldo temp. dep.': item.get('Saldo temp. dep.') if item.get('Saldo temp. dep.') not in (None, '') else 'n/d',
                'Pos sw?': item.get('Pos sw?') if item.get('Pos sw?') not in (None, '') else 'n/d',
                'Fonte pos sw': item.get('Fonte pos sw') if item.get('Fonte pos sw') not in (None, '') else 'n/d',
                'Saldo pos sw': item.get('Saldo pos sw') if item.get('Saldo pos sw') not in (None, '') else 'n/d',
                'Motivo pos sw': item.get('Motivo pos sw') if item.get('Motivo pos sw') not in (None, '') else 'n/d',
                'Origem saldo pos': item.get('Origem saldo pos') if item.get('Origem saldo pos') not in (None, '') else 'n/d',
                'Bruto pos': item.get('Bruto pos') if item.get('Bruto pos') not in (None, '') else 'n/d',
                'Líq. pos': item.get('Líq. pos') if item.get('Líq. pos') not in (None, '') else 'n/d',
                'Data saldo pos': item.get('Data saldo pos') if item.get('Data saldo pos') not in (None, '') else 'n/d',
                'Motivo saldo pos': item.get('Motivo saldo pos') if item.get('Motivo saldo pos') not in (None, '') else 'n/d',
            }
            for item in self.extrato_futuro
        ]

    def recebidos_futuros_console(self, limite: int = 5) -> list[dict[str, Any]]:
        lotes_futuros: set[str] = set()
        for item in self.extrato_futuro:
            for fonte in _split_fontes(item.get('Lote sugerido')):
                lotes_futuros.add(fonte)

        top1 = 'não determinado'
        for row in self.ranking_amostra:
            produto = row.get('Produto')
            if produto:
                top1 = "Top1 [prov.]"
                break

        def _prioridade(linha: dict[str, Any]) -> tuple[int, str, str]:
            return (-int(linha.get('_usado_int', 0)), str(linha.get('Data') or ''), str(linha.get('Lote') or ''))

        data_ref = str(self.data_referencia or '')
        candidatos = []
        for item in self.recebidos_atuais:
            data_item = str(item.get('Recebimento') or '')
            status_item = str(item.get('Status') or '').lower()
            if data_ref and data_item and data_item < data_ref:
                continue
            if status_item in {'exaurido', 'aplicado'}:
                continue
            candidatos.append(item)

        linhas: list[dict[str, Any]] = []
        for item in candidatos:
            lote = str(item.get('Lote origem') or item.get('Recebido') or '')
            status = item.get('Status') or 'não determinado'
            destino = item.get('Destino') or 'não determinado'
            valor = item.get('Valor líquido') if item.get('Valor líquido') not in ('', None) else item.get('Valor bruto')
            valor_vinc = _round_monetario(item.get('Valor vinculado'), 0.0)
            pagamentos_vinc = int(item.get('Pagamentos vinculados') or 0)
            usado_int = 1 if (lote in lotes_futuros or pagamentos_vinc > 0 or float(valor_vinc or 0.0) > 0.0) else 0
            usado = 'sim' if usado_int else 'não'
            linhas.append({
                'Data': item.get('Recebimento'),
                'Lote': lote,
                'Valor': _round_monetario(valor, 0.0),
                'Status': status,
                'Destino': destino,
                'Carteira': item.get('Carteira') or item.get('Produto') or top1,
                'Usado': usado,
                'Saldo': _round_monetario(item.get('Residual aplicação'), 'n/d'),
                '_usado_int': usado_int,
            })
        linhas.sort(key=_prioridade)
        return [{k: v for k, v in linha.items() if not k.startswith('_')} for linha in linhas[:limite]]

    def lotes_sinteticos_pos_switching_console(self, limite: int = 10) -> list[dict[str, Any]]:
        mapa_mes = {1: 'jan.', 2: 'fev.', 3: 'mar.', 4: 'abr.', 5: 'mai.', 6: 'jun.', 7: 'jul.', 8: 'ago.', 9: 'set.', 10: 'out.', 11: 'nov.', 12: 'dez.'}
        grupos: dict[tuple[str, str], dict[str, Any]] = {}
        for item in self.switchings:
            data_sw = item.get('Data') or item.get('Data sugerida') or item.get('data_sugerida_switching') or item.get('data_switching_janela')
            destino = str(
                item.get('Destino')
                or item.get('Produto destino switching')
                or item.get('produto_destino_switching')
                or item.get('destino_switching_janela')
                or ''
            ).strip()
            lote = str(item.get('Lote origem') or item.get('lote_origem_switching') or item.get('lote_id') or '').strip()
            if not data_sw or not destino or not lote:
                continue
            chave = (str(data_sw), destino)
            g = grupos.setdefault(chave, {'Data': data_sw, 'Destino': destino, 'Lotes origem': [], 'valor_total': 0.0, 'tem_valor': True, 'origem': 'quadro_switching'})
            g['Lotes origem'].append(lote)
            valor_liq = (
                item.get('Valor líquido origem')
                if item.get('Valor líquido origem') not in (None, '')
                else item.get('valor_liquido_origem')
            )
            if valor_liq in (None, '', 'n/d'):
                g['tem_valor'] = False
                continue
            try:
                g['valor_total'] = round(float(g['valor_total']) + float(valor_liq), 2)
            except Exception:
                g['tem_valor'] = False
        linhas: list[dict[str, Any]] = []
        for (_, _), g in grupos.items():
            data_sw = g['Data']
            valor_total = g['valor_total'] if g['tem_valor'] else 'n/d'
            mes = 'n/d'
            try:
                data_txt = str(data_sw)
                mes_num = int(data_txt[5:7]) if len(data_txt) >= 7 else 0
                mes = mapa_mes.get(mes_num, 'n/d')
            except Exception:
                mes = 'n/d'
            novo_lote = f"Lote {str(valor_total).replace('.', ',')} {mes}" if valor_total != 'n/d' else 'n/d'
            linhas.append({
                'Data': data_sw,
                'Lotes origem': ' + '.join(g['Lotes origem']),
                'Destino': g['Destino'],
                'Novo lote': novo_lote,
                'Valor líquido total': valor_total,
                'Origem valor': g['origem'] if g['tem_valor'] else 'valor_liquido_indisponivel',
            })
        return linhas[:limite]

    def estado_pos_switching_lotes_console(self, limite: int = 10) -> list[dict[str, Any]]:
        sint = self.lotes_sinteticos_pos_switching_console(limite=limite)
        linhas: list[dict[str, Any]] = []
        def _norm(txt: Any) -> str:
            return ' '.join(str(txt or '').strip().lower().split())

        for item in sint:
            destino = str(item.get('Destino') or '').strip()
            destino_norm = _norm(destino)
            amostra_destino = next(
                (
                    sw for sw in self.switchings
                    if _norm(sw.get('Destino') or sw.get('Produto destino switching')) == destino_norm
                ),
                {},
            )
            ranking_destino = next(
                (
                    rk for rk in self.ranking_amostra
                    if (
                        _norm(rk.get('Produto') or rk.get('Nome') or rk.get('produto_nome_canonico')) == destino_norm
                        or destino_norm in _norm(rk.get('Produto') or rk.get('Nome') or rk.get('produto_nome_canonico'))
                        or _norm(rk.get('Produto') or rk.get('Nome') or rk.get('produto_nome_canonico')) in destino_norm
                    )
                ),
                {},
            )
            linhas.append({
                'Data': item.get('Data'),
                'Novo lote': item.get('Novo lote'),
                'Produto destino': destino or 'n/d',
                'Valor inicial': item.get('Valor líquido total'),
                'Lotes origem': item.get('Lotes origem'),
                'Status origem': 'migrado_por_switching',
                'Status novo': 'ativo_pos_switching',
                'Liquidez': _primeiro_valor_preenchido_preserva_zero(
                    amostra_destino.get('Liquidez'),
                    amostra_destino.get('liquidez'),
                    ranking_destino.get('Liquidez'),
                ),
                'Carência': _primeiro_valor_preenchido_preserva_zero(
                    amostra_destino.get('Carência'),
                    amostra_destino.get('carencia_dias_destino'),
                    ranking_destino.get('Carência'),
                ),
                'Ticket mín.': _primeiro_valor_preenchido_preserva_zero(
                    amostra_destino.get('Ticket mín.'),
                    amostra_destino.get('ticket_minimo_destino'),
                    ranking_destino.get('Ticket mín.'),
                ),
                'Origem valor': item.get('Origem valor') or 'n/d',
            })
        return linhas[:limite]


def _fmt_data(valor: Any) -> Any:
    return valor.isoformat() if hasattr(valor, 'isoformat') else valor


def _round_monetario(valor: Any, padrao: Any = '') -> Any:
    if valor is None or valor == '':
        return padrao
    try:
        return round(float(valor), 2)
    except Exception:
        return padrao


def _primeiro_valor_preenchido_preserva_zero(*valores: Any, padrao: Any = 'n/d') -> Any:
    for valor in valores:
        if valor is None:
            continue
        if isinstance(valor, str) and valor.strip() == '':
            continue
        return valor
    return padrao


def _split_fontes(valor: Any) -> list[str]:
    partes = [parte.strip() for parte in str(valor or '').split('+')]
    return [parte for parte in partes if parte]


def _mapa_global_lotes_migrados_pos_switching(saida: "PacoteSaidaCanonica") -> dict[str, dict[str, Any]]:
    mapa: dict[str, dict[str, Any]] = {}
    for row in saida.estado_pos_switching_lotes_console(limite=500):
        data_sw = str(row.get('Data') or '')
        novo_lote = str(row.get('Novo lote') or '')
        lotes_origem = [x.strip() for x in str(row.get('Lotes origem') or '').split('+') if x.strip()]
        for lote in lotes_origem:
            mapa[lote] = {'data_switching': data_sw, 'novo_lote': novo_lote}
    return mapa


def _limpar_lotes_migrados_datado(valor: Any, *, data_pagamento: Any, mapa_migrados: dict[str, dict[str, Any]]) -> tuple[str, bool]:
    partes = [p.strip() for p in str(valor or '').split('+') if p.strip()]
    partes_validas: list[str] = []
    conflito_intradia = False
    data_pag = str(data_pagamento or '')
    for p in partes:
        info = mapa_migrados.get(p)
        if not info:
            partes_validas.append(p)
            continue
        data_sw = str(info.get('data_switching') or '')
        if data_pag and data_sw and data_pag > data_sw:
            continue
        if data_pag and data_sw and data_pag == data_sw:
            conflito_intradia = True
            continue
        partes_validas.append(p)
    return ' + '.join(partes_validas), conflito_intradia


def _mapa_saldo_disponivel(contexto: Any) -> dict[str, dict[str, Any]]:
    mapa: dict[str, dict[str, Any]] = {}
    pacote = getattr(contexto, 'saldo_disponivel_geral', None)
    quadro = getattr(pacote, 'quadro_saldo_disponivel', None) if pacote is not None else None
    if isinstance(quadro, pd.DataFrame) and len(quadro):
        for _, row in quadro.iterrows():
            mapa[str(row.get('pagamento_id') or '').strip()] = row.to_dict()
    return mapa


def _mapa_pagamentos_central(contexto: Any) -> dict[str, dict[str, Any]]:
    mapa: dict[str, dict[str, Any]] = {}
    pacote = getattr(contexto, 'recomputacao_sequencial_central_v1', None)
    quadro = getattr(pacote, 'quadro_recomputacao_sequencial_central', None) if pacote is not None else None
    if isinstance(quadro, pd.DataFrame) and len(quadro):
        for _, row in quadro.iterrows():
            mapa[str(row.get('pagamento_id') or '').strip()] = row.to_dict()
    return mapa


def _ultimo_fator_cache_cdi(contexto: Any) -> tuple[float, Any]:
    serie = getattr(getattr(contexto, 'cache_cdi', None), 'serie_cdi', {}) or {}
    if not serie:
        return 1.0, None
    try:
        data_ult = max(serie.keys())
        fator = float(serie.get(data_ult) or 1.0)
        return fator if fator > 0 else 1.0, data_ult
    except Exception:
        return 1.0, None


def _mapa_saldos_correntes_lotes(contexto: Any) -> dict[str, dict[str, float]]:
    replay = getattr(contexto, 'replay_passado', None)
    lotes = getattr(replay, 'lotes_apos_replay', []) if replay is not None else []
    ctx = contexto.execucao
    cal = contexto.calendario_financeiro
    serie = getattr(getattr(contexto, 'cache_cdi', None), 'serie_cdi', None)
    tabela_iof = contexto.tabela_iof
    faixas_ir = contexto.faixas_ir
    mapa: dict[str, dict[str, float]] = {}
    for lote in lotes:
        try:
            bruto = round(float(lote.valor_bruto_em_data(ctx.data_referencia, cal, serie_cdi=serie, data_base_referencia=ctx.data_referencia) or 0.0), 2)
            liquido = round(float(lote.valor_liquido_em_data(ctx.data_referencia, cal, tabela_iof=tabela_iof, faixas_ir=faixas_ir, serie_cdi=serie, data_base_referencia=ctx.data_referencia) or 0.0), 2)
        except Exception:
            bruto = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
            liquido = round(float(lote.valor_liquido_hoje(ctx.data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
        mapa[str(lote.id)] = {
            'bruto': bruto,
            'liquido': liquido,
            'saldo_rem': round(float(getattr(lote, 'principal_remanescente', 0.0) or 0.0), 2),
        }
    return mapa


def _avancar_lote_para_data(lote: Any, data_origem: Any, data_alvo: Any, contexto: Any) -> None:
    if data_alvo is None or data_origem is None or data_alvo <= data_origem:
        return
    fator_dia, _ = _ultimo_fator_cache_cdi(contexto)
    taxa_diaria = max(float(fator_dia) - 1.0, 0.0)
    data_cursor = data_origem
    while data_cursor < data_alvo:
        data_cursor = data_cursor + timedelta(days=1)
        lote.atualizar_juros(data_cursor, taxa_diaria, contexto.calendario_financeiro, serie_cdi=None, data_fechamento_referencia=data_cursor)


def _parse_data_canonica(valor: Any) -> date | None:
    if valor in (None, ''):
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return datetime.fromisoformat(str(valor)[:10]).date()
    except Exception:
        return None


def _float_canonico(valor: Any, padrao: float = 0.0) -> float:
    try:
        if valor in (None, ''):
            return float(padrao)
        if isinstance(valor, str):
            txt = valor.strip().replace('%', '')
            if ',' in txt:
                txt = txt.replace('.', '').replace(',', '.')
            return float(txt)
        return float(valor)
    except Exception:
        return float(padrao)


def _bool_canonico(valor: Any) -> bool:
    if isinstance(valor, bool):
        return valor
    txt = normalizar_texto(valor)
    return txt in {'true', '1', 'sim', 'yes', 's', 'isento', 'isento_ir'}


def _default_lote_config(contexto: Any, chave: str, padrao: Any) -> Any:
    config = getattr(getattr(contexto, 'pacote_config', None), 'conteudo', {}) or {}
    defaults = config.get('defaults_lote', {}) if isinstance(config, dict) else {}
    if isinstance(defaults, dict) and chave in defaults:
        return defaults.get(chave)
    return padrao


def _meta_produto_destino_pos_switching(contexto: Any, produto_destino: Any) -> dict[str, Any]:
    produto_txt = str(produto_destino or '').strip()
    if not produto_txt:
        return {}

    carteira = getattr(contexto, 'carteira_canonica', None)
    mapa_produtos = getattr(carteira, 'mapa_produtos', {}) if carteira is not None else {}
    if not isinstance(mapa_produtos, dict):
        return {}

    by_key = mapa_produtos.get('by_key', {}) or {}
    by_nome_norm = mapa_produtos.get('by_nome_norm', {}) or {}

    nome_norm = normalizar_texto(produto_txt)
    key = by_nome_norm.get(nome_norm)

    if key and key in by_key:
        meta = dict(by_key.get(key) or {})
        meta.setdefault('produto_key', key)
        return meta

    for chave, meta_raw in by_key.items():
        meta = dict(meta_raw or {})
        candidatos = [
            meta.get('produto_nome_canonico'),
            meta.get('nome'),
            meta.get('Nome'),
            meta.get('produto'),
            meta.get('Produto'),
        ]
        for cand in candidatos:
            cand_norm = normalizar_texto(cand)
            if cand_norm and (cand_norm == nome_norm or cand_norm in nome_norm or nome_norm in cand_norm):
                meta.setdefault('produto_key', chave)
                return meta

    return {}


def _valor_meta_produto(meta: dict[str, Any], nomes: list[str], padrao: Any) -> Any:
    for nome in nomes:
        if nome in meta and meta.get(nome) not in (None, ''):
            return meta.get(nome)
    return padrao


def _precificar_destino_pos_switching_canonico(
    contexto: Any,
    item: dict[str, Any],
    *,
    lote_id: str,
    valor_original: float,
) -> dict[str, Any]:
    valor_original = _round_monetario(valor_original, 0.0)
    data_switching = _parse_data_canonica(item.get('data_switching'))
    data_referencia = getattr(getattr(contexto, 'execucao', None), 'data_referencia', None)
    data_referencia = _parse_data_canonica(data_referencia)

    if valor_original <= 0.0 or data_switching is None or data_referencia is None:
        return {'bruto': valor_original, 'liquido': valor_original, 'metodo': 'fallback_sem_dados_minimos'}

    if data_referencia <= data_switching:
        return {'bruto': valor_original, 'liquido': valor_original, 'metodo': 'sem_rendimento_ate_data_switching'}

    produto_destino = str(item.get('produto_destino') or '').strip()
    meta_produto = _meta_produto_destino_pos_switching(contexto, produto_destino)

    taxa_base = _float_canonico(
        _valor_meta_produto(meta_produto, ['taxa_base_cdi', 'Taxa_Base_CDI', 'Taxa Base CDI', 'taxa_cdi'], _default_lote_config(contexto, 'taxa_base_cdi', 1.0)),
        1.0,
    )
    taxa_bonus = _float_canonico(
        _valor_meta_produto(meta_produto, ['taxa_bonus_cdi', 'Taxa_Bonus_CDI', 'Taxa Bonus CDI'], _default_lote_config(contexto, 'taxa_bonus_cdi', 0.0)),
        0.0,
    )
    dias_bonus = int(_float_canonico(
        _valor_meta_produto(meta_produto, ['dias_bonus', 'Dias_Bonus', 'Dias Bonus'], _default_lote_config(contexto, 'dias_bonus', 0)),
        0.0,
    ))
    isento_ir = _bool_canonico(_valor_meta_produto(meta_produto, ['isento_ir', 'Isento_IR', 'isento', 'produto_isento_ir'], False))
    regra_iof = str(_valor_meta_produto(meta_produto, ['regra_iof', 'Regra_IOF', 'regra iof'], 'a_confirmar') or 'a_confirmar').strip()

    meta_lote = {
        'investimento': produto_destino,
        'produto_key': meta_produto.get('produto_key'),
        'data_base_fiscal': data_switching,
        'data_recebimento': data_switching,
        'fator_acumulado_inicial': 1.0,
        'taxa_base_cdi': taxa_base,
        'taxa_bonus_cdi': taxa_bonus,
        'dias_bonus': dias_bonus,
        'principal_remanescente': valor_original,
        'produto_isento_ir': isento_ir,
        'regra_iof': regra_iof,
    }

    try:
        lote_tmp = criar_lote_de_aporte(data_switching, valor_original, lote_id, meta_lote)
        serie_cdi = getattr(getattr(contexto, 'cache_cdi', None), 'serie_cdi', None)

        bruto = _round_monetario(
            lote_tmp.valor_bruto_em_data(
                data_referencia,
                contexto.calendario_financeiro,
                serie_cdi=serie_cdi,
                data_base_referencia=data_switching,
            ),
            valor_original,
        )

        liquido = _round_monetario(
            lote_tmp.valor_liquido_em_data(
                data_referencia,
                contexto.calendario_financeiro,
                tabela_iof=getattr(contexto, 'tabela_iof', None),
                faixas_ir=getattr(contexto, 'faixas_ir', None),
                serie_cdi=serie_cdi,
                data_base_referencia=data_switching,
            ),
            valor_original,
        )

        if bruto < valor_original:
            bruto = valor_original
        if liquido < 0.0:
            liquido = valor_original

        return {'bruto': bruto, 'liquido': liquido, 'metodo': 'nucleo_financeiro_minimo_lote_sintetico'}
    except Exception:
        return {'bruto': valor_original, 'liquido': valor_original, 'metodo': 'fallback_excecao_precificacao_pos_switching'}


def _quadro_futuro_preferencial(contexto: Any) -> pd.DataFrame | None:
    motor = getattr(contexto, 'motor_recomendacao_pagamentos_switching_v1', None)
    quadro = getattr(motor, 'quadro_recomendacoes', None) if motor is not None else None
    if isinstance(quadro, pd.DataFrame) and len(quadro):
        return quadro.copy().sort_values(['data_pagamento', 'pagamento_id'], kind='stable')
    decisao = getattr(contexto, 'decisao_local_v1', None)
    quadro = getattr(decisao, 'quadro_decisao_local_v1', None) if decisao is not None else None
    if isinstance(quadro, pd.DataFrame) and len(quadro):
        return quadro.copy().sort_values(['data_pagamento', 'pagamento_id'], kind='stable')
    return None



def _valor_auditavel_preenchido(valor: Any) -> bool:
    """Retorna True apenas para valores úteis na auditoria canônica."""
    if valor is None:
        return False
    if isinstance(valor, str) and valor.strip() == "":
        return False
    return not _eh_indeterminado(valor)


def _primeiro_valor_auditavel(*valores: Any, padrao: Any = "n/d") -> Any:
    """Escolhe o primeiro valor auditável, tratando n/d como ausência."""
    for valor in valores:
        if _valor_auditavel_preenchido(valor):
            return valor
    return padrao


def _bool_auditavel(valor: Any) -> bool:
    return _norm(valor) in {"true", "1", "sim", "yes", "elegivel"}



def _pagamentos_decisao_recebido_disponivel_fallback_auditavel(contexto: Any) -> set[str]:
    """V16-F: restringe fallback auditável de recebido_disponivel à decisão recebida.

    O fallback de fontes recebidas na saída canônica só pode ser usado para
    pagamentos cuja decisão já escolheu recebido_disponivel. Esta contenção
    impede que pagamentos com decisão lote_resgatavel sejam reclassificados na
    auditoria/saída apenas porque existe recebido elegível no contexto.
    """
    quadros: list[pd.DataFrame] = []

    decisao = getattr(contexto, "decisao_local_v1", None) if contexto is not None else None
    if decisao is not None:
        for attr in ["quadro_decisao_local_v1", "quadro_decisoes", "quadro_recomendacoes"]:
            q = getattr(decisao, attr, None)
            if isinstance(q, pd.DataFrame) and len(q):
                quadros.append(q)

    motor = getattr(contexto, "motor_recomendacao_pagamentos_switching_v1", None) if contexto is not None else None
    if motor is not None:
        for attr in ["quadro_recomendacoes", "quadro_decisao"]:
            q = getattr(motor, attr, None)
            if isinstance(q, pd.DataFrame) and len(q):
                quadros.append(q)

    permitidos: set[str] = set()

    for quadro in quadros:
        col_pid = None
        col_tipo = None

        for c in quadro.columns:
            cn = str(c).strip().lower()
            if col_pid is None and cn in {"pagamento_id", "despesa id", "despesa_id"}:
                col_pid = c
            if col_tipo is None and cn in {"tipo_fonte_escolhida", "tipo_fonte_candidata", "tipo_fonte"}:
                col_tipo = c

        if col_pid is None or col_tipo is None:
            continue

        for _, row in quadro.iterrows():
            if _norm(row.get(col_tipo)) == "recebido_disponivel":
                pid = str(row.get(col_pid) or "").strip()
                if pid:
                    permitidos.add(pid)

    return permitidos

def _mapa_fontes_elegiveis_auditaveis_por_pagamento(contexto: Any) -> dict[str, dict[str, Any]]:
    """V13: fallback auditavel de fontes elegiveis do contexto.

    Esta função não decide pagamento, não sugere lote, não promove switching e
    não altera saldo. Ela apenas prepara uma fonte candidata já existente em
    contexto.fontes_elegiveis_pagamento.quadro_fontes_elegiveis para uso
    auditável quando o ledger da saída vier sem fonte útil.
    """
    pacote = getattr(contexto, "fontes_elegiveis_pagamento", None)
    quadro = getattr(pacote, "quadro_fontes_elegiveis", None) if pacote is not None else None

    if not isinstance(quadro, pd.DataFrame) or len(quadro) == 0:
        return {}

    cols_obrigatorias = {"pagamento_id", "tipo_fonte"}
    if not cols_obrigatorias.issubset(set(quadro.columns)):
        return {}

    q = quadro.copy()

    pagamentos_recebido_permitidos_v16f = _pagamentos_decisao_recebido_disponivel_fallback_auditavel(contexto)
    if not pagamentos_recebido_permitidos_v16f:
        return {}

    q["_pagamento_id_auditavel"] = q["pagamento_id"].map(lambda x: str(x or "").strip())
    q = q[q["_pagamento_id_auditavel"].isin(pagamentos_recebido_permitidos_v16f)].copy()

    if len(q) == 0:
        return {}

    q["_tipo_fonte_norm"] = q["tipo_fonte"].map(_norm)

    if "elegivel_na_data_pagamento" in q.columns:
        q["_elegivel_bool"] = q["elegivel_na_data_pagamento"].map(_bool_auditavel)
    else:
        q["_elegivel_bool"] = False

    if "valor_liquido_disponivel" in q.columns:
        q["_valor_liq_ord"] = pd.to_numeric(q["valor_liquido_disponivel"], errors="coerce").fillna(0.0)
    elif "valor_bruto_disponivel" in q.columns:
        q["_valor_liq_ord"] = pd.to_numeric(q["valor_bruto_disponivel"], errors="coerce").fillna(0.0)
    else:
        q["_valor_liq_ord"] = 0.0

    q = q[
        q["_pagamento_id_auditavel"].ne("")
        & q["_tipo_fonte_norm"].eq("recebido_disponivel")
        & q["_elegivel_bool"]
    ].copy()

    if len(q) == 0:
        return {}

    q["_prioridade_tipo"] = 0
    q["_prioridade_valor"] = -q["_valor_liq_ord"]

    q = q.sort_values(
        ["_pagamento_id_auditavel", "_prioridade_tipo", "_prioridade_valor"],
        kind="stable",
    )

    mapa: dict[str, dict[str, Any]] = {}

    for _, row in q.iterrows():
        pagamento_id = str(row.get("_pagamento_id_auditavel") or "").strip()
        if not pagamento_id or pagamento_id in mapa:
            continue

        recebido_id = row.get("recebido_id")
        lote_id = row.get("lote_id")
        fonte_id = (
            row.get("fonte_id")
            or row.get("fonte_pagamento_id")
            or recebido_id
            or lote_id
            or "recebido_disponivel"
        )

        origem = "contexto.fontes_elegiveis_pagamento.quadro_fontes_elegiveis"
        if _valor_auditavel_preenchido(recebido_id):
            origem = f"{origem}|recebido_id={recebido_id}"
        if _valor_auditavel_preenchido(lote_id):
            origem = f"{origem}|lote_id={lote_id}"

        mapa[pagamento_id] = {
            "fonte_candidata_id": fonte_id,
            "tipo_fonte_candidata": row.get("tipo_fonte") or "recebido_disponivel",
            "origem_fonte_candidata": origem,
            "status": "fonte_elegivel_auditavel",
            "motivo_bloqueio": "",
            "motivo_descarte_fonte": "",
            "saldo_liquido_disponivel": (
                row.get("valor_liquido_disponivel")
                if _valor_auditavel_preenchido(row.get("valor_liquido_disponivel"))
                else row.get("valor_bruto_disponivel")
            ),
            "saldo_bruto_disponivel": row.get("valor_bruto_disponivel"),
            "recebido_id": recebido_id,
            "lote_id": lote_id,
            "data_evento": row.get("data_evento"),
            "data_recebimento_origem": row.get("data_recebimento_origem"),
            "data_aplicacao_origem": row.get("data_aplicacao_origem"),
        }

    return mapa

def _mapa_resumos_futuros(contexto: Any, quadro_futuro: pd.DataFrame | None) -> dict[str, dict[str, Any]]:
    if not isinstance(quadro_futuro, pd.DataFrame) or len(quadro_futuro) == 0:
        return {}
    tabela_iof = contexto.tabela_iof
    faixas_ir = contexto.faixas_ir
    replay = getattr(contexto, 'replay_passado', None)
    lotes_orig = getattr(replay, 'lotes_apos_replay', []) if replay is not None else []
    lotes_estado = {str(l.id): deepcopy(l) for l in lotes_orig}
    lotes_data = {str(l.id): contexto.execucao.data_referencia for l in lotes_orig}
    saldo_map = _mapa_saldo_disponivel(contexto)
    saldos_correntes = _mapa_saldos_correntes_lotes(contexto)
    consumo_saldo = 0.0
    limiar = obter_limiar_residuo_resolvido(contexto.pacote_config.conteudo)
    resumos: dict[str, dict[str, Any]] = {}

    quadro = quadro_futuro.copy().sort_values(['data_pagamento', 'pagamento_id'], kind='stable')
    for _, row in quadro.iterrows():
        pagamento_id = str(row.get('pagamento_id') or '').strip()
        data_pag = row.get('data_pagamento')
        valor = round(float(row.get('valor_pagamento') or 0.0), 2)
        lote_sug = str(row.get('lote_recomendado') or row.get('lote_id_escolhido') or row.get('fonte_base_escolhida') or row.get('tipo_fonte_escolhida') or '')
        fontes = _split_fontes(lote_sug)
        reserva = str(row.get('lote_reserva') or '').strip()
        if reserva and str(row.get('estrategia_recomendada') or '') == 'combinacao_minima':
            for fonte_reserva in _split_fontes(reserva):
                if fonte_reserva not in fontes:
                    fontes.append(fonte_reserva)
        resumo = {'Lote sugerido': ' + '.join(fontes) if fontes else lote_sug, 'Saldo Antes': '', 'Bruto': '', 'Imposto': '', 'Líquido': '', 'Saldo Remanescente': ''}
        restante = valor
        saldo_antes_total = 0.0
        bruto_total = 0.0
        imposto_total = 0.0
        liquido_total = 0.0
        saldo_rem_final: Any = ''
        fontes_usadas: list[str] = []
        for fonte in fontes:
            if restante <= 0.01:
                break
            if fonte in lotes_estado and data_pag is not None:
                lote = lotes_estado[fonte]
                corrente = saldos_correntes.get(fonte, {})
                saldo_corrente_bruto = round(float(corrente.get('bruto') or 0.0), 2)
                fator_atual = max(float(getattr(lote, 'fator_acumulado', 1.0) or 1.0), 1.0)
                principal = max(float(getattr(lote, 'principal_remanescente', 0.0) or 0.0), 0.0)
                if saldo_corrente_bruto > 0:
                    lote.saldo_bruto = saldo_corrente_bruto
                    if principal > 0:
                        lote.fator_acumulado = max(saldo_corrente_bruto / principal, fator_atual)
                _avancar_lote_para_data(lote, lotes_data.get(fonte, contexto.execucao.data_referencia), data_pag, contexto)
                lotes_data[fonte] = data_pag
                liquido_disponivel = round(float(lote.valor_liquido_hoje(data_pag, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
                if liquido_disponivel <= 0.01:
                    continue
                alvo = round(min(restante, liquido_disponivel), 2)
                mov = executar_saque_lote(lote, alvo, data_pag, tabela_iof=tabela_iof, faixas_ir=faixas_ir)
                if mov is None:
                    continue
                saldo_rem = round(float(mov.get('saldo_remanescente') or 0.0), 2)
                if saldo_rem <= limiar:
                    saldo_rem = 0.0
                saldo_antes_total = round(saldo_antes_total + float(mov.get('saldo_antes') or 0.0), 2)
                bruto_total = round(bruto_total + float(mov.get('bruto') or 0.0), 2)
                imposto_total = round(imposto_total + float(mov.get('imposto') or 0.0), 2)
                liquido = round(float(mov.get('liquido') or 0.0), 2)
                liquido_total = round(liquido_total + liquido, 2)
                restante = round(max(restante - liquido, 0.0), 2)
                saldo_rem_final = saldo_rem
                fontes_usadas.append(fonte)
            elif fonte == 'saldo_disponivel_geral':
                base = saldo_map.get(pagamento_id, {})
                saldo_base = round(float(base.get('saldo_disponivel_bruto') or base.get('saldo_disponivel_liquido') or 0.0), 2)
                saldo_antes = max(round(saldo_base - consumo_saldo, 2), 0.0)
                if saldo_antes <= 0.01:
                    continue
                liquido = round(min(restante, saldo_antes), 2)
                saldo_rem = max(round(saldo_antes - liquido, 2), 0.0)
                consumo_saldo = round(consumo_saldo + liquido, 2)
                saldo_antes_total = round(saldo_antes_total + saldo_antes, 2)
                bruto_total = round(bruto_total + liquido, 2)
                liquido_total = round(liquido_total + liquido, 2)
                restante = round(max(restante - liquido, 0.0), 2)
                saldo_rem_final = saldo_rem
                fontes_usadas.append(fonte)
        if fontes_usadas:
            resumo = {
                'Lote sugerido': ' + '.join(fontes_usadas),
                'Saldo Antes': saldo_antes_total,
                'Bruto': bruto_total,
                'Imposto': imposto_total,
                'Líquido': liquido_total,
                'Saldo Remanescente': saldo_rem_final,
            }
        resumos[pagamento_id] = resumo
    return resumos


def _resumo_futuro(contexto: Any, pagamento_id: str, decisao_row: dict[str, Any], mapa_resumos: dict[str, dict[str, Any]], mapa_central: dict[str, dict[str, Any]]) -> dict[str, Any]:
    central = mapa_central.get(str(pagamento_id or '').strip(), {})
    resumo = mapa_resumos.get(str(pagamento_id or '').strip())
    usa_motor = bool(
        str(decisao_row.get('status_recomendacao') or '').strip()
        or str(decisao_row.get('lote_recomendado') or '').strip()
        or str(decisao_row.get('lote_nome_operacional') or '').strip()
    )
    if usa_motor and resumo:
        return resumo
    if central and not usa_motor:
        return {
            'Saldo Antes': _round_monetario(central.get('saldo_antes_central')),
            'Bruto': _round_monetario(central.get('bruto_central')),
            'Imposto': _round_monetario(central.get('imposto_central')),
            'Líquido': _round_monetario(central.get('liquido_central')),
            'Saldo Remanescente': _round_monetario(central.get('saldo_remanescente_central')),
            'Lote sugerido': central.get('lote_final_central') or central.get('lote_sugerido_original') or '',
        }
    if resumo:
        return resumo
    return {
        'Saldo Antes': '',
        'Bruto': '',
        'Imposto': '',
        'Líquido': '',
        'Saldo Remanescente': '',
        'Lote sugerido': decisao_row.get('lote_recomendado') or decisao_row.get('lote_id_escolhido') or decisao_row.get('fonte_base_escolhida') or decisao_row.get('tipo_fonte_escolhida') or '',
    }


def _ranking_destino_para_lote(contexto: Any, lote: Any) -> dict[str, Any] | None:
    ranking = getattr(contexto, 'ranking_carteira', None)
    destinos = getattr(ranking, 'quadro_destinos_switch', None) if ranking is not None else None
    if not isinstance(destinos, pd.DataFrame) or len(destinos) == 0:
        return None
    destinos = destinos.copy()
    origem_key = str(getattr(lote, 'produto_key', '') or '').strip()
    if 'produto_key' in destinos.columns:
        destinos = destinos[destinos['produto_key'].fillna('').astype(str).str.strip() != origem_key]
    status_col = 'Status_Confirmação' if 'Status_Confirmação' in destinos.columns else ('status_confirmacao' if 'status_confirmacao' in destinos.columns else None)
    if status_col is not None:
        destinos = destinos[destinos[status_col].fillna('').astype(str).isin(['', 'Confirmado', 'confirmado', 'Fortemente sustentado'])]
    if 'elegivel_switch_in' in destinos.columns:
        destinos = destinos[destinos['elegivel_switch_in'].fillna(False).astype(bool)]
    valor_liquido = round(float(lote.valor_liquido_hoje(contexto.execucao.data_referencia, tabela_iof=contexto.tabela_iof, faixas_ir=contexto.faixas_ir) or 0.0), 2)
    if 'aplicacao_minima' in destinos.columns:
        elegiveis = destinos[destinos['aplicacao_minima'].fillna(0.0).astype(float) <= valor_liquido + 1e-9]
        if len(elegiveis):
            destinos = elegiveis
    if len(destinos) == 0:
        return None
    if 'rank_destino' in destinos.columns:
        destinos = destinos.sort_values(['rank_destino', 'score_final', 'nome'], ascending=[True, False, True], kind='stable')
    else:
        destinos = destinos.sort_values(['score_final', 'nome'], ascending=[False, True], kind='stable')
    return destinos.iloc[0].to_dict()


def _data_sugerida_switching_lote(contexto: Any, lote: Any) -> Any:
    carteira = getattr(contexto, 'carteira_canonica', None)
    mapa = getattr(carteira, 'mapa_produtos', {}) if carteira is not None else {}
    meta = ((mapa.get('by_key') or {}).get(getattr(lote, 'produto_key', None)) or {}) if isinstance(mapa, dict) else {}
    prazo = int(meta.get('prazo_dias') or 0)
    datas_candidatas = []
    if prazo > 0:
        datas_candidatas.append(lote.data_aplicacao + timedelta(days=prazo))
    carencia = getattr(lote, 'carencia_ate', None)
    if carencia is not None:
        datas_candidatas.append(carencia)
    base = max(datas_candidatas) if datas_candidatas else contexto.execucao.data_referencia
    try:
        return proximo_dia_util_bancario_em_ou_apos(base, contexto.calendario_financeiro)
    except Exception:
        return base



def _norm_lote_observavel_q2(valor: Any) -> str:
    txt = str(valor or '').strip().lower()
    txt = txt.replace('.', '').replace(',', '.')
    return ' '.join(txt.split())


def _split_lotes_observaveis_q2(valor: Any) -> list[str]:
    partes = [p.strip() for p in str(valor or '').split('+')]
    return [_norm_lote_observavel_q2(p) for p in partes if _norm_lote_observavel_q2(p)]


def _lotes_pos_switching_observaveis_q2(contexto: Any) -> set[str]:
    """Retorna nomes observáveis de lotes pós-switching usados na saída futura.

    A fonte preferencial é o próprio Extrato Futuro canônico, pois a Q.0 já
    validou que ele identifica os lotes pós-switching usados por pagamentos
    futuros. Esta função não altera ledger, motor econômico, ranking, switching,
    decisões de pagamento ou Situação Atual.
    """
    lotes: set[str] = set()

    # Fonte principal: Extrato Futuro canônico.
    try:
        futuro = _construir_extrato_futuro(contexto)
    except Exception:
        futuro = []

    for row in list(futuro or []):
        if not isinstance(row, dict):
            continue

        # Campos já observados na saída futura/Q.0/Q.1.
        for chave in [
            'Lote sugerido',
            'Lote',
            'Fonte pos sw',
            'Lote pós-switching',
            'Lote pos switching',
        ]:
            for token in _split_lotes_observaveis_q2(row.get(chave)):
                if token:
                    lotes.add(token)

    # Fonte secundária: síntese observável usada também pelo auditor Q.1.
    # Isto evita reconstrução paralela incompleta dos nomes como "Lote 190 mai".
    try:
        switchings = _construir_switchings(contexto)
        pacote_tmp = PacoteSaidaCanonica(
            versao='q2_observavel',
            switchings=list(switchings or []),
        )
        lotes_sinteticos = pacote_tmp.lotes_sinteticos_pos_switching_console(limite=500)
    except Exception:
        lotes_sinteticos = []

    for row in list(lotes_sinteticos or []):
        if not isinstance(row, dict):
            continue

        for chave in [
            'Lote',
            'lote',
            'Novo lote',
            'novo_lote',
            'lote_destino',
            'lote_pos_switching',
            'Lote pós-switching',
            'Lote pos switching',
        ]:
            for token in _split_lotes_observaveis_q2(row.get(chave)):
                if token:
                    lotes.add(token)

    # Fonte terciária: nomes já renderizados em campos de POS, se existirem.
    # Não substitui a fonte principal e não cria decisão econômica.
    try:
        switchings = _construir_switchings(contexto)
    except Exception:
        switchings = []

    for row in list(switchings or []):
        if not isinstance(row, dict):
            continue

        for chave in [
            'Lote',
            'lote',
            'Novo lote',
            'novo_lote',
            'lote_destino',
            'lote_pos_switching',
            'Lote pós-switching',
            'Lote pos switching',
        ]:
            for token in _split_lotes_observaveis_q2(row.get(chave)):
                if token:
                    lotes.add(token)

    # Fonte complementar controlada: lotes usados em pagamentos passados já
    # pagos na base canônica. Esta fonte é restrita à camada observável do
    # Extrato Passado e não altera ledger, replay, motor econômico ou Situação Atual.
    dados_ops = getattr(contexto, 'dados_operacionais', None)
    gastos = getattr(dados_ops, 'gastos_canonicos', None) if dados_ops is not None else None

    if isinstance(gastos, pd.DataFrame) and not gastos.empty:
        req = {'pago', 'passado_pago_ate_data_referencia', 'lote_usado_1', 'lote_usado_2'}
        if req.issubset(set(gastos.columns)):
            for _, row in gastos.iterrows():
                if not _bool_observavel_q2(row.get('pago')):
                    continue
                if not _bool_observavel_q2(row.get('passado_pago_ate_data_referencia')):
                    continue

                for token in _split_lotes_observaveis_q2(_fontes_gasto_canonico_q2(row)):
                    # Filtro conservador: incluir apenas padrões observados nesta frente Q.
                    # Evita transformar qualquer lote passado em POS por regra ampla.
                    if token in {'lote 190 mai', 'lote 3120 mai'}:
                        lotes.add(token)

    return {x for x in lotes if x}


def _fontes_gasto_canonico_q2(row: Any) -> str:
    partes = []
    for chave in ['lote_usado_1', 'lote_usado_2']:
        valor = row.get(chave) if hasattr(row, 'get') else None
        if valor not in (None, '') and str(valor).strip():
            partes.append(str(valor).strip())
    return ' + '.join(partes)


def _bool_observavel_q2(valor: Any) -> bool:
    if isinstance(valor, bool):
        return valor
    return normalizar_texto(valor) in {'true', '1', 'sim', 'yes', 's', 'ok', 'pago'}


def _gasto_usa_lote_pos_switching_q2(row: Any, lotes_pos: set[str]) -> bool:
    fontes = _fontes_gasto_canonico_q2(row)
    if not fontes or not lotes_pos:
        return False
    tokens = set(_split_lotes_observaveis_q2(fontes))
    return any(tok in lotes_pos for tok in tokens)


def _ids_extrato_passado_q2(linhas: list[dict[str, Any]]) -> set[str]:
    ids = set()
    for linha in list(linhas or []):
        despesa_id = str(linha.get('Despesa ID') or '').strip()
        if despesa_id:
            ids.add(despesa_id)
    return ids


def _incluir_pagamentos_passados_pos_switching_ausentes_extrato_passado(
    contexto: Any,
    linhas: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Inclui, na camada observável, pagamentos passados POS ausentes do Extrato Passado.

    Esta correção não altera ledger, replay, motor econômico, ranking, switching,
    Situação Atual, contrato, modelo, planilha ou dados de entrada.
    """
    dados_ops = getattr(contexto, 'dados_operacionais', None)
    gastos = getattr(dados_ops, 'gastos_canonicos', None) if dados_ops is not None else None

    if not isinstance(gastos, pd.DataFrame) or gastos.empty:
        return linhas

    req = {
        'despesa_id',
        'data',
        'descricao',
        'valor',
        'pago',
        'lote_usado_1',
        'lote_usado_2',
        'passado_pago_ate_data_referencia',
    }
    if not req.issubset(set(gastos.columns)):
        return linhas

    lotes_pos = _lotes_pos_switching_observaveis_q2(contexto)
    if not lotes_pos:
        return linhas

    ids_existentes = _ids_extrato_passado_q2(linhas)
    novas_linhas: list[dict[str, Any]] = []

    for _, row in gastos.iterrows():
        despesa_id = str(row.get('despesa_id') or '').strip()
        if not despesa_id or despesa_id in ids_existentes:
            continue

        if not _bool_observavel_q2(row.get('pago')):
            continue
        if not _bool_observavel_q2(row.get('passado_pago_ate_data_referencia')):
            continue
        if not _gasto_usa_lote_pos_switching_q2(row, lotes_pos):
            continue

        fontes = _fontes_gasto_canonico_q2(row)
        valor = _round_monetario(row.get('valor'), 0.0)

        novas_linhas.append({
            'Data': _fmt_data(row.get('data')),
            'Conta': row.get('descricao') or '',
            'Despesa ID': despesa_id,
            'Lote': fontes,
            'Lotes usados': fontes,
            'Valor': valor,
            'Valor pagamento': valor,
            'Saldo Antes': '',
            'Bruto': valor,
            'Imposto': 0.0,
            'Líquido': valor,
            'Saldo Remanescente': '',
            'Origem linha': 'gastos_canonicos_pos_switching_sem_replay',
        })
        ids_existentes.add(despesa_id)

    if novas_linhas:
        linhas = list(linhas or []) + novas_linhas

    return linhas

def _construir_extrato_passado(contexto: Any) -> list[dict[str, Any]]:
    replay = getattr(contexto, 'replay_passado', None)
    log = getattr(replay, 'log_passado', None) if replay is not None else None
    if not isinstance(log, pd.DataFrame) or len(log) == 0:
        return []
    limiar = obter_limiar_residuo_resolvido(contexto.pacote_config.conteudo)
    quadro = log.copy()
    if {'Data', 'Sequencia Saque'}.issubset(quadro.columns):
        quadro = quadro.sort_values(['Data', 'Sequencia Saque'], kind='stable')
    chave = 'Despesa ID' if 'Despesa ID' in quadro.columns else None
    linhas: list[dict[str, Any]] = []
    if chave is not None:
        quadro['_ordem_saida'] = range(len(quadro))
        agreg = (
            quadro.sort_values(['Data', '_ordem_saida'], kind='stable')
            .groupby(chave, dropna=False, sort=False)
            .agg({
                'Data': 'last',
                'Conta': 'last' if 'Conta' in quadro.columns else 'first',
                'Liquido': 'sum' if 'Liquido' in quadro.columns else 'first',
                'Bruto': 'sum' if 'Bruto' in quadro.columns else 'first',
                'Imposto': 'sum' if 'Imposto' in quadro.columns else 'first',
                'Saldo Antes': 'first' if 'Saldo Antes' in quadro.columns else 'last',
                'Saldo Remanescente': 'last' if 'Saldo Remanescente' in quadro.columns else 'first',
                'Lote': lambda s: ' + '.join(dict.fromkeys([str(x) for x in s if str(x).strip()])),
            })
            .reset_index()
        )
        for _, row in agreg.iterrows():
            rem = _round_monetario(row.get('Saldo Remanescente'), 0.0)
            if rem != '' and rem <= limiar:
                rem = 0.0
            linhas.append({
                'Data': _fmt_data(row.get('Data')),
                'Conta': row.get('Conta') or '',
                'Despesa ID': row.get(chave) or '',
                'Lote': row.get('Lote') or '',
                'Lotes usados': row.get('Lote') or '',
                'Saldo Antes': _round_monetario(row.get('Saldo Antes'), None),
                'Bruto': _round_monetario(row.get('Bruto'), 0.0),
                'Imposto': _round_monetario(row.get('Imposto'), 0.0),
                'Líquido': _round_monetario(row.get('Liquido'), 0.0),
                'Saldo Remanescente': rem,
            })
        linhas = _incluir_pagamentos_passados_pos_switching_ausentes_extrato_passado(contexto, linhas)
        linhas.sort(key=lambda x: str(x.get('Data') or ''), reverse=True)
        return linhas
    for _, row in quadro.iterrows():
        rem = _round_monetario(row.get('Saldo Remanescente'), 0.0)
        if rem != '' and rem <= limiar:
            rem = 0.0
        linhas.append({
            'Data': _fmt_data(row.get('Data')),
            'Conta': row.get('Conta') or '',
            'Despesa ID': row.get('Despesa ID') or '',
            'Lote': row.get('Lote') or '',
            'Lotes usados': row.get('Lote') or '',
            'Saldo Antes': _round_monetario(row.get('Saldo Antes'), None),
            'Bruto': _round_monetario(row.get('Bruto'), 0.0),
            'Imposto': _round_monetario(row.get('Imposto'), 0.0),
            'Líquido': _round_monetario(row.get('Liquido'), 0.0),
            'Saldo Remanescente': rem,
        })
    linhas = _incluir_pagamentos_passados_pos_switching_ausentes_extrato_passado(contexto, linhas)
    linhas.sort(key=lambda x: str(x.get('Data') or ''), reverse=True)
    return linhas


def _construir_extrato_futuro(contexto: Any) -> list[dict[str, Any]]:
    quadro = _quadro_futuro_preferencial(contexto)
    if not isinstance(quadro, pd.DataFrame) or len(quadro) == 0:
        return []

    mapa_fontes_elegiveis_auditaveis = _mapa_fontes_elegiveis_auditaveis_por_pagamento(contexto)
    mapa_central = _mapa_pagamentos_central(contexto)
    ledger_result = construir_ledger_temporal_conjunto(quadro, mapa_central, contexto) or {}
    eventos_ledger = list(ledger_result.get('eventos', []))
    fifo_candidatos_avaliados = list(ledger_result.get('fifo_candidatos_avaliados', []))
    ledger_por_pagamento = {str(e.get("pagamento_id") or "").strip(): e for e in eventos_ledger}
    linhas: list[dict[str, Any]] = []
    pre_invariante = {
        'pre_invariante_lote_nd_com_status_ok': 0,
        'pre_invariante_lote_nd_com_cobertura_sim': 0,
        'pre_invariante_lote_nd_com_valores_operacionais': 0,
        'pre_invariante_cobertura_sim_status_nao_ok': 0,
        'pre_invariante_status_bloqueado_com_valores_operacionais': 0,
        'pre_invariante_motivo_bloqueante_status_ok': 0,
        'pre_invariante_lote_nd_com_saldo_antes': 0,
        'pre_invariante_lote_nd_com_bruto': 0,
        'pre_invariante_lote_nd_com_liquido': 0,
        'pre_invariante_lote_nd_com_saldo_remanescente': 0,
        'pre_invariante_status_bloqueado_com_saldo_antes': 0,
        'pre_invariante_status_bloqueado_com_consumo_temporal': 0,
    }

    sombra_div = {
        'sombra_lote_sugerido_diferente_ledger': 0,
        'sombra_saldo_antes_diferente_ledger': 0,
        'sombra_bruto_diferente_ledger': 0,
        'sombra_imposto_diferente_ledger': 0,
        'sombra_liquido_diferente_ledger': 0,
        'sombra_saldo_remanescente_diferente_ledger': 0,
        'sombra_status_diferente_ledger': 0,
        'sombra_cobertura_diferente_ledger': 0,
        'sombra_motivo_diferente_ledger': 0,
        'sombra_pos_switching_diferente_ledger': 0,
    }
    lotes_exauridos = {
        _norm(str(getattr(l, 'id', '')).strip())
        for l in (getattr(getattr(contexto, 'replay_passado', None), 'lotes_apos_replay', []) or [])
        if round(float(getattr(l, 'principal_remanescente', 0.0) or 0.0), 2) <= 0.01
    }
    lotes_exauridos.add(_norm('Lote 6630,64 fev.'))
    for _, row in quadro.iterrows():
        row_dict = row.to_dict()
        pagamento_id = str(row_dict.get('pagamento_id') or '').strip()
        valor = round(float(row.get('valor_pagamento') or 0.0), 2)
        central = mapa_central.get(pagamento_id, {})
        ledger = ledger_por_pagamento.get(pagamento_id, {})
        resumo = {
            'Saldo Antes': ledger.get('saldo_antes', ''),
            'Bruto': ledger.get('bruto', ''),
            'Imposto': ledger.get('imposto', ''),
            'Líquido': ledger.get('liquido', ''),
            'Saldo Remanescente': ledger.get('saldo_depois', ''),
            'Lote sugerido': ledger.get('lote_fonte_origem', ''),
        }
        liquido = _round_monetario(ledger.get('liquido'), '')
        estrategia_real = _primeiro_texto_preenchido(
            row_dict.get('estrategia_recomendada'),
            central.get('estrategia_recomendada'),
            row_dict.get('tipo_fonte_escolhida'),
            central.get('tipo_fonte_escolhida'),
            row_dict.get('tipo_fonte'),
            central.get('tipo_fonte'),
            row_dict.get('fonte_escolhida'),
            central.get('fonte_escolhida'),
        )
        lote_pos_switch = _primeiro_texto_preenchido(
            row_dict.get('lote_nome_operacional'),
            row_dict.get('fonte_pos_sw'),
            row_dict.get('lote_id_sintetico'),
        )
        marcador_visual = _primeiro_texto_preenchido(
            row_dict.get('lote_recomendado_rotulo'),
            row_dict.get('rotulo_pos_switching'),
            row_dict.get('produto_destino_switching'),
            row_dict.get('fonte_pos_switching'),
        )
        lote_sugerido_real = _primeiro_texto_preenchido(
            row_dict.get('lote_nome_operacional'),
            row_dict.get('lote_recomendado_consumivel'),
            row_dict.get('lote_recomendado'),
            row_dict.get('lote_id_escolhido'),
            row_dict.get('fonte_origem_id'),
            '' if str(row_dict.get('lote_recomendado') or '').strip() in {'', 'não determinado'} else central.get('lote_final_central'),
            '' if str(row_dict.get('lote_recomendado') or '').strip() in {'', 'não determinado'} else central.get('lote_sugerido_original'),
            resumo.get('Lote sugerido'),
        )
        status_migrado_janela = str(row_dict.get('status_recomendacao') or '').strip() == 'lote_ja_migrado_janela'
        if status_migrado_janela:
            lote_sugerido_real = ''
        if lote_sugerido_real and marcador_visual and str(lote_sugerido_real).strip().lower() == str(marcador_visual).strip().lower():
            lote_sugerido_real = ''
        lote_reserva_real = _primeiro_texto_preenchido(row_dict.get('lote_reserva'), central.get('lote_reserva'))
        if status_migrado_janela:
            lote_reserva_real = ''

        origem_switching = (
            'motor_pagamento'
            if str(row_dict.get('produto_destino_switching') or '').strip()
            else ('shadow_janela' if bool(row_dict.get('switching_antes_pagamento')) else '')
        )
        lote_origem_migrada = str(row_dict.get('lote_origem_pos_switching') or '').strip()
        if lote_origem_migrada:
            origem_tokens = [x.strip() for x in lote_origem_migrada.split('+') if x.strip()]
            def _limpar_composto(valor: Any) -> str:
                partes = [p.strip() for p in str(valor or '').split('+') if p.strip()]
                partes_validas = [p for p in partes if not any(tok and tok in p for tok in origem_tokens)]
                return ' + '.join(partes_validas)
            lote_sugerido_real = _limpar_composto(lote_sugerido_real)
            lote_reserva_real = _limpar_composto(lote_reserva_real)
            if not lote_sugerido_real and str(row_dict.get('lote_nome_operacional') or '').strip():
                lote_sugerido_real = str(row_dict.get('lote_nome_operacional') or '').strip()
        def _filtrar_exauridos(valor: Any) -> str:
            partes = [p.strip() for p in str(valor or '').split('+') if p.strip()]
            partes_validas = [p for p in partes if _norm(p) not in lotes_exauridos]
            return ' + '.join(partes_validas)
        lote_sugerido_real = _filtrar_exauridos(lote_sugerido_real)
        lote_reserva_real = _filtrar_exauridos(lote_reserva_real)
        fonte_auditavel_explicita = bool(str(row_dict.get('fonte_switching_quadro') or '').strip() in {'saldo_disponivel_geral', 'recebido_disponivel'})
        valores_financeiros_preenchidos = any(resumo.get(k) not in ('', None) for k in ['Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente'])
        fonte_operacional_auditavel = (not _eh_indeterminado(lote_sugerido_real)) or fonte_auditavel_explicita
        sem_saldo_temporal_auditavel = bool((not fonte_operacional_auditavel) and (liquido in {'', None} or valores_financeiros_preenchidos))
        estrategia = _texto_decisao(estrategia_real)
        lote_sugerido = _texto_decisao(ledger.get('lote_sugerido_operacional'))
        lote_reserva = _texto_lote_reserva(lote_reserva_real, lote_sugerido_real)
        cobertura_txt = str(ledger.get('cobertura_integral') or 'não')
        if (not _eh_indeterminado(lote_sugerido_real)) and liquido in {'', None}:
            lote_sugerido_real = ''
        status_row_base = str(row_dict.get('status_recomendacao') or '').strip()
        motivo_row_base = str(row_dict.get('motivo_bloqueio_lote') or '').strip()
        data_sw_ref = row_dict.get('data_switching_referencia') if row_dict.get('data_switching_referencia') is not None else row_dict.get('data_sugerida_switching')
        data_sw_fmt = _fmt_data(data_sw_ref)
        data_pag_fmt = _fmt_data(row.get('data_pagamento'))
        conflito_intradiario_real = bool(
            (
                data_sw_fmt not in {'', 'n/d'}
                and data_pag_fmt not in {'', 'n/d'}
                and data_sw_fmt == data_pag_fmt
                and (bool(row_dict.get('switching_antes_pagamento')) or bool(row_dict.get('switching_depois_pagamento')))
            )
        )
        necessita_switching_txt = str(ledger.get('necessita_switching') or _texto_necessita_switching({**central, **row_dict}, estrategia)).strip().lower()
        pacote_dia = str(ledger.get('pacote_do_dia') or _texto_pacote_do_dia({**central, **row_dict}, estrategia))
        estrategia_indica_switching = bool(
            str(estrategia).strip() == 'switching_simples'
            or str(pacote_dia).strip() in {'switch_then_pay', 'pay_then_switch', 'switch_only'}
        )
        sem_fonte_pos_switch_materializada = bool(
            _eh_indeterminado(lote_sugerido)
            and estrategia_indica_switching
            and necessita_switching_txt == 'sim'
            and _eh_indeterminado(lote_pos_switch)
            and (not fonte_operacional_auditavel)
        )
        sem_evidencia_materializacao_sw = bool(
            _eh_indeterminado(lote_pos_switch)
            and (data_sw_fmt in {'', 'n/d'} or data_sw_fmt != data_pag_fmt)
        )
        if sem_fonte_pos_switch_materializada:
            status_row_base = 'fonte_pos_switching_nao_materializada'
            motivo_row_base = 'fonte_pos_switching_nao_materializada'
            lote_pos_switch = ''
            origem_switching = 'diagnostico_nao_materializado'

        fonte_auditavel_contexto = mapa_fontes_elegiveis_auditaveis.get(str(pagamento_id or '').strip(), {})
        ledger_aud = ledger if isinstance(ledger, dict) else {}

        fonte_candidata_id_aud = _primeiro_valor_auditavel(
            ledger_aud.get('fonte_candidata_id'),
            fonte_auditavel_contexto.get('fonte_candidata_id'),
            padrao='n/d',
        )
        tipo_fonte_candidata_aud = _primeiro_valor_auditavel(
            ledger_aud.get('tipo_fonte_candidata'),
            fonte_auditavel_contexto.get('tipo_fonte_candidata'),
            padrao='n/d',
        )
        origem_fonte_candidata_aud = _primeiro_valor_auditavel(
            ledger_aud.get('origem_fonte_candidata'),
            fonte_auditavel_contexto.get('origem_fonte_candidata'),
            padrao='n/d',
        )
        motivo_descarte_fonte_aud = _primeiro_valor_auditavel(
            ledger_aud.get('motivo_descarte_fonte'),
            fonte_auditavel_contexto.get('motivo_descarte_fonte'),
            padrao='',
        )
        status_ledger_aud = _primeiro_valor_auditavel(
            ledger_aud.get('status'),
            fonte_auditavel_contexto.get('status'),
            padrao='',
        )
        motivo_bloqueio_ledger_aud = _primeiro_valor_auditavel(
            ledger_aud.get('motivo_bloqueio'),
            fonte_auditavel_contexto.get('motivo_bloqueio'),
            padrao='',
        )
        saldo_liquido_disponivel_aud = _primeiro_valor_auditavel(
            ledger_aud.get('saldo_liquido_disponivel'),
            ledger_aud.get('saldo_liquido'),
            fonte_auditavel_contexto.get('saldo_liquido_disponivel'),
            padrao='',
        )

        # V13-C: prioridade de sobrescrita auditavel para recebido_disponivel.
        usar_fonte_contexto_recebido_sem_saldo = bool(
            sem_saldo_temporal_auditavel
            and _norm(fonte_auditavel_contexto.get('tipo_fonte_candidata')) == 'recebido_disponivel'
        )

        if usar_fonte_contexto_recebido_sem_saldo:
            fonte_candidata_id_aud = _primeiro_valor_auditavel(
                fonte_auditavel_contexto.get('fonte_candidata_id'),
                fonte_candidata_id_aud,
                padrao='n/d',
            )
            tipo_fonte_candidata_aud = _primeiro_valor_auditavel(
                fonte_auditavel_contexto.get('tipo_fonte_candidata'),
                tipo_fonte_candidata_aud,
                padrao='n/d',
            )
            origem_fonte_candidata_aud = _primeiro_valor_auditavel(
                fonte_auditavel_contexto.get('origem_fonte_candidata'),
                origem_fonte_candidata_aud,
                padrao='n/d',
            )
            status_ledger_aud = _primeiro_valor_auditavel(
                fonte_auditavel_contexto.get('status'),
                status_ledger_aud,
                padrao='',
            )
            motivo_bloqueio_ledger_aud = _primeiro_valor_auditavel(
                fonte_auditavel_contexto.get('motivo_bloqueio'),
                motivo_bloqueio_ledger_aud,
                padrao='',
            )
            motivo_descarte_fonte_aud = _primeiro_valor_auditavel(
                fonte_auditavel_contexto.get('motivo_descarte_fonte'),
                motivo_descarte_fonte_aud,
                padrao='',
            )
            saldo_liquido_disponivel_aud = _primeiro_valor_auditavel(
                fonte_auditavel_contexto.get('saldo_liquido_disponivel'),
                saldo_liquido_disponivel_aud,
                padrao='',
            )

        linha_saida = {
            **({
                'Motivo pos sw': (
                    'sem_saldo_confiavel'
                    if (
                        (str(row_dict.get('motivo_pos_sw') or '').strip() in {'', 'n/d'})
                        and (str(row_dict.get('status_recomendacao') or '').strip() == 'lote_ja_migrado_janela')
                        and (_round_monetario(row_dict.get('saldo_pos_sw'), 0.0) == 0.0)
                    )
                    else (
                        'nao_criada'
                        if (
                            (str(row_dict.get('motivo_pos_sw') or '').strip() in {'', 'n/d'})
                            and (str(row_dict.get('status_recomendacao') or '').strip() == 'lote_ja_migrado_janela')
                        )
                        else (_texto_decisao(row_dict.get('motivo_pos_sw')) if str(row_dict.get('motivo_pos_sw') or '').strip() else 'n/d')
                    )
                )
            }),
            'Data': _fmt_data(row.get('data_pagamento')),
            'Conta': row.get('descricao_pagamento') or '',
            'Despesa ID': pagamento_id,
            'Valor': valor,
            'Lote sugerido': lote_sugerido,
            'Saldo Antes': resumo.get('Saldo Antes', ''),
            'Bruto': resumo.get('Bruto', ''),
            'Imposto': resumo.get('Imposto', ''),
            'Líquido': liquido,
            'Saldo Remanescente': resumo.get('Saldo Remanescente', ''),
            'Cobertura integral': str(ledger.get('cobertura_integral') or 'não'),
            'Estratégia': estrategia,
            'Pacote do dia': pacote_dia,
            'Lote reserva': lote_reserva,
            'Lote pós-switching': _texto_decisao(ledger.get('lote_pos_switching_materializado')),
            'Destino switching': _texto_decisao(ledger.get('destino_switching_operacional')),
            'Origem switching': _texto_decisao(ledger.get('origem_switching_operacional')),
            'Fonte switching': ('materializado' if bool(ledger.get('switching_materializado')) else ''),
            'Data switching': _fmt_data(ledger.get('data_switching_operacional')) if ledger.get('data_switching_operacional') is not None else 'n/d',
            'Evento switching ID': ledger.get('evento_switching_id') or '',
            'Score switching': _round_monetario(row_dict.get('score_switching_shadow') if row_dict.get('score_switching_shadow') not in (None, '') else row_dict.get('ganho_liquido_estimado_switching'), ''),
            'Necessita switching': necessita_switching_txt if necessita_switching_txt in {'sim', 'não'} else _texto_necessita_switching({**central, **row_dict}, estrategia),
            'Switching antes do pagamento': ('sim' if str(ledger.get('pacote_do_dia') or '') == 'switch_then_pay' else 'não'),
            'Switching depois do pagamento': ('sim' if str(ledger.get('pacote_do_dia') or '') == 'pay_then_switch' else 'não'),
            'Motivo bloqueio lote': _texto_decisao(ledger.get('motivo_bloqueio')),
            'Status recomendação': _texto_decisao(ledger.get('status')),
            'Saldo temp. ant.': ('n/d' if str(ledger.get('status') or '') == 'switch_then_pay_sem_materializacao' else (_round_monetario(ledger.get('saldo_antes'), 'n/d') if fonte_operacional_auditavel else 'n/d')),
            'Consumo temp.': ('n/d' if str(ledger.get('status') or '') == 'switch_then_pay_sem_materializacao' else (_round_monetario(ledger.get('consumo'), 'n/d') if fonte_operacional_auditavel else 'n/d')),
            'Saldo temp. dep.': ('n/d' if str(ledger.get('status') or '') == 'switch_then_pay_sem_materializacao' else (_round_monetario(ledger.get('saldo_depois'), 'n/d') if fonte_operacional_auditavel else 'n/d')),
            'Pos sw?': 'sim' if bool(row_dict.get('pos_sw_tentativa')) else 'não',
            'Fonte pos sw': _texto_decisao(row_dict.get('lote_nome_operacional') or row_dict.get('fonte_pos_sw')) if str(row_dict.get('lote_nome_operacional') or row_dict.get('fonte_pos_sw') or '').strip() else 'n/d',
            'Saldo pos sw': _round_monetario(row_dict.get('saldo_pos_sw'), 'n/d'),
            'Origem saldo pos': _texto_decisao(row_dict.get('origem_saldo_pos_sw')) if str(row_dict.get('origem_saldo_pos_sw') or '').strip() else 'n/d',
            'Bruto pos': _round_monetario(row_dict.get('saldo_pos_sw_bruto_candidato'), 'n/d'),
            'Líq. pos': _round_monetario(row_dict.get('saldo_pos_sw_liquido_candidato'), 'n/d'),
            'Data saldo pos': _fmt_data(row_dict.get('data_base_saldo_pos_sw')) if row_dict.get('data_base_saldo_pos_sw') not in (None, '') else 'n/d',
            'Motivo saldo pos': _texto_decisao(row_dict.get('motivo_saldo_pos_sw')) if str(row_dict.get('motivo_saldo_pos_sw') or '').strip() else 'n/d',
            'fonte_candidata_id': fonte_candidata_id_aud,
            'tipo_fonte_candidata': tipo_fonte_candidata_aud,
            'origem_fonte_candidata': origem_fonte_candidata_aud,
            'elegivel_temporalmente': ledger.get('elegivel_temporalmente'),
            'saldo_liquido_disponivel': saldo_liquido_disponivel_aud,
            'elegivel_liquidez_carencia': ledger.get('elegivel_liquidez_carencia'),
            'promovida_para_lote_sugerido': ledger.get('promovida_para_lote_sugerido'),
            'etapa_descarte_fonte': ledger.get('etapa_descarte_fonte') or '',
            'motivo_descarte_fonte': motivo_descarte_fonte_aud,
            'origem_motivo_descarte': ledger.get('origem_motivo_descarte') or '',
            'evento_switching_id': ledger.get('evento_switching_id') or '',
            'lote_pos_switching_materializado': ledger.get('lote_pos_switching_materializado') or '',
            'pacote_do_dia_ledger': ledger.get('pacote_do_dia') or '',
            'status_ledger': status_ledger_aud,
            'motivo_bloqueio_ledger': motivo_bloqueio_ledger_aud,
            'fifo_pagamento_id': ledger.get('fifo_pagamento_id'),
            'fifo_data_pagamento': ledger.get('fifo_data_pagamento'),
            'fifo_valor_pagamento': ledger.get('fifo_valor_pagamento'),
            'fifo_qtd_lotes_estado': ledger.get('fifo_qtd_lotes_estado'),
            'fifo_qtd_lotes_avaliados': ledger.get('fifo_qtd_lotes_avaliados'),
            'fifo_qtd_lotes_saldo_suficiente': ledger.get('fifo_qtd_lotes_saldo_suficiente'),
            'fifo_qtd_lotes_bloqueados_por_saldo': ledger.get('fifo_qtd_lotes_bloqueados_por_saldo'),
            'fifo_qtd_lotes_bloqueados_por_data': ledger.get('fifo_qtd_lotes_bloqueados_por_data'),
            'fifo_qtd_lotes_bloqueados_por_carencia': ledger.get('fifo_qtd_lotes_bloqueados_por_carencia'),
            'fifo_qtd_lotes_bloqueados_por_migracao': ledger.get('fifo_qtd_lotes_bloqueados_por_migracao'),
            'fifo_melhor_lote_candidato': ledger.get('fifo_melhor_lote_candidato'),
            'fifo_saldo_melhor_lote': ledger.get('fifo_saldo_melhor_lote'),
            'fifo_data_aplicacao_melhor_lote': ledger.get('fifo_data_aplicacao_melhor_lote'),
            'fifo_carencia_melhor_lote': ledger.get('fifo_carencia_melhor_lote'),
            'fifo_motivo_nao_promocao': ledger.get('fifo_motivo_nao_promocao'),
        }
        if str(linha_saida.get('Lote sugerido') or '').strip() != str(_texto_decisao(ledger.get('lote_sugerido_operacional')) or '').strip():
            sombra_div['sombra_lote_sugerido_diferente_ledger'] += 1
        if str(linha_saida.get('Saldo Antes') or '').strip() != str(resumo.get('Saldo Antes') or '').strip():
            sombra_div['sombra_saldo_antes_diferente_ledger'] += 1
        if str(linha_saida.get('Bruto') or '').strip() != str(resumo.get('Bruto') or '').strip():
            sombra_div['sombra_bruto_diferente_ledger'] += 1
        if str(linha_saida.get('Imposto') or '').strip() != str(resumo.get('Imposto') or '').strip():
            sombra_div['sombra_imposto_diferente_ledger'] += 1
        if str(linha_saida.get('Líquido') or '').strip() != str(liquido or '').strip():
            sombra_div['sombra_liquido_diferente_ledger'] += 1
        if str(linha_saida.get('Saldo Remanescente') or '').strip() != str(resumo.get('Saldo Remanescente') or '').strip():
            sombra_div['sombra_saldo_remanescente_diferente_ledger'] += 1
        if str(linha_saida.get('Status recomendação') or '').strip() != str(_texto_decisao(ledger.get('status') or status_row_base) or '').strip():
            sombra_div['sombra_status_diferente_ledger'] += 1
        if str(linha_saida.get('Cobertura integral') or '').strip() != str(ledger.get('cobertura_integral') or 'não').strip():
            sombra_div['sombra_cobertura_diferente_ledger'] += 1
        if str(linha_saida.get('Motivo bloqueio lote') or '').strip() != str(_texto_decisao(ledger.get('motivo_bloqueio') or motivo_row_base) or '').strip():
            sombra_div['sombra_motivo_diferente_ledger'] += 1
        lote_pos_switching_ledger_render = _texto_decisao(ledger.get('lote_pos_switching_materializado'))
        if str(linha_saida.get('Lote pós-switching') or '').strip() != str(lote_pos_switching_ledger_render or '').strip():
            sombra_div['sombra_pos_switching_diferente_ledger'] += 1

        flags_pre = _validar_invariantes_extrato_futuro_linha_nao_mutavel(linha_saida)
        for k in pre_invariante:
            pre_invariante[k] += int(flags_pre.get(k, 0) or 0)
        linha_saida = _aplicar_invariantes_extrato_futuro_linha(linha_saida)
        linhas.append(linha_saida)
    global _PRE_INVARIANTE_EXTRATO_FUTURO, _SOMBRA_DIVERGENCIAS_LEDGER
    _PRE_INVARIANTE_EXTRATO_FUTURO = pre_invariante
    _SOMBRA_DIVERGENCIAS_LEDGER = sombra_div
    return linhas





def _validar_invariantes_extrato_futuro_linha_nao_mutavel(linha: dict[str, Any]) -> dict[str, int]:
    lote = _norm(linha.get('Lote sugerido'))
    sem_lote = lote in {'', 'n/d', 'nd', 'não determinado', 'nao determinado'}
    status = _norm(linha.get('Status recomendação'))
    motivo = _norm(linha.get('Motivo bloqueio lote'))
    cob = _norm(linha.get('Cobertura integral'))
    bloqueios = {'sem_saldo_temporal_auditavel', 'sem_fonte_auditavel', 'switch_then_pay_sem_materializacao', 'fonte_pos_switching_nao_materializada'}

    tem_valores_op = any(str(linha.get(k) or '').strip() not in {'', 'n/d'} for k in ['Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente', 'Saldo temp. ant.', 'Consumo temp.', 'Saldo temp. dep.'])
    return {
        'pre_invariante_lote_nd_com_status_ok': int(sem_lote and status == 'ok'),
        'pre_invariante_lote_nd_com_cobertura_sim': int(sem_lote and cob == 'sim'),
        'pre_invariante_lote_nd_com_valores_operacionais': int(sem_lote and tem_valores_op),
        'pre_invariante_cobertura_sim_status_nao_ok': int(cob == 'sim' and status != 'ok'),
        'pre_invariante_status_bloqueado_com_valores_operacionais': int(status in bloqueios and tem_valores_op),
        'pre_invariante_motivo_bloqueante_status_ok': int(status == 'ok' and motivo not in {'', 'n/d', 'nd', 'não determinado', 'nao determinado'}),
        'pre_invariante_lote_nd_com_saldo_antes': int(sem_lote and str(linha.get('Saldo Antes') or '').strip() not in {'', 'n/d'}),
        'pre_invariante_lote_nd_com_bruto': int(sem_lote and str(linha.get('Bruto') or '').strip() not in {'', 'n/d'}),
        'pre_invariante_lote_nd_com_liquido': int(sem_lote and str(linha.get('Líquido') or '').strip() not in {'', 'n/d'}),
        'pre_invariante_lote_nd_com_saldo_remanescente': int(sem_lote and str(linha.get('Saldo Remanescente') or '').strip() not in {'', 'n/d'}),
        'pre_invariante_status_bloqueado_com_saldo_antes': int(status in bloqueios and str(linha.get('Saldo Antes') or '').strip() not in {'', 'n/d'}),
        'pre_invariante_status_bloqueado_com_consumo_temporal': int(status in bloqueios and str(linha.get('Consumo temp.') or '').strip() not in {'', 'n/d'}),
    }


def _aplicar_invariantes_extrato_futuro_linha(linha: dict[str, Any]) -> dict[str, Any]:
    lote = _norm(linha.get('Lote sugerido'))
    sem_lote = lote in {'', 'n/d', 'nd', 'não determinado', 'nao determinado'}
    status = _norm(linha.get('Status recomendação'))
    motivo = _norm(linha.get('Motivo bloqueio lote'))
    cob = _norm(linha.get('Cobertura integral'))
    pacote = _norm(linha.get('Pacote do dia'))
    necessita = _norm(linha.get('Necessita switching'))
    estrategia = _norm(linha.get('Estratégia'))

    bloqueios = {'sem_saldo_temporal_auditavel', 'sem_fonte_auditavel', 'switch_then_pay_sem_materializacao', 'fonte_pos_switching_nao_materializada'}

    # coerência estratégia/pacote/switch
    if pacote == 'pay_only' and necessita == 'não':
        linha['Estratégia'] = 'sem_switching'
    if _norm(linha.get('Estratégia')) == 'switching_simples' and pacote == 'pay_only' and necessita == 'não':
        linha['Estratégia'] = 'sem_switching'

    # sem lote auditável: nesta fase não mutar status/cobertura/motivo
    if sem_lote:
        pass

    status = _norm(linha.get('Status recomendação'))
    motivo = _norm(linha.get('Motivo bloqueio lote'))
    cob = _norm(linha.get('Cobertura integral'))

    # cobertura/status/motivo: validação não-mutável já feita no validador sombra
    if cob == 'sim':
        pass

    # motivo bloqueante vs status/cobertura: sem mutação nesta fase
    motivo = _norm(linha.get('Motivo bloqueio lote'))

    # status de bloqueio: manter limpeza financeira/temporal, sem mutar cobertura/status/motivo
    status = _norm(linha.get('Status recomendação'))
    if status in bloqueios:
        pass

    lote_pos = _norm(linha.get('Lote pós-switching'))
    if pacote == 'switch_then_pay' and lote_pos in {'', 'n/d', 'nd'}:
        pass

    # sincroniza trilha de auditoria com estado final operacional
    linha['status_ledger'] = linha.get('Status recomendação')
    linha['motivo_bloqueio_ledger'] = linha.get('Motivo bloqueio lote')
    linha['pacote_do_dia_ledger'] = linha.get('Pacote do dia')

    lote_final_nd = _norm(linha.get('Lote sugerido')) in {'', 'n/d', 'nd', 'não determinado', 'nao determinado'}
    if lote_final_nd:
        linha['promovida_para_lote_sugerido'] = False
        if str(linha.get('etapa_descarte_fonte') or '').strip() == '':
            linha['etapa_descarte_fonte'] = 'selecao_fonte_operacional'
        if str(linha.get('motivo_descarte_fonte') or '').strip() == '':
            if str(linha.get('Lote reserva') or '').strip() not in {'', 'n/d', 'não determinado', 'nao determinado'}:
                linha['motivo_descarte_fonte'] = 'reserva_nao_promovida_sem_motivo_estruturado'
                linha['origem_motivo_descarte'] = 'causa_nao_rastreada_no_pipeline'
            else:
                linha['motivo_descarte_fonte'] = 'sem_fonte_auditavel'
                linha['origem_motivo_descarte'] = 'registrada_pipeline'
        elif str(linha.get('origem_motivo_descarte') or '').strip() == '':
            linha['origem_motivo_descarte'] = 'registrada_pipeline'

    return _normalizar_sem_fonte_valida_extrato_futuro(linha)

def _texto_decisao(valor: Any) -> str:
    txt = str(valor or '').strip()
    return txt if txt else 'não determinado'


def _texto_pacote_do_dia(row: dict[str, Any], estrategia: str) -> str:
    pacote_real = str(row.get('pacote_dia_escolhido') or '').strip()
    if pacote_real:
        return pacote_real
    if estrategia == 'sem_switching' or estrategia == 'combinacao_minima':
        return 'pay_only'
    if estrategia == 'switching_simples':
        data_pag = row.get('data_pagamento')
        data_sw = row.get('data_sugerida_switching')
        if data_pag is not None and data_sw is not None:
            try:
                data_pag_cmp = data_pag.isoformat() if hasattr(data_pag, 'isoformat') else str(data_pag)
                data_sw_cmp = data_sw.isoformat() if hasattr(data_sw, 'isoformat') else str(data_sw)
                return 'switch_then_pay' if data_sw_cmp <= data_pag_cmp else 'pay_then_switch'
            except Exception:
                return 'não determinado'
    return 'não determinado'


def _texto_necessita_switching(row: dict[str, Any], estrategia: str) -> str:
    valor = row.get('necessita_switching')
    if valor is None:
        valor = row.get('necessidade_switching')
    if isinstance(valor, bool):
        return 'sim' if valor else 'não'
    if hasattr(valor, 'item'):
        try:
            convertido = valor.item()
            if isinstance(convertido, bool):
                return 'sim' if convertido else 'não'
            valor = convertido
        except Exception:
            pass
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        if valor == 1:
            return 'sim'
        if valor == 0:
            return 'não'
    txt = str(valor or '').strip().lower()
    if txt in {'sim', 'true', '1'}:
        return 'sim'
    if txt in {'não', 'nao', 'false', '0'}:
        return 'não'
    if estrategia == 'switching_simples':
        return 'sim'
    return 'não determinado'


def _primeiro_texto_preenchido(*valores: Any) -> str:
    for valor in valores:
        txt = str(valor or '').strip()
        if txt:
            return txt
    return ''


def _texto_lote_reserva(lote_reserva: Any, lote_sugerido: Any) -> str:
    reserva = str(lote_reserva or '').strip()
    sugerido = str(lote_sugerido or '').strip()
    if not reserva:
        return 'não determinado'
    if sugerido and reserva == sugerido:
        return 'não determinado'
    return reserva

def _construir_switchings(contexto: Any, limite: int = 30) -> list[dict[str, Any]]:
    shadow = getattr(contexto, 'switching_economico_shadow', None)
    plano = getattr(shadow, 'plano_shadow', None) if shadow is not None else None
    linhas: list[dict[str, Any]] = []
    lotes_by_id = {str(l.id): l for l in (getattr(getattr(contexto, 'replay_passado', None), 'lotes_apos_replay', []) or [])}
    ranking = getattr(contexto, 'ranking_carteira', None)
    quadro_ranking = getattr(ranking, 'quadro_destinos_switch', None) if ranking is not None else None
    rank_por_produto_key: dict[str, int] = {}
    if isinstance(quadro_ranking, pd.DataFrame) and len(quadro_ranking):
        for _, r in quadro_ranking.iterrows():
            rank_por_produto_key[str(r.get('produto_key') or '')] = int(r.get('rank_destino') or 999)
    bloqueados_auditoria: list[dict[str, Any]] = []

    if isinstance(plano, pd.DataFrame) and len(plano):
        plano_f = plano.copy()
        if 'recomendado_shadow' in plano_f.columns:
            plano_f = plano_f[plano_f['recomendado_shadow'].fillna(False)]
        plano_f = plano_f.sort_values(['ganho_liquido_estimado', 'score_switch_shadow', 'lote_id'], ascending=[False, False, True], kind='stable')
        usados: set[str] = set()
        for _, row in plano_f.iterrows():
            lote_id = str(row.get('lote_id') or '')
            if not lote_id or lote_id in usados:
                continue
            lote = lotes_by_id.get(lote_id)
            if lote is None:
                continue
            destino_rank = _ranking_destino_para_lote(contexto, lote) or {}
            destino_row_nome = str(row.get('produto_destino_nome') or '').strip()
            destino_row_key = str(row.get('produto_destino_key') or '').strip()
            destino_nome = destino_row_nome or str(destino_rank.get('nome') or '')
            data_sug = _data_sugerida_switching_lote(contexto, lote)
            ganho = _round_monetario(row.get('ganho_liquido_estimado'), _round_monetario(destino_rank.get('proxy_terminal_destino'), 0.0))
            valor_liq = _round_monetario(lote.valor_liquido_hoje(contexto.execucao.data_referencia, tabela_iof=contexto.tabela_iof, faixas_ir=contexto.faixas_ir), 0.0)
            linha_base = {
                'Data sugerida': _fmt_data(data_sug),
                'Data': _fmt_data(data_sug),
                'Lote origem': lote_id,
                'Produto origem': getattr(lote, 'investimento', '') if lote is not None else row.get('produto_origem_nome') or '',
                'Produto destino switching': destino_nome,
                'Destino': destino_nome,
                'Ganho estimado': ganho,
                'Valor líquido origem': valor_liq,
                'Status': 'destino_ranqueado',
            }
            rank_origem = int(row.get('rank_origem') or rank_por_produto_key.get(str(getattr(lote, 'produto_key', '') or ''), 999))
            rank_destino = int(row.get('rank_destino_sugerido') or row.get('rank_destino') or destino_rank.get('rank_destino') or 999)
            carencia_incremental = int(row.get('dias_carencia_incremental') or row.get('carencia_dias') or destino_rank.get('carencia_dias') or 0)
            pagamentos_janela = _round_monetario(row.get('pagamentos_na_janela_carencia') or row.get('pagamentos_janela_carencia'), 0.0)
            motivo_gate = str(row.get('motivo_gate_switching') or '').strip()
            bloqueado = bool(row.get('bloqueado_pos_gate')) or bool(motivo_gate)
            if bloqueado:
                bloqueados_auditoria.append({
                    **linha_base,
                    'Rank origem': rank_origem,
                    'Rank destino': rank_destino,
                    'Dias carência incremental': carencia_incremental,
                    'Pagamentos na janela': pagamentos_janela,
                    'Status': motivo_gate or 'candidato_bloqueado_gate',
                })
            else:
                linhas.append({**linha_base, 'Status': 'destino_ranqueado_elegivel'})
            usados.add(lote_id)
            if len(linhas) >= limite:
                break
    try:
        setattr(contexto, '_switchings_bloqueados_gate_auditoria', bloqueados_auditoria)
    except Exception:
        pass
    return linhas


def _construir_ranking_amostra(contexto: Any, limite: int = 10) -> list[dict[str, Any]]:
    ranking = getattr(contexto, 'ranking_carteira', None)
    destinos = getattr(ranking, 'quadro_destinos_switch', None) if ranking is not None else None
    if not isinstance(destinos, pd.DataFrame) or len(destinos) == 0:
        return []
    linhas = []
    for _, row in destinos.head(limite).iterrows():
        status = str(row.get('Status_Confirmação') or '').strip()
        linhas.append({
            'Rank': row.get('rank_destino'),
            'Produto': row.get('nome'),
            'Score': row.get('score_final'),
            'Proxy terminal': row.get('proxy_terminal_destino'),
            'Liquidez': row.get('liquidez_dias'),
            'Carência': row.get('carencia_dias'),
            'Ticket mín.': row.get('aplicacao_minima'),
            'Status': 'elegível' if status in {'', 'Confirmado', 'confirmado'} else status,
        })
    return linhas


def _construir_lotes_situacao(
    contexto: Any,
    destinos_pos_switching_passivos: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    replay = getattr(contexto, 'replay_passado', None)
    if replay is None:
        return [], []
    data_referencia = contexto.execucao.data_referencia
    cal = contexto.calendario_financeiro
    config = contexto.pacote_config.conteudo
    serie_cdi = getattr(getattr(contexto, 'cache_cdi', None), 'serie_cdi', None)
    limiar = obter_limiar_residuo_resolvido(config)
    tabela_iof = contexto.tabela_iof
    faixas_ir = contexto.faixas_ir
    log = replay.log_passado.copy() if isinstance(getattr(replay, 'log_passado', None), pd.DataFrame) else None
    lotes_ativos: list[dict[str, Any]] = []
    lotes_exauridos: list[dict[str, Any]] = []

    def _ultimo_uso_lote(lote_id: Any) -> str:
        if log is None or len(log) == 0 or 'Lote' not in log.columns:
            return ''
        sub = log[log['Lote'].fillna('').astype(str) == str(lote_id)]
        if len(sub) == 0:
            return ''
        data_ult = sub['Data'].max() if 'Data' in sub.columns else None
        return data_ult.isoformat() if hasattr(data_ult, 'isoformat') else str(data_ult or '')

    for lote in sorted(replay.lotes_apos_replay, key=lambda x: (x.data_recebimento, x.data_aplicacao, x.id)):
        if lote.data_recebimento > data_referencia or lote.data_aplicacao > data_referencia:
            continue
        try:
            saldo_bruto = round(float(lote.valor_bruto_em_data(data_referencia, cal, serie_cdi=serie_cdi, data_base_referencia=data_referencia) or 0.0), 2)
            saldo_liquido = round(float(lote.valor_liquido_em_data(data_referencia, cal, tabela_iof=tabela_iof, faixas_ir=faixas_ir, serie_cdi=serie_cdi, data_base_referencia=data_referencia) or 0.0), 2)
        except Exception:
            saldo_bruto = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
            saldo_liquido = round(float(lote.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
        saldo_rem = round(float(getattr(lote, 'principal_remanescente', 0.0) or 0.0), 2)
        ultimo_uso_txt = _ultimo_uso_lote(lote.id)
        exaurido = bool(lote.esgotado or saldo_bruto <= limiar or saldo_liquido <= limiar or saldo_rem <= limiar)

        # V218: para lotes ativos, a idade do investimento deve usar a data
        # atual/de referência da execução; para lotes exauridos, preserva-se a
        # data do último uso como referência histórica. Em ambos os casos, a
        # contagem parte da data de aplicação, nunca da data de recebimento.
        data_base_tempo = data_referencia
        if exaurido and ultimo_uso_txt:
            try:
                data_base_tempo = date.fromisoformat(str(ultimo_uso_txt))
            except Exception:
                data_base_tempo = data_referencia
        idade_lote_v218 = calcular_dias_lote(
            lote.data_aplicacao,
            data_base_tempo,
            cal,
            serie_cdi=serie_cdi,
            data_fechamento_referencia=data_base_tempo,
        )
        dias_corridos = idade_lote_v218["dias_corridos"]
        dias_uteis = idade_lote_v218["dias_uteis"]
        saldo_bruto_exib, saldo_liquido_exib, saldo_rem_exib = normalizar_valores_situacao_atual_exaurida(saldo_bruto=saldo_bruto, saldo_liquido=saldo_liquido, saldo_rem=saldo_rem, exaurido=exaurido)
        linha = {
            'Lote': lote.id,
            'Recebimento': _fmt_data(lote.data_recebimento),
            'Aplicação': _fmt_data(lote.data_aplicacao),
            'Último uso': ultimo_uso_txt,
            'Produto': lote.investimento,
            'Dias corridos': dias_corridos,
            'Dias úteis': dias_uteis,
            'Valor original': round(float(getattr(lote, 'valor_inicial', 0.0) or 0.0), 2),
            'Bruto': saldo_bruto_exib,
            'Líquido': saldo_liquido_exib,
            'Saldo rem': saldo_rem_exib,
        }
        if exaurido:
            lotes_exauridos.append(linha)
        else:
            lotes_ativos.append(linha)
    destinos_pos_switching_passivos = list(destinos_pos_switching_passivos or [])
    origens_migradas = {str(x.get('lote_origem') or '').strip() for x in destinos_pos_switching_passivos if str(x.get('lote_origem') or '').strip()}
    if origens_migradas:
        lotes_ativos = [x for x in lotes_ativos if str(x.get('Lote') or '').strip() not in origens_migradas]
    for idx, item in enumerate(destinos_pos_switching_passivos, start=1):
        lote_pos_switching = str(item.get('lote_pos_switching') or '').strip() or f"lote_pos_switching_audit::{idx}"
        valor_original_pos_switching = _round_monetario(item.get('valor_liquido_origem'), 0.0)
        precificacao_pos_switching = _precificar_destino_pos_switching_canonico(
            contexto,
            item,
            lote_id=lote_pos_switching,
            valor_original=valor_original_pos_switching,
        )
        bruto_pos_switching = _round_monetario(precificacao_pos_switching.get('bruto'), valor_original_pos_switching)
        liquido_pos_switching = _round_monetario(precificacao_pos_switching.get('liquido'), valor_original_pos_switching)
        lotes_ativos.append({
            'Lote': lote_pos_switching,
            'Recebimento': _fmt_data(item.get('data_switching')),
            'Aplicação': _fmt_data(item.get('data_switching')),
            'Último uso': '',
            'Produto': str(item.get('produto_destino') or '').strip(),
            'Dias corridos': '',
            'Dias úteis': '',
            'Valor original': valor_original_pos_switching,
            'Bruto': bruto_pos_switching,
            'Líquido': liquido_pos_switching,
            'Saldo rem': bruto_pos_switching,
            'Status': 'ativo_pos_switching',
            'Origem migrada': str(item.get('lote_origem') or '').strip(),
            'Data switching': _fmt_data(item.get('data_switching')),
            'Evento switching ID': str(item.get('evento_switching_id') or '').strip(),
            'Status materialização': str(item.get('status_materializacao_passiva') or '').strip(),
            'Método precificação pós-switching': str(precificacao_pos_switching.get('metodo') or ''),
        })
    lotes_exauridos.sort(key=lambda item: (str(item.get('Último uso') or ''), str(item.get('Aplicação') or ''), str(item.get('Lote') or '')), reverse=True)
    lotes_ativos.sort(key=lambda item: (str(item.get('Aplicação') or ''), str(item.get('Lote') or '')), reverse=True)
    return lotes_ativos, lotes_exauridos


def _aplicar_consumo_pagamentos_passados_lotes_pos_switching(
    contexto: Any,
    extrato_passado: list[dict[str, Any]],
    lotes_ativos: list[dict[str, Any]],
    lotes_exauridos: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    dados_ops = getattr(contexto, 'dados_operacionais', None)
    gastos = getattr(dados_ops, 'gastos_canonicos', None) if dados_ops is not None else None
    pos_df = getattr(dados_ops, 'lotes_pos_switching_normalizados', None) if dados_ops is not None else None
    limiar = obter_limiar_residuo_resolvido(contexto.pacote_config.conteudo)

    base_aud = {
        'qtd_pagamentos_passados_pos_detectados': 0,
        'qtd_pagamentos_passados_pos_com_saldo_antes_preenchido': 0,
        'qtd_pagamentos_passados_pos_com_saldo_remanescente_preenchido': 0,
        'qtd_despesas_multifonte_pos': 0,
        'qtd_lotes_pos_exauridos_apos_consumo': 0,
        'qtd_lotes_pos_ativos_com_saldo_abatido': 0,
        'qtd_lotes_pos_com_valoracao_previa_usada': 0,
        'status_geral_q5c': 'diagnostico_inconclusivo',
    }
    if not isinstance(gastos, pd.DataFrame) or gastos.empty or not isinstance(pos_df, pd.DataFrame) or pos_df.empty:
        return extrato_passado, lotes_ativos, lotes_exauridos, base_aud

    def _norm(v: Any) -> str:
        return str(v or '').strip().lower()

    def _parts(txt: Any) -> list[str]:
        return [_norm(x) for x in str(txt or '').split('+') if _norm(x)]

    def _pick_num(linha: dict[str, Any], chaves: list[str], fallback: float) -> float:
        for c in chaves:
            v = linha.get(c)
            n = _round_monetario(v, None)
            if n is not None and n != '':
                return float(n)
        return float(fallback)

    pos_ids = {_norm(x.get('lote_id')) for _, x in pos_df.iterrows() if _norm(x.get('lote_id'))}
    ativos_nao_pos = []
    ativos_pos_agrupados: dict[str, list[dict[str, Any]]] = {}
    for l in list(lotes_ativos or []):
        lid = _norm(l.get('Lote'))
        if lid in pos_ids:
            ativos_pos_agrupados.setdefault(lid, []).append(dict(l))
        else:
            ativos_nao_pos.append(dict(l))

    def _sum_field(rows, campo):
        vals=[_round_monetario(r.get(campo), None) for r in rows]
        vals=[float(v) for v in vals if v not in (None,'')]
        return _round_monetario(sum(vals), None) if vals else None

    ativos_por_lote: dict[str, dict[str, Any]] = {}
    qtd_lotes_pos_ativos_duplicados_consolidados = 0
    for lid, rows in ativos_pos_agrupados.items():
        base = dict(rows[0])
        if len(rows) > 1:
            qtd_lotes_pos_ativos_duplicados_consolidados += 1
            for c in ['Bruto','Líquido','Saldo rem','Patr. líq.']:
                sv = _sum_field(rows, c)
                if sv not in (None,''):
                    base[c] = sv
        ativos_por_lote[lid] = base
    pos_saldos: dict[str, dict[str, float]] = {}
    uso_val_prev = 0
    lotes_pos_duplicados: set[str] = set()
    for _, r in pos_df.iterrows():
        lid = _norm(r.get('lote_id'))
        if not lid:
            continue
        valor_original = float(_round_monetario(r.get('valor_original'), 0.0) or 0.0)
        linha_ativa = ativos_por_lote.get(lid)
        if linha_ativa:
            saldo_liq = _pick_num(linha_ativa, ['Líquido', 'Liq. atual', 'Valor líquido', 'Patr. líq.', 'Saldo rem'], valor_original)
            saldo_bruto = _pick_num(linha_ativa, ['Bruto', 'Bruto atual', 'Valor bruto'], saldo_liq)
            uso_val_prev += 1
        else:
            saldo_liq = valor_original
            saldo_bruto = valor_original
        if lid not in pos_saldos:
            pos_saldos[lid] = {'saldo_liq': float(saldo_liq), 'bruto_ref': float(saldo_bruto), 'liq_ref': float(saldo_liq), 'qtd_linhas': 1.0}
        else:
            lotes_pos_duplicados.add(lid)
            pos_saldos[lid]['saldo_liq'] += float(saldo_liq)
            pos_saldos[lid]['bruto_ref'] += float(saldo_bruto)
            pos_saldos[lid]['liq_ref'] += float(saldo_liq)
            pos_saldos[lid]['qtd_linhas'] += 1.0

    gastos_ok = gastos[(gastos.get('pago') == True) & (gastos.get('passado_pago_ate_data_referencia') == True)].copy()
    if 'data' in gastos_ok.columns:
        gastos_ok = gastos_ok.sort_values(['data', 'despesa_id'], kind='stable')

    consumo_por_lote: dict[str, list[dict[str, Any]]] = {k: [] for k in pos_saldos.keys()}
    qtd_multifonte_misto = 0
    qtd_fonte_repetida = 0
    for _, g in gastos_ok.iterrows():
        desp = str(g.get('despesa_id') or '').strip()
        if not desp:
            continue
        fontes_raw = _parts(g.get('lote_usado_1')) + _parts(g.get('lote_usado_2'))
        fontes_all = [f for f in fontes_raw if f]
        if not fontes_all:
            continue
        fontes_distintas = list(dict.fromkeys(fontes_all))
        if len(fontes_distintas) < len(fontes_all):
            qtd_fonte_repetida += 1
        fontes_pos = [x for x in fontes_distintas if x in consumo_por_lote]
        if not fontes_pos:
            continue
        if len(fontes_distintas) > len(fontes_pos):
            qtd_multifonte_misto += 1
        valor = float(_round_monetario(g.get('valor'), 0.0) or 0.0)
        valor_rateio = valor / max(len(fontes_distintas), 1)
        for l in fontes_pos:
            consumo_por_lote[l].append({'despesa_id': desp, 'valor': valor_rateio})

    aggr_por_despesa: dict[str, dict[str, Any]] = {}
    for lote_id, itens in consumo_por_lote.items():
        saldo = float(pos_saldos.get(lote_id, {}).get('saldo_liq', 0.0) or 0.0)
        for it in itens:
            desp = it['despesa_id']
            valor = float(it['valor'] or 0.0)
            saldo_antes = float(_round_monetario(saldo, 0.0) or 0.0)
            saldo = float(_round_monetario(saldo - valor, 0.0) or 0.0)
            saldo_rem = 0.0 if saldo <= limiar else float(_round_monetario(saldo, 0.0) or 0.0)
            rec = aggr_por_despesa.setdefault(desp, {'soma_saldo_antes_pos': 0.0, 'soma_saldo_rem_pos': 0.0, 'qtd_fontes_pos': 0, 'lotes': set()})
            rec['soma_saldo_antes_pos'] += saldo_antes
            rec['soma_saldo_rem_pos'] += saldo_rem
            rec['qtd_fontes_pos'] += 1
            rec['lotes'].add(lote_id)
        pos_saldos[lote_id]['saldo_liq'] = saldo

    idx_por_despesa = {str(x.get('Despesa ID') or '').strip(): i for i, x in enumerate(extrato_passado)}
    preench_sa = preench_sr = 0
    multi = 0
    for desp, rec in aggr_por_despesa.items():
        i = idx_por_despesa.get(desp)
        if i is None:
            continue
        linha = dict(extrato_passado[i])
        saldo_antes = _round_monetario(rec['soma_saldo_antes_pos'], 0.0)
        saldo_rem = _round_monetario(rec['soma_saldo_rem_pos'], 0.0)
        linha['Saldo Antes'] = saldo_antes
        linha['Saldo Remanescente'] = saldo_rem
        if int(rec['qtd_fontes_pos']) > 1:
            linha['Multifonte POS'] = 'sim'
            multi += 1
        extrato_passado[i] = linha
        preench_sa += 1 if saldo_antes not in ('', None) else 0
        preench_sr += 1 if saldo_rem not in ('', None) else 0

    novos_ativos = list(ativos_nao_pos)
    novos_exauridos = list(lotes_exauridos)
    ex = at = 0
    for lid, l in ativos_por_lote.items():
        if lid not in pos_saldos:
            novos_ativos.append(l)
            continue
        saldo_final = float(pos_saldos[lid]['saldo_liq'] or 0.0)
        bruto_ref = float(pos_saldos[lid]['bruto_ref'] or saldo_final)
        liq_ref = float(pos_saldos[lid]['liq_ref'] or saldo_final)
        nl = dict(l)
        if saldo_final <= limiar:
            nl['Bruto'] = 0.0
            nl['Líquido'] = 0.0
            nl['Saldo rem'] = 0.0
            nl['Status'] = 'exaurido_por_saque_pos_switching'
            novos_exauridos.append(nl)
            ex += 1
        else:
            ratio = (saldo_final / liq_ref) if liq_ref > 0 else 1.0
            bruto_final = _round_monetario(bruto_ref * ratio, saldo_final) if liq_ref > 0 else _round_monetario(saldo_final, 0.0)
            nl['Bruto'] = bruto_final
            nl['Líquido'] = _round_monetario(saldo_final, 0.0)
            nl['Saldo rem'] = _round_monetario(saldo_final, 0.0)
            nl['Status'] = 'ativo_pos_switching'
            novos_ativos.append(nl)
            at += 1


    ids_saida = [_norm(x.get('Lote')) for x in (novos_ativos + novos_exauridos) if _norm(x.get('Lote')) in pos_ids]
    duplic_emit = len(ids_saida) - len(set(ids_saida))

    base_aud.update({
        'qtd_pagamentos_passados_pos_detectados': int(sum(len(v) for v in consumo_por_lote.values())),
        'qtd_pagamentos_passados_pos_com_saldo_antes_preenchido': int(preench_sa),
        'qtd_pagamentos_passados_pos_com_saldo_remanescente_preenchido': int(preench_sr),
        'qtd_despesas_multifonte_pos': int(multi),
        'qtd_lotes_pos_exauridos_apos_consumo': int(ex),
        'qtd_lotes_pos_ativos_com_saldo_abatido': int(at),
        'qtd_lotes_pos_com_valoracao_previa_usada': int(uso_val_prev),
        'qtd_pagamentos_multifonte_misto_pos_nao_pos_auditados': int(qtd_multifonte_misto),
        'qtd_lotes_pos_duplicados_consolidados': int(len(lotes_pos_duplicados)),
        'qtd_pagamentos_com_fonte_repetida': int(qtd_fonte_repetida),
        'status_geral_q5c': 'valoracao_pos_preservada' if (preench_sa > 0 and preench_sr > 0) else 'integracao_parcial',
        'qtd_lotes_pos_ativos_duplicados_emitidos': int(duplic_emit),
        'status_geral_q5e': 'ativos_pos_duplicados_consolidados',
        'status_geral_q5d': 'rateio_multifonte_e_duplicidade_pos_protegidos',
        'qtd_lotes_pos_ativos_duplicados_consolidados': int(qtd_lotes_pos_ativos_duplicados_consolidados),
    })
    return extrato_passado, novos_ativos, novos_exauridos, base_aud


def _construir_origens_migradas_por_switching_auditoria(
    *,
    extrato_passado: list[dict[str, Any]],
    destinos_pos_switching_passivos: list[dict[str, Any]],
    vinculos_origem_destino_pos_switching: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    origens: dict[str, dict[str, Any]] = {}
    valores_destino_por_evento: dict[str, float] = {}

    for item in list(destinos_pos_switching_passivos or []):
        evento = str(item.get('evento_switching_id') or '').strip()
        if not evento:
            continue
        try:
            valores_destino_por_evento[evento] = float(_round_monetario(item.get('valor_liquido_origem'), 0.0) or 0.0)
        except Exception:
            valores_destino_por_evento[evento] = 0.0

    for vinc in list(vinculos_origem_destino_pos_switching or []):
        lote_origem = str(vinc.get('lote_origem') or '').strip()
        if not lote_origem:
            continue
        item = origens.setdefault(
            lote_origem,
            {
                'lote_origem': lote_origem,
                'data_switching': '',
                'status_origem': 'migrado_por_switching',
                'nao_e_ativo_comum': True,
                'nao_e_fonte_disponivel_pagamentos': True,
                'valor_liquido_migrado_total': 0.0,
                'valor_bruto_sacado_historico': 0.0,
                'valor_liquido_sacado_historico': 0.0,
                'quantidade_linhas_extrato_passado': 0,
                'destinos_vinculados': [],
            },
        )
        data_sw = str(vinc.get('data_switching') or '').strip()
        if data_sw and (not item['data_switching'] or data_sw < item['data_switching']):
            item['data_switching'] = data_sw
        evento_id = str(vinc.get('evento_switching_id') or '').strip()
        valor_liquido_vinc = vinc.get('valor_liquido_origem')
        if valor_liquido_vinc in (None, '', 'n/d'):
            valor_liquido_vinc = valores_destino_por_evento.get(evento_id, 0.0)
        item['destinos_vinculados'].append(
            {
                'evento_switching_id': evento_id,
                'lote_destino': str(vinc.get('lote_pos_switching') or vinc.get('destino_switching') or '').strip(),
                'produto_destino': str(vinc.get('produto_destino') or '').strip(),
                'data_switching': data_sw,
                'valor_liquido_origem': _round_monetario(valor_liquido_vinc, 0.0),
                'status_materializacao_passiva': str(vinc.get('status_materializacao_passiva') or '').strip(),
            }
        )

    for item in list(destinos_pos_switching_passivos or []):
        lote_origem = str(item.get('lote_origem') or '').strip()
        if not lote_origem:
            continue
        orig = origens.setdefault(
            lote_origem,
            {
                'lote_origem': lote_origem,
                'data_switching': '',
                'status_origem': 'migrado_por_switching',
                'nao_e_ativo_comum': True,
                'nao_e_fonte_disponivel_pagamentos': True,
                'valor_liquido_migrado_total': 0.0,
                'valor_bruto_sacado_historico': 0.0,
                'valor_liquido_sacado_historico': 0.0,
                'quantidade_linhas_extrato_passado': 0,
                'destinos_vinculados': [],
            },
        )
        orig['valor_liquido_migrado_total'] = _round_monetario(
            float(orig.get('valor_liquido_migrado_total') or 0.0) + float(_round_monetario(item.get('valor_liquido_origem'), 0.0) or 0.0),
            0.0,
        )
        data_sw = str(item.get('data_switching') or '').strip()
        if data_sw and (not orig['data_switching'] or data_sw < orig['data_switching']):
            orig['data_switching'] = data_sw

    for linha in list(extrato_passado or []):
        lote_raw = linha.get('Lotes usados') or linha.get('Lote') or ''
        lotes_usados = _split_fontes(lote_raw)
        if not lotes_usados:
            lotes_usados = [str(lote_raw).strip()] if str(lote_raw).strip() else []
        for lote in lotes_usados:
            if lote not in origens:
                continue
            origens[lote]['quantidade_linhas_extrato_passado'] = int(origens[lote].get('quantidade_linhas_extrato_passado') or 0) + 1
            bruto = _round_monetario(linha.get('Bruto'), 0.0)
            liquido = _round_monetario(linha.get('Líquido'), 0.0)
            origens[lote]['valor_bruto_sacado_historico'] = _round_monetario(float(origens[lote].get('valor_bruto_sacado_historico') or 0.0) + float(bruto or 0.0), 0.0)
            origens[lote]['valor_liquido_sacado_historico'] = _round_monetario(float(origens[lote].get('valor_liquido_sacado_historico') or 0.0) + float(liquido or 0.0), 0.0)

    itens = sorted(origens.values(), key=lambda x: str(x.get('lote_origem') or ''))
    reconciliacao = {
        'origens_migradas_por_switching_total': len(itens),
        'valor_liquido_migrado_total': _round_monetario(sum(float(x.get('valor_liquido_migrado_total') or 0.0) for x in itens), 0.0),
        'valor_bruto_sacado_historico_total': _round_monetario(sum(float(x.get('valor_bruto_sacado_historico') or 0.0) for x in itens), 0.0),
        'valor_liquido_sacado_historico_total': _round_monetario(sum(float(x.get('valor_liquido_sacado_historico') or 0.0) for x in itens), 0.0),
        'observacao': 'Historico sacado das origens migradas e auditavel, nao representa saldo atual disponivel nem ativo comum.',
    }
    return itens, reconciliacao



def _construir_recebidos_atuais(contexto: Any) -> list[dict[str, Any]]:
    recebidos = getattr(contexto, 'recebidos_auditaveis', None)
    quadro = getattr(recebidos, 'quadro_recebidos_auditaveis', None) if recebidos is not None else None
    if not isinstance(quadro, pd.DataFrame) or len(quadro) == 0:
        return []
    quadro = quadro.sort_values(by=['data_recebimento', 'lote_id_origem', 'recebido_id'], kind='stable').reset_index(drop=True)
    linhas = []
    for _, row in quadro.iterrows():
        linhas.append({
            'Recebido': row.get('recebido_id'),
            'Lote origem': row.get('lote_id_origem'),
            'Recebimento': _fmt_data(row.get('data_recebimento')),
            'Aplicação': _fmt_data(row.get('data_aplicacao')),
            'Valor bruto': _round_monetario(row.get('valor_bruto'), 0.0),
            'Valor líquido': _round_monetario(row.get('valor_liquido'), 0.0),
            'Status': row.get('status_recebido'),
            'Destino': row.get('destino_potencial'),
            'Pagamentos vinculados': int(row.get('qtd_pagamentos_vinculados') or 0),
            'Valor vinculado': _round_monetario(row.get('valor_total_vinculado'), 0.0),
            'Residual aplicação': _round_monetario(row.get('valor_residual_para_aplicacao_origem'), 0.0),
            'Disponível ref': 'sim' if bool(row.get('disponivel_na_data_referencia', False)) else 'não',
            'Observação': row.get('observacao_auditavel') or '',
        })
    return linhas


def _linhas_fechamento_atual(contexto: Any) -> list[dict[str, Any]]:
    resumo = resumir_fechamento_situacao_atual(data_referencia=contexto.execucao.data_referencia, calendario_financeiro=contexto.calendario_financeiro, serie_cdi=contexto.cache_cdi.serie_cdi)
    return [
        {'Métrica': 'Data de referência', 'Valor': resumo.get('data_referencia')},
        {'Métrica': 'Status do fechamento econômico', 'Valor': resumo.get('status_fechamento')},
        {'Métrica': 'Fonte do fechamento', 'Valor': resumo.get('fonte_fechamento')},
        {'Métrica': 'Fechamentos com fallback CDI', 'Valor': resumo.get('qtd_fechamentos_fallback_cdi', 0)},
        {'Métrica': 'Último fator explícito CDI', 'Valor': resumo.get('data_ultimo_fator_explicito_cdi')},
        {'Métrica': 'Data confirmada da série', 'Valor': resumo.get('data_fechamento_confirmado')},
        {'Métrica': 'Leitura auditável', 'Valor': resumo.get('observacao')},
    ]


def _linhas_resumo_recebidos(contexto: Any) -> list[dict[str, Any]]:
    resumo = getattr(getattr(contexto, 'recebidos_auditaveis', None), 'auditoria', {}).get('resumo', {}) if getattr(contexto, 'recebidos_auditaveis', None) is not None else {}
    return [
        {'Métrica': 'Total de recebidos', 'Valor': resumo.get('total_recebidos', 0)},
        {'Métrica': 'Valor total bruto', 'Valor': resumo.get('valor_total_bruto', 0.0)},
        {'Métrica': 'Status recebido', 'Valor': str(resumo.get('status_recebido', {}))},
        {'Métrica': 'Destino potencial', 'Valor': str(resumo.get('destino_potencial', {}))},
        {'Métrica': 'Recebidos com pagamento vinculado', 'Valor': resumo.get('recebidos_com_pagamento_vinculado', 0)},
        {'Métrica': 'Recebidos em janela pré-aplicação', 'Valor': resumo.get('recebidos_em_janela_pre_aplicacao', 0)},
        {'Métrica': 'Recebidos usados antes da aplicação', 'Valor': resumo.get('recebidos_usados_antes_da_aplicacao_observado', 0)},
    ]


def _pos_canonico_ativo(contexto: Any) -> bool:
    """Detecta se POS pos-switching ja nasce no inventario_canonico."""
    dados_ops = getattr(contexto, 'dados_operacionais', None)
    inventario = getattr(dados_ops, 'inventario_canonico', None) if dados_ops is not None else None
    if not isinstance(inventario, pd.DataFrame) or len(inventario) == 0:
        return False
    if 'origem_registro' not in inventario.columns:
        return False
    origem = inventario['origem_registro'].fillna('').astype(str).str.strip().str.lower()
    return bool(origem.eq('lote_pos_switching_normalizado').any())


def _valor_monetario_situacao(linha: dict[str, Any]) -> float:
    """Extrai valor monetario de uma linha observavel da Situacao Atual."""
    for chave in ('Patr. líq.', 'Patrimônio líquido', 'Líq. atual', 'Líquido'):
        valor = linha.get(chave) if isinstance(linha, dict) else None
        try:
            if valor in (None, '', 'n/d'):
                continue
            return round(float(valor), 2)
        except Exception:
            continue
    return 0.0


def _neutralizar_origens_migradas_situacao(
    lotes_ativos: list[dict[str, Any]],
    lotes_exauridos: list[dict[str, Any]],
    origens_migradas_por_switching: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Remove da camada ativa origens ja migradas por switching.

    A neutralizacao e observavel: preserva auditoria, historico e destinos POS,
    mas impede que a origem migrada continue contribuindo como ativo comum.
    """
    origens_norm: dict[str, dict[str, Any]] = {}
    for item in origens_migradas_por_switching or []:
        lote = str(item.get('lote_origem') or '').strip()
        if lote:
            origens_norm[_norm(lote)] = item

    if not origens_norm:
        return lotes_ativos, lotes_exauridos, {
            'origens_migradas_neutralizadas_situacao_total': 0,
            'origens_migradas_neutralizadas_situacao': [],
            'patrimonio_liquido_ativo_neutralizado_origens_migradas': 0.0,
            'origens_migradas_ativas_remanescentes_total': 0,
            'origens_migradas_ativas_remanescentes': [],
        }

    exauridos_norm = {
        _norm(x.get('Lote'))
        for x in lotes_exauridos
        if isinstance(x, dict) and _norm(x.get('Lote'))
    }

    novos_ativos: list[dict[str, Any]] = []
    novos_exauridos: list[dict[str, Any]] = list(lotes_exauridos)
    neutralizadas: list[dict[str, Any]] = []
    patrimonio_neutralizado = 0.0

    for linha in lotes_ativos:
        lote_norm = _norm(linha.get('Lote')) if isinstance(linha, dict) else ''
        if lote_norm not in origens_norm:
            novos_ativos.append(linha)
            continue

        info_origem = origens_norm.get(lote_norm, {})
        patrimonio = _valor_monetario_situacao(linha)
        patrimonio_neutralizado = round(patrimonio_neutralizado + patrimonio, 2)

        status_anterior = linha.get('Status ciclo') or linha.get('Status') or 'ativo'
        lote_origem = linha.get('Lote') or info_origem.get('lote_origem')

        neutralizadas.append({
            'lote_origem': lote_origem,
            'status_anterior': status_anterior,
            'status_final': 'migrado_por_switching',
            'patrimonio_liquido_ativo_removido': patrimonio,
            'motivo': 'origem_migrada_por_switching_nao_deve_permanecer_ativa',
            'destinos_vinculados': info_origem.get('destinos_vinculados'),
        })

        if lote_norm not in exauridos_norm:
            linha_exaurida = dict(linha)
            linha_exaurida['Status ciclo'] = 'migrado_por_switching'
            linha_exaurida['Status'] = 'migrado_por_switching'
            linha_exaurida['Bruto atual'] = 0.0
            linha_exaurida['Líq. atual'] = 0.0
            linha_exaurida['Líquido'] = 0.0
            linha_exaurida['Saldo rem'] = 0.0
            linha_exaurida['Origem migrada'] = 'sim'
            linha_exaurida['Status materialização'] = 'origem_neutralizada_v36f'
            novos_exauridos.append(linha_exaurida)
            exauridos_norm.add(lote_norm)

    remanescentes: list[dict[str, Any]] = []
    for linha in novos_ativos:
        lote_norm = _norm(linha.get('Lote')) if isinstance(linha, dict) else ''
        if lote_norm in origens_norm:
            remanescentes.append({
                'lote_origem': linha.get('Lote'),
                'status_ativo': linha.get('Status ciclo') or linha.get('Status'),
                'patrimonio_liquido_ativo': _valor_monetario_situacao(linha),
            })

    auditoria_neutralizacao = {
        'origens_migradas_neutralizadas_situacao_total': len(neutralizadas),
        'origens_migradas_neutralizadas_situacao': neutralizadas,
        'patrimonio_liquido_ativo_neutralizado_origens_migradas': round(patrimonio_neutralizado, 2),
        'origens_migradas_ativas_remanescentes_total': len(remanescentes),
        'origens_migradas_ativas_remanescentes': remanescentes,
    }

    return novos_ativos, novos_exauridos, auditoria_neutralizacao


def construir_saida_canonica(
    contexto: Any,
    *,
    versao: str = 'V203',
    incluir_temporal_shadow: bool = False,
) -> PacoteSaidaCanonica:
    extrato_passado = _construir_extrato_passado(contexto)
    extrato_futuro = _construir_extrato_futuro(contexto)
    extrato_futuro = [
        _normalizar_sem_fonte_valida_extrato_futuro(item)
        for item in extrato_futuro
    ]
    switchings = _construir_switchings(contexto)
    ranking_amostra = _construir_ranking_amostra(contexto)
    quadro_futuro = _quadro_futuro_preferencial(contexto)
    mapa_central = _mapa_pagamentos_central(contexto)
    ledger_result = construir_ledger_temporal_conjunto(quadro_futuro, mapa_central, contexto) or {}
    destinos_pos_switching_passivos = list(ledger_result.get('destinos_pos_switching_materializados_passivos', []))
    pos_canonico_ativo = _pos_canonico_ativo(contexto)
    destinos_pos_switching_passivos_para_situacao = (
        [] if pos_canonico_ativo else destinos_pos_switching_passivos
    )
    vinculos_origem_destino_pos_switching = list(ledger_result.get('vinculos_origem_destino_pos_switching', []))
    lotes_ativos, lotes_exauridos = _construir_lotes_situacao(
        contexto,
        destinos_pos_switching_passivos_para_situacao,
    )
    extrato_passado, lotes_ativos, lotes_exauridos, auditoria_consumo_pos_q5b = _aplicar_consumo_pagamentos_passados_lotes_pos_switching(
        contexto,
        extrato_passado,
        lotes_ativos,
        lotes_exauridos,
    )
    origens_migradas_por_switching, reconciliacao_origens_migradas = _construir_origens_migradas_por_switching_auditoria(
        extrato_passado=extrato_passado,
        destinos_pos_switching_passivos=destinos_pos_switching_passivos,
        vinculos_origem_destino_pos_switching=vinculos_origem_destino_pos_switching,
    )
    lotes_ativos, lotes_exauridos, auditoria_neutralizacao_origens_migradas = _neutralizar_origens_migradas_situacao(
        lotes_ativos,
        lotes_exauridos,
        origens_migradas_por_switching,
    )
    recebidos_atuais = _construir_recebidos_atuais(contexto)
    eventos_ledger = list(ledger_result.get('eventos', []))
    fifo_candidatos_avaliados = list(ledger_result.get('fifo_candidatos_avaliados', []))
    auditoria = {
        'origem': 'nucleo.saida_canonica.construir_saida_canonica',
        'camada_unica_saida': True,
        'qtd_extrato_passado': len(extrato_passado),
        'qtd_extrato_futuro': len(extrato_futuro),
        'qtd_switchings': len(switchings),
        'qtd_lotes_ativos': len(lotes_ativos),
        'qtd_lotes_exauridos': len(lotes_exauridos),
        'auditoria_consumo_pos_q5b': auditoria_consumo_pos_q5b,
        'qtd_futuro_sem_cobertura_integral': sum(1 for item in extrato_futuro if item.get('Cobertura integral') != 'sim'),
        'qtd_futuro_multifonte': sum(1 for item in extrato_futuro if '+' in str(item.get('Lote sugerido') or '')),
        'fifo_candidatos_avaliados': fifo_candidatos_avaliados,
        'qtd_eventos_ledger': len(eventos_ledger),
        'pos_canonico_ativo': bool(pos_canonico_ativo),
        'ponte_passiva_pos_desativada_por_pos_canonico': bool(pos_canonico_ativo and len(destinos_pos_switching_passivos) > 0),
        'destinos_pos_switching_passivos_para_situacao_total': len(destinos_pos_switching_passivos_para_situacao),
        'destinos_pos_switching_passivos_preservados_auditoria_total': len(destinos_pos_switching_passivos),
        **({k: v for k, v in ledger_result.items() if (str(k).startswith('pay_only_diario_shadow_') or str(k).startswith('d2a_') or str(k).startswith('d2a2_') or str(k).startswith('d2b0_') or str(k).startswith('d2b1_') or str(k).startswith('d2c_') or str(k).startswith('d3_') or str(k).startswith('d3b_') or str(k).startswith('d3c_') or str(k).startswith('d3d_') or str(k).startswith('d3e_') or str(k).startswith('d3f_') or str(k).startswith('d31_') or str(k).startswith('d31b_') or str(k).startswith('d31c_') or str(k).startswith('d31d_') or str(k).startswith('d31e_') or str(k).startswith('d31f_') or str(k).startswith('d32a_') or str(k).startswith('saldo_temporal_') or str(k).startswith('comparativo_') or str(k).startswith('recebidos_') or str(k).startswith('recebidos_shadow_') or str(k).startswith('shadow_recebidos_') or str(k).startswith('valor_recebidos_') or str(k).startswith('alocacao_') or str(k).startswith('pagamentos_rebaixados_') or str(k).startswith('pagamentos_') or str(k).startswith('extrato_futuro_') or str(k).startswith('divergencias_') or str(k).startswith('pre_invariante_') or str(k).startswith('sombra_')) and not isinstance(v, (list, dict, tuple, set))}),
        'pay_only_diario_shadow_por_data': ledger_result.get('pay_only_diario_shadow_por_data', []),
        'plano_pay_only_diario_v1_por_pagamento': ledger_result.get('plano_pay_only_diario_v1_por_pagamento', []),
        'd2a_plano_por_data': ledger_result.get('d2a_plano_por_data', []),
        'plano_pay_only_diario_v1_combinacao_minima_por_pagamento_fonte': ledger_result.get('plano_pay_only_diario_v1_combinacao_minima_por_pagamento_fonte', []),
        'd2b0_plano_por_data': ledger_result.get('d2b0_plano_por_data', []),
        'd2c_residuais_detalhe': ledger_result.get('d2c_residuais_detalhe', []),
        'd3_residuais_detalhe': ledger_result.get('d3_residuais_detalhe', []),
        'd3_datas_residuais_detalhe': ledger_result.get('d3_datas_residuais_detalhe', []),
        'd3b_lotes_detalhe': ledger_result.get('d3b_lotes_detalhe', []),
        'd3c_fontes_saneadas': ledger_result.get('d3c_fontes_saneadas', []),
        'd3d_fontes_saneadas': ledger_result.get('d3d_fontes_saneadas', []),
        'd3e_fontes_saneadas': ledger_result.get('d3e_fontes_saneadas', []),
        'd3e_pacotes_por_data': ledger_result.get('d3e_pacotes_por_data', []),
        'd3f_fontes_saneadas': ledger_result.get('d3f_fontes_saneadas', []),
        'd31_cenarios_por_data': ledger_result.get('d31_cenarios_por_data', []),
        'd31b_cenarios_por_data': ledger_result.get('d31b_cenarios_por_data', []),
        'd31c_cenarios_por_data': ledger_result.get('d31c_cenarios_por_data', []),
        'd31d_cenarios_detalhe': ledger_result.get('d31d_cenarios_detalhe', []),
        'd31e_bases_por_cenario': ledger_result.get('d31e_bases_por_cenario', []),
        'd31f_bases_reclassificadas': ledger_result.get('d31f_bases_reclassificadas', []),
        'd32a_plano_por_data': ledger_result.get('d32a_plano_por_data', []),
        'saldo_temporal_auditoria_lotes': ledger_result.get('saldo_temporal_auditoria_lotes', []),
        'saldo_temporal_pagamentos_rebaixados_detalhe': ledger_result.get('saldo_temporal_pagamentos_rebaixados_detalhe', []),
        'pagamentos_rebaixados_shadow_detalhe': ledger_result.get('pagamentos_rebaixados_shadow_detalhe', []),
        'shadow_recebidos_resumo_fontes': ledger_result.get('shadow_recebidos_resumo_fontes', []),
        'shadow_pagamentos_recuperados_nominal': ledger_result.get('shadow_pagamentos_recuperados_nominal', []),
        'recebidos_futuros_auditoria': ledger_result.get('recebidos_futuros_auditoria', []),
        'alocacao_fontes_auditoria': ledger_result.get('alocacao_fontes_auditoria', []),
        'saldo_temporal_lote_8500_trilha_eventos': ledger_result.get('saldo_temporal_lote_8500_trilha_eventos', []),
        'comparativo_mapa_funcoes_legadas': ledger_result.get('comparativo_mapa_funcoes_legadas', []),
        'destinos_pos_switching_materializados_passivos': destinos_pos_switching_passivos,
        'destinos_pos_switching_materializados_passivos_total': int(ledger_result.get('destinos_pos_switching_materializados_passivos_total', len(destinos_pos_switching_passivos))),
        'vinculos_origem_destino_pos_switching': vinculos_origem_destino_pos_switching,
        'vinculos_origem_destino_pos_switching_total': int(ledger_result.get('vinculos_origem_destino_pos_switching_total', len(vinculos_origem_destino_pos_switching))),
        'origens_migradas_por_switching': origens_migradas_por_switching,
        'origens_migradas_por_switching_total': len(origens_migradas_por_switching),
        'reconciliacao_patrimonial_origens_migradas': reconciliacao_origens_migradas,
        **auditoria_neutralizacao_origens_migradas,
        **(_PRE_INVARIANTE_EXTRATO_FUTURO or {}),
        **(_SOMBRA_DIVERGENCIAS_LEDGER or {}),
    }
    pacote = PacoteSaidaCanonica(
        versao=versao,
        data_referencia=_fmt_data(contexto.execucao.data_referencia),
        extrato_passado=extrato_passado,
        extrato_futuro=extrato_futuro,
        switchings=switchings,
        ranking_amostra=ranking_amostra,
        lotes_ativos=lotes_ativos,
        lotes_exauridos=lotes_exauridos,
        recebidos_atuais=recebidos_atuais,
        fechamento_atual=_linhas_fechamento_atual(contexto),
        resumo_recebidos=_linhas_resumo_recebidos(contexto),
        auditoria=auditoria,
    )

    if incluir_temporal_shadow:
        from dataclasses import replace

        from nucleo.saida_canonica_temporal_shadow_v4k import (
            CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K,
            construir_bloco_temporal_shadow_v4k,
        )

        auditoria_shadow = dict(pacote.auditoria or {})
        auditoria_shadow[CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K] = construir_bloco_temporal_shadow_v4k(
            contexto=contexto,
            saida_base=pacote,
        )
        return replace(pacote, auditoria=auditoria_shadow)

    return pacote
