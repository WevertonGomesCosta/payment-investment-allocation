# VALIDAÇÃO LOCAL V25

Comandos executados:

```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```

Resultado:
- ambos retornaram 0;
- o replay controlado do passado permaneceu cobrindo 59/59 contas históricas;
- o cache diário do CDI do BCB foi integrado à baseline, mas na validação local o fetch não pôde ser concluído por indisponibilidade de rede/resolução de nome, então o sistema fez fallback controlado para a taxa de modelo;
- a baseline permaneceu estável sem abrir novas camadas econômicas.
