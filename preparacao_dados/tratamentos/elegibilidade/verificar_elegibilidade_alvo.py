from pathlib import Path

import pandas as pd


def verificar_elegibilidade_alvo(
    antes: pd.DataFrame,
    depois: pd.DataFrame,
    avaliacao: pd.DataFrame,
    datas_por_campo: dict[str, pd.DataFrame],
    protocolo: dict[str, object],
    caminho_origem: Path,
) -> dict[str, object]:
    """Confere a seleção e os rótulos, preservando uma avaliação por cliente."""
    participantes = avaliacao["elegivel"].eq(True)
    if not depois.index.equals(antes.index[participantes]):
        raise ValueError("A população resultante difere da avaliação.")
    if list(depois.columns) != [*antes.columns, "data_corte", "churn"]:
        raise ValueError("A etapa deve acrescentar somente data_corte e churn.")
    if not depois[antes.columns].equals(antes.loc[participantes]):
        raise ValueError("Foram alterados valores dos registros mantidos.")
    if depois["churn"].dtype != pd.Int64Dtype() or depois["churn"].isna().any() or not depois["churn"].isin([0, 1]).all():
        raise ValueError("A população supervisionada deve ter alvo inteiro binário conhecido.")
    if not depois["churn"].equals(avaliacao.loc[participantes, "churn"]):
        raise ValueError("O alvo difere da avaliação identificada.")
    corte = pd.Timestamp(protocolo["data_corte"])
    fim_alvo = pd.Timestamp(protocolo["fim_janela_alvo"])
    acompanhamento = pd.Timestamp(protocolo["fim_acompanhamento"])
    aquisicao = datas_por_campo["data_aquisicao_cliente"]["data_interpretada"].reindex(depois.index)
    cancelamento = datas_por_campo["data_ocorrencia_churn"]["data_interpretada"].reindex(depois.index)
    if (not (corte - aquisicao).dt.days.ge(protocolo["historico_minimo_dias"]).all()
            or cancelamento.le(corte).any() or cancelamento.gt(acompanhamento).any()):
        raise ValueError("Há participantes que violam as condições temporais.")
    # Reconfere os rótulos contra a janela temporal para detectar um alvo calculado incorretamente.
    evento = cancelamento.gt(corte) & cancelamento.le(fim_alvo)
    if not depois["churn"].eq(1).eq(evento).all():
        raise ValueError("O rótulo não corresponde à janela de cancelamento.")
    if depois["churn"].eq(0).any() and (not protocolo["cobertura_completa"] or acompanhamento < fim_alvo):
        raise ValueError("Não atribua zero sem a convenção de cobertura e o acompanhamento completo.")
    if not depois["data_corte"].eq(corte.strftime("%d/%m/%Y")).all():
        raise ValueError("A fotografia usa data diferente do protocolo.")
    auditoria = avaliacao.copy()
    auditoria.insert(0, "linha_excel", antes.index + 2)
    auditoria.insert(0, "arquivo_origem", caminho_origem.name)
    resumo = pd.DataFrame([
        ("Registros", len(antes), len(depois)),
        ("Clientes fora desta análise", 0, int((~participantes).sum())),
        ("Rótulos atribuídos", 0, len(depois)),
        ("Churn = 1", 0, int(depois["churn"].eq(1).sum())),
        ("Churn = 0", 0, int(depois["churn"].eq(0).sum())),
    ], columns=["indicador", "antes", "depois"])
    return {
        "resumo": resumo, "evidencias": auditoria,
        "regra": "Cliente ativo no corte, histórico mínimo de 60 dias e desfecho conhecido na janela seguinte",
        "decisao": "Ausência interpretada por convenção didática aprovada; clientes fora da coorte auditados sem rótulo",
    }
