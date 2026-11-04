import pandas as pd


def diagnosticar_identificadores(dados: pd.DataFrame) -> pd.DataFrame:
    """Quantifica ausências e repetições dos identificadores da fonte."""
    identificadores = dados["id_cliente"]

    ausentes = (
        identificadores.isna()
        | identificadores.astype("string").str.strip().eq("").fillna(False)
    )

    identificadores_validos = identificadores.loc[~ausentes]
    repetidos = identificadores_validos.duplicated(keep=False)

    return pd.DataFrame(
        [
            ("Registros na fonte", len(dados)),
            ("Registros sem identificador", int(ausentes.sum())),
            ("Identificadores distintos preenchidos",
             identificadores_validos.nunique()),
            ("Identificadores com mais de um registro",
             identificadores_validos.loc[repetidos].nunique()),
            ("Registros associados a identificadores repetidos",
             int(repetidos.sum())),
        ],
        columns=["indicador", "quantidade"],
    )