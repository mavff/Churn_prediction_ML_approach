from pathlib import Path
import unittest

import pandas as pd

from preparacao_dados.diagnosticos.datas import interpretar_datas, identificar_eventos_anteriores_aquisicao
from preparacao_dados.tratamentos.cancelamentos import (
    remover_registros_com_cancelamento_inconsistente, verificar_exclusao_cancelamentos_inconsistentes,
)


class TestExclusaoCancelamentos(unittest.TestCase):
    def setUp(self) -> None:
        self.dados = pd.DataFrame({
            "id_cliente": ["C1", "C2", "C3"],
            "data_aquisicao_cliente": ["01/01/2026"] * 3,
            "data_chamado": [""] * 3,
            "data_ocorrencia_churn": ["15/01/2020", "", "15/01/2020"],
        }, index=[0, 3, 8])
        datas = interpretar_datas(self.dados)
        self.casos = identificar_eventos_anteriores_aquisicao(datas, "data_ocorrencia_churn")

    def test_exclusao_direta_rastreavel_sem_esvaziar_as_datas(self) -> None:
        original = self.dados.copy(deep=True)
        tratados = remover_registros_com_cancelamento_inconsistente(self.dados, self.casos)
        resultado = verificar_exclusao_cancelamentos_inconsistentes(self.dados, tratados, self.casos, Path("fonte.xlsx"))
        pd.testing.assert_frame_equal(self.dados, original)
        pd.testing.assert_frame_equal(tratados, self.dados.loc[[3]])
        self.assertEqual(resultado["evidencias"]["linha_excel"].tolist(), [2, 10])
        self.assertEqual(resultado["evidencias"]["data_ocorrencia_churn"].tolist(), ["15/01/2020"] * 2)
        self.assertNotIn("cancelamento_inconsistente", tratados.columns)

    def test_rejeita_remocao_adicional_ou_alteracao_de_cliente_valido(self) -> None:
        tratados = remover_registros_com_cancelamento_inconsistente(self.dados, self.casos)
        corrompidos = tratados.copy()
        corrompidos.loc[3, "data_chamado"] = "01/09/2026"
        for incorretos in (tratados.iloc[:0], corrompidos):
            with self.assertRaisesRegex(ValueError, "somente os registros identificados"):
                verificar_exclusao_cancelamentos_inconsistentes(self.dados, incorretos, self.casos, Path("fonte.xlsx"))
