import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.graficos.estilizar_eixo import estilizar_eixo


def desenhar_ausencias(antes: dict[str, pd.DataFrame], limiar: float, estilo: dict[str, object]) -> Figure:
    """Compara a ausência de cada preditor nos três conjuntos, antes da imputação, com o limiar de alerta."""
    preditores = [campo for campo, regra in definir_dicionario_dados().items() if regra["tipo"] != "alvo"]
    taxas = pd.DataFrame({nome: 100 * tabela[preditores].isna().mean() for nome, tabela in antes.items()})
    sem_ausencia = taxas.index[taxas.max(axis=1).eq(0)].tolist()
    taxas = taxas.loc[taxas.max(axis=1).gt(0)].sort_values("treino")
    alertados = taxas.index[taxas.max(axis=1).gt(100 * limiar)].tolist()
    figura = Figure(figsize=(9, 5), facecolor=estilo["superficie"], layout="constrained")
    eixo = figura.add_subplot()
    altura = 0.8 / len(taxas.columns)
    for i, nome in enumerate(taxas.columns):
        # O treino fica em cima em cada grupo, na mesma ordem da legenda.
        posicoes = np.arange(len(taxas)) + ((len(taxas.columns) - 1) / 2 - i) * altura
        barras = eixo.barh(posicoes, taxas[nome], height=altura * 0.9, color=estilo["conjuntos"][nome],
                           label=estilo["rotulos_conjuntos"][nome])
        eixo.bar_label(barras, labels=[f"{v:.1f}%".replace(".", ",") for v in taxas[nome]], padding=3, fontsize=7.5, color=estilo["tinta"])
    # O contrato de dados da Aula 2, p. 11, pede alerta acima deste limiar.
    eixo.axvline(100 * limiar, color=estilo["neutro"], linewidth=1)
    eixo.text(100 * limiar, len(taxas) - 0.45, f" limiar de alerta ({limiar:.0%})", fontsize=8, color=estilo["secundaria"])
    eixo.set_yticks(range(len(taxas)), taxas.index)
    eixo.set_xlim(0, max(taxas.max().max(), 100 * limiar) * 1.25)
    eixo.legend(frameon=False, fontsize=8, loc="lower right")
    titulo = f"Acima de {limiar:.0%} de ausência antes da imputação: {', '.join(alertados) or 'nenhum campo'}"
    rotulo_x = "Ausentes (%)" + (f"\nSem ausência em nenhum conjunto: {', '.join(sem_ausencia)}" if sem_ausencia else "")
    estilizar_eixo(eixo, estilo, titulo, rotulo_x=rotulo_x, grade="x")
    return figura
