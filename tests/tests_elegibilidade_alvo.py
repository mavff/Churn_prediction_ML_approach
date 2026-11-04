from datetime import date
from pathlib import Path
import unittest

import pandas as pd

from preparacao_dados.diagnosticos.datas.interpretar_datas import interpretar_datas
from preparacao_dados.diagnosticos.datas.identificar_elegibilidade_alvo import (
    identificar_elegibilidade_alvo,
)
from preparacao_dados.tratamentos.elegibilidade.construir_base_elegivel_com_alvo import (
    construir_base_elegivel_com_alvo,
)
from preparacao_dados.tratamentos.elegibilidade.verificar_elegibilidade_alvo import (
    verificar_elegibilidade_alvo,
)


class TestElegibilidadeAlvo(unittest.TestCase):
    def setUp(self) -> None:
        self.dados = pd.DataFrame({
            "id_cliente": [f"C{i}" for i in range(1, 11)],
            "data_aquisicao_cliente": [
                "23/07/2026", "24/07/2026", "01/01/2026", "01/01/2026",
                "01/01/2026", "01/01/2026", "01/01/2026", "22/09/2026",
                "01/01/2026", "",
            ],
            "data_ocorrencia_churn": [
                "22/09/2026", "22/09/2026", "20/11/2026", "21/09/2026",
                "21/11/2026", "", "15/12/2026", "", "15/01/2020", "",
            ],
            "mensalidade_rs": list(range(100, 110)),
            "data_chamado": [""] * 10,
        }, index=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18])
        self.datas = interpretar_datas(self.dados)
        self.protocolo = {
            "data_corte": date(2026, 9, 21),
            "fim_janela_alvo": date(2026, 11, 20),
            "fim_acompanhamento": date(2026, 11, 21),
            "historico_minimo_dias": 60,
            "cobertura_completa": True,
        }

    def test_limites_da_elegibilidade_alvo_e_preservacao_da_entrada(self) -> None:
        original = self.dados.copy(deep=True)
        avaliacao = identificar_elegibilidade_alvo(self.dados, self.datas, self.protocolo)
        tratados = construir_base_elegivel_com_alvo(self.dados, avaliacao)
        abas = verificar_elegibilidade_alvo(
            self.dados, tratados, avaliacao, self.datas, self.protocolo, Path("fonte.xlsx"),
        )
        self.assertEqual(tratados["id_cliente"].tolist(), ["C1", "C3", "C5", "C6"])
        self.assertEqual(tratados["churn"].tolist(), [1, 1, 0, 0])
        self.assertEqual(avaliacao.loc[0, "historico_dias"], 60)
        self.assertEqual(avaliacao.loc[2, "historico_dias"], 59)
        self.assertEqual(avaliacao.loc[2, "motivo"], "historico_inferior_ao_minimo")
        self.assertEqual(avaliacao.loc[6, "motivo"], "cancelado_ate_corte")
        self.assertTrue(avaliacao.loc[~avaliacao["elegivel"], "churn"].isna().all())
        self.assertEqual(abas["evidencias"].loc[10, "linha_excel"], 12)
        self.assertEqual(tratados["churn"].dtype, pd.Int64Dtype())
        pd.testing.assert_frame_equal(self.dados, original)

    def test_sem_cobertura_ou_acompanhamento_completo_nao_atribui_zero(self) -> None:
        sem_cobertura = {**self.protocolo, "cobertura_completa": False}
        avaliacao = identificar_elegibilidade_alvo(self.dados, self.datas, sem_cobertura)
        conhecidos = construir_base_elegivel_com_alvo(self.dados, avaliacao)
        self.assertEqual(conhecidos["id_cliente"].tolist(), ["C1", "C3"])
        self.assertTrue(conhecidos["churn"].eq(1).all())
        incompleto = {**self.protocolo, "fim_acompanhamento": date(2026, 11, 1)}
        avaliacao = identificar_elegibilidade_alvo(self.dados, self.datas, incompleto)
        conhecidos = construir_base_elegivel_com_alvo(self.dados, avaliacao)
        self.assertEqual(conhecidos["id_cliente"].tolist(), ["C1"])
        self.assertTrue(conhecidos["churn"].eq(1).all())

    def test_verificacao_rejeita_preditor_alterado_e_rotulo_incorreto(self) -> None:
        avaliacao = identificar_elegibilidade_alvo(self.dados, self.datas, self.protocolo)
        tratados = construir_base_elegivel_com_alvo(self.dados, avaliacao)
        corrompidos = tratados.copy()
        corrompidos.loc[0, "mensalidade_rs"] = 999
        with self.assertRaisesRegex(ValueError, "alterados valores"):
            verificar_elegibilidade_alvo(
                self.dados, corrompidos, avaliacao, self.datas, self.protocolo, Path("fonte.xlsx"),
            )
        corrompidos = tratados.copy()
        avaliacao_errada = avaliacao.copy()
        corrompidos.loc[0, "churn"] = 0
        avaliacao_errada.loc[0, "churn"] = 0
        with self.assertRaisesRegex(ValueError, "janela de cancelamento"):
            verificar_elegibilidade_alvo(
                self.dados, corrompidos, avaliacao_errada, self.datas, self.protocolo, Path("fonte.xlsx"),
            )
