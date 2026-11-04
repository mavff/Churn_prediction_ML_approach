from pathlib import Path

import pandas as pd


def verificar_padronizacao_datas_aquisicao(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    ocorrencias: pd.DataFrame,
    aquisicoes: pd.DataFrame,
    caminho_origem: Path,
) -> dict[str, object]:
    """Confere o de-para e preserva os demais campos sem repetir a interpretação."""
    campo = "data_aquisicao_cliente"
    if not antes.index.equals(depois.index) or not antes.columns.equals(depois.columns):
        raise ValueError("A padronização alterou linhas, índices ou colunas.")
    if not antes.drop(columns=campo).equals(depois.drop(columns=campo)):
        raise ValueError("A padronização alterou outro campo.")
    esperado = aquisicoes["data_interpretada"].dt.strftime("%d/%m/%Y").reindex(antes.index)
    if esperado.isna().any() or not depois[campo].astype("string").eq(esperado).all():
        raise ValueError("A padronização mudou uma data ou deixou aquisição sem referência.")
    alterados = antes[campo].astype("string").ne(depois[campo].astype("string")).fillna(False)
    indices = ocorrencias["linha_excel"].astype(int) - 2
    if set(antes.index[alterados]) != set(indices):
        raise ValueError("Foram modificadas aquisições diferentes das identificadas.")
    auditoria = pd.DataFrame({
        "arquivo_origem": caminho_origem.name,
        "linha_excel": indices + 2,
        "id_cliente": antes.loc[indices, "id_cliente"].to_numpy(),
        "valor_antes": antes.loc[indices, campo].to_numpy(),
        "valor_depois": depois.loc[indices, campo].to_numpy(),
    })
    resumo = pd.DataFrame([
        ("Registros", len(antes), len(depois)),
        ("Aquisições fora do padrão", len(ocorrencias), 0),
        ("Células padronizadas", 0, int(alterados.sum())),
    ], columns=["indicador", "antes", "depois"])
    return {
        "resumo": resumo, "evidencias": auditoria,
        "regra": "Representar aquisições válidas em DD/MM/AAAA, preservando a data",
        "decisao": "De-para aplicado; aquisições ausentes ou inválidas interrompem a etapa",
    }
