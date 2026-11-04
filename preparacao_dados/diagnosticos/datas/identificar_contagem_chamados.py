import pandas as pd


def identificar_contagem_chamados(
    dados: pd.DataFrame,
    datas_chamados: pd.DataFrame,
    chamados_excluidos: pd.DataFrame,
    protocolo: dict[str, object],
) -> pd.DataFrame:
    """Conta datas válidas da janela e identifica campos sem contagem disponível."""
    chaves = ["linha_excel", "valor_data"]
    excluidos = pd.MultiIndex.from_frame(datas_chamados[chaves]).isin(
        pd.MultiIndex.from_frame(chamados_excluidos[chaves])
    )
    atuais = datas_chamados["linha_excel"].isin(dados.index + 2)
    restantes = datas_chamados.loc[atuais & ~excluidos]
    inicio = pd.Timestamp(protocolo["inicio_janela_chamados"])
    corte = pd.Timestamp(protocolo["data_corte"])
    na_janela = restantes["data_interpretada"].between(inicio, corte)
    contagens = restantes.loc[na_janela].groupby("linha_excel").size()
    fora_janela = restantes.loc[~na_janela].groupby("linha_excel").size()
    linhas = pd.Series(dados.index + 2, index=dados.index)
    observados = linhas.map(contagens).fillna(0).astype("Int64")
    vazios = dados["data_chamado"].astype("string").str.strip().fillna("").eq("")
    exclusoes = dados["chamados_excluidos_por_cronologia"]
    situacao = pd.Series("contagem_das_datas_validas", index=dados.index)
    situacao.loc[~vazios & exclusoes.gt(0)] = "contagem_valida_com_exclusao_previa"
    situacao.loc[vazios & exclusoes.eq(0)] = "campo_originalmente_sem_datas"
    situacao.loc[vazios & exclusoes.gt(0)] = "campo_esvaziado_pelo_tratamento"
    return pd.DataFrame({
        "id_cliente": dados["id_cliente"],
        "lista_entrada": dados["data_chamado"],
        "inicio_janela": inicio.strftime("%d/%m/%Y"),
        "fim_janela": corte.strftime("%d/%m/%Y"),
        "datas_validas_observadas_90d": observados,
        "datas_fora_janela": linhas.map(fora_janela).fillna(0).astype("Int64"),
        "datas_excluidas_anteriormente": exclusoes,
        "chamados_suporte": observados.mask(vazios, pd.NA),
        "situacao": situacao,
    })
