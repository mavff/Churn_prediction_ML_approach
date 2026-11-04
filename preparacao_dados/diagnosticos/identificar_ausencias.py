import pandas as pd


def identificar_ausencias(valores: pd.Series) -> pd.Series:
    """Reconhece nulos, espaços e marcadores textuais explícitos nos preditores."""
    # Zero não é marcador de ausência; sua validade depende do domínio de cada campo.
    marcadores = {"", "na", "n/a", "nan", "none", "null"}
    textos = valores.astype("string").str.strip().str.casefold()
    return valores.isna() | textos.isin(marcadores)
