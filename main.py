from pathlib import Path

from preparacao_dados import (
    apresentar_estrutura_base, definir_protocolo_temporal, exportar_base_excel,
    exportar_relatorio_excel, ler_base_excel, montar_abas_relatorio,
)
from preparacao_dados.diagnosticos.datas import (
    identificar_aquisicoes_fora_padrao, identificar_eventos_anteriores_aquisicao,
    interpretar_datas,
)
from preparacao_dados.diagnosticos.identificadores import identificar_duplicatas_excedentes
from preparacao_dados.tratamentos.cancelamentos import (
    remover_registros_com_cancelamento_inconsistente,
    verificar_exclusao_cancelamentos_inconsistentes,
)
from preparacao_dados.tratamentos.chamados import (
    filtrar_chamados_anteriores_aquisicao, verificar_filtragem_chamados,
)
from preparacao_dados.tratamentos.datas_aquisicao import (
    padronizar_datas_aquisicao, verificar_padronizacao_datas_aquisicao,
)
from preparacao_dados.tratamentos.duplicatas import (
    remover_duplicatas_integrais, verificar_remocao_duplicatas,
)


def main() -> None:
    pasta = Path(__file__).resolve().parent
    origem = pasta / "dados" / "base_churn_5000_VF2_aluno.xlsx"
    tratados = pasta / "dados" / "tratados"
    intermediarios = tratados / "intermediarios"
    salvar_intermediarias = False
    protocolo = definir_protocolo_temporal()
    resultados = {}
    dados = ler_base_excel(origem)

    # 1. Identificar as cópias, removê-las e registrar o resultado.
    copias = identificar_duplicatas_excedentes(dados, origem)
    antes = dados
    dados = remover_duplicatas_integrais(antes, copias)
    resultados["01_duplicatas"] = verificar_remocao_duplicatas(antes, dados, copias)
    exportar_base_excel(dados, intermediarios / "01_sem_duplicatas.xlsx", salvar_intermediarias)

    # 2. Interpretar as datas uma vez e aplicar o de-para da aquisição.
    datas = interpretar_datas(dados)
    aquisicoes = identificar_aquisicoes_fora_padrao(datas["data_aquisicao_cliente"])
    antes = dados
    dados = padronizar_datas_aquisicao(antes, aquisicoes)
    resultados["02_datas"] = verificar_padronizacao_datas_aquisicao(
        antes, dados, aquisicoes, datas["data_aquisicao_cliente"], origem,
    )
    exportar_base_excel(dados, intermediarios / "02_datas_padronizadas.xlsx", salvar_intermediarias)

    # 3. Identificar e retirar somente os chamados anteriores à aquisição.
    chamados = identificar_eventos_anteriores_aquisicao(datas, "data_chamado")
    antes = dados
    dados = filtrar_chamados_anteriores_aquisicao(antes, chamados)
    resultados["03_chamados"] = verificar_filtragem_chamados(
        antes, dados, chamados, datas["data_chamado"], protocolo, origem,
    )
    exportar_base_excel(dados, intermediarios / "03_chamados_consistentes.xlsx", salvar_intermediarias)

    # 4. Identificar cancelamentos inconsistentes e excluir os registros diretamente.
    cancelamentos = identificar_eventos_anteriores_aquisicao(datas, "data_ocorrencia_churn")
    antes = dados
    dados = remover_registros_com_cancelamento_inconsistente(antes, cancelamentos)
    resultados["04_cancelamentos"] = verificar_exclusao_cancelamentos_inconsistentes(
        antes, dados, cancelamentos, origem,
    )

    # Exportar a base atual e o relatório consolidado uma única vez.
    abas = montar_abas_relatorio(resultados, protocolo)
    exportar_base_excel(dados, tratados / "base_churn_sem_cancelamentos_inconsistentes.xlsx")
    exportar_relatorio_excel(abas, pasta / "relatorios" / "diagnostico_preparacao.xlsx", substituir_arquivo=True)
    apresentar_estrutura_base(dados)


if __name__ == "__main__":
    main()
