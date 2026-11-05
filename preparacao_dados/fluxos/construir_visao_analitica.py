from pathlib import Path

import pandas as pd

from preparacao_dados.diagnosticos.datas import (
    interpretar_datas, identificar_aquisicoes_fora_padrao,
    identificar_eventos_anteriores_aquisicao, identificar_elegibilidade_alvo,
    identificar_contagem_chamados, identificar_tempo_cliente_meses,
)
from preparacao_dados.diagnosticos.identificadores import identificar_duplicatas_excedentes
from preparacao_dados.tratamentos.duplicatas import remover_duplicatas_integrais, verificar_remocao_duplicatas
from preparacao_dados.tratamentos.datas_aquisicao import padronizar_datas_aquisicao, verificar_padronizacao_datas_aquisicao
from preparacao_dados.tratamentos.chamados import (
    filtrar_chamados_anteriores_aquisicao, verificar_filtragem_chamados,
    substituir_datas_por_contagem_chamados, verificar_contagem_chamados,
)
from preparacao_dados.tratamentos.cancelamentos import remover_registros_com_cancelamento_inconsistente, verificar_exclusao_cancelamentos_inconsistentes
from preparacao_dados.tratamentos.elegibilidade import construir_base_elegivel_com_alvo, verificar_elegibilidade_alvo
from preparacao_dados.tratamentos.tempo_cliente import adicionar_tempo_cliente_meses, verificar_tempo_cliente_meses


def construir_visao_analitica(
    dados: pd.DataFrame,
    origem: Path,
    protocolo: dict[str, object],
) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    """Constrói a população e os atributos temporais antes de dividir os clientes."""
    # Cada verificação leva a base que a etapa entregou; a exportação grava uma etapa por arquivo.
    resultados = {}
    # 1. Identificar as cópias, removê-las e registrar o resultado.
    copias = identificar_duplicatas_excedentes(dados, origem)
    # Guarda a entrada da etapa; os tratamentos devolvem cópias sem modificá-la.
    antes = dados
    dados = remover_duplicatas_integrais(antes, copias)
    resultados["01_duplicatas"] = {**verificar_remocao_duplicatas(antes, dados, copias), "saida": dados}

    # 2. Interpretar as datas uma vez e aplicar o de-para da aquisição.
    # As datas da fonte serão reutilizadas, considerando depois as exclusões identificadas.
    datas = interpretar_datas(dados)
    aquisicoes = identificar_aquisicoes_fora_padrao(datas["data_aquisicao_cliente"])
    antes = dados
    dados = padronizar_datas_aquisicao(antes, aquisicoes)
    resultados["02_datas"] = {**verificar_padronizacao_datas_aquisicao(
        antes, dados, aquisicoes, datas["data_aquisicao_cliente"], origem,
    ), "saida": dados}

    # 3. Identificar e retirar somente os chamados anteriores à aquisição.
    chamados = identificar_eventos_anteriores_aquisicao(datas, "data_chamado")
    antes = dados
    dados = filtrar_chamados_anteriores_aquisicao(antes, chamados)
    resultados["03_chamados"] = {**verificar_filtragem_chamados(
        antes, dados, chamados, datas["data_chamado"], protocolo, origem,
    ), "saida": dados}

    # 4. Identificar cancelamentos inconsistentes e excluir os registros diretamente.
    cancelamentos = identificar_eventos_anteriores_aquisicao(datas, "data_ocorrencia_churn")
    antes = dados
    dados = remover_registros_com_cancelamento_inconsistente(antes, cancelamentos)
    resultados["04_cancelamentos"] = {**verificar_exclusao_cancelamentos_inconsistentes(
        antes, dados, cancelamentos, origem,
    ), "saida": dados}

    # 5. Identificar quem participa da análise e construir o alvo de 60 dias.
    avaliacao = identificar_elegibilidade_alvo(dados, datas, protocolo)
    antes = dados
    dados = construir_base_elegivel_com_alvo(antes, avaliacao)
    resultados["05_elegibilidade_alvo"] = {**verificar_elegibilidade_alvo(
        antes, dados, avaliacao, datas, protocolo, origem,
    ), "saida": dados}

    # 6. Substituir as listas por quantidade de chamados válidos nos 90 dias históricos.
    contagem = identificar_contagem_chamados(dados, datas["data_chamado"], chamados, protocolo)
    antes = dados
    dados = substituir_datas_por_contagem_chamados(antes, contagem)
    resultados["06_contagem_chamados"] = {**verificar_contagem_chamados(antes, dados, contagem, origem), "saida": dados}

    # 7. Acrescentar o tempo de cliente em meses completos até o corte.
    tempo = identificar_tempo_cliente_meses(dados, datas["data_aquisicao_cliente"], protocolo)
    antes = dados
    dados = adicionar_tempo_cliente_meses(antes, tempo)
    resultados["07_tempo_cliente"] = {**verificar_tempo_cliente_meses(antes, dados, tempo, origem), "saida": dados}
    return dados, resultados
