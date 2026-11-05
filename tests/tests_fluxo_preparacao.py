import unittest
from unittest.mock import patch

import pandas as pd

import main


class TestFluxoPreparacao(unittest.TestCase):
    def test_fluxo_reproduzivel_relatorio_compacto_e_fonte_preservada(self) -> None:
        fonte = pd.DataFrame({
            "id_cliente": [f"C{i:03}" for i in range(1, 17)],
            "data_aquisicao_cliente": ["2026-01-01"] * 16,
            "mensalidade_rs": [100, 9999] + [100] * 14,
            "atrasos_6m": [0, 99] + [0] * 14,
            "fibra_optica": [1] * 16, "debito_automatico": [0] * 16,
            "tipo_contrato": ["mensal"] * 16, "forma_pagamento": ["PIX"] * 16,
            "data_chamado": ["15/12/2025, 01/09/2026"] + [""] * 15,
            "data_ocorrencia_churn": [""] * 8 + ["01/10/2026"] * 8,
        })
        copia = fonte.iloc[[0]].copy()
        inconsistente = fonte.iloc[[0]].assign(id_cliente="C017", data_ocorrencia_churn="15/01/2020")
        recente = fonte.iloc[[0]].assign(id_cliente="C018", data_aquisicao_cliente="01/09/2026", data_chamado="")
        fonte = pd.concat([fonte, copia, inconsistente, recente], ignore_index=True)
        original = fonte.copy(deep=True)
        # Simula somente as bordas de entrada e saída; toda a preparação e divisão são reais.
        with patch.object(main, "ler_base_excel", return_value=fonte), \
             patch("preparacao_dados.fluxos.exportar_resultados.exportar_base_excel") as bases, \
             patch("preparacao_dados.fluxos.exportar_resultados.exportar_relatorio_excel") as relatorios, \
             patch("preparacao_dados.fluxos.exportar_resultados.exportar_graficos_aed") as graficos, \
             patch("builtins.print"):
            main.main()
            main.main()
        finais = [c.args[0] for c in bases.call_args_list]
        pd.testing.assert_frame_equal(fonte, original)
        pd.testing.assert_frame_equal(finais[0], finais[1])
        self.assertEqual(finais[0]["id_cliente"].tolist(), [f"C{i:03}" for i in range(1, 17)])
        self.assertEqual(finais[0]["churn"].tolist(), [0] * 8 + [1] * 8)
        self.assertEqual(finais[0].loc[0, "chamados_excluidos_por_cronologia"], 1)
        self.assertEqual(finais[0].loc[0, "chamados_suporte"], 1)
        # A lista vazia vira zero; os inválidos isolados recebem a mediana aprendida no treino.
        self.assertEqual(finais[0].loc[1, "chamados_suporte"], 0)
        self.assertEqual(finais[0].loc[1, "mensalidade_rs"], 100)
        self.assertEqual(finais[0].loc[1, "atrasos_6m"], 0)
        preditores = ["tempo_cliente_meses", "mensalidade_rs", "chamados_suporte", "atrasos_6m", "tipo_contrato", "forma_pagamento", "fibra_optica", "debito_automatico"]
        self.assertFalse(finais[0][preditores].isna().any().any())
        self.assertEqual(finais[0]["tempo_cliente_meses"].tolist(), [8] * 16)
        self.assertEqual(finais[0]["tipo_contrato"].tolist(), ["Mensal"] * 16)
        self.assertEqual(finais[0]["forma_pagamento"].tolist(), ["Pix"] * 16)
        abas = relatorios.call_args.args[0]
        self.assertEqual(list(abas), ["00_resumo", "00_protocolo", "01_duplicatas", "02_datas", "03_chamados", "04_cancelamentos", "05_elegibilidade_alvo", "06_contagem_chamados", "07_tempo_cliente", "08_categorias", "09_numericos", "10_divisao", "11_imputacao", "12_atributos", "13_descritiva"])
        atribuicoes = abas["10_divisao"][["id_cliente", "conjunto"]]
        anteriores = relatorios.call_args_list[1].args[0]["10_divisao"][["id_cliente", "conjunto"]]
        pd.testing.assert_frame_equal(atribuicoes, anteriores)
        self.assertEqual(atribuicoes["conjunto"].value_counts().to_dict(), {"treino": 8, "validacao": 4, "teste": 4})
        self.assertIn("conjunto", abas["08_categorias"])
        self.assertIn("conjunto", abas["09_numericos"])
        self.assertIn("conjunto", abas["11_imputacao"])
        self.assertIn("imputacao estrategia chamados suporte", abas["00_protocolo"]["parametro"].tolist())
        self.assertIn("atributos selecao forma pagamento", abas["00_protocolo"]["parametro"].tolist())
        # forma_pagamento sai do X, mas o treino enviado aos gráficos ainda traz todos os preditores.
        treino_grafico = graficos.call_args.args[0]
        self.assertEqual(len(treino_grafico), 8)
        self.assertIn("forma_pagamento", treino_grafico)
        self.assertEqual(graficos.call_count, 2)
        self.assertTrue(relatorios.call_args.kwargs["substituir_arquivo"])
        self.assertEqual(len(bases.call_args_list), 2)
