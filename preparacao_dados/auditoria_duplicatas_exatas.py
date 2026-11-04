import pandas as pd


def identificar_duplicatas_exatas(
    dados: pd.DataFrame,
) -> pd.DataFrame:
    """Retorna as cópias exatas que aparecem após a primeira ocorrência."""

    copias_excedentes = dados.duplicated(keep="first")

    return dados.loc[copias_excedentes].copy()