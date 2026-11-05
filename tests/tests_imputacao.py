from pathlib import Path
import unittest

import pandas as pd

from preparacao_dados.fluxos import imputar_conjuntos
from preparacao_dados.imputacao import ajustar_imputacao, aplicar_imputacao, definir_protocolo_imputacao


def montar_conjunto(indices: list[int], **valores: list[object]) -> dict[str, object]:
    """Monta X, y e metadados com os tipos produzidos pela preparação dos conjuntos."""
    n = len(indices)
    padrao = {
        "tempo_cliente_meses": [12] * n, "mensalidade_rs": [80.0] * n, "chamados_suporte": [1] * n,
        "atrasos_6m": [0] * n, "tipo_contrato": ["Anual"] * n, "forma_pagamento": ["Boleto"] * n,
        "fibra_optica": [0] * n, "debito_automatico": [1] * n,
    }
    padrao.update(valores)
    tipos = {"mensalidade_rs": "Float64", "tipo_contrato": "string", "forma_pagamento": "string"}
    X = pd.DataFrame({campo: pd.array(lista, dtype=tipos.get(campo, "Int64")) for campo, lista in padrao.items()}, index=indices)
    metadados = pd.DataFrame({"id_cliente": [f"C{i:03}" for i in indices]}, index=indices)
    y = pd.Series(pd.array([i % 2 for i in indices], dtype="Int64"), index=indices, name="churn")
    return {"X": X, "y": y, "metadados": metadados, "ordem_colunas": [*X.columns, "churn", "id_cliente"]}


