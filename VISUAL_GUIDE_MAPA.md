# 🗺️ MAPA INTERATIVO COM LEAFLET - VISUAL GUIDE

## 📍 Localização no Projeto

```
ILHAS_DE_CALOR/
├─ backend/
│  ├─ app/
│  │  ├─ routes/
│  │  │  ├─ __init__.py              ✏️ MODIFICADO (registrar blueprint)
│  │  │  ├─ dashboard_map.py         ✨ NOVO (2 rotas)
│  │  │  └─ api_gold.py              ✏️ MODIFICADO (novo endpoint)
│  │  ├─ templates/
│  │  │  ├─ mapa.html                ✨ NOVO (Leaflet + JS)
│  │  │  └─ dashboard/base_dashboard.html  ✏️ MODIFICADO (menu link)
│  │  └─ static/geo/
│  │     └─ municipios_pe.geojson    ✨ NOVO (GeoJSON)
│  │
│  ├─ requirements.txt                (sem mudanças - já tem Leaflet via CDN)
│  └─ run.py
│
├─ scripts/
│  └─ download_geojson.py             ✨ NOVO (atualizar GeoJSON)
│
└─ docs/
   ├─ TESTING_MAPA.md                 ✨ NOVO (14 testes)
   ├─ ETAPA_5_README.md               ✨ NOVO (resumo completo)
   └─ PROJECT_STATUS.md               ✨ NOVO (status 1-5)
```

---

## 🎨 Interface do Mapa (Wireframe)

```
┌──────────────────────────────────────────────────────────┐
│  🔷 Observatório de Ilhas de Calor - Pernambuco         │
│  [Dashboard] [Mapa] [API] [Histórico]                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                 │   │
│  │         LEAFLET MAP (600px altura)             │   │
│  │         Center: [-8.05, -34.9]                 │   │
│  │         Zoom: 8                                │   │
│  │         Basemap: OpenStreetMap                 │   │
│  │                                                 │   │
│  │  Municípios renderizados com GeoJSON:         │   │
│  │  ┌─────────────────────────────────────────┐  │   │
│  │  │                                         │  │   │
│  │  │  🟢 Recife         (Risco: 20 - Baixo)  │  │   │
│  │  │  🟡 Olinda         (Risco: 40 - Mod)    │  │   │
│  │  │  🟠 Jaboatão       (Risco: 60 - Alto)   │  │   │
│  │  │  🔴 Caruaru        (Risco: 80 - Muito)  │  │   │
│  │  │  🔴🔴 Petrolina    (Risco: 100 - Extr)  │  │   │
│  │  │                                         │  │   │
│  │  │ [Popup ao clicar]:                      │  │   │
│  │  │ Recife                                  │  │   │
│  │  │ Risco: 75 (Muito Alto)                  │  │   │
│  │  │ Temperatura: 32.5°C                     │  │   │
│  │  │ [Ver detalhes →]                        │  │   │
│  │  │                                         │  │   │
│  │  └─────────────────────────────────────────┘  │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌────────────────────┐  ┌─────────────────────────┐   │
│  │  LEGENDA           │  │  ESTATÍSTICAS           │   │
│  ├────────────────────┤  ├─────────────────────────┤   │
│  │ █ Baixo            │  │ Risco Máximo:    85°C   │   │
│  │ █ Moderado         │  │ Risco Mínimo:    20°C   │   │
│  │ █ Alto             │  │ Risco Médio:     52°C   │   │
│  │ █ Muito Alto       │  │ Predominante:    Alto   │   │
│  │ █ Extremo          │  │                         │   │
│  │                    │  │ [🔄 Resetar Mapa]      │   │
│  └────────────────────┘  └─────────────────────────┘   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Dados (Sequência)

### 1️⃣ User acessa `/dashboard/mapa`

```
HTTP GET /dashboard/mapa
    ↓
Flask route: @app.route('/dashboard/mapa')
    ↓
Renderiza template: mapa.html
    ↓
HTTP 200 + HTML (template)
```

### 2️⃣ Página carrega (HTML + JS)

```html
<!-- mapa.html -->
<html>
  <head>
    <!-- Leaflet 1.9.4 CDN -->
    <link href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/..."
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/..."
  </head>
  <body>
    <!-- Div principal -->
    <div id="map" style="height: 600px;"></div>
    
    <!-- Script js/main.js ou inline -->
    <script>
      async function initMap() { ... }
      async function loadMapData() { ... }
      async function loadGeoJSON() { ... }
      function colorByRisk(risco) { ... }
      
      // Chamar ao carregar
      initMap();
      loadMapData();
      loadGeoJSON();
    </script>
  </body>
