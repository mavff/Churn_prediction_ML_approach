from math import ceil
from pathlib import Path

from openpyxl.styles import Alignment

import pandas as pd


def exportar_relatorio_excel(
    abas: dict[str, pd.DataFrame],
    caminho_relatorio: Path,
    substituir_arquivo: bool = False,
) -> None:
    """Exporta as abas; pode reconstruir o relatório completo para retirar abas obsoletas."""
    caminho_relatorio.parent.mkdir(parents=True, exist_ok=True)

    opcoes = {"engine": "openpyxl", "mode": "w"}

    # No fluxo completo, reconstruir o arquivo impede o acúmulo de abas de versões anteriores.
    if caminho_relatorio.exists() and not substituir_arquivo:
        opcoes.update(mode="a", if_sheet_exists="replace")

    with pd.ExcelWriter(caminho_relatorio, **opcoes) as arquivo:
        for nome_aba, tabela in abas.items():
            tabela.to_excel(
                arquivo,
                sheet_name=nome_aba,
                index=False,
                freeze_panes=(1, 0),
            )

            planilha = arquivo.sheets[nome_aba]
            planilha.auto_filter.ref = planilha.dimensions

            for coluna in planilha.columns:
                largura = max(
                    len(str(celula.value)) if celula.value is not None else 0
                    for celula in coluna
                )
                letra = coluna[0].column_letter
                planilha.column_dimensions[letra].width = min(largura + 2, 50)

            # Ajusta a altura para que listas e justificativas possam ser lidas com quebra de texto.
            for linha in planilha.iter_rows():
                altura = 1
                for celula in linha:
                    celula.alignment = Alignment(vertical="top", wrap_text=True)
                    largura = planilha.column_dimensions[celula.column_letter].width
                    altura = max(altura, ceil(len(str(celula.value or "")) / max(largura - 2, 1)))
                planilha.row_dimensions[linha[0].row].height = 15 * altura
