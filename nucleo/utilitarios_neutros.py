"""Utilitários neutros transversais compartilhados pela baseline.

Este módulo concentra apenas helpers genéricos de texto, datas, valores,
identificadores, booleanos e arredondamento monetário. Ele não implementa
regras de negócio, replay, switching, fiscalidade ou motor financeiro.
"""

from __future__ import annotations

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
        texto = texto.replace('R$', '').replace('%', '').replace(' ', '')
        if ',' in texto and '.' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        return float(texto)
    except Exception:
        return default


def arredondar_monetario(valor: Any, casas: int = 2) -> float:
    quant = '1.' + ('0' * casas)
    return float(Decimal(str(valor)).quantize(Decimal(quant), rounding=ROUND_HALF_UP))


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
