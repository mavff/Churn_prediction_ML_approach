import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from scipy.stats import gaussian_kde

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.graficos.estilizar_eixo import estilizar_eixo


def desenhar_kde(treino: pd.DataFrame, estilo: dict[str, object]) -> Figure:
    """Desenha a densidade estimada (KDE) das contagens e dos valores contínuos para cada classe de churn."""
    dicionario = definir_dicionario_dados()
    continuos = [c for c, r in dicionario.items() if r["tipo"] in {"Int64", "Float64"} and r["maximo"] > 1]
    y = treino["churn"].astype(int)
    figura = Figure(figsize=(9, 6.5), facecolor=estilo["superficie"], layout="constrained")
    for eixo, campo in zip(figura.subplots(2, 2).flat, continuos):
        valores = treino[campo].astype(float)
        # A curva fica dentro da faixa observada, sem inventar valores negativos nas pontas.
        pontos = np.linspace(valores.min(), valores.max(), 300)
        for classe, (rotulo, cor) in estilo["classes"].items():
            amostra = valores[y.eq(classe)]
            if amostra.nunique() < 2:
                continue
            densidade = gaussian_kde(amostra)(pontos)
            eixo.fill_between(pontos, densidade, color=cor, alpha=0.15)
            eixo.plot(pontos, densidade, color=cor, linewidth=2, label=rotulo)
        estilizar_eixo(eixo, estilo, campo, rotulo_y="Densidade")
    figura.legend(*eixo.get_legend_handles_labels(), loc="outside upper right", frameon=False, fontsize=9)
    figura.suptitle("Densidade (KDE) por classe de churn no treino", x=0.01, ha="left", fontsize=11, color=estilo["tinta"])
    return figura
