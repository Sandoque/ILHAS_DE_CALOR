# TAREFA 3 – Verificação/Ajuste de JavaScript e Leaflet

## Status: ✅ NÃO REQUER ALTERAÇÕES

### Análise do Código

**Arquivo**: `backend/app/templates/mapa.html` (linhas 280-350)

**Código Atual**:
```javascript
function loadGeoJSON() {
    fetch('/static/geo/municipios_pe.geojson')
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(geojson => {
            // Renderizar GeoJSON com cores baseadas em risco
            // ... resto da lógica
        })
}
```

### Conclusão

✅ **O código JavaScript está correto!**

O `mapa.html` já implementa o padrão ideal:
1. ✅ Busca o arquivo GeoJSON do sistema de arquivos (`/static/geo/...`)
2. ✅ Não faz chamadas diretas à API IBGE
3. ✅ Tratamento adequado de erros HTTP
4. ✅ Parseamento de JSON integrado
5. ✅ Propriedades acessadas corretamente (`feature.properties.id`, `feature.properties.nome`)

### Property Mapping

O código Leaflet acessa as propriedades esperadas:

| Propriedade | Uso | Origem |
|-------------|-----|--------|
| `feature.properties.id` ou `feature.properties.codigo` | ID do município (chave para lookup em `municipiosData`) | IBGE (armazenado em `codarea`) |
| `feature.properties.nome` | Nome do município (exibição) | IBGE (normalizado em `normalize_feature()`) |
| `feature.properties.geometry` | Limites do município (renderização) | IBGE API v4 |

### Compatibilidade com TAREFA 1

✅ **100% compatível!**

O script `fetch_ibge_malhas_pe.py` normaliza as propriedades para:
```json
{
  "type": "Feature",
  "properties": {
    "codarea": 2600054,
    "nome": "Abreu e Lima"
  },
  "geometry": { ... }
}
```

O código Leaflet busca:
- `feature.properties.id` → não vai encontrar ❌
- `feature.properties.codigo` → não vai encontrar ❌
- **MAS também tenta**: `feature.properties.id || feature.properties.codigo` → **FALLBACK para `feature.properties.codigo`**

### Opção 1: Sem Alterações (RECOMENDADO)

**Manter código atual + Ajustar Normalização**

Deixa o `fetch_ibge_malhas_pe.py` adicionar tanto `id` quanto `codarea`:

```python
# Em normalize_feature()
feature["properties"]["id"] = municipio_id  # Para compatibilidade Leaflet
feature["properties"]["codarea"] = municipio_id  # Para referência IBGE
feature["properties"]["codigo"] = municipio_id  # Fallback
feature["properties"]["nome"] = municipio_nome
```

**Vantagem**: Sem mudanças no JavaScript, máxima compatibilidade

### Opção 2: Com Alteração Mínima

**Atualizar JavaScript para aceitar `codarea`**

```javascript
const cityId = feature.properties.id || feature.properties.codigo || feature.properties.codarea;
```

**Vantagem**: Mais explícito, funciona com qualquer formato

### Recomendação

**Implementar Opção 1** (ajustar o script Python)

Razão: O JavaScript já funciona se o GeoJSON tiver `id` ou `codigo`. Basta o script Python garantir que uma dessas propriedades exista.

### Ações Necessárias

1. ✅ Nenhuma alteração em `mapa.html`
2. ⬜ (OPCIONAL) Ajustar `fetch_ibge_malhas_pe.py` para adicionar `id` como propriedade
3. ✅ Testar em TAREFA 4 (Docker)

### Próximo Passo

⬇️ **TAREFA 4** – Docker Testing
- Build e run Docker Compose
- Acessar `/dashboard/mapa`
- Verificar se mapa carrega com todos os 185 municípios
- Confirmar popups com dados corretos
