import pandas as pd


def diagnosticar_cronologia(
    datas_por_campo: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Compara os eventos com a aquisição da mesma linha da fonte."""
    aquisicoes = datas_por_campo["data_aquisicao_cliente"][[
        "linha_excel", "valor_original", "data_interpretada",
    ]].rename(columns={
        "valor_original": "aquisicao_original",
        "data_interpretada": "data_aquisicao_interpretada",
    })
    regras = {
        "data_chamado": "Chamado anterior à aquisição",
        "data_ocorrencia_churn": "Cancelamento anterior à aquisição",
    }
    resumos = []
    evidencias = []

    for campo, regra in regras.items():
        linhas = datas_por_campo[campo].merge(
            aquisicoes,
            on="linha_excel",
            how="left",
            validate="many_to_one",
            sort=False,
        )
        comparaveis = (
            linhas["data_interpretada"].notna()
            & linhas["data_aquisicao_interpretada"].notna()
        )
        anteriores = comparaveis & (
            linhas["data_interpretada"]
            < linhas["data_aquisicao_interpretada"]
        )

        resumos.append({
            "regra": regra,
            "datas_informadas": len(linhas),
            "datas_comparaveis": int(comparaveis.sum()),
            "datas_nao_comparaveis": int((~comparaveis).sum()),
            "ocorrencias": int(anteriores.sum()),
            "registros_afetados": linhas.loc[
                anteriores, "linha_excel"
            ].nunique(),
            "clientes_afetados": linhas.loc[
                anteriores, "id_cliente"
            ].nunique(),
        })

        detalhes = linhas.loc[anteriores].copy()
        detalhes.insert(0, "campo", campo)
        detalhes.insert(0, "regra", regra)
        detalhes["tratamento_proposto"] = "Conferir origem e eventual reativação"
        detalhes["decisao"] = "Pendente"
        evidencias.extend(detalhes.to_dict("records"))

    return {
        "02_resumo_cronologia": pd.DataFrame(resumos),
        "02_inconsistencias_temporais": pd.DataFrame(evidencias, columns=[
            "regra", "campo", "linha_excel", "id_cliente",
            "valor_original", "valor_data", "data_interpretada",
            "aquisicao_original", "data_aquisicao_interpretada",
            "tratamento_proposto", "decisao",
        ]),
    }
