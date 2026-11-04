import pandas as pd


def padronizar_datas_aquisicao(
    dados: pd.DataFrame,
    ocorrencias: pd.DataFrame,
) -> pd.DataFrame:
    """Aplica o de-para somente às aquisições já identificadas."""
    tratados = dados.copy()
    indices = ocorrencias["linha_excel"].astype(int) - 2
    valores = ocorrencias["data_interpretada"].dt.strftime("%d/%m/%Y")
    # Atribui na ordem das ocorrências, sem realinhar pelos índices da tabela de evidências.
    tratados.loc[indices, "data_aquisicao_cliente"] = valores.to_numpy()
    return tratados
