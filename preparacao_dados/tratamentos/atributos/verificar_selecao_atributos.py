import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def verificar_selecao_atributos(
    antes: dict[str, dict[str, object]],
    depois: dict[str, dict[str, object]],
    avaliacao: pd.DataFrame,
    protocolo: dict[str, object],
) -> dict[str, object]:
    """Confere a retirada aprovada nos três conjuntos e registra a decisão sobre cada atributo."""
    preditores = [campo for campo, regra in definir_dicionario_dados().items() if regra["tipo"] != "alvo"]
    retirados = [campo for campo in preditores if protocolo[f"selecao_{campo}"] == "retirar"]
    treino = antes["treino"]
    if list(treino["X"].columns) != preditores or list(avaliacao["campo"].unique()) != preditores:
        raise ValueError("O diagnóstico deve avaliar os oito preditores do dicionário antes da seleção.")
    if treino["X"].isna().any().any() or not treino["y"].isin([0, 1]).all():
        raise ValueError("A seleção exige treino imputado e alvo binário.")
    # Reconfere as sinalizações contra os limiares, sem recalcular as correlações.
    irrelevantes = ~avaliacao["correlacao_churn"].abs().ge(protocolo["limiar_irrelevancia"])
    redundantes = avaliacao["correlacao_atributo"].abs().ge(protocolo["limiar_redundancia"])
    situacao = avaliacao["situacao"]
    if (not irrelevantes.eq(situacao.str.contains("candidato_irrelevante")).all()
            or not redundantes.eq(situacao.str.contains("candidato_redundante")).all()):
        raise ValueError("As sinalizações não correspondem aos limiares do diagnóstico.")
    # Só sai do X o campo cujos indicadores foram todos sinalizados como irrelevantes na AED do treino.
    sem_evidencia = [campo for campo in retirados if not irrelevantes[avaliacao["campo"].eq(campo)].all()]
    if sem_evidencia:
        raise ValueError(f"Retirada sem evidência de irrelevância no treino: {sem_evidencia}.")
    mantidos = [campo for campo in preditores if campo not in retirados]
    for nome, partes in depois.items():
        original = antes[nome]
        # Reconstruída, a tabela completa deve ser idêntica: a coluna retirada muda só de papel.
        completo_antes = pd.concat([original["X"], original["y"], original["metadados"]], axis=1)[original["ordem_colunas"]]
        completo_depois = pd.concat([partes["X"], partes["y"], partes["metadados"]], axis=1)[partes["ordem_colunas"]]
        if list(partes["X"].columns) != mantidos or not completo_depois.equals(completo_antes):
            raise ValueError(f"A seleção alterou valores ou perdeu colunas no conjunto {nome}.")
    # Preditores idênticos com rótulos diferentes indicariam ruído no alvo (Aula 2, p. 10).
    conflitos = int(pd.concat([treino["X"], treino["y"]], axis=1).groupby(preditores)[treino["y"].name].nunique().gt(1).sum())
    extremos = int(avaliacao["extremos_iqr"].fillna(0).sum())
    decisoes = []
    for campo, sinais in zip(avaliacao["campo"], situacao):
        if campo in retirados:
            decisoes.append("retirado do X; mantido na base para o benchmark")
        elif "candidato_redundante" in sinais:
            decisoes.append("mantido; redundância registrada para a modelagem")
        elif "extremos_a_investigar" in sinais:
            decisoes.append("mantido; extremos plausíveis documentados")
        elif "candidato_irrelevante" in sinais:
            decisoes.append("mantido; candidato a irrelevante registrado")
        else:
            decisoes.append("mantido")
    resumo = pd.DataFrame([
        ("Clientes do treino", len(treino["X"]), len(treino["X"])),
        *[(f"Preditores em X — {nome}", len(preditores), partes["X"].shape[1]) for nome, partes in depois.items()],
        ("Atributos candidatos a irrelevantes no X", int(irrelevantes.sum()), int((irrelevantes & ~avaliacao["campo"].isin(retirados)).sum())),
        ("Atributos candidatos a redundantes", int(redundantes.sum()), int(redundantes.sum())),
        ("Valores extremos por IQR", extremos, extremos),
        ("Grupos de preditores iguais com churn diferente", conflitos, conflitos),
    ], columns=["indicador", "antes", "depois"])
    return {
        "resumo": resumo,
        "evidencias": avaliacao.assign(decisao=decisoes),
        "regra": (
            f"AED somente no treino imputado: Pearson com churn e entre atributos, categorias em indicadores 0/1; "
            f"|r| < {protocolo['limiar_irrelevancia']} sinaliza irrelevância; |r| ≥ {protocolo['limiar_redundancia']} "
            "entre campos diferentes sinaliza redundância; extremos fora de 1,5 IQR (Aula 2, pp. 10 e 17)"
        ),
        "decisao": (
            f"Retirado do X: {', '.join(retirados) or 'nenhum'}, mantido na base para o benchmark; "
            f"{protocolo['decisao_redundancia']}; {protocolo['decisao_ruido']}; {protocolo['fora_do_X']}"
        ),
    }
