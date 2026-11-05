from pathlib import Path

import pandas as pd

from preparacao_dados.exportar_base_excel import exportar_base_excel
from preparacao_dados.exportar_graficos_aed import exportar_graficos_aed
from preparacao_dados.exportar_relatorio_excel import exportar_relatorio_excel
from preparacao_dados.limpar_pasta_saidas import limpar_pasta_saidas
from preparacao_dados.montar_abas_relatorio import montar_abas_relatorio
from preparacao_dados.montar_tabelas_etapa import montar_tabelas_etapa


def exportar_resultados(
    conjuntos: dict[str, dict[str, object]],
    resultados: dict[str, dict[str, object]],
    protocolo_temporal: dict[str, object],
    protocolos: dict[str, dict[str, object]],
    pasta_projeto: Path,
    caminho_origem: Path,
    salvar_etapas: bool = True,
) -> None:
    """Recria dados/tratados com as etapas e as bases finais e exporta o relatório e os gráficos da AED."""
    tratados = pasta_projeto / "dados" / "tratados"
    # Saídas de execuções anteriores são apagadas: a pasta mostra só o fluxo desta execução.
    limpar_pasta_saidas(tratados, caminho_origem)
    ordenados = dict(sorted(resultados.items()))
    # Uma etapa por arquivo, com o mesmo número e nome da aba do relatório.
    if salvar_etapas:
        for problema, resultado in ordenados.items():
            if "saida" in resultado:
                exportar_relatorio_excel(montar_tabelas_etapa(resultado["saida"]), tratados / "etapas" / f"{problema}.xlsx", substituir_arquivo=True)
    # Base tratada legível: todos os clientes, com conjunto, preditores selecionados, alvo e metadados.
    tabelas = {}
    for nome, partes in conjuntos.items():
        metadados = partes["metadados"]
        tabelas[nome] = pd.concat([
            metadados[["id_cliente"]].assign(conjunto=nome), partes["X"], partes["y"], metadados.drop(columns="id_cliente"),
        ], axis=1)
    exportar_base_excel(pd.concat(tabelas.values()).sort_index(), tratados / "base_churn_tratada.xlsx")
    # Uma base de modelagem por escala, acompanhada da descrição das colunas aprendida no treino.
    colunas = resultados["14_codificacao"]["evidencias"]
    for escala in conjuntos["treino"]["modelagem"]:
        abas = {nome: partes["modelagem"][escala] for nome, partes in conjuntos.items()}
        abas["colunas"] = colunas.loc[colunas["escala"].eq(escala)].drop(columns="escala")
        exportar_relatorio_excel(abas, tratados / f"base_churn_modelagem_{escala}.xlsx", substituir_arquivo=True)
    protocolo = {
        **protocolo_temporal,
        "isolamento_avaliacao": "Clientes separados antes da qualidade; EDA e parâmetros aprendidos somente no treino",
        **{f"{prefixo}_{nome}": valor for prefixo, itens in protocolos.items() for nome, valor in itens.items()},
    }
    abas = montar_abas_relatorio(ordenados, protocolo)
    exportar_relatorio_excel(abas, pasta_projeto / "relatorios" / "diagnostico_preparacao.xlsx", substituir_arquivo=True)
    # O treino legível traz também os campos retirados do X, para que a AED mostre todos os preditores.
    exportar_graficos_aed(tabelas["treino"], pasta_projeto / "relatorios" / "graficos")
    for nome, partes in conjuntos.items():
        modelagem = next(iter(partes["modelagem"].values())).shape[1] - 2
        print(f"{nome.capitalize()}: {len(partes['X'])} clientes | {partes['X'].shape[1]} preditores | {modelagem} colunas de modelagem")
