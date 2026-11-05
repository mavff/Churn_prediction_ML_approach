import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.imputacao.converter_ausencias_para_nan import converter_ausencias_para_nan


def ajustar_codificacao(X_treino: pd.DataFrame, protocolo: dict[str, object], escala: str) -> ColumnTransformer:
    """Aprende a escala e o one-hot somente no treino, encapsulados em um ColumnTransformer."""
    escaladores = {"padronizada": StandardScaler, "minmax": MinMaxScaler}
    if f"escala_{escala}" not in protocolo or escala not in escaladores:
        raise ValueError(f"Escala não prevista no protocolo: {escala}.")
    if X_treino.isna().any().any():
        raise ValueError("A codificação exige os preditores imputados.")
    dicionario = definir_dicionario_dados()
    papeis = {campo: protocolo[f"codificacao_{campo}"] for campo in X_treino.columns}
    escalados = [campo for campo, papel in papeis.items() if papel == "escalar"]
    categoricos = [campo for campo, papel in papeis.items() if papel == "one_hot"]
    mantidos = [campo for campo, papel in papeis.items() if papel == "manter"]
    # As categorias vêm do dicionário, para que as colunas sejam as mesmas mesmo se uma faltar no treino.
    categorias = [list(dicionario[campo]["de_para"].values()) for campo in categoricos]
    ajuste = ColumnTransformer([
        ("escala", escaladores[escala](), escalados),
        ("one_hot", OneHotEncoder(categories=categorias, handle_unknown="ignore", sparse_output=False), categoricos),
        ("binarios", "passthrough", mantidos),
    ], verbose_feature_names_out=False)
    return ajuste.fit(converter_ausencias_para_nan(X_treino))
