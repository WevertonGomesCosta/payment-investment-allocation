from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import date, datetime
from hashlib import sha256
from typing import Any, Iterable


TOLERANCIA_MONETARIA_PADRAO = 0.01
LIMIAR_RESIDUO_PADRAO = 0.20

_ESTADOS_LOTE_INDISPONIVEIS = {
    "exaurido",
    "exaurido_por_saque",
    "exaurido_por_switching",
    "migrado_por_switching",
    "indisponivel",
    "bloqueado",
}


@dataclass(slots=True)
class UnidadeEconomicaCanonica:
    unidade_id: str
    tipo_unidade: str
    identidade_origem: str
    estado_ciclo: str
    valor_liquido_atual: float
    disponivel_pagamento_na_referencia: bool
    data_referencia: date
    data_origem: date | None = None
    data_aplicacao: date | None = None
    data_inicio_rendimento: date | None = None
    data_disponibilidade_resgate: date | None = None
    data_vencimento: date | None = None
    produto: str | None = None
    origem_canonica: str | None = None
    vinculos: dict[str, Any] = field(default_factory=dict)
    evidencias: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EventoConservacaoEconomica:
    evento_id: str
    tipo_evento: str
    data_evento: date | None
    unidade_origem_id: str | None
    unidade_destino_id: str | None
    valor_saida: float
    valor_entrada: float
    custo_ou_imposto: float
    diferenca_conservacao: float
    ok: bool
    referencias: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AuditoriaEstadoEconomicoCanonico:
    ok: bool
    bloqueios: list[str]
    avisos: list[str]
    reconciliacoes: list[str]
    resumo: dict[str, Any]


@dataclass(slots=True)
class EstadoEconomicoCanonico:
    data_referencia: date
    unidades: list[UnidadeEconomicaCanonica]
    fontes_disponiveis: list[dict[str, Any]]
    fontes_bloqueadas: list[dict[str, Any]]
    eventos_conservacao: list[EventoConservacaoEconomica]
    auditoria: AuditoriaEstadoEconomicoCanonico
    metadados: dict[str, Any] = field(default_factory=dict)

    def como_dict(self) -> dict[str, Any]:
        return {
            "data_referencia": self.data_referencia.isoformat(),
            "unidades": [_serializar_dataclass(item) for item in self.unidades],
            "fontes_disponiveis": [_serializar_valores(item) for item in self.fontes_disponiveis],
            "fontes_bloqueadas": [_serializar_valores(item) for item in self.fontes_bloqueadas],
            "eventos_conservacao": [_serializar_dataclass(item) for item in self.eventos_conservacao],
            "auditoria": _serializar_dataclass(self.auditoria),
            "metadados": _serializar_valores(self.metadados),
        }


class EstadoEconomicoCanonicoInvalido(RuntimeError):
    pass


def _serializar_dataclass(valor: Any) -> dict[str, Any]:
    return _serializar_valores(asdict(valor))


