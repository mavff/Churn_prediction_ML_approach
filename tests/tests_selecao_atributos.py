import unittest

import pandas as pd

from preparacao_dados import definir_protocolo_atributos
from preparacao_dados.diagnosticos.atributos import identificar_relevancia_redundancia_ruido
from preparacao_dados.fluxos import selecionar_atributos
from preparacao_dados.tratamentos.atributos import verificar_selecao_atributos


def montar_partes(X: pd.DataFrame, y: pd.Series) -> dict[str, object]:
    """Monta X, y e metadados como saem da imputação."""
    metadados = pd.DataFrame({"id_cliente": [f"C{i:03}" for i in X.index]}, index=X.index)
    return {"X": X, "y": y, "metadados": metadados, "ordem_colunas": ["id_cliente", *X.columns, "churn"]}


class TestSelecaoAtributos(unittest.TestCase):
    def setUp(self) -> None:
        indices = range(120)
        churn = [i % 2 for i in indices]
        fibra = [(i // 2) % 2 for i in indices]
        X = pd.DataFrame({
            "tempo_cliente_meses": pd.array([10 + (i % 7) * 5 + 20 * (1 - c) for i, c in zip(indices, churn)], dtype="Int64"),
            # Mensalidade praticamente determinada pela fibra: par redundante.
            "mensalidade_rs": pd.array([60.0 + 40 * f + i % 5 for i, f in zip(indices, fibra)], dtype="Float64"),
            # Um chamado muito acima dos demais deve aparecer como extremo a investigar.
            "chamados_suporte": pd.array([40 if i == 10 else 1 + 2 * c for i, c in zip(indices, churn)], dtype="Int64"),
            "atrasos_6m": pd.array([i % 4 for i in indices], dtype="Int64"),
            "tipo_contrato": pd.array(["Mensal" if c or i % 4 == 0 else "Bienal" for i, c in zip(indices, churn)], dtype="string"),
            # Mesma taxa de churn em cada forma de pagamento: sem relação com o alvo.
            "forma_pagamento": pd.array([["Boleto", "Cartão", "Pix"][i % 3] for i in indices], dtype="string"),
            "fibra_optica": pd.array(fibra, dtype="Int64"),
            "debito_automatico": pd.array([int(i % 5 == 0) for i in indices], dtype="Int64"),
        }, index=[2 * i for i in indices])
        y = pd.Series(pd.array(churn, dtype="Int64"), index=X.index, name="churn")
        # Repete os preditores de um cliente com rótulo oposto: um conflito de rótulo.
        X.iloc[1] = X.iloc[0]
        self.preparados = {
            "treino": montar_partes(X, y),
            "validacao": montar_partes(X.iloc[:6].set_axis(range(1, 12, 2)), y.iloc[:6].set_axis(range(1, 12, 2))),
            "teste": montar_partes(X.iloc[6:12].set_axis(range(13, 24, 2)), y.iloc[6:12].set_axis(range(13, 24, 2))),
        }
        self.protocolo = definir_protocolo_atributos()

    def test_retira_irrelevante_e_mantem_redundantes_nos_tres_conjuntos(self) -> None:
        originais = {nome: partes["X"].copy(deep=True) for nome, partes in self.preparados.items()}
        selecionados, resultados = selecionar_atributos(self.preparados, self.protocolo)
        for nome, partes in selecionados.items():
            self.assertNotIn("forma_pagamento", partes["X"])
            self.assertIn("mensalidade_rs", partes["X"])
            self.assertIn("fibra_optica", partes["X"])
            # A coluna retirada continua disponível, com os mesmos valores, para o benchmark futuro.
            pd.testing.assert_series_equal(partes["metadados"]["forma_pagamento"], originais[nome]["forma_pagamento"])
            pd.testing.assert_frame_equal(self.preparados[nome]["X"], originais[nome])
        avaliacao = resultados["12_atributos"]["evidencias"].set_index("atributo")
        self.assertIn("candidato_redundante", avaliacao.loc["mensalidade_rs", "situacao"])
        self.assertEqual(avaliacao.loc["mensalidade_rs", "atributo_mais_correlacionado"], "fibra_optica")
        self.assertEqual(avaliacao.loc["mensalidade_rs", "decisao"], "mantido; redundância registrada para a modelagem")
        for categoria in ("Boleto", "Cartão", "Pix"):
            self.assertIn("candidato_irrelevante", avaliacao.loc[f"forma_pagamento={categoria}", "situacao"])
            self.assertTrue(avaliacao.loc[f"forma_pagamento={categoria}", "decisao"].startswith("retirado do X"))
        self.assertGreaterEqual(avaliacao.loc["chamados_suporte", "extremos_iqr"], 1)
        self.assertTrue(pd.isna(avaliacao.loc["fibra_optica", "extremos_iqr"]))
        # Bienal e Mensal são complementares, mas pertencem ao mesmo campo e não contam como redundância.
        self.assertNotEqual(avaliacao.loc["tipo_contrato=Mensal", "atributo_mais_correlacionado"], "tipo_contrato=Bienal")
        resumo = resultados["12_atributos"]["resumo"].set_index("indicador")
        self.assertEqual(resumo.loc["Preditores em X — teste"].tolist(), [8, 7])
        # Saem os três indicadores de pagamento; os demais candidatos do exemplo seguem só registrados.
        candidatos = resumo.loc["Atributos candidatos a irrelevantes no X"]
        self.assertEqual(candidatos["antes"] - candidatos["depois"], 3)
        self.assertEqual(resumo.loc["Grupos de preditores iguais com churn diferente", "depois"], 1)

    def test_descritiva_resume_o_treino_por_campo_e_categoria(self) -> None:
        _, resultados = selecionar_atributos(self.preparados, self.protocolo)
        tabela = resultados["13_descritiva"]["evidencias"]
        X, y = self.preparados["treino"]["X"], self.preparados["treino"]["y"]
        mensal = tabela.loc[tabela["campo"].eq("tipo_contrato") & tabela["categoria"].eq("Mensal")].iloc[0]
        self.assertAlmostEqual(mensal["taxa_churn"], y[X["tipo_contrato"].eq("Mensal")].mean())
        self.assertEqual(mensal["clientes"], int(X["tipo_contrato"].eq("Mensal").sum()))
        anual = tabela.loc[tabela["campo"].eq("tipo_contrato") & tabela["categoria"].eq("Anual")].iloc[0]
        self.assertEqual(anual["clientes"], 0)
        chamados = tabela.loc[tabela["campo"].eq("chamados_suporte")].iloc[0]
        self.assertAlmostEqual(chamados["media_churn_1"], X.loc[y.eq(1), "chamados_suporte"].astype(float).mean())
        self.assertTrue(pd.isna(chamados["categoria"]))
        self.assertEqual(set(tabela["campo"]), set(X.columns))

    def test_bloqueia_retirada_sem_evidencia_e_sinalizacao_incoerente(self) -> None:
        decisoes = {campo.removeprefix("selecao_"): valor for campo, valor in self.protocolo.items() if campo.startswith("selecao_")}
        tempo = definir_protocolo_atributos({**decisoes, "tempo_cliente_meses": "retirar"})
        with self.assertRaisesRegex(ValueError, "sem evidência"):
            selecionar_atributos(self.preparados, tempo)
        treino = self.preparados["treino"]
        avaliacao = identificar_relevancia_redundancia_ruido(treino["X"], treino["y"], 0.05, 0.8)
        avaliacao.loc[avaliacao["atributo"].eq("mensalidade_rs"), "situacao"] = "sem_sinalizacao"
        with self.assertRaisesRegex(ValueError, "limiares"):
            verificar_selecao_atributos(self.preparados, self.preparados, avaliacao, self.protocolo)

    def test_exige_treino_imputado_e_protocolo_valido(self) -> None:
        X = self.preparados["treino"]["X"].copy()
        X.loc[0, "mensalidade_rs"] = pd.NA
        with self.assertRaisesRegex(ValueError, "imputados"):
            identificar_relevancia_redundancia_ruido(X, self.preparados["treino"]["y"], 0.05, 0.8)
        decisoes = {campo.removeprefix("selecao_"): valor for campo, valor in self.protocolo.items() if campo.startswith("selecao_")}
        with self.assertRaises(ValueError):
            definir_protocolo_atributos({**decisoes, "forma_pagamento": "talvez"})
        with self.assertRaises(ValueError):
            definir_protocolo_atributos({campo: "retirar" for campo in decisoes})
