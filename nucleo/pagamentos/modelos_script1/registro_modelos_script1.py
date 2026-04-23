from __future__ import annotations

from nucleo.pagamentos.modelos_script1.contrato_modelos_script1 import HeuristicaScript1Contratada


HEURISTICAS_SCRIPT1_PRIORITARIAS = (
    HeuristicaScript1Contratada(
        codigo='score_hibrido_5p_fonte',
        nome='Score híbrido 5P por fonte',
        fase_absorcao=1,
        papel_inicial='score_auxiliar_por_fonte',
        origem_legado='resolver_hibrido_5p_shadow',
        objetivo_economico='Ranques econômicos mais coerentes entre fontes elegíveis.',
        ativo_para_implementacao=True,
        usar_como_score_auxiliar=True,
        observacao='Primeira heurística a ser integrada ao alocador.',
    ),
    HeuristicaScript1Contratada(
        codigo='penalidade_cliff_idade',
        nome='Penalidade de cliff e idade tributária',
        fase_absorcao=1,
        papel_inicial='desempate_fiscal_tributario',
        origem_legado='resolver_hibrido_5p_shadow',
        objetivo_economico='Evitar resgates em ponto fiscalmente ruim quando a diferença terminal for pequena.',
        ativo_para_implementacao=True,
        usar_como_desempate=True,
        observacao='Entra junto com o score híbrido 5P.',
    ),
    HeuristicaScript1Contratada(
        codigo='oportunidade_vpl_marginal',
        nome='Oportunidade VPL marginal',
        fase_absorcao=1,
        papel_inicial='reforco_terminal_marginal',
        origem_legado='resolver_hibrido_5p_shadow',
        objetivo_economico='Distinguir cobertura local de cobertura economicamente correta.',
        ativo_para_implementacao=True,
        usar_como_score_auxiliar=True,
        observacao='Reforça a visão terminal do alocador.',
    ),
    HeuristicaScript1Contratada(
        codigo='seletor_modo_individual_ou_combinado',
        nome='Seletor de modo individual ou combinado',
        fase_absorcao=2,
        papel_inicial='abertura_controlada_da_combinacao_minima',
        origem_legado='benchmark_agrupado_individual_shadow',
        objetivo_economico='Abrir combinação mínima apenas quando houver ganho plausível.',
        ativo_para_implementacao=False,
        usar_como_filtro_triagem=True,
        abrir_combinacao_minima=True,
        observacao='Só entra após estabilização das heurísticas da fase 1.',
    ),
    HeuristicaScript1Contratada(
        codigo='triagem_topk_fontes_combinacao',
        nome='Triagem top-k de fontes para combinação',
        fase_absorcao=2,
        papel_inicial='controle_combinatorio',
        origem_legado='resolver_hibrido_5p_shadow',
        objetivo_economico='Reduzir custo combinatório sem abrir solver pesado.',
        ativo_para_implementacao=False,
        usar_como_filtro_triagem=True,
        observacao='Fica para a fase 2 junto com o seletor de modo.',
    ),
)


def listar_heuristicas_script1_prioritarias() -> list[dict[str, object]]:
    return [item.para_dict() for item in HEURISTICAS_SCRIPT1_PRIORITARIAS]
