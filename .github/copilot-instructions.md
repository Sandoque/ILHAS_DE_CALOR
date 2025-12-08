# Instruções para Agentes IA – Observatório Estadual de Ilhas de Calor – PE

## Visão Geral da Arquitetura

Este é um projeto full-stack para monitoramento de ilhas de calor em Pernambuco:

- **Backend**: Flask REST API + web pages com HTMX/ECharts (porta 8000/5000)
- **ETL**: Pipeline Python que baixa dados climáticos do INMET, normaliza, calcula métricas de calor e carrega no PostgreSQL
- **Dados**: PostgreSQL 15 contendo tabelas de dimensão (estações, cidades), dados climáticos horários e métricas derivadas
- **Frontend**: Templates Jinja2 com HTMX para interatividade e ECharts para visualizações

## Fluxo de Dados

1. **ETL (`etl/`)** → Baixa CSVs anuais do INMET → Normaliza para schema canônico → Calcula métricas (`apparent_temperature`, `heat_index`, `thermal_amplitude`, `rolling_heat_7d`) → Carrega em `public.climate_hourly`
2. **API (`backend/app/routes/`)** → Consulta dados via SQLAlchemy ORM → Serializa com Marshmallow → Retorna JSON
3. **Web (`backend/app/templates/`)** → Renderiza views Jinja2 → HTMX/JS fazem requisições aos endpoints `/api`

## Estrutura do Projeto

```
backend/
  app/
    models/        # SQLAlchemy ORM: ClimateHourly, Station, Metrics
    routes/        # Flask Blueprints: API endpoints + web pages
    services/      # Lógica de negócio (station_service, climate_service, etc)
    utils/         # Helpers: responses.py (success/error), pagination, exceptions
    templates/     # Jinja2 + HTMX
    static/        # CSS (Tailwind custom), JS (charts.js, heatmap.js, simulator.js)
  requirements.txt # Flask, SQLAlchemy, Marshmallow, psycopg2, pandas
  run.py          # Entry point: app.run()
etl/
  pipeline/cli.py  # CLI entrypoint: python -m etl.pipeline.cli run-full|run-inc
  ingest/         # Download ZIP files from INMET
  transform/      # Normalize CSVs, compute heat metrics
  load/           # Validate schema, append to PostgreSQL
  utils/          # Logger, timers, constants
db/
  schema.sql      # Star schema: dim_estacao, dim_cidade_pe, bronze/silver/gold tables
```

## Convenções do Projeto

### Backend (Flask)

- **Factory pattern**: `app.create_app()` em `backend/app/__init__.py` retorna app configurado
- **Config via env**: Todas as vars em `backend/app/config.py` (DATABASE_URL, SECRET_KEY, DEBUG)
- **Blueprints**: Organizar rotas por domínio (api.py, api_climate.py, api_stations.py, api_simulation.py, api_analytics.py)
- **Response standard**: Use `utils.responses.success(data)` ou `.error(msg)` – sempre retornam `{"success": bool, "data"/"error": ...}`
- **Serviços**: Lógica de negócio em `services/` – modelos consultan via `extensions.db`, serviços transformam e retornam dicts
- **Schemas Marshmallow**: Um `Schema` por modelo ORM para serialização automática

### ETL

- **Pipeline modular**: `ingest/` (download) → `transform/` (normalizar) → `load/` (validar e inserir)
- **CLI**: `python -m etl.pipeline.cli run-full` (histórico completo) ou `run-inc --year YYYY` (anos faltantes)
- **Environment**: INMET_BASE_URL, DATA_DIR, DATABASE_URL
- **Schema canônico**: Normalizar para `date, hour_utc, temp_ins_c, humidity, ..., apparent_temperature, heat_index, rolling_heat_7d, municipality`
- **Transformações críticas**: Filtrar UF=PE, computar `rolling_heat_7d` (7-day mean), enriquecer município (TODO: IBGE API)

### Banco de Dados

