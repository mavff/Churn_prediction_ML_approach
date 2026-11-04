# Preparação de dados de churn

Projeto de preparação reproduzível de dados para estudos posteriores de aprendizagem supervisionada e não supervisionada. A referência metodológica são as Aulas 1, 2 e 3 do professor.

O programa começa pela planilha original, identifica problemas, aplica as regras aprovadas e gera uma base com população definida e alvo `churn`. **Os modelos ainda não foram treinados e os demais tratamentos de qualidade ainda estão pendentes.**

## Como rodar

Ambiente utilizado: Python 3.12.3 no Linux. As dependências estão fixadas em `requirements.txt`.

Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

No Windows, a criação e ativação do ambiente com PowerShell são:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Depois, use os mesmos comandos de instalação e de execução. A entrada esperada é `dados/base_churn_5000_VF2_aluno.xlsx`, com uma única aba. Os caminhos são resolvidos a partir da localização de `main.py`.

O resultado desta fonte tem **4.976 registros e 13 colunas**. Uma nova execução reproduz toda a sequência a partir da fonte.

## O que acontece, na ordem

A sequência está explícita em `main.py`. Cada bloco identifica os casos, transforma uma cópia da base e verifica o resultado. A base devolvida alimenta o próximo bloco, sem reler arquivos intermediários.

| Etapa | Identificação e decisão aplicada | Registros depois |
| --- | --- | ---: |
| Fonte | Leitura do Excel preservando os valores originais | 5.020 |
| 1 — duplicatas | Remover 20 cópias iguais nas dez colunas da fonte; manter a primeira ocorrência | 5.000 |
| 2 — datas | Padronizar 15 aquisições em formato alternativo para `DD/MM/AAAA`, sem mudar a data | 5.000 |
| 3 — chamados | Excluir 52 datas anteriores à aquisição, distribuídas entre 33 clientes; preservar os chamados válidos | 5.000 |
| 4 — cancelamentos | Excluir diretamente os dez registros com cancelamento anterior à aquisição, conforme decisão do projeto | 4.990 |
| 5 — elegibilidade e alvo | Selecionar clientes com pelo menos 60 dias de histórico, ativos no corte e com desfecho conhecido; criar `churn` | 4.976 |
| 6 — contagem de chamados | Substituir as listas pela quantidade de datas válidas nos 90 dias históricos; preservar ausências para a imputação posterior | 4.976 |

A exclusão de clientes na etapa 4 é específica para esses casos aprovados. A Aula 2, pp. 9–10 do PDF, alerta contra descarte indiscriminado de ausências e discute o risco de erro no alvo. Uma inconsistência cronológica não prova que todos os demais campos do cadastro estejam errados. Os dez registros completos continuam na fonte e na auditoria.

O fluxo antigo esvaziava as dez datas, criava uma sinalização e depois excluía os mesmos clientes. Agora a exclusão é direta; a coluna `cancelamento_inconsistente` deixou de ser necessária.

## Como o alvo foi construído

As convenções ficam em `preparacao_dados/definir_protocolo_temporal.py` e são exportadas para `00_protocolo`:

| Conceito | Convenção adotada |
| --- | --- |
| Unidade de análise | Um cliente no final do dia de corte |
| Corte | 21/09/2026 |
| Histórico de chamados | 24/06 a 21/09/2026, inclusive: 90 dias |
| Horizonte do alvo | 22/09 a 20/11/2026, inclusive: 60 dias |
| Limite de acompanhamento informado | 21/11/2026 |
| Histórico mínimo no corte | 60 dias, seguindo a maturação discutida na Aula 1, p. 18 do PDF |
| Cobertura dos cancelamentos | Completa por **hipótese didática aprovada**, não por comprovação na fonte |

O mínimo de histórico e o acompanhamento futuro são condições distintas. Ter 60 dias de contrato no corte não comprova que os 60 dias seguintes foram observados. O limite didático de 21/11 oferece um dia além da janela do alvo adotada.

Entre os clientes participantes:

