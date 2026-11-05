import pandas as pd
from matplotlib.figure import Figure

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.graficos.estilizar_eixo import estilizar_eixo


def desenhar_churn_tempo_contrato(treino: pd.DataFrame, estilo: dict[str, object]) -> Figure:
    """Mostra a taxa de churn por faixa de tempo de casa, com uma linha por tipo de contrato."""
    faixas = estilo["faixas_tempo"]
    y = treino["churn"].astype(int)
    tempo = pd.cut(treino["tempo_cliente_meses"].astype(float), bins=faixas["limites"], labels=faixas["rotulos"], right=False)
    taxas = y.groupby([treino["tipo_contrato"], tempo], observed=False).mean().mul(100)
    contratos = list(definir_dicionario_dados()["tipo_contrato"]["de_para"].values())
    figura = Figure(figsize=(9, 5), facecolor=estilo["superficie"], layout="constrained")
    eixo = figura.add_subplot()
    posicoes = range(len(faixas["rotulos"]))
    # Do mensal ao bienal, o tom escurece com a duração do contrato.
    for contrato, cor in zip(contratos, estilo["ordinal"]):
        if contrato not in taxas.index.get_level_values(0):
            continue
        serie = taxas.loc[contrato].reindex(faixas["rotulos"])
        eixo.plot(posicoes, serie.to_numpy(), color=cor, linewidth=2, marker="o", markersize=6, label=contrato)
        ultimo = serie.last_valid_index()
        if ultimo is not None:
            eixo.text(faixas["rotulos"].index(ultimo) + 0.08, serie[ultimo], contrato, va="center", fontsize=9, color=estilo["tinta"])
    eixo.axhline(100 * y.mean(), color=estilo["neutro"], linewidth=1)
    eixo.text(-0.25, 100 * y.mean() + 1, f"média do treino {100 * y.mean():.1f}%".replace(".", ","), fontsize=8, color=estilo["secundaria"])
    eixo.set_xticks(list(posicoes), faixas["rotulos"])
    eixo.set_xlim(-0.3, len(faixas["rotulos"]) - 0.4)
    eixo.legend(frameon=False, fontsize=8, loc="upper right")
    estilizar_eixo(eixo, estilo, "Churn por tempo de casa e tipo de contrato no treino",
                   rotulo_x="Tempo de casa no corte (meses)", rotulo_y="Churn (%)")
    return figura
