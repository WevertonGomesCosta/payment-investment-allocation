# Auditoria estrutural de pastas pós-limpeza

## Objetivo

Inventariar diretórios rastreados pelo Git e classificar pastas para manutenção, avaliação ou possível remoção, sem apagar arquivos automaticamente.

## Resumo por pasta de primeiro nível

| Pasta | Arquivos rastreados | Ação preliminar | Motivo |
|---|---:|---|---|
| `.editorconfig` | 1 | MANTER | arquivo/pasta estrutural do projeto |
| `.gitattributes` | 1 | MANTER | arquivo/pasta estrutural do projeto |
| `.gitignore` | 1 | MANTER | arquivo/pasta estrutural do projeto |
| `LICENSE` | 1 | MANTER | arquivo/pasta estrutural do projeto |
| `README.md` | 1 | MANTER | arquivo/pasta estrutural do projeto |
| `aplicacao` | 9 | MANTER | pasta operacional, motor, dados, configuração ou saída oficial |
| `config` | 3 | MANTER | pasta operacional, motor, dados, configuração ou saída oficial |
| `dados` | 6 | MANTER | pasta operacional, motor, dados, configuração ou saída oficial |
| `docs` | 2 | MANTER_POR_ENQUANTO | documentação de governança; avaliar só depois |
| `logs` | 16 | AVALIAR | não classificado automaticamente |
| `nucleo` | 65 | MANTER | pasta operacional, motor, dados, configuração ou saída oficial |
| `payment-investment-allocation.Rproj` | 1 | AVALIAR | não classificado automaticamente |
| `prompts` | 8 | AVALIAR | prompts podem ser úteis, mas talvez excessivos |
| `relatorios` | 462 | AVALIAR | não classificado automaticamente |
| `requirements.txt` | 1 | MANTER | arquivo/pasta estrutural do projeto |
| `saidas` | 4 | AVALIAR | raiz de saídas contém oficial, diagnóstico e histórico |
| `scripts` | 125 | AVALIAR | raiz de scripts contém subpastas com destinos distintos |

## Resumo por ação preliminar — profundidade 2

| Ação | Qtde de pastas |
|---|---:|
| AVALIAR | 15 |
| CANDIDATO_CONSOLIDACAO | 1 |
| CANDIDATO_REMOCAO | 1 |
| CANDIDATO_REMOCAO_APOS_CONFERENCIA | 1 |
| MANTER | 14 |
| MANTER_POR_ENQUANTO | 1 |

## Arquivos gerados

- `relatorios/atuais/limpeza_estrutura/inventario_pastas_profundidade_1.csv`
- `relatorios/atuais/limpeza_estrutura/inventario_pastas_profundidade_2.csv`
- `relatorios/atuais/limpeza_estrutura/inventario_pastas_profundidade_3.csv`
- `relatorios/atuais/limpeza_estrutura/status_local_ignorados_estrutura.txt`
