import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.graficos.estilizar_eixo import estilizar_eixo


def desenhar_distribuicoes(treino: pd.DataFrame, estilo: dict[str, object]) -> Figure:
    """Compara, por classe de churn, os histogramas das contagens e dos valores contínuos do treino."""
    dicionario = definir_dicionario_dados()
    continuos = [c for c, r in dicionario.items() if r["tipo"] in {"Int64", "Float64"} and r["maximo"] > 1]
    y = treino["churn"].astype(int)
    figura = Figure(figsize=(9, 6.5), facecolor=estilo["superficie"], layout="constrained")
    for eixo, campo in zip(figura.subplots(2, 2).flat, continuos):
        valores = treino[campo].astype(float)
        # Contagens usam um intervalo por valor inteiro; a mensalidade usa 20 faixas iguais.
        if dicionario[campo]["tipo"] == "Int64":
            limites = np.arange(valores.min() - 0.5, valores.max() + 1.5)
        else:
            limites = np.linspace(valores.min(), valores.max(), 21)
        for classe, (rotulo, cor) in estilo["classes"].items():
            eixo.hist(valores[y.eq(classe)], bins=limites, density=True, histtype="step", linewidth=2, color=cor, label=rotulo)
        estilizar_eixo(eixo, estilo, campo, rotulo_y="Densidade")
    figura.legend(*eixo.get_legend_handles_labels(), loc="outside upper right", frameon=False, fontsize=9)
    figura.suptitle(f"Histogramas no treino por classe de churn (n = {len(treino):,})".replace(",", "."),
                    x=0.01, ha="left", fontsize=11, color=estilo["tinta"])
    return figura
