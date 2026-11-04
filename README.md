# Preparação de dados de churn

Miniprojeto de preparação de dados para uso posterior em aprendizagem supervisionada e não supervisionada. A metodologia toma como referência as Aulas 1, 2 e 3 disponibilizadas pelo professor.

A versão atual lê a fonte, diagnostica identificadores e datas e aplica quatro tratamentos auditáveis. A preparação para modelagem ainda está em andamento: a base tratada não contém um alvo de churn validado.

## Como rodar

O ambiente utilizado foi Python 3.12.3 no Linux. As dependências estão fixadas em `requirements.txt`.

Na raiz do projeto, crie e ative o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows com PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências e rode o fluxo completo:

```bash
python -m pip install -r requirements.txt
python main.py
```

A fonte esperada é `dados/base_churn_5000_VF2_aluno.xlsx`. O leitor verifica sua existência e exige uma única aba. Os caminhos são resolvidos a partir da localização de `main.py`.

O programa cria automaticamente as pastas de saída. Nesta fonte, o resultado apresentado no terminal tem **5.000 registros e 12 colunas**.

## Fluxo e tratamentos concluídos

Cada execução começa pela fonte original. Os tratamentos recebem em memória o `DataFrame` retornado pela etapa anterior; os arquivos Excel são saídas de conferência e não precisam ser relidos entre etapas.

1. Ler a fonte e registrar o diagnóstico dos identificadores.
2. Aplicar T01: identificar, remover, verificar e auditar cópias integrais excedentes.
3. Registrar o diagnóstico de formatos de datas e da cronologia.
4. Aplicar T02: padronizar datas de aquisição, verificar e auditar o de-para.
5. Aplicar T03: filtrar chamados anteriores à aquisição, verificar e auditar as datas removidas.
6. Aplicar T04: isolar cancelamentos anteriores à aquisição, verificar e auditar a sinalização.
7. Apresentar as dimensões e colunas da base resultante.

| Tratamento | Regra aplicada | Resultado nesta fonte |
| --- | --- | --- |
| T01 — duplicatas | Remover somente cópias iguais nas dez colunas originais, mantendo a primeira ocorrência na ordem da fonte | 5.020 → 5.000 registros; 20 cópias excedentes removidas; 5.000 IDs preservados |
| T02 — datas de aquisição | Converter representações válidas em `AAAA-MM-DD` para `DD/MM/AAAA`, preservando a data | 15 células padronizadas; mesmos 5.000 registros e 10 campos |
| T03 — chamados | Retirar apenas datas de chamados estritamente anteriores à aquisição da mesma linha da fonte | 52 datas retiradas de 33 clientes; 5.000 registros e 11 campos |
| T04 — cancelamentos | Esvaziar a data de cancelamento estritamente anterior à aquisição e sinalizar sua inconsistência | 10 datas isoladas; 5.000 registros e 12 campos |

O diagnóstico considera identificadores nulos, vazios ou compostos somente por espaços como ausentes. Marcadores como `NA` ainda dependem de avaliação de domínio. Foram encontrados 20 IDs em duas linhas cada, com conteúdo integralmente igual; compartilhar um ID com conteúdos diferentes não autoriza remover um registro. Manter a primeira cópia é um critério determinístico: a fonte não oferece data de atualização para escolher a mais recente. Essa ressalva acompanha a discussão da Aula 2.

O diagnóstico de datas aceita explicitamente `DD/MM/AAAA` e `AAAA-MM-DD`; não decide o formato por inferência automática. Aquisições ausentes ou não interpretáveis interrompem a etapa de padronização para investigação. Datas no mesmo dia da aquisição não violam a regra cronológica. Datas sem referência interpretável são contabilizadas como não comparáveis, sem serem consideradas conformes.

As regras de T03 e T04 foram aprovadas como decisões deste projeto. Uma data anterior à aquisição pode decorrer de erro na origem, reativação ou significado diferente dos campos; não inventamos uma data corrigida nem afirmamos qual dessas causas ocorreu. Os valores originais permanecem disponíveis na fonte e na auditoria.

