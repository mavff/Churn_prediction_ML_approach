import pandas as pd
from matplotlib.figure import Figure

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.graficos.estilizar_eixo import estilizar_eixo


def desenhar_violinos(treino: pd.DataFrame, estilo: dict[str, object]) -> Figure:
    """Mostra forma, mediana e quartis das contagens e dos valores contínuos para cada classe de churn."""
    dicionario = definir_dicionario_dados()
    continuos = [c for c, r in dicionario.items() if r["tipo"] in {"Int64", "Float64"} and r["maximo"] > 1]
    y = treino["churn"].astype(int)
    figura = Figure(figsize=(9, 6.5), facecolor=estilo["superficie"], layout="constrained")
    for eixo, campo in zip(figura.subplots(2, 2).flat, continuos):
        grupos = [treino.loc[y.eq(classe), campo].astype(float) for classe in estilo["classes"]]
        corpos = eixo.violinplot(grupos, positions=[0, 1], widths=0.8, showextrema=False)
        for corpo, (_, cor) in zip(corpos["bodies"], estilo["classes"].values()):
            corpo.set_facecolor(cor)
            corpo.set_edgecolor(cor)
            corpo.set_alpha(0.35)
        # A barra escura vai do primeiro ao terceiro quartil; o ponto branco é a mediana.
        for posicao, valores in enumerate(grupos):
            q1, mediana, q3 = valores.quantile([0.25, 0.5, 0.75])
            eixo.vlines(posicao, q1, q3, color=estilo["tinta"], linewidth=4)
            eixo.scatter(posicao, mediana, s=22, color="#ffffff", edgecolors=estilo["tinta"], zorder=3)
            numero = f"{mediana:g}" if float(mediana).is_integer() else f"{mediana:.2f}"
            eixo.text(posicao + 0.1, mediana, f"mediana {numero}".replace(".", ","), va="center", fontsize=8, color=estilo["tinta"])
        eixo.set_xticks([0, 1], ["Permaneceu", "Cancelou"])
        estilizar_eixo(eixo, estilo, campo)
    figura.suptitle("Violino por classe de churn no treino: forma da distribuição, mediana e quartis",
                    x=0.01, ha="left", fontsize=11, color=estilo["tinta"])
    return figura
