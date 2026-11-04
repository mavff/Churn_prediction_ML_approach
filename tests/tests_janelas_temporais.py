from datetime import date
from pathlib import Path
import unittest

import pandas as pd

from preparacao_dados import definir_protocolo_temporal
from preparacao_dados.diagnosticos.datas import interpretar_datas, identificar_eventos_anteriores_aquisicao
from preparacao_dados.tratamentos.chamados import filtrar_chamados_anteriores_aquisicao, verificar_filtragem_chamados


class TestDatasTemporais(unittest.TestCase):
    def test_iso_e_eventos_da_mesma_linha_da_fonte(self) -> None:
        dados = pd.DataFrame({
            "id_cliente": ["C1"], "data_aquisicao_cliente": ["2026-08-21"],
            "data_chamado": ["20/08/2026, 21/08/2026"], "data_ocorrencia_churn": [""],
        }, index=[7])
        original = dados.copy(deep=True)
        datas = interpretar_datas(dados)
        casos = identificar_eventos_anteriores_aquisicao(datas, "data_chamado")
        self.assertEqual(casos["valor_data"].tolist(), ["20/08/2026"])
        self.assertEqual(casos["linha_excel"].tolist(), [9])
        pd.testing.assert_frame_equal(dados, original)

    def test_janela_historica_e_eventos_futuros_permanecem_distintos(self) -> None:
        dados = pd.DataFrame({
            "id_cliente": ["C1"], "data_aquisicao_cliente": ["01/01/2026"],
            "data_chamado": ["23/06/2026, 24/06/2026, 21/09/2026, 22/09/2026, 20/11/2026, 21/11/2026, 22/11/2026"],
            "data_ocorrencia_churn": [""],
        })
        protocolo = definir_protocolo_temporal()
        self.assertEqual(protocolo["inicio_janela_chamados"], date(2026, 6, 24))
        self.assertEqual(protocolo["fim_janela_alvo"], date(2026, 11, 20))
        datas = interpretar_datas(dados)
        casos = identificar_eventos_anteriores_aquisicao(datas, "data_chamado")
        tratados = filtrar_chamados_anteriores_aquisicao(dados, casos)
        resultado = verificar_filtragem_chamados(dados, tratados, casos, datas["data_chamado"], protocolo, Path("fonte.xlsx"))
        resumo = resultado["resumo"].set_index("indicador")
        self.assertEqual(resumo.loc["Datas na janela histórica", "depois"], 2)
        self.assertEqual(resumo.loc["Datas após o corte", "depois"], 4)
        self.assertEqual(tratados.loc[0, "data_chamado"], dados.loc[0, "data_chamado"])

    def test_data_invalida_nao_vira_conformidade_ou_ausencia(self) -> None:
        dados = pd.DataFrame({
            "id_cliente": ["C1"], "data_aquisicao_cliente": ["31/02/2026"],
            "data_chamado": [""], "data_ocorrencia_churn": [""],
        })
        with self.assertRaisesRegex(ValueError, "Datas não interpretáveis"):
            interpretar_datas(dados)