- `churn = 1`: cancelamento observado após o corte e até 20/11/2026, inclusive.
- `churn = 0`: ausência de cancelamento na janela, sob a convenção aprovada de cobertura completa. Cancelamento posterior à janela também não é um evento dentro dela.

Antes do alvo, são verificadas aquisição, atividade no corte, histórico mínimo e referência de acompanhamento. Cancelamento no dia do corte é um evento já conhecido e não entra na janela futura.

Quatorze clientes da fonte tratada têm menos de 60 dias de histórico. Eles ficam fora **desta população de análise**, com motivo registrado e alvo vazio na auditoria; não são convertidos em não churn. A base atual contém:

| Alvo | Clientes |
| --- | ---: |
| `0` | 3.213 |
| `1` | 1.763 |
| Total participante | 4.976 |

O código impede criar rótulos zero quando a cobertura não é assumida ou quando o acompanhamento informado não cobre a janela inteira. Eventos positivos já observados podem ser conhecidos mesmo sem acompanhamento completo.

## Contagem numérica dos chamados

A Aula 1, p. 7 do PDF, define `chamados_suporte` como o volume de chamados abertos em 90 dias. A etapa 6 conta as ocorrências válidas entre 24/06 e 21/09/2026, inclusive. Chamados futuros e datas anteriores à aquisição já excluídas não entram no cálculo. Duas ocorrências no mesmo dia são contadas separadamente; a fonte não fornece ID de chamado para concluir que sejam duplicatas.

A coluna `data_chamado` é substituída por `chamados_suporte`, com tipo `Int64` e sem alterar os demais campos. As listas usadas na conversão ficam na auditoria `06_contagem_chamados` e continuam disponíveis na fonte.

Na base atual, há 3.917 contagens numéricas e 1.059 campos sem lista. Estes permanecem ausentes: 1.045 já não tinham datas na entrada e 14 ficaram vazios quando datas anteriores à aquisição foram removidas. As listas que ainda contêm datas válidas são contadas, preservando o indicador de exclusão anterior. Portanto, o atributo mede os registros válidos disponíveis, não reconstrói eventos sem data confiável.

Uma lista vazia não é preenchida automaticamente com zero nesta etapa. Já uma lista preenchida cujos eventos estão todos fora dos 90 dias tem contagem histórica zero. Os dois casos são distintos.

A Aula 2, pp. 9 e 16 do PDF, orienta aprender mediana/moda somente no treino. A separação de avaliação e a imputação serão implementadas depois; esta conversão não aprende estatísticas nem preenche os ausentes. Valores imputados serão estimativas identificáveis, não novos eventos observados.

## O que mudou nas colunas

As informações originais permanecem na fonte e na auditoria. Na base atual, `data_chamado` foi substituída por `chamados_suporte`, e os demais campos dos registros mantidos são preservados, exceto os tratamentos aprovados. A base também contém:

- `chamados_excluidos_por_cronologia`: quantidade de datas retiradas de cada cliente na etapa 3. Distingue uma lista esvaziada pelo tratamento de um campo originalmente sem chamados.
- `data_corte`: data de referência da fotografia.
- `churn`: alvo inteiro binário, armazenado como `Int64` no programa.

Antes das exclusões posteriores, 17 clientes tiveram todas as datas de chamados removidas, além de 1.048 campos originalmente sem chamados. Esses vazios ainda não foram transformados automaticamente em contagem zero. As contagens no relatório referem-se à entrada e à saída de cada etapa.

**Esta base ainda não é a matriz de atributos dos modelos.** `churn` é o alvo supervisionado. Churn, datas de cancelamento e outras informações derivadas do desfecho ficam fora dos preditores, inclusive do agrupamento não supervisionado. IDs e metadados serão preservados para auditoria e separados dos atributos de modelagem.

## Saídas e leitura do relatório

Por padrão, são gerados dois arquivos:

| Arquivo | Uso |
| --- | --- |
| `dados/tratados/base_churn_com_contagem_chamados.xlsx` | Base atual, na aba `base_tratada` |
| `relatorios/diagnostico_preparacao.xlsx` | Resumo, protocolo e evidências da execução |

