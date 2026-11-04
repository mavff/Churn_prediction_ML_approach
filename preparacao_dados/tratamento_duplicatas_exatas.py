import pandas as pd


def remover_duplicatas_exatas(
    dados: pd.DataFrame,
) -> pd.DataFrame:
    """Remove cópias exatas, mantendo a primeira ocorrência."""

    return dados.drop_duplicates(keep="first").copy()