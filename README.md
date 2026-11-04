# Preparação de dados de churn

Miniprojeto de preparação de dados para uso posterior em aprendizagem supervisionada e não supervisionada. A metodologia toma como referência as Aulas 1, 2 e 3 disponibilizadas pelo professor.

A versão atual lê a fonte, diagnostica os identificadores, remove cópias integrais e gera uma base tratada com relatório de auditoria. **A preparação para modelagem ainda está em andamento.**

## Como rodar

O ambiente utilizado foi Python 3.12.3 no Linux. As dependências estão fixadas em `requirements.txt`.

Na raiz do projeto, crie e ative o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows com PowerShell, os comandos equivalentes são:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências e rode o programa:

```bash
python -m pip install -r requirements.txt
python main.py
```

A fonte esperada é `dados/base_churn_5000_VF2_aluno.xlsx`. O leitor verifica a existência do arquivo e exige uma única aba. Os caminhos dos arquivos são resolvidos a partir da localização de `main.py`.

O programa cria automaticamente as pastas e os arquivos de saída. Ao final, o terminal apresenta as dimensões e os nomes das colunas da base tratada: nesta fonte, **5.000 registros e 10 colunas**.

## Fluxo implementado

1. Ler a base original.
2. Produzir o diagnóstico dos identificadores, as evidências e as conclusões.
3. Identificar as cópias integrais excedentes e suas respectivas ocorrências mantidas.
4. Remover essas cópias, mantendo a primeira ocorrência na ordem da fonte.
5. Verificar o resultado antes de exportar.
6. Salvar a base tratada e atualizar o relatório.
7. Apresentar a estrutura da base resultante no terminal.

Cada execução começa pela fonte original. Os tratamentos serão encadeados em memória: a próxima etapa receberá o `DataFrame` retornado pela anterior. A base Excel gerada serve como saída para conferência e não precisa ser relida entre funções.

## Diagnóstico e tratamento realizados

O diagnóstico considera identificadores nulos, vazios ou formados somente por espaços como ausentes. Outros marcadores textuais, como `NA`, ainda dependem de avaliação de domínio. As comparações de repetição usam os valores como foram lidos, sem normalização prévia.

Foram encontrados 5.000 identificadores distintos, nenhum ausente pelo critério acima e 20 identificadores presentes em duas linhas cada. Os 20 pares tinham valores iguais nas dez colunas da fonte.

O primeiro tratamento remove somente **cópias integrais**. Compartilhar um identificador, mas ter outro conteúdo diferente, não é motivo suficiente para remoção.

| Indicador | Antes | Depois |
| --- | ---: | ---: |
| Registros | 5.020 | 5.000 |
| Identificadores distintos | 5.000 | 5.000 |
| Cópias integrais excedentes | 20 | 0 |

A primeira ocorrência foi escolhida como critério determinístico: os pares são iguais e a fonte não apresenta uma data de atualização que permita estabelecer qual registro é mais recente. Essa ressalva acompanha a orientação de consolidação discutida na Aula 2.

A verificação interrompe o fluxo se houver alteração das colunas, quantidade incorreta de registros, cópias integrais restantes, mudança no conjunto de identificadores ou alteração do conteúdo das linhas mantidas. Os índices da leitura original são preservados em memória para apoiar a rastreabilidade.

## Arquivos gerados

| Arquivo | Conteúdo |
| --- | --- |
| `dados/tratados/01_base_churn_sem_duplicatas.xlsx` | Base após o primeiro tratamento, na aba `base_tratada` |
| `relatorios/diagnostico_preparacao.xlsx` | Diagnóstico, evidências, decisões e auditoria do tratamento |

O relatório contém as seguintes abas:

| Aba | Conteúdo |
| --- | --- |
| `01_diagnostico_identificadores` | Cinco indicadores estruturais calculados sobre a fonte original |
| `01_evidencias_identificadores` | Os 40 registros associados aos identificadores repetidos |
| `01_conclusoes_identificadores` | Regra de referência, conclusões, justificativa e tratamento aprovado |
| `T01_indicadores` | Indicadores medidos antes e depois da deduplicação |
| `T01_registros_removidos` | As 20 ocorrências removidas, vinculadas às ocorrências mantidas |

A auditoria registra `arquivo_origem`, `linha_excel_removida`, `linha_excel_mantida` e as colunas originais. As linhas Excel referem-se à fonte, considerando o cabeçalho na linha 1.

As reexecuções atualizam os mesmos arquivos e substituem as abas informadas, preservando as demais. A fonte original é mantida intacta. As saídas geradas ficam fora do Git e podem ser recriadas com `python main.py`.

## Organização do código