- **Star schema**: `dim_estacao` (dimensão estações) e `dim_cidade_pe` (dimensão cidades)
- **Tabela principal**: `climate_hourly` (SQLAlchemy) com índices compostos `(station_code, datetime_utc)`
- **Índices**: `ix_climate_station_date` para queries rápidas por estação + data
- **Postgres 15**: Porta 5433 em dev (docker-compose), 5432 em container

## Padrões de Desenvolvimento

### Adicionar um novo endpoint de API

1. Criar função em `backend/app/services/` que retorna `dict` ou `list`
2. Adicionar rota em `backend/app/routes/api_*.py` que chama o serviço e retorna `success(data)`
3. Se precisar serializar ORM, usar `.dump()` do schema (ex: `station_schema_many.dump(stations)`)
4. Adicionar paginação se necessário: `Pagination.from_request(request, query)`

Exemplo (endpoint de estações):
```python
# Em services/station_service.py
def list_stations() -> List[dict]:
    stations = Station.query.order_by(Station.station_code).all()
    return station_schema_many.dump(stations)

# Em routes/api_stations.py
@api_bp.get('/stations')
def list_stations_endpoint():
    data = list_stations()
    return success(data)
```

### Adicionar transformação de dados no ETL

1. Implementar função em `etl/transform/` que recebe DataFrame
2. Registrar em `etl/pipeline/run_full_pipeline.py` no fluxo de orchestração
3. Validar schema em `etl/load/validate_schema.py` antes de inserir
4. Usar `etl.utils.logger.get_logger()` para logging e `timers.time_it()` para profile

### Consultar dados do BD

- Sempre usar SQLAlchemy ORM (`Station.query.filter_by()`) – NEVER raw SQL em routes
- Models estão em `backend/app/models/`
- Usar `db.session.add()`, `db.session.commit()` se modificar dados
- Paginação: `from utils.pagination import Pagination; p = Pagination.from_request(request, query)`

## Comandos Essenciais

### Desenvolvimento local

```bash
# Instalar dependências
pip install -r backend/requirements.txt

# Configurar .env (opcional)
cp backend/.env.example backend/.env

# Rodar Flask em dev (debug=True)
python backend/run.py
# ou
flask --app backend.app:create_app --debug run

# Rodar ETL full
python -m etl.pipeline.cli run-full

# Rodar ETL incremental (detecta anos faltantes)
python -m etl.pipeline.cli run-inc
```

### Docker

```bash
# Build e start services (postgres + web)
docker-compose up --build

# Acessar psql
docker exec -it ilhas_calor_postgres psql -U ilhas_user -d ilhas_de_calor
```

## Integrações e Dependências Externas

- **INMET**: Downloads ZIP anuais via `INMET_BASE_URL` (default: `https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip`)
- **IBGE API**: TODO – atualmente mock para enriquecimento de município (função placeholder em `etl/transform/geospatial_enrichment.py`)
- **ECharts (JS)**: Visualizações interativas em `backend/app/static/js/charts.js`
- **HTMX**: Requisições dinâmicas sem page reload em templates

## Notas Importantes

- Nenhuma autenticação implementada ainda – CORS habilitado globalmente
- Dados de simulação são mocks (não persistem) – em `backend/app/services/simulation_service.py`
- `rolling_heat_7d` é computado por estação em `etl/transform/compute_heat_metrics.py`
- Tabelas `bronze_*` e `silver_*` no schema.sql estão planejadas para futuro (atualmente usa apenas public)
- Após ETL, rodar migrações Flask se houver mudanças no schema (usar Flask-Migrate se necessário)

## Pontos de Extensão Futuros

- [ ] Integração com IBGE API para nomes de municípios (replace mock geospatial_enrichment)
- [ ] Detecção de outliers e alertas em climate_service
- [ ] Cache Redis para endpoints hot (heatmap, hottest stations)
- [ ] Autenticação/autorização e rate limiting
- [ ] Testes unitários e CI pipeline
- [ ] Persistir arquivos parquet entre execuções ETL para reprocessamento rápido
