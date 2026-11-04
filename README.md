# Preparação de dados de churn

Miniprojeto de preparação de dados para uso posterior em aprendizagem supervisionada e não supervisionada. A metodologia toma como referência as Aulas 1, 2 e 3 disponibilizadas pelo professor.

A versão atual lê a fonte, diagnostica os identificadores e as datas, remove cópias integrais e padroniza as datas de aquisição. Gera bases tratadas e um relatório de auditoria. **A preparação para modelagem ainda está em andamento.**

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
5. Verificar a deduplicação, salvar a base 01 e atualizar o relatório.
6. Diagnosticar formatos de datas e comparar chamados e cancelamentos com a aquisição da mesma linha da fonte.
7. Padronizar as aquisições escritas em `AAAA-MM-DD` para `DD/MM/AAAA`.
8. Verificar a preservação das datas e dos demais campos.
9. Salvar a base 02 e a auditoria antes/depois da padronização.
10. Apresentar a estrutura da base resultante no terminal.

Cada execução começa pela fonte original. Os tratamentos serão encadeados em memória: a próxima etapa receberá o `DataFrame` retornado pela anterior. A base Excel gerada serve como saída para conferência e não precisa ser relida entre funções.

## Diagnósticos e tratamentos realizados

### T01: remoção de cópias integrais

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

### T02: padronização das datas de aquisição

O diagnóstico interpreta explicitamente `DD/MM/AAAA` e `AAAA-MM-DD`. Em `data_chamado`, separa as datas informadas por vírgulas para examinar cada uma. Espaços externos são desconsiderados somente na interpretação; os valores originais continuam disponíveis nas evidências.

Foram identificadas 15 aquisições em `AAAA-MM-DD`. Eram datas válidas em uma representação alternativa. A decisão do projeto foi padronizá-las em `DD/MM/AAAA`, por exemplo:

```text
2024-08-21 -> 21/08/2024
```

O tratamento altera somente essas representações textuais de aquisição. As demais datas já estavam no padrão adotado. Não há mudança do dia, mês ou ano, nem preenchimento de valores ausentes.

| Indicador | Antes do T02 | Depois do T02 |
| --- | ---: | ---: |
| Registros | 5.000 | 5.000 |
| Identificadores distintos | 5.000 | 5.000 |
| Aquisições em formato ISO | 15 | 0 |
| Células alteradas nesta etapa | 0 | 15 |

A verificação exige os mesmos índices e colunas, preservação dos demais campos, equivalência das datas e representação final em `DD/MM/AAAA`. A auditoria registra cada valor antes e depois. Aquisições ausentes ou não interpretáveis interrompem essa etapa para investigação.

O diagnóstico temporal é calculado **antes do T02**: por isso, `02_resumo_datas` registra as 15 representações ISO na entrada. `T02_indicadores` comprova a passagem de 15 para zero na saída.

### Consistência cronológica: diagnosticada, com tratamento pendente

| Ocorrência sinalizada | Datas envolvidas | Clientes afetados |
| --- | ---: | ---: |
| Chamado anterior à aquisição | 52 | 33 |
| Cancelamento anterior à aquisição | 10 | 10 |

As comparações usam a aquisição da mesma linha da fonte. Datas no mesmo dia não são classificadas como anteriores. Datas sem referência interpretável são contabilizadas como não comparáveis, sem serem consideradas conformes.

Esses alertas exigem investigar a origem dos dados e possíveis reativações ou diferenças de significado entre os campos. A padronização de formato não resolve a cronologia. Nenhuma dessas ocorrências foi corrigida ou excluída automaticamente, e os grupos de clientes podem se sobrepor.

## Arquivos gerados

| Arquivo | Conteúdo |
| --- | --- |
| `dados/tratados/01_base_churn_sem_duplicatas.xlsx` | Base após o primeiro tratamento, na aba `base_tratada` |
| `dados/tratados/02_base_churn_datas_padronizadas.xlsx` | Base após T01 e T02, na aba `base_tratada`; saída atual para conferência |
| `relatorios/diagnostico_preparacao.xlsx` | Diagnósticos, evidências, decisões e auditorias dos tratamentos |

O relatório contém as seguintes abas:

| Aba | Conteúdo |
| --- | --- |
| `01_diagnostico_identificadores` | Cinco indicadores estruturais calculados sobre a fonte original |
| `01_evidencias_identificadores` | Os 40 registros associados aos identificadores repetidos |
| `01_conclusoes_identificadores` | Regra de referência, conclusões, justificativa e tratamento aprovado |
| `T01_indicadores` | Indicadores medidos antes e depois da deduplicação |
| `T01_registros_removidos` | As 20 ocorrências removidas, vinculadas às ocorrências mantidas |
| `02_resumo_datas` | Presença, formatos e intervalos das datas antes do T02 |
| `02_datas_nao_interpretadas` | Valores que não puderam ser interpretados nos dois formatos aceitos; vazia na fonte atual |
| `02_resumo_cronologia` | Quantidades comparáveis e alertas de eventos anteriores à aquisição |
| `02_inconsistencias_temporais` | Evidências das ocorrências cronológicas, com decisões pendentes |
| `T02_indicadores` | Indicadores medidos antes e depois da padronização |
| `T02_alteracoes_datas` | As 15 alterações, com cliente, campo, linha da fonte e valores antes/depois |

