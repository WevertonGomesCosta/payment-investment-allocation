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
