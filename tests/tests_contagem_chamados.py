from pathlib import Path
import unittest

import pandas as pd

from preparacao_dados import definir_protocolo_temporal
from preparacao_dados.diagnosticos.datas import interpretar_datas, identificar_eventos_anteriores_aquisicao
from preparacao_dados.diagnosticos.datas.identificar_contagem_chamados import identificar_contagem_chamados
from preparacao_dados.tratamentos.chamados import filtrar_chamados_anteriores_aquisicao
from preparacao_dados.tratamentos.chamados.substituir_datas_por_contagem_chamados import substituir_datas_por_contagem_chamados
from preparacao_dados.tratamentos.chamados.verificar_contagem_chamados import verificar_contagem_chamados


class TestContagemChamados(unittest.TestCase):
    def setUp(self) -> None:
        dados = pd.DataFrame({
            "id_cliente": ["C1", "C2", "C3", "C4", "C5"],
            "data_aquisicao_cliente": ["01/01/2026"] * 5,
            "data_chamado": [
                "23/06/2026, 24/06/2026, 24/06/2026, 21/09/2026, 22/09/2026, 01/01/2025",
                "", "05/01/2019", "05/01/2019, 01/09/2026", "22/09/2026",
            ],
            "data_ocorrencia_churn": [""] * 5,
            "churn": [0, 1, 0, 1, 0],
        }, index=[0, 2, 4, 6, 8])
        self.protocolo = definir_protocolo_temporal()
        self.datas = interpretar_datas(dados)
        self.excluidos = identificar_eventos_anteriores_aquisicao(self.datas, "data_chamado")
        self.dados = filtrar_chamados_anteriores_aquisicao(dados, self.excluidos)

    def test_contagem_temporal_preserva_repeticoes_validas_e_distingue_ausencia(self) -> None:
        original = self.dados.copy(deep=True)
        avaliacao = identificar_contagem_chamados(self.dados, self.datas["data_chamado"], self.excluidos, self.protocolo)
        tratados = substituir_datas_por_contagem_chamados(self.dados, avaliacao)
        resultado = verificar_contagem_chamados(self.dados, tratados, avaliacao, Path("fonte.xlsx"))
        # Compara repetição válida, lista parcialmente corrigida e eventos fora da janela.
        self.assertEqual(tratados.loc[[0, 6, 8], "chamados_suporte"].tolist(), [3, 1, 0])
        self.assertTrue(tratados.loc[[2, 4], "chamados_suporte"].isna().all())
        self.assertEqual(avaliacao.loc[2, "situacao"], "campo_originalmente_sem_datas")
        self.assertEqual(avaliacao.loc[4, "situacao"], "campo_esvaziado_pelo_tratamento")
        self.assertEqual(tratados["chamados_suporte"].dtype, pd.Int64Dtype())
        self.assertEqual(resultado["evidencias"]["linha_excel"].tolist(), [2, 4, 6, 8, 10])
        pd.testing.assert_frame_equal(self.dados, original)

    def test_rejeita_alteracao_do_alvo_e_preenchimento_prematuro(self) -> None:
        avaliacao = identificar_contagem_chamados(self.dados, self.datas["data_chamado"], self.excluidos, self.protocolo)
        tratados = substituir_datas_por_contagem_chamados(self.dados, avaliacao)
        corrompidos = tratados.copy()
        corrompidos.loc[0, "churn"] = 1
        with self.assertRaisesRegex(ValueError, "inclusive o alvo"):
            verificar_contagem_chamados(self.dados, corrompidos, avaliacao, Path("fonte.xlsx"))
        corrompidos = tratados.copy()
        corrompidos.loc[2, "chamados_suporte"] = 0
        with self.assertRaisesRegex(ValueError, "difere da identificação"):
            verificar_contagem_chamados(self.dados, corrompidos, avaliacao, Path("fonte.xlsx"))
