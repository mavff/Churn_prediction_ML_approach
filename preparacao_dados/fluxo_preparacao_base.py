from pathlib import Path
from typing import Callable

import pandas as pd

from preparacao_dados.auditoria_identificadores import auditar_identificadores
from preparacao_dados.exportacao_resultados_excel import salvar_resultados_excel
from preparacao_dados.auditoria_duplicatas_exatas import identificar_duplicatas_exatas

from preparacao_dados.tratamento_duplicatas_exatas import (
    remover_duplicatas_exatas,
)
def gerar_diagnostico_inicial(
    pasta_projeto: Path,
    leitor_base: Callable[[Path], pd.DataFrame],
) -> Path:
    """Conecta a leitura, a auditoria de IDs e a geração do relatório."""

    caminho_base = (
        pasta_projeto
        / "dados_originais"
        / "base_churn_5000_VF2_aluno.xlsx"
    )

    dados = leitor_base(caminho_base)

    diagnostico = auditar_identificadores(dados)
    duplicatas_exatas = identificar_duplicatas_exatas(dados)

    resumo = pd.DataFrame(
        [
            ("Total de registros", diagnostico.total_registros),
            ("Registros sem ID", diagnostico.registros_sem_id),
            ("IDs distintos preenchidos", diagnostico.ids_distintos),
            ("IDs repetidos", diagnostico.ids_repetidos),
            (
                "Registros envolvidos nas repetições",
                len(diagnostico.registros_com_id_repetido),
            ),
            ("Cópias exatas além da primeira ocorrência", len(duplicatas_exatas)),
            ("Situação da etapa", "Diagnóstico, sem tratamento"),
        ],
        columns=["Verificacao", "Resultado"],
    )

    caminho_relatorio = (
        pasta_projeto
        / "resultados_preparacao"
        / "01_diagnostico_identificadores.xlsx"
    )

    return salvar_resultados_excel(
        caminho_arquivo=caminho_relatorio,
        tabelas={
            "Resumo": resumo,
            "IDs_repetidos": diagnostico.registros_com_id_repetido,
            "Copias_exatas": duplicatas_exatas,
        },
    )