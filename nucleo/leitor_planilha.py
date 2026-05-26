"""Leitura e canonização inicial da planilha base do projeto.

Este módulo permanece propositalmente restrito à leitura estrutural e à
canonização inicial das colunas. Ele não cria ainda entidades finais nem
implementa derivação financeira profunda.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import tempfile
from typing import Any, Iterable, Mapping, Optional

import pandas as pd

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

from nucleo.config_utils import obter_config as _cfg_get
from nucleo.entrada_resolvida import JanelaConsultaCDI, MapaAbasResolvidas, MapaColunasResolvidas
from nucleo.utilitarios_neutros import normalizar_texto


@dataclass(slots=True)
class PacotePlanilha:
    caminho: Path
    nomes_abas: list[str]
    quadros_brutos: dict[str, pd.DataFrame]
    quadros_canonicos: dict[str, pd.DataFrame]
    auditoria: dict[str, Any]
    validacao: dict[str, Any]
    mapa_abas_resolvidas: Optional[MapaAbasResolvidas] = None
    mapa_colunas_resolvidas: Optional[MapaColunasResolvidas] = None
    quadros_estruturais_resolvidos: Optional[dict[str, pd.DataFrame]] = None
    janela_consulta_cdi: Optional[JanelaConsultaCDI] = None


def _montar_url_download_planilha(config: Mapping[str, Any]) -> Optional[str]:
    url_direta = str(_cfg_get(config, 'urls', 'planilha_financeira_url', padrao='') or '').strip()
    if url_direta:
        return url_direta
    file_id = str(_cfg_get(config, 'google_drive', 'sheets_file_id', padrao='') or '').strip()
    if not file_id:
        return None
    base = str(_cfg_get(config, 'urls', 'google_sheets_export_base', padrao='') or '').strip()
    if not base:
        return None
    try:
        return base.format(file_id=file_id)
    except Exception:
        return None


def _tentar_baixar_planilha(config: Mapping[str, Any], destino: Path) -> tuple[bool, Optional[str]]:
    if requests is None:
        return False, 'requests_indisponivel'
    url = _montar_url_download_planilha(config)
    if not url:
        return False, 'url_planilha_ausente'
    timeout = int(_cfg_get(config, 'rede', 'timeout_download_segundos', padrao=30) or 30)
    verify = bool(_cfg_get(config, 'rede', 'verificar_ssl', padrao=False))
    headers = {
        'User-Agent': str(_cfg_get(config, 'rede', 'user_agent_download_planilha', padrao='Mozilla/5.0')),
    }
    try:
        resp = requests.get(url, timeout=timeout, verify=verify, headers=headers)
        resp.raise_for_status()
        conteudo = resp.content
        if not conteudo:
            return False, 'download_vazio'
        destino.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx', dir=str(destino.parent)) as tmp:
            tmp.write(conteudo)
            tmp_path = Path(tmp.name)
        # valida minimamente o arquivo antes de sobrescrever a planilha local
        try:
            with pd.ExcelFile(tmp_path) as excel_tmp:
                _ = excel_tmp.sheet_names
        except Exception:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
            return False, 'arquivo_baixado_invalido'
        try:
            tmp_path.replace(destino)
        except PermissionError as exc_perm:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
            detalhe_perm = str(exc_perm).strip().replace('\n', ' ').replace('\r', ' ')
            if detalhe_perm:
                return False, f"falha_download_planilha:PermissionError:destino_bloqueado_ou_em_uso:{detalhe_perm}"
            return False, 'falha_download_planilha:PermissionError:destino_bloqueado_ou_em_uso'
        return True, None
    except Exception as exc:  # pragma: no cover
        detalhe = str(exc).strip().replace('\n', ' ').replace('\r', ' ')
        if detalhe:
            return False, f'falha_download_planilha:{exc.__class__.__name__}:{detalhe}'
        return False, f'falha_download_planilha:{exc.__class__.__name__}'


def construir_mapa_alias(mapa_alias: Mapping[str, Iterable[str]]) -> dict[str, str]:
    mapa: dict[str, str] = {}
    for nome_canonico, aliases in mapa_alias.items():
        mapa[normalizar_texto(nome_canonico)] = nome_canonico
        for alias in aliases:
            mapa[normalizar_texto(alias)] = nome_canonico
    return mapa


def canonizar_colunas(
    quadro: pd.DataFrame,
    mapa_alias: Optional[Mapping[str, Iterable[str]]] = None,
) -> pd.DataFrame:
    quadro_canonico = quadro.copy()
    if not mapa_alias:
        quadro_canonico.columns = [normalizar_texto(coluna) for coluna in quadro_canonico.columns]
        return quadro_canonico

    lookup = construir_mapa_alias(mapa_alias)
    renomear: dict[str, str] = {}
    destinos_usados: set[str] = set()

    for original in quadro_canonico.columns:
        normalizado = normalizar_texto(original)
        destino = lookup.get(normalizado, normalizado)
        if destino in destinos_usados:
            sufixo = 2
            candidato = f"{destino}__dup{sufixo}"
            while candidato in destinos_usados:
                sufixo += 1
                candidato = f"{destino}__dup{sufixo}"
            destino = candidato
        renomear[original] = destino
        destinos_usados.add(destino)

    return quadro_canonico.rename(columns=renomear)


def materializar_quadros_estruturais_resolvidos(
    quadros_canonicos: Mapping[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Materializa o nome normativo dos quadros estruturais resolvidos.

    No código legado, esses quadros ainda são chamados de ``quadros_canonicos``.
    Na arquitetura da Etapa 1, o nome normativo é
    ``quadros_estruturais_resolvidos``. Esta função não altera DataFrames, não
    copia dados internamente e não muda consumidores existentes.
    """

    return dict(quadros_canonicos)


