import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def validar_estrutura_visao(dados: pd.DataFrame) -> None:
    """Bloqueia colunas ausentes, chaves inválidas e corrupção do alvo da visão."""
    obrigatorias = {*definir_dicionario_dados(), "id_cliente", "data_corte"}
    faltantes = sorted(obrigatorias.difference(dados.columns))
    if faltantes or not dados.columns.is_unique:
        raise ValueError(f"Esquema da visão inválido; colunas ausentes: {faltantes}; confira nomes repetidos.")
    ids = dados["id_cliente"].astype("string")
    if ids.isna().any() or ids.str.strip().eq("").any() or dados.duplicated(["id_cliente", "data_corte"]).any():
        raise ValueError("A visão exige identificador preenchido e uma linha por cliente e corte.")
    if not dados.index.is_unique or not pd.api.types.is_integer_dtype(dados.index.dtype):
        raise ValueError("Preserve os índices inteiros únicos da fonte.")
    # Corrupção do alvo exige investigação; não recebe o tratamento de ausência dos preditores.
    alvo = dados["churn"]
    if not pd.api.types.is_integer_dtype(alvo.dtype) or alvo.isna().any() or not alvo.isin([0, 1]).all():
        raise ValueError("Churn deve ser inteiro em {0, 1}, sem ausências; o alvo não será corrigido ou imputado.")
