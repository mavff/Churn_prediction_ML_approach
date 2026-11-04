from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from preparacao_dados import validar_estrutura_visao
from preparacao_dados.diagnosticos.numericos import identificar_violacoes_numericas
from preparacao_dados.tratamentos.numericos import normalizar_valores_numericos, verificar_normalizacao_numerica


class TestDicionarioNumerico(unittest.TestCase):
    def setUp(self) -> None:
        self.dados = pd.DataFrame({
            "id_cliente": [f"C{i}" for i in range(12)],
            "data_corte": ["21/09/2026"] * 12,
            "tempo_cliente_meses": [0, 120, 121, -1, 1.5, "12", 2, 2, 2, 2, 2, 2],
            "mensalidade_rs": [10, 500, -88, 9999, " NA ", "100.50", np.inf, True, 0, -85, "erro", None],
            "chamados_suporte": [0, 50, 51, -1, 0.5, "2", None, 3, 0, 4, 5, 6],
            "atrasos_6m": [0, 6, 99, -1, 2.5, "3", None, 2, 0, 0, 1, 2],
            "fibra_optica": [0, 1, 2, -1, 0.5, "1", None, 0, 0, 1, True, 0],
            "debito_automatico": [1, 0, 2, -1, 1.5, "0", None, 1, 0, 0, 1, 0],
            "tipo_contrato": ["Mensal"] * 12,
            "forma_pagamento": ["Pix"] * 12,
            "churn": [0, 1] * 6,
        }, index=list(range(0, 24, 2)))

    def test_limites_invalidos_ausencias_e_conversoes_sem_imputacao(self) -> None:
        original = self.dados.copy(deep=True)
        validar_estrutura_visao(self.dados)
        avaliacoes = identificar_violacoes_numericas(self.dados)
        tratados = normalizar_valores_numericos(self.dados, avaliacoes)
        resultado = verificar_normalizacao_numerica(self.dados, tratados, avaliacoes, Path("fonte.xlsx"))
        self.assertEqual(tratados.loc[[0, 2], "mensalidade_rs"].tolist(), [10, 500])
        self.assertTrue(tratados.loc[[4, 6, 8, 12, 14, 16, 18, 20, 22], "mensalidade_rs"].isna().all())
        self.assertEqual(tratados.loc[10, "mensalidade_rs"], 100.5)
        self.assertEqual(tratados.loc[10, "atrasos_6m"], 3)
        self.assertEqual(tratados.loc[10, "fibra_optica"], 1)
        self.assertTrue(tratados.loc[[4, 6, 8], "tempo_cliente_meses"].isna().all())
        self.assertTrue(tratados.loc[[4, 6, 8, 12], "atrasos_6m"].isna().all())
        self.assertTrue(tratados.loc[[4, 6, 8, 12, 20], "fibra_optica"].isna().all())
        # A mensalidade zero é inválida, enquanto zero em contagens e indicadores continua válido.
        self.assertEqual(tratados.loc[16, "chamados_suporte"], 0)
        self.assertEqual(tratados.loc[16, "atrasos_6m"], 0)
        self.assertEqual(tratados.loc[16, "fibra_optica"], 0)
        evidencia = resultado["evidencias"]
        caso = evidencia.loc[evidencia["campo"].eq("mensalidade_rs") & evidencia["linha_excel"].eq(6)].iloc[0]
        self.assertEqual(caso["valor_antes"], -88)
        self.assertTrue(pd.isna(caso["valor_depois"]))
        self.assertEqual(caso["situacao"], "fora_faixa")
        pd.testing.assert_frame_equal(self.dados, original)
        pd.testing.assert_series_equal(tratados["churn"], original["churn"])

    def test_normalizacao_repetida_preserva_resultado(self) -> None:
        primeiro = normalizar_valores_numericos(self.dados, identificar_violacoes_numericas(self.dados))
        segundo = normalizar_valores_numericos(primeiro, identificar_violacoes_numericas(primeiro))
        pd.testing.assert_frame_equal(primeiro, segundo)

    def test_rejeita_resultado_corrompido_e_diagnostico_desatualizado(self) -> None:
        avaliacoes = identificar_violacoes_numericas(self.dados)
        tratados = normalizar_valores_numericos(self.dados, avaliacoes)
        for campo, indice, valor in [("churn", 0, 1), ("mensalidade_rs", 4, 100), ("chamados_suporte", 0, pd.NA)]:
            corrompidos = tratados.copy()
            corrompidos.loc[indice, campo] = valor
            with self.assertRaises(ValueError):
                verificar_normalizacao_numerica(self.dados, corrompidos, avaliacoes, Path("fonte.xlsx"))
        atualizados = self.dados.copy()
        atualizados.loc[0, "mensalidade_rs"] = 20
        with self.assertRaisesRegex(ValueError, "mudou depois"):
            normalizar_valores_numericos(atualizados, avaliacoes)

    def test_estrutura_bloqueia_alvo_colunas_e_chaves_invalidas(self) -> None:
        for valor in [pd.NA, 2, "1"]:
            corrompidos = self.dados.copy()
            if isinstance(valor, str):
                corrompidos["churn"] = corrompidos["churn"].astype(object)
            corrompidos.loc[0, "churn"] = valor
            with self.assertRaisesRegex(ValueError, "Churn"):
                validar_estrutura_visao(corrompidos)
        with self.assertRaisesRegex(ValueError, "colunas ausentes"):
            validar_estrutura_visao(self.dados.drop(columns="mensalidade_rs"))
        duplicados = self.dados.copy()
        duplicados.loc[2, "id_cliente"] = duplicados.loc[0, "id_cliente"]
        with self.assertRaisesRegex(ValueError, "uma linha por cliente"):
            validar_estrutura_visao(duplicados)