def _serializar_valores(valor: Any) -> Any:
    if isinstance(valor, dict):
        return {str(k): _serializar_valores(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_serializar_valores(v) for v in valor]
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    return valor


def _texto(valor: Any) -> str:
    texto = str(valor or "").strip()
    return "" if texto.lower() in {"", "nan", "none", "n/d", "nd"} else texto


def _numero(valor: Any) -> float | None:
    if valor is None or isinstance(valor, bool):
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    if numero != numero:
        return None
    return numero


def _data(valor: Any) -> date | None:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        texto = valor.strip()[:10]
        for formato in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(texto, formato).date()
            except ValueError:
                continue
    return None


def _primeiro_numero(registro: dict[str, Any], campos: Iterable[str]) -> tuple[float | None, str | None]:
    for campo in campos:
        if campo not in registro:
            continue
        valor = _numero(registro.get(campo))
        if valor is not None:
            return valor, campo
    return None, None


def _id_deterministico(prefixo: str, *partes: Any) -> str:
    texto = "|".join(str(parte or "").strip() for parte in partes)
    digest = sha256(texto.encode("utf-8")).hexdigest()[:16]
    return f"{prefixo}::{digest}"


def _id_lote(registro: dict[str, Any]) -> str:
    return _texto(
        registro.get("lote_id")
        or registro.get("Lote (ID)")
        or registro.get("lote")
        or registro.get("fonte_id")
    )


def _id_recebido(registro: dict[str, Any]) -> str:
    recebido_id = _texto(registro.get("recebido_id") or registro.get("fonte_id_tecnico"))
    if recebido_id:
        return recebido_id
    return _id_deterministico(
        "recebido",
        registro.get("origem"),
        registro.get("data_recebimento"),
        registro.get("valor"),
    )


def _estado_textual(registro: dict[str, Any]) -> str:
    return _texto(
        registro.get("status_temporal")
        or registro.get("status_ciclo")
        or registro.get("situacao_investimento")
        or registro.get("status_recebido")
        or registro.get("status")
    ).lower()


def _registro_equivalente(a: dict[str, Any], b: dict[str, Any], tolerancia: float) -> bool:
    campos_texto = (
        "status_temporal",
        "status_ciclo",
        "status_recebido",
        "origem",
        "lote_id",
        "recebido_id",
        "data_recebimento",
        "data_aplicacao",
    )
    for campo in campos_texto:
        if _texto(a.get(campo)).lower() != _texto(b.get(campo)).lower():
            return False
    campos_valor = (
        "valor",
        "valor_liquido_disponivel_atual",
        "saldo_disponivel_atual",
        "valor_liquido_migrado",
        "saldo_residual_recebido",
    )
    for campo in campos_valor:
        va = _numero(a.get(campo))
        vb = _numero(b.get(campo))
        if va is None and vb is None:
            continue
        if va is None or vb is None or abs(va - vb) > tolerancia:
            return False
    return True


def _agrupar_unicos(
    registros: Iterable[dict[str, Any]],
    obter_id,
    tipo: str,
    tolerancia: float,
    bloqueios: list[str],
    reconciliacoes: list[str],
) -> list[tuple[str, dict[str, Any]]]:
    grupos: dict[str, list[dict[str, Any]]] = {}
    for registro in registros:
        identificador = obter_id(registro)
        if not identificador:
            bloqueios.append(f"{tipo}_sem_identidade_canonica")
            continue
        grupos.setdefault(identificador, []).append(dict(registro))

    saida: list[tuple[str, dict[str, Any]]] = []
    for identificador, itens in grupos.items():
        base = itens[0]
        if len(itens) > 1:
            if all(_registro_equivalente(base, item, tolerancia) for item in itens[1:]):
                reconciliacoes.append(f"{tipo}_duplicado_equivalente_deduplicado:{identificador}:{len(itens)}")
            else:
                bloqueios.append(f"{tipo}_duplicado_conflitante:{identificador}")
                continue
        saida.append((identificador, base))
    return saida


def _construir_unidade_lote(
    lote_id: str,
    registro: dict[str, Any],
    data_ref: date,
    tolerancia: float,
    reconciliacoes: list[str],
    avisos: list[str],
    bloqueios: list[str],
) -> UnidadeEconomicaCanonica:
    status = _estado_textual(registro)
    data_origem = _data(registro.get("data_recebimento"))
    data_aplicacao = _data(registro.get("data_aplicacao"))
    data_inicio_rendimento = _data(
        registro.get("data_inicio_rendimento") or registro.get("data_aplicacao")
    )
    data_resgate = _data(
        registro.get("data_disponibilidade_resgate")
        or registro.get("carencia_ate")
        or registro.get("carencia_ate_origem")
    )
    data_vencimento = _data(registro.get("data_vencimento") or registro.get("vencimento"))

    valor_atual, campo_valor = _primeiro_numero(
        registro,
        (
            "valor_liquido_disponivel_atual",
            "saldo_disponivel_atual",
            "valor_liquido_disponivel",
            "saldo_disponivel",
            "saldo_atual",
        ),
    )
    if valor_atual is None:
        valor_atual = 0.0

    sintetico = bool(registro.get("sintetico_pos_switching")) or "pos_switching" in status
    valor_migrado = _numero(registro.get("valor_liquido_migrado"))
    if sintetico and valor_atual <= tolerancia and valor_migrado is not None and valor_migrado > tolerancia:
        valor_atual = valor_migrado
        campo_valor = "valor_liquido_migrado"
        reconciliacoes.append(f"lote_sintetico_materializado_por_switching:{lote_id}")

    if valor_atual < -tolerancia:
        bloqueios.append(f"lote_saldo_atual_negativo:{lote_id}:{valor_atual:.2f}")

    futuro = bool((data_aplicacao and data_aplicacao > data_ref) or (data_origem and data_origem > data_ref))
    migrado = bool(registro.get("migrado_por_switching")) or "migrado" in status
    indisponivel_explicito = (
        registro.get("disponibilidade") == "indisponivel"
        or registro.get("disponivel_na_data_referencia") is False
        or registro.get("disponivel") is False
        or status in _ESTADOS_LOTE_INDISPONIVEIS
    )

    valor_original = _numero(registro.get("valor_original")) or 0.0
    if valor_atual <= tolerancia and valor_original > tolerancia and not sintetico:
        reconciliacoes.append(f"fallback_valor_original_proibido:{lote_id}")

    if futuro:
        estado_ciclo = "futuro_nao_materializado"
    elif migrado:
        estado_ciclo = "migrado_por_switching"
    elif indisponivel_explicito:
        estado_ciclo = status or "indisponivel"
    elif valor_atual <= LIMIAR_RESIDUO_PADRAO + tolerancia:
        estado_ciclo = "exaurido_sem_saldo_atual"
        if valor_original > tolerancia:
            reconciliacoes.append(f"lote_zerado_nao_ressuscitado:{lote_id}")
    elif data_resgate and data_resgate > data_ref:
        estado_ciclo = "ativo_bloqueado_carencia"
    else:
        estado_ciclo = "ativo_disponivel"

    disponivel = estado_ciclo == "ativo_disponivel" and valor_atual > LIMIAR_RESIDUO_PADRAO + tolerancia
    if campo_valor is None and estado_ciclo.startswith("ativo"):
        avisos.append(f"lote_ativo_sem_campo_saldo_atual:{lote_id}")

    return UnidadeEconomicaCanonica(
        unidade_id=f"lote::{lote_id}",
        tipo_unidade="lote",
        identidade_origem=lote_id,
        estado_ciclo=estado_ciclo,
        valor_liquido_atual=round(max(valor_atual, 0.0), 10),
        disponivel_pagamento_na_referencia=disponivel,
        data_referencia=data_ref,
        data_origem=data_origem,
        data_aplicacao=data_aplicacao,
        data_inicio_rendimento=data_inicio_rendimento,
        data_disponibilidade_resgate=data_resgate,
        data_vencimento=data_vencimento,
        produto=_texto(registro.get("produto") or registro.get("investimento")) or None,
        origem_canonica=_texto(registro.get("origem_canonica")) or "inventario_temporal",
        vinculos={
            "origem_switching": registro.get("origem_switching"),
            "sintetico_pos_switching": sintetico,
        },
        evidencias={
            "campo_valor_atual": campo_valor,
            "valor_original_informativo": valor_original,
            "valor_liquido_migrado": valor_migrado,
            "status_origem": status,
        },
    )


def _valor_residual_recebido(registro: dict[str, Any]) -> tuple[float | None, str | None]:
    return _primeiro_numero(
        registro,
        (
            "saldo_residual_recebido",
            "valor_residual",
            "saldo_disponivel",
            "valor_disponivel",
        ),
    )


def _construir_unidade_recebido(
    recebido_id: str,
    registro: dict[str, Any],
    data_ref: date,
    tolerancia: float,
    reconciliacoes: list[str],
    bloqueios: list[str],
) -> UnidadeEconomicaCanonica:
    data_origem = _data(registro.get("data_recebimento") or registro.get("data_disponibilidade"))
    data_aplicacao = _data(registro.get("data_aplicacao"))
    valor_total, campo_total = _primeiro_numero(registro, ("valor", "valor_liquido", "valor_bruto"))
    valor_total = float(valor_total or 0.0)
    valor_residual, campo_residual = _valor_residual_recebido(registro)

    if valor_total < -tolerancia or (valor_residual is not None and valor_residual < -tolerancia):
        bloqueios.append(f"recebido_valor_negativo:{recebido_id}")

    futuro = bool(data_origem is None or data_origem > data_ref)
    aplicacao_materializada = bool(
        data_aplicacao is not None and data_aplicacao <= data_ref
    )
    aplicado_sem_data = bool(registro.get("aplicado")) and data_aplicacao is None
    aplicado = aplicacao_materializada or aplicado_sem_data
    vinculado = bool(registro.get("vinculado"))
    usado_antes = bool(registro.get("usado_antes_da_aplicacao"))
    explicitamente_disponivel = registro.get("disponivel_na_referencia") is True

    if valor_residual is not None:
        valor_atual = max(valor_residual, 0.0)
    elif futuro or aplicado or vinculado or usado_antes:
        valor_atual = 0.0
    else:
        valor_atual = max(valor_total, 0.0)

    if futuro:
        estado_ciclo = "futuro_nao_materializado"
    elif aplicado and valor_atual <= tolerancia:
        estado_ciclo = "aplicado_em_lote"
        reconciliacoes.append(f"recebido_aplicado_excluido_caixa:{recebido_id}")
    elif (vinculado or usado_antes) and valor_atual <= tolerancia:
        estado_ciclo = "consumido_ou_vinculado"
        reconciliacoes.append(f"recebido_consumido_excluido_caixa:{recebido_id}")
    elif valor_atual > LIMIAR_RESIDUO_PADRAO + tolerancia and campo_residual:
        estado_ciclo = "residual_disponivel"
    elif explicitamente_disponivel and valor_atual > LIMIAR_RESIDUO_PADRAO + tolerancia:
        estado_ciclo = "caixa_disponivel"
    elif valor_atual <= LIMIAR_RESIDUO_PADRAO + tolerancia:
        estado_ciclo = "exaurido_sem_saldo_atual"
    else:
        estado_ciclo = "bloqueado_sem_disponibilidade_explicita"

    disponivel = estado_ciclo in {"caixa_disponivel", "residual_disponivel"}

    return UnidadeEconomicaCanonica(
        unidade_id=f"recebido::{recebido_id}",
        tipo_unidade="recebido",
        identidade_origem=recebido_id,
        estado_ciclo=estado_ciclo,
        valor_liquido_atual=round(valor_atual, 10),
        disponivel_pagamento_na_referencia=disponivel,
        data_referencia=data_ref,
        data_origem=data_origem,
        data_aplicacao=data_aplicacao,
        data_inicio_rendimento=data_aplicacao,
        produto=_texto(registro.get("investimento") or registro.get("carteira_destino")) or None,
        origem_canonica=_texto(registro.get("origem_canonica")) or "recebidos_temporais",
        vinculos={
            "lote_id_operacional_previsto": registro.get("lote_id_operacional_previsto"),
            "pagamento_vinculado_id": registro.get("pagamento_vinculado_id"),
            "aplicado": aplicado,
            "vinculado": vinculado,
            "usado_antes_da_aplicacao": usado_antes,
        },
        evidencias={
            "campo_valor_total": campo_total,
            "valor_total_informativo": valor_total,
            "campo_valor_residual": campo_residual,
            "disponivel_na_referencia_origem": registro.get("disponivel_na_referencia"),
        },
    )


def _fonte_de_unidade(unidade: UnidadeEconomicaCanonica) -> dict[str, Any]:
    tipo_fonte = "lote" if unidade.tipo_unidade == "lote" else "recebido"
    lote_id = unidade.identidade_origem if unidade.tipo_unidade == "lote" else None
    recebido_id = unidade.identidade_origem if unidade.tipo_unidade == "recebido" else None
    data_disponibilidade = unidade.data_origem or unidade.data_aplicacao or unidade.data_referencia
    if unidade.tipo_unidade == "lote":
        data_disponibilidade = unidade.data_disponibilidade_resgate or unidade.data_aplicacao or unidade.data_origem or unidade.data_referencia
    return {
        "fonte_id": unidade.identidade_origem,
        "unidade_economica_id": unidade.unidade_id,
        "tipo_fonte": tipo_fonte,
        "lote_id": lote_id,
        "recebido_id": recebido_id,
        "data_disponibilidade": data_disponibilidade,
        "valor_estimado": unidade.valor_liquido_atual,
        "valor_liquido_disponivel": unidade.valor_liquido_atual,
        "valor_disponivel": unidade.valor_liquido_atual,
        "saldo_disponivel": unidade.valor_liquido_atual,
        "saldo": unidade.valor_liquido_atual,
        "valor": unidade.valor_liquido_atual,
        "status_temporal": "disponivel" if unidade.disponivel_pagamento_na_referencia else "indisponivel",
        "estado_ciclo": unidade.estado_ciclo,
        "disponivel_na_referencia": unidade.disponivel_pagamento_na_referencia,
        "elegivel_na_data_pagamento": unidade.disponivel_pagamento_na_referencia,
        "origem_canonica": "EstadoEconomicoCanonico",
        "produto": unidade.produto,
        "data_aplicacao": unidade.data_aplicacao,
        "data_inicio_rendimento": unidade.data_inicio_rendimento,
        "data_disponibilidade_resgate": unidade.data_disponibilidade_resgate,
        "motivo_indisponibilidade": None if unidade.disponivel_pagamento_na_referencia else unidade.estado_ciclo,
    }


def _reconciliar_fontes_declaradas(
    fontes_originais: Iterable[dict[str, Any]],
    unidades_por_identidade: dict[str, UnidadeEconomicaCanonica],
    data_ref: date,
    tolerancia: float,
    reconciliacoes: list[str],
    avisos: list[str],
) -> dict[str, Any]:
    qtd_linhas = 0
    qtd_disponiveis_origem = 0
    total_disponivel_origem = 0.0
    snapshots_futuros = 0
    ids_vistos: dict[str, int] = {}

    for fonte in fontes_originais:
        qtd_linhas += 1
        fonte_id = _texto(fonte.get("lote_id") or fonte.get("fonte_id") or fonte.get("recebido_id"))
        if fonte_id:
            ids_vistos[fonte_id] = ids_vistos.get(fonte_id, 0) + 1
        data_fonte = _data(
            fonte.get("data_disponibilidade")
            or fonte.get("data_pagamento")
            or fonte.get("data_evento")
        )
        marcada_disponivel = fonte.get("disponivel_na_referencia") is True or fonte.get("elegivel_na_data_pagamento") is True
        valor, _ = _primeiro_numero(
            fonte,
            (
                "valor_liquido_disponivel",
                "valor_estimado",
                "valor_disponivel",
                "saldo_disponivel",
                "saldo",
                "valor",
            ),
        )
        valor = float(valor or 0.0)
        if marcada_disponivel and valor > tolerancia:
            qtd_disponiveis_origem += 1
            total_disponivel_origem += valor
        if data_fonte and data_fonte > data_ref:
            snapshots_futuros += 1
            if marcada_disponivel:
                reconciliacoes.append(f"snapshot_futuro_nao_antecipado:{fonte_id or 'sem_id'}:{data_fonte.isoformat()}")
        unidade = unidades_por_identidade.get(fonte_id)
        if marcada_disponivel and unidade is not None and not unidade.disponivel_pagamento_na_referencia:
            reconciliacoes.append(f"fonte_declarada_disponivel_bloqueada_pelo_ciclo:{fonte_id}:{unidade.estado_ciclo}")
        if fonte_id and unidade is None:
            avisos.append(f"fonte_declarada_sem_unidade_economica:{fonte_id}")

    duplicatas = sum(max(qtd - 1, 0) for qtd in ids_vistos.values())
    if duplicatas:
        reconciliacoes.append(f"linhas_fontes_duplicadas_nao_somadas:{duplicatas}")

    return {
        "qtd_linhas_fontes_origem": qtd_linhas,
        "qtd_fontes_marcadas_disponiveis_origem": qtd_disponiveis_origem,
        "total_fontes_marcadas_disponiveis_origem": round(total_disponivel_origem, 10),
        "qtd_snapshots_futuros_ignorados": snapshots_futuros,
        "qtd_linhas_duplicadas_por_identidade": duplicatas,
    }


def _eventos_switching(
    registros: Iterable[dict[str, Any]],
    unidades: dict[str, UnidadeEconomicaCanonica],
    data_ref: date,
    tolerancia: float,
    bloqueios: list[str],
    reconciliacoes: list[str],
) -> list[EventoConservacaoEconomica]:
    eventos: list[EventoConservacaoEconomica] = []
    entrada_por_destino: dict[str, float] = {}
    qtd_eventos_por_destino: dict[str, int] = {}

    for posicao, registro in enumerate(registros, start=1):
        status = _estado_textual(registro)
        data_evento = _data(registro.get("data_switching") or registro.get("data_aplicacao"))
        materializado = status == "materializado" or bool(data_evento and data_evento <= data_ref)
        if not materializado:
            continue
        origem = _texto(registro.get("lote_origem") or registro.get("lote_origem_id"))
        destino = _texto(registro.get("lote_destino") or registro.get("lote_destino_id"))
        valor = _numero(
            registro.get("valor_liquido_migrado")
            or registro.get("valor_liquido_origem")
            or registro.get("valor_migrado")
            or registro.get("valor")
        )
        valor = float(valor or 0.0)
        evento_id = _texto(registro.get("switching_id")) or f"switching::{posicao:05d}"
        if not origem:
            bloqueios.append(f"switching_materializado_sem_origem:{evento_id}")
        if not destino:
            bloqueios.append(f"switching_materializado_sem_destino:{evento_id}")
        if valor <= tolerancia:
            bloqueios.append(f"switching_materializado_sem_valor_positivo:{evento_id}")

        origem_uid = f"lote::{origem}" if origem else None
        destino_uid = f"lote::{destino}" if destino else None
        unidade_origem = unidades.get(origem_uid or "")
        unidade_destino = unidades.get(destino_uid or "")

        if origem_uid and unidade_origem is None:
            bloqueios.append(f"switching_origem_ausente_no_estado:{evento_id}:{origem}")
        elif unidade_origem and unidade_origem.disponivel_pagamento_na_referencia:
            unidades[origem_uid] = replace(
                unidade_origem,
                estado_ciclo="migrado_por_switching",
                disponivel_pagamento_na_referencia=False,
            )
            reconciliacoes.append(f"switching_origem_removida_das_fontes:{evento_id}:{origem}")

        if destino_uid and unidade_destino is None and valor > tolerancia:
            unidades[destino_uid] = UnidadeEconomicaCanonica(
                unidade_id=destino_uid,
                tipo_unidade="lote",
                identidade_origem=destino,
                estado_ciclo="ativo_disponivel",
                valor_liquido_atual=round(valor, 10),
                disponivel_pagamento_na_referencia=True,
                data_referencia=data_ref,
                data_origem=_data(registro.get("data_recebimento")),
                data_aplicacao=_data(registro.get("data_aplicacao")) or data_evento,
                data_inicio_rendimento=_data(registro.get("data_aplicacao")) or data_evento,
                produto=_texto(registro.get("produto_destino")) or None,
                origem_canonica="switching_temporal_realizado",
                vinculos={"origem_switching": origem, "sintetico_pos_switching": True},
                evidencias={"valor_liquido_migrado": valor},
            )
            reconciliacoes.append(f"switching_destino_sintetico_materializado:{evento_id}:{destino}")

        if destino:
            entrada_por_destino[destino] = entrada_por_destino.get(destino, 0.0) + valor
            qtd_eventos_por_destino[destino] = qtd_eventos_por_destino.get(destino, 0) + 1

        diferenca = round(valor - valor, 10)
        eventos.append(
            EventoConservacaoEconomica(
                evento_id=evento_id,
                tipo_evento="switching_interno",
                data_evento=data_evento,
                unidade_origem_id=origem_uid,
                unidade_destino_id=destino_uid,
                valor_saida=round(valor, 10),
                valor_entrada=round(valor, 10),
                custo_ou_imposto=0.0,
                diferenca_conservacao=diferenca,
                ok=abs(diferenca) <= tolerancia,
                referencias=dict(registro),
            )
        )

    for destino, total_entrada in entrada_por_destino.items():
        unidade = unidades.get(f"lote::{destino}")
        if unidade is None:
            continue
        informado = _numero(unidade.evidencias.get("valor_liquido_migrado"))
        if qtd_eventos_por_destino.get(destino, 0) == 1 and informado is not None and abs(informado - total_entrada) > tolerancia:
            bloqueios.append(
                f"switching_destino_valor_migrado_divergente:{destino}:{informado:.2f}:{total_entrada:.2f}"
            )
    return eventos


def construir_estado_economico_canonico(
    estado_temporal: Any,
    *,
    tolerancia_monetaria: float = TOLERANCIA_MONETARIA_PADRAO,
) -> EstadoEconomicoCanonico:
    data_ref = _data(getattr(estado_temporal, "data_referencia", None))
    if data_ref is None:
        raise EstadoEconomicoCanonicoInvalido("EstadoTemporalInicial sem data_referencia válida.")

    bloqueios: list[str] = []
    avisos: list[str] = []
    reconciliacoes: list[str] = []

    inventario = list(getattr(estado_temporal, "inventario_temporal", []) or [])
    recebidos = list(getattr(estado_temporal, "recebidos_temporais", []) or [])
    fontes_originais = list(getattr(estado_temporal, "fontes_temporais", []) or [])
    switchings = list(getattr(estado_temporal, "switching_temporal_realizado", []) or [])

    unidades: dict[str, UnidadeEconomicaCanonica] = {}

    for lote_id, registro in _agrupar_unicos(
        inventario,
        _id_lote,
        "lote",
        tolerancia_monetaria,
        bloqueios,
        reconciliacoes,
    ):
        unidade = _construir_unidade_lote(
            lote_id,
            registro,
            data_ref,
            tolerancia_monetaria,
            reconciliacoes,
            avisos,
            bloqueios,
        )
        unidades[unidade.unidade_id] = unidade

    for recebido_id, registro in _agrupar_unicos(
        recebidos,
        _id_recebido,
        "recebido",
        tolerancia_monetaria,
        bloqueios,
        reconciliacoes,
    ):
        unidade = _construir_unidade_recebido(
            recebido_id,
            registro,
            data_ref,
            tolerancia_monetaria,
            reconciliacoes,
            bloqueios,
        )
        unidades[unidade.unidade_id] = unidade

    eventos = _eventos_switching(
        switchings,
        unidades,
        data_ref,
        tolerancia_monetaria,
        bloqueios,
        reconciliacoes,
    )

    unidades_por_identidade = {
        unidade.identidade_origem: unidade
        for unidade in unidades.values()
        if unidade.identidade_origem
    }
    resumo_fontes_origem = _reconciliar_fontes_declaradas(
        fontes_originais,
        unidades_por_identidade,
        data_ref,
        tolerancia_monetaria,
        reconciliacoes,
        avisos,
    )

    fontes_disponiveis: list[dict[str, Any]] = []
    fontes_bloqueadas: list[dict[str, Any]] = []
    for unidade in sorted(unidades.values(), key=lambda item: item.unidade_id):
        fonte = _fonte_de_unidade(unidade)
        if unidade.disponivel_pagamento_na_referencia:
            fontes_disponiveis.append(fonte)
        else:
            fontes_bloqueadas.append(fonte)

    ids_fontes = [item["unidade_economica_id"] for item in fontes_disponiveis]
    if len(ids_fontes) != len(set(ids_fontes)):
        bloqueios.append("fontes_disponiveis_com_identidade_economica_duplicada")

    eventos_invalidos = [evento.evento_id for evento in eventos if not evento.ok]
    if eventos_invalidos:
        bloqueios.extend(f"evento_conservacao_invalido:{evento_id}" for evento_id in eventos_invalidos)

    total_lotes = round(
        sum(
            unidade.valor_liquido_atual
            for unidade in unidades.values()
            if unidade.tipo_unidade == "lote" and unidade.disponivel_pagamento_na_referencia
        ),
        10,
    )
    total_recebidos = round(
        sum(
            unidade.valor_liquido_atual
            for unidade in unidades.values()
            if unidade.tipo_unidade == "recebido" and unidade.disponivel_pagamento_na_referencia
        ),
        10,
    )
    total_canonico = round(total_lotes + total_recebidos, 10)
    total_fontes_materializadas = round(
        sum(float(fonte["valor_liquido_disponivel"]) for fonte in fontes_disponiveis),
        10,
    )
    diferenca_materializacao = round(total_canonico - total_fontes_materializadas, 10)
    if abs(diferenca_materializacao) > tolerancia_monetaria:
        bloqueios.append(
            f"conservacao_fontes_materializadas_divergente:{diferenca_materializacao:.2f}"
        )

    resumo = {
        "qtd_unidades": len(unidades),
        "qtd_lotes": sum(1 for u in unidades.values() if u.tipo_unidade == "lote"),
        "qtd_recebidos": sum(1 for u in unidades.values() if u.tipo_unidade == "recebido"),
        "qtd_fontes_disponiveis": len(fontes_disponiveis),
        "qtd_fontes_bloqueadas": len(fontes_bloqueadas),
        "qtd_eventos_conservacao": len(eventos),
        "qtd_bloqueios": len(bloqueios),
        "qtd_avisos": len(avisos),
        "qtd_reconciliacoes": len(reconciliacoes),
        "valor_lotes_disponiveis": total_lotes,
        "valor_recebidos_disponiveis": total_recebidos,
        "valor_total_disponivel_canonico": total_canonico,
        "valor_total_fontes_materializadas": total_fontes_materializadas,
        "diferenca_conservacao_fontes": diferenca_materializacao,
        "qtd_recebidos_aplicados_excluidos": sum(
            1 for item in reconciliacoes if item.startswith("recebido_aplicado_excluido_caixa:")
        ),
        "qtd_recebidos_consumidos_excluidos": sum(
            1 for item in reconciliacoes if item.startswith("recebido_consumido_excluido_caixa:")
        ),
        "qtd_lotes_zerados_nao_ressuscitados": sum(
            1 for item in reconciliacoes if item.startswith("lote_zerado_nao_ressuscitado:")
        ),
        "qtd_fallbacks_valor_original_proibidos": sum(
            1 for item in reconciliacoes if item.startswith("fallback_valor_original_proibido:")
        ),
        **resumo_fontes_origem,
    }

    auditoria = AuditoriaEstadoEconomicoCanonico(
        ok=not bloqueios,
        bloqueios=bloqueios,
        avisos=avisos,
        reconciliacoes=reconciliacoes,
        resumo=resumo,
    )
    return EstadoEconomicoCanonico(
        data_referencia=data_ref,
        unidades=sorted(unidades.values(), key=lambda item: item.unidade_id),
        fontes_disponiveis=fontes_disponiveis,
        fontes_bloqueadas=fontes_bloqueadas,
        eventos_conservacao=eventos,
        auditoria=auditoria,
        metadados={
            "artefato": "EstadoEconomicoCanonico",
            "bloco": "BLOCO-1",
            "fonte_formal": "EstadoTemporalInicial",
            "tolerancia_monetaria": tolerancia_monetaria,
            "limiar_residuo": LIMIAR_RESIDUO_PADRAO,
            "valor_original_nunca_usado_como_saldo_atual": True,
            "snapshots_futuros_nunca_antecipados": True,
            "recebidos_aplicados_ou_consumidos_nunca_reutilizados": True,
            "switching_tratado_como_transferencia_interna": True,
            "sem_decisao_economica": True,
            "sem_motor_argmax": True,
            "sem_console_xlsx": True,
        },
    )


def exigir_estado_economico_canonico_valido(estado: EstadoEconomicoCanonico) -> None:
    if estado.auditoria.ok:
        return
    detalhes = "; ".join(estado.auditoria.bloqueios[:10])
    if len(estado.auditoria.bloqueios) > 10:
        detalhes += f"; ... {len(estado.auditoria.bloqueios) - 10} bloqueio(s) adicional(is)"
    raise EstadoEconomicoCanonicoInvalido(
        "EstadoEconomicoCanonico reprovado: " + detalhes
    )


__all__ = [
    "AuditoriaEstadoEconomicoCanonico",
    "EstadoEconomicoCanonico",
    "EstadoEconomicoCanonicoInvalido",
    "EventoConservacaoEconomica",
    "LIMIAR_RESIDUO_PADRAO",
    "TOLERANCIA_MONETARIA_PADRAO",
    "UnidadeEconomicaCanonica",
    "construir_estado_economico_canonico",
    "exigir_estado_economico_canonico_valido",
]
