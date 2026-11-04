import pandas as pd


def filtrar_chamados_anteriores_aquisicao(
    dados: pd.DataFrame,
    ocorrencias: pd.DataFrame,
) -> pd.DataFrame:
    """Filtra as datas já diagnosticadas e registra a quantidade excluída."""
    tratados = dados.copy()
    controle = "chamados_excluidos_por_cronologia"
    if controle not in tratados.columns:
        tratados[controle] = 0

    for linha_excel, grupo in ocorrencias.groupby("linha_excel", sort=False):
        indice = int(linha_excel) - 2
        if indice not in tratados.index:
            raise ValueError("A ocorrência não corresponde a uma linha da entrada.")
        if not grupo["id_cliente"].eq(tratados.at[indice, "id_cliente"]).all():
            raise ValueError("O cliente da ocorrência difere da entrada.")
        aquisicao = pd.to_datetime(
            tratados.at[indice, "data_aquisicao_cliente"],
            format="%d/%m/%Y", errors="raise",
        )
        if (
            not grupo["data_aquisicao_interpretada"].eq(aquisicao).all()
            or not grupo["data_interpretada"].lt(aquisicao).all()
        ):
            raise ValueError("O diagnóstico não corresponde à aquisição atual.")

        valor_atual = tratados.at[indice, "data_chamado"]
        partes = [p.strip() for p in str(valor_atual).split(",") if p.strip()]
        excluir = set(grupo["valor_data"])
        restantes = [p for p in partes if p not in excluir]
        quantidade = len(partes) - len(restantes)
        if quantidade:
            if not grupo["valor_original"].eq(valor_atual).all():
                raise ValueError("A lista mudou depois do diagnóstico.")
            tratados.at[indice, "data_chamado"] = ", ".join(restantes)
            tratados.at[indice, controle] += quantidade

    return tratados