</html>
```

### 3️⃣ JavaScript carrega em paralelo (Fetch)

```
┌─────────────────────────────────────────────────────────┐
│  Browser: mapa.html loading (onload event)              │
└─────────────────────────────────────────────────────────┘
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
   
   fetch('/dashboard/mapa/dados')
        ↓
   Backend: @app.route('/dashboard/mapa/dados')
        ↓
   SQLAlchemy Query:
     SELECT id_cidade, nome_cidade, uf, risco_calor,
            AVG(heat_index_max) as heat_index_avg,
            MAX(data) as data_atualizacao
     FROM gold_clima_pe_diario
     WHERE uf='PE'
     GROUP BY id_cidade, nome_cidade, uf, risco_calor
        ↓
   Risk Score Mapping:
     'Baixo' → 20
     'Moderado' → 40
     'Alto' → 60
     'Muito Alto' → 80
     'Extremo' → 100
        ↓
   Response JSON
        ↓
   JavaScript: municipiosData = [{...}, {...}, ...]
   
   ┌──────────────────────────────────────────────┐
   
   fetch('/static/geo/municipios_pe.geojson')
        ↓
   Static file served by Flask
        ↓
   JavaScript: geoJsonData = FeatureCollection
```

### 4️⃣ Leaflet renderiza mapa

```javascript
// initMap()
map = L.map('map').setView([-8.05, -34.9], 8);
L.tileLayer('https://...openstreetmap...').addTo(map);