### T03: por que a nova coluna existe

`chamados_excluidos_por_cronologia` registra quantas datas foram excluídas de cada cliente. Os chamados válidos, inclusive no dia da aquisição, são preservados.

Em 17 clientes, todas as datas informadas violavam a regra e o campo ficou vazio. A contagem distingue esses casos dos 1.048 campos originalmente sem chamados. Na saída há 1.065 campos vazios e 8.545 datas informadas, contra 8.597 na entrada. Um campo vazio após exclusão não comprova que o cliente nunca teve chamados.

### T04: por que esvaziar e sinalizar

`cancelamento_inconsistente=True` identifica os dez clientes cuja data foi isolada. Esses clientes permanecem na base com **desfecho desconhecido**. A quantidade de datas de cancelamento em branco passa de 3.218 para 3.228.

O tratamento não cria `churn`, não converte esses casos em `churn = 0` e não interpreta `cancelamento_inconsistente=False` como comprovação de não churn. A sinalização é metadado de qualidade derivado do desfecho e não deverá ser usada como atributo dos modelos supervisionados ou do agrupamento.

## Arquivos gerados

| Arquivo | Conteúdo |
| --- | --- |
| `dados/tratados/01_base_churn_sem_duplicatas.xlsx` | Resultado de T01 |
| `dados/tratados/02_base_churn_datas_padronizadas.xlsx` | Resultado acumulado de T01 + T02 |
| `dados/tratados/03_base_churn_chamados_filtrados.xlsx` | Resultado acumulado de T01 + T02 + T03 |
| `dados/tratados/04_base_churn_cancelamentos_sinalizados.xlsx` | Resultado acumulado dos quatro tratamentos; saída atual para conferência |
| `relatorios/diagnostico_preparacao.xlsx` | Diagnósticos, evidências e auditorias antes/depois |

Cada base é exportada na aba `base_tratada`. Os números dos arquivos indicam a sequência. A próxima transformação receberá a saída de T04 em memória, sem escolher um Excel manualmente.

As reexecuções começam pela fonte, atualizam os mesmos arquivos e substituem as abas informadas, preservando as demais. A fonte é mantida intacta. As saídas ficam fora do Git e podem ser recriadas com `python main.py`. Hoje as quatro bases são exportadas; tornar opcionais as bases intermediárias permanece uma pendência.

## Como ler o relatório

| Aba | Conteúdo |
| --- | --- |
| `01_diagnostico_identificadores` | Cinco indicadores estruturais sobre a fonte original |
| `01_evidencias_identificadores` | Os 40 registros associados aos IDs repetidos |
| `01_conclusoes_identificadores` | Evidências, regra de referência e decisão da deduplicação |
| `T01_indicadores` | Indicadores antes/depois da deduplicação |
| `T01_registros_removidos` | As 20 cópias excedentes, vinculadas às ocorrências mantidas |
| `02_resumo_datas` | Presença, formatos e intervalos das datas após T01 e antes de T02 |
| `02_datas_nao_interpretadas` | Falhas nos formatos aceitos; vazia na fonte atual |
| `02_resumo_cronologia` | Quantidades comparáveis e alertas anteriores a T03 e T04 |
| `02_inconsistencias_temporais` | Uma linha por data inconsistente: 52 de chamados e 10 de cancelamentos |
| `T02_indicadores` | Indicadores antes/depois da padronização |
| `T02_alteracoes_datas` | As 15 células padronizadas, com valores antes/depois |
| `T03_indicadores` | Quantidades de datas, clientes, campos vazios e exclusões antes/depois |
| `T03_datas_excluidas` | As 52 datas retiradas, com listas antes/depois e motivo |
| `T04_indicadores` | Quantidades de cancelamentos inconsistentes, vazios e sinalizações antes/depois |
| `T04_cancelamentos_isolados` | As dez datas isoladas, com valores originais e decisão aplicada |

