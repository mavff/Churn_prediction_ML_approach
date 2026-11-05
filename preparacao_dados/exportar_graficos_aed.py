from pathlib import Path

import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.graficos import (
    definir_estilo_graficos, desenhar_funil_registros, desenhar_ausencias, desenhar_churn_por_chamados,
    desenhar_distribuicoes, desenhar_violinos, desenhar_kde, desenhar_correlacoes, desenhar_mensalidade_por_fibra,
    desenhar_ranking_associacao, desenhar_churn_por_categoria, desenhar_churn_tempo_contrato, desenhar_mapa_tempo_chamados,
)
from preparacao_dados.limpar_pasta_saidas import limpar_pasta_saidas


def exportar_graficos_aed(
    treino: pd.DataFrame,
    resultados: dict[str, dict[str, object]],
    protocolos: dict[str, dict[str, object]],
    pasta_graficos: Path,
    caminho_origem: Path,
) -> None:
    """Recria a pasta de gráficos da AED, numerados na ordem de leitura, sem alterar nenhum dado."""
    preditores = [campo for campo, regra in definir_dicionario_dados().items() if regra["tipo"] != "alvo"]
    if treino[[*preditores, "churn"]].isna().any().any():
        raise ValueError("Os gráficos da AED exigem o treino imputado e com alvo.")
    estilo = definir_estilo_graficos()
    # Gráficos de versões anteriores saem; a pasta mostra só os desta execução.
    limpar_pasta_saidas(pasta_graficos, caminho_origem)
    # Funil e ausências usam a auditoria dos três conjuntos; os demais, só o treino.
    antes_imputacao = resultados["10_numericos"]["saida"]
    figuras = {
        "01_funil_registros": desenhar_funil_registros(resultados, estilo),
        "02_ausencias": desenhar_ausencias(antes_imputacao, protocolos["imputacao"]["limiar_alerta_ausencia"], estilo),
        "03_churn_por_chamados": desenhar_churn_por_chamados(antes_imputacao["treino"], estilo),
        "04_distribuicoes": desenhar_distribuicoes(treino, estilo),
        "05_violinos": desenhar_violinos(treino, estilo),
        "06_kde": desenhar_kde(treino, estilo),
        "07_correlacoes": desenhar_correlacoes(treino, estilo),
        "08_mensalidade_por_fibra": desenhar_mensalidade_por_fibra(treino, estilo),
        "09_ranking_associacao": desenhar_ranking_associacao(
            resultados["12_atributos"]["evidencias"], treino, protocolos["atributos"]["limiar_irrelevancia"], estilo,
        ),
        "10_churn_por_categoria": desenhar_churn_por_categoria(treino, estilo),
        "11_churn_tempo_contrato": desenhar_churn_tempo_contrato(treino, estilo),
        "12_mapa_tempo_chamados": desenhar_mapa_tempo_chamados(treino, estilo),
    }
    for nome, figura in figuras.items():
        figura.savefig(pasta_graficos / f"{nome}.png", **estilo["salvar"])
