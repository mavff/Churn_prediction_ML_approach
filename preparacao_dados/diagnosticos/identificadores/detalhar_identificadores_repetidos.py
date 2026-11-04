import pandas as pd


def detalhar_identificadores_repetidos(
    dados: pd.DataFrame,
) -> pd.DataFrame:
    """Detalha repetições na base original, na ordem de leitura do Excel."""
    identificadores = dados["id_cliente"]

    ausentes = (
        identificadores.isna()
        | identificadores.astype("string").str.strip().eq("").fillna(False)
    )

    repetidos = ~ausentes & identificadores.duplicated(keep=False)

    evidencias = dados.loc[repetidos].copy()
    evidencias.insert(0, "linha_excel", evidencias.index + 2)

    evidencias["registro_integral_repetido"] = (
        dados.duplicated(keep=False).loc[repetidos]
    )

    return evidencias