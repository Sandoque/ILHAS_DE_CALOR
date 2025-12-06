(function() {
    const chartEl = document.getElementById('chart-cidades');
    if (!chartEl || !window.echarts) return;

    const chart = echarts.init(chartEl);
    const cidades = ['Recife', 'Olinda', 'Caruaru', 'Petrolina', 'Garanhuns'];
    const valores = [82, 74, 63, 71, 52];

    chart.setOption({
        tooltip: {},
        xAxis: { type: 'category', data: cidades },
        yAxis: { type: 'value', name: 'Índice de risco' },
        series: [{
            data: valores,
            type: 'bar',
            itemStyle: { color: '#047857' }
        }]
    });
})();
