# UX Data-Driven Story

## Problema
Ilhas de calor urbanas em Pernambuco agravam riscos à saúde, energia e infraestrutura. Gestores precisam identificar áreas críticas, priorizar intervenções e comunicar riscos de forma clara.

## Por que dados
- Dados climáticos horários permitem detectar picos e padrões locais.
- Métricas derivadas (índice de calor, amplitude térmica, chuvas) contextualizam risco além da temperatura bruta.
- Simulações ajudam a testar cenários de mitigação ou agravamento antes de agir.

## Como a experiência ajuda decisores
- **Identificar áreas mais quentes**: Heatmap estadual e ranking mostram rapidamente onde concentrar esforços.
- **Priorizar intervenções**: Séries diárias por estação destacam tendências e amplitudes que exigem infraestrutura verde ou ações emergenciais.
- **Comunicar risco**: Cards e rótulos claros (°C, mm) traduzem análises complexas para públicos não técnicos.
- **Planejar cenários**: O simulador permite testar aumentos de temperatura, mudanças de precipitação e umidade para avaliar impactos e risco de ilhas de calor.

## Escolhas de UX (Tailwind + HTMX + ECharts)
- **Hierarquia clara**: Hero com título e subtítulo define propósito; cards destacam indicadores-chave; seções dividem mapa, ranking e séries temporais.
- **Divulgação progressiva**: HTMX carrega métricas e tabelas sob demanda, mantendo a interface rápida e focada; detalhes por cidade ficam em página dedicada.
- **Contexto visual**: ECharts fornece linhas, barras e scatter maps com cores consistentes para calor e chuva, reforçando leitura imediata de risco.
- **Interações leves**: HTMX permite atualizações pontuais (heatmap por data, ranking, séries) sem recarregar a página; estados de carregamento informam o usuário.
- **Simulações guiadas**: Formulário simples define variáveis climáticas; o gráfico de projeção e blocos de insight retornam riscos e tendências em linguagem direta.

## Narrativa para apresentação / portfólio
1. **Framing**: "Pernambuco enfrenta ondas de calor mais frequentes; precisamos monitorar e agir rápido." 
2. **Dados**: "Ingerimos séries históricas do INMET, calculamos métricas de conforto térmico e armazenamos em um DW PostgreSQL." 
3. **Produto**: "A API Flask expõe endpoints usados por um front-end leve em Tailwind + HTMX + ECharts para dashboards e simulador." 
4. **Impacto**: "Gestores visualizam hotspots, acompanham tendências diárias e testam cenários de aumento de temperatura ou redução de chuvas para priorizar intervenções." 
5. **Próximos passos**: "Integrar geocodificação IBGE, alertas em tempo real e testes de usabilidade com públicos não técnicos."
