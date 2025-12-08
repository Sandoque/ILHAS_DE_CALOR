# TAREFA 2 – Endpoint Flask para GeoJSON

## Status: ✅ IMPLEMENTADO

### Arquivo Criado
**`backend/app/routes/api_geo.py`** (~130 linhas)

### Endpoints Implementados

#### 1. `GET /api/geo/municipios-pe`
- **Propósito**: Retorna GeoJSON com todos os 185 municípios de PE
- **Response**: JSON (GeoJSON FeatureCollection)
- **Content-Type**: `application/json`
- **Status Codes**:
  - `200`: Sucesso
  - `404`: Arquivo não encontrado
  - `500`: Erro ao ler arquivo

#### 2. `GET /api/geo/estado-pe`
- **Propósito**: Retorna GeoJSON com a geometria do estado de PE
- **Response**: JSON (GeoJSON FeatureCollection)
- **Content-Type**: `application/json`
- **Status Codes**:
  - `200`: Sucesso
  - `404`: Arquivo não encontrado
  - `500`: Erro ao ler arquivo

#### 3. `GET /api/geo/municipios-pe/raw`
- **Propósito**: Retorna arquivo GeoJSON bruto (raw) com MIME type correto
- **Response**: File stream
- **Content-Type**: `application/geo+json`
- **Uso**: Integração com ferramentas GIS ou consumo direto

### Características Principais

✅ **Carregamento Eficiente**
- Lê arquivos GeoJSON do sistema de arquivos
- Parseamento JSON rápido
- Sem processamento desnecessário

✅ **Tratamento de Erros**
- Verifica existência do arquivo
- Retorna mensagens claras se arquivo não encontrado
- Logging de erros para debug

✅ **Integração com Flask**
- Usa Blueprint pattern
- Registrado em `backend/app/routes/__init__.py`
- Segue padrão de respostas do projeto

### Arquivo de Configuração Modificado

**`backend/app/routes/__init__.py`**
```python
# Adicionado:
from .api_geo import api_geo_bp as geo_bp

# Registrado:
app.register_blueprint(geo_bp)
```

### Arquivos Servidos

Os endpoints servem arquivos gerados pela **TAREFA 1**:
- `backend/app/static/geo/municipios_pe.geojson` (3.1 MB, 185 features)
- `backend/app/static/geo/estado_pe.geojson` (152 KB)

### Testes de Uso

#### Teste 1: cURL
```bash
curl http://localhost:5000/api/geo/municipios-pe | jq '.features | length'
# Esperado: 185

curl http://localhost:5000/api/geo/estado-pe | jq '.type'
# Esperado: "FeatureCollection"
```

#### Teste 2: JavaScript/Fetch (no navegador ou Node.js)
```javascript
fetch('/api/geo/municipios-pe')
  .then(res => res.json())
  .then(data => console.log(`Municípios carregados: ${data.features.length}`));
```

#### Teste 3: Python
```python
import requests
response = requests.get('http://localhost:5000/api/geo/municipios-pe')
geojson = response.json()
print(f"Total de features: {len(geojson['features'])}")
```

### Próximo Passo

⬇️ **TAREFA 3** - Verificar/Ajustar JavaScript
- A função `loadGeoJSON()` em `mapa.html` pode continuar usando `/static/geo/municipios_pe.geojson`
- OU pode ser atualizada para usar `/api/geo/municipios-pe` (novo endpoint)
- Alternativamente, pode usar `/api/geo/municipios-pe/raw` para GeoJSON raw

### Notas
- Todos os endpoints retornam JSON parseado (não raw) por padrão
- Use `municipios-pe/raw` para receber o arquivo com MIME type correto
- Os endpoints não fazem cache – ideal para adicionar Redis no futuro
- Logging integrado para monitoramento em produção
