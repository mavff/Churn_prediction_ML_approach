import pandas as pd
from sklearn.compose import ColumnTransformer

from preparacao_dados.imputacao.converter_ausencias_para_nan import converter_ausencias_para_nan


def aplicar_imputacao(X: pd.DataFrame, ajuste: ColumnTransformer) -> pd.DataFrame:
    """Aplica somente transform com os valores do treino e restaura os tipos da entrada."""
    if list(X.columns) != list(ajuste.feature_names_in_):
        raise ValueError("Os preditores diferem dos usados no ajuste da imputação.")
    valores = ajuste.transform(converter_ausencias_para_nan(X))
    # Os valores aprendidos já respeitam o dicionário; os tipos Int64, Float64 e string voltam iguais.
    return pd.DataFrame(valores, index=X.index, columns=X.columns).astype(X.dtypes.to_dict())
