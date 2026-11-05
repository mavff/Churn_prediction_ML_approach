def definir_estilo_graficos() -> dict[str, object]:
    """Centraliza cores validadas, rótulos, faixas de leitura e opções de gravação dos gráficos da AED."""
    return {
        "superficie": "#fcfcfb", "tinta": "#0b0b0b", "secundaria": "#52514e",
        "neutro": "#898781", "grade": "#e1e0d9", "eixo": "#c3c2b7", "faixa": "#f0efec",
        # Azul para quem permaneceu e laranja para quem cancelou, em todos os gráficos por classe.
        "classes": {0: ("Permaneceu (churn = 0)", "#2a78d6"), 1: ("Cancelou (churn = 1)", "#eb6834")},
        "taxa": "#2a78d6",
        "destaque": "#1baf7a",
        # Conjuntos sem laranja, para não confundir com a classe; cada barra leva seu valor escrito.
        "conjuntos": {"treino": "#2a78d6", "validacao": "#1baf7a", "teste": "#e87ba4"},
        "rotulos_conjuntos": {"treino": "Treino", "validacao": "Validação", "teste": "Teste"},
        # Contratos têm ordem de duração; por isso uma rampa de um só tom, do mensal ao bienal.
        "ordinal": ["#86b6ef", "#2a78d6", "#104281"],
        "sequencial": ["#cde2fb", "#6da7ec", "#256abf", "#0d366b"],
        "divergente": ["#256abf", "#f0efec", "#e34948"],
        "faixas_tempo": {"limites": [0, 12, 24, 48, 121], "rotulos": ["menos de 12", "12 a 23", "24 a 47", "48 ou mais"]},
        "salvar": {"dpi": 150, "facecolor": "#fcfcfb", "metadata": {"Software": None}},
    }
