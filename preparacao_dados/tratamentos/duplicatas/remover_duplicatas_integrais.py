import pandas as pd


def remover_duplicatas_integrais(
    dados: pd.DataFrame,
    ocorrencias: pd.DataFrame,
) -> pd.DataFrame:
    """Remove as cópias identificadas, sem procurar duplicatas novamente."""
    indices = ocorrencias["linha_excel_removida"].astype(int) - 2
    return dados.drop(index=indices).copy()
