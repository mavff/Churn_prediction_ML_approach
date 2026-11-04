from pathlib import Path

import pandas as pd


def verificar_tempo_cliente_meses(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    avaliacao: pd.DataFrame,
    caminho_origem: Path,
) -> dict[str, object]:
    """Confere o atributo acrescentado e registra o cálculo por cliente."""
    esperado = antes.columns.tolist()
    esperado.insert(esperado.index("data_aquisicao_cliente") + 1, "tempo_cliente_meses")
    if not antes.index.equals(depois.index) or list(depois.columns) != esperado:
        raise ValueError("O tempo de cliente alterou os clientes ou o esquema indevidamente.")
    # O novo atributo não pode modificar aquisição, contagem de chamados ou alvo já construídos.
    if not depois[antes.columns].equals(antes):
        raise ValueError("O tempo de cliente alterou campos existentes, inclusive o alvo.")
    meses = depois["tempo_cliente_meses"]
    if meses.dtype != pd.Int64Dtype() or meses.isna().any() or meses.lt(0).any():
        raise ValueError("Tempo de cliente deve ser inteiro não negativo e conhecido.")
    if not meses.equals(avaliacao["tempo_cliente_meses"]):
        raise ValueError("O tempo de cliente difere do cálculo identificado.")
    auditoria = avaliacao.copy()
    auditoria.insert(0, "linha_excel", antes.index + 2)
    auditoria.insert(0, "arquivo_origem", caminho_origem.name)
    resumo = pd.DataFrame([
        ("Registros", len(antes), len(depois)),
        ("Tempos de cliente disponíveis", 0, int(meses.notna().sum())),
    ], columns=["indicador", "antes", "depois"])
    return {
        "resumo": resumo, "evidencias": auditoria,
        "regra": "Contar meses completos de calendário até o corte, descontando o mês cujo dia de aquisição ainda não chegou",
        "decisao": "Atributo derivado conforme Aula 1, p. 7; fórmula de meses completos aprovada no projeto",
    }
