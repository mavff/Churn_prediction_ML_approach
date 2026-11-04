from pathlib import Path

import pandas as pd

from preparacao_dados.exportar_relatorio_excel import exportar_relatorio_excel


def exportar_base_excel(
    dados: pd.DataFrame,
    caminho_saida: Path,
) -> None:
    """Exporta a base em uma aba identificada."""
    exportar_relatorio_excel(
        abas={"base_tratada": dados},
        caminho_relatorio=caminho_saida,
    )