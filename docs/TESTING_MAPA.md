# TESTING_MAPA.md - Checklist de Testes para Mapa Interativo

Guia de testes manuais para a funcionalidade de mapa com Leaflet.

## Pré-requisitos

```bash
# 1. Iniciar Docker stack
docker-compose up --build

# 2. Verificar se há dados GOLD no banco
docker exec -it ilhas_calor_postgres psql -U ilhas_user -d ilhas_de_calor \
  -c "SELECT COUNT(*) FROM gold_clima_pe_diario;"

# 3. Se vazio, rodar ETL
python -m etl.pipeline.cli run-gold

# 4. Acessar mapa
http://localhost:5000/dashboard/mapa
```

## T1: Carregamento do Mapa

- [ ] Página `/dashboard/mapa` carrega sem erros
- [ ] Mensagem "Carregando mapa..." desaparece
- [ ] Mapa Leaflet inicializa com Pernambuco centralizado
- [ ] Tile layer (OpenStreetMap) carrega
- [ ] Zoom inicial é 8 (razoável para estado)
- [ ] Controles de zoom funcionam (+ e -)
- [ ] Pode arrastar o mapa

## T2: Carregamento do GeoJSON

- [ ] Arquivo `/static/geo/municipios_pe.geojson` existe
- [ ] GeoJSON contém features válidas
- [ ] Municipípios aparecem desenhados no mapa
- [ ] Fronteiras são visíveis
- [ ] Não há erros no console (DevTools F12)

**Comando para verificar arquivo:**
```bash
curl -s http://localhost:5000/static/geo/municipios_pe.geojson | jq '.features | length'
```

## T3: Carregamento do Risco

- [ ] Endpoint `/dashboard/mapa/dados` retorna HTTP 200
- [ ] Resposta JSON contém `{ "success": true, "data": [...] }`
- [ ] Cada município tem: `id_cidade`, `nome_cidade`, `risco`, `categoria`
- [ ] Contador "Total de municípios carregados" atualiza
- [ ] Não há erros de rede (DevTools → Network)

**Teste no console:**
```javascript
fetch('/dashboard/mapa/dados')
  .then(r => r.json())
  .then(d => console.table(d.data.slice(0, 5)))
```

## T4: Cores Corretas

Verificar se as cores correspondem ao mapa de risco:

| Risco | Categoria | Cor | RGB |
|-------|-----------|-----|-----|
| 0-30 | Baixo | Verde | #8BC34A |
| 31-50 | Moderado | Amarelo | #FFC107 |
| 51-70 | Alto | Laranja | #FF5722 |
| 71-85 | Muito Alto | Vermelho | #D32F2F |
| 86-100 | Extremo | Vermelho Escuro | #B71C1C |

**Como verificar:**
1. Clicar em um município
2. Observar a cor do fill
3. Verificar se corresponde ao risco no popup

## T5: Clique Redireciona

- [ ] Clicar em um município abre o popup
- [ ] Popup contém:
  - [ ] Nome do município
  - [ ] Risco (0-100)
  - [ ] Categoria (Baixo/Moderado/Alto/etc)
  - [ ] Temperatura máxima média
  - [ ] Botão "Ver detalhes"
- [ ] Clique em "Ver detalhes" navega para `/dashboard/cidade/<id>`
- [ ] Ou diretamente clicar no município também redireciona

## T6: Responsividade

- [ ] Em desktop (1920px): Mapa ocupa 100% da largura
- [ ] Em tablet (768px): Mapa responsivo, cards em 2 colunas
- [ ] Em mobile (375px): Mapa responsivo, cards empilhados
- [ ] Legenda e estatísticas ajustam para mobile
- [ ] Controles de zoom permanecem acessíveis
- [ ] Não há scroll horizontal

**Teste com DevTools:**
```
F12 → Toggle device toolbar → Ctrl+Shift+M
```

## T7: Erro Quando API Vazia

- [ ] Se não houver dados de risco, mapa ainda carrega
- [ ] Aviso "Sem dados disponíveis" aparece (ou similar)
- [ ] Popup de município vazio não mostra dados
- [ ] Página não quebra

