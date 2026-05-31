# GATES-RESUMO-01 — Reaplica resumo observável dos gates sobre base limpa

## Objetivo

Tornar o bloqueio por `ResultadoGatesValidacaoNucleo.pronto_para_etapa8=False` observável no terminal, sem liberar console/XLSX oficiais.

## Escopo

- altera apenas `aplicacao/principal.py`;
- adiciona log desta frente;
- não altera motor;
- não altera ledger;
- não altera gates;
- não altera `SaidaCanonicaOficial`;
- não cria adaptadores;
- não cria comparadores;
- não gera saída oficial nova.

## Resultado esperado

`python -B aplicacao/principal.py` deve continuar bloqueando console/XLSX, mas agora deve exibir:

- gates executados;
- gates aprovados;
- gates reprovados;
- número de bloqueios;
- número de avisos;
- principais bloqueios;
- principais avisos.

## Próxima frente

`MACRO-GATES-01 — Corrige decisao_temporal_inconsistente / data_com_obrigacao_sem_vencedor`.