def aliases_coluna(config: Mapping[str, Any], secao: str, chave: str) -> list[str]:
    colunas_cfg = config.get("colunas", {}) if isinstance(config.get("colunas"), Mapping) else {}
    secao_cfg = colunas_cfg.get(secao, {}) if isinstance(colunas_cfg.get(secao), Mapping) else {}
    aliases = secao_cfg.get(chave)
    if aliases is None:
        raise KeyError(f"Config de coluna ausente para {secao}/{chave}.")
    if not isinstance(aliases, list) or not aliases:
        raise KeyError(f"Aliases de coluna inválidos para {secao}/{chave}.")
    return [str(alias) for alias in aliases]


def resolver_coluna(
    df: pd.DataFrame,
    config: Mapping[str, Any],
    secao: str,
    chave: str,
    obrigatoria: bool = True,
) -> Optional[str]:
    if df is None or len(getattr(df, "columns", [])) == 0:
        if obrigatoria:
            raise KeyError(f"DataFrame vazio ao resolver coluna {secao}/{chave}.")
        return None

    cols_reais = list(df.columns)
    mapa_norm = {normalizar_texto(c): c for c in cols_reais}

    try:
        aliases = aliases_coluna(config, secao, chave)
    except Exception:
        if obrigatoria:
            raise
        return None

    for alias in aliases:
        alias_norm = normalizar_texto(alias)
        if alias_norm in mapa_norm:
            return str(mapa_norm[alias_norm])

    if obrigatoria:
        raise KeyError(
            f"Coluna não encontrada para {secao}/{chave}. "
            f"Aliases tentados: {aliases}. Colunas disponíveis: {cols_reais}"
        )
    return None


