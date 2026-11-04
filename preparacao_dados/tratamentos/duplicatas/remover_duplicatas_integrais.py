import pandas as pd


def remover_duplicatas_integrais(dados: pd.DataFrame) -> pd.DataFrame:
    """Remove cópias integrais, mantendo a primeira ocorrência da fonte."""
    return dados.drop_duplicates(keep="first").copy()