// loadGeoJSON()
geoJsonLayer = L.geoJSON(geojson, {
  style: (feature) => {
    const cityId = feature.properties.id;
    const municipio = municipiosData[cityId];
    const color = colorByRisk(municipio.risco);
    return { fillColor: color, fillOpacity: 0.75 };
  },
  onEachFeature: (feature, layer) => {
    layer.on('click', () => {
      // Navegar para /dashboard/cidade/<id>
      window.location.href = `/dashboard/cidade/${id}`;
    });
  }
}).addTo(map);
```

### 5️⃣ Resultado visual

```
🌐 Browser Display
├─ Mapa com municípios coloridos
├─ Popups ao clicar (nome, risco, temperatura)
├─ Hover effects (opacidade aumentada)
├─ Legenda visual (5 cores)
└─ Estatísticas (max, min, avg, predominante)
```

---

## 🎨 Esquema de Cores

```
┌──────────────────────────────────────────────────────┐
│  MAPEAMENTO DE RISCO (Contínuo 0-100)               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  0 ═════════════════ 50 ════════════════ 100        │
│  │                   │                   │          │
│  Baixo            Alto                Extremo       │
│  🟢                 🟠                  🔴          │
│ #8BC34A            #FF5722             #B71C1C     │
│                                                      │
│  Categorias Discretas (mapeadas):                   │
│  ─────────────────────────────────                  │
│  Risco 0-20   → Verde (#8BC34A)     ← Baixo        │
│  Risco 21-40  → Amarelo (#FFC107)   ← Moderado     │
│  Risco 41-60  → Laranja (#FF5722)   ← Alto         │
│  Risco 61-80  → Vermelho (#D32F2F)  ← Muito Alto   │
│  Risco 81-100 → V.Escuro (#B71C1C)  ← Extremo      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Função colorByRisk(risco)

```javascript
function colorByRisk(risco) {
  if (risco <= 20) return '#8BC34A';      // Baixo - Verde
  if (risco <= 40) return '#FFC107';      // Moderado - Amarelo
  if (risco <= 60) return '#FF5722';      // Alto - Laranja
  if (risco <= 80) return '#D32F2F';      // Muito Alto - Vermelho
  return '#B71C1C';                       // Extremo - Vermelho Escuro
}
```

---

## 📱 Responsividade

### Desktop (>1024px)
```
┌────────────────────────────────────────────┐
│ Header (menu)                              │
├────────────────────────────────────────────┤
│                                            │
│    Mapa (70%)              Legenda (30%)  │
│ ┌─────────────────────┐  ┌──────────────┐ │
│ │                     │  │              │ │
│ │    LEAFLET MAP      │  │  CORES       │ │
│ │    600px            │  │              │ │
│ │                     │  │  STATS       │ │
│ └─────────────────────┘  └──────────────┘ │
│                                            │
└────────────────────────────────────────────┘
```

### Tablet (768-1024px)
```
┌────────────────────────────────────────────┐
│ Header (menu)                              │
├────────────────────────────────────────────┤
│  Legenda (flex-wrap)                       │
│ ┌──────────┬──────────┐                   │
│ │ CORES    │  STATS   │                   │
│ └──────────┴──────────┘                   │
│                                            │
│  Mapa (100% width)                        │
│ ┌────────────────────────────────────────┐ │
│ │                                         │ │
│ │    LEAFLET MAP                          │ │
│ │    400px                                │ │
│ │                                         │ │
│ └────────────────────────────────────────┘ │
│                                            │
└────────────────────────────────────────────┘
```

### Mobile (<768px)
```
┌────────────────────────────────────────────┐
│ Header (menu)                              │
├────────────────────────────────────────────┤
│                                            │
│  Mapa (Fullscreen)                        │
│ ┌────────────────────────────────────────┐ │
│ │                                         │ │
│ │                                         │ │
│ │    LEAFLET MAP                          │ │
│ │    (100% - height: 60vh)               │ │
│ │                                         │ │
│ │                                         │ │
│ └────────────────────────────────────────┘ │
│                                            │
│  Legenda (collapse/popup)                 │
│ ┌────────────────────────────────────────┐ │
│ │ [▼ Mostrar Legenda]                    │ │
│ └────────────────────────────────────────┘ │
│                                            │
└────────────────────────────────────────────┘
```

---

## 🧪 Fluxo de Teste (Resumido)

### T1: Carregamento Básico ✅
```bash
# 1. Acessar URL
http://localhost:5000/dashboard/mapa

# 2. Browser DevTools (F12)
✓ Leaflet library loaded
✓ Map element exists (id="map")
✓ Center: [-8.05, -34.9]
✓ Zoom: 8
✓ OSM tiles visible
✓ No console errors
```

### T2: Dados GeoJSON ✅
```bash
# 1. Acessar GeoJSON
http://localhost:5000/static/geo/municipios_pe.geojson

# 2. Validar
✓ Valid JSON
✓ Type: "FeatureCollection"
✓ Features: 8 (ou 143 when IBGE API available)
✓ Each feature has geometry (Polygon)
✓ Properties: id, codigo, nome
```

### T3: API Risco ✅
```bash
# 1. Testar endpoint
curl http://localhost:5000/api/gold/mapa

# 2. Resposta
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
✓ Success: true
✓ Data array has 8+ items (ou N)
✓ Risco values: 0-100
```

### T4: Cores Corretas ✅
```javascript
// Browser console
colorByRisk(20)  // "#8BC34A" (Baixo)
colorByRisk(40)  // "#FFC107" (Moderado)
colorByRisk(60)  // "#FF5722" (Alto)
colorByRisk(80)  // "#D32F2F" (Muito Alto)
colorByRisk(100) // "#B71C1C" (Extremo)
```

### T5: Clique e Navegação ✅
```
1. Clicar em município no mapa
   ↓
2. Popup exibe:
   - Nome: "Recife"
   - Risco: "75 (Muito Alto)"
   - Temp: "32.5°C"
   - Botão: "Ver detalhes →"
   ↓
3. Clicar no botão
   ↓
4. Navega para: /dashboard/cidade/26100
   ✓ URL muda
   ✓ Página carrega
```

---

## 📊 Arquivos Criados (Detalhe)

### 1. `backend/app/routes/dashboard_map.py`
```python
from flask import Blueprint, render_template, jsonify, request
from ...extensions import db
from ...models.climate import GoldClimaPeDiario
from ...utils.responses import success, error
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)
map_bp = Blueprint('map', __name__, url_prefix='/dashboard/mapa')

@map_bp.route('/', methods=['GET'])
def map_main():
    """Renderiza página principal do mapa"""
    return render_template('mapa.html')

@map_bp.route('/dados', methods=['GET'])
def map_risk_data():
    """Retorna dados de risco por município em JSON"""
    try:
        municipios = db.session.query(
            GoldClimaPeDiario.id_cidade,
            GoldClimaPeDiario.nome_cidade,
            GoldClimaPeDiario.uf,
            GoldClimaPeDiario.risco_calor,
            func.avg(GoldClimaPeDiario.heat_index_max).label('heat_index_avg'),
            func.max(GoldClimaPeDiario.data).label('data_atualizacao')
        ).filter(
            GoldClimaPeDiario.uf == 'PE'
        ).group_by(
            GoldClimaPeDiario.id_cidade,
            GoldClimaPeDiario.nome_cidade,
            GoldClimaPeDiario.uf,
            GoldClimaPeDiario.risco_calor
        ).all()
        
        # Mapear risco para 0-100
        risk_mapping = {
            'Baixo': 20,
            'Moderado': 40,
            'Alto': 60,
            'Muito Alto': 80,
            'Extremo': 100
        }
        
        data = [{
            'id_cidade': m.id_cidade,
            'nome_cidade': m.nome_cidade,
            'uf': m.uf,
            'risco': risk_mapping.get(m.risco_calor, 0),
            'categoria': m.risco_calor,
            'heat_index_avg': float(m.heat_index_avg) if m.heat_index_avg else 0,
            'data_atualizacao': m.data_atualizacao.isoformat() if m.data_atualizacao else None
        } for m in municipios]
        
        return success(data)
    except Exception as e:
        logger.exception("Erro ao buscar dados de risco")
        return error("Erro ao buscar dados"), 500
```

### 2. `backend/app/templates/mapa.html` (estrutura)
```html
{% extends "dashboard/base_dashboard.html" %}

{% block content %}
<div class="container mx-auto p-4">
  <h1 class="text-3xl font-bold mb-4">Mapa - Ilhas de Calor em PE</h1>
  
  <div id="error-container" class="hidden bg-red-100 p-4 rounded"></div>
  
  <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
    <!-- Mapa principal -->
    <div class="lg:col-span-3">
      <div id="map" style="height: 600px;"></div>
    </div>
    
    <!-- Legenda e Estatísticas -->
    <div class="lg:col-span-1">
      <!-- Legenda -->
      <div class="bg-white p-4 rounded shadow mb-4">
        <h3 class="font-bold mb-2">Legenda</h3>
        <div id="legend">
          <div class="flex items-center gap-2 mb-2">
            <div style="width: 20px; height: 20px; background-color: #8BC34A;"></div>
            <span>Baixo</span>
          </div>
          <!-- ... outras cores ... -->
        </div>
      </div>
      
      <!-- Estatísticas -->
      <div class="bg-white p-4 rounded shadow">
        <h3 class="font-bold mb-2">Estatísticas</h3>
        <p>Máximo: <span id="stat-max">-</span></p>
        <p>Mínimo: <span id="stat-min">-</span></p>
        <p>Médio: <span id="stat-avg">-</span></p>
        <button onclick="resetMap()" class="mt-4 bg-blue-500 text-white p-2 rounded">
          Resetar Mapa
        </button>
      </div>
    </div>
  </div>
</div>

<script>
  // Variáveis globais
  let map;
  let geoJsonLayer;
  let municipiosData = {};
  
  // Funções
  function initMap() { ... }
  function loadMapData() { ... }
  function loadGeoJSON() { ... }
  function colorByRisk(risco, categoria) { ... }
  function updateStatistics(municipios) { ... }
  function showError(message) { ... }
  function resetMap() { ... }
  
  // Iniciar ao carregar
  window.addEventListener('load', async () => {
    initMap();
    await loadMapData();
    await loadGeoJSON();
  });
</script>
{% endblock %}
```

### 3. `backend/app/static/geo/municipios_pe.geojson`
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": "26100",
        "codigo": "2610100",
        "nome": "Recife"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[...coordinates...]]
      }
    },
    // ... mais 7 municípios ...
  ]
}
```

---

## 🔗 Endpoints Mapa

### GET `/dashboard/mapa`
- **Tipo:** HTML
- **Resposta:** Template mapa.html renderizado
- **Status:** 200 OK
- **Usado por:** Browser direto, menu link

### GET `/dashboard/mapa/dados`
- **Tipo:** JSON
- **Query:** Nenhum parâmetro obrigatório
- **Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id_cidade": "string",
      "nome_cidade": "string",
      "uf": "PE",
      "risco": 0-100,
      "categoria": "Baixo|Moderado|Alto|Muito Alto|Extremo",
      "heat_index_avg": float,
      "data_atualizacao": "ISO8601"
    }
  ]
}
```
- **Status:** 200 OK ou 500 Error
- **Usado por:** JavaScript (mapa.html) via fetch()

