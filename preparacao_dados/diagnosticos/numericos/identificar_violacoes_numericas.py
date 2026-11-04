import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.diagnosticos.numericos.avaliar_campo_numerico import avaliar_campo_numerico


def identificar_violacoes_numericas(dados: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Identifica o resultado de cada campo numérico e preserva sua entrada para auditoria."""
    avaliacoes = {}
    for campo, regra in definir_dicionario_dados().items():
        # Categorias têm seu próprio de-para; o alvo fica fora da normalização numérica.
        if regra["tipo"] not in {"Int64", "Float64"}:
            continue
        tabela = avaliar_campo_numerico(dados[campo], regra)
        tabela.insert(0, "id_cliente", dados["id_cliente"])
        tabela.insert(0, "linha_excel", dados.index + 2)
        tabela.insert(2, "campo", campo)
        avaliacoes[campo] = tabela
    return avaliacoes
