from pathlib import Path

import pandas as pd


def identificar_duplicatas_excedentes(
    dados: pd.DataFrame,
    caminho_origem: Path,
) -> pd.DataFrame:
    """Rastreia cópias integrais na base original, com índices preservados."""
    colunas_fonte = dados.columns.tolist()
    repetidos = dados.duplicated(keep="first")

    referencias = dados.copy()
    referencias.insert(0, "linha_excel", dados.index + 2)

    mantidos = referencias.loc[~repetidos].rename(
        columns={"linha_excel": "linha_excel_mantida"}
    )
    removidos = referencias.loc[repetidos].rename(
        columns={"linha_excel": "linha_excel_removida"}
    )

    auditoria = removidos.merge(
        mantidos,
        on=colunas_fonte,
        how="left",
        validate="many_to_one",
        sort=False,
    )

    if (
        len(auditoria) != int(repetidos.sum())
        or auditoria["linha_excel_mantida"].isna().any()
    ):
        raise ValueError("Não foi possível rastrear todas as cópias integrais.")

    auditoria.insert(0, "arquivo_origem", caminho_origem.name)

    return auditoria[
        [
            "arquivo_origem",
            "linha_excel_removida",
            "linha_excel_mantida",
            *colunas_fonte,
        ]
    ]