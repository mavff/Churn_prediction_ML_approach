import pandas as pd


def identificar_aquisicoes_fora_padrao(aquisicoes: pd.DataFrame) -> pd.DataFrame:
    """Seleciona datas válidas cuja representação difere de DD/MM/AAAA."""
    esperado = aquisicoes["data_interpretada"].dt.strftime("%d/%m/%Y")
    return aquisicoes.loc[aquisicoes["valor_original"].astype("string").ne(esperado)].copy()
