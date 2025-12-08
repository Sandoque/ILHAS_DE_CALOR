# 🔧 CORREÇÃO: openpyxl Missing Dependency

## Problema
```
ImportError: Missing optional dependency 'openpyxl'.
Use pip or conda to install openpyxl.
```

**Causa**: O pacote `openpyxl` não estava em `requirements.txt`, mas é necessário para ler arquivos Excel (`.xlsx`) no MapBiomas ETL.

## Solução Aplicada

### 1. Adicionar ao requirements.txt
```bash
# backend/requirements.txt
openpyxl  ← Adicionado
```

### 2. Instalar no container Docker
```bash
docker compose exec web pip install openpyxl
```

### 3. Testar
```bash
docker compose exec web python -m etl.pipeline.cli run-mapbiomas
# ✅ Agora funciona!
```

## Commit
```
a5cfa4f fix: adicionar openpyxl ao requirements.txt
```

## Por que foi necessário?

O MapBiomas ETL baixa um arquivo Excel `.xlsx` e o processa:
```python
# etl/mapbiomas/extract_relevant_sheets.py
pd.read_excel(xlsx_path, sheet_name=RELEVANT_SHEET, engine="openpyxl")
```

Pandas usa `openpyxl` como engine para ler Excel. Sem ele, ocorre erro `ImportError`.

## Próximos Passos

Sempre que adicionar uma nova dependência:
1. Adicionar ao `backend/requirements.txt`
2. Instalar localmente: `pip install -r backend/requirements.txt`
3. Instalar no Docker: `docker compose exec web pip install <package>`
4. Fazer commit

## Pacotes Relacionados

Outros pacotes que podem ser necessários no futuro:
- `xlrd` (para Excel antigo .xls)
- `xlwt` (para escrever Excel)
- `openpyxl` (para Excel moderno .xlsx) ✅ AGORA INCLUÍDO

---

**Data**: 08 de Dezembro de 2025  
**Status**: ✅ RESOLVIDO
