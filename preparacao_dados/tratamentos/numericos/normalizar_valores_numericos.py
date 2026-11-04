import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def normalizar_valores_numericos(
    dados: pd.DataFrame,
    avaliacoes: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Aplica os tipos e ausências identificados, sem modificar alvo ou identificadores."""
    esperados = {campo for campo, regra in definir_dicionario_dados().items() if regra["tipo"] in {"Int64", "Float64"}}
    if set(avaliacoes) != esperados:
        raise ValueError("A avaliação deve conter exatamente os preditores numéricos do dicionário.")
    tratados = dados.copy()
    for campo, tabela in avaliacoes.items():
        if not dados.index.equals(tabela.index) or not dados["id_cliente"].equals(tabela["id_cliente"]):
            raise ValueError("A avaliação numérica não corresponde aos clientes da entrada.")
        # Impede aplicar a avaliação se a célula tiver mudado depois da identificação.
        if not dados[campo].astype(object).equals(tabela["valor_antes"].astype(object)):
            raise ValueError("O valor numérico mudou depois da identificação.")
        tratados[campo] = tabela["valor_depois"].copy()
    return tratados