def construir_mapa_abas_resolvidas(
    nomes_abas: Iterable[str],
    config: Mapping[str, Any],
) -> MapaAbasResolvidas:
    """Constrói o mapa estrutural de abas resolvidas da Etapa 1.

    Esta função apenas explicita a correspondência atualmente usada entre
    blocos canônicos e abas físicas configuradas. Ela não altera a leitura da
    planilha, não cria dados operacionais canônicos e não resolve aliases de
    colunas.
    """

    nomes_abas_lista = [str(nome_aba) for nome_aba in nomes_abas]
    nomes_abas_set = set(nomes_abas_lista)
    abas_config = config.get("abas", {}) if isinstance(config.get("abas"), Mapping) else {}

    abas_por_bloco: dict[str, str] = {}
    metadados_por_bloco: dict[str, Mapping[str, Any]] = {}
    blocos_ausentes: list[str] = []

    for nome_bloco, nome_aba_cfg in abas_config.items():
        bloco = str(nome_bloco)
        aba_configurada = str(nome_aba_cfg)
        presente = aba_configurada in nomes_abas_set
        aba_resolvida = aba_configurada if presente else None

        if presente and aba_resolvida is not None:
            abas_por_bloco[bloco] = aba_resolvida
        else:
            blocos_ausentes.append(bloco)

        metadados_por_bloco[bloco] = {
            "aba_configurada": aba_configurada,
            "aba_resolvida": aba_resolvida,
            "presente": presente,
            "criterio_resolucao": "config_abas_correspondencia_exata",
        }

    auditoria = {
        "qtd_abas_planilha": len(nomes_abas_lista),
        "qtd_blocos_configurados": len(abas_config),
        "qtd_blocos_resolvidos": len(abas_por_bloco),
        "blocos_ausentes": blocos_ausentes,
        "criterio_resolucao": "config_abas_correspondencia_exata",
        "altera_leitura_planilha": False,
        "altera_fluxo_operacional": False,
    }

    return MapaAbasResolvidas(
        abas_por_bloco=abas_por_bloco,
        metadados_por_bloco=metadados_por_bloco,
        auditoria=auditoria,
    )


def construir_mapa_colunas_resolvidas(
    quadros_brutos: Mapping[str, pd.DataFrame],
    mapa_abas_resolvidas: MapaAbasResolvidas,
    config: Mapping[str, Any],
) -> MapaColunasResolvidas:
    """Constrói o mapa estrutural de colunas resolvidas da Etapa 1.

    A função apenas explicita a correspondência entre campos configurados e
    colunas físicas encontradas. Ela usa o mesmo critério de normalização de
    aliases já usado por ``resolver_coluna`` e ``canonizar_colunas``, mas não
    altera os DataFrames, não cria dados operacionais canônicos e não executa
    validação pré-execução.
    """

    colunas_config = config.get("colunas", {}) if isinstance(config.get("colunas"), Mapping) else {}

    colunas_por_bloco: dict[str, dict[str, str]] = {}
    metadados_por_bloco: dict[str, Mapping[str, Any]] = {}
    campos_ausentes_por_bloco: dict[str, list[str]] = {}

    for bloco, aba_resolvida in mapa_abas_resolvidas.abas_por_bloco.items():
        quadro = quadros_brutos.get(aba_resolvida)
        aliases_por_campo = colunas_config.get(bloco, {}) if isinstance(colunas_config.get(bloco), Mapping) else {}

        colunas_resolvidas: dict[str, str] = {}
        metadados_campos: dict[str, Mapping[str, Any]] = {}
        campos_ausentes: list[str] = []

        if quadro is None:
            campos_ausentes_por_bloco[str(bloco)] = [str(campo) for campo in aliases_por_campo]
            metadados_por_bloco[str(bloco)] = {
                "aba_resolvida": aba_resolvida,
                "quadro_presente": False,
                "campos": {},
                "criterio_resolucao": "aliases_config_colunas_normalizados",
            }
            continue

        colunas_reais = [str(coluna) for coluna in quadro.columns]
        mapa_colunas_normalizadas = {normalizar_texto(coluna): coluna for coluna in colunas_reais}

        for campo, aliases in aliases_por_campo.items():
            campo_str = str(campo)
            aliases_lista = [str(alias) for alias in aliases] if isinstance(aliases, list) else []
            coluna_resolvida: Optional[str] = None
            alias_resolvido: Optional[str] = None

            for alias in aliases_lista:
                alias_norm = normalizar_texto(alias)
                if alias_norm in mapa_colunas_normalizadas:
                    coluna_resolvida = str(mapa_colunas_normalizadas[alias_norm])
                    alias_resolvido = alias
                    break

            if coluna_resolvida is not None:
                colunas_resolvidas[campo_str] = coluna_resolvida
            else:
                campos_ausentes.append(campo_str)

            metadados_campos[campo_str] = {
                "aliases_configurados": aliases_lista,
                "alias_resolvido": alias_resolvido,
                "coluna_resolvida": coluna_resolvida,
                "presente": coluna_resolvida is not None,
            }

        colunas_por_bloco[str(bloco)] = colunas_resolvidas
        campos_ausentes_por_bloco[str(bloco)] = campos_ausentes
        metadados_por_bloco[str(bloco)] = {
            "aba_resolvida": aba_resolvida,
            "quadro_presente": True,
            "qtd_colunas_quadro": len(colunas_reais),
            "qtd_campos_configurados": len(aliases_por_campo),
            "qtd_campos_resolvidos": len(colunas_resolvidas),
            "campos": metadados_campos,
            "criterio_resolucao": "aliases_config_colunas_normalizados",
        }

    auditoria = {
        "qtd_blocos_com_abas_resolvidas": len(mapa_abas_resolvidas.abas_por_bloco),
        "qtd_blocos_com_colunas_resolvidas": len(colunas_por_bloco),
        "campos_ausentes_por_bloco": campos_ausentes_por_bloco,
        "criterio_resolucao": "aliases_config_colunas_normalizados",
        "altera_colunas_dataframe": False,
        "altera_leitura_planilha": False,
        "altera_fluxo_operacional": False,
    }

    return MapaColunasResolvidas(
        colunas_por_bloco=colunas_por_bloco,
        metadados_por_bloco=metadados_por_bloco,
        auditoria=auditoria,
    )


