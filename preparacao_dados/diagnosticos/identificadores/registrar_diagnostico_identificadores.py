from pathlib import Path

import pandas as pd

from preparacao_dados.diagnosticos.identificadores.diagnosticar_identificadores import (
    diagnosticar_identificadores,
)
from preparacao_dados.diagnosticos.identificadores.detalhar_identificadores_repetidos import (
    detalhar_identificadores_repetidos,
)
from preparacao_dados.exportar_relatorio_excel import exportar_relatorio_excel

from preparacao_dados.diagnosticos.identificadores.montar_conclusoes_identificadores import (
    montar_conclusoes_identificadores,
)

def registrar_diagnostico_identificadores(
    dados: pd.DataFrame,
    caminho_relatorio: Path,
) -> None:
    """Coordena o diagnóstico, as evidências e o registro das conclusões."""
    resumo = diagnosticar_identificadores(dados)
    evidencias = detalhar_identificadores_repetidos(dados)
    conclusoes = montar_conclusoes_identificadores(dados, evidencias)

    abas = {
        "01_diagnostico_identificadores": resumo,
        "01_evidencias_identificadores": evidencias,
        "01_conclusoes_identificadores": conclusoes,
    }

    exportar_relatorio_excel(
        abas=abas,
        caminho_relatorio=caminho_relatorio,
    )