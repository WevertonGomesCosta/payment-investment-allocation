# Auditoria arquitetural da V3

## Objetivo desta reconstrução

Esta versão não amplia o domínio financeiro do projeto. Ela apenas reconstrói a
baseline para deixá-la mais coerente com a regra de auditoria por
**responsabilidade real**, e não por módulo físico herdado dos scripts-base.

## Problemas identificados na V2 revisada

1. A estrutura já sugeria diretórios futuros como `motores/`, `estrategias/` e
   `adapters/` antes de termos mapeado suficientemente as responsabilidades
   reais nos scripts-base.
2. Parte importante da base ainda estava nomeada em inglês, o que contrariava a
   diretriz de manter o projeto em português.
3. O carregador de config estava funcional, mas ainda subrepresentava a lógica
   auditada do Script 1 para descoberta e priorização de arquivos de config.
4. A base ainda precisava ficar mais neutra, para evitar que a própria árvore
   do repositório induzisse modularização prematura.

## Decisões aplicadas nesta reconstrução

- A árvore do projeto foi reduzida a uma base mais neutra e menor.
- Os módulos iniciais foram renomeados para português.
- O repositório passou a usar `dados/`, `saidas/`, `relatorios/` e `testes/`.
- O núcleo inicial ficou restrito a:
  - `nucleo/ambiente.py`
  - `nucleo/carregador_config.py`
  - `nucleo/leitor_planilha.py`
- O carregador de config passou a aceitar:
  - lista ordenada de nomes candidatos;
  - variável de ambiente do projeto;
  - compatibilidade com `OTIMIZADOR_CONFIG`.
- O leitor da planilha permanece restrito à leitura estrutural e canonização
  inicial de colunas.

## O que esta versão deliberadamente não faz

- não cria entidades finais de domínio;
- não cria motor de pagamentos;
- não cria motor de switching;
- não cria adaptadores remotos ainda;
- não cria contrato operacional final;
- não altera o núcleo financeiro.

## Interpretação correta da V3

A V3 deve ser entendida como uma **reconstrução da baseline**, não como uma
expansão funcional do projeto.
