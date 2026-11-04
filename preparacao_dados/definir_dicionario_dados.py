def definir_dicionario_dados() -> dict[str, dict[str, object]]:
    """Define tipos e domínios fixos da Aula 2, página 3, sem aprender parâmetros."""
    return {
        "tempo_cliente_meses": {"tipo": "Int64", "minimo": 0, "maximo": 120, "obrigatorio": True},
        "mensalidade_rs": {"tipo": "Float64", "minimo": 10, "maximo": 500, "obrigatorio": False},
        "chamados_suporte": {"tipo": "Int64", "minimo": 0, "maximo": 50, "obrigatorio": True},
        "atrasos_6m": {"tipo": "Int64", "minimo": 0, "maximo": 6, "obrigatorio": True},
        "tipo_contrato": {
            "tipo": "categoria", "obrigatorio": True,
            "de_para": {"mensal": "Mensal", "anual": "Anual", "bienal": "Bienal"},
        },
        "forma_pagamento": {
            "tipo": "categoria", "obrigatorio": True,
            "de_para": {"boleto": "Boleto", "cartao": "Cartão", "pix": "Pix"},
        },
        "fibra_optica": {"tipo": "Int64", "minimo": 0, "maximo": 1, "obrigatorio": True},
        "debito_automatico": {"tipo": "Int64", "minimo": 0, "maximo": 1, "obrigatorio": True},
        # O alvo tem papel separado: é validado e nunca participa da correção dos preditores.
        "churn": {"tipo": "alvo", "minimo": 0, "maximo": 1, "obrigatorio": True},
    }
