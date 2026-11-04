from pathlib import Path

import pandas as pd


def verificar_exclusao_cancelamentos_inconsistentes(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    ocorrencias: pd.DataFrame,
    caminho_origem: Path,
) -> dict[str, object]:
    """Verifica a exclusão direta e preserva os registros completos na auditoria."""
    if ocorrencias["linha_excel"].duplicated().any():
        raise ValueError("Há mais de uma evidência de cancelamento para a mesma linha.")
    indices = ocorrencias["linha_excel"].astype(int) - 2
    if not depois.equals(antes.drop(index=indices)):
        raise ValueError("Exclua somente os registros identificados, sem alterar os demais.")
    if antes.loc[indices, "id_cliente"].tolist() != ocorrencias["id_cliente"].tolist():
        raise ValueError("Os clientes das evidências diferem da entrada.")
    originais = antes.loc[indices, "data_ocorrencia_churn"].astype("string").tolist()
    if originais != ocorrencias["valor_original"].astype("string").tolist():
        raise ValueError("As datas inconsistentes mudaram depois da identificação.")
    auditoria = antes.loc[indices].copy()
    auditoria.insert(0, "linha_excel", indices.to_numpy() + 2)
    auditoria.insert(0, "arquivo_origem", caminho_origem.name)
    auditoria["motivo"] = "Cancelamento anterior à aquisição; exclusão aprovada pelo usuário"
    resumo = pd.DataFrame([
        ("Registros", len(antes), len(depois)),
        ("Identificadores distintos", antes["id_cliente"].nunique(), depois["id_cliente"].nunique()),
        ("Cancelamentos anteriores à aquisição", len(ocorrencias), 0),
        ("Clientes excluídos nesta etapa", 0, len(ocorrencias)),
    ], columns=["indicador", "antes", "depois"])
    return {
        "resumo": resumo, "evidencias": auditoria,
        "regra": "Excluir o registro completo quando o cancelamento antecede a aquisição",
        "decisao": "Decisão do projeto aprovada; fonte e registros excluídos preservados na auditoria",
    }
