# Scripts do repositório

Estrutura canônica da baseline vigente V188:

- `scripts/diagnostico/`: scripts canônicos de diagnóstico, inspeção e release;
- `scripts/operacional/`: scripts canônicos de geração operacional e exportação;
- `scripts/auditoria/`: scripts canônicos de auditoria;
- `scripts/historico_raiz/`: cópias históricas movidas da antiga raiz de `scripts/`.

Na raiz de `scripts/` permanecem apenas wrappers mínimos de compatibilidade e arquivos de suporte compartilhado. Eles são preservados intencionalmente para não quebrar caminhos legados, mas não constituem o caminho canônico de uso.

A derivação futura de `resolver_dia(t, E_t)` deve respeitar primeiro a `relatorios/atuais/ESPECIFICACAO_SAIDA_OFICIAL.md`, para nascer já compatível com console, markdown, json e `.xlsx`.