As abas `02_*` retratam a **entrada dos tratamentos temporais**. Por isso continuam mostrando as 15 aquisições ISO e os alertas cronológicos encontrados. Os textos de proposta e decisão dessa fotografia do diagnóstico também permanecem como foram produzidos. As decisões efetivamente aplicadas e os resultados estão em `T02_*`, `T03_*` e `T04_*`; manter as evidências de entrada não significa que o tratamento falhou.

Na aba de inconsistências, um cliente pode aparecer várias vezes por ter várias datas inválidas. `valor_original` guarda o conteúdo completo da célula, `valor_data` contém a data individual analisada e `data_interpretada` contém sua conversão para comparação. A unidade dessa aba é a ocorrência de inconsistência; a unidade da base tratada continua sendo o registro de cliente.

Os logs incluem o arquivo original e a linha Excel da fonte, com o cabeçalho na linha 1. Os índices originais são preservados em memória para manter esse vínculo. A auditoria de T01 relaciona cada linha removida à mantida; as demais registram o de-para das células ou datas modificadas.

## Organização do código

```text
main.py
preparacao_dados/
├── __init__.py
├── leitura_dados.py
├── apresentar_estrutura_base.py
├── exportar_base_excel.py
├── exportar_relatorio_excel.py
├── diagnosticos/
│   ├── __init__.py
│   ├── identificadores/          # identificação e evidências de IDs
│   └── datas/                    # formatos e cronologia
└── tratamentos/
    ├── __init__.py
    ├── duplicatas/               # T01
    ├── datas_aquisicao/          # T02
    ├── chamados/                 # T03
    └── cancelamentos/            # T04
dados/
├── base_churn_5000_VF2_aluno.xlsx
└── tratados/                    # saídas geradas; fora do Git
relatorios/                     # saídas geradas; fora do Git
tests/
requirements.txt
.gitignore
README.md
```

Cada arquivo Python de implementação contém uma função. As novas subpastas possuem `__init__.py` vazio. Agrupar por assunto facilita encontrar o diagnóstico e o tratamento correspondente; não exige criar novas classes ou padrões.

`main.py` configura os caminhos e encadeia as chamadas. Os módulos compartilhados leem a fonte (`leitura_dados`), apresentam dimensões (`apresentar_estrutura_base`), exportam tabelas preservando as outras abas (`exportar_relatorio_excel`) e adaptam essa exportação para bases na aba `base_tratada` (`exportar_base_excel`).

Dentro dos pacotes abaixo, cada nome de módulo corresponde ao arquivo Python e à função nele definida:

| Pacote | Módulo | Responsabilidade |
| --- | --- | --- |
| `diagnosticos.identificadores` | `diagnosticar_identificadores` | Contar ausências e repetições |
| `diagnosticos.identificadores` | `detalhar_identificadores_repetidos` | Selecionar evidências e marcar repetições integrais |
| `diagnosticos.identificadores` | `montar_conclusoes_identificadores` | Registrar conclusões e decisão aprovada |
| `diagnosticos.identificadores` | `registrar_diagnostico_identificadores` | Coordenar o diagnóstico e sua exportação |
| `diagnosticos.datas` | `diagnosticar_datas` | Interpretar datas, produzir o perfil e encaminhar à checagem cronológica |
| `diagnosticos.datas` | `diagnosticar_cronologia` | Comparar eventos com a aquisição da mesma linha da fonte |
| `tratamentos.duplicatas` | `identificar_duplicatas_excedentes` | Vincular cópias excedentes às ocorrências mantidas |
| `tratamentos.duplicatas` | `remover_duplicatas_integrais` | Aplicar a deduplicação numa cópia |
| `tratamentos.duplicatas` | `verificar_remocao_duplicatas` | Conferir integridade e produzir indicadores |
| `tratamentos.duplicatas` | `preparar_base_sem_duplicatas` | Coordenar T01 e suas exportações |
| `tratamentos.datas_aquisicao` | `padronizar_datas_aquisicao` | Aplicar o de-para das aquisições ISO |
| `tratamentos.datas_aquisicao` | `verificar_padronizacao_datas_aquisicao` | Conferir datas e campos preservados; produzir indicadores e auditoria |
| `tratamentos.datas_aquisicao` | `preparar_base_com_datas_padronizadas` | Coordenar T02 e suas exportações |
| `tratamentos.chamados` | `filtrar_chamados_anteriores_aquisicao` | Remover somente datas já diagnosticadas e contar exclusões |
| `tratamentos.chamados` | `verificar_filtragem_chamados` | Conferir datas removidas e campos preservados; produzir indicadores e auditoria |
| `tratamentos.chamados` | `preparar_base_com_chamados_consistentes` | Coordenar T03 e suas exportações |
| `tratamentos.cancelamentos` | `isolar_cancelamentos_inconsistentes` | Esvaziar datas diagnosticadas e sinalizar a incerteza |
| `tratamentos.cancelamentos` | `verificar_isolamento_cancelamentos` | Conferir o isolamento e a sinalização; produzir indicadores e auditoria |
| `tratamentos.cancelamentos` | `preparar_base_com_cancelamentos_sinalizados` | Coordenar T04 e suas exportações |

