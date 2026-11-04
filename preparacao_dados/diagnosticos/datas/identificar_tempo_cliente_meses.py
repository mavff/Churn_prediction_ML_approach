import pandas as pd


def identificar_tempo_cliente_meses(
    dados: pd.DataFrame,
    aquisicoes: pd.DataFrame,
    protocolo: dict[str, object],
) -> pd.DataFrame:
    """Calcula meses completos até o corte usando as aquisições já interpretadas."""
    # Alinha as datas da fonte aos clientes que permaneceram após as etapas anteriores.
    referencias = aquisicoes.reindex(dados.index)
    if not dados["id_cliente"].equals(referencias["id_cliente"]):
        raise ValueError("As aquisições não correspondem aos clientes da entrada.")
    aquisicao = referencias["data_interpretada"]
    corte = pd.Timestamp(protocolo["data_corte"])
    if aquisicao.isna().any() or aquisicao.gt(corte).any():
        raise ValueError("Tempo de cliente exige aquisição conhecida e não posterior ao corte.")
    meses = (corte.year - aquisicao.dt.year) * 12 + corte.month - aquisicao.dt.month
    # Só completa outro mês quando o corte alcança o dia da aquisição.
    meses = (meses - aquisicao.dt.day.gt(corte.day).astype(int)).astype("Int64")
    return pd.DataFrame({
        "id_cliente": dados["id_cliente"],
        "data_aquisicao_entrada": dados["data_aquisicao_cliente"],
        "data_corte": corte.strftime("%d/%m/%Y"),
        "tempo_cliente_meses": meses,
    })
