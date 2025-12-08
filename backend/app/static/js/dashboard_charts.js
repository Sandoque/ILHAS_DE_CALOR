/**
 * dashboard_charts.js
 * 
 * Módulo modular para gerenciar gráficos ECharts no dashboard
 * Funções reutilizáveis para: temperatura, risco de calor, heatmap
 * 
 * Dependências: ECharts 5.5.0 (global: echarts)
 */

const DashboardCharts = (function() {
  'use strict';

  /**
   * Cores padrão para risco de calor
   * Baixo/Moderado/Alto/Muito Alto/Extremo
   */
  const RISK_COLORS = {
    'Baixo': '#10b981',        // verde
    'Moderado': '#3b82f6',     // azul
    'Alto': '#f59e0b',         // amarelo
    'Muito Alto': '#ef6d45',   // laranja
    'Extremo': '#dc2626'       // vermelho
  };

  /**
   * Inicializa um gráfico ECharts com tratamento de responsividade
   * @param {string} domId - ID do container HTML
   * @returns {Object} instância do ECharts
   */
  function initChart(domId) {
    const container = document.getElementById(domId);
    if (!container) {
      console.error(`Container #${domId} não encontrado`);
      return null;
    }
    const chart = echarts.init(container);
    
    // Redimensionar gráfico ao viewport mudar
    window.addEventListener('resize', () => {
      if (chart) chart.resize();
    });
    
    return chart;
  }

  /**
   * Carrega dados de uma URL e retorna Promise com JSON
   * @param {string} url - URL da API
   * @returns {Promise<Array>} Array de dados JSON
   */
  function fetchData(url) {
    return fetch(url)
      .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then(result => {
        if (!result.success || !result.data) {
          throw new Error(result.error || 'Resposta inválida da API');
        }
        return result.data;
      })
      .catch(error => {
        console.error(`Erro ao buscar dados de ${url}:`, error);
        return null;
      });
  }

  /**
   * Carrega e renderiza gráfico de série temporal de temperatura
   * Exibe: temp_min (azul), temp_media (laranja), temp_max (vermelho)
   * 
   * @param {string} domId - ID do container (ex: 'chart-temperatura')
   * @param {number} cidadeId - ID da cidade
   * @param {number} range - Número de dias para consultar
   * @returns {Promise<Object>} Promise que resolve quando gráfico é renderizado
   */
  function loadTemperaturaChart(domId, cidadeId, range) {
    const chart = initChart(domId);
    if (!chart) return Promise.reject('Gráfico não inicializado');

    const url = `/api/gold/${cidadeId}/serie?limit=${range * 30 || 365}`;
    
    return fetchData(url).then(data => {
      if (!data || data.length === 0) {
        chart.setOption({
          title: { text: 'Sem dados disponíveis', left: 'center' }
        });
        return chart;
      }

      // Extrair datas e temperaturas
      const dates = data.map(d => d.data || d.date);
      const tempMin = data.map(d => parseFloat(d.temp_min || 0));
      const tempMedia = data.map(d => parseFloat(d.temp_media || 0));
      const tempMax = data.map(d => parseFloat(d.temp_max || 0));

      const option = {
        title: { text: 'Série Temporal de Temperatura' },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' },
          formatter: (params) => {
            if (!params || params.length === 0) return '';
            const date = params[0].axisValue;
            let html = `<strong>${date}</strong><br/>`;
            params.forEach(p => {
              html += `${p.marker} ${p.seriesName}: ${p.value.toFixed(1)}°C<br/>`;
            });
            return html;
          }
        },
        legend: { data: ['Mínima', 'Média', 'Máxima'] },
        grid: { left: '10%', right: '10%', bottom: '10%', top: '15%', containLabel: true },
        xAxis: {
          type: 'category',
          data: dates,
          boundaryGap: false
        },
        yAxis: {
          type: 'value',
          name: 'Temperatura (°C)',
          axisLabel: { formatter: '{value}°C' }
        },
        series: [
          {
            name: 'Mínima',
            data: tempMin,
            type: 'line',
            smooth: true,
            itemStyle: { color: '#3b82f6' },
            areaStyle: { color: 'rgba(59, 130, 246, 0.1)' }
          },
          {
            name: 'Média',
            data: tempMedia,
            type: 'line',
            smooth: true,
            itemStyle: { color: '#f59e0b' },
            areaStyle: { color: 'rgba(245, 158, 11, 0.1)' }
          },
          {
            name: 'Máxima',
            data: tempMax,
            type: 'line',
            smooth: true,
            itemStyle: { color: '#ef4444' },
            areaStyle: { color: 'rgba(239, 68, 68, 0.1)' }
          }
        ]
      };

      chart.setOption(option);
      return chart;
    });
  }

  /**
   * Carrega e renderiza gráfico de risco de calor (barra)
   * Exibe: contagem de dias por categoria de risco
   * 
   * @param {string} domId - ID do container (ex: 'chart-risco')
   * @param {number} cidadeId - ID da cidade
   * @param {number} range - Número de dias para consultar
   * @returns {Promise<Object>} Promise que resolve quando gráfico é renderizado
   */
  function loadRiscoChart(domId, cidadeId, range) {
    const chart = initChart(domId);
    if (!chart) return Promise.reject('Gráfico não inicializado');

    const url = `/api/gold/${cidadeId}/serie?limit=${range * 30 || 365}`;
    
    return fetchData(url).then(data => {
      if (!data || data.length === 0) {
        chart.setOption({
          title: { text: 'Sem dados disponíveis', left: 'center' }
        });
        return chart;
      }

      // Contar ocorrências por categoria de risco
      const riskCounts = {
        'Baixo': 0,
        'Moderado': 0,
        'Alto': 0,
        'Muito Alto': 0,
        'Extremo': 0
      };

      data.forEach(d => {
        const risk = d.risco_calor || 'Baixo';
        if (riskCounts.hasOwnProperty(risk)) {
          riskCounts[risk]++;
        }
      });

      const categories = Object.keys(riskCounts);
      const counts = Object.values(riskCounts);
      const colors = categories.map(cat => RISK_COLORS[cat] || '#ccc');

      const option = {
        title: { text: 'Distribuição de Risco de Calor' },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: (params) => {
            if (!params || params.length === 0) return '';
            const p = params[0];
            return `<strong>${p.name}</strong><br/>Dias: ${p.value}`;
          }
        },
        legend: { show: false },
        grid: { left: '10%', right: '10%', bottom: '10%', top: '15%', containLabel: true },
        xAxis: {
          type: 'category',
          data: categories,
          axisLabel: { interval: 0, rotate: 45 }
        },
        yAxis: {
          type: 'value',
          name: 'Número de Dias',
          axisLabel: { formatter: '{value}' }
        },
        series: [
          {
            data: counts,
            type: 'bar',
            itemStyle: {
              color: (params) => colors[params.dataIndex]
            },
            label: {
              show: true,
              position: 'top',
              formatter: '{c}'
            }
          }
        ]
      };

      chart.setOption(option);
      return chart;
    });
  }

  /**
   * Carrega e renderiza heatmap térmico (7 últimos dias)
   * Exibe: distribuição de temperatura (min/media/max) por dia
   * 
   * @param {string} domId - ID do container (ex: 'chart-heatmap')
   * @param {number} cidadeId - ID da cidade
   * @returns {Promise<Object>} Promise que resolve quando gráfico é renderizado
   */
  function loadHeatmapChart(domId, cidadeId) {
    const chart = initChart(domId);
    if (!chart) return Promise.reject('Gráfico não inicializado');

    const url = `/api/gold/${cidadeId}/diario?limit=7`;
    
    return fetchData(url).then(data => {
      if (!data || data.length === 0) {
        chart.setOption({
          title: { text: 'Sem dados disponíveis', left: 'center' }
        });
        return chart;
      }

      // Preparar dados: X=dias, Y=tipo temp, Z=valor
      const heatmapData = [];
      data.forEach((day, dayIdx) => {
        const tempMin = parseFloat(day.temp_min || 0);
        const tempMedia = parseFloat(day.temp_media || 0);
        const tempMax = parseFloat(day.temp_max || 0);
        
        heatmapData.push([dayIdx, 0, tempMin]);   // Mínima
        heatmapData.push([dayIdx, 1, tempMedia]); // Média
        heatmapData.push([dayIdx, 2, tempMax]);   // Máxima
      });

      const dates = data.map(d => d.data || d.date);
      const tempTypes = ['Mínima', 'Média', 'Máxima'];

      const option = {
        title: { text: 'Heatmap de Temperatura (últimos 7 dias)' },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const date = dates[params.value[0]];
            const type = tempTypes[params.value[1]];
            const temp = params.value[2];
            return `${date}<br/>${type}: ${temp.toFixed(1)}°C`;
          }
        },
        grid: { left: '15%', right: '10%', bottom: '10%', top: '15%', containLabel: true },
        xAxis: {
          type: 'category',
          data: dates,
          splitArea: { show: true }
        },
        yAxis: {
          type: 'category',
          data: tempTypes,
          splitArea: { show: true }
        },
        visualMap: {
          min: 15,
          max: 40,
          calculable: true,
          orient: 'vertical',
          right: '3%',
          bottom: '10%',
          inRange: {
            color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
          },
          textStyle: { color: '#666' }
        },
        series: [
          {
            name: 'Temperatura (°C)',
            type: 'heatmap',
            data: heatmapData,
            label: {
              show: true,
              formatter: (params) => `${params.value[2].toFixed(0)}°`
            }
          }
        ]
      };

      chart.setOption(option);
      return chart;
    });
  }

  /**
   * Carrega múltiplos gráficos em paralelo
   * @param {Array<Object>} chartConfigs - Configuração: [{ domId, type, cidadeId, range }]
   * @returns {Promise<Array>} Array de promises
   */
  function loadMultipleCharts(chartConfigs) {
    return Promise.all(
      chartConfigs.map(config => {
        switch (config.type) {
          case 'temperatura':
            return loadTemperaturaChart(config.domId, config.cidadeId, config.range);
          case 'risco':
            return loadRiscoChart(config.domId, config.cidadeId, config.range);
          case 'heatmap':
            return loadHeatmapChart(config.domId, config.cidadeId);
          default:
            console.warn(`Tipo de gráfico desconhecido: ${config.type}`);
            return Promise.reject(`Tipo inválido: ${config.type}`);
        }
      })
    );
  }

  /**
   * API pública do módulo
   */
  return {
    loadTemperaturaChart,
    loadRiscoChart,
    loadHeatmapChart,
    loadMultipleCharts,
    fetchData,
    RISK_COLORS
  };
})();
