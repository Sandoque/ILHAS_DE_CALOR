-- ============================================================================
-- DIMENSÕES
-- ============================================================================

-- Cidades de Pernambuco
CREATE TABLE IF NOT EXISTS dim_cidade_pe (
    id_cidade          SERIAL PRIMARY KEY,
    nome_cidade        VARCHAR(120) NOT NULL,
    uf                 CHAR(2)      NOT NULL DEFAULT 'PE',
    codigo_ibge        INTEGER,
    latitude           NUMERIC(9,6),
    longitude          NUMERIC(9,6),
    populacao_total    INTEGER,
    densidade_demo     NUMERIC(10,2),
    perc_idosos        NUMERIC(5,2),
    renda_media        NUMERIC(12,2),
    UNIQUE (nome_cidade, uf)
);

-- Estações meteorológicas INMET
CREATE TABLE IF NOT EXISTS dim_estacao (
    id_estacao      SERIAL PRIMARY KEY,
    codigo_estacao  VARCHAR(10)  NOT NULL,
    nome_estacao    VARCHAR(150) NOT NULL,
    uf              CHAR(2)      NOT NULL DEFAULT 'PE',
    municipio       VARCHAR(120),
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6),
    altitude_m      NUMERIC(8,2),
    data_fundacao   DATE,
    id_cidade       INTEGER REFERENCES dim_cidade_pe(id_cidade),
    UNIQUE (codigo_estacao)
);

-- ============================================================================
-- BRONZE: DADOS CLIMÁTICOS HORÁRIOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS bronze_clima_pe_horario (
    id_registro           BIGSERIAL PRIMARY KEY,
    id_estacao            INTEGER NOT NULL REFERENCES dim_estacao(id_estacao),
    data_hora_utc         TIMESTAMPTZ NOT NULL,
    data_hora_local       TIMESTAMP WITHOUT TIME ZONE,
    ano                   SMALLINT NOT NULL,
    mes                   SMALLINT NOT NULL,
    dia                   SMALLINT NOT NULL,
    hora                  SMALLINT NOT NULL,

    precipitacao_mm       NUMERIC(10,2),
    pressao_hpa           NUMERIC(10,1),
    radiacao_kj_m2        NUMERIC(10,1),

    temp_ar_c             NUMERIC(5,2),
    temp_ponto_orvalho_c  NUMERIC(5,2),
    temp_max_ant          NUMERIC(5,2),
    temp_min_ant          NUMERIC(5,2),

    umid_rel_pct          NUMERIC(5,2),
    umid_max_ant          NUMERIC(5,2),
    umid_min_ant          NUMERIC(5,2),

    vento_dir_graus       SMALLINT,
    vento_rajada_ms       NUMERIC(5,2),
    vento_vel_ms          NUMERIC(5,2),

    nome_arquivo_origem   VARCHAR(255),
    linha_arquivo         INTEGER,

    criado_em             TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (id_estacao, data_hora_utc)
);

CREATE INDEX IF NOT EXISTS idx_bronze_estacao_datahora
    ON bronze_clima_pe_horario (id_estacao, data_hora_utc);

CREATE INDEX IF NOT EXISTS idx_bronze_ano_mes_estacao
    ON bronze_clima_pe_horario (ano, mes, id_estacao);

-- ============================================================================
-- GOLD: MÉTRICAS DIÁRIAS POR CIDADE
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_clima_diario_cidade (
    id_diario            BIGSERIAL PRIMARY KEY,
    id_cidade            INTEGER NOT NULL REFERENCES dim_cidade_pe(id_cidade),
    data                 DATE    NOT NULL,
    ano                  SMALLINT NOT NULL,
    mes                  SMALLINT NOT NULL,
    dia                  SMALLINT NOT NULL,

    temp_media_c         NUMERIC(5,2),
    temp_max_c           NUMERIC(5,2),
    temp_min_c           NUMERIC(5,2),
    amplitude_termica_c  NUMERIC(5,2),

    umid_media_pct       NUMERIC(5,2),
    chuva_mm             NUMERIC(10,2),
    rad_total_kj_m2      NUMERIC(12,2),

    dia_calor_extremo    BOOLEAN,
    noite_quente         BOOLEAN,

    criado_em            TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (id_cidade, data)
);

CREATE INDEX IF NOT EXISTS idx_diario_cidade_data
    ON gold_clima_diario_cidade (id_cidade, data);

CREATE INDEX IF NOT EXISTS idx_diario_ano_mes
    ON gold_clima_diario_cidade (ano, mes, id_cidade);

