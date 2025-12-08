# Guia Rápido – IBGE API v4 para Ilhas de Calor PE

## 🚀 Quick Start

### 1. Gerar/Atualizar GeoJSON (5 minutos)

```bash
# Terminal PowerShell
cd c:\Projetos\ILHAS_DE_CALOR
.\venv\Scripts\python scripts/fetch_ibge_malhas_pe.py
```

**Resultado**:
```
✅ GeoJSON de 185 municípios
✅ Arquivo: backend/app/static/geo/municipios_pe.geojson (3.1 MB)
✅ Estado: backend/app/static/geo/estado_pe.geojson (152 KB)
```

### 2. Iniciar Aplicação (1 minuto)

```bash
# Flask Dev
python backend/run.py

# Ou Docker
docker-compose up -d
```

### 3. Acessar Mapa Interativo

```
http://localhost:5000/dashboard/mapa   (Flask)
http://localhost:8000/dashboard/mapa   (Docker)
```

---

## 📡 Endpoints Disponíveis

### GET `/api/geo/municipios-pe`
```bash
curl http://localhost:5000/api/geo/municipios-pe

# Resposta: GeoJSON com 185 features
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": 2600054,
        "codigo": 2600054,
        "codarea": 2600054,
        "nome": "Abreu e Lima"
      },
      "geometry": { ... }
    },
    ...
  ]
}
```

### GET `/api/geo/estado-pe`
```bash
curl http://localhost:5000/api/geo/estado-pe
# Retorna: GeoJSON com geometria do estado
```

### GET `/api/geo/municipios-pe/raw`
```bash
curl -H "Accept: application/geo+json" \
  http://localhost:5000/api/geo/municipios-pe/raw
# Retorna: Arquivo GeoJSON com MIME type correto
```

---

## 🗺️ Usar em JavaScript (Leaflet)

### Opção 1: Arquivo Estático (Atual)
```javascript
// Em mapa.html (linha 283)
fetch('/static/geo/municipios_pe.geojson')
  .then(res => res.json())
  .then(geojson => {
    L.geoJSON(geojson, {
      style: (feature) => {
        const cityId = feature.properties.id || 
                      feature.properties.codigo;
        // ... resto do código
      }
    }).addTo(map);
  });
```

### Opção 2: Endpoint Flask
```javascript
fetch('/api/geo/municipios-pe')
  .then(res => res.json())
  .then(geojson => {
    // ... usar geojson como acima
  });
```

---

## 🔄 Fluxo de Dados

```
IBGE API v4
    ↓
scripts/fetch_ibge_malhas_pe.py
    ↓ (processa 185 municipios)
    ↓
backend/app/static/geo/municipios_pe.geojson
    ↓
┌─────────────────────────────────┐
├─ /static/geo/municipios_pe.geojson (arquivo)
├─ /api/geo/municipios-pe (endpoint JSON)
├─ /api/geo/municipios-pe/raw (endpoint raw)
└─ /dashboard/mapa (HTML + Leaflet)
    ↓
🗺️ Mapa Interativo
```

---

## 📊 Propriedades GeoJSON

Cada feature tem estas propriedades:

| Campo | Tipo | Exemplo | Uso |
|-------|------|---------|-----|
| `id` | int | 2600054 | Leaflet lookup |
| `codigo` | int | 2600054 | Fallback Leaflet |
| `codarea` | int | 2600054 | Referência IBGE |
| `nome` | string | "Abreu e Lima" | Exibição |

---

## 🧪 Teste Rápido

### PowerShell
```powershell
# 1. Verificar se arquivo existe
Test-Path "backend/app/static/geo/municipios_pe.geojson"
# True

# 2. Verificar quantidade de features
$json = Get-Content "backend/app/static/geo/municipios_pe.geojson" | 
  ConvertFrom-Json
$json.features.Count
# 185

# 3. Testar endpoint
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/geo/municipios-pe"
$data = $response.Content | ConvertFrom-Json
$data.features.Count
# 185
```

### Bash/curl
```bash
# 1. Verificar arquivo
ls -lah backend/app/static/geo/municipios_pe.geojson
# -rw-r--r-- ... 3.1M ... municipios_pe.geojson

# 2. Contar features
curl -s http://localhost:5000/api/geo/municipios-pe | \
  jq '.features | length'
# 185

# 3. Verificar primeiro município
curl -s http://localhost:5000/api/geo/municipios-pe | \
  jq '.features[0].properties'
# {
#   "id": 2600054,
#   "codigo": 2600054,
#   "codarea": 2600054,
#   "nome": "Abreu e Lima"
# }
```

