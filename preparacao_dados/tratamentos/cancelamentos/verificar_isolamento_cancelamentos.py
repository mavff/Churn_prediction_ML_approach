from pathlib import Path

import pandas as pd

from preparacao_dados.diagnosticos.datas.diagnosticar_datas import diagnosticar_datas


def verificar_isolamento_cancelamentos(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    ocorrencias: pd.DataFrame,
    caminho_origem: Path,
) -> dict[str, pd.DataFrame]:
    """Verifica o isolamento das datas e a distinção entre vazio e desconhecido."""
    campo = "data_ocorrencia_churn"
    controle = "cancelamento_inconsistente"
    colunas = list(antes.columns) + ([controle] if controle not in antes else [])
    if not antes.index.equals(depois.index) or list(depois.columns) != colunas:
        raise ValueError("O T04 alterou linhas, índices ou colunas indevidamente.")
    if not antes.drop(columns=[campo, controle], errors="ignore").equals(
        depois.drop(columns=[campo, controle])
    ):
        raise ValueError("O T04 alterou outros campos da base.")

    linhas = pd.Series(antes.index + 2, index=antes.index)
    selecionados = linhas.isin(ocorrencias["linha_excel"])
    campo_esperado = antes[campo].copy()
    campo_esperado.loc[selecionados] = ""
    controle_antes = antes.get(controle, pd.Series(False, index=antes.index))
    controle_esperado = controle_antes.copy()
    controle_esperado.loc[selecionados] = True
    if not depois[campo].equals(campo_esperado):
        raise ValueError("Foram alteradas datas diferentes das diagnosticadas.")
    if not depois[controle].eq(controle_esperado).all():
        raise ValueError("A sinalização dos cancelamentos desconhecidos é incorreta.")

    analise_saida = diagnosticar_datas(depois)
    cronologia = analise_saida["02_resumo_cronologia"].set_index("regra")
    if int(cronologia.loc["Cancelamento anterior à aquisição", "ocorrencias"]):
        raise ValueError("Ainda há cancelamentos anteriores à aquisição.")

    alterados = antes[campo].astype("string").ne(depois[campo].astype("string")).fillna(False)
    auditoria = pd.DataFrame({
        "arquivo_origem": caminho_origem.name,
        "linha_excel": antes.index[alterados] + 2,
        "id_cliente": antes.loc[alterados, "id_cliente"],
        "campo": campo,
        "valor_antes": antes.loc[alterados, campo],
        "valor_depois": depois.loc[alterados, campo],
        "cancelamento_inconsistente": depois.loc[alterados, controle],
        "decisao": "Data isolada; desfecho desconhecido",
    })
    vazios_antes = antes[campo].isna() | antes[campo].astype("string").str.strip().eq("").fillna(False)
    vazios_depois = depois[campo].isna() | depois[campo].astype("string").str.strip().eq("").fillna(False)
    indicadores = pd.DataFrame([
        ("Registros", len(antes), len(depois)),
        ("Identificadores distintos", antes["id_cliente"].nunique(), depois["id_cliente"].nunique()),
        ("Cancelamentos anteriores à aquisição", int((selecionados & ~vazios_antes).sum()), 0),
        ("Datas de cancelamento em branco", int(vazios_antes.sum()), int(vazios_depois.sum())),
        ("Cancelamentos marcados como inconsistentes", int(controle_antes.sum()), int(depois[controle].sum())),
        ("Células de cancelamento alteradas", 0, int(alterados.sum())),
    ], columns=["indicador", "antes", "depois"])

    return {"T04_indicadores": indicadores, "T04_cancelamentos_isolados": auditoria}
