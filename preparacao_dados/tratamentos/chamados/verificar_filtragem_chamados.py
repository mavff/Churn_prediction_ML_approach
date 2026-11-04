from collections import Counter
from pathlib import Path

import pandas as pd


def verificar_filtragem_chamados(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    ocorrencias: pd.DataFrame,
    datas_chamados: pd.DataFrame,
    protocolo: dict[str, object],
    caminho_origem: Path,
) -> dict[str, object]:
    """Confere as exclusões identificadas e gera uma evidência por cliente."""
    campo = "data_chamado"
    controle = "chamados_excluidos_por_cronologia"
    colunas = [*antes.columns] + ([] if controle in antes else [controle])
    if not antes.index.equals(depois.index) or list(depois.columns) != colunas:
        raise ValueError("A filtragem alterou linhas ou colunas indevidamente.")
    if not antes.drop(columns=[campo, controle], errors="ignore").equals(depois.drop(columns=[campo, controle])):
        raise ValueError("A filtragem alterou outros campos.")
    contagens = ocorrencias.groupby("linha_excel").size()
    incrementos = pd.Series(antes.index + 2, index=antes.index).map(contagens).fillna(0).astype(int)
    controle_antes = antes.get(controle, pd.Series(0, index=antes.index))
    if not depois[controle].eq(controle_antes + incrementos).all():
        raise ValueError("A quantidade excluída não corresponde às evidências.")
    sem_ocorrencia = incrementos.eq(0)
    if not antes.loc[sem_ocorrencia, campo].equals(depois.loc[sem_ocorrencia, campo]):
        raise ValueError("Foram modificados clientes sem chamados inconsistentes.")
    for linha, grupo in ocorrencias.groupby("linha_excel", sort=False):
        indice = int(linha) - 2
        # Counter preserva multiplicidades: duas ocorrências no mesmo dia não equivalem a uma.
        originais = Counter(p.strip() for p in str(antes.at[indice, campo]).split(",") if p.strip())
        finais = Counter(p.strip() for p in str(depois.at[indice, campo]).split(",") if p.strip())
        if finais - originais or originais - finais != Counter(grupo["valor_data"]):
            raise ValueError("As datas removidas diferem das identificadas.")

    chaves = ["linha_excel", "valor_data"]
    removidas = pd.MultiIndex.from_frame(datas_chamados[chaves]).isin(
        pd.MultiIndex.from_frame(ocorrencias[chaves])
    )
    restantes = datas_chamados.loc[~removidas, "data_interpretada"]
    datas_antes = datas_chamados["data_interpretada"]
    vazios_antes = antes[campo].astype("string").str.strip().fillna("").eq("")
    vazios_depois = depois[campo].astype("string").str.strip().fillna("").eq("")
    # Reúne todas as datas excluídas em uma evidência por cliente para facilitar a leitura.
    auditoria = ocorrencias.groupby("linha_excel", sort=False).agg(
        id_cliente=("id_cliente", "first"),
        datas_excluidas=("valor_data", ", ".join),
        quantidade_excluida=("valor_data", "size"),
    ).reset_index()
    fora_janela = datas_chamados.loc[~datas_antes.between(
        pd.Timestamp(protocolo["inicio_janela_chamados"]), pd.Timestamp(protocolo["data_corte"]),
    )].groupby("linha_excel", sort=False).agg(
        id_cliente=("id_cliente", "first"), datas_fora_janela=("valor_data", ", ".join),
    ).reset_index()
    auditoria = auditoria.merge(fora_janela, on=["linha_excel", "id_cliente"], how="outer", sort=False)
    auditoria["quantidade_excluida"] = auditoria["quantidade_excluida"].fillna(0).astype(int)
    auditoria[["datas_excluidas", "datas_fora_janela"]] = auditoria[["datas_excluidas", "datas_fora_janela"]].fillna("")
    indices = auditoria["linha_excel"].astype(int) - 2
    auditoria.insert(0, "arquivo_origem", caminho_origem.name)
    auditoria["aquisicao"] = antes.loc[indices, "data_aquisicao_cliente"].to_numpy()
    auditoria["lista_antes"] = antes.loc[indices, campo].to_numpy()
    auditoria["lista_depois"] = depois.loc[indices, campo].to_numpy()
    resumo = pd.DataFrame([
        ("Registros", len(antes), len(depois)),
        ("Datas de chamados", len(datas_chamados), len(restantes)),
        ("Datas anteriores à aquisição", len(ocorrencias), 0),
        ("Clientes com chamados inconsistentes", ocorrencias["id_cliente"].nunique(), 0),
        ("Campos sem chamados", int(vazios_antes.sum()), int(vazios_depois.sum())),
        ("Campos vazios com exclusão registrada", int((vazios_antes & controle_antes.gt(0)).sum()), int((vazios_depois & depois[controle].gt(0)).sum())),
        ("Datas após o corte", int(datas_antes.gt(pd.Timestamp(protocolo["data_corte"])).sum()), int(restantes.gt(pd.Timestamp(protocolo["data_corte"])).sum())),
        ("Datas na janela histórica", int(datas_antes.between(pd.Timestamp(protocolo["inicio_janela_chamados"]), pd.Timestamp(protocolo["data_corte"])).sum()), int(restantes.between(pd.Timestamp(protocolo["inicio_janela_chamados"]), pd.Timestamp(protocolo["data_corte"])).sum())),
    ], columns=["indicador", "antes", "depois"])
    return {
        "resumo": resumo, "evidencias": auditoria,
        "regra": "Excluir somente datas anteriores à aquisição; preservar os demais chamados",
        "decisao": "Aplicado; campos esvaziados e originalmente ausentes permanecem distinguíveis",
    }
