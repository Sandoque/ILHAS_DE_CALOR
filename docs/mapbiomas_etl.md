# MapBiomas ETL

## Fonte
- XLSX oficial: https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_10/lulc/statistics/MAPBIOMAS_BRAZIL-COL.10-BIOME_STATE_MUNICIPALITY.xlsx
- Sheet usada: `COVERAGE_10`
- Anos: 2010–2024
- Estado: Pernambuco
- Classes mantidas: Urban Infrastructure; Forest (todas); Water; Agriculture (todas); Pasture.

## Pipeline
1. `etl/mapbiomas/download_mapbiomas.py` – baixa o XLSX para `data/mapbiomas/raw/`.
2. `etl/mapbiomas/extract_relevant_sheets.py` – carrega a aba COVERAGE_10.
3. `etl/mapbiomas/filter_pernambuco.py` – filtra state == "Pernambuco".
4. `etl/mapbiomas/filter_municipios_inmet.py` – filtra `geocode` pertencente aos municípios presentes no `climate_hourly` (consulta DB).
5. `etl/mapbiomas/normalize_mapbiomas.py` – filtra classes importantes e pivota anos 2010..2024 para formato tidy (`year`, `area`).
6. `etl/mapbiomas/load_to_postgres.py` – truncates + insere em `public.mapbiomas_coverage`.
7. Orquestração: `etl/mapbiomas/run_mapbiomas_pipeline.py`.

## Como executar
- Via CLI já existente:
```bash
python -m etl.pipeline.cli run-mapbiomas
```

- Variáveis de ambiente relevantes:
  - `DATABASE_URL` – conexão PostgreSQL (aponta para o serviço postgres no Compose em produção).
  - `DATA_DIR` – base dos dados (default `/app/data/inmet`, MapBiomas usa `/app/data/mapbiomas`).
  - `START_YEAR`/`END_YEAR` podem ser ignorados aqui; o módulo fixa 2010–2024.

## Consulta no banco
Tabela alvo: `public.mapbiomas_coverage`

Campos:
- `geocode` (int)
- `municipality` (text)
- `state` (text)
- `class` (text)
- `class_level_0` .. `class_level_4` (text)
- `year` (int)
- `area` (float)

Exemplos:
```sql
SELECT * FROM public.mapbiomas_coverage WHERE year = 2024 LIMIT 10;

-- Área urbana por município em 2024
SELECT municipality, SUM(area) AS area_urbana
FROM public.mapbiomas_coverage
WHERE class LIKE 'Urban Infrastructure%' AND year = 2024
GROUP BY municipality
ORDER BY area_urbana DESC;
```
