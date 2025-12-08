# 📊 OBSERVATÓRIO ESTADUAL DE ILHAS DE CALOR - PE

## Status Geral do Projeto

**Última Atualização:** 2024-01-XX  
**Versão:** 5.0 (ETAPA 5 Completa)  
**Commit:** `3776564`  
**Status Geral:** ✅ **5 DE 5 ETAPAS COMPLETAS**

---

## 🎯 Visão Geral (Roadmap Completado)

```
ETAPA 1: Base de Dados ✅
├─ Schema PostgreSQL (star schema)
├─ Tabelas: estações, cidades, dados climáticos
└─ ETL pipeline funcional

ETAPA 2: API REST ✅
├─ Flask com Blueprints
├─ 5 endpoints principais
└─ Serialização com Marshmallow

ETAPA 3: Dashboard de Dados ✅
├─ Tabela de estações interativa
├─ Filtros por cidade/período
└─ Exportação CSV

ETAPA 4: Dashboard Analytics ✅
├─ HTMX para interatividade
├─ ECharts para visualizações
├─ Análise de risco por município
└─ Alertas e notificações

ETAPA 5: Mapa Interativo ✅
├─ Leaflet 1.9.4
├─ GeoJSON com municípios
├─ Colorização por risco
└─ Navegação integrada

ETAPA 6: (PLANEJADO - Filtros Avançados)
```

---

## 📦 Arquitetura do Projeto

### Estrutura Geral

```
ILHAS_DE_CALOR/
├─ backend/                      # Flask app principal
│  ├─ app/
│  │  ├─ models/                 # SQLAlchemy ORM
│  │  │  ├─ climate.py           # ClimateHourly, GoldClimaPeDiario
│  │  │  ├─ metrics.py           # Métricas derivadas
│  │  │  └─ stations.py          # Station, City
│  │  ├─ routes/                 # Flask Blueprints
│  │  │  ├─ main.py              # Index
│  │  │  ├─ api.py               # Endpoints gerais
│  │  │  ├─ api_climate.py       # /api/climate/*
│  │  │  ├─ api_stations.py      # /api/stations/*
│  │  │  ├─ api_analytics.py     # /api/analytics/*
│  │  │  ├─ api_gold.py          # /api/gold/*
│  │  │  ├─ api_simulation.py    # /api/simulation/*
│  │  │  ├─ dashboard.py         # /dashboard/*
│  │  │  └─ dashboard_map.py     # /dashboard/mapa/* [NOVO]
│  │  ├─ services/               # Lógica de negócio
│  │  │  ├─ climate_service.py
│  │  │  ├─ station_service.py
│  │  │  ├─ analytics_service.py
│  │  │  └─ simulation_service.py
│  │  ├─ templates/              # Jinja2 templates
│  │  │  ├─ base.html
│  │  │  ├─ index.html
│  │  │  ├─ dashboard/
│  │  │  │  ├─ base_dashboard.html
│  │  │  │  ├─ dashboard.html
│  │  │  │  ├─ city_detail.html
│  │  │  │  └─ mapa.html         # [NOVO]
│  │  │  └─ components/
│  │  ├─ static/                 # CSS, JS, images
│  │  │  ├─ css/
│  │  │  ├─ js/
│  │  │  │  ├─ charts.js
│  │  │  │  ├─ heatmap.js
│  │  │  │  ├─ htmx_helpers.js
│  │  │  │  └─ main.js
│  │  │  └─ geo/                 # [NOVO]
│  │  │     └─ municipios_pe.geojson
│  │  ├─ utils/
│  │  │  ├─ responses.py
│  │  │  ├─ pagination.py
│  │  │  └─ exceptions.py
│  │  ├─ extensions.py           # SQLAlchemy, Flask extensions
│  │  ├─ config.py               # Configurações
│  │  └─ __init__.py             # App factory
│  ├─ requirements.txt
│  ├─ run.py                     # Entry point (dev)
│  └─ run_wsgi.py                # Entry point (prod)
│
├─ etl/                          # ETL pipeline
│  ├─ pipeline/
│  │  ├─ cli.py                  # CLI entrypoint
│  │  ├─ run_full_pipeline.py
│  │  └─ run_incremental.py
│  ├─ ingest/
│  │  ├─ download_inmet.py
│  │  └─ extract_zip.py
│  ├─ transform/
│  │  ├─ normalize_inmet.py
│  │  ├─ compute_heat_metrics.py
│  │  └─ geospatial_enrichment.py
│  ├─ load/
│  │  ├─ load_to_postgres.py
│  │  └─ validate_schema.py
│  └─ utils/
│     ├─ logger.py
│     ├─ constants.py
│     └─ timers.py
│
├─ db/                           # Database scripts
│  ├─ schema.sql
│  └─ seed_example.sql
│
├─ scripts/
│  ├─ run_app_dev.sh
│  ├─ run_app_docker.sh
│  ├─ run_etl_full.py
│  ├─ run_etl_incremental.py
│  └─ download_geojson.py        # [NOVO]
│
├─ docs/                         # Documentação
│  ├─ architecture_overview.md
│  ├─ api_reference.md
│  ├─ data_dictionary.md
│  ├─ TESTING_MAPA.md            # [NOVO]
│  ├─ ETAPA_4_README.md          # [ANTERIOR]
│  └─ ETAPA_5_README.md          # [NOVO]
│
├─ docker-compose.yml            # Docker services
├─ README.md
└─ .github/
   └─ copilot-instructions.md
```

