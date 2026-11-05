from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd

from preparacao_dados.exportar_graficos_aed import exportar_graficos_aed


class TestGraficosAED(unittest.TestCase):
    def setUp(self) -> None:
        n = 40
        self.treino = pd.DataFrame({
            "id_cliente": [f"C{i:03}" for i in range(n)],
            "tempo_cliente_meses": pd.array([2 + i for i in range(n)], dtype="Int64"),
            "mensalidade_rs": pd.array([50.0 + i for i in range(n)], dtype="Float64"),
            "chamados_suporte": pd.array([i % 5 for i in range(n)], dtype="Int64"),
            "atrasos_6m": pd.array([i % 3 for i in range(n)], dtype="Int64"),
            # Categoria sem clientes no treino deve aparecer identificada, sem quebrar o gráfico.
            "tipo_contrato": pd.array(["Mensal", "Anual"] * (n // 2), dtype="string"),
            "forma_pagamento": pd.array(["Boleto", "Cartão", "Pix", "Pix"] * (n // 4), dtype="string"),
            "fibra_optica": pd.array([i % 2 for i in range(n)], dtype="Int64"),
            "debito_automatico": pd.array([int(i % 4 == 0) for i in range(n)], dtype="Int64"),
            "churn": pd.array([int(i % 3 == 0) for i in range(n)], dtype="Int64"),
        })

    def test_salva_os_tres_graficos_da_aed(self) -> None:
        original = self.treino.copy(deep=True)
        with TemporaryDirectory() as pasta:
            destino = Path(pasta) / "graficos"
            exportar_graficos_aed(self.treino, destino)
            for nome in ("correlacoes.png", "distribuicoes.png", "churn_por_categoria.png"):
                self.assertGreater((destino / nome).stat().st_size, 0)
        pd.testing.assert_frame_equal(self.treino, original)

    def test_rejeita_treino_com_ausencias(self) -> None:
        self.treino.loc[0, "mensalidade_rs"] = pd.NA
        with TemporaryDirectory() as pasta, self.assertRaisesRegex(ValueError, "imputado"):
            exportar_graficos_aed(self.treino, Path(pasta))
