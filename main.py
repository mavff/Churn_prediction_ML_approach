from pathlib import Path

from preparacao_dados.apresentar_estrutura_base import apresentar_estrutura_base
from preparacao_dados.leitura_dados import ler_base_excel
from preparacao_dados.diagnosticos.registrar_diagnostico_identificadores import (
    registrar_diagnostico_identificadores,
)
from preparacao_dados.tratamentos.preparar_base_sem_duplicatas import (
    preparar_base_sem_duplicatas,
)


def main() -> None:
    pasta_projeto = Path(__file__).resolve().parent

    caminho_base = (
        pasta_projeto / "dados" / "base_churn_5000_VF2_aluno.xlsx"
    )
    caminho_relatorio = (
        pasta_projeto / "relatorios" / "diagnostico_preparacao.xlsx"
    )
    caminho_base_tratada = (
        pasta_projeto
        / "dados"
        / "tratados"
        / "01_base_churn_sem_duplicatas.xlsx"
    )

    dados = ler_base_excel(caminho_base)
    registrar_diagnostico_identificadores(dados, caminho_relatorio)

    dados_tratados = preparar_base_sem_duplicatas(
        dados=dados,
        caminho_origem=caminho_base,
        caminho_saida=caminho_base_tratada,
        caminho_relatorio=caminho_relatorio,
    )

    apresentar_estrutura_base(dados_tratados)


if __name__ == "__main__":
    main()