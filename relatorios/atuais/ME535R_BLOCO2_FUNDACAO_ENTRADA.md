# ME-535R — Bloco 2: fundação de entrada

## 1. Escopo

Esta entrega cria dois gates anteriores à conexão do `EstadoEconomicoCanonico`
com o motor:

1. proveniência portátil do cache JSON;
2. suficiência temporal explícita da série CDI.

A entrega não conecta o estado ao motor, não gera pacotes, não executa
`argmax` e não altera ledger, console operacional ou XLSX.

## 2. Proveniência portátil

A identidade do cache passa a ser registrada por cinco evidências separadas:

- `sha256_fisico`: bytes observados no working tree;
- `sha256_semantico`: JSON canônico, independente de EOL, indentação e ordem
  das chaves;
- `git_blob_sha`: identidade do blob versionado no `HEAD`;
- `formato_eol`: `lf`, `crlf`, `cr`, misto ou sem quebra;
- `status_git`: alterações locais detectadas para o arquivo.

O hash semântico usa `json_canonico_v1`:

```text
UTF-8
sort_keys=true
separators=(",", ":")
allow_nan=false
```

O hash físico permanece como diagnóstico local e não deve ser usado sozinho
para comparar ambientes.

## 3. Gate temporal CDI

O resultado usa quatro classificações formais:

- `suficiente`;
- `dia_sem_observacao`;
- `defasagem_admissivel`;
- `fator_requerido_ausente`.

A ausência de fator em uma data explicitamente requerida é bloqueante, salvo
quando a data também estiver explicitamente declarada como sem observação
permitida.

Nesta fundação, ainda não existem datas requeridas pelo motor. O gate avalia
apenas as bordas da série real com:

```text
max_lacuna_inicial_dias = 1
max_defasagem_dias = 2
```

Quando o motor começar a valorar pacotes, cada data efetivamente usada deverá
ser fornecida em `datas_requeridas`.

## 4. Testes adversariais

A entrega comprova:

1. JSON LF e CRLF têm hashes físicos diferentes;
2. JSON LF e CRLF semanticamente equivalentes têm o mesmo hash canônico;
3. alteração real de valor muda o hash canônico;
4. auditoria resolve `git_blob_sha` e status limpo;
5. JSON inválido reprova a identidade semântica;
6. bordas atuais do CDI são classificadas sem bloqueio;
7. cobertura integral resulta em `suficiente`;
8. fator requerido ausente bloqueia;
9. dia sem observação explicitamente permitido não bloqueia;
10. defasagem acima da tolerância bloqueia;
11. fator inválido em data requerida bloqueia.

## 5. Validação

```bash
python -m unittest -v \
  tests.test_proveniencia_portatil \
  tests.test_suficiencia_temporal_cdi

python -B scripts/validacao/validar_bloco2_fundacao_entrada.py
```

Artefato:

```text
saidas/diagnostico/bloco2_fundacao_entrada.json
```

## 6. Critérios para avançar

- todos os testes aprovados;
- proveniência semântica válida;
- cache sem alterações locais;
- `git_blob_sha` resolvido;
- gate temporal com `ok=true` nos dados homologados;
- qualquer data requerida ausente produz bloqueio;
- nenhuma decisão econômica é executada nesta entrega.

Somente após esse fechamento o `EstadoEconomicoCanonico` poderá ser conectado
como entrada única do motor em alteração separada.
