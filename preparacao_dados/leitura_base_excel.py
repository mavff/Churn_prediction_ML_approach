from pathlib import Path

import pandas as pd


def carregar_base_excel(caminho_base: Path) -> pd.DataFrame:
    """Lê uma planilha com uma única aba e retorna seus dados."""

    if not caminho_base.is_file():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho_base}"
        )

    with pd.ExcelFile(caminho_base, engine="openpyxl") as arquivo:
        abas = arquivo.sheet_names

        if len(abas) != 1:
            raise ValueError(
                f"Esperávamos uma única aba, mas encontramos: {abas}. "
                "É necessário escolher qual aba será utilizada."
            )

        dados = pd.read_excel(
            arquivo,
            sheet_name=abas[0],
            dtype=object,
            keep_default_na=False,
        )

    return dados