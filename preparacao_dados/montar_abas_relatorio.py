from datetime import date

import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados


def montar_abas_relatorio(
    resultados: dict[str, dict[str, object]],
    protocolo: dict[str, object],
) -> dict[str, pd.DataFrame]:
    """Reúne um resumo global, o protocolo e uma aba de evidências por problema."""
    resumos = []
    regras = []
    # Todas as verificações entregam o mesmo conjunto de resumo, evidências, regra e decisão.
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
    dominios = []
    for campo, regra in definir_dicionario_dados().items():
        dominio = ", ".join(regra["de_para"].values()) if regra["tipo"] == "categoria" else f"[{regra['minimo']}, {regra['maximo']}]"
        dominios.append((f"Dicionário — {campo}", f"{regra['tipo']}; domínio {dominio}; obrigatório: {regra['obrigatorio']}"))
    parametros = pd.concat([parametros, pd.DataFrame(dominios, columns=parametros.columns)], ignore_index=True)
    abas = {
        "00_resumo": pd.concat(resumos, ignore_index=True),
        "00_protocolo": parametros,
    }
    prioridades = [
        "id_cliente", "linha_excel", "linha_excel_removida", "linha_excel_mantida",
        "campo", "valor_antes", "valor_depois", "tempo_cliente_meses",
        "chamados_suporte", "situacao", "datas_validas_observadas_90d",
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
