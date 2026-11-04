from pathlib import Path

import pandas as pd


def verificar_contagem_chamados(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    avaliacao: pd.DataFrame,
    caminho_origem: Path,
) -> dict[str, object]:
    """Confere a contagem, os ausentes e a preservação de clientes e demais campos."""
    colunas = ["chamados_suporte" if c == "data_chamado" else c for c in antes.columns]
    if not antes.index.equals(depois.index) or list(depois.columns) != colunas:
        raise ValueError("A contagem alterou os clientes ou o esquema indevidamente.")
    if not antes.drop(columns="data_chamado").equals(depois.drop(columns="chamados_suporte")):
        raise ValueError("A contagem alterou outros campos, inclusive o alvo.")
    quantidade = depois["chamados_suporte"]
    if quantidade.dtype != pd.Int64Dtype() or quantidade.dropna().lt(0).any():
        raise ValueError("Chamados devem ser inteiros não negativos ou ausentes.")
    if not quantidade.equals(avaliacao["chamados_suporte"]):
        raise ValueError("A contagem exportada difere da identificação.")
    # Impede que a conversão trate uma lista vazia como ausência comprovada de chamados.
    vazios = antes["data_chamado"].astype("string").str.strip().fillna("").eq("")
    if not quantidade.isna().eq(vazios).all():
        raise ValueError("As listas vazias devem continuar ausentes antes da imputação.")
    conhecidos = quantidade.notna()
    if not quantidade.loc[conhecidos].equals(avaliacao.loc[conhecidos, "datas_validas_observadas_90d"]):
        raise ValueError("A quantidade não corresponde aos eventos válidos observados.")
    auditoria = avaliacao.copy()
    auditoria.insert(0, "linha_excel", antes.index + 2)
    auditoria.insert(0, "arquivo_origem", caminho_origem.name)
    resumo = pd.DataFrame([
        ("Registros", len(antes), len(depois)),
        ("Contagens numéricas disponíveis", 0, int(conhecidos.sum())),
        ("Campos sem contagem disponível", int(vazios.sum()), int(quantidade.isna().sum())),
        ("Campos vazios após exclusão de datas", int((vazios & antes["chamados_excluidos_por_cronologia"].gt(0)).sum()), int((quantidade.isna() & depois["chamados_excluidos_por_cronologia"].gt(0)).sum())),
        ("Eventos válidos registrados na janela", int(avaliacao["datas_validas_observadas_90d"].sum()), int(quantidade.sum())),
    ], columns=["indicador", "antes", "depois"])
    return {
        "resumo": resumo, "evidencias": auditoria,
        "regra": "Contar datas válidas nos 90 dias até o corte; cada ocorrência corresponde a um chamado registrado",
        "decisao": "Listas vazias permanecem ausentes; imputação por mediana ou moda será ajustada somente no treino",
    }
