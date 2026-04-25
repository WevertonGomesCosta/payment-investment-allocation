# Scripts do repositório

Estrutura canônica da baseline vigente V201:

- `scripts/diagnostico/`: scripts canônicos de diagnóstico, inspeção e release;
- `scripts/operacional/`: scripts canônicos de geração operacional e exportação;
- `scripts/auditoria/`: scripts canônicos de auditoria;
- `scripts/historico_raiz/`: cópias históricas movidas da antiga raiz de `scripts/`.

Na raiz de `scripts/` permanecem apenas wrappers mínimos de compatibilidade e arquivos de suporte compartilhado. Eles são preservados intencionalmente para não quebrar caminhos legados, mas não constituem o caminho canônico de uso.

A classificação vigente de autoridade dos scripts está em `relatorios/atuais/MAPA_SCRIPTS_V201.md`.

Regra operacional: scripts históricos não devem escrever em `saidas/oficial/`. A próxima etapa deve substituir recálculos locais de saída por uma camada única de saída canônica.
