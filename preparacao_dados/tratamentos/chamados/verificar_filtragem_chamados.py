from collections import Counter
from pathlib import Path

import pandas as pd

from preparacao_dados.diagnosticos.datas.diagnosticar_datas import diagnosticar_datas


def verificar_filtragem_chamados(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    diagnostico_entrada: dict[str, pd.DataFrame],
    caminho_origem: Path,
) -> dict[str, pd.DataFrame]:
    """Confere os eventos excluídos, os campos preservados e sua rastreabilidade."""
    campo = "data_chamado"
    controle = "chamados_excluidos_por_cronologia"
    colunas = list(antes.columns) + ([controle] if controle not in antes else [])
    if not antes.index.equals(depois.index) or list(depois.columns) != colunas:
        raise ValueError("O T03 alterou linhas, índices ou colunas indevidamente.")
    if not antes.drop(columns=[campo, controle], errors="ignore").equals(
        depois.drop(columns=[campo, controle])
    ):
        raise ValueError("O T03 alterou outros campos da base.")

    evidencias = diagnostico_entrada["02_inconsistencias_temporais"]
    casos = evidencias.loc[evidencias["campo"].eq(campo)].copy()
    contagens = casos.groupby("linha_excel").size()
    linhas = pd.Series(antes.index + 2, index=antes.index)
    incrementos = linhas.map(contagens).fillna(0).astype("int64")
    controle_antes = antes.get(controle, pd.Series(0, index=antes.index))
    if not depois[controle].eq(controle_antes + incrementos).all():
        raise ValueError("A quantidade de datas excluídas é inconsistente.")
    sem_ocorrencia = incrementos.eq(0)
    if not antes.loc[sem_ocorrencia, campo].equals(depois.loc[sem_ocorrencia, campo]):
        raise ValueError("O T03 alterou listas sem ocorrência diagnosticada.")

    for linha_excel, grupo in casos.groupby("linha_excel", sort=False):
        indice = int(linha_excel) - 2
        originais = Counter(p.strip() for p in str(antes.at[indice, campo]).split(",") if p.strip())
        finais = Counter(p.strip() for p in str(depois.at[indice, campo]).split(",") if p.strip())
        if finais - originais or originais - finais != Counter(grupo["valor_data"]):
            raise ValueError("Os eventos excluídos diferem dos diagnosticados.")

    analise_saida = diagnosticar_datas(depois)
    cronologia = analise_saida["02_resumo_cronologia"].set_index("regra")
    if int(cronologia.loc["Chamado anterior à aquisição", "ocorrencias"]):
        raise ValueError("Ainda há chamados anteriores à aquisição.")
    perfil_antes = diagnostico_entrada["02_resumo_datas"].set_index("campo").loc[campo]
    perfil_depois = analise_saida["02_resumo_datas"].set_index("campo").loc[campo]
    if int(perfil_antes["datas_informadas"]) - int(perfil_depois["datas_informadas"]) != len(casos):
        raise ValueError("A quantidade total de datas não foi preservada corretamente.")

    originais = antes[campo].copy()
    originais.index = antes.index + 2
    finais = depois[campo].copy()
    finais.index = depois.index + 2
    auditoria = casos[["linha_excel", "id_cliente", "valor_data"]].rename(
        columns={"valor_data": "data_excluida"}
    )
    auditoria.insert(0, "arquivo_origem", caminho_origem.name)
    auditoria["valor_antes"] = auditoria["linha_excel"].map(originais)
    auditoria["valor_depois"] = auditoria["linha_excel"].map(finais)
    auditoria["motivo"] = "Chamado anterior à aquisição"
    auditoria["decisao"] = "Exclusão aplicada ao campo tratado"

    vazios_antes = antes[campo].isna() | antes[campo].astype("string").str.strip().eq("").fillna(False)
    vazios_depois = depois[campo].isna() | depois[campo].astype("string").str.strip().eq("").fillna(False)
    indicadores = pd.DataFrame([
        ("Registros", len(antes), len(depois)),
        ("Identificadores distintos", antes["id_cliente"].nunique(), depois["id_cliente"].nunique()),
        ("Datas de chamado informadas", int(perfil_antes["datas_informadas"]), int(perfil_depois["datas_informadas"])),
        ("Chamados anteriores à aquisição", len(casos), 0),
        ("Datas excluídas registradas no controle", int(controle_antes.sum()), int(depois[controle].sum())),
        ("Clientes com exclusão registrada", antes.loc[controle_antes.gt(0), "id_cliente"].nunique(), depois.loc[depois[controle].gt(0), "id_cliente"].nunique()),
        ("Campos sem data de chamado", int(vazios_antes.sum()), int(vazios_depois.sum())),
        ("Campos vazios com exclusão registrada", int((vazios_antes & controle_antes.gt(0)).sum()), int((vazios_depois & depois[controle].gt(0)).sum())),
    ], columns=["indicador", "antes", "depois"])

    return {"T03_indicadores": indicadores, "T03_datas_excluidas": auditoria}
