import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure


def desenhar_mapa_tempo_chamados(treino: pd.DataFrame, estilo: dict[str, object], minimo: int = 30) -> Figure:
    """Cruza faixas de tempo de casa e de chamados para mostrar onde o churn se concentra."""
    faixas = estilo["faixas_tempo"]
    y = treino["churn"].astype(int)
    tempo = pd.cut(treino["tempo_cliente_meses"].astype(float), bins=faixas["limites"], labels=faixas["rotulos"], right=False)
    chamados = pd.cut(treino["chamados_suporte"].astype(float), bins=[-0.5, 0.5, 1.5, 2.5, 3.5, np.inf], labels=["0", "1", "2", "3", "4+"])
    tabela = y.groupby([tempo, chamados], observed=False).agg(["mean", "size"])
    taxa = tabela["mean"].unstack().mul(100)
    quantidade = tabela["size"].unstack()
    figura = Figure(figsize=(8, 5), facecolor=estilo["superficie"], layout="constrained")
    eixo = figura.add_subplot()
    escala = LinearSegmentedColormap.from_list("sequencial", estilo["sequencial"]).with_extremes(bad=estilo["faixa"])
    # Células com poucos clientes ficam em cinza: uma taxa ali seria instável.
    imagem = eixo.imshow(taxa.where(quantidade >= minimo).to_numpy(dtype=float), cmap=escala, vmin=0, vmax=100, aspect="auto")
    for i in range(taxa.shape[0]):
        for j in range(taxa.shape[1]):
            n = int(quantidade.iat[i, j])
            if n >= minimo:
                texto, cor = f"{taxa.iat[i, j]:.0f}%\nn = {n}", "#ffffff" if taxa.iat[i, j] > 55 else estilo["tinta"]
            else:
                texto, cor = f"n = {n}", estilo["secundaria"]
            eixo.text(j, i, texto, ha="center", va="center", fontsize=8, color=cor)
    eixo.set_xticks(range(taxa.shape[1]), taxa.columns)
    eixo.set_yticks(range(taxa.shape[0]), taxa.index)
    eixo.set_xlabel("Chamados nos 90 dias", fontsize=8, color=estilo["secundaria"])
    eixo.set_ylabel("Tempo de casa (meses)", fontsize=8, color=estilo["secundaria"])
    eixo.tick_params(length=0, labelsize=8, colors=estilo["secundaria"])
    for borda in eixo.spines.values():
        borda.set_visible(False)
    eixo.set_title(f"Churn por tempo de casa e chamados no treino (cinza: menos de {minimo} clientes)",
                   loc="left", fontsize=10, color=estilo["tinta"])
    barra = figura.colorbar(imagem, ax=eixo, shrink=0.8, label="Churn (%)")
    barra.ax.tick_params(labelsize=8, colors=estilo["secundaria"])
    barra.outline.set_visible(False)
    return figura
