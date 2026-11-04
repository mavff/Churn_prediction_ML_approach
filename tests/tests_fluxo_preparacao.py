import unittest
from unittest.mock import patch

import pandas as pd

import main


class TestFluxoPreparacao(unittest.TestCase):
    def test_fluxo_reproduzivel_relatorio_compacto_e_fonte_preservada(self) -> None:
        fonte = pd.DataFrame({
            "id_cliente": ["C1", "C1", "C2", "C3"],
            "data_aquisicao_cliente": ["2026-01-01", "2026-01-01", "01/01/2026", "01/01/2026"],
            "mensalidade_rs": [100, 100, 120, 150],
            "data_chamado": ["15/12/2025, 01/09/2026", "15/12/2025, 01/09/2026", "", ""],
            "data_ocorrencia_churn": ["", "", "15/01/2020", "01/10/2026"],
        })
        original = fonte.copy(deep=True)
        finais = []
        with patch.object(main, "ler_base_excel", return_value=fonte), \
             patch.object(main, "exportar_base_excel") as bases, \
             patch.object(main, "exportar_relatorio_excel") as relatorios, \
             patch.object(main, "apresentar_estrutura_base", side_effect=lambda df: finais.append(df.copy(deep=True))):
            main.main()
            main.main()
        pd.testing.assert_frame_equal(fonte, original)
        pd.testing.assert_frame_equal(finais[0], finais[1])
        self.assertEqual(finais[0]["id_cliente"].tolist(), ["C1", "C3"])
        self.assertEqual(finais[0]["chamados_excluidos_por_cronologia"].tolist(), [1, 0])
        self.assertNotIn("cancelamento_inconsistente", finais[0].columns)
        self.assertEqual(finais[0]["churn"].tolist(), [0, 1])
        self.assertEqual(finais[0].loc[0, "chamados_suporte"], 1)
        self.assertTrue(pd.isna(finais[0].loc[3, "chamados_suporte"]))
        self.assertNotIn("data_chamado", finais[0].columns)
        abas = relatorios.call_args.args[0]
        self.assertEqual(list(abas), ["00_resumo", "00_protocolo", "01_duplicatas", "02_datas", "03_chamados", "04_cancelamentos", "05_elegibilidade_alvo", "06_contagem_chamados"])
        self.assertEqual(len(abas["03_chamados"]), 1)
        self.assertTrue(relatorios.call_args.kwargs["substituir_arquivo"])
        habilitadas = [c for c in bases.call_args_list if len(c.args) < 3 or c.args[2]]
        self.assertEqual(len(habilitadas), 2)  # Uma base final por execução.
