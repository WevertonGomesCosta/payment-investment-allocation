# ME-14 — Pipeline de Machine Learning para importância de marcadores em arroz
# Projeto: rice-gwas-ml-marker-identification
# Escopo: preparar X, y e grade de modelos ML. Sem executar Machine Learning por padrão.

message("=== ME-14: pipeline de Machine Learning para importância de marcadores em arroz ===")

# Controle operacional: manter FALSE durante builds e validações leves.
executar_machine_learning <- FALSE

arquivo_fenotipos <- "output/dados/fenotipos_preparados.csv"
arquivo_genotipos <- "output/dados/genotipos_preparados.rds"
arquivo_mapa_regioes <- "output/dados/mapa_snps_regioes_069mb.csv"

pasta_ml <- "output/ml"
pasta_entrada_ml <- file.path(pasta_ml, "entrada_modelos")
pasta_resultados_brutos <- file.path(pasta_ml, "resultados_brutos")
pasta_resultados_consolidados <- file.path(pasta_ml, "resultados_consolidados")

if (!dir.exists("output")) {
  dir.create("output", recursive = TRUE)
}

if (!dir.exists(pasta_ml)) {
  dir.create(pasta_ml, recursive = TRUE)
}

if (!dir.exists(pasta_entrada_ml)) {
  dir.create(pasta_entrada_ml, recursive = TRUE)
}

if (!dir.exists(pasta_resultados_brutos)) {
  dir.create(pasta_resultados_brutos, recursive = TRUE)
}

if (!dir.exists(pasta_resultados_consolidados)) {
  dir.create(pasta_resultados_consolidados, recursive = TRUE)
}

arquivos_entrada_ml <- data.frame(
  arquivo = c(arquivo_fenotipos, arquivo_genotipos, arquivo_mapa_regioes),
  papel = c(
    "fenótipos preparados pelo módulo de dados",
    "genótipos preparados pelo módulo de dados",
    "mapa físico com regiões de 0,69 Mb"
  ),
  existe = c(
    file.exists(arquivo_fenotipos),
    file.exists(arquivo_genotipos),
    file.exists(arquivo_mapa_regioes)
  ),
  stringsAsFactors = FALSE
)

write.csv(
  arquivos_entrada_ml,
  file = file.path(pasta_ml, "checagem_arquivos_entrada_ml.csv"),
  row.names = FALSE
)