---

## 🗄️ Banco de Dados (PostgreSQL 15)

### Tabelas Principais

```sql
-- Dimensões
dim_estacao (station_code, name, latitude, longitude, altitude)
dim_cidade_pe (id_cidade, nome_cidade, uf, latitude, longitude)

-- Fatos
climate_hourly (
  id_clima,
  station_code,
  datetime_utc,
  temperatura_instante,
  umidade_relativa,
  pressao_atmosferica,
  velocidade_vento,
  direcao_vento,
  precipitacao,
  aparent_temperature,
  heat_index,
  created_at
)

-- GOLD (análise)
gold_clima_pe_diario (
  id_gold,
  id_cidade,
  nome_cidade,
  uf,
  data,
  temp_media,
  temp_max,
  temp_min,
  umidade_media,
  heat_index_max,
  risco_calor,      # Categorias: Baixo, Moderado, Alto, Muito Alto, Extremo
  amplitude_termica,
  dias_acima_threshold,
  created_at
)
```

### Índices Otimizados

```sql
CREATE INDEX ix_climate_station_date ON climate_hourly(station_code, datetime_utc);
CREATE INDEX ix_gold_cidade_data ON gold_clima_pe_diario(id_cidade, data DESC);
CREATE INDEX ix_gold_risco ON gold_clima_pe_diario(risco_calor);
```

---

## 🚀 API REST (5 Blueprints Principais)

### 1. **Climate API** (`/api/climate`)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/data` | GET | Lista dados climáticos com filtros |
| `/hourly/<code>` | GET | Dados horários por estação |
| `/stats/<code>` | GET | Estatísticas por estação |
| `/trends` | GET | Tendências temporais |

### 2. **Stations API** (`/api/stations`)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Lista todas estações |
| `/<code>` | GET | Detalhes estação |
| `/nearby` | GET | Estações próximas |

### 3. **Analytics API** (`/api/analytics`)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/summary` | GET | Resumo de riscos |
| `/municipality/<id>` | GET | Análise por município |
| `/alerts` | GET | Alertas ativos |
| `/trends` | GET | Tendências gerais |

### 4. **Gold API** (`/api/gold`) [NOVO]

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/resumo` | GET | Resumo diário por município |
| `/municipios` | GET | Lista municípios com risco |
| `/mapa` | GET | Dados para mapa (risco por município) |
| `/alerts` | GET | Municípios em alerta |

### 5. **Simulation API** (`/api/simulation`)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/forecast` | POST | Previsão customizada |
| `/scenario` | POST | Simulação de cenário |

---

## 🎨 Frontend (Templates + JS)

### Dashboard (HTMX + ECharts)

**Página:** `/dashboard`

