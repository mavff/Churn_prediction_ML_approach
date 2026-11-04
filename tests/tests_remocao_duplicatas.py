import unittest

import pandas as pd

from preparacao_dados.tratamentos.duplicatas.remover_duplicatas_integrais import (
    remover_duplicatas_integrais,
)
from preparacao_dados.tratamentos.duplicatas.verificar_remocao_duplicatas import (
    verificar_remocao_duplicatas,
)


class TestRemocaoDuplicatas(unittest.TestCase):
    def test_remocao_integral_com_preservacao_da_fonte(self) -> None:
        originais = pd.DataFrame(
            {
                "id_cliente": ["C001", "C001", "C001", "C002"],
                "mensalidade_rs": [100, 100, 120, 80],
            }
        )
        copia_original = originais.copy(deep=True)

        tratados = remover_duplicatas_integrais(originais)
        indicadores = verificar_remocao_duplicatas(originais, tratados)

        pd.testing.assert_frame_equal(originais, copia_original)
        pd.testing.assert_frame_equal(
            tratados,
            originais.iloc[[0, 2, 3]],
        )

        self.assertEqual(
            indicadores[["antes", "depois"]].to_numpy().tolist(),
            [[4, 3], [2, 2], [1, 0]],
        )

        corrompidos = tratados.copy()
        corrompidos.loc[2, "mensalidade_rs"] = 999

        with self.assertRaisesRegex(ValueError, "diferem das linhas da fonte"):
            verificar_remocao_duplicatas(originais, corrompidos)