from pathlib import Path
import unittest

import pandas as pd

from preparacao_dados.diagnosticos.identificadores import identificar_duplicatas_excedentes
from preparacao_dados.tratamentos.duplicatas import remover_duplicatas_integrais, verificar_remocao_duplicatas


class TestRemocaoDuplicatas(unittest.TestCase):
    def test_remocao_integral_com_preservacao_da_fonte(self) -> None:
        dados = pd.DataFrame({"id_cliente": ["C1", "C1", "C1", "C2"], "mensalidade_rs": [100, 100, 120, 80]})
        original = dados.copy(deep=True)
        casos = identificar_duplicatas_excedentes(dados, Path("fonte.xlsx"))
        tratados = remover_duplicatas_integrais(dados, casos)
        resultado = verificar_remocao_duplicatas(dados, tratados, casos)
        pd.testing.assert_frame_equal(dados, original)
        pd.testing.assert_frame_equal(tratados, dados.iloc[[0, 2, 3]])
        self.assertEqual(resultado["resumo"][["antes", "depois"]].values.tolist(), [[4, 3], [2, 2], [1, 0], [0, 0]])
        corrompidos = tratados.copy()
        corrompidos.loc[2, "mensalidade_rs"] = 999
        with self.assertRaisesRegex(ValueError, "diferem das linhas"):
            verificar_remocao_duplicatas(dados, corrompidos, casos)
