from preparacao_dados.diagnosticos.atributos import descrever_atributos_treino, identificar_relevancia_redundancia_ruido
from preparacao_dados.tratamentos.atributos import retirar_atributos_irrelevantes, verificar_selecao_atributos


def selecionar_atributos(
    preparados: dict[str, dict[str, object]],
    protocolo: dict[str, object],
) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    """Explora o treino imputado e retira dos três conjuntos os atributos aprovados como irrelevantes."""
    treino = preparados["treino"]
    # A AED usa somente o treino; validação e teste apenas recebem a mesma retirada.
    avaliacao = identificar_relevancia_redundancia_ruido(
        treino["X"], treino["y"], protocolo["limiar_irrelevancia"], protocolo["limiar_redundancia"],
    )
    selecionados = {nome: retirar_atributos_irrelevantes(partes, protocolo) for nome, partes in preparados.items()}
    return selecionados, {
        "12_atributos": {**verificar_selecao_atributos(preparados, selecionados, avaliacao, protocolo), "saida": selecionados},
        "13_descritiva": descrever_atributos_treino(treino["X"], treino["y"]),
    }
