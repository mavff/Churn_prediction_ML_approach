import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def separar_atributos_alvo(dados: pd.DataFrame) -> dict[str, object]:
    """Separa os oito preditores do dicionário, o alvo e os campos de auditoria."""
    atributos = [campo for campo, regra in definir_dicionario_dados().items() if regra["tipo"] != "alvo"]
    faltantes = sorted(set([*atributos, "churn"]).difference(dados.columns))
    if faltantes:
        raise ValueError(f"Colunas ausentes para montar os conjuntos: {faltantes}.")
    # Dados de cancelamento, identificadores e metadados não entram em X.
    return {
        "X": dados[atributos].copy(),
        "y": dados["churn"].copy(),
        "metadados": dados.drop(columns=[*atributos, "churn"]).copy(),
        "ordem_colunas": dados.columns.tolist(),
    }
