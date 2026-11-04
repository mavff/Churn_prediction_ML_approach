import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def padronizar_categorias(
    dados: pd.DataFrame,
    ocorrencias: pd.DataFrame,
) -> pd.DataFrame:
    """Aplica o de-para e marca ausências e categorias desconhecidas sem preenchê-las."""
    tratados = dados.copy()
    for campo, regra in definir_dicionario_dados().items():
        if regra["tipo"] == "categoria":
            tratados[campo] = tratados[campo].astype("string")
    # Cada ocorrência já indica a categoria correta ou a ausência a aplicar; não estima valores.
    for campo, grupo in ocorrencias.groupby("campo", sort=False):
        indices = grupo["linha_excel"].astype(int) - 2
        ids = tratados.loc[indices, "id_cliente"].tolist()
        valores = dados.loc[indices, campo].astype(object).reset_index(drop=True)
        originais = grupo["valor_antes"].astype(object).reset_index(drop=True)
        if ids != grupo["id_cliente"].tolist() or not valores.equals(originais):
            raise ValueError("O de-para de categorias não corresponde à entrada.")
        tratados.loc[indices, campo] = grupo["valor_depois"].to_numpy()
    return tratados
