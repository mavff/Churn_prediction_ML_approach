from pathlib import Path

import pandas as pd


def verificar_padronizacao_datas_aquisicao(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    caminho_origem: Path,
) -> dict[str, pd.DataFrame]:
    """Verifica o de-para das aquisições e registra somente as células alteradas."""
    campo = "data_aquisicao_cliente"
    if not antes.index.equals(depois.index) or not antes.columns.equals(depois.columns):
        raise ValueError("A padronização alterou linhas, índices ou colunas.")
    if not antes.drop(columns=campo).equals(depois.drop(columns=campo)):
        raise ValueError("A padronização alterou dados fora da data de aquisição.")

    originais = antes[campo].astype("string")
    padronizados = depois[campo].astype("string")
    datas_antes = pd.to_datetime(
        originais, format="%d/%m/%Y", errors="coerce"
    ).fillna(pd.to_datetime(originais, format="%Y-%m-%d", errors="coerce"))

    if datas_antes.isna().any():
        raise ValueError("Há aquisições ausentes ou não interpretáveis; investigar antes.")
    esperado = datas_antes.dt.strftime("%d/%m/%Y").astype("string")
    if not padronizados.equals(esperado):
        raise ValueError("O tratamento mudou uma data ou não produziu DD/MM/AAAA.")

    alterados = originais.ne(padronizados).fillna(False)
    auditoria = pd.DataFrame({
        "arquivo_origem": caminho_origem.name,
        "linha_excel": antes.index[alterados] + 2,
        "id_cliente": antes.loc[alterados, "id_cliente"],
        "campo": campo,
        "valor_antes": antes.loc[alterados, campo],
        "valor_depois": depois.loc[alterados, campo],
    })
    indicadores = pd.DataFrame([
        ("Registros", len(antes), len(depois)),
        ("Identificadores distintos", antes["id_cliente"].nunique(),
         depois["id_cliente"].nunique()),
        ("Aquisições em formato ISO",
         int(originais.str.fullmatch(r"\d{4}-\d{2}-\d{2}", na=False).sum()),
         int(padronizados.str.fullmatch(r"\d{4}-\d{2}-\d{2}", na=False).sum())),
        ("Células alteradas", 0, int(alterados.sum())),
    ], columns=["indicador", "antes", "depois"])

    return {
        "T02_indicadores": indicadores,
        "T02_alteracoes_datas": auditoria,
    }
