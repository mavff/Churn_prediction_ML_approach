import pandas as pd


def interpretar_datas(dados: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Interpreta as datas uma vez, preservando valores e linhas da fonte."""
    if not dados.index.is_unique or not pd.api.types.is_integer_dtype(dados.index.dtype):
        raise ValueError("Preserve os índices inteiros únicos da leitura original.")
    ids = dados["id_cliente"].astype("string")
    if ids.isna().any() or ids.str.strip().eq("").any() or ids.duplicated().any():
        raise ValueError("Resolva identificadores ausentes ou conflitantes antes de construir a fotografia.")
    resultado = {}
    for campo in ("data_aquisicao_cliente", "data_chamado", "data_ocorrencia_churn"):
        valores = dados[campo].astype("string").str.strip()
        presentes = valores.notna() & valores.ne("")
        linhas = dados.loc[presentes, ["id_cliente", campo]].copy()
        linhas.insert(0, "linha_excel", linhas.index + 2)
        linhas = linhas.rename(columns={campo: "valor_original"})
        linhas["valor_data"] = valores.loc[presentes]
        if campo == "data_chamado":
            linhas["valor_data"] = linhas["valor_data"].str.split(",")
            linhas = linhas.explode("valor_data")
        linhas["valor_data"] = linhas["valor_data"].str.strip()
        linhas["data_interpretada"] = pd.to_datetime(
            linhas["valor_data"], format="%d/%m/%Y", errors="coerce"
        ).fillna(pd.to_datetime(linhas["valor_data"], format="%Y-%m-%d", errors="coerce"))
        invalidas = linhas["data_interpretada"].isna()
        if invalidas.any():
            amostra = linhas.loc[invalidas, ["linha_excel", "id_cliente", "valor_data"]]
            raise ValueError(f"Datas não interpretáveis em {campo}: {amostra.head(5).to_dict('records')}")
        resultado[campo] = linhas
    return resultado
