# VALIDAÇÃO LOCAL — V225

## Natureza da versão

A V225 é uma versão de formalização de baseline. A lógica funcional é herdada da V224.

## Comandos recomendados

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v223.py --real
python scripts/diagnostico/auditar_gate_economico_aportes_v223.py --real
python scripts/diagnostico/auditoria_final_pre_baseline_v223.py
python scripts/diagnostico/verificar_release_limpo.py
```

## Critério de aprovação

A V225 é aprovada se:

- a auditoria de impacto processar os cenários reais;
- o gate econômico manter bloqueio quando o cenário com aporte for inferior;
- a auditoria final tiver `falhas: 0`;
- o release limpo validar a versão;
- não houver alteração de lógica nos módulos centrais em relação à V224.

## Resultado esperado

```text
OK - release baseline validado para V225
```


## Validação estática nesta geração

- baseline_doc_presente: OK
- promocao_doc_presente: OK
- validacao_doc_presente: OK
- matriz_presente: OK
- hash_logica_presente: OK
- sem_alteracao_logica_central: OK
- sem_pycache: OK
- sem_pyc: OK
- release_limpo_script_presente: OK