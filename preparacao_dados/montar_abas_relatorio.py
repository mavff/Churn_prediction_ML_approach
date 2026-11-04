from datetime import date

import pandas as pd


def montar_abas_relatorio(
    resultados: dict[str, dict[str, object]],
    protocolo: dict[str, object],
) -> dict[str, pd.DataFrame]:
    """Reúne um resumo global, o protocolo e uma aba de evidências por problema."""
    resumos = []
    regras = []
    for problema, resultado in resultados.items():
        resumo = resultado["resumo"].copy()
        resumo.insert(0, "problema", problema)
        resumos.append(resumo)
        regras.extend([
            (f"Regra — {problema}", resultado["regra"]),
            (f"Decisão — {problema}", resultado["decisao"]),
        ])
    parametros = pd.DataFrame([
        (nome.replace("_", " "), valor.strftime("%d/%m/%Y") if isinstance(valor, date) else valor)
        for nome, valor in protocolo.items()
    ] + regras, columns=["parametro", "valor"])
    abas = {
        "00_resumo": pd.concat(resumos, ignore_index=True),
        "00_protocolo": parametros,
    }
    prioridades = [
        "id_cliente", "linha_excel", "linha_excel_removida", "linha_excel_mantida",
        "historico_dias", "elegivel", "motivo", "churn", "aquisicao",
        "quantidade_excluida", "datas_excluidas", "data_aquisicao_cliente", "data_ocorrencia_churn",
    ]
    for nome, resultado in resultados.items():
        evidencia = resultado["evidencias"].copy()
        primeiras = [coluna for coluna in prioridades if coluna in evidencia]
        restantes = [coluna for coluna in evidencia if coluna not in primeiras and coluna != "arquivo_origem"]
        if "arquivo_origem" in evidencia:
            restantes.append("arquivo_origem")
        abas[nome] = evidencia[primeiras + restantes]
    return abas
