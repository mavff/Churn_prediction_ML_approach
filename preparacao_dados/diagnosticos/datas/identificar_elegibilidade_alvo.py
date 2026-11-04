import pandas as pd


def identificar_elegibilidade_alvo(
    dados: pd.DataFrame,
    datas_por_campo: dict[str, pd.DataFrame],
    protocolo: dict[str, object],
) -> pd.DataFrame:
    """Identifica a coorte e o alvo usando as datas já interpretadas."""
    corte = pd.Timestamp(protocolo["data_corte"])
    fim_alvo = pd.Timestamp(protocolo["fim_janela_alvo"])
    acompanhamento = pd.Timestamp(protocolo["fim_acompanhamento"])
    aquisicao = datas_por_campo["data_aquisicao_cliente"]["data_interpretada"].reindex(dados.index)
    cancelamento = datas_por_campo["data_ocorrencia_churn"]["data_interpretada"].reindex(dados.index)
    historico = (corte - aquisicao).dt.days.astype("Int64")
    preenchido = dados["data_ocorrencia_churn"].astype("string").str.strip().fillna("").ne("")
    motivo = pd.Series("elegivel", index=dados.index, dtype="string")
    impedimentos = [
        (aquisicao.isna(), "aquisicao_ausente_ou_invalida"),
        (aquisicao.gt(corte), "aquisicao_apos_corte"),
        (cancelamento.lt(aquisicao), "cancelamento_inconsistente"),
        (preenchido & cancelamento.isna(), "cancelamento_sem_referencia_interpretada"),
        (cancelamento.le(corte), "cancelado_ate_corte"),
        (historico.lt(protocolo["historico_minimo_dias"]), "historico_inferior_ao_minimo"),
        (cancelamento.gt(acompanhamento), "evento_apos_acompanhamento"),
    ]
    for condicao, justificativa in impedimentos:
        motivo.loc[motivo.eq("elegivel") & condicao.fillna(False)] = justificativa
    evento = cancelamento.gt(corte) & cancelamento.le(fim_alvo) & cancelamento.le(acompanhamento)
    if not protocolo["cobertura_completa"] or acompanhamento < fim_alvo:
        motivo.loc[motivo.eq("elegivel") & ~evento] = (
            "acompanhamento_insuficiente" if acompanhamento < fim_alvo else "cobertura_nao_assumida"
        )
    elegivel = motivo.eq("elegivel")
    alvo = pd.Series(pd.NA, index=dados.index, dtype="Int64")
    alvo.loc[elegivel] = evento.loc[elegivel].astype("int64")
    fundamento = pd.Series("Alvo não atribuído; fora da população desta análise", index=dados.index)
    fundamento.loc[alvo.eq(1).fillna(False)] = f"Cancelamento observado após {corte:%d/%m/%Y} e até {fim_alvo:%d/%m/%Y}"
    fundamento.loc[alvo.eq(0).fillna(False)] = "Sem evento na janela; cobertura completa assumida por convenção didática"
    return pd.DataFrame({
        "id_cliente": dados["id_cliente"],
        "data_corte": corte.strftime("%d/%m/%Y"),
        "data_aquisicao_entrada": dados["data_aquisicao_cliente"],
        "cancelamento_entrada": dados["data_ocorrencia_churn"],
        "historico_dias": historico,
        "elegivel": elegivel,
        "motivo": motivo,
        "churn": alvo,
        "fundamento_alvo": fundamento,
    })
