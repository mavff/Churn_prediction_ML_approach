from pathlib import Path

import pandas as pd

from preparacao_dados.exportar_base_excel import exportar_base_excel
from preparacao_dados.exportar_relatorio_excel import exportar_relatorio_excel
from preparacao_dados.tratamentos.chamados.filtrar_chamados_anteriores_aquisicao import (
    filtrar_chamados_anteriores_aquisicao,
)
from preparacao_dados.tratamentos.chamados.verificar_filtragem_chamados import (
    verificar_filtragem_chamados,
)


def preparar_base_com_chamados_consistentes(
    dados: pd.DataFrame,
    diagnostico_entrada: dict[str, pd.DataFrame],
    caminho_origem: Path,
    caminho_saida: Path,
    caminho_relatorio: Path,
) -> pd.DataFrame:
    """Coordena a filtragem dos chamados já diagnosticados e sua auditoria."""
    evidencias = diagnostico_entrada["02_inconsistencias_temporais"]
    casos = evidencias.loc[evidencias["campo"].eq("data_chamado")]
    tratados = filtrar_chamados_anteriores_aquisicao(dados, casos)
    abas = verificar_filtragem_chamados(dados, tratados, diagnostico_entrada, caminho_origem)

    exportar_base_excel(tratados, caminho_saida)
    exportar_relatorio_excel(abas=abas, caminho_relatorio=caminho_relatorio)
    return tratados
