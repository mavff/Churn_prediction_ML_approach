from pathlib import Path
from typing import Mapping

import pandas as pd


def salvar_resultados_excel(
    caminho_arquivo: Path,
    tabelas: Mapping[str, pd.DataFrame],
) -> Path:
    """Salva as tabelas recebidas em abas de um arquivo Excel."""

    caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(
        caminho_arquivo,
        engine="openpyxl",
    ) as arquivo_excel:
        for nome_aba, tabela in tabelas.items():
            tabela.to_excel(
                arquivo_excel,
                sheet_name=nome_aba,
                index=False,
            )

    return caminho_arquivo