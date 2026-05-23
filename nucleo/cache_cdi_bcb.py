"""Cache diário de CDI do BCB para auditoria e replay.

Esta camada cria um cache local do CDI diário a partir da janela necessária
para a baseline atual. Quando a rede não está disponível, ela falha de forma
controlada e permite fallback para a taxa de modelo do calendário.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping, Optional
import json

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

from nucleo.config_utils import obter_config as _cfg_get
from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.entrada_resolvida import JanelaConsultaCDI
from nucleo.utilitarios_neutros import para_data, para_float_monetario


@dataclass(slots=True)
class PacoteCacheCDIDiario:
    serie_cdi: dict[date, float]
    data_inicial_consulta: date
    data_final_consulta: date
    caminho_cache: Path
    auditoria: dict[str, Any]
    validacao: dict[str, Any]


def _primeiro_dia_do_mes(dt: date) -> date:
    return dt.replace(day=1)


def _datas_relevantes(dados_operacionais: PacoteDadosOperacionaisCanonicos, data_referencia: date) -> tuple[date, date]:
    datas: list[date] = []
    try:
        invent = dados_operacionais.inventario_canonico
        if len(invent):
            datas.extend([d for d in invent['data_aplicacao'].dropna().tolist() if isinstance(d, date)])
    except Exception:
        pass
    try:
        gastos = dados_operacionais.gastos_canonicos
        if len(gastos):
            datas.extend([d for d in gastos['data'].dropna().tolist() if isinstance(d, date)])
    except Exception:
        pass
    data_min = min(datas) if datas else data_referencia
    return _primeiro_dia_do_mes(data_min), data_referencia


def _janela_cdi_contem_apenas_data_referencia(
    janela_consulta_cdi: JanelaConsultaCDI,
    data_referencia: date,
) -> bool:
    """Identifica janela estrutural que não acrescenta datas operacionais.

    Durante a transição V4Z, a Etapa 1 pode produzir uma JanelaConsultaCDI
    contendo apenas a data de referência. Essa janela é válida como evidência
    estrutural, mas não deve estreitar o cache CDI operacional em relação ao
    comportamento legado enquanto o runtime principal ainda usa
    ContextoBaseline.
    """

    data_inicial = janela_consulta_cdi.data_inicial_consulta
    data_final = janela_consulta_cdi.data_final_consulta
    if data_inicial != data_referencia or data_final != data_referencia:
        return False
    metadados = janela_consulta_cdi.metadados if isinstance(janela_consulta_cdi.metadados, Mapping) else {}
    fontes_datas = metadados.get('fontes_datas') if isinstance(metadados.get('fontes_datas'), Mapping) else {}
    fontes_reais = {str(chave) for chave in fontes_datas.keys() if str(chave) != 'data_referencia'}
    qtd_datas = metadados.get('qtd_datas_identificadas')
    try:
        qtd_datas_int = int(qtd_datas)
    except Exception:
        qtd_datas_int = None
    return not fontes_reais and qtd_datas_int in (None, 1)


def _datas_relevantes_por_janela_cdi(
    janela_consulta_cdi: Optional[JanelaConsultaCDI],
    data_referencia: date,
) -> Optional[tuple[date, date]]:
    """Resolve datas do cache a partir da JanelaConsultaCDI da Etapa 1.

    Esta função não consulta BCB, não lê cache e não calcula rendimento. Ela
    apenas traduz a janela estrutural da entrada resolvida para a janela usada
    pelo cache, quando a janela está completa.
    """

    if janela_consulta_cdi is None:
        return None
    data_inicial = janela_consulta_cdi.data_inicial_consulta
    data_final = janela_consulta_cdi.data_final_consulta
    if data_inicial is None or data_final is None:
        return None
    if not isinstance(data_inicial, date) or not isinstance(data_final, date):
        return None
    if _janela_cdi_contem_apenas_data_referencia(janela_consulta_cdi, data_referencia):
        return None
    data_ini = _primeiro_dia_do_mes(data_inicial)
    data_fim = max(data_final, data_referencia)
    if data_fim < data_ini:
        return None
    return data_ini, data_fim


def _parse_data_bcb_estrita(valor: Any) -> Optional[date]:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    texto = str(valor).strip()
    if not texto:
        return None
    try:
        return datetime.strptime(texto, '%d/%m/%Y').date()
    except Exception:
        pass
    return para_data(texto)


def _converter_taxa_bcb_para_fator(valor: Any, convencao_dias_ano: int) -> Optional[float]:
    taxa = float(para_float_monetario(valor, 0.0) or 0.0)
    if taxa <= 0.0:
        return None
    taxa_decimal = taxa / 100.0
    fator = 1.0 + taxa_decimal
    return float(fator)


def _extrair_data_atualizacao_cache(dados: Any) -> Optional[date]:
    if not isinstance(dados, Mapping):
        return None
    meta = dados.get('meta') if isinstance(dados.get('meta'), Mapping) else {}
    for chave in ('data_atualizacao', 'data_final', 'data_final_consulta'):
        valor = dados.get(chave) or meta.get(chave)
        dt = para_data(valor)
        if dt is not None:
            return dt
    return None


def _ler_payload_cache(caminho_cache: Path) -> Any:
    if not caminho_cache.exists():
        return None
    try:
        return json.loads(caminho_cache.read_text(encoding='utf-8'))
    except Exception:
        return None


def _cache_atualizado_para_referencia(payload: Any, data_referencia: date) -> bool:
    data_atualizacao = _extrair_data_atualizacao_cache(payload)
    return data_atualizacao is not None and data_atualizacao >= data_referencia


def _ler_cache(caminho_cache: Path, convencao_dias_ano: int, payload: Any | None = None) -> dict[date, float]:
    dados = _ler_payload_cache(caminho_cache) if payload is None else payload
    if dados is None:
        return {}
    serie: dict[date, float] = {}

    if isinstance(dados, Mapping) and isinstance(dados.get('mapa'), Mapping):
        for chave, valor in dados.get('mapa', {}).items():
            dt = para_data(chave)
            try:
                fator = float(valor)
            except Exception:
                continue
            if dt is not None and fator > 1.0:
                serie[dt] = fator
        return dict(sorted(serie.items(), key=lambda kv: kv[0]))

    registros = dados.get('registros', dados if isinstance(dados, list) else []) if isinstance(dados, Mapping) else dados
    if not isinstance(registros, list):
        return {}
    for item in registros:
        if not isinstance(item, Mapping):
            continue
        dt = _parse_data_bcb_estrita(item.get('data') or item.get('Data'))
        fator = item.get('fator_dia')
        if dt is None:
            continue
        if fator is None:
            fator = _converter_taxa_bcb_para_fator(item.get('valor') or item.get('Valor'), convencao_dias_ano)
        try:
            fator = float(fator)
        except Exception:
            continue
        if fator > 1.0:
            serie[dt] = fator
    return dict(sorted(serie.items(), key=lambda kv: kv[0]))


def _salvar_cache(caminho_cache: Path, serie: dict[date, float], meta: Mapping[str, Any]) -> None:
    payload = {
        'mapa': {d.isoformat(): float(f) for d, f in sorted(serie.items(), key=lambda kv: kv[0])},
        'taxa_projecao': float(meta.get('taxa_projecao', 0.0) or 0.0),
        'data_atualizacao': str(meta.get('data_atualizacao') or datetime.now().date().isoformat()),
        'meta': dict(meta),
        'registros': [
            {'data': d.isoformat(), 'fator_dia': float(f)}
            for d, f in sorted(serie.items(), key=lambda kv: kv[0])
        ],
    }
    caminho_cache.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def _buscar_bcb(config: Mapping[str, Any], data_inicial: date, data_final: date, convencao_dias_ano: int) -> tuple[dict[date, float], Optional[str]]:
    if requests is None:
        return {}, 'requests_indisponivel'
    url_base = _cfg_get(config, 'urls', 'bcb_sgs_12_url', padrao='')
    if not url_base:
        return {}, 'url_bcb_ausente'
    url = str(url_base).format(
        data_inicial=data_inicial.strftime('%d/%m/%Y'),
        data_final=data_final.strftime('%d/%m/%Y'),
    )
    timeout = int(_cfg_get(config, 'rede', 'timeout_bcb_segundos', padrao=10) or 10)
    verify = bool(_cfg_get(config, 'rede', 'verificar_ssl', padrao=False))
    headers = {
        'User-Agent': str(_cfg_get(config, 'rede', 'user_agent_bcb', padrao='Mozilla/5.0')),
        'Accept': str(_cfg_get(config, 'rede', 'accept_bcb', padrao='application/json')),
    }
    try:
        resp = requests.get(url, timeout=timeout, verify=verify, headers=headers)
        resp.raise_for_status()
        dados = resp.json()
    except Exception as exc:  # pragma: no cover
        return {}, f'falha_fetch_bcb:{exc.__class__.__name__}'
    serie: dict[date, float] = {}
    if not isinstance(dados, list):
        return {}, 'resposta_bcb_invalida'
    for item in dados:
        if not isinstance(item, Mapping):
            continue
        dt = _parse_data_bcb_estrita(item.get('data') or item.get('Data'))
        fator = _converter_taxa_bcb_para_fator(item.get('valor') or item.get('Valor'), convencao_dias_ano)
        if dt is None or fator is None or fator <= 1.0:
            continue
        if not (data_inicial <= dt <= data_final):
            continue
        serie[dt] = fator
    return dict(sorted(serie.items(), key=lambda kv: kv[0])), None


def carregar_cache_cdi_diario(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
    raiz_repositorio: Path,
    janela_consulta_cdi: Optional[JanelaConsultaCDI] = None,
) -> PacoteCacheCDIDiario:
    janela_resolvida = _datas_relevantes_por_janela_cdi(janela_consulta_cdi, data_referencia)
    if janela_resolvida is not None:
        data_ini, data_fim = janela_resolvida
        origem_janela_consulta = 'janela_consulta_cdi'
    else:
        data_ini, data_fim = _datas_relevantes(dados_operacionais, data_referencia)
        origem_janela_consulta = 'dados_operacionais_legado'

    caminho_cache = raiz_repositorio / str(_cfg_get(config, 'arquivos', 'cache_bcb', padrao='cache_bcb.json'))
    convencao = int(_cfg_get(config, 'execucao', 'convencao_dias_ano', 'cdi', padrao=252) or 252)

    payload_cache = _ler_payload_cache(caminho_cache)
    cache_atualizado = _cache_atualizado_para_referencia(payload_cache, data_referencia)
    data_atualizacao_cache = _extrair_data_atualizacao_cache(payload_cache)
    serie = _ler_cache(caminho_cache, convencao, payload=payload_cache)
    if serie:
        serie = {dt: fator for dt, fator in serie.items() if data_ini <= dt <= data_fim}
        serie = dict(sorted(serie.items(), key=lambda kv: kv[0]))
    fonte = 'cache_local' if serie else 'sem_cache'
    fetch_status = 'cache_atualizado_sem_fetch' if cache_atualizado and serie else None

    precisa_buscar = not (cache_atualizado and serie)
    if precisa_buscar:
        serie_fetch, erro = _buscar_bcb(config, data_ini, data_fim, convencao)
        if serie_fetch:
            serie = serie_fetch
            fonte = 'bcb_online'
            fetch_status = 'ok'
            try:
                _salvar_cache(caminho_cache, serie, {
                    'fonte': fonte,
                    'data_inicial': data_ini.isoformat(),
                    'data_final': data_fim.isoformat(),
                    'taxa_projecao': _cfg_get(config, 'premissas_mercado', 'cdi_diario_projecao', padrao=0.0),
                    'data_atualizacao': data_referencia.isoformat(),
                    'origem_janela_consulta': origem_janela_consulta,
                })
                data_atualizacao_cache = data_referencia
                cache_atualizado = True
            except Exception:
                pass
        else:
            fetch_status = erro or 'sem_dados'
    auditoria = {
        'data_inicial_consulta': data_ini,
        'data_final_consulta': data_fim,
        'origem_janela_consulta': origem_janela_consulta,
        'janela_consulta_cdi_informada': janela_consulta_cdi is not None,
        'fonte_serie_cdi': fonte,
        'fetch_status': fetch_status,
        'qtd_datas_serie_cdi': len(serie),
        'ultima_data_serie_cdi': max(serie.keys()).isoformat() if serie else None,
        'data_atualizacao_cache': data_atualizacao_cache.isoformat() if hasattr(data_atualizacao_cache, 'isoformat') else data_atualizacao_cache,
        'cache_atualizado_para_referencia': bool(cache_atualizado and serie),
        'caminho_cache': str(caminho_cache),
    }
    avisos = []
    if not serie:
        avisos.append('serie_cdi_bcb_indisponivel_usando_taxa_modelo')
    validacao = {'ok': True, 'erros': [], 'avisos': avisos}
    return PacoteCacheCDIDiario(serie, data_ini, data_fim, caminho_cache, auditoria, validacao)
