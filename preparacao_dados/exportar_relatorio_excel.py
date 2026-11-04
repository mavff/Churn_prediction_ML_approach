from pathlib import Path

import pandas as pd


def exportar_relatorio_excel(
    abas: dict[str, pd.DataFrame],
    caminho_relatorio: Path,
) -> None:
    """Atualiza as abas informadas, preservando as demais do relatório."""
    caminho_relatorio.parent.mkdir(parents=True, exist_ok=True)

    opcoes = {"engine": "openpyxl", "mode": "w"}

    if caminho_relatorio.exists():
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
                planilha.column_dimensions[letra].width = min(largura + 2, 70)