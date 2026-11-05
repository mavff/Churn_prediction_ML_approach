import pandas as pd
from sklearn.compose import ColumnTransformer

from preparacao_dados.imputacao.converter_ausencias_para_nan import converter_ausencias_para_nan


def aplicar_codificacao(X: pd.DataFrame, ajuste: ColumnTransformer) -> pd.DataFrame:
    """Aplica somente transform com os parâmetros do treino e nomeia as colunas resultantes."""
    if list(X.columns) != list(ajuste.feature_names_in_):
        raise ValueError("Os preditores diferem dos usados no ajuste da codificação.")
    valores = ajuste.transform(converter_ausencias_para_nan(X))
    return pd.DataFrame(valores, index=X.index, columns=ajuste.get_feature_names_out())
