import pandas as pd

from preparacao_dados.codificacao import ajustar_codificacao, aplicar_codificacao, verificar_codificacao


def codificar_conjuntos(
    preparados: dict[str, dict[str, object]],
    protocolo: dict[str, object],
) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    """Ajusta one-hot e escalas somente no treino e monta as bases de modelagem dos três conjuntos."""
    escalas = [chave.removeprefix("escala_") for chave in protocolo if chave.startswith("escala_")]
    # Um ajuste por escala, sempre no treino; validação e teste recebem somente transform.
    ajustes = {escala: ajustar_codificacao(preparados["treino"]["X"], protocolo, escala) for escala in escalas}
    codificados = {}
    for nome, partes in preparados.items():
        # Identificador e alvo ficam nas pontas para conferência; não são atributos de modelagem.
        modelagem = {
            escala: pd.concat([partes["metadados"][["id_cliente"]], aplicar_codificacao(partes["X"], ajuste), partes["y"]], axis=1)
            for escala, ajuste in ajustes.items()
        }
        codificados[nome] = {**partes, "modelagem": modelagem}
    resultado = verificar_codificacao(preparados, codificados, ajustes, protocolo)
    saida = {f"{escala}_{nome}": partes["modelagem"][escala] for escala in escalas for nome, partes in codificados.items()}
    return codificados, {"14_codificacao": {**resultado, "saida": saida}}
