BEGIN;

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
    perc_idosos        NUMERIC(5,2),   -- percentual de população idosa
    renda_media        NUMERIC(12,2),  -- renda média, se quisermos
    UNIQUE (nome_cidade, uf)
);

-- Estações meteorológicas INMET (apenas as de PE)
CREATE TABLE IF NOT EXISTS dim_estacao (
    id_estacao      SERIAL PRIMARY KEY,
    codigo_estacao  VARCHAR(10)  NOT NULL,   -- ex: A307
    nome_estacao    VARCHAR(150) NOT NULL,   -- ex: PETROLINA
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
-- BRONZE: DADOS CLIMÁTICOS HORÁRIOS (TIPADOS, LIMPOS O SUFICIENTE)
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
-- GOLD: MÉTRICAS DIÁRIAS POR CIDADE (agregadas do bronze)
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_clima_pe_diario (
    id                      SERIAL PRIMARY KEY,
    id_cidade               INTEGER NOT NULL REFERENCES dim_cidade_pe(id_cidade),
    data                    DATE NOT NULL,

    temp_media              NUMERIC(5,2),
    temp_max                NUMERIC(5,2),
    temp_min                NUMERIC(5,2),
    umidade_media           NUMERIC(5,2),
    precipitacao_total      NUMERIC(10,2),
    radiacao_total          NUMERIC(12,2),
    amplitude_termica       NUMERIC(5,2),
    aparente_media          NUMERIC(5,2),
    heat_index_max          NUMERIC(5,2),
    rolling_heat_7d         NUMERIC(5,2),
    risco_calor             VARCHAR(20),

    criado_em               TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (id_cidade, data)
);

CREATE INDEX IF NOT EXISTS idx_gold_diario_cidade_data
    ON gold_clima_pe_diario (id_cidade, data);

CREATE INDEX IF NOT EXISTS idx_gold_diario_risco
    ON gold_clima_pe_diario (risco_calor, data);

-- ============================================================================
-- GOLD: MÉTRICAS DIÁRIAS POR CIDADE (tabela legada, anterior)
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

    -- flags para facilitar análises
    dia_calor_extremo    BOOLEAN,   -- true se o dia atingir critério X de calor
    noite_quente         BOOLEAN,   -- true se a mínima noturna for alta

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
-- AUXILIARES: COBERTURA VEGETAL E DEMOGRAFIA (IBGE / MAPBIOMAS)
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
-- GOLD: ÍNDICE COMPOSTO DE RISCO DE CALOR
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_indice_risco_calor_cidade (
    id_risco        BIGSERIAL PRIMARY KEY,
    id_cidade       INTEGER NOT NULL REFERENCES dim_cidade_pe(id_cidade),
    ano             SMALLINT NOT NULL,
    mes             SMALLINT,  -- opcional: se quiser risco mensal; se for anual, mantenha NULL

    indice_risco    NUMERIC(5,2) NOT NULL,  -- 0–100
    categoria       VARCHAR(20),            -- 'Baixo', 'Médio', 'Alto', 'Crítico'

    -- componentes do índice para explicar o score
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
-- VIEW PARA O DASHBOARD: RESUMO POR CIDADE / ANO / MÊS
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

-- ============================================================================
-- STATIONS (Tabela usada pelo ETL INMET)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.stations (
    station_code TEXT PRIMARY KEY,
    name TEXT,
    state TEXT,
    municipality TEXT,
    latitude FLOAT,
    longitude FLOAT,
    altitude FLOAT,
    geocode BIGINT
);

-- ============================================================================
-- TABELA CLIMATE_HOURLY (BRONZE OFICIAL DO ETL INMET)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.climate_hourly (
    id BIGSERIAL PRIMARY KEY,

    datetime_utc TIMESTAMP NOT NULL,
    date DATE GENERATED ALWAYS AS (datetime_utc::date) STORED,
    hour_utc TEXT,

    station_code TEXT REFERENCES public.stations(station_code),

    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    radiation FLOAT,
    precipitation FLOAT,

    apparent_temperature FLOAT,
    heat_index FLOAT,
    thermal_amplitude FLOAT,
    rolling_heat_7d FLOAT,

    latitude FLOAT,
    longitude FLOAT,
    altitude FLOAT,

    municipality TEXT,
    municipality_geocode BIGINT
);

CREATE INDEX IF NOT EXISTS idx_climate_station_date
    ON public.climate_hourly (station_code, date);

CREATE INDEX IF NOT EXISTS idx_climate_date
    ON public.climate_hourly (date);

-- ============================================================================
-- MAPBIOMAS COVERAGE (NORMALIZADO)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.mapbiomas_coverage (
    id BIGSERIAL PRIMARY KEY,

    geocode BIGINT NOT NULL,
    municipality TEXT,
    state TEXT,

    class TEXT,
    class_level_0 TEXT,
    class_level_1 TEXT,
    class_level_2 TEXT,
    class_level_3 TEXT,
    class_level_4 TEXT,

    year SMALLINT NOT NULL,
    area NUMERIC(20,4),

    UNIQUE (geocode, class, year)
);

CREATE INDEX IF NOT EXISTS idx_mapb_year
    ON public.mapbiomas_coverage (year);

CREATE INDEX IF NOT EXISTS idx_mapb_geocode
    ON public.mapbiomas_coverage (geocode);


COMMIT;
