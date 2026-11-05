from pathlib import Path

from preparacao_dados import definir_protocolo_atributos, definir_protocolo_temporal, ler_base_excel
from preparacao_dados.codificacao import definir_protocolo_codificacao
from preparacao_dados.divisao import definir_protocolo_divisao, dividir_conjuntos
from preparacao_dados.fluxos import (
    construir_visao_analitica, preparar_conjuntos, imputar_conjuntos,
    selecionar_atributos, codificar_conjuntos, exportar_resultados,
)
from preparacao_dados.imputacao import definir_protocolo_imputacao


def main() -> None:
    pasta = Path(__file__).resolve().parent
    origem = pasta / "dados" / "base_churn_5000_VF2_aluno.xlsx"
    protocolo = definir_protocolo_temporal()
    protocolo_divisao = definir_protocolo_divisao()
    protocolo_imputacao = definir_protocolo_imputacao()
    protocolo_atributos = definir_protocolo_atributos()
    protocolo_codificacao = definir_protocolo_codificacao()
    dados = ler_base_excel(origem)

    # 1. Consolidar a população, o alvo e os atributos temporais (etapas 01 a 07).
    visao, diagnosticos = construir_visao_analitica(dados, origem, protocolo)

    # 2. Isolar os clientes antes dos tratamentos de qualidade (etapa 08).
    conjuntos, diagnosticos["08_divisao"] = dividir_conjuntos(visao, protocolo_divisao, origem)

    # 3. Aplicar regras fixas em cada conjunto e separar X, y e metadados (etapas 09 e 10).
    preparados, qualidade = preparar_conjuntos(conjuntos, origem)
    diagnosticos.update(qualidade)

    # 4. Aprender a imputação somente no treino e aplicá-la aos três conjuntos (etapa 11).
    preparados, imputacao = imputar_conjuntos(preparados, protocolo_imputacao, origem)
    diagnosticos.update(imputacao)

    # 5. Explorar o treino e retirar dos três conjuntos os atributos aprovados como irrelevantes (etapas 12 e 13).
    preparados, atributos = selecionar_atributos(preparados, protocolo_atributos)
    diagnosticos.update(atributos)

    # 6. Aprender one-hot e escalas somente no treino e montar as bases de modelagem (etapa 14).
    preparados, codificacao = codificar_conjuntos(preparados, protocolo_codificacao)
    diagnosticos.update(codificacao)

    # 7. Recriar dados/tratados e registrar relatório e gráficos usando os exportadores existentes.
    exportar_resultados(
        preparados, diagnosticos, protocolo,
        {"divisao": protocolo_divisao, "imputacao": protocolo_imputacao,
         "atributos": protocolo_atributos, "codificacao": protocolo_codificacao},
        pasta, origem, salvar_etapas=True,
    )


if __name__ == "__main__":
    main()
