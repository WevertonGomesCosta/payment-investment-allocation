# ME-V17-F0-V4O.0a

Microetapa executavel de diagnostico sem alteracao observavel.

Arquivo criado:

scripts/diagnostico/auditar_lote_3120_mai_replay_vs_saida_v4o0a.py

Validacao local esperada:

python -m py_compile scripts/diagnostico/auditar_lote_3120_mai_replay_vs_saida_v4o0a.py
python scripts/diagnostico/auditar_lote_3120_mai_replay_vs_saida_v4o0a.py --saldo-app 50 --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
