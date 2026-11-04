from pathlib import Path

import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def verificar_padronizacao_categorias(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    ocorrencias: pd.DataFrame,
    caminho_origem: Path,
) -> dict[str, object]:
    """Confere o de-para e as ausências, mantendo o original e a regra na auditoria."""
    # Usa o de-para identificado para conferir a saída, sem procurar novamente as grafias.
    esperado = antes.copy()
    for campo, regra in definir_dicionario_dados().items():
        if regra["tipo"] == "categoria":
            esperado[campo] = esperado[campo].astype("string")
    for campo, grupo in ocorrencias.groupby("campo", sort=False):
        indices = grupo["linha_excel"].astype(int) - 2
        esperado.loc[indices, campo] = grupo["valor_depois"].to_numpy()
    if not depois.equals(esperado):
        raise ValueError("A padronização alterou células diferentes das previstas, inclusive alvo ou ausências.")
    indicadores = [("Registros", len(antes), len(depois))]
    for campo in ("tipo_contrato", "forma_pagamento"):
        situacoes = ocorrencias.loc[ocorrencias["campo"].eq(campo), "situacao"]
        quantidade = int(situacoes.eq("padronizar").sum())
        indicadores.append((f"Grafias a padronizar — {campo}", quantidade, 0))
        desconhecidos = int(situacoes.eq("categoria_desconhecida").sum())
        ausentes = int(situacoes.eq("ausente_na_entrada").sum())
        indicadores.extend([
            (f"Categorias desconhecidas — {campo}", desconhecidos, 0),
            (f"Ausentes após validação — {campo}", ausentes, ausentes + desconhecidos),
        ])
    auditoria = ocorrencias.copy()
    auditoria.insert(0, "arquivo_origem", caminho_origem.name)
    return {
        "resumo": pd.DataFrame(indicadores, columns=["indicador", "antes", "depois"]),
        "evidencias": auditoria,
        "regra": "Usar Mensal/Anual/Bienal e Boleto/Cartão/Pix; normalizar caixa, espaços externos e acentos para comparação",
        "decisao": "De-para fixo da Aula 2, p. 3; manter Cartão na saída; desconhecidos viram ausentes, com original auditado e sem imputação",
    }
