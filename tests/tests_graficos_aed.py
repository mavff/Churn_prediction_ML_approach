from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd

from preparacao_dados.diagnosticos.atributos import identificar_relevancia_redundancia_ruido
from preparacao_dados.exportar_graficos_aed import exportar_graficos_aed
from preparacao_dados.graficos import calcular_information_value

PREDITORES = ["tempo_cliente_meses", "mensalidade_rs", "chamados_suporte", "atrasos_6m",
              "tipo_contrato", "forma_pagamento", "fibra_optica", "debito_automatico"]


class TestGraficosAED(unittest.TestCase):
    def setUp(self) -> None:
        n = 60
        self.treino = pd.DataFrame({
            "id_cliente": [f"C{i:03}" for i in range(n)],
            "tempo_cliente_meses": pd.array([2 + i for i in range(n)], dtype="Int64"),
            "mensalidade_rs": pd.array([50.0 + i for i in range(n)], dtype="Float64"),
            "chamados_suporte": pd.array([i % 5 for i in range(n)], dtype="Int64"),
            # Na classe que cancela, atrasos fica constante: o KDE dessa classe é pulado sem erro.
            "atrasos_6m": pd.array([i % 3 for i in range(n)], dtype="Int64"),
            "tipo_contrato": pd.array([["Mensal", "Anual", "Bienal"][i % 3] for i in range(n)], dtype="string"),
            "forma_pagamento": pd.array([["Boleto", "Cartão", "Pix", "Pix"][i % 4] for i in range(n)], dtype="string"),
            "fibra_optica": pd.array([i % 2 for i in range(n)], dtype="Int64"),
            "debito_automatico": pd.array([int(i % 4 == 0) for i in range(n)], dtype="Int64"),
            "churn": pd.array([int(i % 3 == 0) for i in range(n)], dtype="Int64"),
        })
        # Antes da imputação, 15 de 60 chamados (25%) estão ausentes e passam do limiar de 20%.
        antes = self.treino.copy()
        antes.loc[:14, "chamados_suporte"] = pd.NA
        antes.loc[[20, 21], "mensalidade_rs"] = pd.NA
        registros = lambda antes_n, depois_n: {"resumo": pd.DataFrame([("Registros", antes_n, depois_n)], columns=["indicador", "antes", "depois"])}
        self.resultados = {
            "01_duplicatas": registros(70, 68),
            "04_cancelamentos": registros(68, 66),
            "05_elegibilidade_alvo": registros(66, 60),
            "08_divisao": {"saida": {"treino": self.treino, "validacao": self.treino.iloc[:20], "teste": self.treino.iloc[20:40]}},
            "10_numericos": {"saida": {"treino": antes, "validacao": antes.iloc[:20], "teste": antes.iloc[20:40]}},
            "12_atributos": {"evidencias": identificar_relevancia_redundancia_ruido(self.treino[PREDITORES], self.treino["churn"], 0.05, 0.8)},
        }
        self.protocolos = {"imputacao": {"limiar_alerta_ausencia": 0.2}, "atributos": {"limiar_irrelevancia": 0.05}}

    def test_recria_a_pasta_com_os_doze_graficos_numerados(self) -> None:
        original = self.treino.copy(deep=True)
        with TemporaryDirectory() as pasta:
            fonte = Path(pasta) / "fonte.xlsx"
            destino = Path(pasta) / "graficos"
            destino.mkdir()
            (destino / "correlacoes.png").write_text("versão antiga")
            exportar_graficos_aed(self.treino, self.resultados, self.protocolos, destino, fonte)
            gerados = sorted(p.name for p in destino.iterdir())
            self.assertEqual(gerados, [
                "01_funil_registros.png", "02_ausencias.png", "03_churn_por_chamados.png", "04_distribuicoes.png",
                "05_violinos.png", "06_kde.png", "07_correlacoes.png", "08_mensalidade_por_fibra.png",
                "09_ranking_associacao.png", "10_churn_por_categoria.png", "11_churn_tempo_contrato.png",
                "12_mapa_tempo_chamados.png",
            ])
            self.assertTrue(all((destino / nome).stat().st_size > 0 for nome in gerados))
        pd.testing.assert_frame_equal(self.treino, original)

    def test_rejeita_treino_com_ausencias(self) -> None:
        self.treino.loc[0, "mensalidade_rs"] = pd.NA
        with TemporaryDirectory() as pasta, self.assertRaisesRegex(ValueError, "imputado"):
            exportar_graficos_aed(self.treino, self.resultados, self.protocolos, Path(pasta) / "graficos", Path(pasta) / "fonte.xlsx")

    def test_information_value_separa_atributo_forte_de_irrelevante(self) -> None:
        n = 300
        y = pd.Series([i % 2 for i in range(n)], name="churn")
        X = pd.DataFrame({
            # Contrato quase determinado pelo alvo; forma de pagamento com a mesma taxa em todas as categorias.
            "tipo_contrato": pd.array(["Mensal" if (c or i % 10 == 0) else "Bienal" for i, c in enumerate(y)], dtype="string"),
            "forma_pagamento": pd.array([["Boleto", "Cartão", "Pix"][(i // 2) % 3] for i in range(n)], dtype="string"),
            "tempo_cliente_meses": pd.array([10 + 20 * (1 - c) + i % 7 for i, c in enumerate(y)], dtype="Int64"),
        })
        iv = calcular_information_value(X, y).set_index("campo")["information_value"]
        self.assertGreater(iv["tipo_contrato"], 0.3)
        self.assertGreater(iv["tempo_cliente_meses"], 0.3)
        self.assertLess(iv["forma_pagamento"], 0.02)
        self.assertEqual(iv.index[0] in {"tipo_contrato", "tempo_cliente_meses"}, True)
