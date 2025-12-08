# Documentação - ECharts Dashboard Charts

## Visão Geral

Este documento descreve o módulo JavaScript `DashboardCharts` que gerencia todos os gráficos ECharts no dashboard de ilhas de calor.

**Arquivo**: `backend/app/static/js/dashboard_charts.js`
**CDN ECharts**: https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js
**Versão**: 5.5.0

## Módulo DashboardCharts

O módulo é implementado como um **IIFE (Immediately Invoked Function Expression)** retornando uma API pública.

```javascript
const DashboardCharts = (function() {
  // Funções privadas e dados
  // ...
  
  // API pública
  return {
    loadTemperaturaChart,
    loadRiscoChart,
    loadHeatmapChart,
    loadMultipleCharts,
    fetchData,
    RISK_COLORS
  };
})();
```

### Constantes

#### `RISK_COLORS`
Mapa de cores para categorias de risco de calor:

```javascript
{
  'Baixo': '#10b981',        // Verde (Tailwind: green-500)
  'Moderado': '#3b82f6',     // Azul (Tailwind: blue-500)
  'Alto': '#f59e0b',         // Amarelo (Tailwind: amber-500)
  'Muito Alto': '#ef6d45',   // Laranja (Tailwind: orange-500)
  'Extremo': '#dc2626'       // Vermelho (Tailwind: red-600)
}
```

## Funções Públicas

### 1. `loadTemperaturaChart(domId, cidadeId, range)`

Carrega e renderiza gráfico de série temporal de temperatura.

**Parâmetros:**
- `domId` (string): ID do elemento HTML container
- `cidadeId` (number): ID da cidade no banco de dados
- `range` (number): Número de dias para visualizar

**Retorna:**
- Promise que resolve para instância do ECharts

**Exemplo:**
```javascript
DashboardCharts.loadTemperaturaChart('chart-temperatura', 1, 30)
  .then(chart => console.log('Gráfico carregado'))
  .catch(error => console.error(error));
```

**Gráfico Exibido:**
- Tipo: Line Chart com 3 séries
- Série 1: `temp_min` (Mínima) - Azul #3b82f6
- Série 2: `temp_media` (Média) - Laranja #f59e0b
- Série 3: `temp_max` (Máxima) - Vermelho #ef4444
- Eixo X: Data (YYYY-MM-DD)
- Eixo Y: Temperatura (°C)
- Tooltip: Mostra as 3 séries ao passar mouse

**Configuração ECharts:**
```javascript
{
  title: 'Série Temporal de Temperatura',
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  },
  legend: { data: ['Mínima', 'Média', 'Máxima'] },
  grid: { ... },
  xAxis: { type: 'category', boundaryGap: false },
  yAxis: { type: 'value', name: 'Temperatura (°C)' },
  series: [
    { name: 'Mínima', type: 'line', smooth: true, itemStyle: { color: '#3b82f6' } },
    { name: 'Média', type: 'line', smooth: true, itemStyle: { color: '#f59e0b' } },
    { name: 'Máxima', type: 'line', smooth: true, itemStyle: { color: '#ef4444' } }
  ]
}
```

---

### 2. `loadRiscoChart(domId, cidadeId, range)`

Carrega e renderiza gráfico de distribuição de risco de calor (barra).

**Parâmetros:**
- `domId` (string): ID do elemento HTML container
- `cidadeId` (number): ID da cidade
- `range` (number): Número de dias

**Retorna:**
- Promise que resolve para instância do ECharts

**Exemplo:**
```javascript
DashboardCharts.loadRiscoChart('chart-risco', 1, 7)
```

**Gráfico Exibido:**
- Tipo: Bar Chart
- Eixo X: Categorias de risco (Baixo, Moderado, Alto, Muito Alto, Extremo)
- Eixo Y: Contagem de dias
- Cores: Aplicadas automaticamente conforme `RISK_COLORS`
- Label: Número de dias aparece no topo de cada barra

**Processamento de Dados:**
1. Fetch de `/api/gold/{cidadeId}/serie?limit={range * 30}`
2. Contagem de ocorrências por categoria
3. Renderização de barra com cor correspondente

---

### 3. `loadHeatmapChart(domId, cidadeId)`

Carrega e renderiza heatmap térmico dos últimos 7 dias.

**Parâmetros:**
- `domId` (string): ID do elemento HTML container
- `cidadeId` (number): ID da cidade

**Retorna:**
- Promise que resolve para instância do ECharts

**Exemplo:**
```javascript
DashboardCharts.loadHeatmapChart('chart-heatmap', 1)
```

**Gráfico Exibido:**
- Tipo: Heatmap
- Eixo X: 7 últimos dias (formato YYYY-MM-DD)
- Eixo Y: Tipos de temperatura (Mínima, Média, Máxima)
- Cores: Escala de temperatura 15-40°C (azul → vermelho)
- Label: Temperatura em °C centralizada em cada célula

**Mapa de Cores:**
```javascript
{
  min: 15,
  max: 40,
  color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
}
// 15°C = azul escuro (#313695)
// 27°C = amarelo claro (#ffffbf)
// 40°C = vermelho escuro (#a50026)
```

