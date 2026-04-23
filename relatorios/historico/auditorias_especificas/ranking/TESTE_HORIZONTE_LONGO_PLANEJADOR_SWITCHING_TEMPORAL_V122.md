# Teste do planejador temporal multidestino em horizonte mais longo — V122

## Objetivo

- Verificar se algum switching passa a sobreviver economicamente quando o horizonte deixa de penalizar excessivamente o custo fiscal inicial.
- A análise desta etapa é do **planejador**; ela não reexecuta o simulador central completo em horizonte longo.

## Síntese geral

- O primeiro horizonte com switching economicamente sobrevivente foi **60 dias** com **32** candidatos elegíveis.
- O recorte curto de 30 dias continua sem sobreviventes econômicos, mas a partir da ampliação do horizonte o planejador passa a encontrar candidatos positivos.

## Comparativo por horizonte

### Horizonte de 30 dias
- Intervalo: 2026-04-20 até 2026-05-20
- Pagamentos considerados: 15
- Lotes considerados: 5
- Destinos elegíveis por lote: 12
- Switching elegível no planejador: 0

#### Melhor destino por lote

- Lote 5680 abr.: Tesouro Educa+ 2032 | ganho=-0.7 | elegível=False
- Lote 6630,64 fev.: Tesouro Educa+ 2027 | ganho=-2.07 | elegível=False
- Lote 3000 mar. B: Tesouro Educa+ 2027 | ganho=-8.9 | elegível=False
- Lote 3000 mar. V: Tesouro Educa+ 2027 | ganho=-9.78 | elegível=False
- Lote 8500 mar.: Tesouro Educa+ 2027 | ganho=-82.98 | elegível=False

### Horizonte de 60 dias
- Intervalo: 2026-04-20 até 2026-06-19
- Pagamentos considerados: 25
- Lotes considerados: 5
- Destinos elegíveis por lote: 12
- Switching elegível no planejador: 32
- Melhor switching do horizonte: Lote 6630,64 fev. → Tesouro Educa+ 2027
- Ganho terminal econômico mínimo estimado: 15.61
- Patrimônio terminal origem estimado: 2838.58
- Patrimônio terminal destino estimado: 2854.19
- Custo fiscal estimado: 19.63
- Penalidade carência reprojetada: 0.0

#### Melhor destino por lote

- Lote 6630,64 fev.: Tesouro Educa+ 2027 | ganho=15.61 | elegível=True
- Lote 3000 mar. B: Tesouro Educa+ 2027 | ganho=9.96 | elegível=True
- Lote 3000 mar. V: Tesouro Educa+ 2027 | ganho=9.1 | elegível=True
- Lote 5680 abr.: CDB BMG IPCA+ 8,68% - 3 anos | ganho=-10.19 | elegível=False
- Lote 8500 mar.: Tesouro Educa+ 2027 | ganho=-133.42 | elegível=False

### Horizonte de 90 dias
- Intervalo: 2026-04-20 até 2026-07-19
- Pagamentos considerados: 35
- Lotes considerados: 5
- Destinos elegíveis por lote: 12
- Switching elegível no planejador: 33
- Melhor switching do horizonte: Lote 6630,64 fev. → Tesouro Educa+ 2027
- Ganho terminal econômico mínimo estimado: 33.4
- Patrimônio terminal origem estimado: 2839.03
- Patrimônio terminal destino estimado: 2872.43
- Custo fiscal estimado: 19.63
- Penalidade carência reprojetada: 0.0

#### Melhor destino por lote

- Lote 6630,64 fev.: Tesouro Educa+ 2027 | ganho=33.4 | elegível=True
- Lote 3000 mar. B: Tesouro Educa+ 2027 | ganho=28.95 | elegível=True
- Lote 3000 mar. V: Tesouro Educa+ 2027 | ganho=28.1 | elegível=True
- Lote 5680 abr.: Tesouro Educa+ 2027 | ganho=-62.94 | elegível=False
- Lote 8500 mar.: Tesouro Educa+ 2027 | ganho=-184.78 | elegível=False

### Horizonte de 120 dias
- Intervalo: 2026-04-20 até 2026-08-18
- Pagamentos considerados: 50
- Lotes considerados: 5
- Destinos elegíveis por lote: 12
- Switching elegível no planejador: 33
- Melhor switching do horizonte: Lote 6630,64 fev. → Tesouro Educa+ 2027
- Ganho terminal econômico mínimo estimado: 51.3
- Patrimônio terminal origem estimado: 2839.49
- Patrimônio terminal destino estimado: 2890.79
- Custo fiscal estimado: 19.63
- Penalidade carência reprojetada: 0.0

#### Melhor destino por lote

- Lote 6630,64 fev.: Tesouro Educa+ 2027 | ganho=51.3 | elegível=True
- Lote 3000 mar. B: Tesouro Educa+ 2027 | ganho=48.06 | elegível=True
- Lote 3000 mar. V: Tesouro Educa+ 2027 | ganho=47.22 | elegível=True
- Lote 5680 abr.: Tesouro Educa+ 2027 | ganho=-116.14 | elegível=False
- Lote 8500 mar.: Tesouro Educa+ 2027 | ganho=-237.08 | elegível=False

## Interpretação

- O teste confirma que a ausência de switching no recorte curto não era prova suficiente de dominância estrutural do baseline sem switching.
- Parte da penalização vinha da janela curta, que não dava tempo para o destino compensar o custo fiscal inicial.
- Os lotes `Lote 6630,64 fev.`, `Lote 3000 mar. B` e `Lote 3000 mar. V` tornam-se positivos já no horizonte de 60 dias, sempre com `Tesouro Educa+ 2027` como melhor destino no teste atual.
- `Lote 8500 mar.` e `Lote 5680 abr.` seguem economicamente negativos mesmo em horizonte mais longo, sugerindo que o bloqueio nesses casos não é apenas miopia temporal.

## Conclusão operacional

- O próximo passo correto não é voltar ao simulador curto, e sim levar os candidatos positivos do horizonte mais longo para uma simulação central controlada.
- O recorte curto continua útil como filtro conservador, mas não deve ser tratado como prova final contra switching quando o objetivo é patrimônio terminal.
