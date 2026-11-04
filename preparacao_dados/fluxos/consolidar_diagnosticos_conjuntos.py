import pandas as pd


def consolidar_diagnosticos_conjuntos(
    resultados_por_conjunto: dict[str, dict[str, dict[str, object]]],
) -> dict[str, dict[str, object]]:
    """Soma contagens e reúne evidências das mesmas regras nos três conjuntos."""
    primeiro = next(iter(resultados_por_conjunto.values()))
    consolidados = {}
    for problema, referencia in primeiro.items():
        resumos = []
        evidencias = []
        for nome, resultados in resultados_por_conjunto.items():
            resultado = resultados[problema]
            resumos.append(resultado["resumo"])
            evidencia = resultado["evidencias"].copy()
            evidencia["conjunto"] = nome
            evidencias.append(evidencia)
        # Só consolida contagens de auditoria; não calcula médias, medianas ou modas.
        resumo = pd.concat(resumos).groupby("indicador", sort=False, as_index=False)[["antes", "depois"]].sum()
        evidencia = pd.concat(evidencias, ignore_index=True).sort_values(["linha_excel", "campo"])
        consolidados[problema] = {
            "resumo": resumo, "evidencias": evidencia,
            "regra": referencia["regra"], "decisao": referencia["decisao"],
        }
    return consolidados
