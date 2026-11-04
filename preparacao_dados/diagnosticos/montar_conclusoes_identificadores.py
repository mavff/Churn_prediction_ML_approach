import pandas as pd


def montar_conclusoes_identificadores(
    dados: pd.DataFrame,
    evidencias: pd.DataFrame,
) -> pd.DataFrame:
    """Organiza as conclusões e a decisão sobre repetições integrais."""
    registros_integrais = evidencias.loc[
        evidencias["registro_integral_repetido"]
    ]

    excedentes = int(
        registros_integrais.duplicated(
            subset=dados.columns.tolist()
        ).sum()
    )

    return pd.DataFrame(
        [
            ("Verificação", "Repetição integral de registros"),
            ("Registros envolvidos", len(registros_integrais)),
            ("Identificadores envolvidos",
             registros_integrais["id_cliente"].nunique()),
            ("Ocorrências excedentes", excedentes),
            ("Regra de referência",
             "Uma observação por cliente e data de corte"),
            ("Evidência",
             "01_evidencias_identificadores: coluna linha_excel"),
            ("Tratamento aprovado",
             "Manter a primeira ocorrência e remover cópias integrais"),
            ("Critério de escolha",
             "Primeira ocorrência na ordem original da fonte"),
            ("Justificativa",
             "Registros iguais; ausência de data de atualização"),
            ("Registros antes do tratamento", len(dados)),
            ("Registros esperados após tratamento",
             len(dados) - excedentes),
            ("Verificação planejada",
             "Preservar todos os identificadores distintos"),
            ("Referência metodológica", "Aula 2, páginas 11 e 14"),
        ],
        columns=["aspecto", "registro"],
    )