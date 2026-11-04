from pathlib import Path

import pandas as pd

from preparacao_dados.exportar_base_excel import exportar_base_excel
from preparacao_dados.exportar_relatorio_excel import exportar_relatorio_excel
from preparacao_dados.tratamentos.identificar_duplicatas_excedentes import (
    identificar_duplicatas_excedentes,
)
from preparacao_dados.tratamentos.remover_duplicatas_integrais import (
    remover_duplicatas_integrais,
)
from preparacao_dados.tratamentos.verificar_remocao_duplicatas import (
    verificar_remocao_duplicatas,
)


def preparar_base_sem_duplicatas(
    dados: pd.DataFrame,
    caminho_origem: Path,
    caminho_saida: Path,
    caminho_relatorio: Path,
) -> pd.DataFrame:
    """Coordena a deduplicação, sua verificação e suas saídas."""
    auditoria = identificar_duplicatas_excedentes(dados, caminho_origem)
    dados_tratados = remover_duplicatas_integrais(dados)
    indicadores = verificar_remocao_duplicatas(dados, dados_tratados)

    exportar_base_excel(dados_tratados, caminho_saida)

    exportar_relatorio_excel(
        abas={
            "T01_indicadores": indicadores,
            "T01_registros_removidos": auditoria,
        },
        caminho_relatorio=caminho_relatorio,
    )

    return dados_tratados