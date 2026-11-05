def retirar_atributos_irrelevantes(partes: dict[str, object], protocolo: dict[str, object]) -> dict[str, object]:
    """Tira do X os campos aprovados e os preserva nos metadados para o benchmark futuro."""
    X = partes["X"]
    retirados = [campo for campo in X.columns if protocolo[f"selecao_{campo}"] == "retirar"]
    if set(retirados) & set(partes["metadados"].columns):
        raise ValueError("Os atributos a retirar já aparecem nos metadados.")
    # A coluna muda de papel, não de valor: a base exportada continua completa.
    return {
        **partes,
        "X": X.drop(columns=retirados),
        "metadados": partes["metadados"].join(X[retirados]),
    }
