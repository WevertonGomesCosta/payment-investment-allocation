from __future__ import annotations
import argparse, json, py_compile, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TOL = 0.01


def _listar_historicos_v4() -> list[Path]:
    return sorted((ROOT / 'scripts' / 'diagnostico' / 'historico' / 'etapa4').glob('*.py'))


def _compilar(paths: list[Path]) -> tuple[bool, int]:
    ok = True
    qtd = 0
    for p in paths:
        try:
            py_compile.compile(str(p), doraise=True)
            qtd += 1
        except Exception:
            ok = False
    return ok, qtd


def _norm(v: Any) -> str:
    return str(v or "").strip().lower().replace('.', '')


def _f(v: Any) -> float:
    try:
        return round(float(v), 2)
    except Exception:
        return 0.0


def _validar_interface_etapa4_5() -> dict[str, object]:
    saida_validada = False
    pacotes_disponiveis = False
    saida_coerente = False
    erro = ""
    faltantes: list[str] = []
    try:
        from nucleo.contexto_baseline import carregar_contexto_baseline
        from nucleo.saida_canonica import construir_saida_canonica, PacoteSaidaCanonica
        from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida_shadow
        from nucleo.saida_observavel import construir_amostras_pagamentos_operacionais, construir_linhas_lotes_consolidados
        from nucleo.saida_canonica_temporal_shadow_v4k import CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K

        ctx = carregar_contexto_baseline(
            raiz_repositorio=ROOT,
            instalar_automaticamente=False,
            incluir_benchmark_agrupado_individual_shadow=False,
        )

        s0 = construir_saida_canonica(ctx)
        s1 = construir_saida_canonica(ctx, incluir_temporal_shadow=False)
        s2 = construir_saida_canonica(ctx, incluir_temporal_shadow=True)

        checagens_saida = [
            isinstance(s0, PacoteSaidaCanonica),
            isinstance(s1, PacoteSaidaCanonica),
            isinstance(s2, PacoteSaidaCanonica),
        ]
        if not all(checagens_saida):
            faltantes.append('pacote_saida_canonica_invalido')

        auditoria_true = dict(getattr(s2, 'auditoria', {}) or {})
        if CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K not in auditoria_true:
            faltantes.append('chave_auditoria_temporal_shadow_ausente')

        agregador = construir_pacotes_temporais_agregados_saida_shadow(ctx)
        attrs = [
            'pacote_replay_passado',
            'pacote_ledger_temporal_operacional',
            'pacote_estado_temporal',
            'pacote_auditoria_temporal',
        ]
        faltantes.extend([a for a in attrs if getattr(agregador, a, None) is None])
        pacotes_disponiveis = len([a for a in attrs if getattr(agregador, a, None) is not None]) == 4

        ativos = construir_linhas_lotes_consolidados(ctx, s0, tipo='ativos')
        exauridos = construir_linhas_lotes_consolidados(ctx, s0, tipo='exauridos')
        lote = 'Lote 3120 mai'
        linha_ativo = next((r for r in ativos if _norm(r.get('Lote')) == _norm(lote)), None)
        linha_ex = next((r for r in exauridos if _norm(r.get('Lote')) == _norm(lote)), None)
        if linha_ativo is None:
            faltantes.append('lote_3120_mai_ausente_ativos')
        if linha_ex is not None:
            faltantes.append('lote_3120_mai_presente_exauridos')

        bruto = _f((linha_ativo or {}).get('Bruto atual'))
        liq = _f((linha_ativo or {}).get('Líq. atual'))
        if not (abs(bruto - 50.52) <= TOL or abs(liq - 50.52) <= TOL):
            faltantes.append('lote_3120_mai_saldo_final_incompativel_50_52')

        amostras = construir_amostras_pagamentos_operacionais(s0, limite=1000, contexto=ctx)
        realizados = list((amostras.get('realizados') or {}).get('linhas') or [])
        linhas_lote = [r for r in realizados if _norm(r.get('Lotes usados') or r.get('Lote')) == _norm(lote)]
        saldos_antes = [_f(r.get('Saldo Antes')) for r in linhas_lote]
        if any(v < -TOL for v in saldos_antes):
            faltantes.append('saldo_antes_negativo_lote_3120_mai')

        ativos_set = {_norm(r.get('Lote')) for r in ativos}
        exauridos_set = {_norm(r.get('Lote')) for r in exauridos}
        if ativos_set & exauridos_set:
            faltantes.append('lotes_duplicados_ativos_exauridos')

        saida_validada = len([x for x in faltantes if x.startswith('pacote_saida') or x.startswith('chave_auditoria')]) == 0 and all(checagens_saida)
        saida_coerente = len([x for x in faltantes if 'lote_3120' in x or 'saldo_antes' in x or 'duplicados' in x]) == 0
    except Exception as exc:
        erro = f"{type(exc).__name__}: {exc}"

    return {
        'saida_etapa4_validada_para_etapa5': saida_validada,
        'pacotes_temporais_disponiveis_para_etapa5': pacotes_disponiveis,
        'saida_observavel_coerente_para_etapa5': saida_coerente,
        'residuos_funcionais_bloqueiam_abertura_etapa5': True,
        'etapa5_pode_abrir_agora': False,
        'proxima_etapa_recomendada': 'V17-F0-V.4U',
        'erro_validacao_etapa4_etapa5': erro,
        'componentes_etapa4_etapa5_faltantes': sorted(set(faltantes)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-csv", action="store_true")
    parser.parse_args()
    h = _listar_historicos_v4()
    com_root_fragil = [str(p.relative_to(ROOT)) for p in h if 'parents[2]' in p.read_text(encoding='utf-8')]
    py_ok, qtd_comp = _compilar(h)
    out = {
        'historicos_v4_root_resolver_corrigido': len(com_root_fragil) == 0,
        'historicos_v4_py_compile_ok': py_ok,
        'qtd_historicos_v4_compilados': qtd_comp,
        'qtd_historicos_v4_com_root_fragil': len(com_root_fragil),
        'historicos_v4_com_root_fragil': com_root_fragil,
    }
    out.update(_validar_interface_etapa4_5())
    for k, v in out.items():
        print(f"{k}={json.dumps(v, ensure_ascii=False)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