---

## ❌ Troubleshooting

### Problema: GeoJSON não encontrado (404)
```bash
# Solução: Re-executar script
python scripts/fetch_ibge_malhas_pe.py
```

### Problema: Mapa vazio no navegador
```bash
# 1. Verificar console (F12)
# 2. Verificar Network tab (procurar por municipios_pe.geojson)
# 3. Se erro 404: executar script acima
# 4. Se erro 500: verificar logs do Flask
```

### Problema: Dados de risco não aparecem
```bash
# Dados vêm do banco (gold_clima_pe_diario)
# Não é problema do GeoJSON!
# Executar ETL para popular banco:
python -m etl.pipeline.cli run-full
```

### Problema: IBGE API lenta/timeout
```bash
# Aumentar timeout em fetch_ibge_malhas_pe.py:
REQUEST_TIMEOUT = 60  # segundos
MAX_RETRIES = 5       # tentativas
```

---

## 📚 Referências

### API IBGE v4
- **Docs**: https://servicodados.ibge.gov.br/api/docs/
- **Municípios PE**: `/api/v1/localidades/estados/26/municipios`
- **Malha município**: `/api/v4/malhas/municipios/{id}?formato=application/vnd.geo+json`
- **Malha estado**: `/api/v4/malhas/estados/26?formato=application/vnd.geo+json`

### Documentação Local
- `TAREFA0_MAPEAMENTO_IBGE.md` – Mapeamento de código
- `TAREFA1_*.md` – Script ETL detalhes
- `TAREFA2_API_ENDPOINT.md` – Endpoints Flask
- `TAREFA3_JAVASCRIPT_LEAFLET.md` – Frontend
- `TAREFA4_DOCKER_TESTING.md` – Testes
- `TAREFA5_LIMPEZA_VALIDACAO.md` – Validação
- `MIGRACAO_IBGE_RESUMO.md` – Resumo completo

### Leaflet
- **Docs**: https://leafletjs.com/
- **GeoJSON**: https://leafletjs.com/examples/geojson/

---

## 🎯 Casos de Uso Comuns

### 1. Atualizar mapa com novos dados IBGE
```bash
# Toda 2ª-feira às 00:00
python scripts/fetch_ibge_malhas_pe.py
# Pronto! Novos dados no mapa
```

### 2. Exportar GeoJSON para SIG (QGIS, ArcGIS)
```bash
# Copiar arquivo
cp backend/app/static/geo/municipios_pe.geojson \
   ~/Desktop/municipios_pe.geojson

# Abrir em QGIS/ArcGIS
```

### 3. Integrar em aplicação externa
```bash
# API pública
curl https://seu-dominio.com/api/geo/municipios-pe
```

### 4. Adicionar novos municípios/propriedades
```python
# Editar fetch_ibge_malhas_pe.py
# Na função normalize_feature():
feature["properties"]["meu_campo"] = meu_valor
```

---

## ⚡ Performance

| Operação | Tempo | Tamanho |
|----------|-------|---------|
| Download IBGE (185) | ~45s | - |
| Normalização | ~5s | - |
| Arquivo GeoJSON | - | 3.1 MB |
| Endpoint resposta | <500ms | 3.1 MB |
| Renderizar no mapa | <2s | - |
| Total (primeira vez) | ~52s | - |
| Total (atualização) | ~45s | - |

---

## 🔐 Segurança

- ✅ Sem autenticação necessária (dados públicos IBGE)
- ✅ CORS habilitado (Flask)
- ✅ Validação de arquivo GeoJSON
- ✅ Tratamento de erros HTTP

### Para Production

1. Adicionar rate limiting
2. Implementar cache Redis
3. Gzip GeoJSON (~70% economia)
4. CDN para arquivo estático
5. Backup automático

---

## 📞 Suporte

Problemas? Verificar:
1. `TAREFA4_DOCKER_TESTING.md` – Troubleshooting
2. Logs: `docker-compose logs -f web`
3. Console navegador: F12 → Console
4. Network tab: F12 → Network

---

**Last Updated**: 08 de Dezembro de 2025  
**Status**: 🟢 PRONTO  
**Compatibilidade**: Flask 2.0+, PostgreSQL 15, Leaflet 1.9.4