```html
┌─────────────────────────────────────────┐
│ Observatório de Ilhas de Calor - PE    │
├─────────────────────────────────────────┤
│  [Filtros: Município | Período | ...]  │
├─────────────────────────────────────────┤
│  ┌──────────────┬──────────────┐        │
│  │ Risco Médio  │ Temp Max     │        │
│  │   72 (Alto)  │   35.8°C     │        │
│  ├──────────────┼──────────────┤        │
│  │ Municípios   │ Dias Críticos│        │
│  │ em Alerta: 5 │     12       │        │
│  └──────────────┴──────────────┘        │
│                                        │
│  [ECharts - Séries Temporais]          │
│  ┌────────────────────────────┐        │
│  │ Temperatura Max Diária     │        │
│  │ (Últimos 30 dias)          │        │
│  │ [Gráfico interativo]       │        │
│  └────────────────────────────┘        │
│                                        │
│  [Tabela de Municípios]                │
│  ID | Nome | Risco | Temp Max | ...   │
└─────────────────────────────────────────┘
```

**Componentes:**
- Header com branding
- Painel de filtros (HTMX)
- Cards de KPI (métricas principais)
- Gráficos ECharts (temperatura, risco, tendências)
- Tabela interativa (com paginação)
- Legenda e ajuda

### Mapa Interativo (Leaflet) [NOVO]

**Página:** `/dashboard/mapa`

```
┌─────────────────────────────────────────┐
│ Mapa - Ilhas de Calor em PE            │
├─────────────────────────────────────────┤
│        ┌──────────────┬──────┐         │
│        │              │Legenda          │
│        │  MAPA LEAFLET│──────┤         │
│        │              │█ Baixo           │
│        │ (600px)      │█ Moderado        │
│        │              │█ Alto            │
│        │  Zoom: 8     │█ Muito Alto      │
│        │  Center PE   │█ Extremo         │
│        │              ├──────┤         │
│        │              │Stats            │
│        │              │Max: 85          │
│        │              │Min: 20          │
│        │              │Avg: 52          │
│        │              └──────┘         │
│        └──────────────────────┘         │
│ Features:                              │
│ • Click = popup com detalhes           │
│ • Hover = highlight (opacity 0.95)    │
│ • Cores = 5 categorias risco           │
│ • Link = /dashboard/cidade/<id>       │
└─────────────────────────────────────────┘
```

**Tecnologia:**
- Leaflet 1.9.4 (CDN)
- OpenStreetMap tiles
- GeoJSON (8 municípios sample, 143 produção)
- Vanilla JavaScript (fetch, L.geoJSON)
- Tailwind CSS

---

## 📊 Fluxos de Dados

### ETL Pipeline (INMET → PostgreSQL)

```
1. DOWNLOAD (etl/ingest/)
   INMET API → CSV files → /data/raw/

2. EXTRACT (etl/ingest/)
   ZIP extraction → Raw CSVs

3. TRANSFORM (etl/transform/)
   ├─ normalize_inmet.py
   │  Input: CSV (INMET format)
   │  Output: Standard schema (date, hour, temp, humidity, ...)
   │
   ├─ compute_heat_metrics.py
   │  Calcula: apparent_temperature, heat_index, rolling_heat_7d
   │
   └─ geospatial_enrichment.py
      Enriquece: municipality, latitude, longitude

4. VALIDATE (etl/load/)
   Schema check → Data quality checks

5. LOAD (etl/load/)
   Append to PostgreSQL → climate_hourly table
   Build GOLD table (aggregated daily)

6. ANALYZE (backend services)
   Query via ORM → Serialize → Return JSON
```

### API Request → Response

```
HTTP GET /api/gold/mapa
   ↓
Flask Route Handler (dashboard_map.py)
   ↓
SQLAlchemy Query (GoldClimaPeDiario)
   .filter(uf='PE')
   .group_by(id_cidade)
   .order_by(risco_calor DESC)
   ↓
Risk Score Mapping (0-100 escala)
   Baixo: 20, Moderado: 40, Alto: 60, Muito Alto: 80, Extremo: 100
   ↓
Response JSON (success + data array)
{
  "success": true,
  "data": [
    {
      "id_cidade": "26100",
      "nome_cidade": "Recife",
      "uf": "PE",
      "risco": 75,
      "categoria": "Muito Alto",
      "heat_index_avg": 32.5,
      "data_atualizacao": "2024-01-15"
    }
  ]
}
   ↓
JavaScript (mapa.html)
   colorByRisk(75) → "#D32F2F"
   Renderiza GeoJSON com cor
   Event listeners (click, hover)
   ↓
Browser Display
   Mapa colorido, popups, navegação
```

---

## 🔄 Fluxo de Usuário

