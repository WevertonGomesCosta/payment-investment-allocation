"""Utilitários neutros transversais compartilhados pela baseline.

Este módulo concentra apenas helpers genéricos de texto, datas, valores,
identificadores, booleanos e arredondamento monetário. Ele não implementa
regras de negócio, replay, switching, fiscalidade ou motor financeiro.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Iterable, Optional
import unicodedata

import pandas as pd


TEXTOS_NULOS_PADRAO = {"", "nan", "none", "null"}
VERDADEIROS_PADRAO = {"1", "true", "t", "sim", "s", "ok", "ativo", "yes", "y", "isento", "pago"}
FALSOS_PADRAO = {"0", "false", "f", "nao", "não", "n", "inativo", "no"}


def remover_acentos(texto: str) -> str:
    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    )


def normalizar_texto(texto: Any) -> str:
    texto = "" if texto is None else str(texto)
    texto = remover_acentos(texto).strip().lower()
    for antigo, novo in [("/", " "), ("-", " "), ("(", " "), (")", " "), ("_", " ")]:
        texto = texto.replace(antigo, novo)
    return " ".join(texto.split())


def limpar_texto(valor: Any, default: str = "") -> str:
    if valor is None:
        return default
    try:
        texto = " ".join(str(valor).strip().split())
        if texto.lower() in TEXTOS_NULOS_PADRAO:
            return default
        return texto
    except Exception:
        return default


def normalizar_identificador(valor: Any, *, remover_sufixo_excel: bool = True) -> str:
    texto = limpar_texto(valor)
    if not texto:
        return ""
    if remover_sufixo_excel and texto.endswith('.0'):
        texto = texto[:-2]
    return texto


def para_data(valor: Any) -> Optional[date]:
    if valor is None:
        return None
    try:
        if pd.isna(valor):
            return None
    except Exception:
        pass
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        ts = pd.to_datetime(valor, errors='coerce')
        if pd.isna(ts):
            return None
        return ts.date()
    except Exception:
        return None


def para_bool(
    valor: Any,
    default: bool = False,
    *,
    verdadeiros: Optional[Iterable[str]] = None,
    falsos: Optional[Iterable[str]] = None,
) -> bool:
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return default
    if isinstance(valor, bool):
        return valor
    texto = str(valor).strip().lower()
    conjunto_verdadeiros = {x.lower() for x in (verdadeiros or VERDADEIROS_PADRAO)}
    conjunto_falsos = {x.lower() for x in (falsos or FALSOS_PADRAO)}
    if texto in conjunto_verdadeiros:
        return True
    if texto in conjunto_falsos:
        return False
    return default


def para_int(valor: Any, default: int = 0) -> int:
    if valor is None or valor == "" or (isinstance(valor, float) and pd.isna(valor)):
        return default
    try:
        return int(float(str(valor).strip().replace(',', '.')))
    except Exception:
        return default


def para_float_monetario(valor: Any, default: float = 0.0) -> float:
    if valor is None or valor == "":
        return default
    try:
        if isinstance(valor, (int, float)):
            if pd.isna(valor):
                return default
            return float(valor)
    except Exception:
        pass
    try:
        texto = str(valor).strip()
        if not texto or texto.lower() in TEXTOS_NULOS_PADRAO:
            return default
        texto = (
            texto.replace('R$', '')
            .replace('%', '')
            .replace(' ', '')
            .replace('\u00a0', '')
        )
        if not texto:
            return default

        sinal = -1.0 if texto.startswith('-') else 1.0
        if texto[:1] in {'+', '-'}:
            texto = texto[1:]

        texto = ''.join(ch for ch in texto if ch.isdigit() or ch in {'.', ','})
        if not texto:
            return default

        separadores = [i for i, ch in enumerate(texto) if ch in {'.', ','}]
        if separadores:
            ultimo = separadores[-1]
            parte_inteira = ''.join(ch for ch in texto[:ultimo] if ch.isdigit())
            parte_decimal = ''.join(ch for ch in texto[ultimo + 1:] if ch.isdigit())
            if parte_decimal:
                texto = f"{parte_inteira}.{parte_decimal}"
            else:
                texto = parte_inteira
        return sinal * float(texto)
    except Exception:
        return default


# Helpers canônicos de baixo risco centralizados na V204.
# Mantêm semântica utilitária simples e não implementam regra econômica.
def _safe_float(valor: Any, default: float = 0.0) -> float:
    try:
        if valor in (None, ''):
            return float(default)
        return float(valor)
    except Exception:
        return float(default)


def _coerce_date(valor: Any) -> date | None:
    if valor is None:
        return None
    try:
        if pd.isna(valor):
            return None
    except Exception:
        pass
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        ts = pd.to_datetime(valor, errors='coerce')
        if pd.isna(ts):
            return None
        return ts.date()
    except Exception:
        return None


def _valor_ausente(valor: Any) -> bool:
    if valor is None:
        return True
    if isinstance(valor, str):
        return valor.strip() == ''
    if isinstance(valor, (pd.Series, pd.DataFrame)):
        return bool(valor.empty)
    try:
        nulo = pd.isna(valor)
        if isinstance(nulo, (bool, int, float)):
            return bool(nulo)
    except Exception:
        pass
    return False


def _valor_campo(objeto: Any, chave: str, default: Any = None) -> Any:
    if objeto is None:
        return default
    if isinstance(objeto, Mapping):
        return objeto.get(chave, default)
    if isinstance(objeto, pd.Series):
        return objeto.get(chave, default)
    metodo_get = getattr(objeto, 'get', None)
    if callable(metodo_get):
        try:
            return metodo_get(chave, default)
        except TypeError:
            try:
                return metodo_get(chave)
            except Exception:
                return default
        except Exception:
            return default
    return getattr(objeto, chave, default)


def _primeiro_campo_texto(objeto: Any, chaves: Iterable[str]) -> str:
    for chave in chaves:
        valor = _valor_campo(objeto, chave)
        if not _valor_ausente(valor):
            texto = str(valor).strip()
            if texto:
                return texto
    return ''


def _split_fontes_compostas(valor: Any) -> list[str]:
    if _valor_ausente(valor):
        return []
    partes = [parte.strip() for parte in str(valor).split('+')]
    return [parte for parte in partes if parte]



# Helpers semânticos centralizados na V206.
# Mantêm a semântica pré-existente de rótulo de fonte, identificação de fonte,
# proxy terminal e alíquota estimada, sem introduzir nova regra econômica.
def _slug_fonte(chave: Any) -> str:
    texto = normalizar_texto(chave).replace(' ', '_')
    return texto or 'fonte'


def _rotulo_fonte(candidato: Any) -> str:
    lote_id = _primeiro_campo_texto(candidato, ('lote_id', 'lote_id_escolhido'))
    if lote_id:
        return lote_id
    return _primeiro_campo_texto(candidato, ('fonte_base_escolhida', 'fonte_escolhida_id'))


def _fonte_id(candidato_ou_tipo: Any, *, lote_id: str | None = None, recebido_id: str | None = None) -> str:
    if isinstance(candidato_ou_tipo, (Mapping, pd.Series)) or callable(getattr(candidato_ou_tipo, 'get', None)):
        return _primeiro_campo_texto(candidato_ou_tipo, ('fonte_base_escolhida', 'fonte_escolhida_id'))
    tipo_fonte = '' if _valor_ausente(candidato_ou_tipo) else str(candidato_ou_tipo).strip()
    base = lote_id or recebido_id or tipo_fonte
    return f"fonte::{_slug_fonte(tipo_fonte)}::{_slug_fonte(base)}"


def _normalizar_proxy_terminal(valor: Any) -> float:
    numero = _safe_float(valor)
    if numero > 1.0:
        numero = numero / 100.0
    return max(numero, 0.0)


def _aliquota_ir_estimada(data_aplicacao: date | None, data_acao: date | None) -> float:
    if data_aplicacao is None or data_acao is None:
        return 0.15
    dias = max((data_acao - data_aplicacao).days, 0)
    if dias <= 180:
        return 0.225
    if dias <= 360:
        return 0.20
    if dias <= 720:
        return 0.175
    return 0.15


def arredondar_monetario(valor: Any, casas: int = 2) -> float:
    quant = '1.' + ('0' * casas)
    return float(Decimal(str(valor)).quantize(Decimal(quant), rounding=ROUND_HALF_UP))



def normalizar_valores_situacao_atual_exaurida(*, saldo_bruto: float, saldo_liquido: float, saldo_rem: float, exaurido: bool) -> tuple[float, float, float]:
    if not exaurido:
        return saldo_bruto, saldo_liquido, saldo_rem
    return 0.0, 0.0, 0.0


def normalizar_saldo_remanescente_operacional(
    valor: Any,
    *,
    limiar_residuo_resolvido: float = 0.20,
    tolerancia_monetaria: float = 0.01,
    exaurido: bool = False,
) -> float:
    saldo = arredondar_monetario(para_float_monetario(valor, 0.0))
    limiar = arredondar_monetario(max(float(limiar_residuo_resolvido or 0.0), 0.0))
    tolerancia = arredondar_monetario(max(float(tolerancia_monetaria or 0.0), 0.0))
    if saldo <= 0.0:
        return 0.0
    if saldo <= limiar:
        return 0.0
    if saldo <= arredondar_monetario(limiar + tolerancia):
        return 0.0
    if exaurido:
        return 0.0
    return saldo


def tokenizar_texto_normalizado(valor: Any) -> list[str]:
    texto = normalizar_texto(valor)
    return [parte for parte in texto.split() if parte]


def escolher_melhor_correspondencia_textual(
    valor: Any,
    opcoes: Iterable[tuple[str, str]],
    *,
    minimo_score: float = 0.55,
) -> tuple[Optional[str], dict[str, Any]]:
    """Escolhe a melhor correspondência textual neutra entre um valor e opções."""
    texto = normalizar_texto(valor)
    if not texto:
        return None, {"score": 0.0, "motivo": "texto_vazio"}

    tokens_alvo = set(tokenizar_texto_normalizado(texto))
    melhor_chave = None
    melhor_score = 0.0
    melhor_referencia = ""

    for chave, referencia in opcoes:
        referencia_norm = normalizar_texto(referencia)
        if not referencia_norm:
            continue
        if referencia_norm == texto:
            return chave, {"score": 1.0, "motivo": "texto_exato", "referencia": referencia}

        tokens_ref = set(tokenizar_texto_normalizado(referencia_norm))
        if not tokens_ref:
            continue

        inter = len(tokens_alvo & tokens_ref)
        if inter == 0:
            continue

        cobertura_alvo = inter / max(len(tokens_alvo), 1)
        cobertura_ref = inter / max(len(tokens_ref), 1)
        score = (0.65 * cobertura_alvo) + (0.35 * cobertura_ref)

        numeros_alvo = {t for t in tokens_alvo if any(ch.isdigit() for ch in t)}
        numeros_ref = {t for t in tokens_ref if any(ch.isdigit() for ch in t)}
        if numeros_alvo and numeros_ref and numeros_alvo == numeros_ref:
            score += 0.15
        elif numeros_alvo and numeros_ref and numeros_alvo & numeros_ref:
            score += 0.08

        if texto in referencia_norm or referencia_norm in texto:
            score += 0.05

        if score > melhor_score:
            melhor_score = score
            melhor_chave = chave
            melhor_referencia = referencia

    if melhor_chave is None or melhor_score < minimo_score:
        return None, {
            "score": melhor_score,
            "motivo": "sem_correspondencia_suficiente",
            "referencia": melhor_referencia,
        }

    return melhor_chave, {
        "score": melhor_score,
        "motivo": "melhor_correspondencia_textual",
        "referencia": melhor_referencia,
    }



def limitar_intervalo(valor: Any, minimo: float = 0.0, maximo: float = 100.0) -> float:
    try:
        valor_num = float(valor)
    except Exception:
        valor_num = float(minimo)
    return max(float(minimo), min(float(maximo), valor_num))


def percentual_lista(valores: Iterable[float], valor: float) -> float:
    lista = [float(v) for v in valores if v is not None]
    if not lista:
        return 0.0
    menor = min(lista)
    maior = max(lista)
    if abs(maior - menor) <= 1e-12:
        return 100.0
    return limitar_intervalo(((float(valor) - menor) / (maior - menor)) * 100.0)