def _string_iso_yyyy_mm_dd(valor: str) -> bool:
    texto = valor.strip()
    return (
        len(texto) == 10
        and texto[4] == "-"
        and texto[7] == "-"
        and texto[:4].isdigit()
        and texto[5:7].isdigit()
        and texto[8:10].isdigit()
    )


def _normalizar_data_para_janela_cdi(valor: Any) -> Optional[date]:
    if valor is None:
        return None
    try:
        if pd.isna(valor):
            return None
    except Exception:
        pass

    if isinstance(valor, pd.Timestamp):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return None

    if isinstance(valor, str):
        texto = valor.strip()
        if not texto:
            return None
        if _string_iso_yyyy_mm_dd(texto):
            try:
                convertido_iso = pd.to_datetime(texto, errors="coerce", format="%Y-%m-%d")
            except Exception:
                convertido_iso = pd.NaT
            if not pd.isna(convertido_iso):
                return convertido_iso.date()
        try:
            convertido_br = pd.to_datetime(texto, errors="coerce", dayfirst=True)
        except Exception:
            return None
        if pd.isna(convertido_br):
            return None
        return convertido_br.date()

    try:
        convertido = pd.to_datetime(valor, errors="coerce", dayfirst=True)
    except Exception:
        return None
    if pd.isna(convertido):
        return None
    return convertido.date()


def _primeiro_dia_do_mes_janela_cdi(dt: date) -> date:
    return dt.replace(day=1)


def _nome_temporal_para_janela_cdi(valor: Any) -> bool:
    normalizado = normalizar_texto(valor)
    tokens = normalizado.replace("_", " ").replace("-", " ").replace("/", " ").replace(".", " ").split()
    return "data" in tokens or "vencimento" in tokens


def _resolver_coluna_janela_cdi(
    quadro: pd.DataFrame,
    *,
    campo: Any,
    coluna_resolvida: Any,
) -> Optional[Any]:
    """Resolve coluna temporal preservando compatibilidade original/canônica.

    ``mapa_colunas_resolvidas`` guarda a coluna física encontrada no quadro
    bruto, enquanto ``quadros_estruturais_resolvidos`` pode ter colunas
    renomeadas por aliases canônicos. Esta função aceita ambos os nomes antes
    de desistir da coluna.
    """

    if quadro is None or not hasattr(quadro, "columns"):
        return None

    colunas = list(quadro.columns)
    candidatos = [coluna_resolvida, campo]
    candidatos.extend(normalizar_texto(candidato) for candidato in list(candidatos))

    for candidato in candidatos:
        if candidato in quadro.columns:
            return candidato

    colunas_por_normalizado = {normalizar_texto(coluna): coluna for coluna in colunas}
    for candidato in candidatos:
        normalizado = normalizar_texto(candidato)
        if normalizado in colunas_por_normalizado:
            return colunas_por_normalizado[normalizado]

    return None


