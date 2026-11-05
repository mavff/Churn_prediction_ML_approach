import shutil
from pathlib import Path


def limpar_pasta_saidas(pasta_saidas: Path, caminho_origem: Path) -> None:
    """Apaga as saídas reproduzíveis da execução anterior, sem nunca tocar na fonte."""
    # Tudo o que é apagado é regerado a partir da fonte; por isso ela não pode estar dentro da pasta.
    if caminho_origem.resolve().is_relative_to(pasta_saidas.resolve()):
        raise ValueError("A fonte está dentro da pasta de saídas; a limpeza foi interrompida.")
    if pasta_saidas.exists():
        shutil.rmtree(pasta_saidas)
    pasta_saidas.mkdir(parents=True)
