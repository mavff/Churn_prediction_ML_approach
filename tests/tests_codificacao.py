import unittest

import numpy as np
import pandas as pd

from preparacao_dados.codificacao import ajustar_codificacao, aplicar_codificacao, definir_protocolo_codificacao, verificar_codificacao
from preparacao_dados.fluxos import codificar_conjuntos


def montar_partes(indices: list[int], **valores: list[object]) -> dict[str, object]:
    """Monta X, y e metadados com os sete preditores selecionados e seus tipos."""
    tipos = {"mensalidade_rs": "Float64", "tipo_contrato": "string"}
    X = pd.DataFrame({campo: pd.array(lista, dtype=tipos.get(campo, "Int64")) for campo, lista in valores.items()}, index=indices)
    y = pd.Series(pd.array([i % 2 for i in indices], dtype="Int64"), index=indices, name="churn")
    metadados = pd.DataFrame({"id_cliente": [f"C{i:03}" for i in indices]}, index=indices)
    return {"X": X, "y": y, "metadados": metadados, "ordem_colunas": ["id_cliente", *X.columns, "churn"]}


class TestCodificacao(unittest.TestCase):
    def setUp(self) -> None:
        self.preparados = {
            "treino": montar_partes(
                [0, 2, 4, 6],
                tempo_cliente_meses=[10, 20, 30, 40], mensalidade_rs=[50.0, 60.0, 70.0, 80.0],
                chamados_suporte=[0, 1, 2, 3], atrasos_6m=[0, 0, 1, 1],
                tipo_contrato=["Mensal", "Anual", "Mensal", "Bienal"], fibra_optica=[1, 0, 1, 0], debito_automatico=[0, 1, 0, 1],
            ),
            # Valores fora da faixa do treino mostram que a escala não é reajustada na avaliação.
            "validacao": montar_partes(
                [1, 3],
                tempo_cliente_meses=[50, 0], mensalidade_rs=[100.0, 40.0], chamados_suporte=[5, 0], atrasos_6m=[2, 0],
                tipo_contrato=["Bienal", "Anual"], fibra_optica=[0, 1], debito_automatico=[1, 0],
            ),
            "teste": montar_partes(
                [5, 7],
                tempo_cliente_meses=[25, 25], mensalidade_rs=[65.0, 65.0], chamados_suporte=[1, 1], atrasos_6m=[0, 1],
                tipo_contrato=["Mensal", "Mensal"], fibra_optica=[1, 1], debito_automatico=[0, 0],
            ),
        }
        self.protocolo = definir_protocolo_codificacao()
        self.escalados = ["tempo_cliente_meses", "mensalidade_rs", "chamados_suporte", "atrasos_6m"]

    def test_escalas_e_one_hot_aprendidos_no_treino(self) -> None:
        originais = {nome: partes["X"].copy(deep=True) for nome, partes in self.preparados.items()}
        codificados, resultado = codificar_conjuntos(self.preparados, self.protocolo)
        colunas = ["id_cliente", *self.escalados, "tipo_contrato_Mensal", "tipo_contrato_Anual", "tipo_contrato_Bienal",
                   "fibra_optica", "debito_automatico", "churn"]
        padronizada = codificados["treino"]["modelagem"]["padronizada"]
        minmax = codificados["treino"]["modelagem"]["minmax"]
        self.assertEqual(list(padronizada.columns), colunas)
        np.testing.assert_allclose(padronizada[self.escalados].mean(), 0, atol=1e-12)
        np.testing.assert_allclose(padronizada[self.escalados].std(ddof=0), 1)
        np.testing.assert_allclose(minmax[self.escalados].min(), 0)
        np.testing.assert_allclose(minmax[self.escalados].max(), 1)
        # Tempo 50 na validação: (50 - 10) / (40 - 10) com mínimo e máximo do treino.
        self.assertAlmostEqual(codificados["validacao"]["modelagem"]["minmax"].loc[1, "tempo_cliente_meses"], 40 / 30)
        validacao = codificados["validacao"]["modelagem"]["padronizada"]
        self.assertEqual(validacao.loc[1, ["tipo_contrato_Mensal", "tipo_contrato_Anual", "tipo_contrato_Bienal"]].tolist(), [0, 0, 1])
        self.assertEqual(validacao["fibra_optica"].tolist(), [0, 1])
        self.assertEqual(validacao["id_cliente"].tolist(), ["C001", "C003"])
        pd.testing.assert_series_equal(validacao["churn"], self.preparados["validacao"]["y"])
        for nome, partes in self.preparados.items():
            pd.testing.assert_frame_equal(partes["X"], originais[nome])
            pd.testing.assert_frame_equal(codificados[nome]["X"], originais[nome])
        colunas_aprendidas = resultado["14_codificacao"]["evidencias"].set_index(["escala", "coluna"])
        self.assertEqual(colunas_aprendidas.loc[("padronizada", "tempo_cliente_meses"), "media_aprendida"], 25)
        self.assertEqual(colunas_aprendidas.loc[("minmax", "mensalidade_rs"), ["minimo_aprendido", "maximo_aprendido"]].tolist(), [50, 80])
        self.assertEqual(colunas_aprendidas.loc[("minmax", "tipo_contrato_Anual"), "transformacao"], "one-hot")
        self.assertEqual(set(resultado["14_codificacao"]["saida"]), {f"{e}_{n}" for e in ("padronizada", "minmax") for n in self.preparados})

    def test_dados_de_avaliacao_nao_alteram_o_ajuste(self) -> None:
        codificados, _ = codificar_conjuntos(self.preparados, self.protocolo)
        alterados = {nome: {**partes, "X": partes["X"].copy()} for nome, partes in self.preparados.items()}
        alterados["validacao"]["X"]["mensalidade_rs"] = pd.array([500.0, 10.0], dtype="Float64")
        novamente, _ = codificar_conjuntos(alterados, self.protocolo)
        for escala in ("padronizada", "minmax"):
            pd.testing.assert_frame_equal(codificados["treino"]["modelagem"][escala], novamente["treino"]["modelagem"][escala])
            pd.testing.assert_frame_equal(codificados["teste"]["modelagem"][escala], novamente["teste"]["modelagem"][escala])

    def test_categoria_nova_vira_zeros_e_entradas_invalidas_sao_rejeitadas(self) -> None:
        ajuste = ajustar_codificacao(self.preparados["treino"]["X"], self.protocolo, "padronizada")
        novo = self.preparados["teste"]["X"].copy()
        novo["tipo_contrato"] = pd.array(["Trimestral", "Mensal"], dtype="string")
        codificado = aplicar_codificacao(novo, ajuste)
        self.assertEqual(codificado.loc[5, ["tipo_contrato_Mensal", "tipo_contrato_Anual", "tipo_contrato_Bienal"]].tolist(), [0, 0, 0])
        with self.assertRaisesRegex(ValueError, "diferem"):
            aplicar_codificacao(novo.iloc[:, ::-1], ajuste)
        with self.assertRaisesRegex(ValueError, "Escala"):
            ajustar_codificacao(self.preparados["treino"]["X"], self.protocolo, "robusta")
        ausente = self.preparados["treino"]["X"].copy()
        ausente.loc[0, "mensalidade_rs"] = pd.NA
        with self.assertRaisesRegex(ValueError, "imputados"):
            ajustar_codificacao(ausente, self.protocolo, "minmax")

    def test_verificacao_bloqueia_escala_ajustada_fora_do_treino(self) -> None:
        # Ajustar na validação vazaria informação da avaliação para a preparação.
        vazado = ajustar_codificacao(self.preparados["validacao"]["X"], self.protocolo, "padronizada")
        codificados = {
            nome: {**partes, "modelagem": {"padronizada": pd.concat([
                partes["metadados"][["id_cliente"]], aplicar_codificacao(partes["X"], vazado), partes["y"],
            ], axis=1)}}
            for nome, partes in self.preparados.items()
        }
        with self.assertRaisesRegex(ValueError, "somente no treino"):
            verificar_codificacao(self.preparados, codificados, {"padronizada": vazado}, self.protocolo)
