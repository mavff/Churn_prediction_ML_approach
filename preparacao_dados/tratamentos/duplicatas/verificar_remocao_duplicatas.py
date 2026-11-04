import pandas as pd


def verificar_remocao_duplicatas(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    ocorrencias: pd.DataFrame,
) -> dict[str, object]:
    """Confirma a remoção das cópias previstas e a preservação dos demais dados."""
    indices = ocorrencias["linha_excel_removida"].astype(int) - 2
    if not depois.equals(antes.drop(index=indices)):
        raise ValueError("Os registros mantidos diferem das linhas da fonte.")
    if depois.duplicated().any():
        raise ValueError("Ainda há cópias integrais após o tratamento.")
    if set(antes["id_cliente"].dropna()) != set(depois["id_cliente"].dropna()):
        raise ValueError("A deduplicação alterou o conjunto de clientes.")
    resumo = pd.DataFrame([
        ("Registros", len(antes), len(depois)),
        ("Identificadores distintos", antes["id_cliente"].nunique(), depois["id_cliente"].nunique()),
        ("Cópias integrais excedentes", len(ocorrencias), 0),
        ("Registros sem identificador", int(antes["id_cliente"].astype("string").str.strip().fillna("").eq("").sum()), int(depois["id_cliente"].astype("string").str.strip().fillna("").eq("").sum())),
    ], columns=["indicador", "antes", "depois"])
    return {
        "resumo": resumo,
        "evidencias": ocorrencias.copy(),
        "regra": "Manter a primeira ocorrência e remover apenas cópias integrais",
        "decisao": "Aplicado; valores e identificadores dos registros mantidos preservados",
    }
