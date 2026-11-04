import pandas as pd


def identificar_eventos_anteriores_aquisicao(
    datas_por_campo: dict[str, pd.DataFrame],
    campo: str,
) -> pd.DataFrame:
    """Relaciona cada evento à aquisição da mesma linha da fonte."""
    referencias = datas_por_campo["data_aquisicao_cliente"][[
        "linha_excel", "valor_original", "data_interpretada",
    ]].rename(columns={
        "valor_original": "aquisicao_original",
        "data_interpretada": "data_aquisicao_interpretada",
    })
    eventos = datas_por_campo[campo].merge(
        referencias, on="linha_excel", how="left", validate="many_to_one", sort=False,
    )
    if eventos["data_aquisicao_interpretada"].isna().any():
        raise ValueError("Há eventos sem aquisição conhecida; investigue a referência temporal.")
    anteriores = eventos["data_interpretada"].lt(eventos["data_aquisicao_interpretada"])
    return eventos.loc[anteriores].copy()
