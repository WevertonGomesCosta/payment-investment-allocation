# CORRECAO-EXTRATO-FUTURO-OFICIAL-01 — Renderiza obrigações oficiais no Extrato Futuro

- CLASSE: CORREÇÃO CIRÚRGICA / EXPORTAÇÃO XLSX OFICIAL
- ESCOPO: `nucleo/gerar_planilha_operacional.py`
- STATUS: implementada localmente

## Diagnóstico confirmado

A aba `Extrato Futuro` era criada no exportador oficial a partir de `saida.extrato_futuro`. Quando essa lista vinha vazia, a aba permanecia sem linhas mesmo quando a cadeia oficial/observável já continha obrigações futuras em `PacoteSaidaObservavelOficial`.

As abas `Obs Proximos Pagamentos` e `Obs Obrigacoes Bloqueadas` já vinham de `PacoteSaidaObservavelOficial.bloco_xlsx.abas`, adicionado ao XLSX pelo próprio exportador oficial.

## Correção aplicada

A correção mantém a rota existente do XLSX e adiciona apenas fallback interno para a aba `Extrato Futuro`:

1. se `saida.extrato_futuro` tiver linhas, o comportamento existente é preservado;
2. se `saida.extrato_futuro` estiver vazio, o exportador monta linhas da aba `Extrato Futuro` a partir de `PacoteSaidaObservavelOficial.bloco_xlsx.abas['Obrigacoes Cobertas']` e `['Obrigacoes Bloqueadas']`;
3. obrigações bloqueadas permanecem bloqueadas, com `Cobertura integral = não`, `Status recomendação` preservado e `Motivo bloqueio lote` preenchido com o motivo oficial;
4. quando não há pacote/fonte oficial, os campos de lote/fonte/saldo/switching ficam como `n/d` ou marcador oficial controlado (`sem_pacote_valido`).

## Origem oficial dos dados

- Fonte exclusiva usada no fallback: `PacoteSaidaObservavelOficial.bloco_xlsx.abas`.
- Abas usadas: `Obrigacoes Cobertas` e `Obrigacoes Bloqueadas`.
- Não são usadas as abas diagnósticas V17-F0-U.7 (`Pagamentos Operacionais`, `Fontes Pagamento`, `Pendencias Pagamentos`, `Pagamentos Metadados`).
- FIFO diagnóstico, saldos diagnósticos e candidatos não promovidos não são lidos nem convertidos em recomendação.

## Restrições preservadas

- Etapa 5 não alterada.
- Motor temporal conjunto não alterado.
- LedgerTemporalCanonico não alterado.
- Gates não alterados.
- SaidaCanonicaOficial não alterada.
- PacoteSaidaObservavelOficial não alterado como fonte decisória.
- ResultadoParidadeRenderizacaoOficial não alterado.
- ResultadoLimpezaDepreciacaoControlada não alterado.
- Dados e cache não alterados.
- Contratos e modelo oficial não alterados.
- Nenhuma decisão econômica criada ou alterada.

## Validação local

- `python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py`: aprovado.
- `python -B aplicacao/principal.py`: aprovado; XLSX gerado em `saidas/oficial/relatorio_operacional_v225.xlsx`.
- Auditoria do XLSX gerado:
  - `Extrato Futuro`: 158 linhas oficiais.
  - obrigações cobertas: 2.
  - obrigações bloqueadas: 156.
  - motivo `sem_pacote_valido_para_obrigacao_temporal`: 156 ocorrências preservadas.
  - obrigações bloqueadas apresentadas como cobertas: 0.
  - campos U.7/FIFO/saldos diagnósticos promovidos para cabeçalhos do `Extrato Futuro`: 0.
- Etapa 9 permaneceu presente no console.
- Etapa 10 permaneceu com XLSX aprovado e status geral `aprovado_com_ressalva` por ressalva não material de console não auditado.
- Etapa 11 permaneceu como governança, sem remoção automática.
