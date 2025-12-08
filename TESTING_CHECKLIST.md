# Testing Checklist - ETAPA 4: Dashboard Interativo

Este documento descreve os testes manuais a realizar para validar o dashboard.

## Pré-requisitos

```bash
# 1. Iniciar stack Docker
docker-compose up --build

# 2. Verificar se banco contém dados GOLD
docker exec -it ilhas_calor_postgres psql -U ilhas_user -d ilhas_de_calor -c "SELECT COUNT(*) FROM gold_clima_pe_diario;"

# 3. Se vazio, rodar ETL
python -m etl.pipeline.cli run-gold

# 4. Acessar dashboard
http://localhost:5000/dashboard
```

## Testes

### T1: Página Principal (/dashboard)
- [ ] Página carrega sem erros
- [ ] Título "Dashboard - Ilhas de Calor - PE" aparece
- [ ] Dropdown "Selecione uma cidade" é carregado via API (/api/gold/cidades)
- [ ] Aparecem 3 cards: "Temperatura Média Hoje", "Risco Atual", "Tendência (7 dias)"
- [ ] Seção "Cidades Principais" mostra 6 cidades em grid
- [ ] Clicking no dropdown permite selecionar uma cidade
- [ ] Clicking no botão "Ir" navega para /dashboard/cidade/<id>

### T2: Endpoint /api/gold/cidades
- [ ] GET /api/gold/cidades retorna HTTP 200
- [ ] Resposta JSON contém `{ "success": true, "data": [...] }`
- [ ] Cada cidade tem: `id_cidade`, `nome_cidade`, `uf`, `codigo_ibge`
- [ ] Lista está ordenada por nome_cidade (A-Z)

### T3: Página Detalhe Cidade (/dashboard/cidade/<id>)
- [ ] Página carrega sem erros para cidade válida
- [ ] Header mostra nome da cidade (ex: "Recife")
- [ ] Card de risco mostra valor atual (ex: "Alto")
- [ ] 4 cards de métricas mostram valores: Temp Max/Min, Amplitude, Dias de Calor
- [ ] Botões de range (7/30/90/365 dias) estão presentes

### T4: Endpoint /api/gold/<id>/resumo
- [ ] GET /api/gold/1/resumo retorna HTTP 200 (id_cidade=1)
- [ ] Resposta contém: `nome_cidade`, `risco_calor`, `temp_max`, `temp_min`, `umidade_media`, `dias_risco_alto_7d`, `tendencia_temp`
- [ ] `risco_calor` é um de: "Baixo", "Moderado", "Alto", "Muito Alto", "Extremo"
- [ ] `dias_risco_alto_7d` é número inteiro entre 0-7
- [ ] `tendencia_temp` é um de: "aumentando", "diminuindo", "estável"

### T5: Endpoint /api/gold/<id>/serie
- [ ] GET /api/gold/1/serie retorna HTTP 200
- [ ] Resposta contém array de objetos com: `data`, `temp_min`, `temp_media`, `temp_max`, `risco_calor`
- [ ] Query param `?limit=30` limita a 30 registros
- [ ] Query params `?start_date=2025-01-01&end_date=2025-01-31` filtram por data

### T6: Carregamento de Gráficos
- [ ] Ao navegar para /dashboard/cidade/<id>, 3 gráficos carregam
  1. **Temperatura (linha)**: Exibe min/média/max com cores azul/laranja/vermelho
  2. **Risco de Calor (barra)**: Exibe contagem de dias por categoria com cores
  3. **Heatmap**: Exibe últimos 7 dias com intensidade de cores (15-40°C)
- [ ] Gráficos podem ser redimensionados (responsive)
- [ ] Tooltip aparece ao passar mouse sobre gráfico

### T7: HTMX Integration - Range Button Clicks
- [ ] Clicking "7 dias" recarrega gráficos SEM refreshar página
  - [ ] Header HTMX: `HX-Request: true` é enviado
  - [ ] Response é partial HTML (apenas gráficos, sem header/nav)
  - [ ] Charts são substituídos no DOM sem piscar
  - [ ] Spinner aparece durante carregamento
