import pandas as pd


def padronizar_datas_aquisicao(dados: pd.DataFrame) -> pd.DataFrame:
    """Converte aquisições textuais AAAA-MM-DD para DD/MM/AAAA."""
    tratados = dados.copy()
    campo = "data_aquisicao_cliente"
    valores = tratados[campo].astype("string")
    formato_iso = valores.str.fullmatch(r"\d{4}-\d{2}-\d{2}", na=False)

    tratados.loc[formato_iso, campo] = pd.to_datetime(
        valores.loc[formato_iso],
        format="%Y-%m-%d",
        errors="raise",
    ).dt.strftime("%d/%m/%Y")

    return tratados
