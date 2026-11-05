import pandas as pd


def montar_tabelas_etapa(saida: pd.DataFrame | dict[str, object]) -> dict[str, pd.DataFrame]:
    """Converte a saída de uma etapa em abas: base única, conjuntos ou bases de modelagem."""
    if isinstance(saida, pd.DataFrame):
        return {"base": saida}
    tabelas = {}
    for nome, parte in saida.items():
        # Depois da separação, preditores, alvo e metadados aparecem lado a lado, nessa ordem.
        if isinstance(parte, pd.DataFrame):
            tabelas[nome] = parte
        else:
            tabelas[nome] = pd.concat([parte["X"], parte["y"], parte["metadados"]], axis=1)
    return tabelas