**Forçar erro (reset BD):**
```sql
DELETE FROM gold_clima_pe_diario;
```

## T8: Desempenho

- [ ] Tempo de carregamento do mapa: < 3 segundos
- [ ] Tempo de clique → popup: < 0.5 segundos
- [ ] Sem lag ao arrastar mapa
- [ ] Zoom é responsivo
- [ ] Sem memory leaks (DevTools → Memory)

**Teste com DevTools:**
```
F12 → Performance → Start recording → Interagir com mapa → Stop
```

## T9: Logs e Debugging

- [ ] DevTools Console não mostra erros vermelhos
- [ ] Requisições GET aparecem com status 200 (Network tab)
- [ ] Nenhum erro de CORS
- [ ] Logs do backend (Docker) não mostram exceções

**Ver logs:**
```bash
docker logs -f ilhas_calor_web
```

## T10: Compatibilidade Mobile

- [ ] Mapa funciona em Chrome mobile
- [ ] Mapa funciona em Safari iOS
- [ ] Funciona em Firefox mobile
- [ ] Touch gestures (pinch to zoom) funcionam
- [ ] Tap para abrir popup funciona
- [ ] Botões são grandes o suficiente para tap (48px mínimo)

**Teste com Emulador:**
```
DevTools → Toggle device toolbar → Selecionar iPhone/Android
```

## Testes Adicionais (Opcional)

### T11: Legenda e Estatísticas

- [ ] Legenda de cores exibe corretamente
- [ ] Estatísticas mostram:
  - [ ] Risco Máximo (maior valor entre municípios)
  - [ ] Risco Mínimo (menor valor)
  - [ ] Risco Médio (média aritmética)
  - [ ] Categoria Predominante (mais frequente)

### T12: Botão Resetar Mapa

- [ ] Clique em "Resetar Mapa" volta para view inicial
- [ ] Centraliza em Pernambuco
- [ ] Zoom volta para 8

### T13: Hover Effects

- [ ] Ao passar mouse sobre município, fill opacity aumenta
- [ ] Bordas ficam mais visíveis
- [ ] Cursor muda para pointer
- [ ] Efeito reverso ao sair

### T14: GeoJSON Estrutura

Verificar se GeoJSON está bem-formado:

```bash
python -c "
import json
with open('backend/app/static/geo/municipios_pe.geojson') as f:
    data = json.load(f)
    print(f'Type: {data[\"type\"]}')
    print(f'Features: {len(data[\"features\"])}')
    for feat in data['features'][:3]:
        print(f'  - {feat[\"properties\"][\"nome\"]}: {feat[\"geometry\"][\"type\"]}')
"
```

## Resultado Final

Após passar em todos os testes, execute:

```bash
git add -A
git commit -m "ETAPA 5.X: Teste mapa concluído - todos os testes passaram"
git push origin main
```

## Troubleshooting

### Mapa não carrega
- Verificar se Leaflet CDN está acessível: https://cdn.jsdelivr.net/npm/leaflet@1.9.4/
- Verificar DevTools Console para erros
- Limpar cache do navegador (Ctrl+Shift+Delete)

### GeoJSON não aparece
- Verificar se arquivo existe: `/static/geo/municipios_pe.geojson`
- Verificar tamanho do arquivo (> 100KB esperado)
- Verificar encoding UTF-8

### Cores erradas
- Verificar resposta de `/dashboard/mapa/dados`
- Verificar se `risco` é um número (0-100)
- Verificar função `colorByRisk()` no console

### Clique não redireciona
- Verificar se `id_cidade` está na resposta da API
- Testar URL manualmente: `/dashboard/cidade/1`
- Verificar console para erros JavaScript

### Popup não aparece
- Clicar no centro do município, não na borda
- Verificar se dados estão sendo carregados (`/dashboard/mapa/dados`)
- Verificar se GeoJSON tem `properties` válidas

## Notas

- GeoJSON de exemplo contém 8 municípios (para desenvolvimento)
- Para produção, substituir por GeoJSON completo do IBGE (143 municípios)
- Script `scripts/download_geojson.py` disponível para atualizar

