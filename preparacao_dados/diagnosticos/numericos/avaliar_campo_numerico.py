import numpy as np
import pandas as pd

from preparacao_dados.diagnosticos.identificar_ausencias import identificar_ausencias


def avaliar_campo_numerico(valores: pd.Series, regra: dict[str, object]) -> pd.DataFrame:
    """Avalia tipo, integralidade e faixa, sem estimar valores ausentes."""
    ausentes = identificar_ausencias(valores)
    numeros = pd.to_numeric(valores.mask(ausentes, pd.NA), errors="coerce").astype("Float64")
    booleanos = valores.map(type).isin([bool, np.bool_])
    tipo_invalido = numeros.isna() | ~np.isfinite(numeros).fillna(False) | booleanos
    situacao = pd.Series("valido", index=valores.index)
    situacao.loc[tipo_invalido] = "tipo_invalido"
    if regra["tipo"] == "Int64":
        fracionarios = numeros.where(~tipo_invalido).mod(1).ne(0).fillna(False)
        situacao.loc[situacao.eq("valido") & fracionarios] = "nao_inteiro"
    na_faixa = numeros.between(regra["minimo"], regra["maximo"]).fillna(False)
    situacao.loc[situacao.eq("valido") & ~na_faixa] = "fora_faixa"
    # Distingue o vazio de entrada de um valor preenchido que foi considerado inválido.
    situacao.loc[ausentes] = "ausente_na_entrada"
    validos = situacao.eq("valido")
    textos_convertidos = validos & valores.map(type).eq(str)
    situacao.loc[textos_convertidos] = "converter_tipo"
    # Isola os inválidos como ausentes; os tipos pandas escolhidos mantêm essas ausências.
    depois = numeros.where(validos, pd.NA).astype(regra["tipo"])
    return pd.DataFrame({
        "valor_antes": valores,
        "valor_depois": depois,
        "situacao": situacao,
        "regra": f"{regra['tipo']}; faixa inclusiva [{regra['minimo']}, {regra['maximo']}]",
    })
