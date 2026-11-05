import numpy as np
import pandas as pd


def converter_ausencias_para_nan(X: pd.DataFrame) -> pd.DataFrame:
    """Representa pd.NA como np.nan, formato aceito pelo SimpleImputer, sem alterar valores."""
    entrada = pd.DataFrame(index=X.index)
    for campo in X.columns:
        if pd.api.types.is_numeric_dtype(X[campo].dtype):
            entrada[campo] = X[campo].astype("float64")
        else:
            entrada[campo] = X[campo].astype(object).where(X[campo].notna(), np.nan)
    return entrada
