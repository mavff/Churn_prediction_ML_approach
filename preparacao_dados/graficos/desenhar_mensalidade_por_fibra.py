import pandas as pd
from matplotlib.figure import Figure

from preparacao_dados.graficos.estilizar_eixo import estilizar_eixo


def desenhar_mensalidade_por_fibra(treino: pd.DataFrame, estilo: dict[str, object]) -> Figure:
    """Mostra a mensalidade de quem tem e de quem não tem fibra, origem da redundância entre os dois campos."""
    mensalidade = treino["mensalidade_rs"].astype(float)
    fibra = treino["fibra_optica"].astype(int)
    r = mensalidade.corr(fibra.astype(float))
    grupos = [mensalidade[fibra.eq(valor)] for valor in (0, 1)]
    figura = Figure(figsize=(7.5, 5), facecolor=estilo["superficie"], layout="constrained")
    eixo = figura.add_subplot()
    corpos = eixo.violinplot(grupos, positions=[0, 1], widths=0.8, showextrema=False)
    for corpo in corpos["bodies"]:
        corpo.set_facecolor(estilo["taxa"])
        corpo.set_edgecolor(estilo["taxa"])
        corpo.set_alpha(0.3)
    for posicao, valores in enumerate(grupos):
        q1, mediana, q3 = valores.quantile([0.25, 0.5, 0.75])
        eixo.vlines(posicao, q1, q3, color=estilo["tinta"], linewidth=4)
        eixo.scatter(posicao, mediana, s=22, color="#ffffff", edgecolors=estilo["tinta"], zorder=3)
        clientes = f"{len(valores):,}".replace(",", ".")
        eixo.text(posicao + 0.1, mediana, f"mediana R$ {mediana:.2f}".replace(".", ",") + f"  (n = {clientes})",
                  va="center", fontsize=8.5, color=estilo["tinta"])
    eixo.set_xticks([0, 1], ["Sem fibra (0)", "Com fibra (1)"])
    titulo = f"A fibra separa a mensalidade em duas faixas de preço (r = {r:.2f})".replace(".", ",")
    estilizar_eixo(eixo, estilo, titulo, rotulo_y="Mensalidade (R$)")
    return figura