**Processamento de Dados:**
1. Fetch de `/api/gold/{cidadeId}/diario?limit=7`
2. Construção de matriz: X=dia (0-6), Y=tipo (0-2), Z=temperatura
3. Renderização com visual map

---

### 4. `loadMultipleCharts(chartConfigs)`

Carrega múltiplos gráficos em paralelo (Promise.all).

**Parâmetros:**
- `chartConfigs` (Array<Object>): Array de configurações

**Exemplo:**
```javascript
DashboardCharts.loadMultipleCharts([
  { domId: 'chart-temperatura', type: 'temperatura', cidadeId: 1, range: 30 },
  { domId: 'chart-risco', type: 'risco', cidadeId: 1, range: 30 },
  { domId: 'chart-heatmap', type: 'heatmap', cidadeId: 1 }
])
.then(() => console.log('Todos os gráficos carregados'))
.catch(error => console.error(error));
```

**Objeto de Configuração:**
```javascript
{
  domId: string,      // ID do container
  type: string,       // 'temperatura' | 'risco' | 'heatmap'
  cidadeId: number,   // ID da cidade
  range?: number      // Dias (7, 30, 90, 365) - opcional para heatmap
}
```

---

### 5. `fetchData(url)`

Wrapper para fetch com tratamento de erros e parsing JSON.

**Parâmetros:**
- `url` (string): URL da API

**Retorna:**
- Promise que resolve para array de dados ou null se erro

**Exemplo:**
```javascript
DashboardCharts.fetchData('/api/gold/cidades')
  .then(cidades => console.log(cidades))
  .catch(error => console.error(error));
```

**Tratamento de Erros:**
- HTTP error → throw Error
- JSON parsing error → throw Error
- API response com `success: false` → throw Error
- Erro logado no console.error

---

## Fluxo de Dados

```
Templates (cidade_charts.html, index.html, cidade.html)
    ↓
DashboardCharts.loadTemperaturaChart/loadRiscoChart/loadHeatmapChart
    ↓
DashboardCharts.fetchData(URL)
    ↓
API: /api/gold/<id>/serie ou /api/gold/<id>/diario
    ↓
Backend Flask → GoldClimaPeDiario.query
    ↓
JSON Response: { success: true, data: [...] }
    ↓
ECharts.init() + chart.setOption(option)
    ↓
Renderização no DOM
```

## Responsividade

Todos os gráficos incluem handler para resize:

```javascript
window.addEventListener('resize', () => {
  if (chart) chart.resize();
});
```

Quando viewport muda de tamanho, ECharts automaticamente:
1. Redimensiona canvas
2. Recalcula posições de elementos
3. Atualiza legendas e tooltips

## HTMX Integration

Quando HTMX carrega `cidade_charts.html` partial:

1. `htmx:afterSwap` event dispara
2. IIFE em `cidade_charts.html` detecta evento
3. Chama `DashboardCharts.loadMultipleCharts([...])`
4. Gráficos são renderizados no novo DOM

## Tratamento de Erros

Cada função trata erros gracefully:

```javascript
loadTemperaturaChart('invalid-id', 1, 30)
// Loga: "Container #invalid-id não encontrado"
// Retorna: Promise.reject('Gráfico não inicializado')
```

## Performance

- **Parallelismo**: `loadMultipleCharts` carrega 3 gráficos simultaneamente
- **Caching**: Sem cache de cliente (servidor controla via headers)
- **Lazy Loading**: Gráficos carregados apenas quando necessário
- **Memory**: Instâncias ECharts limpas ao trocar de cidade (ECharts dispose)

## Dependências Externas

- **ECharts 5.5.0**: CDN
- **Fetch API**: Browser nativo (polyfill não necessário em navegadores modernos)

## Exemplos de Uso Avançado

### Recarregar gráfico ao clicar botão
```javascript
document.getElementById('refresh-btn').addEventListener('click', () => {
  DashboardCharts.loadTemperaturaChart('chart-temperatura', 1, 30);
});
```

### Mudar cor de risco dinamicamente
```javascript
DashboardCharts.RISK_COLORS['Alto'] = '#ff6b6b'; // Vermelho customizado
DashboardCharts.loadRiscoChart('chart-risco', 1, 30);
```

### Debug no console
```javascript
// Verificar disponibilidade do módulo
console.log(DashboardCharts);

// Testar fetchData
DashboardCharts.fetchData('/api/gold/1/resumo').then(data => console.table(data));

// Listar cores
console.table(DashboardCharts.RISK_COLORS);
```

## Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| "Uncaught ReferenceError: echarts is not defined" | CDN não carregou | Verificar URL do CDN em base_dashboard.html |
| Gráfico em branco | Dados vazios ou erro na API | Verificar console.error, validar cidadeId |
| Gráfico não redimensiona | Window resize handler não ativo | Verificar se chart foi inicializado |
| HTMX não carrega charts | htmx:afterSwap não dispara | Verificar header HX-Request no servidor |
| Cores erradas no risk chart | RISK_COLORS não atualizado | Confirmar valor de `risco_calor` na API |

