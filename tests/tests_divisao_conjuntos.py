from pathlib import Path
import unittest

import pandas as pd

from preparacao_dados.divisao import definir_protocolo_divisao, dividir_conjuntos
from preparacao_dados.divisao.verificar_divisao import verificar_divisao
from preparacao_dados.fluxos import preparar_conjuntos


class TestDivisaoConjuntos(unittest.TestCase):
    def setUp(self) -> None:
        self.visao = pd.DataFrame({
            "id_cliente": [f"C{i:03}" for i in range(100)],
            "data_corte": ["21/09/2026"] * 100,
            "data_aquisicao_cliente": ["21/09/2025"] * 100,
            "data_ocorrencia_churn": [""] * 65 + ["01/10/2026"] * 35,
            "tempo_cliente_meses": [12] * 100, "mensalidade_rs": [100] * 100,
            "chamados_suporte": [1] * 100, "atrasos_6m": [0] * 100,
            "tipo_contrato": ["mensal"] * 100, "forma_pagamento": ["PIX"] * 100,
            "fibra_optica": [1] * 100, "debito_automatico": [0] * 100,
            "chamados_excluidos_por_cronologia": [0] * 100,
            "churn": pd.array([0] * 65 + [1] * 35, dtype="Int64"),
        }, index=list(range(0, 200, 2)))
        self.protocolo = definir_protocolo_divisao()
        self.origem = Path("fonte.xlsx")

    def test_divisao_estratificada_reproduzivel_preserva_clientes_e_linhas(self) -> None:
        original = self.visao.copy(deep=True)
        conjuntos, resultado = dividir_conjuntos(self.visao, self.protocolo, self.origem)
        reordenada = self.visao.sample(frac=1, random_state=7)
        novamente, _ = dividir_conjuntos(reordenada, self.protocolo, self.origem)
        self.assertEqual({k: len(v) for k, v in conjuntos.items()}, {"treino": 50, "validacao": 25, "teste": 25})
        encontrados = set()
        for nome, tabela in conjuntos.items():
            pd.testing.assert_frame_equal(tabela, novamente[nome])
            self.assertFalse(encontrados.intersection(tabela["id_cliente"]))
            encontrados.update(tabela["id_cliente"])
            self.assertLessEqual(abs(int(tabela["churn"].sum()) - len(tabela) * 0.35), 1)
        self.assertEqual(encontrados, set(self.visao["id_cliente"]))
        self.assertEqual(set(resultado["evidencias"]["linha_excel"]), set(self.visao.index + 2))
        pd.testing.assert_frame_equal(self.visao, original)

    def test_verificacao_rejeita_sobreposicao_ou_conteudo_alterado(self) -> None:
        conjuntos, _ = dividir_conjuntos(self.visao, self.protocolo, self.origem)
        repetidos = {nome: tabela.copy() for nome, tabela in conjuntos.items()}
        repetidos["validacao"] = pd.concat([repetidos["validacao"].iloc[1:], repetidos["treino"].iloc[[0]]])
        with self.assertRaisesRegex(ValueError, "mais de um conjunto"):
            verificar_divisao(self.visao, repetidos, self.protocolo, self.origem)
        alterados = {nome: tabela.copy() for nome, tabela in conjuntos.items()}
        indice = alterados["teste"].index[0]
        alterados["teste"].loc[indice, "mensalidade_rs"] = 200
        with self.assertRaisesRegex(ValueError, "Conteúdo"):
            verificar_divisao(self.visao, alterados, self.protocolo, self.origem)

    def test_rejeita_proporcoes_invalidas_e_estratificacao_impossivel(self) -> None:
        with self.assertRaises(ValueError):
            definir_protocolo_divisao(treino=0.5, validacao=0.3, teste=0.3)
        rara = self.visao.copy()
        rara["churn"] = pd.array([0] * 99 + [1], dtype="Int64")
        with self.assertRaisesRegex(ValueError, "Não foi possível estratificar"):
            dividir_conjuntos(rara, self.protocolo, self.origem)

    def test_preparacao_separa_X_y_e_nao_aprende_com_avaliacao(self) -> None:
        conjuntos, _ = dividir_conjuntos(self.visao, self.protocolo, self.origem)
        original = {nome: tabela.copy(deep=True) for nome, tabela in conjuntos.items()}
        preparados, _ = preparar_conjuntos(conjuntos, self.origem)
        for nome, partes in preparados.items():
            self.assertEqual(partes["X"].shape[1], 8)
            self.assertNotIn("churn", partes["X"])
            self.assertNotIn("id_cliente", partes["X"])
            self.assertNotIn("data_ocorrencia_churn", partes["X"])
            pd.testing.assert_series_equal(partes["y"], conjuntos[nome]["churn"])
            pd.testing.assert_frame_equal(conjuntos[nome], original[nome])
        # Uma alteração nos dados de avaliação não pode modificar a preparação do treino.
        alterados = {nome: tabela.copy() for nome, tabela in conjuntos.items()}
        alterados["validacao"]["mensalidade_rs"] = 400
        indice = alterados["teste"].index[0]
        alterados["teste"].loc[indice, "mensalidade_rs"] = 9999
        novamente, _ = preparar_conjuntos(alterados, self.origem)
        pd.testing.assert_frame_equal(preparados["treino"]["X"], novamente["treino"]["X"])
        self.assertTrue(pd.isna(novamente["teste"]["X"].loc[indice, "mensalidade_rs"]))
