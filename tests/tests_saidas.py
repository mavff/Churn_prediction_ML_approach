from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd

from preparacao_dados.limpar_pasta_saidas import limpar_pasta_saidas
from preparacao_dados.montar_tabelas_etapa import montar_tabelas_etapa


class TestSaidas(unittest.TestCase):
    def test_tabelas_da_etapa_seguem_o_formato_da_saida(self) -> None:
        base = pd.DataFrame({"id_cliente": ["C1"], "churn": [0]})
        self.assertEqual(list(montar_tabelas_etapa(base)), ["base"])
        self.assertEqual(list(montar_tabelas_etapa({"treino": base, "teste": base})), ["treino", "teste"])
        partes = {
            "X": pd.DataFrame({"tempo_cliente_meses": [12]}, index=[4]),
            "y": pd.Series([1], index=[4], name="churn"),
            "metadados": pd.DataFrame({"id_cliente": ["C1"], "forma_pagamento": ["Pix"]}, index=[4]),
            "ordem_colunas": ["id_cliente", "tempo_cliente_meses", "forma_pagamento", "churn"],
        }
        # Depois da separação, a etapa mostra preditores, alvo e metadados, nessa ordem.
        tabela = montar_tabelas_etapa({"treino": partes})["treino"]
        self.assertEqual(list(tabela.columns), ["tempo_cliente_meses", "churn", "id_cliente", "forma_pagamento"])
        self.assertEqual(tabela.index.tolist(), [4])

    def test_limpeza_apaga_saidas_antigas_e_protege_a_fonte(self) -> None:
        with TemporaryDirectory() as pasta:
            dados = Path(pasta) / "dados"
            tratados = dados / "tratados"
            (tratados / "etapas").mkdir(parents=True)
            (tratados / "05_base_antiga.xlsx").write_text("antiga")
            (tratados / "etapas" / "01_duplicatas.xlsx").write_text("antiga")
            fonte = dados / "fonte.xlsx"
            fonte.write_text("fonte")
            limpar_pasta_saidas(tratados, fonte)
            self.assertTrue(tratados.is_dir())
            self.assertEqual(list(tratados.iterdir()), [])
            self.assertEqual(fonte.read_text(), "fonte")
            # Uma fonte dentro da pasta de saídas interrompe a limpeza antes de apagar qualquer arquivo.
            interna = tratados / "fonte.xlsx"
            interna.write_text("fonte")
            with self.assertRaisesRegex(ValueError, "fonte"):
                limpar_pasta_saidas(tratados, interna)
            self.assertTrue(interna.exists())
