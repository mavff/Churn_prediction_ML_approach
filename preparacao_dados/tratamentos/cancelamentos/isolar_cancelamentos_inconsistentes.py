import pandas as pd


def isolar_cancelamentos_inconsistentes(
    dados: pd.DataFrame,
    ocorrencias: pd.DataFrame,
) -> pd.DataFrame:
    """Isola datas inconsistentes, preservando clientes e marcando a incerteza."""
    tratados = dados.copy()
    campo = "data_ocorrencia_churn"
    controle = "cancelamento_inconsistente"
    if controle not in tratados.columns:
        tratados[controle] = False

    for linha_excel, grupo in ocorrencias.groupby("linha_excel", sort=False):
        indice = int(linha_excel) - 2
        if indice not in tratados.index:
            raise ValueError("A ocorrência não corresponde a uma linha da entrada.")
        if not grupo["id_cliente"].eq(tratados.at[indice, "id_cliente"]).all():
            raise ValueError("O cliente da ocorrência difere da entrada.")
        atual = tratados.at[indice, campo]
        if atual == "" and bool(tratados.at[indice, controle]):
            continue
        aquisicao = pd.to_datetime(
            tratados.at[indice, "data_aquisicao_cliente"],
            format="%d/%m/%Y", errors="raise",
        )
        if (
            not grupo["valor_data"].eq(str(atual).strip()).all()
            or not grupo["data_aquisicao_interpretada"].eq(aquisicao).all()
            or not grupo["data_interpretada"].lt(aquisicao).all()
        ):
            raise ValueError("O diagnóstico não corresponde ao cancelamento atual.")
        tratados.at[indice, campo] = ""
        tratados.at[indice, controle] = True

    return tratados
