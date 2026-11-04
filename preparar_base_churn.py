from pathlib import Path

from preparacao_dados.fluxo_preparacao_base import (
    gerar_diagnostico_inicial,
)
from preparacao_dados.leitura_base_excel import (
    carregar_base_excel,
)


if __name__ == "__main__":
    pasta_projeto = Path(__file__).resolve().parent

    caminho_relatorio = gerar_diagnostico_inicial(
        pasta_projeto=pasta_projeto,
        leitor_base=carregar_base_excel,
    )

    print("Diagnóstico salvo em:", caminho_relatorio)