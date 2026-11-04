import pandas as pd


def apresentar_estrutura_base(dados: pd.DataFrame) -> None:
    """Apresenta as dimensões e os nomes das colunas da base."""
    print("Quantidade de registros:", dados.shape[0])
    print("Quantidade de colunas:", dados.shape[1])

    print("\nColunas:")
    for nome_coluna in dados.columns:
        print(f"- {nome_coluna}")