-- DDL inicial para o data warehouse de ilhas de calor

CREATE TABLE IF NOT EXISTS clima_horario_bronze (
    id SERIAL PRIMARY KEY,
    cidade TEXT NOT NULL,
    estacao TEXT,
    data_hora TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    temperatura NUMERIC,
    umidade NUMERIC,
    vento NUMERIC,
    pressao NUMERIC
);

CREATE INDEX IF NOT EXISTS idx_clima_horario_bronze_cidade_data ON clima_horario_bronze (cidade, data_hora);

CREATE TABLE IF NOT EXISTS clima_diario_gold (
    id SERIAL PRIMARY KEY,
    cidade TEXT NOT NULL,
    data DATE NOT NULL,
    temp_max NUMERIC,
    temp_min NUMERIC,
    temp_media NUMERIC,
    dias_calor_extremo INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS indicadores_cidade_gold (
    id SERIAL PRIMARY KEY,
    cidade TEXT NOT NULL,
    risco_calor NUMERIC,
    ilhas_calor_detectadas INTEGER,
    atualizacao TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
