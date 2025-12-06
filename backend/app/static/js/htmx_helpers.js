// Global HTMX listeners for loading indicator and errors
(function () {
  const loader = document.getElementById('htmx-loading');
  document.body.addEventListener('htmx:beforeRequest', () => loader && loader.classList.remove('hidden'));
  document.body.addEventListener('htmx:afterRequest', () => loader && loader.classList.add('hidden'));
  document.body.addEventListener('htmx:sendError', (evt) => {
    console.error('HTMX send error', evt.detail);
    loader && loader.classList.add('hidden');
  });
  document.body.addEventListener('htmx:responseError', (evt) => {
    console.error('HTMX response error', evt.detail);
    loader && loader.classList.add('hidden');
  });

  document.body.addEventListener('htmx:afterOnLoad', (evt) => {
    const target = evt.target;
    const resp = evt.detail.xhr?.responseText;
    if (!resp) return;
    try {
      const json = JSON.parse(resp);
      if (target.dataset.metric) {
        renderMetricCard(target, json, target.dataset.metric);
      }
      if (target.id === 'ranking-loader') {
        renderRanking(json);
      }
      if (target.dataset.dailyMetric) {
        renderDailyMetric(target, json, target.dataset.dailyMetric);
      }
      if (target.id === 'daily-loader') {
        renderDailyTable(json);
      }
    } catch (err) {
      console.error('Erro ao processar resposta HTMX', err);
    }
  });

  function renderMetricCard(container, json, type) {
    const card = container.querySelector('.metric-value') ? container : container.querySelector('div');
    const setValues = (label, value) => {
      card.querySelector('.metric-label').textContent = label;
      card.querySelector('.metric-value').textContent = value;
    };
    const data = json.data || [];
    if (type === 'max-temp') {
      const val = data[0]?.peak_temp || data[0]?.peak_apparent_temp || '--';
      setValues('Maior temperatura (7d)', typeof val === 'number' ? `${val.toFixed(1)} °C` : '--');
    } else if (type === 'hottest-station') {
      const val = data[0]?.station_code || '--';
      setValues('Estação mais quente', val);
    } else if (type === 'amplitude') {
      const maxAmp = Math.max(...data.map((d) => d.thermal_amplitude || 0));
      setValues('Maior amplitude térmica', maxAmp ? `${maxAmp.toFixed(1)} °C` : '--');
    }
  }

  function renderRanking(json) {
    const data = json.data || [];
    const labels = data.map((d) => d.station_code);
    const values = data.map((d) => d.peak_apparent_temp || d.peak_temp || 0);
    const table = document.createElement('div');
    table.className = 'divide-y divide-slate-100';
    data.forEach((row, idx) => {
      const div = document.createElement('div');
      div.className = 'flex items-center justify-between py-2 text-sm';
      div.innerHTML = `<span class=\"font-semibold text-slate-800\">${idx + 1}. ${row.station_code}</span><span class=\"text-slate-600\">${(row.peak_apparent_temp || row.peak_temp || 0).toFixed(1)} °C</span>`;
      table.appendChild(div);
    });
    const loader = document.getElementById('ranking-loader');
    if (loader) loader.replaceWith(table);
    renderRankingChart('ranking-chart', labels, values);
  }

  function renderDailyMetric(container, json, type) {
    const card = container.querySelector('.metric-value') ? container : container.querySelector('div');
    const setValues = (label, value) => {
      card.querySelector('.metric-label').textContent = label;
      card.querySelector('.metric-value').textContent = value;
    };
    const row = (json.data || [])[0] || {};
    if (type === 'max24') {
      setValues('Máx. 24h', row.max_temp ? `${row.max_temp.toFixed(1)} °C` : '--');
    } else if (type === 'min24') {
      setValues('Mín. 24h', row.min_temp ? `${row.min_temp.toFixed(1)} °C` : '--');
    } else if (type === 'heatindex') {
      setValues('Índice de calor', row.heat_index_max ? `${row.heat_index_max.toFixed(1)} °C` : '--');
    } else if (type === 'amplitude') {
      setValues('Amplitude térmica', row.thermal_amplitude ? `${row.thermal_amplitude.toFixed(1)} °C` : '--');
    }
  }

  function renderDailyTable(json) {
    const data = json.data || [];
    const table = document.createElement('div');
    table.className = 'text-sm divide-y divide-slate-100';
    data.forEach((row) => {
      const div = document.createElement('div');
      div.className = 'py-2 flex items-center justify-between';
      div.innerHTML = `<span class=\"font-medium text-slate-800\">${row.date || '--'}</span><span class=\"text-slate-600\">Máx: ${(row.max_temp || 0).toFixed(1)} °C · Chuva: ${(row.precipitation_total || 0).toFixed(1)} mm</span>`;
      table.appendChild(div);
    });
    const loader = document.getElementById('daily-loader');
    if (loader) loader.replaceWith(table);
  }
})();
