// Handle simulation HTMX responses and update charts/insights
(function () {
  const resultContainer = document.getElementById('simulation-result');
  const chartEl = document.getElementById('simulation-chart');

  document.body.addEventListener('htmx:afterRequest', async (evt) => {
    if (!evt.detail || !evt.detail.elt || evt.detail.elt.id !== 'simulator-form') return;
    const resp = evt.detail.xhr;
    try {
      const json = JSON.parse(resp.responseText || '{}');
      const data = json.data || [];
      const labels = data.map((d) => d.datetime_utc || '').reverse();
      const temps = data.map((d) => d.temperature || d.apparent_temperature || 0).reverse();
      renderTempHeatLineChart(chartEl, labels, temps, temps);
      renderInsights(data);
    } catch (err) {
      console.error('Erro ao processar simulação', err);
    }
  });

  function renderInsights(data) {
    if (!resultContainer) return;
    if (!data.length) {
      resultContainer.innerHTML = '<p class="text-sm text-slate-500">Nenhum dado simulado.</p>';
      return;
    }
    const maxTemp = Math.max(...data.map((d) => d.temperature || 0));
    const avgTemp = data.reduce((acc, d) => acc + (d.temperature || 0), 0) / data.length;
    const risk = maxTemp > 40 ? 'Alto risco de ilha de calor' : 'Risco moderado';
    resultContainer.innerHTML = `
      <div class="card">
        <p class="metric-label">Risco de ilhas de calor</p>
        <p class="metric-value">${risk}</p>
      </div>
      <div class="card">
        <p class="metric-label">Tendência projetada</p>
        <p class="metric-value">${avgTemp.toFixed(1)} °C</p>
      </div>
      <div class="card">
        <p class="metric-label">Impacto esperado</p>
        <p class="metric-value">Máx: ${maxTemp.toFixed(1)} °C</p>
      </div>`;
  }
})();
