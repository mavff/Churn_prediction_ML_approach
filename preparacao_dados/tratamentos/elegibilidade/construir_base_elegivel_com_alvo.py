import pandas as pd


def construir_base_elegivel_com_alvo(
    dados: pd.DataFrame,
    avaliacao: pd.DataFrame,
) -> pd.DataFrame:
    """Seleciona os participantes identificados e acrescenta corte e alvo à cópia."""
    if not dados.index.equals(avaliacao.index) or not dados["id_cliente"].equals(avaliacao["id_cliente"]):
        raise ValueError("A avaliação não corresponde à entrada.")
    if "churn" in dados.columns or "data_corte" in dados.columns:
        raise ValueError("A entrada desta etapa deve estar sem alvo e corte.")
    participantes = avaliacao["elegivel"].eq(True)
    tratados = dados.loc[participantes].copy()
    tratados["data_corte"] = avaliacao.loc[participantes, "data_corte"]
    tratados["churn"] = avaliacao.loc[participantes, "churn"]
    return tratados