### 1. Explorar Dados (Dashboard)

```
User → /dashboard
  ↓
Carrega dashboard.html
  ├─ KPI cards (HTMX)
  ├─ Filtros (HTMX + JS)
  ├─ Gráficos ECharts (JS)
  └─ Tabela municípios (Pagination)
  ↓
User clica em filtro
  ├─ HTMX recarrega cards
  ├─ HTMX recarrega tabela
  └─ ECharts reajusta gráficos
  ↓
User clica em município na tabela
  → /dashboard/cidade/<id>
```

### 2. Visualizar Mapa (NOVO)

```
User → /dashboard/mapa
  ↓
Carrega mapa.html
  ├─ Leaflet map (OpenStreetMap)
  ├─ GeoJSON (fetch /static/geo/...)
  ├─ API data (fetch /api/gold/mapa)
  ├─ Legenda (5 cores)
  └─ Estatísticas (max/min/avg)
  ↓
Leaflet renderiza features com cores
  ├─ Cores baseadas em risco
  ├─ Popups ao clicar
  └─ Hover effects
  ↓
User clica em município
  ├─ Popup exibe detalhes
  ├─ Botão "Ver detalhes"
  └─ → /dashboard/cidade/<id>
```

### 3. Analisar Cidade Detalhes

```
User → /dashboard/cidade/<id>
  ↓
Carrega city_detail.html
  ├─ Nome, coordenadas
  ├─ Risco atual (grande)
  ├─ Histórico (gráfico)
  ├─ Estações próximas
  └─ Alertas
  ↓
Permite voltar ao mapa: /dashboard/mapa
```

---

## 📈 Métricas Implementadas

### GOLD (Daily Aggregation)

Para cada município em PE:

| Métrica | Cálculo | Faixa |
|---------|---------|-------|
| **Temperatura Média** | mean(temp_insante) | °C |
| **Temperatura Máx** | max(temp_insante) | °C |
| **Temperatura Mín** | min(temp_insante) | °C |
| **Umidade Média** | mean(umidade) | % |
| **Heat Index Máx** | max(heat_index) | °C |
| **Amplitude Térmica** | temp_max - temp_min | °C |
| **Risco de Calor** | Categorizado | Baixo/Moderado/Alto/Muito Alto/Extremo |
| **Dias Críticos** | count(temp > 32°C) | dias |

### Categorização de Risco

| Categoria | Range | Cor | Descrição |
|-----------|-------|-----|-----------|
| **Baixo** | 0-20 | 🟢 #8BC34A | Temp < 28°C, safe |
| **Moderado** | 21-40 | 🟡 #FFC107 | Temp 28-32°C, caution |
| **Alto** | 41-60 | 🟠 #FF5722 | Temp 32-35°C, warning |
| **Muito Alto** | 61-80 | 🔴 #D32F2F | Temp 35-38°C, alert |
| **Extremo** | 81-100 | 🔴🔴 #B71C1C | Temp > 38°C, critical |

---

## 🛠️ Stack Tecnológico Completo

### Backend
- **Python 3.9+**
- **Flask 2.3+** (web framework)
- **SQLAlchemy 2.0+** (ORM)
- **Marshmallow 3.19+** (serialization)
- **PostgreSQL 15** (database)
- **psycopg2** (PostgreSQL driver)
- **Pandas** (data processing ETL)

### Frontend
- **HTML5** (markup)
- **Tailwind CSS** (styling)
- **Vanilla JavaScript ES6** (interactivity)
- **ECharts 5+** (charts)
- **HTMX 1.9+** (dynamic updates)
- **Leaflet 1.9.4** (mapping)
- **OpenStreetMap** (basemap tiles)

### DevOps
- **Docker** (containerization)
- **Docker Compose** (orchestration)
- **Git** (version control)
- **GitHub** (repository)

### Data Sources
- **INMET** (weather data - CSV)
- **IBGE** (geospatial data - GeoJSON)

---

## 📋 Checklist de Funcionalidades

### ETAPA 1: Base de Dados ✅
- [x] Schema PostgreSQL (star schema)
- [x] Tabelas dim_estacao, dim_cidade_pe, climate_hourly
- [x] Índices otimizados
- [x] GOLD table (gold_clima_pe_diario)
- [x] Seeding de dados exemplo

