import pandas as pd

from preparacao_dados.diagnosticos.datas.diagnosticar_cronologia import (
    diagnosticar_cronologia,
)


def diagnosticar_datas(dados: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Diagnostica datas textuais sem alterar a base e seus índices da fonte."""
    campos = (
        "data_aquisicao_cliente",
        "data_chamado",
        "data_ocorrencia_churn",
    )
    resumos = []
    evidencias = []
    datas_por_campo = {}

    for campo in campos:
        valores = dados[campo].astype("string").str.strip()
        ausentes = valores.isna() | valores.eq("")

        linhas = dados.loc[~ausentes, ["id_cliente", campo]].copy()
        linhas.insert(0, "linha_excel", linhas.index + 2)
        linhas = linhas.rename(columns={campo: "valor_original"})
        linhas["valor_data"] = valores.loc[~ausentes]

        if campo == "data_chamado":
            linhas["valor_data"] = linhas["valor_data"].str.split(",")
            linhas = linhas.explode("valor_data")

        linhas["valor_data"] = linhas["valor_data"].str.strip()
        datas_brasileiras = pd.to_datetime(
            linhas["valor_data"], format="%d/%m/%Y", errors="coerce"
        )
        datas_iso = pd.to_datetime(
            linhas["valor_data"], format="%Y-%m-%d", errors="coerce"
        )
        datas = datas_brasileiras.fillna(datas_iso)
        nao_interpretadas = datas.isna()
        linhas["data_interpretada"] = datas
        datas_por_campo[campo] = linhas

        resumos.append({
            "campo": campo,
            "registros": len(dados),
            "campos_sem_data": int(ausentes.sum()),
            "datas_informadas": len(linhas),
            "datas_interpretadas": int(datas.notna().sum()),
            "datas_formato_iso": int(
                (datas_brasileiras.isna() & datas_iso.notna()).sum()
            ),
            "datas_nao_interpretadas": int(nao_interpretadas.sum()),
            "registros_com_falha": linhas.loc[
                nao_interpretadas, "linha_excel"
            ].nunique(),
            "menor_data": datas.min(),
            "maior_data": datas.max(),
        })

        detalhes = linhas.loc[nao_interpretadas].copy()
        detalhes.insert(0, "campo", campo)
        detalhes["regra"] = "Data em DD/MM/AAAA ou AAAA-MM-DD"
        detalhes["tratamento_proposto"] = "Investigar formato e origem"
        detalhes["decisao"] = "Pendente"
        evidencias.extend(detalhes.to_dict("records"))

    abas = {
        "02_resumo_datas": pd.DataFrame(resumos),
        "02_datas_nao_interpretadas": pd.DataFrame(evidencias, columns=[
            "campo", "linha_excel", "id_cliente", "valor_original",
            "valor_data", "regra", "tratamento_proposto", "decisao",
        ]),
    }
    abas.update(diagnosticar_cronologia(datas_por_campo))
    return abas
