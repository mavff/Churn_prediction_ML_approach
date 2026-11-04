from pathlib import Path

import pandas as pd

from preparacao_dados.exportar_relatorio_excel import exportar_relatorio_excel


def exportar_base_excel(
    dados: pd.DataFrame,
    caminho_saida: Path,
    habilitado: bool = True,
) -> None:
    """Exporta a base; permite desligar saídas intermediárias sem mudar o fluxo."""
    if habilitado:
        exportar_relatorio_excel(
            abas={"base_tratada": dados},
            caminho_relatorio=caminho_saida,
            substituir_arquivo=True,
        )
