from pathlib import Path

import pandas as pd

from preparacao_dados.exportar_base_excel import exportar_base_excel
from preparacao_dados.exportar_relatorio_excel import exportar_relatorio_excel
from preparacao_dados.montar_abas_relatorio import montar_abas_relatorio


def exportar_resultados(
    conjuntos: dict[str, dict[str, object]],
    resultados: dict[str, dict[str, object]],
    protocolo_temporal: dict[str, object],
    protocolo_divisao: dict[str, object],
    pasta_projeto: Path,
    salvar_conjuntos: bool = True,
    salvar_base_completa: bool = True,
) -> None:
    """Exporta a base, os conjuntos opcionais e o relatório consolidado da execução."""
    tabelas = {}
    for nome, partes in conjuntos.items():
        tabela = pd.concat([partes["X"], partes["y"], partes["metadados"]], axis=1)
        tabelas[nome] = tabela[partes["ordem_colunas"]].sort_index()
    base = pd.concat(tabelas.values()).sort_index()
    tratados = pasta_projeto / "dados" / "tratados"
    exportar_base_excel(base, tratados / "base_churn_com_dicionario_tratado.xlsx", salvar_base_completa)
    if salvar_conjuntos:
        exportar_relatorio_excel(tabelas, tratados / "conjuntos_churn.xlsx", substituir_arquivo=True)
    protocolo = {
        **protocolo_temporal,
        "isolamento_avaliacao": "Clientes separados antes da qualidade; EDA e parâmetros aprendidos somente no treino",
        **{f"divisao_{nome}": valor for nome, valor in protocolo_divisao.items()},
    }
    ordenados = dict(sorted(resultados.items()))
    abas = montar_abas_relatorio(ordenados, protocolo)
    exportar_relatorio_excel(abas, pasta_projeto / "relatorios" / "diagnostico_preparacao.xlsx", substituir_arquivo=True)
    for nome, partes in conjuntos.items():
        print(f"{nome.capitalize()}: {len(partes['X'])} clientes | {partes['X'].shape[1]} atributos")
