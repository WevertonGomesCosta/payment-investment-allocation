from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Risco:
    arquivo: str
    categoria: str
    severidade: str
    evidencia: str
    detalhe: str


def _run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, cwd=Path(__file__).resolve().parents[2])


def _diff(commit: str) -> str:
    return _run(["git", "show", "--unified=0", "--no-color", commit])


def analisar_commit(commit: str) -> list[Risco]:
    txt = _diff(commit)
    riscos: list[Risco] = []
    blocos = re.split(r"\ndiff --git ", "\n" + txt)
    for b in blocos:
        if "+++ b/" not in b:
            continue
        m = re.search(r"\+\+\+ b/(.+)", b)
        if not m:
            continue
        arq = m.group(1).strip()

        if arq == "nucleo/saida_canonica.py" and "construir_ledger_temporal_conjunto" in b and "construir_saida_canonica" in b:
            riscos.append(Risco(
                arquivo=arq,
                categoria="duplicidade_de_execucao",
                severidade="medio",
                evidencia="ledger_result calculado em construir_saida_canonica",
                detalhe="Risco de divergência temporal entre execução do extrato e auditoria, além de custo duplicado.",
            ))

        if arq == "nucleo/gerar_planilha_operacional.py" and "isinstance(v, (list, dict, tuple, set))" in b:
            riscos.append(Risco(
                arquivo=arq,
                categoria="silenciamento_de_dados",
                severidade="medio",
                evidencia="filtro de não escalares na aba Saida Canonica",
                detalhe="Pode ocultar sinais de perda de contrato de auditoria ao invés de corrigir a origem dos dados.",
            ))

        if arq == "nucleo/gerar_planilha_operacional.py" and "fifo_nao_aplicavel_sem_motivo_explicito" in b:
            riscos.append(Risco(
                arquivo=arq,
                categoria="mascaramento_de_causa",
                severidade="alto",
                evidencia="injeção de motivo genérico na renderização da planilha",
                detalhe="Se houver ausência de avaliação no núcleo, a planilha mascara o problema ao invés de falhar/propagar causa real.",
            ))

        if arq == "nucleo/ledger_temporal_conjunto.py" and "fifo_nao_aplicavel_lote_ja_determinado" in b:
            riscos.append(Risco(
                arquivo=arq,
                categoria="motivo_semantico",
                severidade="medio",
                evidencia="motivo de não promoção alterado para lote_ja_determinado",
                detalhe="Pode classificar como não aplicável casos onde houve avaliação real, impactando leitura diagnóstica.",
            ))
    return riscos


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--commit", default="HEAD", help="Commit para auditoria")
    p.add_argument("--json", action="store_true", help="Saída JSON")
    args = p.parse_args()

    riscos = analisar_commit(args.commit)
    if args.json:
        print(json.dumps([asdict(r) for r in riscos], ensure_ascii=False, indent=2))
    else:
        print(f"commit_analisado={args.commit}")
        print(f"qtd_riscos={len(riscos)}")
        for i, r in enumerate(riscos, 1):
            print(f"[{i}] arquivo={r.arquivo} | severidade={r.severidade} | categoria={r.categoria}")
            print(f"    evidencia={r.evidencia}")
            print(f"    detalhe={r.detalhe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
