from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def definir_protocolo_codificacao() -> dict[str, object]:
    """Define como cada preditor entra nas bases de modelagem; os parâmetros são aprendidos só no treino."""
    dicionario = definir_dicionario_dados()
    codificacoes = {}
    for campo, regra in dicionario.items():
        if regra["tipo"] == "alvo":
            continue
        # Categorias viram uma coluna 0/1 por categoria; contagens e contínuos são escalados; binários ficam iguais.
        if regra["tipo"] == "categoria":
            codificacoes[campo] = "one_hot"
        else:
            codificacoes[campo] = "escalar" if regra["maximo"] > 1 else "manter"
    return {
        **{f"codificacao_{campo}": valor for campo, valor in codificacoes.items()},
        "escala_padronizada": "StandardScaler: média e desvio aprendidos no treino",
        "escala_minmax": "MinMaxScaler: mínimo e máximo aprendidos no treino; o treino fica em [0, 1]",
        "one_hot": "Uma coluna 0/1 por categoria do dicionário; categoria desconhecida vira zeros (handle_unknown='ignore')",
        "ajuste": "Somente no treino; validação, teste e novos dados recebem apenas transform",
        "referencia": "Aula 3, pp. 3 e 4",
    }
