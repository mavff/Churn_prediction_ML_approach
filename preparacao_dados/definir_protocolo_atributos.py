from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def definir_protocolo_atributos(decisoes: dict[str, str] | None = None) -> dict[str, object]:
    """Registra as decisões aprovadas de relevância, redundância e ruído, sem aprender parâmetros."""
    preditores = [campo for campo, regra in definir_dicionario_dados().items() if regra["tipo"] != "alvo"]
    if decisoes is None:
        # forma_pagamento não se relaciona com churn no treino; sai do X e permanece na base para o benchmark.
        decisoes = {campo: "retirar" if campo == "forma_pagamento" else "manter" for campo in preditores}
    if set(decisoes) != set(preditores) or not set(decisoes.values()) <= {"manter", "retirar"} or "manter" not in decisoes.values():
        raise ValueError("Defina manter ou retirar para cada preditor do dicionário, mantendo ao menos um.")
    return {
        **{f"selecao_{campo}": decisoes[campo] for campo in preditores},
        "limiar_irrelevancia": 0.05,
        "limiar_redundancia": 0.8,
        "decisao_redundancia": "mensalidade_rs e fibra_optica mantidas; redundância registrada para a modelagem",
        "decisao_ruido": "extremos plausíveis dentro do dicionário mantidos e documentados; só outliers comprovados seriam removidos",
        "fora_do_X": "id_cliente, datas de aquisição, cancelamento e corte e controles de auditoria permanecem como metadados",
        "referencia": "Aula 2, pp. 10 e 17; o benchmark com todas as variáveis fica para a modelagem",
    }
