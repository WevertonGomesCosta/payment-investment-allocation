# 01_diagnostico_pos_merge.md — RD-2026-04-28-03

## 1) Identificação
- **Rodada:** RD-2026-04-28-03
- **Data:** 2026-04-28
- **Objetivo:** diagnóstico pós-merge do estado do repositório e do bloqueio de infraestrutura da validação numérica.
- **Escopo:** documental/diagnóstico (sem alteração de motor, regras econômicas, dados oficiais, cache e saída canônica).

## 2) Estado pós-merge observado
- **Branch atual:** `work` (derivada do histórico já mergeado no repositório local).
- **Status do git:** árvore limpa na abertura da rodada.
- **Histórico recente:** commit topo `3125801` com integração dos artefatos das rodadas anteriores.

## 3) Consistência dos artefatos anteriores
- **Framework base presente:** `relatorios/atuais/framework_execucao/`.
- **RD-2026-04-28-01 presente e íntegra:** plano, matriz, achados e decisão GO.
- **RD-2026-04-28-02 presente e íntegra:** plano, matriz, achados, decisão NO_GO e evidências (`console_execucao.txt`, `planilha_execucao.txt`, `pip_install.txt`, `pip_install_scipy.txt`).

## 4) Diagnóstico técnico sobre `scipy`

### 4.1 Onde `scipy` é exigido
- Import direto em `nucleo/resolver_hibrido_5p_shadow.py`:
  - `from scipy.optimize import linprog`.

### 4.2 Cadeia de import que gera a falha
1. `aplicacao/principal.py` importa `aplicacao.console.principal`.
2. `aplicacao.console.principal` importa `nucleo.contexto_baseline`.
3. `nucleo.contexto_baseline` importa `nucleo.resolver_hibrido_5p_shadow` no topo do módulo.
4. O import do topo em `resolver_hibrido_5p_shadow` requer `scipy` e aborta antes da execução funcional.

### 4.3 Declaração de dependências
- `requirements.txt` **não declara `scipy`**.
- `nucleo/ambiente.py` lista `scipy` apenas como dependência opcional do grupo `otimizacao`.
- `carregar_contexto_baseline(...)` é chamado com `incluir_resolver_hibrido_5p_shadow=False` nos comandos operacionais principais, porém isso **não evita** a falha pois o import ocorre antes do uso da flag.

### 4.4 Evidências de ambiente
- RD-02 registrou `ModuleNotFoundError: No module named 'scipy'` nos comandos oficiais.
- RD-02 registrou falha de instalação por proxy/rede (`403 Forbidden`) ao tentar `pip install scipy`.

## 5) Conclusão diagnóstica
- O bloqueio da RD-2026-04-28-02 **não indica falha econômica do motor**.
- Há dois fatores simultâneos:
  1. **Dependência não declarada** para o caminho de import atualmente executado.
  2. **Restrição de infraestrutura de rede/proxy** que impediu instalar `scipy` na rodada anterior.
- Portanto, o bloqueio não é exclusivamente “motor” e nem “dados”; é de **dependência + infraestrutura** antes da validação numérica.

## 6) Ação mínima para liberar N2–N11 (sem mexer no motor econômico)
1. Disponibilizar ambiente com `scipy` pré-instalado **ou** com acesso autorizado ao índice de pacotes.
2. Em microetapa separada, formalizar a dependência em manifesto de ambiente (se confirmado como requisito operacional dos entrypoints atuais).
3. Só então reexecutar a rodada numérica (N2–N11), preservando as restrições de não alteração econômica.
