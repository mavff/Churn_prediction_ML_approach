import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.graficos.estilizar_eixo import estilizar_eixo


def desenhar_churn_por_categoria(treino: pd.DataFrame, estilo: dict[str, object]) -> Figure:
    """Compara a taxa de churn de cada categoria e indicador binário com a média do treino."""
    dicionario = definir_dicionario_dados()
    discretos = [c for c, r in dicionario.items() if r["tipo"] == "categoria" or (r["tipo"] == "Int64" and r["maximo"] == 1)]
    y = treino["churn"].astype(int)
    media = 100 * y.mean()
    figura = Figure(figsize=(9, 6.5), facecolor=estilo["superficie"], layout="constrained")
    for eixo, campo in zip(figura.subplots(2, 2).flat, discretos):
        regra = dicionario[campo]
        categorias = list(regra["de_para"].values()) if regra["tipo"] == "categoria" else sorted(treino[campo].unique())
        grupos = [treino[campo].eq(categoria) for categoria in categorias]
        taxas = [100 * y[grupo].mean() if grupo.any() else np.nan for grupo in grupos]
        barras = eixo.bar([str(c) for c in categorias], np.nan_to_num(taxas), width=0.6, color=estilo["taxa"])
        rotulos = ["sem clientes" if np.isnan(t) else f"{t:.1f}%".replace(".", ",") for t in taxas]
        eixo.bar_label(barras, labels=rotulos, padding=3, fontsize=8, color=estilo["tinta"])
        eixo.axhline(media, color=estilo["neutro"], linewidth=1)
        eixo.set_ylim(0, max(np.nanmax(taxas + [media]), 1) * 1.25)
        estilizar_eixo(eixo, estilo, campo, rotulo_y="Churn (%)")
    media_texto = f"{media:.1f}%".replace(".", ",")
    figura.suptitle(f"Taxa de churn por categoria no treino (linha cinza: média de {media_texto})",
                    x=0.01, ha="left", fontsize=11, color=estilo["tinta"])
    return figura
