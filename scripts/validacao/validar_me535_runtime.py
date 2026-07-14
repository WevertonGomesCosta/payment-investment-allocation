from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from aplicacao.console.principal import render_console
from aplicacao.principal import carregar_contexto_e_saida
from nucleo.gerar_planilha_operacional import main as gerar_planilha_operacional
from nucleo.governanca_residuos_pipeline import construir_resultado_governanca_residuos_pipeline
from nucleo.inventario_residuos_pipeline import construir_inventario_residuos_pipeline
from nucleo.paridade_renderizacao_oficial import validar_paridade_renderizacao_oficial


def exigir(condicao: bool, mensagem: str) -> None:
    if not condicao:
        raise RuntimeError(mensagem)


def main() -> None:
    saida_silenciada = io.StringIO()
    with redirect_stdout(saida_silenciada):
        (
            contexto,
            estado_temporal_inicial,
            resultado_motor,
            ledger,
            gates,
            saida_canonica,
            saida_canonica_oficial,
            pacote_observavel,
        ) = carregar_contexto_e_saida()

    exigir(resultado_motor is not None, "ResultadoMotorTemporalConjunto ausente")
    exigir(resultado_motor.pronto_para_etapa6 is True, "Etapa 5 não está pronta para a Etapa 6")
    exigir(resultado_motor.metadados.get("motor_funcional") is True, "motor_funcional não materializado")
    exigir(resultado_motor.metadados.get("pacotes_normativos_completos") is True, "pacotes normativos incompletos")
    exigir(resultado_motor.metadados.get("argmax_comprovado") is True, "argmax não comprovado")
    exigir(resultado_motor.metadados.get("comparacao_mesmo_estado") is True, "pacotes não comparados no mesmo estado")
    exigir(resultado_motor.metadados.get("obrigacoes_integralmente_cobertas") is True, "há obrigação sem cobertura integral")

    evidencias = dict(resultado_motor.metadados.get("evidencias_economicas_por_data", {}) or {})
    exigir(bool(evidencias), "matriz econômica por data ausente")
    for data_ref, evidencia in evidencias.items():
        permitidos = set(evidencia.get("pacotes_permitidos", []) or [])
        avaliados = set(evidencia.get("pacotes_avaliados", []) or [])
        exigir(permitidos == avaliados, f"pacotes divergentes em {data_ref}: {avaliados} != {permitidos}")
        exigir(evidencia.get("argmax_comprovado") is True, f"argmax ausente em {data_ref}")
        exigir(evidencia.get("pacote_vencedor") in permitidos, f"vencedor fora do contrato em {data_ref}")

    exigir(ledger is not None, "LedgerTemporalCanonico ausente")
    exigir(ledger.pronto_para_etapa_posterior is True, "Etapa 6 não está pronta para a Etapa 7")
    exigir(ledger.metadados.get("etapa6_sem_reotimizacao_confirmada") is True, "Etapa 6 não confirmou ausência de reotimização")

    exigir(gates is not None, "ResultadoGatesValidacaoNucleo ausente")
    exigir(gates.ok is True, "Etapa 7 possui bloqueios")
    exigir(gates.pronto_para_etapa8 is True, "Etapa 7 não liberou a Etapa 8")
    gate_motor = next((gate for gate in gates.gates if gate.gate_id == "gate_motor_funcional"), None)
    exigir(gate_motor is not None, "gate_motor_funcional ausente")
    exigir(gate_motor.aprovado is True, "gate_motor_funcional reprovado")

    exigir(saida_canonica is not None, "saída canônica de compatibilidade ausente")
    exigir(saida_canonica_oficial is not None, "SaidaCanonicaOficial ausente")
    exigir(pacote_observavel is not None, "PacoteSaidaObservavelOficial ausente")
    exigir(pacote_observavel.preparado is True, "Etapa 9 não preparou a saída observável")
    exigir(pacote_observavel.ok is True, "Etapa 9 reprovada")

    with redirect_stdout(saida_silenciada):
        console_auditavel = render_console(
            contexto,
            saida_canonica,
            estado_temporal_inicial=estado_temporal_inicial,
            pacote_saida_observavel_oficial=pacote_observavel,
        )
        caminho_xlsx = Path(
            gerar_planilha_operacional(
                contexto=contexto,
                saida=saida_canonica,
                estado_temporal_inicial=estado_temporal_inicial,
                pacote_saida_observavel_oficial=pacote_observavel,
            )
        )
    exigir(caminho_xlsx.exists(), f"XLSX oficial não foi gerado: {caminho_xlsx}")

    paridade = validar_paridade_renderizacao_oficial(
        pacote_saida_observavel=pacote_observavel,
        caminho_xlsx=caminho_xlsx,
        console_renderizado=console_auditavel,
    )
    exigir(paridade.ok is True, "Etapa 10 reprovada")
    exigir(getattr(paridade.resumo, "qtd_divergencias_materiais", 0) == 0, "Etapa 10 contém divergência material")

    inventario = construir_inventario_residuos_pipeline()
    governanca = construir_resultado_governanca_residuos_pipeline(
        paridade,
        evidencias_auxiliares=inventario,
    )
    exigir(governanca.ok is True, "Etapa 11 reprovada")

    abas = list(getattr(pacote_observavel.bloco_xlsx, "abas", {}).keys())
    abas_esperadas = ["Extrato Passado", "Extrato Futuro", "Switching", "Carteira", "Situação Atual"]
    exigir(abas == abas_esperadas, f"abas oficiais divergentes: {abas}")

    resumo = {
        "etapa5_pronta": resultado_motor.pronto_para_etapa6,
        "argmax_comprovado": resultado_motor.metadados.get("argmax_comprovado"),
        "datas_auditadas": len(evidencias),
        "etapa6_pronta": ledger.pronto_para_etapa_posterior,
        "gate_motor_funcional": gate_motor.aprovado,
        "etapa7_pronta": gates.pronto_para_etapa8,
        "etapa9_ok": pacote_observavel.ok,
        "etapa10_ok": paridade.ok,
        "etapa11_ok": governanca.ok,
        "xlsx": str(caminho_xlsx),
        "abas": abas,
    }
    print("ME535_RUNTIME_APROVADO=" + json.dumps(resumo, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        print(f"ME535_RUNTIME_FALHA={type(erro).__name__}:{erro}")
        raise
