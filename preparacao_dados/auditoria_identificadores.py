from dataclasses import dataclass

import pandas as pd

@dataclass
class ResultadoAuditoriaIdentificadores:
    total_registros: int
    registros_sem_id: int
    ids_distintos: int
    ids_repetidos: int
    registros_com_id_repetido: pd.DataFrame


def auditar_identificadores( dados: pd.DataFrame,) -> ResultadoAuditoriaIdentificadores:
    """Verifica a presença e a repetição dos identificadores."""

    if "id_cliente" not in dados.columns:
        raise ValueError("Coluna obrigatória ausente: id_cliente")

    ids = dados["id_cliente"]

    ids_em_branco = (
        ids.astype("string")
        .str.strip()
        .eq("")
        .fillna(False)
    )

    sem_id = ids.isna() | ids_em_branco

    repetidos = (~sem_id) & ids.duplicated(keep=False)

    return ResultadoAuditoriaIdentificadores(
        total_registros=len(dados),
        registros_sem_id=int(sem_id.sum()),
        ids_distintos=int(ids[~sem_id].nunique()),
        ids_repetidos=int(ids[repetidos].nunique()),
        registros_com_id_repetido=dados.loc[repetidos].copy(),
    )