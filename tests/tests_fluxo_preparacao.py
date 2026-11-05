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
        # Simula somente as bordas de entrada e saída; toda a preparação, divisão e codificação são reais.
        modulo = "preparacao_dados.fluxos.exportar_resultados"
        with patch.object(main, "ler_base_excel", return_value=fonte), \
             patch(f"{modulo}.limpar_pasta_saidas") as limpeza, \
             patch(f"{modulo}.exportar_base_excel") as bases, \
             patch(f"{modulo}.exportar_relatorio_excel") as arquivos, \
             patch(f"{modulo}.exportar_graficos_aed") as graficos, \
             patch("builtins.print"):
            main.main()
            main.main()
        finais = [c.args[0] for c in bases.call_args_list]
        pd.testing.assert_frame_equal(fonte, original)
        pd.testing.assert_frame_equal(finais[0], finais[1])
        self.assertEqual(len(finais), 2)
        self.assertEqual(bases.call_args.args[1].name, "base_churn_tratada.xlsx")
        self.assertEqual(finais[0]["id_cliente"].tolist(), [f"C{i:03}" for i in range(1, 17)])
        self.assertEqual(finais[0]["churn"].tolist(), [0] * 8 + [1] * 8)
        self.assertEqual(finais[0]["conjunto"].value_counts().to_dict(), {"treino": 8, "validacao": 4, "teste": 4})
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
        # Cada execução limpa a pasta e grava etapas numeradas, bases de modelagem e relatório.
        self.assertEqual(limpeza.call_count, 2)
        caminhos = [c.args[1] for c in arquivos.call_args_list]
        primeira = caminhos[:len(caminhos) // 2]
        etapas = [p.name for p in primeira if p.parent.name == "etapas"]
        self.assertEqual(etapas, [
            "01_duplicatas.xlsx", "02_datas.xlsx", "03_chamados.xlsx", "04_cancelamentos.xlsx", "05_elegibilidade_alvo.xlsx",
            "06_contagem_chamados.xlsx", "07_tempo_cliente.xlsx", "08_divisao.xlsx", "09_categorias.xlsx",
            "10_numericos.xlsx", "11_imputacao.xlsx", "12_atributos.xlsx", "14_codificacao.xlsx",
        ])
        finais_modelagem = {c.args[1].name: c.args[0] for c in arquivos.call_args_list if c.args[1].name.startswith("base_churn_modelagem")}
        self.assertEqual(set(finais_modelagem), {"base_churn_modelagem_padronizada.xlsx", "base_churn_modelagem_minmax.xlsx"})
        modelagem = finais_modelagem["base_churn_modelagem_padronizada.xlsx"]
        self.assertEqual(list(modelagem), ["treino", "validacao", "teste", "colunas"])
        self.assertEqual(list(modelagem["treino"].columns), [
            "id_cliente", "tempo_cliente_meses", "mensalidade_rs", "chamados_suporte", "atrasos_6m",
            "tipo_contrato_Mensal", "tipo_contrato_Anual", "tipo_contrato_Bienal", "fibra_optica", "debito_automatico", "churn",
        ])
        relatorios = [c.args[0] for c in arquivos.call_args_list if c.args[1].name == "diagnostico_preparacao.xlsx"]
        abas = relatorios[-1]
        self.assertEqual(list(abas), [
            "00_resumo", "00_protocolo", "01_duplicatas", "02_datas", "03_chamados", "04_cancelamentos",
            "05_elegibilidade_alvo", "06_contagem_chamados", "07_tempo_cliente", "08_divisao", "09_categorias",
            "10_numericos", "11_imputacao", "12_atributos", "13_descritiva", "14_codificacao",
        ])
        atribuicoes = abas["08_divisao"][["id_cliente", "conjunto"]]
        pd.testing.assert_frame_equal(atribuicoes, relatorios[0]["08_divisao"][["id_cliente", "conjunto"]])
        self.assertEqual(atribuicoes["conjunto"].value_counts().to_dict(), {"treino": 8, "validacao": 4, "teste": 4})
        self.assertIn("conjunto", abas["09_categorias"])
        self.assertIn("conjunto", abas["10_numericos"])
        self.assertIn("conjunto", abas["11_imputacao"])
        parametros = abas["00_protocolo"]["parametro"].tolist()
        self.assertIn("imputacao estrategia chamados suporte", parametros)
        self.assertIn("atributos selecao forma pagamento", parametros)
        self.assertIn("codificacao codificacao tipo contrato", parametros)
        # forma_pagamento sai do X, mas o treino enviado aos gráficos ainda traz todos os preditores.
        treino_grafico = graficos.call_args.args[0]
        self.assertEqual(len(treino_grafico), 8)
        self.assertIn("forma_pagamento", treino_grafico)
        self.assertEqual(graficos.call_count, 2)
