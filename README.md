## Como executar

Na pasta do projeto, crie e ative o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Execute a leitura:

```bash
python leitura_dados.py
```

O script identifica a única aba da planilha e apresenta a quantidade
de registros, os nomes das colunas e as primeiras cinco linhas.

## Etapas concluídas

- Organização inicial do projeto.
- Configuração do ambiente Python.
- Leitura da base Excel e conferência de sua estrutura.