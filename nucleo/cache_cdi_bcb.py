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

from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.utilitarios_neutros import para_data, para_float_monetario


@dataclass(slots=True)
class PacoteCacheCDIDiario:
    serie_cdi: dict[date, float]
    data_inicial_consulta: date
    data_final_consulta: date
    caminho_cache: Path
    auditoria: dict[str, Any]
    validacao: dict[str, Any]


def _cfg_get(config: Mapping[str, Any], *caminho: str, padrao: Any = None) -> Any:
    atual: Any = config
    for chave in caminho:
        if not isinstance(atual, Mapping) or chave not in atual:
            return padrao
        atual = atual[chave]
    return atual


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
    # O retorno diário do SGS deve ser tratado diretamente como taxa diária em %.
    taxa_decimal = taxa / 100.0
    fator = 1.0 + taxa_decimal
    return float(fator)


def _ler_cache(caminho_cache: Path, convencao_dias_ano: int) -> dict[date, float]:
    if not caminho_cache.exists():
        return {}
    try:
        dados = json.loads(caminho_cache.read_text(encoding='utf-8'))
    except Exception:
        return {}
    serie: dict[date, float] = {}

    # Formato legado/fornecido pelo usuário:
    # {"mapa": {"YYYY-MM-DD": 1.0005...}, "taxa_projecao": ..., "data_atualizacao": ...}
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

    registros = dados.get('registros', dados if isinstance(dados, list) else [])
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
) -> PacoteCacheCDIDiario:
    data_ini, data_fim = _datas_relevantes(dados_operacionais, data_referencia)
    caminho_cache = raiz_repositorio / str(_cfg_get(config, 'arquivos', 'cache_bcb', padrao='cache_bcb.json'))
    convencao = int(_cfg_get(config, 'execucao', 'convencao_dias_ano', 'cdi', padrao=252) or 252)

    serie = _ler_cache(caminho_cache, convencao)
    if serie:
        serie = {dt: fator for dt, fator in serie.items() if data_ini <= dt <= data_fim}
        serie = dict(sorted(serie.items(), key=lambda kv: kv[0]))
    fonte = 'cache_local' if serie else 'sem_cache'
    fetch_status = None
    if not serie or min(serie.keys(), default=data_ini) > data_ini or max(serie.keys(), default=data_ini) < data_fim:
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
                    'data_atualizacao': datetime.now().date().isoformat(),
                })
            except Exception:
                pass
        else:
            fetch_status = erro or 'sem_dados'
    auditoria = {
        'data_inicial_consulta': data_ini,
        'data_final_consulta': data_fim,
        'fonte_serie_cdi': fonte,
        'fetch_status': fetch_status,
        'qtd_datas_serie_cdi': len(serie),
        'caminho_cache': str(caminho_cache),
    }
    avisos = []
    if not serie:
        avisos.append('serie_cdi_bcb_indisponivel_usando_taxa_modelo')
    validacao = {'ok': True, 'erros': [], 'avisos': avisos}
    return PacoteCacheCDIDiario(serie, data_ini, data_fim, caminho_cache, auditoria, validacao)
