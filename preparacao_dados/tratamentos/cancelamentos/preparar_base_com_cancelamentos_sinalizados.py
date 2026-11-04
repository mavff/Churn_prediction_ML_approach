from pathlib import Path

import pandas as pd

from preparacao_dados.exportar_base_excel import exportar_base_excel
from preparacao_dados.exportar_relatorio_excel import exportar_relatorio_excel
from preparacao_dados.tratamentos.cancelamentos.isolar_cancelamentos_inconsistentes import (
    isolar_cancelamentos_inconsistentes,
)
from preparacao_dados.tratamentos.cancelamentos.verificar_isolamento_cancelamentos import (
    verificar_isolamento_cancelamentos,
)


def preparar_base_com_cancelamentos_sinalizados(
    dados: pd.DataFrame,
    ocorrencias: pd.DataFrame,
    caminho_origem: Path,
    caminho_saida: Path,
    caminho_relatorio: Path,
) -> pd.DataFrame:
    """Coordena o isolamento dos cancelamentos e preserva sua auditoria."""
    casos = ocorrencias.loc[ocorrencias["campo"].eq("data_ocorrencia_churn")]
    tratados = isolar_cancelamentos_inconsistentes(dados, casos)
    abas = verificar_isolamento_cancelamentos(dados, tratados, casos, caminho_origem)

    exportar_base_excel(tratados, caminho_saida)
    exportar_relatorio_excel(abas=abas, caminho_relatorio=caminho_relatorio)
    return tratados
