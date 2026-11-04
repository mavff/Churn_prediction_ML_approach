from math import isclose, isfinite


def definir_protocolo_divisao(
    treino: float = 0.50,
    validacao: float = 0.25,
    teste: float = 0.25,
    random_state: int = 42,
) -> dict[str, object]:
    """Define a opção 50/25/25 da Aula 3, p. 5, com estratificação e semente fixa."""
    proporcoes = (treino, validacao, teste)
    if not all(isfinite(p) and 0 < p < 1 for p in proporcoes) or not isclose(sum(proporcoes), 1.0):
        raise ValueError("As três proporções devem ser positivas e somar 1.")
    if not isinstance(random_state, int) or isinstance(random_state, bool):
        raise ValueError("random_state deve ser um inteiro.")
    return {
        "proporcao_treino": treino,
        "proporcao_validacao": validacao,
        "proporcao_teste": teste,
        "random_state": random_state,
        "estratificacao": "churn; usado somente para a divisão",
        "unidade_divisao": "id_cliente; sem compartilhamento entre conjuntos",
        "tipo_avaliacao": "Clientes da mesma fotografia; não é avaliação fora do tempo",
        "referencia": "Aula 3, pp. 4–5; proporção 50/25/25 e semente 42 aprovadas",
    }
