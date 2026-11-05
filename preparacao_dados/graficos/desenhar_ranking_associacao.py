import pandas as pd
from matplotlib.figure import Figure

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.graficos.calcular_information_value import calcular_information_value
from preparacao_dados.graficos.estilizar_eixo import estilizar_eixo


def desenhar_ranking_associacao(
    avaliacao: pd.DataFrame,
    treino: pd.DataFrame,
    limiar_irrelevancia: float,
    estilo: dict[str, object],
) -> Figure:
    """Ordena os atributos pela correlação com churn e pelo Information Value, com as faixas de leitura."""
    preditores = [campo for campo, regra in definir_dicionario_dados().items() if regra["tipo"] != "alvo"]
    r = avaliacao.set_index("atributo")["correlacao_churn"].fillna(0).sort_values(key=abs)
    iv = calcular_information_value(treino[preditores], treino["churn"]).sort_values("information_value")
    figura = Figure(figsize=(10, 5.6), facecolor=estilo["superficie"], layout="constrained")
    esquerda, direita = figura.subplots(1, 2, width_ratios=[1.15, 1])
    # Correlação positiva aumenta o risco (vermelho); negativa protege (azul); a faixa cinza é a zona irrelevante.
    limite = max(r.abs().max(), limiar_irrelevancia) * 1.35
    esquerda.axvspan(-limiar_irrelevancia, limiar_irrelevancia, color=estilo["faixa"])
    cores = [estilo["divergente"][2] if valor > 0 else estilo["divergente"][0] for valor in r]
    barras = esquerda.barh(r.index, r.to_numpy(), height=0.6, color=cores)
    esquerda.bar_label(barras, labels=[f"{valor:+.2f}".replace(".", ",") for valor in r], padding=3, fontsize=7.5, color=estilo["tinta"])
    esquerda.axvline(0, color=estilo["eixo"], linewidth=1)
    esquerda.set_xlim(-limite, limite)
    estilizar_eixo(esquerda, estilo, f"Correlação com churn (faixa cinza: |r| < {limiar_irrelevancia:g})".replace(".", ","), grade="x")
    barras = direita.barh(iv["campo"], iv["information_value"], height=0.6, color=estilo["taxa"])
    direita.bar_label(barras, labels=[f"{valor:.3f}".replace(".", ",") for valor in iv["information_value"]], padding=3, fontsize=7.5, color=estilo["tinta"])
    # Escala usual do IV: abaixo de 0,02 inútil; até 0,1 fraco; até 0,3 médio; acima, forte.
    for corte, nome in ((0.02, "fraco"), (0.1, "médio"), (0.3, "forte")):
        direita.axvline(corte, color=estilo["neutro"], linewidth=0.8)
        direita.text(corte, len(iv) - 0.4, f" {nome}", fontsize=7.5, color=estilo["secundaria"])
    direita.set_xlim(0, max(iv["information_value"].max(), 0.3) * 1.25)
    estilizar_eixo(direita, estilo, "Information Value (WoE) por campo", grade="x")
    figura.suptitle("Associação de cada atributo com churn no treino", x=0.01, ha="left", fontsize=11, color=estilo["tinta"])
    figura.text(0.01, 0.005, "Vermelho: associado a mais churn · azul: a menos churn · IV abaixo de 0,02 = sem poder de separação",
                fontsize=8, color=estilo["secundaria"])
    return figura
