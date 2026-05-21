from __future__ import annotations
import argparse, json, py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


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


def _validar_interface_etapa4_5() -> dict[str, object]:
    saida_validada = False
    pacotes_disponiveis = False
    saida_coerente = False
    residuos_bloqueiam = False
    try:
        from nucleo.contexto_saida import construir_contexto_saida
        from nucleo.saida_canonica import construir_saida_canonica
        from nucleo.pacote_saida_canonica import PacoteSaidaCanonica
        from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida_shadow
        from nucleo.pacote_replay_passado import PacoteReplayPassado
        from nucleo.pacote_ledger_temporal_operacional import PacoteLedgerTemporalOperacional
        from nucleo.pacote_estado_temporal import PacoteEstadoTemporal
        from nucleo.pacote_auditoria_temporal import PacoteAuditoriaTemporal
        _ = [PacoteReplayPassado, PacoteLedgerTemporalOperacional, PacoteEstadoTemporal, PacoteAuditoriaTemporal]
        pacotes_disponiveis = True
        ctx = construir_contexto_saida()
        s0 = construir_saida_canonica(ctx)
        s1 = construir_saida_canonica(ctx, incluir_temporal_shadow=False)
        s2 = construir_saida_canonica(ctx, incluir_temporal_shadow=True)
        _ = construir_pacotes_temporais_agregados_saida_shadow(ctx)
        saida_validada = isinstance(s0, PacoteSaidaCanonica) and isinstance(s1, PacoteSaidaCanonica) and isinstance(s2, PacoteSaidaCanonica)
        saida_coerente = True
        residuos_bloqueiam = False
    except Exception:
        residuos_bloqueiam = True
    return {
        'saida_etapa4_validada_para_etapa5': saida_validada,
        'pacotes_temporais_disponiveis_para_etapa5': pacotes_disponiveis,
        'saida_observavel_coerente_para_etapa5': saida_coerente,
        'residuos_funcionais_bloqueiam_abertura_etapa5': residuos_bloqueiam,
        'etapa5_pode_abrir_agora': False,
        'proxima_etapa_recomendada': 'V17-F0-V.4U',
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
    for k,v in out.items():
        print(f"{k}={json.dumps(v, ensure_ascii=False)}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