O relatório tem **oito abas**: resumo e protocolo globais, mais evidências. O assunto chamados tem duas abas dedicadas, uma para a correção das datas e outra para a conversão numérica:

| Aba | O que procurar |
| --- | --- |
| `00_resumo` | Indicadores antes/depois por problema; comece por aqui |
| `00_protocolo` | Datas, hipóteses, regras aprovadas e pendências |
| `01_duplicatas` | As 20 cópias removidas e a linha da ocorrência mantida |
| `02_datas` | Os 15 valores antes/depois da padronização |
| `03_chamados` | Uma linha por cliente afetado: datas excluídas, quantidade e lista antes/depois; também registra datas fora da janela histórica quando houver |
| `04_cancelamentos` | Os dez registros excluídos, com suas datas originais |
| `05_elegibilidade_alvo` | Uma avaliação por cliente da entrada desta etapa: histórico, participação, motivo e alvo |
| `06_contagem_chamados` | Uma linha por cliente participante, com lista de entrada, datas da janela, contagem observada, ausências e sinalização de exclusões anteriores |

Na aba `05_elegibilidade_alvo`, filtre `elegivel = False` para ver os 14 clientes fora da população. Os 4.990 clientes avaliados aparecem ali; apenas os 4.976 participantes aparecem na base atual.

Cada evidência inclui cliente, arquivo e linha Excel da fonte. A numeração considera o cabeçalho na linha 1. Os índices originais são preservados em memória, mesmo depois das exclusões.

As oito abas são reconstruídas juntas em cada execução. Os resultados anteriores de cada problema continuam representados, sem acumular abas antigas ou duplicadas. A fonte permanece intacta; os arquivos de saída ficam fora do Git e são reproduzíveis.

As bases numeradas das versões anteriores são arquivos de conferência daquele fluxo. O resultado atual é o arquivo principal indicado acima. Para gerar intermediárias no novo fluxo, altere `salvar_intermediarias = False` para `True` em `main.py`; elas serão salvas em `dados/tratados/intermediarios/`.

## Como os arquivos Python se dividem

`main.py` mostra a ordem e faz as chamadas. As funções de negócio não leem Excel, não imprimem resultados e não exportam arquivos. As funções de entrada e saída concentram essas operações.

```text
main.py                                  # sequência explícita
preparacao_dados/
├── leitura_dados.py                      # entrada
├── definir_protocolo_temporal.py         # convenções aprovadas
├── montar_abas_relatorio.py              # montagem do relatório compacto
├── exportar_base_excel.py                # saída da base; intermediárias opcionais
├── exportar_relatorio_excel.py           # escrita e formatação do Excel
├── apresentar_estrutura_base.py          # dimensões e colunas no terminal
├── diagnosticos/
│   ├── identificadores/                  # identificar cópias e referências
│   └── datas/                            # interpretar datas, identificar problemas e população
└── tratamentos/
    ├── duplicatas/                       # remover cópias e verificar
    ├── datas_aquisicao/                  # aplicar de-para e verificar
    ├── chamados/                         # filtrar datas e verificar
    ├── cancelamentos/                    # excluir registros e verificar
    └── elegibilidade/                    # selecionar participantes, acrescentar alvo e verificar
tests/                                   # testes automatizados
```

Cada arquivo de implementação contém uma função. Os arquivos `__init__.py` identificam os pacotes e disponibilizam os nomes para imports mais curtos na `main`; não executam o fluxo.

### Identificar, transformar e verificar

