"""Download dos arquivos históricos do INMET."""

def baixar_arquivos_inmet(anos: list[int]) -> None:
    """Baixa e organiza os ZIPs/CSVs do INMET para os anos fornecidos."""
    print(f"Baixando arquivos para anos: {anos}")
