from pathlib import Path

from preparacao_dados import definir_protocolo_atributos, definir_protocolo_temporal, ler_base_excel
from preparacao_dados.divisao import definir_protocolo_divisao, dividir_conjuntos
from preparacao_dados.fluxos import (
    construir_visao_analitica, preparar_conjuntos, imputar_conjuntos,
    selecionar_atributos, exportar_resultados,
)
from preparacao_dados.imputacao import definir_protocolo_imputacao


def main() -> None:
    pasta = Path(__file__).resolve().parent
    origem = pasta / "dados" / "base_churn_5000_VF2_aluno.xlsx"
    protocolo = definir_protocolo_temporal()
    protocolo_divisao = definir_protocolo_divisao()
    protocolo_imputacao = definir_protocolo_imputacao()
    protocolo_atributos = definir_protocolo_atributos()
    salvar_intermediarias = False
    dados = ler_base_excel(origem)

    # 1. Consolidar a população, o alvo e os atributos temporais.
    intermediarios = pasta / "dados" / "tratados" / "intermediarios" if salvar_intermediarias else None
    visao, diagnosticos = construir_visao_analitica(dados, origem, protocolo, intermediarios)

    # 2. Isolar os clientes antes dos tratamentos de qualidade.
    conjuntos, diagnosticos["10_divisao"] = dividir_conjuntos(visao, protocolo_divisao, origem)

    # 3. Aplicar regras fixas em cada conjunto e separar X, y e metadados.
    preparados, qualidade = preparar_conjuntos(conjuntos, origem)
    diagnosticos.update(qualidade)

    # 4. Aprender a imputação somente no treino e aplicá-la aos três conjuntos.
    preparados, imputacao = imputar_conjuntos(preparados, protocolo_imputacao, origem)
    diagnosticos.update(imputacao)

    # 5. Explorar o treino e retirar dos três conjuntos os atributos aprovados como irrelevantes.
    preparados, atributos = selecionar_atributos(preparados, protocolo_atributos)
    diagnosticos.update(atributos)

    # 6. Registrar bases, diagnóstico e gráficos usando os exportadores existentes.
    exportar_resultados(
        preparados, diagnosticos, protocolo, protocolo_divisao, protocolo_imputacao, protocolo_atributos, pasta,
        salvar_conjuntos=True, salvar_base_completa=True,
    )


if __name__ == "__main__":
    main()
