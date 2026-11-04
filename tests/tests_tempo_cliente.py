from pathlib import Path
import unittest

import pandas as pd

from preparacao_dados import definir_protocolo_temporal
from preparacao_dados.diagnosticos.datas import interpretar_datas
from preparacao_dados.diagnosticos.datas.identificar_tempo_cliente_meses import identificar_tempo_cliente_meses
from preparacao_dados.tratamentos.tempo_cliente import adicionar_tempo_cliente_meses, verificar_tempo_cliente_meses


class TestTempoCliente(unittest.TestCase):
    def test_meses_completos_preservam_datas_alvo_e_rastreabilidade(self) -> None:
        dados = pd.DataFrame({
            "id_cliente": ["C1", "C2", "C3", "C4"],
            "data_aquisicao_cliente": ["21/09/2025", "22/09/2025", "21/09/2026", "20/12/2025"],
            "data_chamado": [""] * 4,
            "data_ocorrencia_churn": [""] * 4,
            "churn": [0, 1, 0, 1],
        }, index=[0, 2, 5, 8])
        original = dados.copy(deep=True)
        datas = interpretar_datas(dados)
        avaliacao = identificar_tempo_cliente_meses(dados, datas["data_aquisicao_cliente"], definir_protocolo_temporal())
        tratados = adicionar_tempo_cliente_meses(dados, avaliacao)
        resultado = verificar_tempo_cliente_meses(dados, tratados, avaliacao, Path("fonte.xlsx"))
        # Confere o aniversário do contrato, a véspera e uma aquisição no próprio corte.
        self.assertEqual(tratados["tempo_cliente_meses"].tolist(), [12, 11, 0, 9])
        self.assertEqual(tratados["tempo_cliente_meses"].dtype, pd.Int64Dtype())
        self.assertEqual(resultado["evidencias"]["linha_excel"].tolist(), [2, 4, 7, 10])
        pd.testing.assert_frame_equal(tratados[dados.columns], original)
        pd.testing.assert_frame_equal(dados, original)

    def test_rejeita_referencia_futura_e_alteracao_do_alvo(self) -> None:
        dados = pd.DataFrame({
            "id_cliente": ["C1"], "data_aquisicao_cliente": ["22/09/2026"],
            "data_chamado": [""], "data_ocorrencia_churn": [""], "churn": [1],
        })
        datas = interpretar_datas(dados)
        with self.assertRaisesRegex(ValueError, "posterior ao corte"):
            identificar_tempo_cliente_meses(dados, datas["data_aquisicao_cliente"], definir_protocolo_temporal())
        dados.loc[0, "data_aquisicao_cliente"] = "21/09/2025"
        datas = interpretar_datas(dados)
        avaliacao = identificar_tempo_cliente_meses(dados, datas["data_aquisicao_cliente"], definir_protocolo_temporal())
        tratados = adicionar_tempo_cliente_meses(dados, avaliacao)
        tratados.loc[0, "churn"] = 0
        with self.assertRaisesRegex(ValueError, "inclusive o alvo"):
            verificar_tempo_cliente_meses(dados, tratados, avaliacao, Path("fonte.xlsx"))
