from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def definir_protocolo_imputacao(estrategias: dict[str, str] | None = None) -> dict[str, object]:
    """Define a estratégia de cada preditor; medianas e modas serão aprendidas somente no treino."""
    if estrategias is None:
        estrategias = {
            "tempo_cliente_meses": "mediana",
            "mensalidade_rs": "mediana",
            # Lista vazia significa nenhum chamado registrado na janela, como na consolidação da Aula 1, p. 12.
            "chamados_suporte": "zero",
            "atrasos_6m": "mediana",
            "tipo_contrato": "moda",
            "forma_pagamento": "moda",
            "fibra_optica": "moda",
            "debito_automatico": "moda",
        }
    preditores = [campo for campo, regra in definir_dicionario_dados().items() if regra["tipo"] != "alvo"]
    if set(estrategias) != set(preditores) or not set(estrategias.values()) <= {"mediana", "moda", "zero"}:
        raise ValueError("Defina mediana, moda ou zero para cada um dos oito preditores do dicionário.")
    return {
        **{f"estrategia_{campo}": estrategias[campo] for campo in preditores},
        # Contrato de dados da Aula 2, p. 11: ausência acima do limiar no lote gera alerta e imputação.
        "limiar_alerta_ausencia": 0.20,
        "ajuste": "Somente no treino; validação, teste e novos dados recebem apenas transform",
        "referencia": "Aula 2, pp. 9 e 16; Aula 3, p. 4; chamados sem lista como zero conforme Aula 1, p. 12",
    }
