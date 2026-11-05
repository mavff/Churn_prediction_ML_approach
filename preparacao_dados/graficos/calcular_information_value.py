import numpy as np
import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def calcular_information_value(X: pd.DataFrame, y: pd.Series, faixas: int = 10) -> pd.DataFrame:
    """Calcula o Information Value de cada preditor: categorias como estão, numéricas em faixas de quantis."""
    dicionario = definir_dicionario_dados()
    eventos = y.astype(int).eq(1)
    linhas = []
    for campo in X.columns:
        regra = dicionario[campo]
        # Contagens e contínuos viram faixas de quantis; quantis repetidos se fundem em uma faixa só.
        if regra["tipo"] in {"Int64", "Float64"} and regra["maximo"] > 1:
            grupos = pd.qcut(X[campo].astype(float), q=faixas, duplicates="drop")
        else:
            grupos = X[campo].astype("string")
        tabela = pd.crosstab(grupos, eventos).reindex(columns=[False, True], fill_value=0)
        # Meio cliente em cada célula evita log de zero quando uma faixa não tem uma das classes.
        nao = (tabela[False] + 0.5) / (tabela[False].sum() + 0.5 * len(tabela))
        sim = (tabela[True] + 0.5) / (tabela[True].sum() + 0.5 * len(tabela))
        woe = np.log(nao / sim)
        linhas.append({"campo": campo, "information_value": float(((nao - sim) * woe).sum()), "faixas": len(tabela)})
    return pd.DataFrame(linhas).sort_values("information_value", ascending=False, ignore_index=True)
