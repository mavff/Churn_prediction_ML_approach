from pathlib import Path

import pandas as pd


pasta_projeto = Path(__file__).resolve().parent

caminho_base = (
    pasta_projeto
    / "dados"
    / "base_churn_5000_VF2_aluno.xlsx"
)

if not caminho_base.is_file():
    raise FileNotFoundError(f"Arquivo não encontrado: {caminho_base}")

with pd.ExcelFile(caminho_base, engine="openpyxl") as arquivo:
    abas = arquivo.sheet_names

    if len(abas) != 1:
        raise ValueError(
            f"Esperávamos uma única aba, mas encontramos: {abas}. "
            "É necessário escolher qual aba será utilizada."
        )

    nome_aba = abas[0]

    dados = pd.read_excel(
        arquivo,
        sheet_name=nome_aba,
        dtype=object,
        keep_default_na=False,
    )

print("Arquivo lido:", caminho_base.name)
print("Aba lida:", nome_aba)

print("\nQuantidade de registros:", dados.shape[0])
print("Quantidade de colunas:", dados.shape[1])

print("\nNomes das colunas:")
print(dados.columns.tolist())

print("\nPrimeiros cinco registros:")
print(dados.head())