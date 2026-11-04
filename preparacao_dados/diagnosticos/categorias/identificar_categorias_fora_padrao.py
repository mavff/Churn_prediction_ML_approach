import pandas as pd

from preparacao_dados.definir_dicionario_dados import definir_dicionario_dados
from preparacao_dados.diagnosticos.identificar_ausencias import identificar_ausencias


def identificar_categorias_fora_padrao(dados: pd.DataFrame) -> pd.DataFrame:
    """Identifica grafias corrigíveis e ausências, isolando categorias desconhecidas."""
    # As categorias permitidas vêm do material, sem aprender um vocabulário com a base.
    dicionario = definir_dicionario_dados()
    evidencias = []
    for campo, regra in dicionario.items():
        if regra["tipo"] != "categoria":
            continue
        mapa = regra["de_para"]
        valores = dados[campo].astype("string")
        # Normaliza a comparação; a saída mantém a grafia canônica, como Cartão.
        chaves = valores.str.strip().str.casefold().str.normalize("NFKD")
        chaves = chaves.str.replace(r"[\u0300-\u036f]", "", regex=True)
        esperados = chaves.map(mapa)
        ausentes = identificar_ausencias(dados[campo])
        conhecidos = esperados.notna()
        iguais = valores.eq(esperados).fillna(False)
        situacao = pd.Series("categoria_desconhecida", index=dados.index)
        situacao.loc[ausentes] = "ausente_na_entrada"
        situacao.loc[conhecidos] = "padronizar"
        # Sem correspondência no mapa, a saída permanece ausente e o original fica na evidência.
        depois = esperados.astype("string")
        tabela = pd.DataFrame({
            "linha_excel": dados.index + 2,
            "id_cliente": dados["id_cliente"],
            "campo": campo,
            "valor_antes": dados[campo],
            "valor_depois": depois,
            "situacao": situacao,
            "regra": "Domínio: " + ", ".join(mapa.values()),
        })
        evidencias.append(tabela.loc[~iguais])
    return pd.concat(evidencias, ignore_index=True)
