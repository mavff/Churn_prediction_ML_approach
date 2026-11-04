from math import ceil, floor
from pathlib import Path

import pandas as pd


def verificar_divisao(
    visao: pd.DataFrame,
    conjuntos: dict[str, pd.DataFrame],
    protocolo: dict[str, object],
    caminho_origem: Path,
) -> dict[str, object]:
    """Confere cobertura, tamanhos, conteúdo e ausência de clientes compartilhados."""
    if set(conjuntos) != {"treino", "validacao", "teste"}:
        raise ValueError("São necessários treino, validação e teste.")
    treino = floor(len(visao) * protocolo["proporcao_treino"])
    reserva = len(visao) - treino
    teste = ceil(reserva * protocolo["proporcao_teste"] / (protocolo["proporcao_validacao"] + protocolo["proporcao_teste"]))
    tamanhos = {"treino": treino, "validacao": reserva - teste, "teste": teste}
    vistos = set()
    evidencias = []
    indicadores = [("Clientes participantes", len(visao), sum(map(len, conjuntos.values())))]
    for nome, tabela in conjuntos.items():
        ids = set(tabela["id_cliente"])
        if vistos.intersection(ids) or len(ids) != len(tabela):
            raise ValueError("Um cliente aparece em mais de um conjunto ou está repetido.")
        vistos.update(ids)
        if len(tabela) != tamanhos[nome] or not tabela.index.is_unique:
            raise ValueError(f"Tamanho ou índice inválido no conjunto {nome}.")
        if not tabela.equals(visao.loc[tabela.index]) or set(tabela["churn"].unique()) != {0, 1}:
            raise ValueError(f"Conteúdo ou classes diferentes do esperado no conjunto {nome}.")
        evidencia = tabela[["id_cliente", "data_corte", "churn"]].copy()
        evidencia.insert(0, "linha_excel", tabela.index + 2)
        evidencia.insert(0, "arquivo_origem", caminho_origem.name)
        evidencia["conjunto"] = nome
        evidencias.append(evidencia)
        indicadores.append((f"Clientes — {nome}", 0, len(tabela)))
        for classe in (0, 1):
            indicadores.append((f"Churn = {classe} — {nome}", 0, int(tabela["churn"].eq(classe).sum())))
    if vistos != set(visao["id_cliente"]) or sum(map(len, conjuntos.values())) != len(visao):
        raise ValueError("A divisão perdeu ou acrescentou clientes.")
    indicadores.append(("Clientes compartilhados entre conjuntos", 0, 0))
    return {
        "resumo": pd.DataFrame(indicadores, columns=["indicador", "antes", "depois"]),
        "evidencias": pd.concat(evidencias, ignore_index=True).sort_values("linha_excel"),
        "regra": "Divisão estratificada por churn, reproduzível e sem clientes compartilhados",
        "decisao": "Treino aprende parâmetros; validação seleciona configurações; teste permanece reservado para avaliação final",
    }
