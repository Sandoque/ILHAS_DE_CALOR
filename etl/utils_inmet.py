"""Funções auxiliares para parsing de dados do INMET."""

def normalizar_nome_cidade(nome: str) -> str:
    """Normaliza nomes de cidades para padrão interno."""
    return nome.strip().title()