def _datas_coluna_janela_cdi(
    quadro: pd.DataFrame,
    coluna: Any,
    *,
    data_referencia: Optional[date],
) -> tuple[list[date], int]:
    datas: list[date] = []
    datas_futuras_ignoradas = 0

    for valor in quadro[coluna]:
        data_normalizada = _normalizar_data_para_janela_cdi(valor)
        if data_normalizada is None:
            continue
        if data_referencia is not None and data_normalizada > data_referencia:
            datas_futuras_ignoradas += 1
            continue
        datas.append(data_normalizada)

    return datas, datas_futuras_ignoradas


def construir_janela_consulta_cdi(
    quadros_estruturais_resolvidos: Mapping[str, pd.DataFrame],
    mapa_abas_resolvidas: MapaAbasResolvidas,
    mapa_colunas_resolvidas: MapaColunasResolvidas,
    *,
    data_referencia: Optional[date] = None,
) -> JanelaConsultaCDI:
    """Deriva a janela bruta de consulta CDI a partir da entrada resolvida.

    A função identifica datas interpretáveis em campos resolvidos cujo nome
    estrutural contém ``data`` ou ``vencimento`` e, de forma complementar,
    varre colunas operacionais com nomes temporais. Ela não consulta BCB, não
    carrega cache, não calcula rendimento e não altera DataFrames.
    """

    datas: list[date] = []
    fontes_datas: dict[str, list[str]] = {}
    fontes_sem_coluna_resolvida: list[str] = []
    datas_futuras_ignoradas_por_fonte: dict[str, int] = {}
    colunas_usadas_por_bloco: dict[str, set[Any]] = {}

    data_ref_norm: Optional[date] = None
    if data_referencia is not None:
        data_ref_norm = _normalizar_data_para_janela_cdi(data_referencia)
        if data_ref_norm is not None:
            datas.append(data_ref_norm)
            fontes_datas["data_referencia"] = [data_ref_norm.isoformat()]

    for bloco, aba_resolvida in mapa_abas_resolvidas.abas_por_bloco.items():
        bloco_str = str(bloco)
        quadro = quadros_estruturais_resolvidos.get(aba_resolvida)
        colunas_bloco = mapa_colunas_resolvidas.colunas_por_bloco.get(bloco_str, {})
        if quadro is None:
            continue

        colunas_usadas = colunas_usadas_por_bloco.setdefault(bloco_str, set())

        for campo, coluna in colunas_bloco.items():
            if not _nome_temporal_para_janela_cdi(campo) and not _nome_temporal_para_janela_cdi(coluna):
                continue

            coluna_quadro = _resolver_coluna_janela_cdi(
                quadro,
                campo=campo,
                coluna_resolvida=coluna,
            )
            chave_fonte = f"{bloco}.{campo}"
            if coluna_quadro is None:
                fontes_sem_coluna_resolvida.append(chave_fonte)
                continue

            datas_coluna, qtd_futuras = _datas_coluna_janela_cdi(
                quadro,
                coluna_quadro,
                data_referencia=data_ref_norm,
            )
            colunas_usadas.add(coluna_quadro)
            if qtd_futuras:
                datas_futuras_ignoradas_por_fonte[chave_fonte] = qtd_futuras
            if not datas_coluna:
                continue

            datas.extend(datas_coluna)
            fontes_datas[chave_fonte] = sorted({valor.isoformat() for valor in datas_coluna})

        for coluna in quadro.columns:
            if coluna in colunas_usadas:
                continue
            if not _nome_temporal_para_janela_cdi(coluna):
                continue

            datas_coluna, qtd_futuras = _datas_coluna_janela_cdi(
                quadro,
                coluna,
                data_referencia=data_ref_norm,
            )
            chave_fonte = f"{bloco}.__coluna_operacional__.{coluna}"
            if qtd_futuras:
                datas_futuras_ignoradas_por_fonte[chave_fonte] = qtd_futuras
            if not datas_coluna:
                continue

            datas.extend(datas_coluna)
            colunas_usadas.add(coluna)
            fontes_datas[chave_fonte] = sorted({valor.isoformat() for valor in datas_coluna})

    metadados_base = {
        "fontes_datas": fontes_datas,
        "fontes_sem_coluna_resolvida": fontes_sem_coluna_resolvida,
        "datas_futuras_ignoradas_por_fonte": datas_futuras_ignoradas_por_fonte,
        "criterio_resolucao": "campos_resolvidos_e_colunas_operacionais_com_data_ou_vencimento",
        "criterio_cobertura_replay_historico": "primeiro_dia_mes_menor_data_operacional_ate_data_referencia",
        "inclui_data_referencia": data_ref_norm is not None,
        "altera_cache_cdi": False,
        "altera_rendimento": False,
        "altera_fluxo_operacional": False,
    }

    if not datas:
        return JanelaConsultaCDI(
            data_inicial_consulta=None,
            data_final_consulta=None,
            metadados={
                "qtd_datas_identificadas": 0,
                **metadados_base,
            },
        )

    data_minima = min(datas)
    data_maxima = max(datas)
    data_inicial_consulta = _primeiro_dia_do_mes_janela_cdi(data_minima)
    data_final_consulta = max(data_maxima, data_ref_norm) if data_ref_norm is not None else data_maxima

    return JanelaConsultaCDI(
        data_inicial_consulta=data_inicial_consulta,
        data_final_consulta=data_final_consulta,
        metadados={
            "qtd_datas_identificadas": len(datas),
            "menor_data_identificada": data_minima.isoformat(),
            "maior_data_identificada": data_maxima.isoformat(),
            **metadados_base,
        },
    )


