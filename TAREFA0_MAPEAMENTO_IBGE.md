# 🔍 TAREFA 0 - MAPEAMENTO DE REFERÊNCIAS IBGE (ETAPA 5 Correção v4)

**Data:** 2024-01-XX | **Status:** ✅ MAPEADO

---

## 📍 Arquivos Que Usam API IBGE / GeoJSON

### 1. ✅ `scripts/download_geojson.py` (ARQUIVO ANTIGO)
- **Localização:** `c:\Projetos\ILHAS_DE_CALOR\scripts\download_geojson.py`
- **Usa API antiga:** `https://servicodados.ibge.gov.br/api/v1/malhas/estados/26`
- **Status:** SERÁ SUBSTITUÍDO pela TAREFA 1
- **Ação:** Será substituído por `scripts/fetch_ibge_malhas_pe.py`

### 2. ✅ `backend/app/templates/mapa.html` (LEAFLET MAP)
- **Localização:** `c:\Projetos\ILHAS_DE_CALOR\backend\app\templates\mapa.html`
- **Usa:** `fetch('/static/geo/municipios_pe.geojson')` (linha 283)
- **Tipo:** Arquivo estático local
- **Status:** ✅ JÁ CORRETO (usa arquivo local, não IBGE direto)
- **Ação:** Nenhuma (já está otimizado)

### 3. ❌ Nenhuma rota Flask consultando IBGE
- Procurado: `api_geo.py`, `geo_routes.py`, endpoints `/api/geo/`
- **Resultado:** Não encontrado no código
- **Status:** Precisa ser criado na TAREFA 2

### 4. ✅ `backend/app/routes/dashboard_map.py`
- **Localização:** `c:\Projetos\ILHAS_DE_CALOR\backend\app\routes\dashboard_map.py`
- **Usa:** Endpoint `/api/gold/mapa` para risco
- **Status:** ✅ Não consulta IBGE (correto)
- **Ação:** Nenhuma

### 5. ❌ Nenhum arquivo JavaScript isolado
- Procurado: `leaflet_map.js`, `mapa_ilhas_calor.js`, `map.js`
- **Resultado:** Código JavaScript está inline em `mapa.html`
- **Status:** OK (tudo em um lugar)
- **Ação:** Atualizar inline no `mapa.html` se necessário

---

## 📊 Resumo do Mapeamento

| Arquivo | Usa IBGE? | Tipo | Ação |
|---------|-----------|------|------|
| `scripts/download_geojson.py` | ✅ API v1 (antigo) | Script ETL | REMOVER |
| `scripts/fetch_ibge_malhas_pe.py` | ⚠️ Não existe | Script ETL | CRIAR (TAREFA 1) |
| `backend/app/templates/mapa.html` | ❌ Arquivo local | Frontend | Nenhuma |
| `backend/app/routes/dashboard_map.py` | ❌ Não | Backend | Nenhuma |
| `/api/geo/municipios-pe` | ⚠️ Não existe | Flask Route | CRIAR (TAREFA 2) |

---

## 🎯 Dependências Encontradas

**Usadas no projeto:**
- `requests` ✅ (já em requirements.txt)
- `json` ✅ (built-in)
- `pathlib.Path` ✅ (built-in)

**Para os scripts:**
- `requests` ← Verificar se já está em requirements.txt

---

## 📋 Checklist TAREFA 0

- [x] Localizar referências ao IBGE antigo
- [x] Identificar `scripts/download_geojson.py` (será removido)
- [x] Confirmar `mapa.html` já usa arquivo local (correto)
- [x] Identificar necessidade de criar `api_geo.py` (TAREFA 2)
- [x] Mapear estrutura de código JavaScript (inline em `mapa.html`)
- [x] Documentar achados

---

## 🚀 Próximas Tarefas

1. **TAREFA 1:** Criar `scripts/fetch_ibge_malhas_pe.py` com API v4
2. **TAREFA 2:** Criar endpoint `/api/geo/municipios-pe` em Flask
3. **TAREFA 3:** Ajustar JavaScript/Leaflet (provavelmente nenhuma mudança necessária)
4. **TAREFA 4:** Testar com Docker
5. **TAREFA 5:** Remover script antigo

---

**Status:** ✅ MAPEAMENTO COMPLETO
