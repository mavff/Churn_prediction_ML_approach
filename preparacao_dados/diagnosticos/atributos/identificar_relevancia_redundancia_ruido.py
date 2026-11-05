import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def identificar_relevancia_redundancia_ruido(
    X: pd.DataFrame,
    y: pd.Series,
    limiar_irrelevancia: float,
    limiar_redundancia: float,
) -> pd.DataFrame:
    """Mede associação com churn, correlação entre atributos e extremos, sem alterar X."""
    if X.isna().any().any() or not X.index.equals(y.index):
        raise ValueError("O diagnóstico exige preditores imputados e alinhados ao alvo.")
    dicionario = definir_dicionario_dados()
    # Cada categoria vira um indicador 0/1, como as dummies usadas na Aula 3.
    colunas = {}
    origens = {}
    for campo in X.columns:
        regra = dicionario[campo]
        if regra["tipo"] == "categoria":
            for categoria in regra["de_para"].values():
                colunas[f"{campo}={categoria}"] = X[campo].eq(categoria).astype(float)
                origens[f"{campo}={categoria}"] = campo
        else:
            colunas[campo] = X[campo].astype(float)
            origens[campo] = campo
    atributos = pd.DataFrame(colunas, index=X.index)
    correlacoes = atributos.assign(churn=y.astype(float)).corr()
    linhas = []
    for nome, campo in origens.items():
        valores = atributos[nome]
        # Indicadores do mesmo campo são complementares; só campos diferentes indicam redundância.
        outros = correlacoes.loc[nome, [n for n, c in origens.items() if c != campo]]
        parceiro = outros.abs().fillna(0).idxmax()
        frequencias = valores.value_counts(normalize=True)
        regra = dicionario[campo]
        inferior = superior = extremos = pd.NA
        # Extremos só fazem sentido em contagens e valores contínuos, não em binários ou indicadores.
        if regra["tipo"] in {"Int64", "Float64"} and regra["maximo"] > 1:
            q1, q3 = valores.quantile([0.25, 0.75])
            inferior, superior = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
            extremos = int((~valores.between(inferior, superior)).sum())
        sinais = []
        # Correlação indefinida (atributo constante) também não mostra relação com o alvo.
        if not abs(correlacoes.loc[nome, "churn"]) >= limiar_irrelevancia:
            sinais.append("candidato_irrelevante")
        if abs(outros[parceiro]) >= limiar_redundancia:
            sinais.append("candidato_redundante")
        if extremos is not pd.NA and extremos > 0:
            sinais.append("extremos_a_investigar")
        linhas.append({
            "campo": campo,
            "atributo": nome,
            "correlacao_churn": correlacoes.loc[nome, "churn"],
            "atributo_mais_correlacionado": parceiro,
            "correlacao_atributo": outros[parceiro],
            "valor_mais_frequente": frequencias.index[0],
            "proporcao_valor_mais_frequente": frequencias.iloc[0],
            "limite_inferior_iqr": inferior,
            "limite_superior_iqr": superior,
            "extremos_iqr": extremos,
            "situacao": "; ".join(sinais) or "sem_sinalizacao",
        })
    return pd.DataFrame(linhas).astype({
        "limite_inferior_iqr": "Float64", "limite_superior_iqr": "Float64", "extremos_iqr": "Int64",
    })
