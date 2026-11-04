from datetime import date, timedelta


def definir_protocolo_temporal(
    data_corte: date = date(2026, 9, 21),
    fim_acompanhamento: date = date(2026, 11, 21),
    cobertura_completa: bool = True,
) -> dict[str, object]:
    """Centraliza as convenções didáticas aprovadas, sem aprender parâmetros."""
    if fim_acompanhamento < data_corte or not isinstance(cobertura_completa, bool):
        raise ValueError("Confira as datas do protocolo e a convenção de cobertura.")
    return {
        "data_corte": data_corte,
        "inicio_janela_chamados": data_corte - timedelta(days=89),
        "inicio_janela_alvo": data_corte + timedelta(days=1),
        "fim_janela_alvo": data_corte + timedelta(days=60),
        "fim_acompanhamento": fim_acompanhamento,
        "historico_minimo_dias": 60,
        "cobertura_completa": cobertura_completa,
        "origem_cobertura": "Hipótese didática aprovada; cobertura real não comprovada pela fonte",
        "unidade_analise": "Um registro de cliente no final do dia de corte",
        "isolamento_avaliacao": "Pendente antes da EDA e das transformações aprendidas",
    }
