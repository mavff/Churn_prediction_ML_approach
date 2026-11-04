from pathlib import Path
import unittest

import pandas as pd

from preparacao_dados.diagnosticos.categorias import identificar_categorias_fora_padrao
from preparacao_dados.tratamentos.categorias import padronizar_categorias, verificar_padronizacao_categorias


class TestCategorias(unittest.TestCase):
    def setUp(self) -> None:
        # Inclui grafias corrigíveis e casos que precisam permanecer sem alteração.
        self.dados = pd.DataFrame({
            "id_cliente": ["C1", "C2", "C3", "C4", "C5", "C6"],
            "tipo_contrato": [" mensal ", "ANUAL", "Bienal", "", "Trimestral", None],
            "forma_pagamento": ["CARTAO", " PIX ", "Boleto", " ", "Débito", pd.NA],
            "churn": [0, 1, 0, 1, 0, 1],
        }, index=[0, 2, 4, 6, 8, 10])

    def test_de_para_isola_desconhecidos_e_preserva_fonte(self) -> None:
        original = self.dados.copy(deep=True)
        casos = identificar_categorias_fora_padrao(self.dados)
        tratados = padronizar_categorias(self.dados, casos)
        resultado = verificar_padronizacao_categorias(self.dados, tratados, casos, Path("fonte.xlsx"))
        self.assertEqual(tratados.loc[[0, 2, 4], "tipo_contrato"].tolist(), ["Mensal", "Anual", "Bienal"])
        self.assertEqual(tratados.loc[[0, 2, 4], "forma_pagamento"].tolist(), ["Cartão", "Pix", "Boleto"])
        self.assertTrue(tratados.loc[[6, 8, 10], ["tipo_contrato", "forma_pagamento"]].isna().all().all())
        pd.testing.assert_frame_equal(tratados[["id_cliente", "churn"]], original[["id_cliente", "churn"]])
        pd.testing.assert_frame_equal(self.dados, original)
        self.assertEqual(casos["situacao"].value_counts().to_dict(), {"padronizar": 4, "ausente_na_entrada": 4, "categoria_desconhecida": 2})
        self.assertEqual(resultado["evidencias"].loc[0, "linha_excel"], 2)

    def test_reexecucao_nao_produz_novas_correcoes(self) -> None:
        casos = identificar_categorias_fora_padrao(self.dados)
        tratados = padronizar_categorias(self.dados, casos)
        novos_casos = identificar_categorias_fora_padrao(tratados)
        self.assertFalse(novos_casos["situacao"].eq("padronizar").any())
        pd.testing.assert_frame_equal(tratados, padronizar_categorias(tratados, novos_casos))

    def test_marcadores_de_ausencia_sao_distintos_de_categoria_invalida(self) -> None:
        dados = pd.DataFrame({
            "id_cliente": ["C1", "C2", "C3"],
            "tipo_contrato": [" NA ", "N/A", "0"],
            "forma_pagamento": ["null", "None", "NaN"],
        })
        casos = identificar_categorias_fora_padrao(dados)
        tratados = padronizar_categorias(dados, casos)
        self.assertTrue(tratados[["tipo_contrato", "forma_pagamento"]].isna().all().all())
        self.assertEqual(casos["situacao"].value_counts().to_dict(), {"ausente_na_entrada": 5, "categoria_desconhecida": 1})

    def test_verificacao_rejeita_mudanca_do_alvo_ou_imputacao(self) -> None:
        casos = identificar_categorias_fora_padrao(self.dados)
        tratados = padronizar_categorias(self.dados, casos)
        for campo, indice, valor in [("churn", 0, 1), ("tipo_contrato", 6, "Mensal")]:
            corrompidos = tratados.copy()
            corrompidos.loc[indice, campo] = valor
            with self.assertRaisesRegex(ValueError, "células diferentes"):
                verificar_padronizacao_categorias(self.dados, corrompidos, casos, Path("fonte.xlsx"))
