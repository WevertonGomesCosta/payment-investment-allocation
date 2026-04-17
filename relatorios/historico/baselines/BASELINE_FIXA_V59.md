# Baseline fixa V59

## Objetivo desta versão

Derivar a V58 de forma cirúrgica para consolidar a higiene operacional/documental da baseline, remover resíduos estruturais do fluxo antigo e adicionar uma checagem mínima automática de release, sem alterar o motor financeiro.

## Reorganização aplicada

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- remoção do ramo residual `menos_1_dia` em `nucleo/contexto_baseline.py`;
- atualização do mapa documental vigente em `relatorios/INDICE_RELATORIOS.md`;
- criação da checagem mínima automática de release em `scripts/diagnostico/verificar_release_baseline.py`;
- manutenção dos wrappers de compatibilidade antigos;
- limpeza da entrega para evitar artefatos efêmeros e saídas redundantes de versões anteriores.

## Garantia de compatibilidade

Os comandos canônicos e os comandos antigos continuam executáveis na V59.

## Critério desta baseline

A V59 preserva a matemática já validada dos lotes, do replay e da planilha operacional, mas fecha a governança mínima da release para deixar a baseline atual limpa, consistente e auditável como artefato oficial.

## Atualização V59

- limpeza de artefatos efêmeros (`__pycache__` e `.pyc`) do pacote final;
- atualização da documentação vigente para a versão atual;
- remoção do código morto residual associado ao fluxo `menos_1_dia`;
- adição de uma checagem mínima automática de release para validar higiene da baseline, índice documental, referências ativas e presença dos caminhos canônicos.
