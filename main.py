from pathlib import Path

from apresentar_estrutura_base import apresentar_estrutura_base
from leitura_dados import ler_base_excel


def main() -> None:
    caminho_base = (
        Path(__file__).resolve().parent
        / "dados"
        / "base_churn_5000_VF2_aluno.xlsx"
    )

    dados = ler_base_excel(caminho_base)
    apresentar_estrutura_base(dados)


if __name__ == "__main__":
    main()