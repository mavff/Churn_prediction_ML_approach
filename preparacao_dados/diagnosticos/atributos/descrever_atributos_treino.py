import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def descrever_atributos_treino(X: pd.DataFrame, y: pd.Series) -> dict[str, object]:
    """Resume a distribuição e a taxa de churn de cada preditor do treino, sem alterar valores."""
    if X.isna().any().any() or not X.index.equals(y.index):
        raise ValueError("A estatística descritiva exige o treino imputado e alinhado ao alvo.")
    dicionario = definir_dicionario_dados()
    linhas = []
    for campo in X.columns:
        regra = dicionario[campo]
        # Contagens e valores contínuos recebem medidas de posição; binários e categorias, frequências.
        if regra["tipo"] in {"Int64", "Float64"} and regra["maximo"] > 1:
            valores = X[campo].astype(float)
            q1, mediana, q3 = valores.quantile([0.25, 0.5, 0.75])
            linhas.append({
                "campo": campo, "clientes": len(valores), "media": valores.mean(),
                "desvio_padrao": valores.std(), "minimo": valores.min(), "q1": q1, "mediana": mediana,
                "q3": q3, "maximo": valores.max(), "assimetria": valores.skew(),
                "media_churn_0": valores[y.eq(0)].mean(), "media_churn_1": valores[y.eq(1)].mean(),
            })
            continue
        categorias = regra["de_para"].values() if regra["tipo"] == "categoria" else sorted(X[campo].unique())
        for categoria in categorias:
            grupo = X[campo].eq(categoria)
            linhas.append({
                "campo": campo, "categoria": str(categoria), "clientes": int(grupo.sum()),
                "proporcao": grupo.mean(), "taxa_churn": y[grupo].mean() if grupo.any() else pd.NA,
            })
    colunas = [
        "campo", "categoria", "clientes", "proporcao", "taxa_churn", "media", "desvio_padrao", "minimo",
        "q1", "mediana", "q3", "maximo", "assimetria", "media_churn_0", "media_churn_1",
    ]
    tabela = pd.DataFrame(linhas).reindex(columns=colunas)
    numericos = int(tabela["categoria"].isna().sum())
    resumo = pd.DataFrame([
        ("Clientes do treino", len(X), len(X)),
        ("Taxa de churn no treino (%)", round(100 * float(y.mean()), 2), round(100 * float(y.mean()), 2)),
        ("Atributos numéricos descritos", numericos, numericos),
        ("Categorias e indicadores descritos", len(tabela) - numericos, len(tabela) - numericos),
    ], columns=["indicador", "antes", "depois"])
    return {
        "resumo": resumo,
        "evidencias": tabela,
        "regra": (
            "Somente no treino imputado: média, desvio, quartis e assimetria em contagens e valores contínuos; "
            "frequência e taxa de churn por categoria e indicador binário (Aula 3)"
        ),
        "decisao": "Descrição exploratória; nenhum valor alterado",
    }
