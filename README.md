# Preparação de dados de churn

Projeto de preparação reproduzível de dados para estudos posteriores de aprendizagem supervisionada e não supervisionada. A referência metodológica são as Aulas 1, 2 e 3 do professor.

O programa começa pela planilha original, identifica problemas, aplica as regras aprovadas e gera uma base com os tratamentos estruturais aprovados. **Os modelos ainda não foram treinados e os demais tratamentos de qualidade ainda estão pendentes.**

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

O resultado desta fonte tem **4.990 registros e 11 colunas**. Uma nova execução reproduz toda a sequência a partir da fonte.

## O que acontece, na ordem

A sequência está explícita em `main.py`. Cada bloco identifica os casos, transforma uma cópia da base e verifica o resultado. A base devolvida alimenta o próximo bloco, sem reler arquivos intermediários.

| Etapa | Identificação e decisão aplicada | Registros depois |
| --- | --- | ---: |
| Fonte | Leitura do Excel preservando os valores originais | 5.020 |
| 1 — duplicatas | Remover 20 cópias iguais nas dez colunas da fonte; manter a primeira ocorrência | 5.000 |
| 2 — datas | Padronizar 15 aquisições em formato alternativo para `DD/MM/AAAA`, sem mudar a data | 5.000 |
| 3 — chamados | Excluir 52 datas anteriores à aquisição, distribuídas entre 33 clientes; preservar os chamados válidos | 5.000 |
| 4 — cancelamentos | Excluir diretamente os dez registros com cancelamento anterior à aquisição, conforme decisão do projeto | 4.990 |

A exclusão de clientes na etapa 4 é específica para esses casos aprovados. A Aula 2, pp. 9–10 do PDF, alerta contra descarte indiscriminado de ausências e discute o risco de erro no alvo. Uma inconsistência cronológica não prova que todos os demais campos do cadastro estejam errados. Os dez registros completos continuam na fonte e na auditoria.

O fluxo antigo esvaziava as dez datas, criava uma sinalização e depois excluía os mesmos clientes. Agora a exclusão é direta; a coluna `cancelamento_inconsistente` deixou de ser necessária.

## Protocolo temporal

A fotografia é o final de 21/09/2026; a janela futura de 60 dias vai de 22/09 a 20/11 e a referência didática de acompanhamento é 21/11/2026. A janela histórica de chamados vai de 24/06 a 21/09, inclusive, com 90 dias.

Essas convenções ficam em `definir_protocolo_temporal.py`. A cobertura completa dos cancelamentos foi aprovada como hipótese didática, sem comprovação na fonte. A elegibilidade e o alvo serão acrescentados na próxima parte desta entrega; esta parte preserva o resultado dos tratamentos existentes.

## O que mudou nas colunas

As dez colunas originais são preservadas nos registros mantidos, exceto as células cujo tratamento foi aprovado. Esta parte acrescenta apenas o metadado de qualidade:

- `chamados_excluidos_por_cronologia`: quantidade de datas retiradas de cada cliente na etapa 3. Distingue uma lista esvaziada pelo tratamento de um campo originalmente sem chamados.

Antes das exclusões posteriores, 17 clientes tiveram todas as datas de chamados removidas, além de 1.048 campos originalmente sem chamados. Esses vazios ainda não foram transformados automaticamente em contagem zero. As contagens no relatório referem-se à entrada e à saída de cada etapa.

**Esta base ainda não é a matriz de atributos dos modelos.** `churn` é o alvo supervisionado. Churn, datas de cancelamento e outras informações derivadas do desfecho ficam fora dos preditores, inclusive do agrupamento não supervisionado. IDs e metadados serão preservados para auditoria e separados dos atributos de modelagem.

## Saídas e leitura do relatório

Por padrão, são gerados dois arquivos:

| Arquivo | Uso |
| --- | --- |
| `dados/tratados/base_churn_sem_cancelamentos_inconsistentes.xlsx` | Base atual, na aba `base_tratada` |
| `relatorios/diagnostico_preparacao.xlsx` | Resumo, protocolo e evidências da execução |

O relatório tem **seis abas**, com no máximo um resumo global e uma aba de evidências por problema:

| Aba | O que procurar |
| --- | --- |
| `00_resumo` | Indicadores antes/depois por problema; comece por aqui |
| `00_protocolo` | Datas, hipóteses, regras aprovadas e pendências |
| `01_duplicatas` | As 20 cópias removidas e a linha da ocorrência mantida |
| `02_datas` | Os 15 valores antes/depois da padronização |
| `03_chamados` | Uma linha por cliente afetado: datas excluídas, quantidade e lista antes/depois; também registra datas fora da janela histórica quando houver |
| `04_cancelamentos` | Os dez registros excluídos, com suas datas originais |

Cada evidência inclui cliente, arquivo e linha Excel da fonte. A numeração considera o cabeçalho na linha 1. Os índices originais são preservados em memória, mesmo depois das exclusões.

As seis abas são reconstruídas juntas em cada execução. Os resultados anteriores de cada problema continuam representados, sem acumular abas antigas ou duplicadas. A fonte permanece intacta; os arquivos de saída ficam fora do Git e são reproduzíveis.

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
| Cancelamentos | `remover_registros_com_cancelamento_inconsistente` | Excluir diretamente os registros identificados |
| Cancelamentos | `verificar_exclusao_cancelamentos_inconsistentes` | Conferir os registros mantidos e guardar os excluídos na auditoria |

Os tratamentos usam as ocorrências identificadas; não procuram novamente o mesmo problema. As verificações confirmam condições essenciais da saída. A interpretação de todas as datas não é repetida a cada tratamento.

Cada verificação devolve `resumo`, `evidencias`, `regra` e `decisao`. `montar_abas_relatorio` reúne esses resultados. Assim, uma nova regra pode ser acrescentada à sequência sem criar outro coordenador ou escritor Excel por tratamento.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os sete testes cobrem preservação da fonte, cópias integrais, remoção direta de cancelamentos inconsistentes, datas inválidas, limites da janela histórica e reprodução do fluxo. As exportações são simuladas nos testes do fluxo.

## Pendências e limites desta versão

- Acrescentar elegibilidade e alvo na parte seguinte, seguindo as convenções aprovadas.

- Construir `tempo_cliente_meses` e a contagem de chamados nos 90 dias históricos, definindo o significado dos chamados ausentes e dos campos esvaziados pelo tratamento.
- Diagnosticar e tratar categorias, tipos, domínios, faixas, ausências dos preditores, redundância e ruído.
- Definir o isolamento dos conjuntos de avaliação antes da EDA e das transformações aprendidas. Imputação, escala e codificação aprendida serão ajustadas somente no treino.
- A base atual tem uma fotografia temporal. Uma avaliação estritamente fora do tempo exige fotografias de outras datas; isso não é obtido simplesmente separando clientes desta mesma fotografia.
- A Aula 3 utiliza uma VF3 e tamanhos próprios do exemplo. Seus totais e métricas não são metas a copiar para a VF2 após os filtros deste projeto.
- Preparar os atributos adequados a cada tarefa, separar alvo e metadados e só então avançar para modelagem.

As regras implementadas são fixas e aprovadas, sem parâmetros estatísticos aprendidos. Esta parte entrega o fluxo refatorado com os tratamentos anteriores e auditoria compacta; a preparação completa para aprendizagem de máquina continua incremental.
