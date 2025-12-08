# TAREFA 4 – Instruções para Rodar e Testar com Docker

## Status: 📋 GUIA DE TESTES

### Pré-requisitos

- Docker instalado (v20.10+)
- Docker Compose instalado (v2.0+)
- Terminal/PowerShell com acesso aos comandos Docker

### Passo 1: Preparar o Arquivo GeoJSON

**Executado automaticamente pela TAREFA 1.**

O arquivo `backend/app/static/geo/municipios_pe.geojson` deve existir antes de rodar Docker.

**Verificação**:
```powershell
Test-Path "c:\Projetos\ILHAS_DE_CALOR\backend\app\static\geo\municipios_pe.geojson"
# Esperado: True
```

### Passo 2: Build e Deploy Docker

```bash
# 1. Navegar para raiz do projeto
cd c:\Projetos\ILHAS_DE_CALOR

# 2. Build da imagem Docker
docker-compose build

# 3. Iniciar serviços (postgres + web)
docker-compose up -d

# 4. Aguardar inicialização (~10-15s)
Start-Sleep -Seconds 15

# 5. Verificar status
docker-compose ps
```

**Saída esperada**:
```
NAME                COMMAND                  SERVICE      STATUS       PORTS
ilhas_calor_web     "python backend/run_"   web          Up 10 days   0.0.0.0:8000->5000/tcp
ilhas_calor_postgres "docker-entrypoint..."  postgres     Up 10 days   5432/tcp
```

### Passo 3: Testar Endpoints da API

#### Teste 3.1: Endpoint do GeoJSON

```bash
# Verificar se arquivo foi carregado corretamente
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/geo/municipios-pe" `
  -UseBasicParsing -ErrorAction SilentlyContinue

if ($response.StatusCode -eq 200) {
    $json = $response.Content | ConvertFrom-Json
    Write-Host "✅ Endpoint /api/geo/municipios-pe respondendo"
    Write-Host "   - Tipo: $($json.type)"
    Write-Host "   - Features: $($json.features.Count)"
} else {
    Write-Host "❌ Erro HTTP $($response.StatusCode)"
}
```

#### Teste 3.2: Arquivo GeoJSON Estático

```bash
# Verificar se arquivo estático é acessível
curl -I "http://localhost:8000/static/geo/municipios_pe.geojson"
# Esperado: HTTP/1.1 200 OK
```

#### Teste 3.3: Mapa Interativo

```bash
# 1. Abrir navegador
Start-Process "http://localhost:8000/dashboard/mapa"

# 2. Inspecionar Console do Navegador (F12 > Console)
# Verificar:
# - Nenhum erro de rede (Status 200)
# - Nenhum erro de JavaScript
# - Mapa carregou
# - 185 municípios visíveis como polígonos
```

### Passo 4: Teste de Funcionalidade Completa

#### 4.1 Verificar Carregamento do Mapa

No navegador, abra `http://localhost:8000/dashboard/mapa` e:

- [ ] Mapa exibe corretamente
- [ ] Zoom e pan funcionam (mouse scroll, drag)
- [ ] 185 municípios visíveis (como áreas coloridas)
- [ ] Cores representam nível de risco (escala gradual)

#### 4.2 Testar Interações

- [ ] Passar mouse sobre município → cor mais escura (hover)
- [ ] Clicar em município → abre popup com:
  - [ ] Nome do município
  - [ ] Risco (0-100)
  - [ ] Categoria
  - [ ] Temperatura máxima
  - [ ] Botão "Ver detalhes"

#### 4.3 Testar Navegação

- [ ] Clicar em "Ver detalhes" → redireciona para `/dashboard/cidade/{id}`
- [ ] Página de detalhe carrega dados específicos do município

#### 4.4 Verificar DevTools

```javascript
// No console do navegador (F12 > Console), executar:

// 1. Verificar carregamento do GeoJSON
console.log('Features carregadas:', geoJsonLayer.toGeoJSON().features.length);
// Esperado: 185

// 2. Verificar dados de risco
console.log('Municípios com dados:', Object.keys(municipiosData).length);
// Esperado: > 0

// 3. Verificar aplicação de cores
const layer = geoJsonLayer.getLayers()[0];
console.log('Estilo aplicado:', layer.options.style);
// Verificar se cores estão sendo aplicadas dinamicamente
```