class TestImputacao(unittest.TestCase):
    def setUp(self) -> None:
        self.preparados = {
            "treino": montar_conjunto(
                [0, 2, 4, 6, 8],
                tempo_cliente_meses=[10, 20, 30, 40, 50],
                mensalidade_rs=[50.0, 60.0, None, 100.0, 70.0],
                chamados_suporte=[3, None, 5, None, 1],
                atrasos_6m=[0, 1, 1, None, 2],
                tipo_contrato=["Mensal", "Anual", "Mensal", None, "Bienal"],
                forma_pagamento=["Pix", "Pix", None, "Boleto", "Cartão"],
                fibra_optica=[1, 1, 0, 1, 0],
                debito_automatico=[0, 0, 1, 0, 1],
            ),
            "validacao": montar_conjunto([1, 3], mensalidade_rs=[None, 500.0], chamados_suporte=[None, 2], tipo_contrato=[None, "Bienal"]),
            "teste": montar_conjunto([5, 7], mensalidade_rs=[None, 10.0], atrasos_6m=[None, 6], forma_pagamento=[None, "Boleto"]),
        }
        self.protocolo = definir_protocolo_imputacao()
        self.origem = Path("fonte.xlsx")

    def test_ajuste_no_treino_e_aplicado_aos_tres_conjuntos(self) -> None:
        originais = {nome: partes["X"].copy(deep=True) for nome, partes in self.preparados.items()}
        imputados, diagnostico = imputar_conjuntos(self.preparados, self.protocolo, self.origem)
        treino = imputados["treino"]["X"]
        # Mediana de 50, 60, 70 e 100; moda Mensal e Pix; chamados ausentes viram zero, não a mediana 3.
        self.assertEqual(treino.loc[4, "mensalidade_rs"], 65.0)
        self.assertEqual(treino.loc[[2, 6], "chamados_suporte"].tolist(), [0, 0])
        self.assertEqual(treino.loc[6, "atrasos_6m"], 1)
        self.assertEqual(treino.loc[6, "tipo_contrato"], "Mensal")
        self.assertEqual(treino.loc[4, "forma_pagamento"], "Pix")
        self.assertEqual(imputados["validacao"]["X"].loc[1, "mensalidade_rs"], 65.0)
        self.assertEqual(imputados["validacao"]["X"].loc[1, "tipo_contrato"], "Mensal")
        self.assertEqual(imputados["teste"]["X"].loc[5, "atrasos_6m"], 1)
        self.assertEqual(imputados["teste"]["X"].loc[5, "forma_pagamento"], "Pix")
        for nome, partes in imputados.items():
            X = partes["X"]
            self.assertFalse(X.isna().any().any())
            pd.testing.assert_series_equal(X.dtypes, originais[nome].dtypes)
            observados = originais[nome].notna()
            pd.testing.assert_frame_equal(X.where(observados), originais[nome].where(observados))
            pd.testing.assert_series_equal(partes["y"], self.preparados[nome]["y"])
            pd.testing.assert_frame_equal(partes["metadados"], self.preparados[nome]["metadados"])
            pd.testing.assert_frame_equal(self.preparados[nome]["X"], originais[nome])
        evidencias = diagnostico["11_imputacao"]["evidencias"]
        self.assertEqual(len(evidencias), sum(int(x.isna().sum().sum()) for x in originais.values()))
        self.assertEqual(set(evidencias["conjunto"]), {"treino", "validacao", "teste"})
        caso = evidencias.loc[evidencias["linha_excel"].eq(3) & evidencias["campo"].eq("mensalidade_rs")].iloc[0]
        self.assertEqual((caso["id_cliente"], caso["valor_depois"], caso["estrategia"]), ("C001", 65.0, "mediana do treino"))
        resumo = diagnostico["11_imputacao"]["resumo"].set_index("indicador")
        self.assertEqual(resumo.loc["Ausentes — mensalidade_rs"].tolist(), [3, 0])
        self.assertIn("mensalidade_rs = 65", diagnostico["11_imputacao"]["decisao"])
        # Chamados: 40% no treino e 50% na validação passam do limiar; o teste não tem ausência.
        self.assertEqual(resumo.loc["Conjuntos com ausência acima de 20% — chamados_suporte"].tolist(), [2, 0])
        # Mensalidade com exatamente 20% no treino não dispara; a regra exige passar do limiar.
        treino = evidencias.loc[evidencias["conjunto"].eq("treino")].set_index("campo")
        self.assertTrue(treino.loc["chamados_suporte", "alerta_ausencia"].all())
        self.assertFalse(treino.loc["mensalidade_rs", "alerta_ausencia"])
        self.assertAlmostEqual(treino.loc["mensalidade_rs", "taxa_ausencia_campo"], 0.2)

    def test_dados_de_avaliacao_nao_alteram_o_ajuste(self) -> None:
        imputados, _ = imputar_conjuntos(self.preparados, self.protocolo, self.origem)
        alterados = {nome: {**partes, "X": partes["X"].copy()} for nome, partes in self.preparados.items()}
        alterados["validacao"]["X"]["mensalidade_rs"] = pd.array([None, 10.0], dtype="Float64")
        alterados["teste"]["X"]["tipo_contrato"] = pd.array(["Bienal", "Bienal"], dtype="string")
        novamente, _ = imputar_conjuntos(alterados, self.protocolo, self.origem)
        pd.testing.assert_frame_equal(imputados["treino"]["X"], novamente["treino"]["X"])
        self.assertEqual(novamente["validacao"]["X"].loc[1, "mensalidade_rs"], 65.0)

    def test_rejeita_valor_aprendido_fora_do_dicionario(self) -> None:
        # Mediana de 0 e 1 seria 0,5 atraso: o fluxo para em vez de arredondar silenciosamente.
        X = self.preparados["treino"]["X"].copy()
        X["atrasos_6m"] = pd.array([0, 1, None, None, None], dtype="Int64")
        with self.assertRaisesRegex(ValueError, "atrasos_6m"):
            ajustar_imputacao(X, self.protocolo)
        with self.assertRaisesRegex(ValueError, "oito preditores"):
            ajustar_imputacao(X.drop(columns="fibra_optica"), self.protocolo)

    def test_protocolo_e_aplicacao_rejeitam_entradas_invalidas(self) -> None:
        estrategias = {campo.removeprefix("estrategia_"): valor for campo, valor in self.protocolo.items() if campo.startswith("estrategia_")}
        with self.assertRaises(ValueError):
            definir_protocolo_imputacao({**estrategias, "mensalidade_rs": "media"})
        with self.assertRaises(ValueError):
            definir_protocolo_imputacao({campo: valor for campo, valor in estrategias.items() if campo != "atrasos_6m"})
        ajuste = ajustar_imputacao(self.preparados["treino"]["X"], self.protocolo)
        with self.assertRaisesRegex(ValueError, "diferem"):
            aplicar_imputacao(self.preparados["teste"]["X"].iloc[:, ::-1], ajuste)
