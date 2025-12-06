// Helpers to render ECharts visualizations

function renderTempHeatLineChart(elId, labels, temps = [], heatIndex = []) {
  const dom = typeof elId === 'string' ? document.getElementById(elId) : elId;
  if (!dom) return;
  const chart = echarts.init(dom);
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Temperatura', 'Índice de calor'] },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value', name: '°C' },
    series: [
      { name: 'Temperatura', type: 'line', smooth: true, data: temps, areaStyle: { opacity: 0.1 } },
      { name: 'Índice de calor', type: 'line', smooth: true, data: heatIndex, areaStyle: { opacity: 0.05 } },
    ],
  };
  chart.setOption(option);
  window.addEventListener('resize', () => chart.resize());
  return chart;
}

function renderPrecipBarChart(elId, labels, precip = []) {
  const dom = typeof elId === 'string' ? document.getElementById(elId) : elId;
  if (!dom) return;
  const chart = echarts.init(dom);
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value', name: 'mm' },
    series: [{ name: 'Precipitação', type: 'bar', data: precip, itemStyle: { color: '#22c55e' } }],
  });
  window.addEventListener('resize', () => chart.resize());
  return chart;
}

function renderRankingChart(elId, labels, values) {
  const dom = typeof elId === 'string' ? document.getElementById(elId) : elId;
  if (!dom) return;
  const chart = echarts.init(dom);
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', name: '°C' },
    yAxis: { type: 'category', data: labels, inverse: true },
    series: [{ type: 'bar', data: values, itemStyle: { color: '#f97316' } }],
  });
  window.addEventListener('resize', () => chart.resize());
  return chart;
}

async function renderHeatmap(container, url) {
  if (!container) return;
  container.innerHTML = '';
  const chart = echarts.init(container);
  chart.showLoading('default', { text: 'Carregando mapa...' });
  try {
    const resp = await fetch(url);
    const json = await resp.json();
    const data = json.data || [];
    const seriesData = data.map((item) => ({
      name: item.station_code,
      value: [item.longitude, item.latitude, item.avg_heat_index || item.avg_apparent_temp],
    }));
    chart.setOption({
      backgroundColor: '#f8fafc',
      tooltip: {
        trigger: 'item',
        formatter: (params) => `${params.name}: ${params.value[2]?.toFixed(1) || '--'} °C`,
      },
      visualMap: {
        min: 20,
        max: 50,
        text: ['Alto', 'Baixo'],
        realtime: true,
        calculable: true,
        inRange: { color: ['#22c55e', '#f59e0b', '#ef4444'] },
      },
      geo: {
        map: 'world',
        roam: true,
        itemStyle: {
          areaColor: '#e2e8f0',
          borderColor: '#cbd5e1',
        },
      },
      series: [
        {
          name: 'Índice de calor',
          type: 'scatter',
          coordinateSystem: 'geo',
          data: seriesData,
          symbolSize: (val) => Math.max(8, Math.min(18, (val[2] || 0) / 2)),
          itemStyle: { color: '#ef4444' },
        },
      ],
    });
  } catch (err) {
    console.error('Erro ao renderizar heatmap', err);
  } finally {
    chart.hideLoading();
  }
}

window.renderTempHeatLineChart = renderTempHeatLineChart;
window.renderPrecipBarChart = renderPrecipBarChart;
window.renderRankingChart = renderRankingChart;
window.renderHeatmap = renderHeatmap;
