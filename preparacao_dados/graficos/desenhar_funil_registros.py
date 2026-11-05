from matplotlib.figure import Figure

from preparacao_dados.graficos.estilizar_eixo import estilizar_eixo


def desenhar_funil_registros(resultados: dict[str, dict[str, object]], estilo: dict[str, object]) -> Figure:
    """Mostra quantos registros cada exclusão retirou até a divisão em treino, validação e teste."""
    registros = {
        problema: resultados[problema]["resumo"].set_index("indicador").loc["Registros"]
        for problema in ("01_duplicatas", "04_cancelamentos", "05_elegibilidade_alvo")
    }
    etapas = [
        ("Fonte", int(registros["01_duplicatas"]["antes"]), ""),
        ("Sem cópias integrais", int(registros["01_duplicatas"]["depois"]), "cópias"),
        ("Sem cancelamento anterior à aquisição", int(registros["04_cancelamentos"]["depois"]), "inconsistentes"),
        ("Com 60 dias ou mais de casa", int(registros["05_elegibilidade_alvo"]["depois"]), "menos de 60 dias"),
    ]
    conjuntos = {nome: len(tabela) for nome, tabela in resultados["08_divisao"]["saida"].items()}
    inicio, final = etapas[0][1], etapas[-1][1]
    figura = Figure(figsize=(9, 4.6), facecolor=estilo["superficie"], layout="constrained")
    eixo = figura.add_subplot()
    for posicao, (_, quantidade, motivo) in enumerate(etapas):
        eixo.barh(posicao, quantidade, height=0.6, color=estilo["taxa"])
        perda = etapas[posicao - 1][1] - quantidade if posicao else 0
        texto = f"{quantidade:,}".replace(",", ".") + (f"   −{perda} ({motivo})" if perda else "")
        eixo.text(quantidade + inicio * 0.01, posicao, texto, va="center", fontsize=9, color=estilo["tinta"])
    # A última linha reparte a população nos três conjuntos, na mesma escala das anteriores.
    linha, esquerda = len(etapas), 0
    for nome, quantidade in conjuntos.items():
        eixo.barh(linha, quantidade, left=esquerda, height=0.6, color=estilo["conjuntos"][nome],
                  edgecolor=estilo["superficie"], linewidth=2)
        eixo.text(esquerda + quantidade / 2, linha, f"{estilo['rotulos_conjuntos'][nome]}\n{quantidade:,}".replace(",", "."),
                  ha="center", va="center", fontsize=8.5, color="#ffffff")
        esquerda += quantidade
    eixo.set_yticks(range(linha + 1), [rotulo for rotulo, _, _ in etapas] + ["Divisão estratificada 50/25/25"])
    eixo.invert_yaxis()
    eixo.set_xlim(0, inicio * 1.6)
    eixo.set_xticks([])
    titulo = f"{final:,} de {inicio:,} linhas chegam à análise ({100 * final / inicio:.1f}%)".replace(",", "X").replace(".", ",").replace("X", ".")
    estilizar_eixo(eixo, estilo, titulo, grade=None)
    eixo.spines["bottom"].set_visible(False)
    return figura
