from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer


def verificar_imputacao(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    ajuste: ColumnTransformer,
    ids: pd.Series,
    limiar_alerta: float,
    caminho_origem: Path,
) -> dict[str, object]:
    """Confere que só as ausências mudaram, recebendo os valores do treino, e emite alertas de ausência."""
    if not antes.index.equals(depois.index) or not antes.columns.equals(depois.columns) or not antes.dtypes.equals(depois.dtypes):
        raise ValueError("A imputação alterou clientes, colunas ou tipos.")
    if not ids.index.equals(antes.index) or depois.isna().any().any():
        raise ValueError("A imputação deve preencher todas as ausências dos clientes identificados.")
    nomes = {"median": "mediana do treino", "most_frequent": "moda do treino", "constant": "zero por regra"}
    estrategias = {}
    taxas = {}
    aprendidos = []
    indicadores = [("Registros", len(antes), len(depois))]
    for campo in antes.columns:
        imputador = ajuste.named_transformers_[campo]
        valor = imputador.statistics_[0]
        ausentes = antes[campo].isna()
        # Valores observados permanecem idênticos; somente as ausências recebem o valor do treino.
        if not depois.loc[~ausentes, campo].equals(antes.loc[~ausentes, campo]):
            raise ValueError(f"A imputação alterou valores observados: {campo}.")
        if not depois.loc[ausentes, campo].eq(valor).all():
            raise ValueError(f"Ausência preenchida com valor diferente do aprendido no treino: {campo}.")
        estrategias[campo] = nomes[imputador.strategy]
        taxas[campo] = float(ausentes.mean())
        aprendidos.append(f"{campo} = {valor if isinstance(valor, str) else f'{float(valor):g}'}")
        indicadores.append((f"Ausentes — {campo}", int(ausentes.sum()), 0))
        # Somado entre os conjuntos, o indicador conta em quantos lotes o campo passou do limiar.
        indicadores.append((f"Conjuntos com ausência acima de {limiar_alerta:.0%} — {campo}", int(taxas[campo] > limiar_alerta), 0))
    # Uma linha por célula preenchida, com cliente e linha da fonte para rastrear a estimativa.
    posicoes = antes.isna().stack()
    posicoes = posicoes[posicoes].index
    indices = posicoes.get_level_values(0)
    campos = posicoes.get_level_values(1)
    auditoria = pd.DataFrame({
        "arquivo_origem": caminho_origem.name,
        "linha_excel": indices + 2,
        "id_cliente": ids.loc[indices].to_numpy(),
        "campo": campos,
        "valor_antes": pd.NA,
        "valor_depois": [depois.at[indice, campo] for indice, campo in posicoes],
        "estrategia": [estrategias[campo] for campo in campos],
        "taxa_ausencia_campo": [taxas[campo] for campo in campos],
        "alerta_ausencia": [taxas[campo] > limiar_alerta for campo in campos],
    })
    return {
        "resumo": pd.DataFrame(indicadores, columns=["indicador", "antes", "depois"]),
        "evidencias": auditoria,
        "regra": (
            "Ajuste somente no treino (Aula 2, p. 16; Aula 3, p. 4): " + "; ".join(f"{c}: {e}" for c, e in estrategias.items())
            + f"; alerta quando a ausência do campo no conjunto passa de {limiar_alerta:.0%} (Aula 2, p. 11)"
        ),
        "decisao": "Valores aprendidos no treino e aplicados aos três conjuntos, inclusive nos campos com alerta: " + ", ".join(aprendidos),
    }