def resolver_caminho_planilha(
    config: Mapping[str, Any],
    *,
    raiz_repositorio: Optional[Path] = None,
    caminho_explicito: Optional[str | Path] = None,
) -> Path:
    if caminho_explicito is not None:
        caminho = Path(caminho_explicito).expanduser().resolve()
        if not caminho.exists():
            raise FileNotFoundError(f"Planilha explícita não encontrada: {caminho}")
        return caminho

    raiz = (raiz_repositorio or Path.cwd()).resolve()
    arquivos_cfg = config.get("arquivos", {}) if isinstance(config.get("arquivos"), Mapping) else {}
    nome_arquivo = arquivos_cfg.get("planilha", "dados_financeiros.xlsx")

    candidatos = [
        raiz / "dados" / nome_arquivo,
        raiz / "data" / nome_arquivo,
        raiz / nome_arquivo,
    ]
    for candidato in candidatos:
        if candidato.exists():
            return candidato.resolve()

    caminhos_testados = "\n - ".join(str(c) for c in candidatos)
    raise FileNotFoundError(f"Planilha não encontrada. Caminhos testados:\n - {caminhos_testados}")


def carregar_planilha(
    config: Mapping[str, Any],
    *,
    raiz_repositorio: Optional[Path] = None,
    caminho_explicito: Optional[str | Path] = None,
    carregar_todas_as_abas: bool = True,
    data_referencia: Optional[date] = None,
) -> PacotePlanilha:
    fonte_planilha = 'caminho_explicito' if caminho_explicito is not None else 'fallback_local'
    fetch_status: Optional[str] = None
    erros_validacao: list[str] = []
    avisos_validacao: list[str] = []

    if caminho_explicito is None:
        raiz = (raiz_repositorio or Path.cwd()).resolve()
        arquivos_cfg = config.get("arquivos", {}) if isinstance(config.get("arquivos"), Mapping) else {}
        nome_arquivo = arquivos_cfg.get("planilha", "dados_financeiros.xlsx")
        destino_planilha = (raiz / "dados" / nome_arquivo).resolve()
        baixou, motivo = _tentar_baixar_planilha(config, destino_planilha)
        if baixou:
            fonte_planilha = 'download'
            fetch_status = 'ok'
        else:
            fetch_status = motivo or 'nao_tentado'
            if motivo not in (None, 'url_planilha_ausente'):
                avisos_validacao.append('download_planilha_indisponivel_usando_fallback_local')

    caminho_planilha = resolver_caminho_planilha(
        config,
        raiz_repositorio=raiz_repositorio,
        caminho_explicito=caminho_explicito,
    )

    excel = pd.ExcelFile(caminho_planilha)
    quadros_brutos: dict[str, pd.DataFrame] = {}
    quadros_canonicos: dict[str, pd.DataFrame] = {}

    abas_alvo = list(excel.sheet_names) if carregar_todas_as_abas else []
    abas_config = config.get("abas", {}) if isinstance(config.get("abas"), Mapping) else {}
    aliases_por_bloco = config.get("colunas", {}) if isinstance(config.get("colunas"), Mapping) else {}
    mapa_abas_resolvidas = construir_mapa_abas_resolvidas(excel.sheet_names, config)

    for nome_bloco, nome_aba in abas_config.items():
        if nome_aba in excel.sheet_names and nome_aba not in abas_alvo:
            abas_alvo.append(nome_aba)

    for nome_aba in abas_alvo:
        quadro = pd.read_excel(caminho_planilha, sheet_name=nome_aba)
        quadros_brutos[nome_aba] = quadro

        nome_bloco = next(
            (bloco for bloco, aba_cfg in abas_config.items() if aba_cfg == nome_aba),
            None,
        )
        mapa_alias = aliases_por_bloco.get(nome_bloco, {}) if nome_bloco else {}
        quadros_canonicos[nome_aba] = canonizar_colunas(quadro, mapa_alias=mapa_alias)

    quadros_estruturais_resolvidos = materializar_quadros_estruturais_resolvidos(quadros_canonicos)

    mapa_colunas_resolvidas = construir_mapa_colunas_resolvidas(
        quadros_brutos,
        mapa_abas_resolvidas,
        config,
    )

    janela_consulta_cdi = construir_janela_consulta_cdi(
        quadros_estruturais_resolvidos,
        mapa_abas_resolvidas,
        mapa_colunas_resolvidas,
        data_referencia=data_referencia,
    )

    auditoria = {
        'fonte_planilha': fonte_planilha,
        'fetch_status_planilha': fetch_status,
        'caminho_planilha': str(caminho_planilha),
        'qtd_abas_planilha': len(excel.sheet_names),
    }
    validacao = {'ok': len(erros_validacao) == 0, 'erros': erros_validacao, 'avisos': avisos_validacao}

    return PacotePlanilha(
        caminho=caminho_planilha,
        nomes_abas=list(excel.sheet_names),
        quadros_brutos=quadros_brutos,
        quadros_canonicos=quadros_canonicos,
        auditoria=auditoria,
        validacao=validacao,
        mapa_abas_resolvidas=mapa_abas_resolvidas,
        mapa_colunas_resolvidas=mapa_colunas_resolvidas,
        quadros_estruturais_resolvidos=quadros_estruturais_resolvidos,
        janela_consulta_cdi=janela_consulta_cdi,
    )


def construir_resumo_planilha(pacote: PacotePlanilha) -> list[dict[str, Any]]:
    resumo: list[dict[str, Any]] = []
    for nome_aba in pacote.nomes_abas:
        quadro = pacote.quadros_brutos.get(nome_aba)
        if quadro is None:
            continue
        resumo.append(
            {
                "nome_aba": nome_aba,
                "n_linhas": int(quadro.shape[0]),
                "n_colunas": int(quadro.shape[1]),
                "colunas": list(map(str, quadro.columns)),
            }
        )
    return resumo