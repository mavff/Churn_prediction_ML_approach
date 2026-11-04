from pathlib import Path

import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def verificar_normalizacao_numerica(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    avaliacoes: dict[str, pd.DataFrame],
    caminho_origem: Path,
) -> dict[str, object]:
    """Confere tipos e domínios, registrando ausências, conversões e valores invalidados."""
    if not antes.index.equals(depois.index) or not antes.columns.equals(depois.columns):
        raise ValueError("A normalização numérica alterou os registros ou o esquema.")
    # A correção numérica não pode modificar categorias, alvo, identificadores ou metadados.
    preservadas = antes.columns.difference(list(avaliacoes))
    if not antes[preservadas].equals(depois[preservadas]):
        raise ValueError("A normalização numérica alterou outros campos, inclusive alvo e identificadores.")
    dicionario = definir_dicionario_dados()
    indicadores = [("Registros", len(antes), len(depois))]
    evidencias = []
    for campo, tabela in avaliacoes.items():
        regra = dicionario[campo]
        valores = depois[campo]
        conhecidos = valores.dropna()
        if str(valores.dtype) != regra["tipo"] or not valores.equals(tabela["valor_depois"]):
            raise ValueError(f"Tipo ou resultado numérico diferente do identificado: {campo}.")
        if not conhecidos.between(regra["minimo"], regra["maximo"]).all():
            raise ValueError(f"Ainda há valor fora da faixa: {campo}.")
        ausentes = int(tabela["situacao"].eq("ausente_na_entrada").sum())
        invalidos = int(tabela["situacao"].isin(["tipo_invalido", "nao_inteiro", "fora_faixa"]).sum())
        # Toda nova ausência precisa corresponder a um inválido identificado; não há imputação.
        if int(valores.isna().sum()) != ausentes + invalidos:
            raise ValueError(f"Foram preenchidos ausentes ou invalidados valores adicionais: {campo}.")
        indicadores.extend([
            (f"Ausentes na entrada — {campo}", ausentes, ausentes),
            (f"Valores inválidos — {campo}", invalidos, 0),
            (f"Ausentes após validação — {campo}", ausentes, int(valores.isna().sum())),
        ])
        evidencias.append(tabela.loc[tabela["situacao"].ne("valido")])
    auditoria = pd.concat(evidencias, ignore_index=True)
    auditoria.insert(0, "arquivo_origem", caminho_origem.name)
    return {
        "resumo": pd.DataFrame(indicadores, columns=["indicador", "antes", "depois"]),
        "evidencias": auditoria,
        "regra": "Tipos e faixas fixos da Aula 2, p. 3; inteiros discretos, binários em {0, 1} e mensalidade em [10, 500]",
        "decisao": "Preditores inválidos sem correção confiável viram ausentes com original auditado; nenhuma imputação nesta etapa",
    }