### ETAPA 2: API REST ✅
- [x] Flask app com factory pattern
- [x] 5 blueprints (climate, stations, analytics, gold, simulation)
- [x] Marshmallow schemas
- [x] Response helpers (success, error)
- [x] Pagination
- [x] Error handling

### ETAPA 3: Dashboard de Dados ✅
- [x] Página /dashboard/estacoes
- [x] Tabela interativa com filtros
- [x] Paginação
- [x] Exportação CSV
- [x] Responsividade

### ETAPA 4: Dashboard Analytics ✅
- [x] Página /dashboard/analytics
- [x] HTMX para filtros dinâmicos
- [x] ECharts - Temperatura timeline
- [x] ECharts - Risco por cidade
- [x] ECharts - Distribuição amplitude térmica
- [x] Cards KPI (risco médio, temp máx, etc)
- [x] Tabela municípios com ranking
- [x] Alertas destacados
- [x] Responsividade

### ETAPA 5: Mapa Interativo ✅
- [x] Página /dashboard/mapa
- [x] Leaflet 1.9.4 (CDN)
- [x] GeoJSON (8 amostras + script para 143)
- [x] Colorização por risco (5 categorias)
- [x] Popups ao clicar
- [x] Navegação /dashboard/cidade/<id>
- [x] Legenda visual
- [x] Estatísticas (max/min/avg)
- [x] Hover effects
- [x] Responsividade (desktop/tablet/mobile)
- [x] Teste checklist (TESTING_MAPA.md)
- [x] Menu integrado

### ETAPA 6: (Planejado - Não Iniciado)
- [ ] Filtros avançados (data range, risco mínimo, etc)
- [ ] Múltiplas camadas (temperatura, umidade, amplitude)
- [ ] Controles Leaflet (fullscreen, zoom, export)
- [ ] Persistência de estado (URL params)
- [ ] Comparação histórica (slider de datas)
- [ ] Exportar dados (GeoJSON, CSV)
- [ ] Cache Redis

---

## 🚀 Como Iniciar

### Desenvolvimento Local

```bash
# 1. Clonar repo
git clone https://github.com/Sandoque/ILHAS_DE_CALOR.git
cd ILHAS_DE_CALOR

# 2. Instalar dependências
pip install -r backend/requirements.txt

# 3. Configurar .env
cp backend/.env.example backend/.env

# 4. Rodar Flask (dev)
python backend/run.py

# 5. Acessar
http://localhost:5000
```

### Docker

```bash
# 1. Build e start
docker-compose up --build

# 2. Acessar
http://localhost:8000 (prod) ou localhost:5000 (dev)

# 3. ETL (data ingestion)
docker exec -it ilhas_calor_web python -m etl.pipeline.cli run-full
```

---

## 📊 Status Resumido

| Etapa | Descrição | Status | Commit | Data |
|-------|-----------|--------|--------|------|
| 1 | Base Dados | ✅ Complete | - | - |
| 2 | API REST | ✅ Complete | - | - |
| 3 | Dashboard | ✅ Complete | - | - |
| 4 | Analytics | ✅ Complete | d081669 | Jan 2024 |
| 5 | Mapa | ✅ Complete | 3776564 | Jan 2024 |
| 6 | Advanced | 📋 Planned | - | - |

---

## 📚 Documentação

- **Architecture:** `docs/architecture_overview.md`
- **API Reference:** `docs/api_reference.md`
- **Data Dictionary:** `docs/data_dictionary.md`
- **ETAPA 4:** `ETAPA_4_README.md`
- **ETAPA 5:** `ETAPA_5_README.md`
- **Testing Mapa:** `docs/TESTING_MAPA.md`
- **Copilot Instructions:** `.github/copilot-instructions.md`

---

## 🤝 Contributing

Pull requests welcome! Siga as convenções do projeto:
1. Feature branches: `feature/nome-feature`
2. Commit messages: Descriptivas em PT-BR
3. Tests: Incluir testes para novas funcionalidades
4. Docs: Atualizar documentação

---

## 📞 Suporte

Dúvidas ou issues? Abra uma GitHub issue ou consulte a documentação acima.

---

**Última Atualização:** 2024-01-XX  
**Versão:** 5.0  
**Próximo:** ETAPA 6 (Filtros Avançados + Camadas Múltiplas)
