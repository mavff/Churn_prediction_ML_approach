import pandas as pd
from matplotlib.figure import Figure

from preparacao_dados.graficos.estilizar_eixo import estilizar_eixo


def desenhar_churn_por_chamados(treino_antes: pd.DataFrame, estilo: dict[str, object]) -> Figure:
    """Mostra a taxa de churn por número de chamados, com a lista vazia antes da regra do zero."""
    churn = treino_antes["churn"].astype(int)
    # Seis ou mais chamados formam um grupo só, porque as contagens altas têm poucos clientes.
    grupos = treino_antes["chamados_suporte"].clip(upper=6).astype("string").replace("6", "6+").fillna("sem lista")
    taxas = churn.groupby(grupos).agg(["mean", "size"])
    ordem = ["sem lista", *sorted((g for g in taxas.index if g != "sem lista"), key=lambda g: int(g.rstrip("+")))]
    taxas = taxas.reindex([g for g in ordem if g in taxas.index])
    figura = Figure(figsize=(9, 5), facecolor=estilo["superficie"], layout="constrained")
    eixo = figura.add_subplot()
    cores = [estilo["destaque"] if g == "sem lista" else estilo["taxa"] for g in taxas.index]
    barras = eixo.bar(range(len(taxas)), 100 * taxas["mean"], width=0.6, color=cores)
    eixo.bar_label(barras, labels=[f"{100 * t:.1f}%".replace(".", ",") for t in taxas["mean"]], padding=3, fontsize=8, color=estilo["tinta"])
    eixo.axhline(100 * churn.mean(), color=estilo["neutro"], linewidth=1)
    eixo.text(len(taxas) - 0.5, 100 * churn.mean() + 1, f"média do treino {100 * churn.mean():.1f}%".replace(".", ","),
              ha="right", fontsize=8, color=estilo["secundaria"])
    eixo.set_xticks(range(len(taxas)), [f"{g}\nn = {n}" for g, n in zip(taxas.index, taxas["size"])])
    eixo.set_ylim(0, 100 * taxas["mean"].max() * 1.2)
    if {"sem lista", "1"} <= set(taxas.index):
        titulo = (f"Sem lista de chamados, o churn é {100 * taxas.loc['sem lista', 'mean']:.1f}%; "
                  f"com 1 chamado, {100 * taxas.loc['1', 'mean']:.1f}%").replace(".", ",")
    else:
        titulo = "Taxa de churn por número de chamados no treino"
    estilizar_eixo(eixo, estilo, titulo, rotulo_x="Chamados nos 90 dias (antes da imputação)", rotulo_y="Churn (%)")
    return figura