- [ ] Mesmo para "30 dias", "90 dias", "365 dias"
- [ ] Dados dos gráficos refletem o período selecionado

### T8: Cores de Risco de Calor
Verificar se cores correspondem ao esquema definido em `dashboard_charts.js`:
```
Baixo      → Verde (#10b981)
Moderado   → Azul (#3b82f6)
Alto       → Amarelo (#f59e0b)
Muito Alto → Laranja (#ef6d45)
Extremo    → Vermelho (#dc2626)
```
- [ ] Badge de risco muda cor conforme categoria
- [ ] Gráfico de risco (barra) colorido corretamente
- [ ] CSS classes `risk-*` aplicadas corretamente

### T9: Responsividade
- [ ] Em desktop (1920px): Layout 3-coluna para cards
- [ ] Em tablet (768px): Layout 2-coluna
- [ ] Em mobile (375px): Layout 1-coluna, sem quebras
- [ ] Gráficos redimensionam ao viewport mudar
- [ ] Dropdown/botões não quebram em mobile

### T10: Tratamento de Erros
- [ ] GET /dashboard/cidade/999 (cidade inexistente) retorna erro 404
- [ ] Se API /api/gold/cidades falhar, console.error é registrado
- [ ] Se gráfico não conseguir carregar dados, msg de erro aparece (sem crash)
- [ ] Network throttle (3G): Página continua responsiva com spinner

### T11: Performance
- [ ] Tempo até "primeiro gráfico visível": < 2 segundos (incluindo API calls)
- [ ] HTMX range click → gráficos substituídos: < 1 segundo
- [ ] Sem memory leaks ao mudar entre cidades (DevTools Memory)

### T12: JavaScript Module
- [ ] `DashboardCharts.loadTemperaturaChart(domId, cidadeId, range)` funciona
- [ ] `DashboardCharts.loadRiscoChart(domId, cidadeId, range)` funciona
- [ ] `DashboardCharts.loadHeatmapChart(domId, cidadeId)` funciona
- [ ] `DashboardCharts.fetchData(url)` trata erros e retorna Promise
- [ ] `DashboardCharts.loadMultipleCharts([...])` carrega 3 gráficos em paralelo

## Resultado Final

Após passar todos os testes, executar:

```bash
# Fazer commit de qualquer pequeno ajuste
git add -A
git commit -m "ETAPA 4: Dashboard finalizado e testado"
git push origin main
```

## Notas de Debugging

### DevTools Browser
```javascript
// No console:
DashboardCharts.fetchData('/api/gold/cidades').then(data => console.log(data))
DashboardCharts.loadTemperaturaChart('chart-temperatura', 1, 7)
htmx.logAll() // Enable HTMX logging
```

### PostgreSQL
```sql
-- Verificar dados GOLD
SELECT COUNT(*) FROM gold_clima_pe_diario;
SELECT DISTINCT id_cidade, nome_cidade FROM gold_clima_pe_diario ORDER BY nome_cidade;
SELECT * FROM gold_clima_pe_diario WHERE id_cidade = 1 ORDER BY data DESC LIMIT 10;
```

### Logs
```bash
# Backend logs (Docker)
docker logs -f ilhas_calor_web

# Flask em dev (local)
python backend/run.py
# Ativar DEBUG: FLASK_DEBUG=1 python backend/run.py
```

## Pontos Críticos

1. **Banco de dados vazio**: Se `COUNT(*)` for 0, rodar `python -m etl.pipeline.cli run-gold`
2. **Porta 5000 em uso**: Parar outro processo: `lsof -i :5000` + `kill -9 <PID>`
3. **CORS**: Se frontend em diferente porta, verificar `backend/app/__init__.py` (CORS habilitado)
4. **Timezone**: Dados estão em UTC, conversão para UTC-3 (America/Recife) no Python

