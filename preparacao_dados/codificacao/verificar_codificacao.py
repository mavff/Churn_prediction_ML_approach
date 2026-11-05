import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def verificar_codificacao(
    antes: dict[str, dict[str, object]],
    depois: dict[str, dict[str, object]],
    ajustes: dict[str, ColumnTransformer],
    protocolo: dict[str, object],
) -> dict[str, object]:
    """Confere escala, one-hot e binários nos três conjuntos e descreve cada coluna de modelagem."""
    dicionario = definir_dicionario_dados()
    X_treino = antes["treino"]["X"].astype({campo: float for campo in antes["treino"]["X"].select_dtypes("number")})
    indicadores = [(f"Clientes — {nome}", len(partes["X"]), len(depois[nome]["X"])) for nome, partes in antes.items()]
    indicadores.append(("Preditores selecionados", X_treino.shape[1], X_treino.shape[1]))
    linhas = []
    for escala, ajuste in ajustes.items():
        papeis = {nome: list(colunas) for nome, _, colunas in ajuste.transformers_ if nome != "remainder"}
        escalador = ajuste.named_transformers_["escala"]
        escalados, categoricos, mantidos = papeis["escala"], papeis["one_hot"], papeis["binarios"]
        # Os parâmetros da escala precisam ser exatamente os do treino; outro valor indicaria vazamento.
        if escala == "padronizada":
            aprendidos = np.allclose(escalador.mean_, X_treino[escalados].mean())
        else:
            aprendidos = np.allclose(escalador.data_min_, X_treino[escalados].min()) and np.allclose(escalador.data_max_, X_treino[escalados].max())
        if not aprendidos:
            raise ValueError(f"A escala {escala} não foi ajustada somente no treino.")
        colunas = list(ajuste.get_feature_names_out())
        for nome, partes in depois.items():
            X = antes[nome]["X"]
            tabela = partes["modelagem"][escala]
            # Identificador e alvo ficam nas pontas e precisam continuar alinhados aos preditores.
            if not tabela.index.equals(X.index) or list(tabela.columns) != ["id_cliente", *colunas, "churn"]:
                raise ValueError(f"A base de modelagem {escala} de {nome} tem linhas ou colunas inesperadas.")
            if not tabela["id_cliente"].equals(antes[nome]["metadados"]["id_cliente"]) or not tabela["churn"].equals(antes[nome]["y"]):
                raise ValueError(f"A base de modelagem {escala} de {nome} perdeu o alinhamento com cliente ou alvo.")
            codificado = tabela[colunas]
            if not np.isfinite(codificado.to_numpy(dtype=float)).all():
                raise ValueError(f"Há valores ausentes ou infinitos na base de modelagem {escala} de {nome}.")
            if not np.allclose(codificado[escalados], escalador.transform(X[escalados].astype(float))):
                raise ValueError(f"Os valores escalados de {nome} não usam os parâmetros do treino.")
            for campo in categoricos:
                # Cada cliente tem exatamente um 1 entre as colunas da sua categoria.
                for categoria in dicionario[campo]["de_para"].values():
                    if not codificado[f"{campo}_{categoria}"].eq(X[campo].eq(categoria).astype(float)).all():
                        raise ValueError(f"O one-hot de {campo} não corresponde às categorias em {nome}.")
            if not codificado[mantidos].equals(X[mantidos].astype(float)):
                raise ValueError(f"Os indicadores binários foram alterados em {nome}.")
        treino = depois["treino"]["modelagem"][escala]
        for coluna in colunas:
            origem = next(campo for campo in X_treino.columns if coluna == campo or coluna.startswith(f"{campo}_"))
            posicao = escalados.index(coluna) if coluna in escalados else None
            linhas.append({
                "escala": escala,
                "coluna": coluna,
                "origem": origem,
                "categoria": coluna.removeprefix(f"{origem}_") if origem in categoricos else pd.NA,
                "transformacao": {"escala": {"padronizada": "padronização", "minmax": "min-max"}[escala], "one_hot": "one-hot", "binarios": "binário mantido"}[
                    next(nome for nome, cols in papeis.items() if origem in cols)
                ],
                "media_aprendida": escalador.mean_[posicao] if posicao is not None and escala == "padronizada" else np.nan,
                "desvio_aprendido": escalador.scale_[posicao] if posicao is not None and escala == "padronizada" else np.nan,
                "minimo_aprendido": escalador.data_min_[posicao] if posicao is not None and escala == "minmax" else np.nan,
                "maximo_aprendido": escalador.data_max_[posicao] if posicao is not None and escala == "minmax" else np.nan,
                "media_treino": treino[coluna].mean(),
                "desvio_treino": treino[coluna].std(ddof=0),
                "minimo_treino": treino[coluna].min(),
                "maximo_treino": treino[coluna].max(),
            })
        indicadores.append((f"Colunas de modelagem — {escala}", X_treino.shape[1], len(colunas)))
    indicadores.append(("Ausências após a codificação", 0, 0))
    return {
        "resumo": pd.DataFrame(indicadores, columns=["indicador", "antes", "depois"]),
        "evidencias": pd.DataFrame(linhas),
        "regra": (
            "Ajuste somente no treino (Aula 3, p. 4): StandardScaler ou MinMaxScaler em contagens e valores contínuos; "
            "one-hot com uma coluna por categoria do dicionário e handle_unknown='ignore'; binários mantidos em 0/1"
        ),
        "decisao": f"Uma base de modelagem por escala ({', '.join(ajustes)}), com os preditores selecionados; {protocolo['ajuste']}",
    }
