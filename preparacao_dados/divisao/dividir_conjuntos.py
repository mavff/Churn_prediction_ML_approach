from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from preparacao_dados.divisao.verificar_divisao import verificar_divisao
from preparacao_dados.validar_estrutura_visao import validar_estrutura_visao


def dividir_conjuntos(
    visao: pd.DataFrame,
    protocolo: dict[str, object],
    caminho_origem: Path,
) -> tuple[dict[str, pd.DataFrame], dict[str, object]]:
    """Divide a visão antes dos tratamentos de qualidade e verifica o isolamento."""
    validar_estrutura_visao(visao)
    if visao["id_cliente"].duplicated().any() or set(visao["churn"].unique()) != {0, 1}:
        raise ValueError("A divisão exige uma linha por cliente e ambas as classes de churn.")
    if visao["data_corte"].isna().any() or visao["data_corte"].nunique() != 1:
        raise ValueError("Este protocolo exige uma única fotografia temporal.")
    # Ordenar pela chave torna a atribuição estável mesmo se a ordem das linhas mudar.
    ordenada = visao.sort_values("id_cliente", kind="stable")
    try:
        treino, reserva = train_test_split(
            ordenada, train_size=protocolo["proporcao_treino"],
            stratify=ordenada["churn"], random_state=protocolo["random_state"],
        )
        fracao_teste = protocolo["proporcao_teste"] / (protocolo["proporcao_validacao"] + protocolo["proporcao_teste"])
        validacao, teste = train_test_split(
            reserva, test_size=fracao_teste,
            stratify=reserva["churn"], random_state=protocolo["random_state"],
        )
    except ValueError as erro:
        raise ValueError("Não foi possível estratificar três conjuntos; confira o tamanho das classes e as proporções.") from erro
    conjuntos = {nome: tabela.sort_index().copy() for nome, tabela in (
        ("treino", treino), ("validacao", validacao), ("teste", teste),
    )}
    return conjuntos, verificar_divisao(visao, conjuntos, protocolo, caminho_origem)
