import pandas as pd


def adicionar_tempo_cliente_meses(
    dados: pd.DataFrame,
    avaliacao: pd.DataFrame,
) -> pd.DataFrame:
    """Acrescenta o tempo calculado, preservando a aquisição e os demais campos."""
    if not dados.index.equals(avaliacao.index) or not dados["id_cliente"].equals(avaliacao["id_cliente"]):
        raise ValueError("A avaliação de tempo de cliente não corresponde à entrada.")
    if "tempo_cliente_meses" in dados.columns:
        raise ValueError("A entrada já contém tempo_cliente_meses.")
    tratados = dados.copy()
    posicao = tratados.columns.get_loc("data_aquisicao_cliente") + 1
    tratados.insert(posicao, "tempo_cliente_meses", avaliacao["tempo_cliente_meses"])
    return tratados
