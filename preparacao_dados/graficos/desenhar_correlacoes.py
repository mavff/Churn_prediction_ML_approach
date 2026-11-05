import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def desenhar_correlacoes(treino: pd.DataFrame, estilo: dict[str, object]) -> Figure:
    """Desenha a matriz de Pearson entre numéricos, binários e o alvo, com escala divergente centrada em zero."""
    numericos = [c for c, r in definir_dicionario_dados().items() if r["tipo"] in {"Int64", "Float64"}]
    matriz = treino[numericos].astype(float).assign(churn=treino["churn"].astype(float)).corr()
    figura = Figure(figsize=(7.5, 6.2), facecolor=estilo["superficie"], layout="constrained")
    eixo = figura.add_subplot()
    escala = LinearSegmentedColormap.from_list("divergente", estilo["divergente"])
    imagem = eixo.imshow(matriz.to_numpy(), cmap=escala, vmin=-1, vmax=1)
    for i in range(len(matriz)):
        for j in range(len(matriz)):
            valor = matriz.iloc[i, j]
            texto = f"{valor:.2f}".replace(".", ",").replace("-0,00", "0,00")
            eixo.text(j, i, texto, ha="center", va="center", fontsize=8, color="#ffffff" if abs(valor) > 0.6 else estilo["tinta"])
    eixo.set_xticks(range(len(matriz)), matriz.columns, rotation=45, ha="right", fontsize=8, color=estilo["secundaria"])
    eixo.set_yticks(range(len(matriz)), matriz.index, fontsize=8, color=estilo["secundaria"])
    eixo.tick_params(length=0)
    for borda in eixo.spines.values():
        borda.set_visible(False)
    eixo.set_title(f"Correlação de Pearson no treino (n = {len(treino):,})".replace(",", "."), loc="left", fontsize=11, color=estilo["tinta"])
    barra = figura.colorbar(imagem, ax=eixo, shrink=0.8)
    barra.ax.tick_params(labelsize=8, colors=estilo["secundaria"])
    barra.outline.set_visible(False)
    return figura
