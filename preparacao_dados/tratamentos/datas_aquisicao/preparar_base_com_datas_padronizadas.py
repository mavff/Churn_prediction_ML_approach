from pathlib import Path

import pandas as pd

from preparacao_dados.exportar_base_excel import exportar_base_excel
from preparacao_dados.exportar_relatorio_excel import exportar_relatorio_excel
from preparacao_dados.tratamentos.datas_aquisicao.padronizar_datas_aquisicao import (
    padronizar_datas_aquisicao,
)
from preparacao_dados.tratamentos.datas_aquisicao.verificar_padronizacao_datas_aquisicao import (
    verificar_padronizacao_datas_aquisicao,
)


def preparar_base_com_datas_padronizadas(
    dados: pd.DataFrame,
    caminho_origem: Path,
    caminho_saida: Path,
    caminho_relatorio: Path,
) -> pd.DataFrame:
    """Coordena a padronização das aquisições, sua verificação e exportação."""
    tratados = padronizar_datas_aquisicao(dados)
    abas = verificar_padronizacao_datas_aquisicao(dados, tratados, caminho_origem)

    exportar_base_excel(tratados, caminho_saida)
    exportar_relatorio_excel(abas=abas, caminho_relatorio=caminho_relatorio)

    return tratados
