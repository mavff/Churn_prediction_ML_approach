from matplotlib.axes import Axes


def estilizar_eixo(
    eixo: Axes,
    estilo: dict[str, object],
    titulo: str,
    rotulo_x: str | None = None,
    rotulo_y: str | None = None,
    grade: str | None = "y",
) -> None:
    """Aplica o mesmo acabamento a todos os painéis: fundo, título, rótulos, grade e bordas."""
    eixo.set_facecolor(estilo["superficie"])
    eixo.set_title(titulo, loc="left", fontsize=10, color=estilo["tinta"])
    if rotulo_x:
        eixo.set_xlabel(rotulo_x, fontsize=8, color=estilo["secundaria"])
    if rotulo_y:
        eixo.set_ylabel(rotulo_y, fontsize=8, color=estilo["secundaria"])
    eixo.tick_params(labelsize=8, colors=estilo["secundaria"])
    if grade:
        eixo.grid(axis=grade, color=estilo["grade"], linewidth=0.8)
        eixo.set_axisbelow(True)
    eixo.spines[["top", "right"]].set_visible(False)
    eixo.spines[["left", "bottom"]].set_color(estilo["eixo"])
