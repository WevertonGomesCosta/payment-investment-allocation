# 03_decisao_reexecucao_numerica.md — RD-2026-04-28-04

## Classificação final obrigatória
**MANIFESTO_CORRIGIDO_MAS_AMBIENTE_BLOQUEADO**

## Justificativa
1. `scipy` foi adicionado ao manifesto principal (`requirements.txt`).
2. A microetapa não alterou motor econômico nem lógica funcional do projeto.
3. A instalação `pip install -r requirements.txt` continua bloqueada por proxy/rede (`403 Forbidden`) especificamente no pacote `scipy`.
4. O smoke test `python -c "import scipy"` falha no ambiente atual por ausência do pacote.

## Conclusão de continuidade
- A correção de governança da dependência foi concluída.
- A reexecução numérica N2–N11 depende de ambiente com acesso/liberação para instalar `scipy` (ou imagem com pacote pré-instalado).
