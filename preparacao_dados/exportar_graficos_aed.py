from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def exportar_graficos_aed(treino: pd.DataFrame, pasta_graficos: Path) -> None:
    """Salva os gráficos da AED do treino: correlações, distribuições por churn e churn por categoria."""
    dicionario = definir_dicionario_dados()
    preditores = [campo for campo, regra in dicionario.items() if regra["tipo"] != "alvo"]
    if treino[[*preditores, "churn"]].isna().any().any():
        raise ValueError("Os gráficos da AED exigem o treino imputado e com alvo.")
    pasta_graficos.mkdir(parents=True, exist_ok=True)
    y = treino["churn"].astype(int)
    numericos = [campo for campo in preditores if dicionario[campo]["tipo"] != "categoria"]
    continuos = [campo for campo in numericos if dicionario[campo]["maximo"] > 1]
    discretos = [campo for campo in preditores if campo not in continuos]
    # Cores da paleta validada; o PNG sem metadados de software mantém a saída reproduzível.
    superficie, tinta, secundaria, grade, eixo_cor = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7"
    classes = {0: ("Permaneceu (churn = 0)", "#2a78d6"), 1: ("Cancelou (churn = 1)", "#eb6834")}
    salvar = {"dpi": 150, "facecolor": superficie, "metadata": {"Software": None}}
    clientes = f"{len(treino):,}".replace(",", ".")

    # 1. Correlação de Pearson entre numéricos, binários e o alvo, com escala divergente centrada em zero.
    matriz = treino[numericos].astype(float).assign(churn=y).corr()
    figura = Figure(figsize=(7.5, 6.2), facecolor=superficie, layout="constrained")
    eixo = figura.add_subplot()
    escala = LinearSegmentedColormap.from_list("divergente", ["#256abf", "#f0efec", "#e34948"])
    imagem = eixo.imshow(matriz.to_numpy(), cmap=escala, vmin=-1, vmax=1)
    for i in range(len(matriz)):
        for j in range(len(matriz)):
            valor = matriz.iloc[i, j]
            texto = f"{valor:.2f}".replace(".", ",").replace("-0,00", "0,00")
            eixo.text(j, i, texto, ha="center", va="center", fontsize=8, color="#ffffff" if abs(valor) > 0.6 else tinta)
    eixo.set_xticks(range(len(matriz)), matriz.columns, rotation=45, ha="right", fontsize=8, color=secundaria)
    eixo.set_yticks(range(len(matriz)), matriz.index, fontsize=8, color=secundaria)
    eixo.tick_params(length=0)
    for borda in eixo.spines.values():
        borda.set_visible(False)
    eixo.set_title(f"Correlação de Pearson no treino (n = {clientes})", loc="left", fontsize=11, color=tinta)
    barra = figura.colorbar(imagem, ax=eixo, shrink=0.8)
    barra.ax.tick_params(labelsize=8, colors=secundaria)
    barra.outline.set_visible(False)
    figura.savefig(pasta_graficos / "correlacoes.png", **salvar)

    # 2. Distribuição de contagens e valores contínuos, separada pela classe de churn.
    figura = Figure(figsize=(9, 6.5), facecolor=superficie, layout="constrained")
    for eixo, campo in zip(figura.subplots(2, 2).flat, continuos):
        valores = treino[campo].astype(float)
        # Contagens usam um intervalo por valor inteiro; a mensalidade usa 20 faixas iguais.
        if dicionario[campo]["tipo"] == "Int64":
            limites = np.arange(valores.min() - 0.5, valores.max() + 1.5)
        else:
            limites = np.linspace(valores.min(), valores.max(), 21)
        for classe, (rotulo, cor) in classes.items():
            eixo.hist(valores[y.eq(classe)], bins=limites, density=True, histtype="step", linewidth=2, color=cor, label=rotulo)
        eixo.set_facecolor(superficie)
        eixo.set_title(campo, loc="left", fontsize=10, color=tinta)
        eixo.set_ylabel("Densidade", fontsize=8, color=secundaria)
        eixo.tick_params(labelsize=8, colors=secundaria)
        eixo.grid(axis="y", color=grade, linewidth=0.8)
        eixo.set_axisbelow(True)
        eixo.spines[["top", "right"]].set_visible(False)
        eixo.spines[["left", "bottom"]].set_color(eixo_cor)
    figura.legend(*eixo.get_legend_handles_labels(), loc="outside upper right", frameon=False, fontsize=9)
    figura.suptitle(f"Distribuição no treino por classe de churn (n = {clientes})", x=0.01, ha="left", fontsize=11, color=tinta)
    figura.savefig(pasta_graficos / "distribuicoes.png", **salvar)

    # 3. Taxa de churn por categoria e indicador binário, comparada à média do treino.
    media = 100 * y.mean()
    figura = Figure(figsize=(9, 6.5), facecolor=superficie, layout="constrained")
    for eixo, campo in zip(figura.subplots(2, 2).flat, discretos):
        regra = dicionario[campo]
        categorias = list(regra["de_para"].values()) if regra["tipo"] == "categoria" else sorted(treino[campo].unique())
        grupos = [treino[campo].eq(categoria) for categoria in categorias]
        taxas = [100 * y[grupo].mean() if grupo.any() else np.nan for grupo in grupos]
        barras = eixo.bar([str(c) for c in categorias], np.nan_to_num(taxas), width=0.6, color=classes[0][1])
        rotulos = ["sem clientes" if np.isnan(t) else f"{t:.1f}%".replace(".", ",") for t in taxas]
        eixo.bar_label(barras, labels=rotulos, padding=3, fontsize=8, color=tinta)
        eixo.axhline(media, color="#898781", linewidth=1)
        eixo.set_ylim(0, max(np.nanmax(taxas + [media]), 1) * 1.25)
        eixo.set_facecolor(superficie)
        eixo.set_title(campo, loc="left", fontsize=10, color=tinta)
        eixo.set_ylabel("Churn (%)", fontsize=8, color=secundaria)
        eixo.tick_params(labelsize=8, colors=secundaria)
        eixo.grid(axis="y", color=grade, linewidth=0.8)
        eixo.set_axisbelow(True)
        eixo.spines[["top", "right"]].set_visible(False)
        eixo.spines[["left", "bottom"]].set_color(eixo_cor)
    media_texto = f"{media:.1f}%".replace(".", ",")
    figura.suptitle(f"Taxa de churn por categoria no treino (linha cinza: média de {media_texto})", x=0.01, ha="left", fontsize=11, color=tinta)
    figura.savefig(pasta_graficos / "churn_por_categoria.png", **salvar)
