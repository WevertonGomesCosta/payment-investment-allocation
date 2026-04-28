# 04_instrucao_execucao_local_ci.md — RD-2026-04-28-05

## Objetivo
Viabilizar execução local/CI da validação numérica após bloqueio de infraestrutura do ambiente atual.

## Procedimento recomendado (local/CI)
1. Criar e ativar ambiente virtual:
   - Linux/macOS:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

2. Instalar dependências:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

3. Gate obrigatório de ambiente:
   ```bash
   python -c "import scipy; print(scipy.__version__)"
   ```

4. Se gate passar, executar validação numérica mínima:
   ```bash
   python aplicacao/principal.py > relatorios/atuais/framework_execucao/rodadas/RD-2026-04-28-05/evidencias/console_execucao_local_ci.txt 2>&1
   python scripts/operacional/gerar_planilha_operacional.py > relatorios/atuais/framework_execucao/rodadas/RD-2026-04-28-05/evidencias/planilha_execucao_local_ci.txt 2>&1
   ```

5. Critérios de classificação (rodada subsequente)
- **GO**: N2–N11 executados sem erro fatal e sem divergência material.
- **GO_COM_RESTRICOES**: execução concluída com achados não críticos documentados.
- **NO_GO**: erro crítico funcional/econômico ou inconsistência material comprovada.

## Evidências mínimas a anexar
- `import_scipy_local_ci.txt`
- `console_execucao_local_ci.txt`
- `planilha_execucao_local_ci.txt`
- matriz N2–N11 preenchida com evidências por linha/arquivo.
