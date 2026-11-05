import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.imputacao.converter_ausencias_para_nan import converter_ausencias_para_nan


def ajustar_imputacao(X_treino: pd.DataFrame, protocolo: dict[str, object]) -> ColumnTransformer:
    """Aprende medianas e modas somente no treino, encapsuladas em um ColumnTransformer."""
    dicionario = definir_dicionario_dados()
    preditores = [campo for campo, regra in dicionario.items() if regra["tipo"] != "alvo"]
    if list(X_treino.columns) != preditores:
        raise ValueError("A imputação deve ser ajustada nos oito preditores do dicionário, sem alvo ou metadados.")
    transformadores = []
    for campo in preditores:
        estrategia = protocolo[f"estrategia_{campo}"]
        if estrategia == "zero":
            imputador = SimpleImputer(strategy="constant", fill_value=0)
        else:
            imputador = SimpleImputer(strategy="median" if estrategia == "mediana" else "most_frequent")
        transformadores.append((campo, imputador, [campo]))
    ajuste = ColumnTransformer(transformadores, verbose_feature_names_out=False)
    ajuste.fit(converter_ausencias_para_nan(X_treino))
    # O valor aprendido será inserido nos três conjuntos; precisa respeitar o dicionário antes de ser usado.
    for campo in preditores:
        valor = ajuste.named_transformers_[campo].statistics_[0]
        regra = dicionario[campo]
        if regra["tipo"] == "categoria":
            valido = valor in regra["de_para"].values()
        else:
            valido = regra["minimo"] <= valor <= regra["maximo"] and (regra["tipo"] != "Int64" or float(valor).is_integer())
        if not valido:
            raise ValueError(f"Valor aprendido fora do dicionário em {campo}: {valor}; mediana fracionária exige regra própria.")
    return ajuste
