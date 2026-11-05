from pathlib import Path

import pandas as pd

from preparacao_dados.diagnosticos.categorias import identificar_categorias_fora_padrao
from preparacao_dados.diagnosticos.numericos import identificar_violacoes_numericas
from preparacao_dados.divisao.separar_atributos_alvo import separar_atributos_alvo
from preparacao_dados.fluxos.consolidar_diagnosticos_conjuntos import consolidar_diagnosticos_conjuntos
from preparacao_dados.tratamentos.categorias import padronizar_categorias, verificar_padronizacao_categorias
from preparacao_dados.tratamentos.numericos import normalizar_valores_numericos, verificar_normalizacao_numerica


def preparar_conjuntos(
    conjuntos: dict[str, pd.DataFrame],
    caminho_origem: Path,
) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    """Aplica regras fixas a cada conjunto e separa atributos, alvo e metadados."""
    preparados = {}
    diagnosticos = {}
    for nome, dados in conjuntos.items():
        resultados = {}
        categorias = identificar_categorias_fora_padrao(dados)
        tratados = padronizar_categorias(dados, categorias)
        resultados["09_categorias"] = {
            **verificar_padronizacao_categorias(dados, tratados, categorias, caminho_origem), "saida": tratados,
        }
        numericos = identificar_violacoes_numericas(tratados)
        depois = normalizar_valores_numericos(tratados, numericos)
        resultados["10_numericos"] = {
            **verificar_normalizacao_numerica(tratados, depois, numericos, caminho_origem), "saida": depois,
        }
        # O ajuste estatístico futuro receberá apenas preparados["treino"]["X"].
        preparados[nome] = separar_atributos_alvo(depois)
        diagnosticos[nome] = resultados
    return preparados, consolidar_diagnosticos_conjuntos(diagnosticos)