if (!all(arquivos_entrada_ml$existe)) {
  message("Arquivos de entrada ausentes. Execute primeiro code/01_preparar_dados_arroz.R.")
  print(arquivos_entrada_ml)
} else {
  message("Lendo saídas consolidadas do módulo de dados.")

  fenotipos_preparados <- read.csv(
    arquivo_fenotipos,
    stringsAsFactors = FALSE,
    check.names = FALSE
  )

  genotipos_preparados <- readRDS(arquivo_genotipos)

  mapa_snps_regioes <- read.csv(
    arquivo_mapa_regioes,
    stringsAsFactors = FALSE,
    check.names = FALSE
  )

  message("Alinhando fenótipos, genótipos e mapa regional para Machine Learning.")

  ids_fenotipos <- as.character(fenotipos_preparados$individuo)
  ids_genotipos <- rownames(genotipos_preparados)

  if (is.null(ids_genotipos)) {
    ids_genotipos <- ids_fenotipos
    rownames(genotipos_preparados) <- ids_genotipos
  }

  ids_comuns <- ids_fenotipos[ids_fenotipos %in% ids_genotipos]

  fenotipos_ml <- fenotipos_preparados[fenotipos_preparados$individuo %in% ids_comuns, ]
  fenotipos_ml <- fenotipos_ml[match(ids_comuns, fenotipos_ml$individuo), ]

  genotipos_ml <- genotipos_preparados[ids_comuns, , drop = FALSE]

  marcadores_genotipos <- colnames(genotipos_ml)
  marcadores_mapa <- as.character(mapa_snps_regioes$marcador)
  marcadores_comuns <- marcadores_mapa[marcadores_mapa %in% marcadores_genotipos]

  mapa_ml <- mapa_snps_regioes[mapa_snps_regioes$marcador %in% marcadores_comuns, ]
  mapa_ml <- mapa_ml[match(marcadores_comuns, mapa_ml$marcador), ]
  genotipos_ml <- genotipos_ml[, marcadores_comuns, drop = FALSE]

  X_marcadores <- as.data.frame(genotipos_ml, check.names = FALSE)
  rownames(X_marcadores) <- ids_comuns

  colunas_fenotipos <- setdiff(colnames(fenotipos_ml), "individuo")
  metodos_ml <- c("RF", "Bagging", "Boosting", "DT", "MARS")

  grade_execucao_ml <- expand.grid(
    fenotipo = colunas_fenotipos,
    metodo_ml = metodos_ml,
    stringsAsFactors = FALSE
  )

  grade_execucao_ml$arquivo_y <- paste0(
    "output/ml/entrada_modelos/y_",
    grade_execucao_ml$fenotipo,
    ".csv"
  )

  grade_execucao_ml$pasta_resultado_bruto <- paste0(
    "output/ml/resultados_brutos/",
    grade_execucao_ml$fenotipo,
    "/",
    grade_execucao_ml$metodo_ml
  )

  grade_execucao_ml$status_execucao <- "planejado_nao_executado"

  message("Gravando matriz X, vetores y e grade de modelos ML.")

  saveRDS(X_marcadores, file.path(pasta_entrada_ml, "X_marcadores_arroz.rds"))
  write.csv(mapa_ml, file.path(pasta_entrada_ml, "mapa_marcadores_regioes_ml.csv"), row.names = FALSE)

  for (nome_fenotipo in colunas_fenotipos) {
    y <- data.frame(
      individuo = fenotipos_ml$individuo,
      valor = fenotipos_ml[[nome_fenotipo]],
      stringsAsFactors = FALSE
    )
    colnames(y) <- c("individuo", nome_fenotipo)

    write.csv(
      y,
      file = file.path(pasta_entrada_ml, paste0("y_", nome_fenotipo, ".csv")),
      row.names = FALSE
    )
  }

  resumo_entrada_ml <- data.frame(
    item = c(
      "n_individuos_fenotipos",
      "n_individuos_genotipos",
      "n_individuos_alinhados",
      "n_fenotipos",
      "n_marcadores_genotipos",
      "n_marcadores_mapa_regionalizado",
      "n_marcadores_alinhados",
      "n_modelos_ml",
      "n_execucoes_planejadas",
      "executar_machine_learning"
    ),
    valor = c(
      length(ids_fenotipos),
      length(ids_genotipos),
      length(ids_comuns),
      length(colunas_fenotipos),
      length(marcadores_genotipos),
      length(marcadores_mapa),
      length(marcadores_comuns),
      length(metodos_ml),
      nrow(grade_execucao_ml),
      executar_machine_learning
    ),
    stringsAsFactors = FALSE
  )

  parametros_ml <- data.frame(
    parametro = c(
      "modelos_ml",
      "formato_X",
      "formato_y",
      "unidade_regional",
      "proporcao_treino_padrao",
      "numero_arvores_padrao",
      "saida_bruta",
      "execucao_no_build_workflowr"
    ),
    valor = c(
      paste(metodos_ml, collapse = ", "),
      "X: linhas como indivíduos e colunas como SNPs em codificação 0/1/2",
      "y: primeira coluna indivíduo, segunda coluna fenótipo",
      "região física de 0,69 Mb definida no módulo de dados",
      "0.80",
      "500",
      "output/ml/resultados_brutos/fenotipo/metodo_ml/",
      "não"
    ),
    stringsAsFactors = FALSE
  )

  write.csv(
    grade_execucao_ml,
    file = file.path(pasta_ml, "grade_execucao_machine_learning.csv"),
    row.names = FALSE
  )

  write.csv(
    resumo_entrada_ml,
    file = file.path(pasta_ml, "resumo_entrada_machine_learning.csv"),
    row.names = FALSE
  )

  write.csv(
    parametros_ml,
    file = file.path(pasta_ml, "parametros_machine_learning.csv"),
    row.names = FALSE
  )

  message("Resumo da entrada Machine Learning:")
  print(resumo_entrada_ml)

  if (executar_machine_learning) {
    message("Execução de Machine Learning ativada. Esta etapa pode ser demorada e não deve ocorrer durante o build do workflowr.")

    pacote_randomForest <- requireNamespace("randomForest", quietly = TRUE)
    pacote_gbm <- requireNamespace("gbm", quietly = TRUE)
    pacote_rpart <- requireNamespace("rpart", quietly = TRUE)
    pacote_earth <- requireNamespace("earth", quietly = TRUE)

    disponibilidade_pacotes <- data.frame(
      pacote = c("randomForest", "gbm", "rpart", "earth"),
      disponivel = c(pacote_randomForest, pacote_gbm, pacote_rpart, pacote_earth),
      stringsAsFactors = FALSE
    )

    write.csv(
      disponibilidade_pacotes,
      file = file.path(pasta_ml, "disponibilidade_pacotes_ml.csv"),
      row.names = FALSE
    )

    importancia_todos_modelos <- data.frame()
    metricas_todos_modelos <- data.frame()

    set.seed(123)

    for (i in seq_len(nrow(grade_execucao_ml))) {
      fenotipo_atual <- grade_execucao_ml$fenotipo[i]
      metodo_atual <- grade_execucao_ml$metodo_ml[i]
      pasta_resultado_atual <- grade_execucao_ml$pasta_resultado_bruto[i]

      if (!dir.exists(pasta_resultado_atual)) {
        dir.create(pasta_resultado_atual, recursive = TRUE)
      }

      y_atual <- fenotipos_ml[[fenotipo_atual]]
      individuos_validos <- !is.na(y_atual)
      X_atual <- X_marcadores[individuos_validos, , drop = FALSE]
      y_atual <- y_atual[individuos_validos]

      linhas_completas <- stats::complete.cases(X_atual)
      X_atual <- X_atual[linhas_completas, , drop = FALSE]
      y_atual <- y_atual[linhas_completas]

      n_validos <- length(y_atual)
      n_treino <- floor(0.80 * n_validos)
      indices_treino <- sample(seq_len(n_validos), size = n_treino)
      indices_teste <- setdiff(seq_len(n_validos), indices_treino)

      X_treino <- X_atual[indices_treino, , drop = FALSE]
      y_treino <- y_atual[indices_treino]
      X_teste <- X_atual[indices_teste, , drop = FALSE]
      y_teste <- y_atual[indices_teste]

      dados_treino <- data.frame(y = y_treino, X_treino, check.names = FALSE)
      dados_teste <- data.frame(y = y_teste, X_teste, check.names = FALSE)

      tempo_inicial <- Sys.time()
      importancia_modelo <- numeric(ncol(X_atual))
      names(importancia_modelo) <- colnames(X_atual)
      predicao_teste <- rep(NA_real_, length(y_teste))
      status_modelo <- "nao_executado"

      if (metodo_atual == "RF" && pacote_randomForest) {
        modelo <- randomForest::randomForest(
          x = X_treino,
          y = y_treino,
          ntree = 500,
          importance = TRUE
        )
        predicao_teste <- stats::predict(modelo, X_teste)
        importancia_extraida <- randomForest::importance(modelo)
        importancia_modelo[names(importancia_modelo) %in% rownames(importancia_extraida)] <- importancia_extraida[, 1]
        status_modelo <- "executado"
      }

      if (metodo_atual == "Bagging" && pacote_randomForest) {
        modelo <- randomForest::randomForest(
          x = X_treino,
          y = y_treino,
          ntree = 500,
          mtry = ncol(X_treino),
          importance = TRUE
        )
        predicao_teste <- stats::predict(modelo, X_teste)
        importancia_extraida <- randomForest::importance(modelo)
        importancia_modelo[names(importancia_modelo) %in% rownames(importancia_extraida)] <- importancia_extraida[, 1]
        status_modelo <- "executado"
      }

      if (metodo_atual == "Boosting" && pacote_gbm) {
        modelo <- gbm::gbm(
          y ~ .,
          data = dados_treino,
          distribution = "gaussian",
          n.trees = 500,
          interaction.depth = 3,
          shrinkage = 0.01,
          bag.fraction = 0.80,
          train.fraction = 1.00,
          verbose = FALSE
        )
        predicao_teste <- stats::predict(modelo, dados_teste, n.trees = 500)
        importancia_extraida <- summary(modelo, plotit = FALSE)
        importancia_modelo[importancia_extraida$var] <- importancia_extraida$rel.inf
        status_modelo <- "executado"
      }

      if (metodo_atual == "DT" && pacote_rpart) {
        modelo <- rpart::rpart(
          y ~ .,
          data = dados_treino,
          method = "anova"
        )
        predicao_teste <- stats::predict(modelo, dados_teste)
        if (!is.null(modelo$variable.importance)) {
          importancia_modelo[names(modelo$variable.importance)] <- modelo$variable.importance
        }
        status_modelo <- "executado"
      }

      if (metodo_atual == "MARS" && pacote_earth) {
        modelo <- earth::earth(
          x = as.matrix(X_treino),
          y = y_treino
        )
        predicao_teste <- stats::predict(modelo, newdata = as.matrix(X_teste))
        importancia_extraida <- earth::evimp(modelo)
        variaveis_importantes <- rownames(importancia_extraida)
        variaveis_importantes <- variaveis_importantes[variaveis_importantes %in% names(importancia_modelo)]
        importancia_modelo[variaveis_importantes] <- importancia_extraida[variaveis_importantes, 1]
        status_modelo <- "executado"
      }

      tempo_final <- Sys.time()

      if (all(is.na(predicao_teste))) {
        rmse <- NA_real_
        correlacao <- NA_real_
      } else {
        rmse <- sqrt(mean((y_teste - predicao_teste)^2, na.rm = TRUE))
        correlacao <- stats::cor(y_teste, predicao_teste, use = "complete.obs")
      }

      importancia_atual <- data.frame(
        fenotipo = fenotipo_atual,
        metodo_ml = metodo_atual,
        marcador = names(importancia_modelo),
        importancia_bruta = as.numeric(importancia_modelo),
        stringsAsFactors = FALSE
      )

      importancia_atual <- merge(
        importancia_atual,
        mapa_ml,
        by = "marcador",
        all.x = TRUE,
        sort = FALSE
      )

      importancia_atual$importancia_padronizada <- NA_real_
      importancia_positiva <- importancia_atual$importancia_bruta
      importancia_positiva[is.na(importancia_positiva)] <- 0

      if (max(abs(importancia_positiva)) > 0) {
        importancia_atual$importancia_padronizada <- importancia_positiva / max(abs(importancia_positiva))
      }

      metricas_atual <- data.frame(
        fenotipo = fenotipo_atual,
        metodo_ml = metodo_atual,
        n_validos = n_validos,
        n_treino = n_treino,
        n_teste = length(indices_teste),
        rmse = rmse,
        correlacao = correlacao,
        status_modelo = status_modelo,
        tempo_inicial = as.character(tempo_inicial),
        tempo_final = as.character(tempo_final),
        tempo_minutos = as.numeric(difftime(tempo_final, tempo_inicial, units = "mins")),
        stringsAsFactors = FALSE
      )

      write.csv(
        importancia_atual,
        file = file.path(pasta_resultado_atual, "importancia_marcadores.csv"),
        row.names = FALSE
      )

      write.csv(
        metricas_atual,
        file = file.path(pasta_resultado_atual, "metricas_predicao.csv"),
        row.names = FALSE
      )

      importancia_todos_modelos <- rbind(importancia_todos_modelos, importancia_atual)
      metricas_todos_modelos <- rbind(metricas_todos_modelos, metricas_atual)
      grade_execucao_ml$status_execucao[i] <- status_modelo
    }

    write.csv(
      importancia_todos_modelos,
      file = file.path(pasta_resultados_consolidados, "importancia_marcadores_ml.csv"),
      row.names = FALSE
    )

    write.csv(
      metricas_todos_modelos,
      file = file.path(pasta_resultados_consolidados, "metricas_modelos_ml.csv"),
      row.names = FALSE
    )

    if (nrow(importancia_todos_modelos) > 0) {
      importancia_regional_ml <- aggregate(
        importancia_padronizada ~ fenotipo + metodo_ml + cromossomo + id_regiao + inicio_regiao + fim_regiao,
        data = importancia_todos_modelos,
        FUN = mean,
        na.rm = TRUE
      )

      colnames(importancia_regional_ml)[7] <- "importancia_regional_media"

      write.csv(
        importancia_regional_ml,
        file = file.path(pasta_resultados_consolidados, "importancia_regional_ml.csv"),
        row.names = FALSE
      )
    }

    write.csv(
      grade_execucao_ml,
      file = file.path(pasta_ml, "grade_execucao_machine_learning.csv"),
      row.names = FALSE
    )
  }

  message("ME-14 concluída: entradas e grade de modelos ML preparadas sem executar Machine Learning por padrão.")
}
