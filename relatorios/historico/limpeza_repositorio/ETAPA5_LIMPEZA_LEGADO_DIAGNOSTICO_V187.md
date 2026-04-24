# Etapa 5 — limpeza residual final do legado diagnóstico ativo (V187)

## Escopo aplicado

Limpeza restrita à camada de diagnóstico histórico ativo, com foco em:
- `saidas/diagnostico/`
- trilhas antigas superseded ainda competindo visualmente com a camada ativa

## O que foi feito

- todo o conteúdo legado de `saidas/diagnostico/`, exceto o `README.md`, foi rebaixado para `saidas/historico/diagnostico_legado/`;
- os arquivos foram organizados em subpastas por finalidade:
  - `auditorias/`
  - `grades/`
  - `motores_experimentais/`
  - `pagamentos_legado/`
  - `comparadores_legado/`
  - `probes/`
- `saidas/diagnostico/` foi mantido como caminho canônico apenas para diagnósticos correntes e temporários;
- `saidas/README.md` e `saidas/diagnostico/README.md` foram atualizados para refletir a nova navegação;
- resíduos efêmeros de `compileall` foram removidos antes da validação final.

## Resultado esperado

- menor ruído operacional na camada ativa de diagnósticos;
- histórico preservado sem competir com a baseline vigente;
- `saidas/diagnostico/` pronto para receber apenas investigações correntes.