-- ============================================================================
-- GOLD: MÉTRICAS MENSAIS POR CIDADE
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_clima_mensal_cidade (
    id_mensal                 BIGSERIAL PRIMARY KEY,
    id_cidade                 INTEGER NOT NULL REFERENCES dim_cidade_pe(id_cidade),
    ano                       SMALLINT NOT NULL,
    mes                       SMALLINT NOT NULL,

    temp_media_c              NUMERIC(5,2),
    temp_max_media_c          NUMERIC(5,2),
    temp_min_media_c          NUMERIC(5,2),
    amplitude_termica_media_c NUMERIC(5,2),

    umid_media_pct            NUMERIC(5,2),
    chuva_total_mm            NUMERIC(12,2),
    dias_calor_extremo        INTEGER,
    noites_quentes            INTEGER,
    rad_media_kj_m2           NUMERIC(12,2),

    criado_em                 TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (id_cidade, ano, mes)
);

CREATE INDEX IF NOT EXISTS idx_mensal_cidade_ano_mes
    ON gold_clima_mensal_cidade (id_cidade, ano, mes);

-- ============================================================================
-- AUXILIARES: COBERTURA VEGETAL & DEMOGRAFIA
-- ============================================================================

CREATE TABLE IF NOT EXISTS aux_cobertura_vegetal_pe (
    id_registro            SERIAL PRIMARY KEY,
    id_cidade              INTEGER NOT NULL REFERENCES dim_cidade_pe(id_cidade),
    ano                    SMALLINT,
    perc_vegetacao_urbana  NUMERIC(5,2),
    perc_area_construida   NUMERIC(5,2),
    perc_corpos_dagua      NUMERIC(5,2),
    fonte                  VARCHAR(120),
    UNIQUE (id_cidade, ano)
);

CREATE TABLE IF NOT EXISTS aux_demografia_pe (
    id_registro        SERIAL PRIMARY KEY,
    id_cidade          INTEGER NOT NULL REFERENCES dim_cidade_pe(id_cidade),
    ano                SMALLINT,
    populacao_total    INTEGER,
    densidade_demo     NUMERIC(10,2),
    perc_idosos        NUMERIC(5,2),
    renda_media        NUMERIC(12,2),
    fonte              VARCHAR(120),
    UNIQUE (id_cidade, ano)
);

-- ============================================================================
-- ÍNDICE COMPOSTO DE RISCO DE CALOR
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_indice_risco_calor_cidade (
    id_risco        BIGSERIAL PRIMARY KEY,
    id_cidade       INTEGER NOT NULL REFERENCES dim_cidade_pe(id_cidade),
    ano             SMALLINT NOT NULL,
    mes             SMALLINT,

    indice_risco    NUMERIC(5,2) NOT NULL,
    categoria       VARCHAR(20),

    score_temp          NUMERIC(5,2),
    score_vegetacao     NUMERIC(5,2),
    score_densidade     NUMERIC(5,2),
    score_idosos        NUMERIC(5,2),
    score_outros        NUMERIC(5,2),

    criado_em       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (id_cidade, ano, mes)
);

CREATE INDEX IF NOT EXISTS idx_risco_cidade_ano_mes
    ON gold_indice_risco_calor_cidade (id_cidade, ano, mes);

CREATE INDEX IF NOT EXISTS idx_risco_ano_mes
    ON gold_indice_risco_calor_cidade (ano, mes, indice_risco DESC);

-- ============================================================================
-- VIEW PRINCIPAL PARA O DASHBOARD
-- ============================================================================

CREATE OR REPLACE VIEW vw_dashboard_risco_cidade AS
SELECT
    c.id_cidade,
    c.nome_cidade,
    c.uf,
    r.ano,
    r.mes,
    r.indice_risco,
    r.categoria,

    gm.temp_max_media_c,
    gm.dias_calor_extremo,
    gm.noites_quentes,

    d.populacao_total,
    d.densidade_demo,
    d.perc_idosos,
    cv.perc_vegetacao_urbana,
    cv.perc_area_construida

FROM gold_indice_risco_calor_cidade r
JOIN dim_cidade_pe c
    ON c.id_cidade = r.id_cidade
LEFT JOIN gold_clima_mensal_cidade gm
    ON gm.id_cidade = r.id_cidade
   AND gm.ano       = r.ano
   AND gm.mes       = r.mes
LEFT JOIN aux_demografia_pe d
    ON d.id_cidade  = r.id_cidade
   AND d.ano        = r.ano
LEFT JOIN aux_cobertura_vegetal_pe cv
    ON cv.id_cidade = r.id_cidade
   AND cv.ano       = r.ano;
