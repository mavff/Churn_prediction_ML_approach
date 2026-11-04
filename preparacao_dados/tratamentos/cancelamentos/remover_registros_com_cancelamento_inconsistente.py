import pandas as pd


def remover_registros_com_cancelamento_inconsistente(
    dados: pd.DataFrame,
    ocorrencias: pd.DataFrame,
) -> pd.DataFrame:
    """Exclui diretamente os registros identificados, sem esvaziar datas antes."""
    indices = ocorrencias["linha_excel"].astype(int) - 2
    return dados.drop(index=indices).copy()