| Grupo | Arquivo/função | Responsabilidade |
| --- | --- | --- |
| Identificadores | `identificar_duplicatas_excedentes` | Encontrar cópias integrais e vincular a linha removida à mantida |
| Duplicatas | `remover_duplicatas_integrais` | Remover as cópias já identificadas |
| Duplicatas | `verificar_remocao_duplicatas` | Conferir clientes, conteúdo preservado e ausência de cópias restantes |
| Datas | `interpretar_datas` | Interpretar os três campos temporais uma vez, com formatos explícitos e rastreabilidade |
| Datas | `identificar_aquisicoes_fora_padrao` | Selecionar aquisições válidas com representação diferente de `DD/MM/AAAA` |
| Aquisição | `padronizar_datas_aquisicao` | Aplicar o de-para aos casos selecionados |
| Aquisição | `verificar_padronizacao_datas_aquisicao` | Conferir datas e demais campos preservados; produzir o de-para de auditoria |
| Datas | `identificar_eventos_anteriores_aquisicao` | Encontrar chamados ou cancelamentos anteriores à aquisição da mesma linha |
| Chamados | `filtrar_chamados_anteriores_aquisicao` | Retirar as datas identificadas e contar exclusões por cliente |
| Chamados | `verificar_filtragem_chamados` | Conferir exatamente quais datas saíram e agrupar a evidência por cliente |
| Datas | `identificar_contagem_chamados` | Contar os registros válidos da janela, reutilizando as datas interpretadas e as exclusões identificadas |
| Chamados | `substituir_datas_por_contagem_chamados` | Trocar a coluna de listas pela coluna numérica sem mudar os demais dados |
| Chamados | `verificar_contagem_chamados` | Conferir tipo inteiro, ausências, alinhamento e preservação do alvo; produzir a auditoria da conversão |
| Cancelamentos | `remover_registros_com_cancelamento_inconsistente` | Excluir diretamente os registros identificados |
| Cancelamentos | `verificar_exclusao_cancelamentos_inconsistentes` | Conferir os registros mantidos e guardar os excluídos na auditoria |
| Datas | `identificar_elegibilidade_alvo` | Avaliar participação e desfecho com o protocolo e as datas já interpretadas |
| Elegibilidade | `construir_base_elegivel_com_alvo` | Selecionar participantes e acrescentar `data_corte` e `churn` |
| Elegibilidade | `verificar_elegibilidade_alvo` | Conferir população, rótulos, histórico mínimo e preservação dos preditores |

Os tratamentos usam as ocorrências identificadas; não procuram novamente o mesmo problema. As verificações confirmam condições essenciais da saída. A interpretação de todas as datas não é repetida a cada tratamento.

Cada verificação devolve `resumo`, `evidencias`, `regra` e `decisao`. `montar_abas_relatorio` reúne esses resultados. Assim, uma nova regra pode ser acrescentada à sequência sem criar outro coordenador ou escritor Excel por tratamento.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os doze testes cobrem preservação da fonte, cópias integrais, remoção direta de cancelamentos inconsistentes, datas inválidas, limites temporais, histórico de 59/60 dias, construção dos rótulos, acompanhamento insuficiente reprodução do fluxo e conversão dos chamados, distinguindo ausência de zero e preservando ocorrências válidas repetidas. As exportações são simuladas nos testes do fluxo.

## Pendências e limites desta versão

- Construir `tempo_cliente_meses` até o corte. A contagem histórica de chamados já está implementada; seu tratamento de ausências depende da imputação aprendida somente no treino.
- Diagnosticar e tratar categorias, tipos, domínios, faixas, ausências dos preditores, redundância e ruído.
- Definir o isolamento dos conjuntos de avaliação antes da EDA e das transformações aprendidas. Imputação, escala e codificação aprendida serão ajustadas somente no treino.
- A base atual tem uma fotografia temporal. Uma avaliação estritamente fora do tempo exige fotografias de outras datas; isso não é obtido simplesmente separando clientes desta mesma fotografia.
- A Aula 3 utiliza uma VF3 e tamanhos próprios do exemplo. Seus totais e métricas não são metas a copiar para a VF2 após os filtros deste projeto.
- Preparar os atributos adequados a cada tarefa, separar alvo e metadados e só então avançar para modelagem.

As regras implementadas são fixas e aprovadas, sem parâmetros estatísticos aprendidos. O marco atual entrega uma população temporal e seu alvo, com auditoria; a preparação completa para aprendizagem de máquina continua incremental.