T02, T03 e T04 têm três módulos cada: transformação, verificação com auditoria e coordenação. T01 preserva seu quarto módulo de identificação, necessário para vincular cópias removidas às mantidas. T03 e T04 reutilizam as ocorrências do diagnóstico já calculado; a verificação da saída confirma se a regra passou a ser atendida.

## Como rodar os testes

Na raiz do projeto, com o ambiente ativo:

```bash
python -m unittest discover -s tests -v
```

O teste versionado atual cobre a deduplicação: preservação da fonte, remoção somente de cópias integrais, manutenção de registros com mesmo ID e conteúdos diferentes, indicadores e rejeição de mudanças indevidas nas linhas mantidas.

Os quatro tratamentos também fazem verificações de integridade durante `python main.py`, antes de suas exportações. Ampliar os testes automatizados versionados para T02, T03 e T04 permanece uma pendência; as verificações do fluxo não equivalem a uma suíte independente de testes.

## Pendências metodológicas e próximas etapas

Os tratamentos concluídos são regras fixas aprovadas, sem parâmetros estatísticos aprendidos. As próximas decisões continuam incrementais.

- **Unidade de análise:** construir e validar uma fotografia de cliente na data de corte, considerando eventuais reativações e o significado dos campos.
- **Protocolo temporal:** o horizonte inicial é de 60 dias. Corte e cobertura do acompanhamento da VF2 ainda não foram confirmados. As candidatas didáticas são 21/09/2026 e 21/11/2026, separadas por 61 dias; é necessária uma convenção explícita para os 60 dias.
- **Disponibilidade dos atributos:** confirmar a fotografia de referência de cada campo e usar somente informações disponíveis até o corte.
- **Alvo:** definir elegibilidade, acompanhamento e desfecho. Data de cancelamento ausente não comprova `churn = 0`; os casos sinalizados em T04 mantêm desfecho desconhecido.
- **Avaliação:** definir isolamento temporal e por cliente antes da EDA que orientará tratamentos. Estatísticas e transformações aprendidas serão ajustadas somente no treino.
- **Qualidade e EDA:** diagnosticar ausências, tipos, domínios, categorias e demais inconsistências; estudar distribuições e relações no treino após estabelecer o protocolo.
- **Modelagem:** preparar representações adequadas a cada tarefa. Churn e informações derivadas do desfecho não serão atributos do agrupamento. `cancelamento_inconsistente` também deve ficar fora dos atributos supervisionados.
- **Entrega final:** gerar a base preparada e o relatório consolidado, tornando opcionais as exportações completas de bases intermediárias.

Nenhum modelo foi treinado. A base 04 representa quatro tratamentos de qualidade concluídos, ainda sem a visão analítica e o protocolo de avaliação necessários à aprendizagem de máquina.
