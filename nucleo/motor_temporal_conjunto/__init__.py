from __future__ import annotations

import importlib.util
import math
import sys
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

LEGACY_NAME = "nucleo._motor_temporal_conjunto_legacy"
LEGACY_PATH = Path(__file__).resolve().parents[1] / "motor_temporal_conjunto.py"
PACOTES_SEM_PAGAMENTO = ("no_action", "switch_only")
PACOTES_COM_PAGAMENTO = ("pay_only", "switch_then_pay", "pay_then_switch")
TOL = 1e-7


def _carregar_legado():
    if LEGACY_NAME in sys.modules:
        return sys.modules[LEGACY_NAME]
    spec = importlib.util.spec_from_file_location(LEGACY_NAME, LEGACY_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Módulo legado não encontrado: {LEGACY_PATH}")
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[LEGACY_NAME] = modulo
    spec.loader.exec_module(modulo)
    return modulo


_legacy = _carregar_legado()
for _nome in getattr(_legacy, "__all__", []):
    globals()[_nome] = getattr(_legacy, _nome)


@dataclass(slots=True)
class ValoracaoEconomicaPacote:
    valor_obrigacoes: float
    valor_cobertura_referencial: float
    valor_descoberto_referencial: float
    cobertura_integral_referencial: bool
    penalidade_bloqueio: float
    penalidade_status: float
    penalidade_switching: float
    score_referencial: float
    patrimonio_terminal_liquido: float
    delta_patrimonio_terminal: float
    qtd_switchings: int
    qtd_fontes_pagamento: int
    factivel: bool


@dataclass(slots=True)
class _Fonte:
    id: str
    saldo: float
    disponivel_em: date
    tipo: str
    produto: str
    retorno: float
    carencia_ate: date | None
    vencimento: date | None
    base_fiscal: date | None
    isento_ir: bool
    regra_iof: str
    switch_out: bool
    ref: dict[str, Any]


@dataclass(slots=True)
class _Trajetoria:
    tipo: str
    factivel: bool
    motivos: list[str]
    fontes: dict[str, _Fonte]
    saldos: dict[str, float]
    alocacoes: list[dict[str, Any]]
    switchings: list[dict[str, Any]]
    patrimonio_terminal: float
    obrigacoes: float
    coberto: float
    estado_inicial_id: str


def _texto(*valores: Any) -> str:
    for valor in valores:
        txt = str(valor or "").strip()
        if txt and txt.casefold() not in {"nan", "none", "n/d", "nd"}:
            return txt
    return ""


def _numero(*valores: Any, padrao: float = 0.0) -> float:
    for valor in valores:
        if valor in (None, "") or isinstance(valor, bool):
            continue
        try:
            n = float(valor)
        except (TypeError, ValueError):
            continue
        if math.isfinite(n):
            return n
    return float(padrao)


def _positivo(*valores: Any) -> float:
    for valor in valores:
        n = _numero(valor, padrao=float("nan"))
        if math.isfinite(n) and n > 0:
            return n
    return 0.0


def _data(*valores: Any) -> date | None:
    for valor in valores:
        if isinstance(valor, date):
            return valor
        if isinstance(valor, str):
            try:
                return date.fromisoformat(valor[:10])
            except ValueError:
                pass
    return None


def _bool(valor: Any, padrao: bool = False) -> bool:
    if isinstance(valor, bool):
        return valor
    txt = str(valor or "").strip().casefold()
    if txt in {"sim", "s", "true", "1", "yes", "isento"}:
        return True
    if txt in {"nao", "não", "n", "false", "0", "no"}:
        return False
    return padrao


def _taxa(valor: Any) -> float:
    n = _numero(valor)
    return max(n / 100.0 if abs(n) > 3 else n, -0.99)


def _status_bloqueado(item: dict[str, Any]) -> bool:
    status = _texto(
        item.get("status_temporal"), item.get("status_recebido"),
        item.get("status_inventario_temporal"), item.get("status_ciclo"),
    ).casefold()
    return any(x in status for x in ("exaurido", "migrado", "indisponivel", "indisponível", "bloqueado"))


def _fonte(item: dict[str, Any], pos: int, data_ref: date, prefixo: str) -> _Fonte | None:
    if _status_bloqueado(item):
        return None
    saldo = _positivo(
        item.get("valor_liquido_disponivel"), item.get("valor_estimado"),
        item.get("valor_disponivel"), item.get("saldo_disponivel"),
        item.get("saldo"), item.get("valor"),
        item.get("valor_liquido_disponivel_atual"),
        item.get("saldo_disponivel_atual"), item.get("valor_original"),
    )
    if saldo <= 0:
        return None
    fid = _texto(item.get("fonte_id"), item.get("recebido_id"), item.get("lote_id"), item.get("id")) or f"{prefixo}:{pos:05d}"
    disponivel = _data(item.get("data_disponibilidade"), item.get("data_recebimento"), item.get("data_aplicacao"), item.get("data"), data_ref) or data_ref
    liquidez = max(int(round(_numero(item.get("liquidez_dias")))), 0)
    carencia = _data(item.get("carencia_ate"), item.get("data_fim_carencia"))
    if carencia is None and liquidez > 0:
        carencia = disponivel + timedelta(days=liquidez)
    return _Fonte(
        id=fid, saldo=round(saldo, 10), disponivel_em=disponivel,
        tipo=_texto(item.get("tipo_fonte"), item.get("tipo_lote_operacional"), prefixo),
        produto=_texto(item.get("produto"), item.get("investimento"), item.get("carteira_destino")),
        retorno=_taxa(item.get("retorno_anual_proxy")), carencia_ate=carencia,
        vencimento=_data(item.get("data_vencimento"), item.get("vencimento")),
        base_fiscal=_data(item.get("data_base_fiscal"), item.get("data_aplicacao"), item.get("data_recebimento"), disponivel),
        isento_ir=_bool(item.get("isento_ir")), regra_iof=_texto(item.get("regra_iof"), "regressiva_30d"),
        switch_out=item.get("elegivel_switch_out") is not False, ref=dict(item),
    )


def _fontes_estado(estado: Any) -> dict[str, _Fonte]:
    candidatos: list[_Fonte] = []
    grupos = (
        (getattr(estado, "fontes_temporais", []), "fonte"),
        (getattr(estado, "recebidos_temporais", []), "recebido"),
        (getattr(estado, "inventario_temporal", []), "inventario"),
    )
    pos = 0
    for itens, prefixo in grupos:
        for item in list(itens or []):
            pos += 1
            reg = dict(item)
            if prefixo == "inventario":
                reg.setdefault("fonte_id", reg.get("lote_id"))
            f = _fonte(reg, pos, estado.data_referencia, prefixo)
            if f:
                candidatos.append(f)
    saida: dict[str, _Fonte] = {}
    for f in candidatos:
        atual = saida.get(f.id)
        if atual is None:
            saida[f.id] = f
            continue
        ref = dict(atual.ref); ref.update(f.ref)
        saida[f.id] = _Fonte(
            id=f.id, saldo=max(atual.saldo, f.saldo),
            disponivel_em=min(atual.disponivel_em, f.disponivel_em),
            tipo=f.tipo or atual.tipo, produto=f.produto or atual.produto,
            retorno=f.retorno if abs(f.retorno) > TOL else atual.retorno,
            carencia_ate=f.carencia_ate or atual.carencia_ate,
            vencimento=f.vencimento or atual.vencimento,
            base_fiscal=f.base_fiscal or atual.base_fiscal,
            isento_ir=f.isento_ir or atual.isento_ir,
            regra_iof=f.regra_iof or atual.regra_iof,
            switch_out=f.switch_out and atual.switch_out, ref=ref,
        )
    return saida


def _destinos(estado: Any) -> list[dict[str, Any]]:
    itens = list((getattr(estado, "metadados", {}) or {}).get("destinos_switching", []) or [])
    out = []
    for i, item in enumerate(itens, 1):
        nome = _texto(item.get("nome"), item.get("produto"))
        if nome and item.get("elegivel_switch_in") is not False:
            out.append({
                "rank": int(round(_numero(item.get("rank_destino"), padrao=i))),
                "nome": nome, "retorno": _taxa(item.get("retorno_anual_proxy")),
                "liquidez": max(int(round(_numero(item.get("liquidez_dias")))), 0),
                "carencia": max(int(round(_numero(item.get("carencia_dias")))), 0),
                "minimo": max(_numero(item.get("aplicacao_minima")), 0.0),
                "maximo": max(_numero(item.get("aplicacao_maxima")), 0.0),
                "isento_ir": _bool(item.get("isento_ir")),
                "regra_iof": _texto(item.get("regra_iof"), "regressiva_30d"),
            })
    return sorted(out, key=lambda x: (x["rank"], -x["retorno"], x["nome"]))


def _ir(dias: int, isento: bool) -> float:
    if isento: return 0.0
    if dias <= 180: return 0.225
    if dias <= 360: return 0.20
    if dias <= 720: return 0.175
    return 0.15


def _iof(dias: int, regra: str) -> float:
    if dias >= 30 or "nao_incide" in str(regra).casefold(): return 0.0
    return max(min((30 - max(dias, 1)) / 30.0, 0.96), 0.0)


def _valor_terminal(f: _Fonte, saldo: float, hoje: date, horizonte: date) -> float:
    inicio = max(hoje, f.disponivel_em)
    fim = min(horizonte, f.vencimento) if f.vencimento else horizonte
    fim = max(fim, inicio)
    dias = max((fim - inicio).days, 0)
    bruto = saldo * (1 + max(f.retorno, -0.99)) ** (dias / 365.0)
    ganho = max(bruto - saldo, 0.0)
    dias_fiscais = max((fim - (f.base_fiscal or inicio)).days, 0)
    imposto_iof = ganho * _iof(dias_fiscais, f.regra_iof)
    imposto_ir = max(ganho - imposto_iof, 0.0) * _ir(dias_fiscais, f.isento_ir)
    return saldo + ganho - imposto_iof - imposto_ir


def _patrimonio(fontes: dict[str, _Fonte], saldos: dict[str, float], hoje: date, horizonte: date) -> float:
    return round(sum(_valor_terminal(fontes[k], v, hoje, horizonte) for k, v in saldos.items() if v > TOL), 10)


def _liquida(f: _Fonte, dia: date) -> bool:
    return bool((f.vencimento and f.vencimento <= dia) or (f.disponivel_em <= dia and (f.carencia_ate is None or f.carencia_ate <= dia)))


def _estado_id(dia: date, saldos: dict[str, float]) -> str:
    partes = [f"{k}:{v:.6f}" for k, v in sorted(saldos.items()) if v > TOL]
    return f"{dia.isoformat()}::" + "|".join(partes)


def _obrigacoes(resultado: Any, dia: date) -> list[dict[str, Any]]:
    estado_dia = (getattr(resultado, "estado_diario_motor", {}) or {}).get(dia)
    if estado_dia is None: return []
    return [dict(x) for x in estado_dia.obrigacoes.pagamentos_referenciados if x.get("pago") is not True]


def _valor_obrigacao(o: dict[str, Any]) -> float:
    return max(_numero(o.get("valor"), o.get("valor_pagamento"), o.get("valor_obrigacao")), 0.0)


def _id_obrigacao(o: dict[str, Any], i: int) -> str:
    return _texto(o.get("obrigacao_id"), o.get("pagamento_id"), o.get("id")) or f"obrigacao:{i:05d}"


def _ativar(defs: dict[str, _Fonte], fontes: dict[str, _Fonte], saldos: dict[str, float], dia: date) -> None:
    for fid, f in defs.items():
        if fid not in fontes and f.disponivel_em <= dia:
            fontes[fid] = deepcopy(f); saldos[fid] = f.saldo


def _alocar(fontes: dict[str, _Fonte], saldos0: dict[str, float], obs: list[dict[str, Any]], dia: date, horizonte: date):
    saldos = dict(saldos0)
    ordem = sorted(
        [k for k, v in saldos.items() if v > TOL and _liquida(fontes[k], dia)],
        key=lambda k: (_valor_terminal(fontes[k], 1.0, dia, horizonte), fontes[k].retorno, k),
    )
    alocacoes, motivos = [], []
    for i, o in enumerate(obs, 1):
        valor, restante, detalhes = _valor_obrigacao(o), _valor_obrigacao(o), []
        oid = _id_obrigacao(o, i)
        for fid in ordem:
            if restante <= TOL: break
            antes = saldos.get(fid, 0.0)
            if antes <= TOL: continue
            uso = min(antes, restante); depois = max(antes - uso, 0.0)
            saldos[fid] = depois; restante -= uso
            detalhes.append({"fonte_id": fid, "saldo_antes": antes, "consumo": uso, "saldo_depois": depois, "referencia": dict(fontes[fid].ref)})
        alocacoes.append({"obrigacao": dict(o), "obrigacao_id": oid, "valor_obrigacao": valor, "valor_coberto": max(valor-restante, 0.0), "detalhes": detalhes})
        if restante > 0.01:
            motivos.append(f"saldo_temporal_insuficiente:{oid}:{restante:.2f}")
            return False, motivos, saldos, alocacoes
    return True, motivos, saldos, alocacoes


def _melhor_destino(f: _Fonte, saldo: float, destinos: list[dict[str, Any]], dia: date, horizonte: date):
    origem = _valor_terminal(f, 1.0, dia, horizonte)
    candidatos = []
    for d in destinos:
        if saldo + 0.01 < d["minimo"] or (d["maximo"] > 0 and saldo - 0.01 > d["maximo"]): continue
        if f.produto and f.produto.casefold() == d["nome"].casefold(): continue
        novo = _Fonte("destino", saldo, dia+timedelta(days=max(d["liquidez"], d["carencia"])), "destino", d["nome"], d["retorno"], dia+timedelta(days=d["carencia"]) if d["carencia"] else None, None, dia, d["isento_ir"], d["regra_iof"], True, d)
        ganho = saldo * (_valor_terminal(novo, 1.0, dia, horizonte) - origem)
        if ganho > 0.01: candidatos.append((-ganho, d["rank"], d["nome"], d))
    return sorted(candidatos, key=lambda x: (x[0], x[1], x[2]))[0][3] if candidatos else None


def _switch(fontes0: dict[str, _Fonte], saldos0: dict[str, float], destinos: list[dict[str, Any]], dia: date, horizonte: date, preservar: set[str] | None = None):
    fontes, saldos, eventos = deepcopy(fontes0), dict(saldos0), []
    for fid in sorted(saldos):
        f, saldo = fontes.get(fid), saldos.get(fid, 0.0)
        if not f or saldo <= TOL or not f.switch_out: continue
        d = _melhor_destino(f, saldo, destinos, dia, horizonte)
        if not d: continue
        imediato = d["liquidez"] <= 0 and d["carencia"] <= 0
        if fid in (preservar or set()) and not imediato: continue
        novo_id = f"switch:{dia.isoformat()}:{fid}:{d['rank']}"
        novo = _Fonte(novo_id, saldo, dia+timedelta(days=max(d["liquidez"], d["carencia"])), "lote_sintetico_pos_switching", d["nome"], d["retorno"], dia+timedelta(days=d["carencia"]) if d["carencia"] else None, None, dia, d["isento_ir"], d["regra_iof"], True, {"fonte_id":novo_id,"lote_id":novo_id,"lote_origem":fid,"lote_destino":novo_id,"produto_origem":f.produto,"produto_destino":d["nome"],"valor_liquido_migrado":saldo,"data_switching":dia,"data_aplicacao":dia,"status_temporal":"materializado","rank_destino":d["rank"]})
        saldos[fid]=0.0; fontes[novo_id]=novo; saldos[novo_id]=saldo
        eventos.append({"switching_id":f"sw:{dia.isoformat()}:{len(eventos)+1:04d}","lote_origem":fid,"lote_destino":novo_id,"produto_origem":f.produto,"produto_destino":d["nome"],"valor_liquido_migrado":saldo,"data_switching":dia,"data_aplicacao":dia,"rank_destino":d["rank"]})
    return fontes, saldos, eventos


def _trajetoria(tipo: str, fontes0: dict[str, _Fonte], saldos0: dict[str, float], obs: list[dict[str, Any]], destinos: list[dict[str, Any]], dia: date, horizonte: date) -> _Trajetoria:
    fontes, saldos = deepcopy(fontes0), dict(saldos0)
    alocacoes, switchings, motivos = [], [], []
    total = sum(_valor_obrigacao(o) for o in obs); coberto = 0.0
    factivel = True
    if tipo == "no_action": factivel = not obs; motivos += ["no_action_proibido_com_pagamento"] if obs else []
    elif tipo == "switch_only":
        factivel = not obs; motivos += ["switch_only_proibido_com_pagamento"] if obs else []
        if factivel: fontes, saldos, switchings = _switch(fontes, saldos, destinos, dia, horizonte)
    elif tipo == "pay_only": factivel, motivos, saldos, alocacoes = _alocar(fontes, saldos, obs, dia, horizonte)
    elif tipo == "switch_then_pay":
        _, _, _, base = _alocar(fontes, saldos, obs, dia, horizonte)
        preservar = {d["fonte_id"] for a in base for d in a["detalhes"]}
        fontes, saldos, switchings = _switch(fontes, saldos, destinos, dia, horizonte, preservar)
        factivel, motivos, saldos, alocacoes = _alocar(fontes, saldos, obs, dia, horizonte)
    elif tipo == "pay_then_switch":
        factivel, motivos, saldos, alocacoes = _alocar(fontes, saldos, obs, dia, horizonte)
        if factivel: fontes, saldos, switchings = _switch(fontes, saldos, destinos, dia, horizonte)
    else: factivel=False; motivos=[f"tipo_pacote_desconhecido:{tipo}"]
    coberto = sum(a["valor_coberto"] for a in alocacoes)
    patrimonio = _patrimonio(fontes, saldos, dia, horizonte) if factivel else float("-inf")
    return _Trajetoria(tipo, factivel, motivos, fontes, saldos, alocacoes, switchings, patrimonio, total, coberto, _estado_id(dia, saldos0))


def _fonte_candidata(f: _Fonte):
    return _legacy.FonteCandidataPacoteTemporal(fonte_id=f.id, tipo_fonte=f.tipo, origem_fonte=_texto(f.ref.get("origem_canonica"), f.tipo), referencia_estado_temporal=dict(f.ref))


def _pacote(t: _Trajetoria, dia: date):
    usados = sorted({d["fonte_id"] for a in t.alocacoes for d in a["detalhes"]})
    trans = []
    if t.switchings: trans.append(_legacy.TransicaoCandidataPacoteTemporal("switching_integral", "materializado_na_trajetoria_candidata", {"qtd":len(t.switchings)}))
    if t.alocacoes: trans.append(_legacy.TransicaoCandidataPacoteTemporal("pagamento_integral", "materializado_na_trajetoria_candidata", {"qtd":len(t.alocacoes)}))
    return _legacy.PacoteTemporalCandidato(
        pacote_id=f"{dia.isoformat()}::{t.tipo}::1", data_referencia=dia, tipo_pacote=t.tipo,
        obrigacoes_referenciadas=[dict(a["obrigacao"]) for a in t.alocacoes],
        fontes_candidatas=[_fonte_candidata(t.fontes[f]) for f in usados if f in t.fontes],
        switchings_candidatos=[_legacy.SwitchingCandidatoPacoteTemporal(switching_id=s["switching_id"], lote_origem_id=s["lote_origem"], lote_destino_id=s["lote_destino"], tipo_switching="integral", referencia_estado_temporal=dict(s)) for s in t.switchings],
        transicoes_candidatas=trans, status_factibilidade="factivel_referencialmente" if t.factivel else "bloqueado_estruturalmente",
        motivos_bloqueio=list(t.motivos), valor_obrigacoes=t.obrigacoes, valor_cobertura_referencial=t.coberto,
        metadados_auditoria={"funcao_objetivo":"patrimonio_liquido_terminal_liquido","patrimonio_terminal_liquido":t.patrimonio_terminal if t.factivel else None,"estado_inicial_id":t.estado_inicial_id,"comparado_no_mesmo_estado":True,"ordem_intradiaria":t.tipo,"alocacoes_pagamento":deepcopy(t.alocacoes),"switchings_planejados":deepcopy(t.switchings),"saldos_finais":dict(t.saldos)},
    )


def _valorado(p: Any, baseline: float):
    ok = p.status_factibilidade == "factivel_referencialmente"
    patrimonio = _numero(p.metadados_auditoria.get("patrimonio_terminal_liquido"), padrao=float("-inf"))
    v = ValoracaoEconomicaPacote(float(p.valor_obrigacoes or 0), float(p.valor_cobertura_referencial or 0), max(float(p.valor_obrigacoes or 0)-float(p.valor_cobertura_referencial or 0),0), ok and float(p.valor_cobertura_referencial or 0)+0.01>=float(p.valor_obrigacoes or 0), 0.0 if ok else float("inf"), 0.0 if ok else float("inf"), 0.0, patrimonio, patrimonio, patrimonio-baseline if ok else float("-inf"), len(p.switchings_candidatos), len(p.fontes_candidatas), ok)
    return _legacy.PacoteTemporalValorado(pacote_candidato=p, valoracao=v, valido_no_schema=True)


def _argmax(valorados: list[Any]):
    validos = [v for v in valorados if v.valoracao.factivel]
    return min(validos, key=lambda v:(-v.valoracao.patrimonio_terminal_liquido,v.valoracao.qtd_switchings,v.valoracao.qtd_fontes_pagamento,v.pacote_candidato.pacote_id)) if validos else None


def _materializar(dia: date, pacote: Any | None, t: _Trajetoria | None):
    if pacote is None or t is None:
        estado = _legacy.EstadoTemporalInternoDia(data=dia,pacote_id=None,tipo_pacote=None,status_referencial="bloqueado_referencialmente",eventos_internos=[],saldos_fontes_referenciais=[],fontes_reservadas=[],obrigacoes_cobertas=[],obrigacoes_bloqueadas=[],switchings_escolhidos=[],alertas=["sem_pacote_factivel"])
        return estado, [], [], [], []
    evento = _legacy.EventoTrajetoriaTemporalInterna(data=dia,tipo_evento_interno="pacote_normativo_materializado",pacote_id=pacote.pacote_id,tipo_pacote=pacote.tipo_pacote,status_referencial="materializado_no_estado_temporal",detalhes={"patrimonio_terminal_liquido":t.patrimonio_terminal,"estado_inicial_id":t.estado_inicial_id,"qtd_alocacoes":len(t.alocacoes),"qtd_switchings":len(t.switchings)})
    reservas, cobertas = [], []
    for a in t.alocacoes:
        detalhes=[]
        for d in a["detalhes"]:
            ref=dict(d["referencia"]); lote=_texto(ref.get("lote_id_operacional"),ref.get("lote_id_operacional_previsto"),ref.get("lote_id"),d["fonte_id"])
            reservas.append(_legacy.FonteReservadaTemporalmente(data=dia,fonte_id=d["fonte_id"],pacote_id=pacote.pacote_id,tipo_fonte=_texto(ref.get("tipo_fonte"),"fonte"),origem_fonte=_texto(ref.get("origem_canonica"),"motor_funcional"),valor_reservado_referencial=d["consumo"],valor_disponivel_antes_referencial=d["saldo_antes"],valor_disponivel_depois_referencial=d["saldo_depois"],obrigacao_id=a["obrigacao_id"],referencia_estado_temporal=ref,fonte_id_tecnico=d["fonte_id"],lote_id_operacional=lote,saldo_antes_fonte=d["saldo_antes"],valor_bruto_resgate="nao_materializado",imposto_resgate="nao_materializado",valor_liquido_resgate=d["consumo"],saldo_remanescente_fonte=d["saldo_depois"],status_saldo_antes_fonte="materializado",status_valor_bruto_resgate="nao_materializado",status_imposto_resgate="nao_materializado",status_valor_liquido_resgate="materializado",status_saldo_remanescente_fonte="materializado"))
            detalhes.append({"fonte_id":d["fonte_id"],"saldo_antes_fonte":d["saldo_antes"],"valor_bruto_resgate":"nao_materializado","imposto_resgate":"nao_materializado","valor_liquido_resgate":d["consumo"],"saldo_remanescente_fonte":d["saldo_depois"],"status_saldo_antes_fonte":"materializado","status_valor_bruto_resgate":"nao_materializado","status_imposto_resgate":"nao_materializado","status_valor_liquido_resgate":"materializado","status_saldo_remanescente_fonte":"materializado"})
        cobertas.append(_legacy.ObrigacaoCobertaTemporalmente(data=dia,obrigacao_id=a["obrigacao_id"],pacote_id=pacote.pacote_id,valor_obrigacao_referencial=a["valor_obrigacao"],valor_coberto_referencial=a["valor_coberto"],fontes_reservadas_ids=[d["fonte_id"] for d in a["detalhes"]],referencia_obrigacao_temporal=dict(a["obrigacao"]),detalhes_fontes_resgate=detalhes,saldo_antes_fonte=sum(_numero(d["saldo_antes_fonte"]) for d in detalhes),valor_bruto_resgate="nao_materializado",imposto_resgate="nao_materializado",valor_liquido_resgate=sum(_numero(d["valor_liquido_resgate"]) for d in detalhes),saldo_remanescente_fonte=sum(_numero(d["saldo_remanescente_fonte"]) for d in detalhes),status_saldo_antes_fonte="materializado",status_valor_bruto_resgate="nao_materializado",status_imposto_resgate="nao_materializado",status_valor_liquido_resgate="materializado",status_saldo_remanescente_fonte="materializado"))
    sw=[_legacy.SwitchingEscolhidoTemporalmente(data=dia,switching_id=s["switching_id"],pacote_id=pacote.pacote_id,lote_origem_id=s["lote_origem"],lote_destino_id=s["lote_destino"],tipo_switching="integral",status_referencial="escolhido_internamente_nao_executado",referencia_estado_temporal=dict(s)) for s in t.switchings]
    saldos=[_legacy.SaldoReferencialFonteTemporal(data=dia,fonte_id=fid,valor_disponivel_referencial=saldo,valor_reservado_acumulado_referencial=sum(d["consumo"] for a in t.alocacoes for d in a["detalhes"] if d["fonte_id"]==fid)) for fid,saldo in sorted(t.saldos.items())]
    estado=_legacy.EstadoTemporalInternoDia(data=dia,pacote_id=pacote.pacote_id,tipo_pacote=pacote.tipo_pacote,status_referencial="materializado_referencialmente",eventos_internos=[evento],saldos_fontes_referenciais=saldos,fontes_reservadas=reservas,obrigacoes_cobertas=cobertas,obrigacoes_bloqueadas=[],switchings_escolhidos=sw,alertas=[])
    return estado,[evento],reservas,cobertas,sw


def construir_resultado_motor_temporal_conjunto(estado: Any, parametros: Any | None = None) -> Any:
    params = deepcopy(parametros) if parametros is not None else _legacy.ParametrosEtapa5()
    params.data_inicio = max(getattr(params,"data_inicio",None),estado.data_referencia) if getattr(params,"data_inicio",None) else estado.data_referencia
    resultado = _legacy.construir_resultado_motor_temporal_conjunto(estado, params)
    defs, destinos = _fontes_estado(estado), _destinos(estado)
    horizonte = _data((getattr(estado,"metadados",{}) or {}).get("data_horizonte_terminal")) or resultado.horizonte_motor.data_fim
    fontes: dict[str,_Fonte]={}; saldos: dict[str,float]={}
    candidatos={}; valorados={}; vencedores={}; decisoes={}; descartados={}; estados={}; saldos_data={}; evidencias={}
    eventos=[]; reservas=[]; cobertas=[]; bloqueadas=[]; switchings=[]; bloqueios=[]
    for dia in resultado.horizonte_motor.datas_temporais:
        _ativar(defs,fontes,saldos,dia); obs=_obrigacoes(resultado,dia); tipos=PACOTES_COM_PAGAMENTO if obs else PACOTES_SEM_PAGAMENTO
        baseline=_patrimonio(fontes,saldos,dia,horizonte)
        tr={tipo:_trajetoria(tipo,fontes,saldos,obs,destinos,dia,horizonte) for tipo in tipos}
        pcs=[_pacote(tr[t],dia) for t in tipos]; vals=[_valorado(p,baseline) for p in pcs]; winv=_argmax(vals); win=winv.pacote_candidato if winv else None; tw=tr.get(win.tipo_pacote) if win else None
        candidatos[dia]=pcs; valorados[dia]=vals; vencedores[dia]=win
        descartados[dia]=[_legacy.PacoteTemporalDescartado(pacote_id=v.pacote_candidato.pacote_id,tipo_pacote=v.pacote_candidato.tipo_pacote,motivos_descarte=["menor_patrimonio_terminal_ou_infactibilidade"],score_referencial=v.valoracao.score_referencial) for v in vals if not win or v.pacote_candidato.pacote_id!=win.pacote_id]
        if win:
            just=_legacy.JustificativaDecisaoTemporal(criterio_principal="argmax_patrimonio_liquido_terminal_liquido",criterios_desempate_aplicados=["menor_numero_switchings","menor_numero_fontes_pagamento","ordem_estavel_pacote_id"],resumo={"patrimonio_terminal_vencedor":winv.valoracao.patrimonio_terminal_liquido,"valores_pacotes_factiveis":{v.pacote_candidato.tipo_pacote:v.valoracao.patrimonio_terminal_liquido for v in vals if v.valoracao.factivel},"estado_inicial_id":tw.estado_inicial_id})
            status="vencedor_argmax_selecionado"
        else:
            just=_legacy.JustificativaDecisaoTemporal(criterio_principal="nenhuma_trajetoria_factivel",criterios_desempate_aplicados=[],resumo={"pacotes_avaliados":list(tipos)}); status="sem_pacote_factivel"
            for i,o in enumerate(obs,1): bloqueadas.append(_legacy.ObrigacaoBloqueadaTemporalmente(data=dia,obrigacao_id=_id_obrigacao(o,i),pacote_id=None,motivo_bloqueio_referencial="sem_pacote_factivel_apos_refactibilizacao",valor_obrigacao_referencial=_valor_obrigacao(o),valor_cobertura_referencial=0.0,referencia_obrigacao_temporal=dict(o)))
            bloqueios.append(_legacy.BloqueioFinalEtapa5(codigo="sem_pacote_factivel",detalhe=f"Nenhum pacote factível em {dia.isoformat()}",data=dia))
        decisoes[dia]=_legacy.DecisaoTemporalDia(data_referencia=dia,pacote_vencedor_id=win.pacote_id if win else None,status_decisao=status,justificativa=just,executa_pagamento=bool(win and win.tipo_pacote in PACOTES_COM_PAGAMENTO),executa_switching=bool(win and win.switchings_candidatos),gera_ledger=False)
        ed,ev,rs,cs,sw=_materializar(dia,win,tw); estados[dia]=ed; eventos+=ev; reservas+=rs; cobertas+=cs; switchings+=sw; saldos_data[dia]=list(ed.saldos_fontes_referenciais)
        evidencias[dia.isoformat()]={"estado_inicial_id":tw.estado_inicial_id if tw else _estado_id(dia,saldos),"pacotes_permitidos":list(tipos),"pacotes_avaliados":[v.pacote_candidato.tipo_pacote for v in vals],"patrimonio_terminal_por_pacote":{v.pacote_candidato.tipo_pacote:(v.valoracao.patrimonio_terminal_liquido if v.valoracao.factivel else None) for v in vals},"pacote_vencedor":win.tipo_pacote if win else None,"argmax_comprovado":winv is not None}
        if tw: fontes,saldos=deepcopy(tw.fontes),dict(tw.saldos)
    completos=all(set(e["pacotes_avaliados"])==set(e["pacotes_permitidos"]) for e in evidencias.values()); argmax=all(e["argmax_comprovado"] for e in evidencias.values()); cobertura=all(o.valor_coberto_referencial+0.01>=o.valor_obrigacao_referencial for o in cobertas) and not bloqueadas; pronto=bool(completos and argmax and cobertura and not bloqueios)
    resultado.schema_pacote_temporal_candidato=_legacy.SchemaPacoteTemporalCandidato(nome="PacoteTemporalCandidatoNormativo",versao="ME-535-MOTOR-FUNCIONAL",tipos_pacote_previstos=list(PACOTES_SEM_PAGAMENTO+PACOTES_COM_PAGAMENTO),status_factibilidade_previstos=["factivel_referencialmente","bloqueado_estruturalmente"],campos_obrigatorios=list(getattr(resultado.schema_pacote_temporal_candidato,"campos_obrigatorios",[]) or []),campos_proibidos_decisao=[])
    resultado.pacotes_temporais_candidatos_por_data=candidatos; resultado.pacotes_temporais_valorados_por_data=valorados; resultado.pacote_vencedor_por_data=vencedores; resultado.decisoes_temporais_por_data=decisoes; resultado.pacotes_descartados_por_data=descartados; resultado.estado_temporal_interno_por_data=estados; resultado.eventos_trajetoria_temporal=eventos; resultado.fontes_reservadas_temporalmente=reservas; resultado.obrigacoes_cobertas_temporalmente=cobertas; resultado.obrigacoes_bloqueadas_temporalmente=bloqueadas; resultado.switchings_escolhidos_temporalmente=switchings
    resultado.trajetoria_temporal_interna_escolhida=_legacy.TrajetoriaTemporalInternaEscolhida(estado_temporal_interno_por_data=estados,eventos_trajetoria_temporal=eventos,fontes_reservadas_temporalmente=reservas,obrigacoes_cobertas_temporalmente=cobertas,obrigacoes_bloqueadas_temporalmente=bloqueadas,switchings_escolhidos_temporalmente=switchings,saldos_referenciais_fontes_temporais=saldos_data,destinos_sobras_recebidos_temporais=[],lotes_futuros_materializados=[])
    resultado.destinos_sobras_recebidos_temporais=[]; resultado.lotes_futuros_materializados=[]
    resultado.auditoria_schema_pacote_temporal_candidato=_legacy.AuditoriaSchemaPacoteTemporalCandidato(ok=completos,avisos=[] if completos else ["pacotes_normativos_incompletos"],resumo={"pacotes_normativos_completos":completos,"qtd_datas":len(candidatos)})
    resultado.auditoria_decisao_temporal_conjunto=_legacy.AuditoriaDecisaoTemporalConjunto(ok=argmax,avisos=[] if argmax else ["argmax_nao_comprovado_em_todas_as_datas"],resumo={"argmax_comprovado":argmax,"qtd_decisoes":len(decisoes)})
    resultado.auditoria_trajetoria_temporal_interna=_legacy.AuditoriaTrajetoriaTemporalInterna(ok=cobertura and not bloqueios,avisos=[],bloqueios=[b.codigo for b in bloqueios],resumo={"qtd_eventos_internos":len(eventos),"qtd_obrigacoes_cobertas_referencialmente":len(cobertas),"qtd_obrigacoes_bloqueadas":len(bloqueadas),"qtd_fontes_reservadas":len(reservas),"qtd_switchings_escolhidos":len(switchings)})
    resultado.auditoria_integridade_resultado=_legacy.AuditoriaIntegridadeResultadoMotorTemporalConjunto(ok=pronto,bloqueios=[b.codigo for b in bloqueios],avisos=[],resumo={"pacotes_normativos_completos":completos,"argmax_comprovado":argmax,"obrigacoes_integralmente_cobertas":cobertura})
    resultado.auditoria_final_etapa5=_legacy.AuditoriaFinalResultadoMotorTemporalConjunto(ok=pronto,pronto_para_etapa6=pronto,bloqueios=bloqueios,avisos=[],resumo={"motor_funcional":True,"pacotes_normativos_completos":completos,"argmax_comprovado":argmax,"comparacao_mesmo_estado":True,"obrigacoes_integralmente_cobertas":cobertura})
    resultado.fechamento_funcional_etapa5=_legacy.FechamentoFuncionalEtapa5(etapa5_fechada_funcionalmente=pronto,pronto_para_etapa6=pronto,criterios_fechamento=["cinco_pacotes_normativos","comparacao_mesmo_estado_inicial","argmax_patrimonio_terminal","pagamentos_integralmente_cobertos","trajetoria_stateful"],criterios_atendidos=[x for x,ok in (("cinco_pacotes_normativos",completos),("comparacao_mesmo_estado_inicial",True),("argmax_patrimonio_terminal",argmax),("pagamentos_integralmente_cobertos",cobertura),("trajetoria_stateful",True)) if ok],criterios_bloqueados=[b.codigo for b in bloqueios],limites_preservados=["sem_execucao_bancaria_real","sem_console_xlsx_como_fonte","sem_reotimizacao_pos_ledger"])
    resultado.contrato_consumo_etapa6=_legacy.ContratoConsumoEtapa6(artefato_exclusivo_consumo="ResultadoMotorTemporalConjunto",blocos_consumo=["decisoes_temporais_por_data","pacote_vencedor_por_data","eventos_trajetoria_temporal","fontes_reservadas_temporalmente","obrigacoes_cobertas_temporalmente","obrigacoes_bloqueadas_temporalmente","switchings_escolhidos_temporalmente"],fontes_proibidas=["console","XLSX","saida_observavel","diagnostico_operacional"],observacoes=["decisao_fechada_por_argmax_na_etapa5","etapa6_nao_reotimiza"])
    resultado.pronto_para_etapa6=pronto
    resultado.sumario_final_etapa5=_legacy.SumarioFinalEtapa5(qtd_datas_horizonte=len(resultado.horizonte_motor.datas_temporais),qtd_dias_motor=len(resultado.horizonte_motor.datas_temporais),qtd_pacotes_candidatos=sum(map(len,candidatos.values())),qtd_pacotes_valorados=sum(map(len,valorados.values())),qtd_decisoes_temporais=len(decisoes),qtd_pacotes_vencedores=sum(v is not None for v in vencedores.values()),qtd_eventos_trajetoria=len(eventos),qtd_obrigacoes_cobertas=len(cobertas),qtd_obrigacoes_bloqueadas=len(bloqueadas),qtd_fontes_reservadas=len(reservas),qtd_switchings_escolhidos=len(switchings),qtd_destinos_sobras_recebidos=0,qtd_lotes_futuros_materializados=0,qtd_bloqueios_estruturais=len(bloqueios),qtd_bloqueios_trajetoria=len(bloqueios),qtd_avisos_relevantes=0)
    vencedores_val=[d.justificativa.resumo.get("patrimonio_terminal_vencedor") for d in decisoes.values() if d.pacote_vencedor_id]
    resultado.metadados.update({"versao_contrato":"ME-535-MOTOR-FUNCIONAL","motor_funcional":True,"funcao_objetivo":"patrimonio_liquido_terminal_liquido","pacotes_normativos":list(PACOTES_SEM_PAGAMENTO+PACOTES_COM_PAGAMENTO),"pacotes_normativos_completos":completos,"argmax_comprovado":argmax,"comparacao_mesmo_estado":True,"obrigacoes_integralmente_cobertas":cobertura,"horizonte_terminal":horizonte,"evidencias_economicas_por_data":evidencias,"resultado_terminal":vencedores_val[-1] if vencedores_val else 0.0,"aderencia_terminal":pronto,"ganho_terminal":0.0,"pronto_para_etapa6":pronto})
    return resultado


__all__ = sorted(set(getattr(_legacy, "__all__", [])) | {"ValoracaoEconomicaPacote", "construir_resultado_motor_temporal_conjunto"})
