import pandas as pd


def substituir_datas_por_contagem_chamados(
    dados: pd.DataFrame,
    avaliacao: pd.DataFrame,
) -> pd.DataFrame:
    """Substitui a lista pela contagem identificada, preservando os demais campos."""
    if not dados.index.equals(avaliacao.index) or not dados["id_cliente"].equals(avaliacao["id_cliente"]):
        raise ValueError("A avaliação de chamados não corresponde à entrada.")
    if "chamados_suporte" in dados.columns:
        raise ValueError("A entrada já contém chamados_suporte.")
    posicao = dados.columns.get_loc("data_chamado")
    tratados = dados.drop(columns="data_chamado").copy()
    tratados.insert(posicao, "chamados_suporte", avaliacao["chamados_suporte"])
    return tratados
