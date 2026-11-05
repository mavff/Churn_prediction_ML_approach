from pathlib import Path

from preparacao_dados.fluxos.consolidar_diagnosticos_conjuntos import consolidar_diagnosticos_conjuntos
from preparacao_dados.imputacao import ajustar_imputacao, aplicar_imputacao, verificar_imputacao


def imputar_conjuntos(
    preparados: dict[str, dict[str, object]],
    protocolo: dict[str, object],
    caminho_origem: Path,
) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    """Ajusta a imputação uma única vez no treino e aplica a mesma transformação aos três conjuntos."""
    # Validação e teste nunca participam do fit; recebem somente transform.
    ajuste = ajustar_imputacao(preparados["treino"]["X"], protocolo)
    imputados = {}
    diagnosticos = {}
    for nome, partes in preparados.items():
        X = aplicar_imputacao(partes["X"], ajuste)
        diagnosticos[nome] = {
            "11_imputacao": verificar_imputacao(
                partes["X"], X, ajuste, partes["metadados"]["id_cliente"], protocolo["limiar_alerta_ausencia"], caminho_origem,
            ),
        }
        # Alvo, metadados e ordem das colunas seguem inalterados ao lado dos preditores imputados.
        imputados[nome] = {**partes, "X": X}
    return imputados, consolidar_diagnosticos_conjuntos(diagnosticos)