```text
main.py
preparacao_dados/
├── __init__.py
├── leitura_dados.py
├── apresentar_estrutura_base.py
├── exportar_relatorio_excel.py
├── exportar_base_excel.py
├── diagnosticos/
│   ├── __init__.py
│   ├── diagnosticar_identificadores.py
│   ├── detalhar_identificadores_repetidos.py
│   ├── montar_conclusoes_identificadores.py
│   └── registrar_diagnostico_identificadores.py
└── tratamentos/
    ├── __init__.py
    ├── identificar_duplicatas_excedentes.py
    ├── remover_duplicatas_integrais.py
    ├── verificar_remocao_duplicatas.py
    └── preparar_base_sem_duplicatas.py
dados/
├── base_churn_5000_VF2_aluno.xlsx
└── tratados/                         # gerada pelo programa
relatorios/                          # gerada pelo programa
tests/
requirements.txt
.gitignore
README.md
```

Cada arquivo Python de implementação contém uma função. Os arquivos `__init__.py` identificam os pacotes e podem permanecer vazios.

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Configurar os caminhos e orquestrar o fluxo |
| `leitura_dados.py` | Ler a fonte pela função `ler_base_excel` |
| `apresentar_estrutura_base.py` | Apresentar dimensões e nomes das colunas |
| `diagnosticar_identificadores.py` | Quantificar ausências e repetições de identificadores |
| `detalhar_identificadores_repetidos.py` | Selecionar as evidências e identificar repetições integrais |
| `montar_conclusoes_identificadores.py` | Organizar as conclusões e a decisão aprovada |
| `registrar_diagnostico_identificadores.py` | Coordenar o diagnóstico e seu registro no relatório |
| `identificar_duplicatas_excedentes.py` | Relacionar cada cópia excedente à ocorrência mantida |
| `remover_duplicatas_integrais.py` | Aplicar a transformação e devolver uma nova base |
| `verificar_remocao_duplicatas.py` | Verificar a transformação e produzir indicadores antes/depois |
| `preparar_base_sem_duplicatas.py` | Coordenar identificação, transformação, verificação e exportações; retornar a base tratada |
| `exportar_relatorio_excel.py` | Exportar tabelas para abas identificadas e preservar as demais abas |
| `exportar_base_excel.py` | Adaptar a exportação de uma base para a aba `base_tratada`, reutilizando o escritor Excel |
| `tests/` | Manter os testes automatizados separados do fluxo da aplicação |

## Como rodar os testes

Na raiz do projeto, com o ambiente virtual ativo:

```bash
python -m unittest discover -s tests -v
```

O teste atual usa dados pequenos e controlados para verificar a preservação da fonte, a remoção somente de cópias integrais, a manutenção de registros com mesmo ID e conteúdo diferente, os indicadores e a rejeição de alterações indevidas nas linhas mantidas. O teste usa `unittest`, incluído no Python.

## Pendências e cuidados metodológicos

O primeiro tratamento foi antecipado após o diagnóstico e a aprovação da regra. Os demais diagnósticos e tratamentos serão desenvolvidos incrementalmente.

- **Unidade de análise:** a unidade prevista é uma fotografia de cliente em uma data de corte. A visão analítica ainda precisa ser construída e validada.
- **Protocolo temporal:** o horizonte inicial é de 60 dias. As datas de corte e cobertura do acompanhamento da VF2 continuam pendentes. As candidatas didáticas são 21/09/2026 e 21/11/2026; elas distam 61 dias e exigem uma convenção explícita para a janela de 60 dias.
- **Disponibilidade dos atributos:** confirmar a que fotografia os valores se referem e usar somente informações disponíveis até o corte.
- **Alvo:** ainda não foi criado. Ausência de data de cancelamento, sozinha, não autoriza atribuir `churn = 0`.
- **Avaliação:** definir o isolamento temporal e por cliente antes da EDA que orientará tratamentos. Estatísticas e transformações aprendidas serão ajustadas somente no treino.
- **Qualidade e EDA:** diagnosticar datas, múltiplas datas em `data_chamado`, ausências, tipos, domínios, categorias e consistência; depois estudar distribuições e relações no treino.
- **Próximos tratamentos:** decidir e implementar cada transformação com verificação e rastreabilidade, recebendo a base resultante da anterior.
- **Modelagem futura:** preparar representações adequadas a cada tarefa. Churn e informações derivadas do desfecho não serão atributos do agrupamento não supervisionado.
- **Entrega final:** gerar a base preparada e o relatório consolidado. Exportações completas de bases intermediárias serão opcionais.

Nenhum modelo foi treinado nesta etapa. A base sem duplicatas representa o primeiro tratamento concluído, e não a conclusão da preparação para aprendizagem de máquina.
