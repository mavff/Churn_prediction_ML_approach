import pandas as pd


def verificar_remocao_duplicatas(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
) -> pd.DataFrame:
    """Verifica a deduplicação e produz os indicadores antes/depois."""
    copias_antes = int(antes.duplicated().sum())
    copias_depois = int(depois.duplicated().sum())

    if not depois.columns.equals(antes.columns):
        raise ValueError("O tratamento alterou as colunas da base.")

    if copias_depois or len(depois) != len(antes) - copias_antes:
        raise ValueError("A quantidade de registros após a remoção é incorreta.")

    ids_antes = set(antes["id_cliente"].dropna())
    ids_depois = set(depois["id_cliente"].dropna())

    if ids_antes != ids_depois:
        raise ValueError("O tratamento alterou o conjunto de identificadores.")

    conteudo_preservado = (
        depois.index.isin(antes.index).all()
        and depois.equals(antes.loc[depois.index])
    )

    if not conteudo_preservado:
        raise ValueError("Os registros mantidos diferem das linhas da fonte.")

    return pd.DataFrame(
        [
            ("Registros", len(antes), len(depois)),
            ("Identificadores distintos", len(ids_antes), len(ids_depois)),
            ("Cópias integrais excedentes", copias_antes, copias_depois),
        ],
        columns=["indicador", "antes", "depois"],
    )