---

## 🎯 Próximos Passos (ETAPA 6)

### Não incluído em ETAPA 5:
- [ ] Filtros de data (date range picker)
- [ ] Filtro por categoria de risco
- [ ] Filtro por temperatura mínima
- [ ] Múltiplas camadas (toggle visibility):
  - [ ] Temperatura
  - [ ] Umidade
  - [ ] Amplitude térmica
- [ ] Controles Leaflet avançados:
  - [ ] Fullscreen
  - [ ] Zoom control
  - [ ] Layer control
- [ ] Comparação histórica (slider de datas)
- [ ] Exportação:
  - [ ] PNG (screenshot)
  - [ ] GeoJSON
  - [ ] CSV
- [ ] Cache Redis para performance

---

## ✅ Checklist Final

- [x] Blueprint criado
- [x] Template Leaflet completo
- [x] GeoJSON integrado
- [x] Endpoint API implementado
- [x] JavaScript funcional
- [x] Menu link adicionado
- [x] Teste checklist criado
- [x] Git commits feitos
- [x] GitHub push completo
- [x] Documentação completa
- [x] **PRONTO PARA TESTES** ✅

---

**Commit:** `3776564` + `7247993` + `cfd7403`  
**Status:** ✅ **ETAPA 5 COMPLETA**