### Passo 5: Testes de Erro

#### Teste 5.1: Falta de Arquivo GeoJSON

```bash
# 1. Remover arquivo (simulação)
Remove-Item "c:\Projetos\ILHAS_DE_CALOR\backend\app\static\geo\municipios_pe.geojson"

# 2. Tentar acessar mapa
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/geo/municipios-pe" `
  -UseBasicParsing -ErrorAction SilentlyContinue

if ($response.StatusCode -eq 404) {
    Write-Host "✅ Erro 404 retornado corretamente (arquivo não encontrado)"
} else {
    Write-Host "❌ Status inesperado: $($response.StatusCode)"
}

# 3. Restaurar arquivo (re-executar TAREFA 1 ou copiar backup)
.\venv\Scripts\python scripts/fetch_ibge_malhas_pe.py
```

#### Teste 5.2: Database Offline

```bash
# 1. Parar banco de dados
docker-compose stop postgres

# 2. Tentar acessar `/dashboard/cidade/{id}`
# - Deve falhar com erro de conexão BD
# - Mas mapa (`/dashboard/mapa`) deve continuar respondendo

# 3. Reiniciar banco
docker-compose start postgres
```

### Passo 6: Performance e Logging

#### 6.1 Verificar Tamanho do Arquivo

```powershell
$file = "c:\Projetos\ILHAS_DE_CALOR\backend\app\static\geo\municipios_pe.geojson"
$size = (Get-Item $file).Length / 1MB
Write-Host "Tamanho do GeoJSON: $($size.ToString('F2')) MB"
# Esperado: ~3.1 MB
```

#### 6.2 Verificar Logs do Container

```bash
# Ver últimos logs da aplicação web
docker-compose logs -f web --tail=50

# Verificar requisições HTTP
docker-compose logs web | Select-String "GET /api/geo"
```

#### 6.3 Medir Tempo de Resposta

```powershell
$start = Get-Date
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/geo/municipios-pe" `
  -UseBasicParsing
$duration = (Get-Date) - $start

Write-Host "Tempo de resposta: $($duration.TotalMilliseconds) ms"
# Esperado: < 500 ms (para arquivo 3.1 MB)
```

### Passo 7: Limpeza e Reset

```bash
# Parar containers
docker-compose stop

# Remover containers (preserva volumes)
docker-compose rm -f

# Remover tudo (incluindo volumes)
docker-compose down -v

# Re-iniciar do zero
docker-compose up -d
```

### Troubleshooting

#### Problema: Porta 8000/5000 já em uso

```bash
# Encontrar processo usando porta
netstat -ano | findstr :8000

# Matar processo (substitua PID)
taskkill /PID <PID> /F

# Ou usar porta diferente
docker-compose up -d -p 9000:5000
```

#### Problema: Permissão negada ao arquivo GeoJSON

```bash
# Verificar permissões
icacls "backend\app\static\geo\municipios_pe.geojson"

# Se necessário, conceder permissões
icacls "backend\app\static\geo\municipios_pe.geojson" /grant:r "%USERNAME%":F
```

#### Problema: GeoJSON não carrega no mapa

1. Verificar console do navegador (F12)
2. Verificar resposta HTTP (Network tab)
3. Executar TAREFA 1 novamente para regenerar arquivo
4. Limpar cache do navegador (Ctrl+Shift+Delete)

#### Problema: Database sem dados de risco

```bash
# 1. Verificar se tabela gold existe
docker-compose exec postgres psql -U ilhas_user -d ilhas_de_calor \
  -c "SELECT COUNT(*) FROM public.gold_clima_pe_diario;"

# 2. Se vazia, executar ETL
docker-compose exec web python -m etl.pipeline.cli run-full

# 3. Verificar dados
docker-compose exec postgres psql -U ilhas_user -d ilhas_de_calor \
  -c "SELECT DISTINCT id_cidade FROM public.gold_clima_pe_diario LIMIT 5;"
```

### Próximo Passo

⬇️ **TAREFA 5** – Limpeza e Validação
- Remover `scripts/download_geojson.py` (antigo)
- Validar que todas as chamadas IBGE usam v4
- Documentar mudanças
- Commit final
