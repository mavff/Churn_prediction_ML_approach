from pathlib import Path

from preparacao_dados.apresentar_estrutura_base import apresentar_estrutura_base
from preparacao_dados.diagnosticos.datas.diagnosticar_datas import diagnosticar_datas
from preparacao_dados.diagnosticos.identificadores.registrar_diagnostico_identificadores import (
    registrar_diagnostico_identificadores,
)
from preparacao_dados.exportar_relatorio_excel import exportar_relatorio_excel
from preparacao_dados.leitura_dados import ler_base_excel
from preparacao_dados.tratamentos.duplicatas.preparar_base_sem_duplicatas import (
    preparar_base_sem_duplicatas,
)
from preparacao_dados.tratamentos.datas_aquisicao.preparar_base_com_datas_padronizadas import (
    preparar_base_com_datas_padronizadas,
)
from preparacao_dados.tratamentos.chamados.preparar_base_com_chamados_consistentes import (
    preparar_base_com_chamados_consistentes,
)
from preparacao_dados.tratamentos.cancelamentos.preparar_base_com_cancelamentos_sinalizados import (
    preparar_base_com_cancelamentos_sinalizados,
)


def main() -> None:
    pasta_projeto = Path(__file__).resolve().parent
    caminho_base = pasta_projeto / "dados" / "base_churn_5000_VF2_aluno.xlsx"
    caminho_relatorio = pasta_projeto / "relatorios" / "diagnostico_preparacao.xlsx"
    caminho_base_tratada = (
        pasta_projeto / "dados" / "tratados" / "01_base_churn_sem_duplicatas.xlsx"
    )
    caminho_datas_padronizadas = (
        pasta_projeto / "dados" / "tratados" / "02_base_churn_datas_padronizadas.xlsx"
    )
    caminho_chamados_filtrados = (
        pasta_projeto / "dados" / "tratados" / "03_base_churn_chamados_filtrados.xlsx"
    )
    caminho_cancelamentos_sinalizados = (
        pasta_projeto / "dados" / "tratados" / "04_base_churn_cancelamentos_sinalizados.xlsx"
    )

    dados = ler_base_excel(caminho_base)
    registrar_diagnostico_identificadores(dados, caminho_relatorio)
    dados_tratados = preparar_base_sem_duplicatas(
        dados=dados,
        caminho_origem=caminho_base,
        caminho_saida=caminho_base_tratada,
        caminho_relatorio=caminho_relatorio,
    )
    abas_temporais = diagnosticar_datas(dados_tratados)
    exportar_relatorio_excel(abas=abas_temporais, caminho_relatorio=caminho_relatorio)

    dados_tratados = preparar_base_com_datas_padronizadas(
        dados=dados_tratados,
        caminho_origem=caminho_base,
        caminho_saida=caminho_datas_padronizadas,
        caminho_relatorio=caminho_relatorio,
    )
    dados_tratados = preparar_base_com_chamados_consistentes(
        dados=dados_tratados,
        diagnostico_entrada=abas_temporais,
        caminho_origem=caminho_base,
        caminho_saida=caminho_chamados_filtrados,
        caminho_relatorio=caminho_relatorio,
    )
    dados_tratados = preparar_base_com_cancelamentos_sinalizados(
        dados=dados_tratados,
        ocorrencias=abas_temporais["02_inconsistencias_temporais"],
        caminho_origem=caminho_base,
        caminho_saida=caminho_cancelamentos_sinalizados,
        caminho_relatorio=caminho_relatorio,
    )
    apresentar_estrutura_base(dados_tratados)


if __name__ == "__main__":
    main()