A auditoria do T01 registra `arquivo_origem`, `linha_excel_removida`, `linha_excel_mantida` e as colunas originais. A do T02 registra `arquivo_origem`, `linha_excel`, `id_cliente`, `campo`, `valor_antes` e `valor_depois`. As linhas Excel referem-se à fonte, considerando o cabeçalho na linha 1.

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
│   ├── diagnosticar_datas.py
│   ├── diagnosticar_cronologia.py
│   ├── diagnosticar_identificadores.py
│   ├── detalhar_identificadores_repetidos.py
│   ├── montar_conclusoes_identificadores.py
│   └── registrar_diagnostico_identificadores.py
└── tratamentos/
    ├── __init__.py
    ├── identificar_duplicatas_excedentes.py
    ├── remover_duplicatas_integrais.py
    ├── verificar_remocao_duplicatas.py
    ├── preparar_base_sem_duplicatas.py
    ├── padronizar_datas_aquisicao.py
    ├── verificar_padronizacao_datas_aquisicao.py
    └── preparar_base_com_datas_padronizadas.py
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
| `diagnosticar_datas.py` | Interpretar as datas uma vez, produzir seu perfil e encaminhá-las à checagem cronológica |
| `diagnosticar_cronologia.py` | Comparar as datas interpretadas com a aquisição e produzir resumo e evidências |
| `detalhar_identificadores_repetidos.py` | Selecionar as evidências e identificar repetições integrais |
| `montar_conclusoes_identificadores.py` | Organizar as conclusões e a decisão aprovada |
| `registrar_diagnostico_identificadores.py` | Coordenar o diagnóstico e seu registro no relatório |
| `identificar_duplicatas_excedentes.py` | Relacionar cada cópia excedente à ocorrência mantida |
| `remover_duplicatas_integrais.py` | Aplicar a transformação e devolver uma nova base |
| `verificar_remocao_duplicatas.py` | Verificar a transformação e produzir indicadores antes/depois |
| `preparar_base_sem_duplicatas.py` | Coordenar identificação, transformação, verificação e exportações; retornar a base tratada |
| `padronizar_datas_aquisicao.py` | Transformar aquisições ISO em texto `DD/MM/AAAA` numa cópia da base |
| `verificar_padronizacao_datas_aquisicao.py` | Verificar a transformação e produzir indicadores e log das células alteradas |
| `preparar_base_com_datas_padronizadas.py` | Coordenar o T02, verificar antes de exportar e retornar sua base resultante |
| `exportar_relatorio_excel.py` | Exportar tabelas para abas identificadas e preservar as demais abas |
| `exportar_base_excel.py` | Adaptar a exportação de uma base para a aba `base_tratada`, reutilizando o escritor Excel |
| `tests/` | Manter os testes automatizados separados do fluxo da aplicação |

## Como rodar os testes

Na raiz do projeto, com o ambiente virtual ativo:

```bash
python -m unittest discover -s tests -v
```

O teste automatizado versionado atual cobre a deduplicação: preservação da fonte, remoção somente de cópias integrais, manutenção de registros com mesmo ID e conteúdo diferente, indicadores e rejeição de alterações indevidas nas linhas mantidas. Ele usa `unittest`, incluído no Python.

Os dois tratamentos também executam verificações de integridade durante `python main.py`, antes das exportações. Ampliar os testes automatizados versionados para padronização de datas e cronologia é uma pendência.

## Pendências e cuidados metodológicos

Os dois tratamentos foram aplicados após diagnóstico e aprovação das regras. São operações estruturais fixas, sem parâmetros estatísticos aprendidos. Os demais diagnósticos e tratamentos serão desenvolvidos incrementalmente.

- **Unidade de análise:** a unidade prevista é uma fotografia de cliente em uma data de corte. A visão analítica ainda precisa ser construída e validada.
- **Protocolo temporal:** o horizonte inicial é de 60 dias. As datas de corte e cobertura do acompanhamento da VF2 continuam pendentes. As candidatas didáticas são 21/09/2026 e 21/11/2026; elas distam 61 dias e exigem uma convenção explícita para a janela de 60 dias.
- **Disponibilidade dos atributos:** confirmar a que fotografia os valores se referem e usar somente informações disponíveis até o corte.
- **Alvo:** ainda não foi criado. Ausência de data de cancelamento, sozinha, não autoriza atribuir `churn = 0`.
- **Avaliação:** definir o isolamento temporal e por cliente antes da EDA que orientará tratamentos. Estatísticas e transformações aprendidas serão ajustadas somente no treino.
- **Cronologia:** decidir como tratar os 52 chamados e 10 cancelamentos anteriores à aquisição, a partir das evidências registradas e do significado dos campos.
- **Qualidade e EDA:** complementar as regras de validação, diagnosticar ausências, tipos, domínios, categorias e outras inconsistências; depois estudar distribuições e relações no treino.
- **Próximos tratamentos:** decidir e implementar cada transformação com verificação e rastreabilidade, recebendo a base resultante da anterior.
- **Modelagem futura:** preparar representações adequadas a cada tarefa. Churn e informações derivadas do desfecho não serão atributos do agrupamento não supervisionado.
- **Entrega final:** gerar a base preparada e o relatório consolidado. Exportações completas de bases intermediárias serão opcionais.

Nenhum modelo foi treinado nesta etapa. A base após T02 representa dois tratamentos concluídos. A visão analítica, o alvo e a preparação para aprendizagem de máquina ainda precisam ser concluídos.
