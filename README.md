# Preparação de dados de churn

Projeto de preparação reproduzível de dados para estudos posteriores de aprendizagem supervisionada e não supervisionada. A referência metodológica são as Aulas 1, 2 e 3 do professor.

O programa começa pela planilha original, constrói a população e o alvo `churn`, divide os clientes e aplica as regras fixas do dicionário em cada conjunto. Depois imputa as ausências com valores aprendidos somente no treino, faz a análise exploratória (AED) do treino e retira dos preditores o atributo aprovado como irrelevante. A divisão é 50% treino, 25% validação e 25% teste. **Codificação, escala e modelagem continuam pendentes.**

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

O resultado desta fonte tem **4.976 registros e 14 colunas**. Uma nova execução reproduz toda a sequência a partir da fonte.

## O que acontece, na ordem

A `main.py` contém seis chamadas principais: construir a visão, dividir os clientes, preparar os conjuntos, imputar as ausências, selecionar os atributos a partir da AED do treino e exportar os resultados. Cada função coordenadora agrupa as chamadas das regras existentes. Dentro de cada tratamento continuam separadas identificação, transformação e verificação. A base devolvida alimenta o próximo bloco, sem reler arquivos intermediários.

| Etapa | Identificação e decisão aplicada | Registros depois |
| --- | --- | ---: |
| Fonte | Leitura do Excel preservando os valores originais | 5.020 |
| 1 — duplicatas | Remover 20 cópias iguais nas dez colunas da fonte; manter a primeira ocorrência | 5.000 |
| 2 — datas | Padronizar 15 aquisições em formato alternativo para `DD/MM/AAAA`, sem mudar a data | 5.000 |
| 3 — chamados | Excluir 52 datas anteriores à aquisição, distribuídas entre 33 clientes; preservar os chamados válidos | 5.000 |
| 4 — cancelamentos | Excluir diretamente os dez registros com cancelamento anterior à aquisição, conforme decisão do projeto | 4.990 |
| 5 — elegibilidade e alvo | Selecionar clientes com pelo menos 60 dias de histórico, ativos no corte e com desfecho conhecido; criar `churn` | 4.976 |
| 6 — contagem de chamados | Substituir as listas pela quantidade de datas válidas nos 90 dias históricos; preservar ausências para a imputação posterior | 4.976 |
| 7 — tempo de cliente | Acrescentar `tempo_cliente_meses`, calculado até o corte, preservando a aquisição | 4.976 |
| Divisão | Isolar os clientes em treino (2.488), validação (1.244) e teste (1.244), antes da qualidade dos preditores | 4.976 |
| 8 — categorias | Padronizar 80 células de contrato e 89 de pagamento; normalizar ausências e converter categorias desconhecidas em ausentes, com auditoria | 4.976 |
| 9 — números | Validar os seis preditores numéricos/binários, aplicar os tipos esperados e converter 20 células fora do domínio em ausentes | 4.976 |
| 11 — imputação | Aprender mediana e moda somente no treino e preencher as 1.279 ausências dos três conjuntos; listas de chamados vazias recebem zero; alertar ausência acima de 20% | 4.976 |
| 12 — atributos | AED do treino para relevância, redundância e ruído; retirar `forma_pagamento` do X nos três conjuntos, mantendo-a na base | 4.976 |
| 13 — descritiva | Estatística descritiva do treino: posição, dispersão e taxa de churn por categoria | 4.976 |

A exclusão de clientes na etapa 4 é específica para esses casos aprovados. A Aula 2, pp. 9–10 do PDF, alerta contra descarte indiscriminado de ausências e discute o risco de erro no alvo. Uma inconsistência cronológica não prova que todos os demais campos do cadastro estejam errados. Os dez registros completos continuam na fonte e na auditoria.

O fluxo antigo esvaziava as dez datas, criava uma sinalização e depois excluía os mesmos clientes. Agora a exclusão é direta; a coluna `cancelamento_inconsistente` deixou de ser necessária.

## Coordenação e divisão dos clientes

| Chamada principal | O que coordena |
| --- | --- |
| `construir_visao_analitica` | Duplicatas, referências temporais, população, alvo, contagem de chamados e tempo de cliente |
| `dividir_conjuntos` | Protocolo de separação, estratificação e verificação dos três conjuntos |
| `preparar_conjuntos` | De-para e validação numérica em cada conjunto, seguidos da separação de atributos, alvo e metadados |
| `imputar_conjuntos` | Ajuste único da imputação no treino, aplicação aos três conjuntos e auditoria de cada célula preenchida |
| `selecionar_atributos` | AED do treino (relevância, redundância, ruído e estatística descritiva) e retirada dos atributos aprovados nos três conjuntos |
| `exportar_resultados` | Base completa, workbook opcional dos conjuntos, diagnóstico consolidado e gráficos da AED |

A Aula 3 apresenta 70/30 na p. 4 e 50/25/25 na p. 5 do PDF. O projeto adotou explicitamente a segunda opção, combinada com a estratificação por churn e `random_state=42` discutidos no exemplo da p. 4. A configuração fica em `preparacao_dados/divisao/definir_protocolo_divisao.py`.

| Conjunto | Clientes | Churn = 0 | Churn = 1 | Uso posterior |
| --- | ---: | ---: | ---: | --- |
| Treino | 2.488 | 1.606 | 882 | Ajuste da imputação, AED, seleção de atributos, futura escala/codificação e treinamento |
| Validação | 1.244 | 803 | 441 | Comparar configurações sem reajustar parâmetros de preparação |
| Teste | 1.244 | 804 | 440 | Avaliação final reservada |

O sorteio ocorre em duas etapas: 50% para treino e 50% de reserva; a reserva é dividida igualmente em validação e teste. Os clientes são ordenados por identificador antes do sorteio para tornar a atribuição estável perante reordenação das linhas. Os índices de origem continuam preservados. A verificação exige cobertura integral, conteúdo preservado e nenhum cliente compartilhado. Se as classes forem pequenas demais para estratificar três conjuntos, o programa informa o problema e não troca o protocolo silenciosamente.

A divisão é de clientes da mesma fotografia. As janelas de 90 dias históricos e 60 dias do alvo permanecem iguais. Isso não implementa uma avaliação em época futura. O campo churn é usado para estratificar e fica separado dos preditores.

Depois da divisão, as regras fixas do dicionário são aplicadas individualmente aos conjuntos. Até a etapa 9, a base completa reconstruída preserva os valores e rótulos da versão anterior; a partir da etapa 11, somente as ausências recebem estimativas. Os totais de auditoria são somados e as evidências recebem `conjunto`, mantendo um relatório único.

Em memória, o resultado de `preparar_conjuntos` é um dicionário com `treino`, `validacao` e `teste`. Cada entrada contém:

- `X`: os oito preditores do dicionário, sem churn, identificador ou datas do desfecho.
- `y`: somente a série `churn`, com os mesmos índices de X.
- `metadados`: identificador, datas e campos de auditoria preservados.
- `ordem_colunas`: a ordem original, usada para reconstruir as exportações completas.

`imputar_conjuntos` devolve a mesma estrutura, com `X` sem ausências; `y`, `metadados` e `ordem_colunas` não mudam. Em seguida, `selecionar_atributos` tira `forma_pagamento` do `X`, que fica com sete preditores, e a guarda em `metadados`; reconstruída, a tabela completa de cada conjunto continua idêntica.

## Imputação ajustada no treino

A Aula 2, pp. 9 e 16, e a Aula 3, p. 4, determinam aprender medianas e modas somente no treino. `imputar_conjuntos` chama `fit` uma única vez, em `preparados["treino"]["X"]`, fora do laço que aplica as regras fixas, e aplica somente `transform` a treino, validação e teste. O ajuste é um `ColumnTransformer` com um `SimpleImputer` por preditor, como orienta a Aula 2, p. 16; codificação e escala poderão ser acrescentadas depois ao mesmo encadeamento. A estratégia de cada campo fica em `preparacao_dados/imputacao/definir_protocolo_imputacao.py` e é exportada para `00_protocolo`.

| Campo | Estratégia | Valor aprendido no treino | Células preenchidas (treino / validação / teste) |
| --- | --- | --- | ---: |
| `tempo_cliente_meses` | Mediana | 21 | 0 |
| `mensalidade_rs` | Mediana | 86,05 | 55 / 37 / 40 |
| `chamados_suporte` | Zero por regra | 0 | 524 / 283 / 252 |
| `atrasos_6m` | Mediana | 1 | 21 / 12 / 10 |
| `tipo_contrato` | Moda | `Mensal` | 15 / 5 / 5 |
| `forma_pagamento` | Moda | `Boleto` | 11 / 3 / 6 |
| `fibra_optica` | Moda | 1 | 0 |
| `debito_automatico` | Moda | 0 | 0 |

Os campos sem ausências também recebem um valor aprendido, para que dados novos com lacunas sejam tratados da mesma forma.

`chamados_suporte` é a exceção aprovada: lista vazia significa nenhum chamado registrado na janela, como na consolidação da Aula 1, p. 12 do PDF. Na base não existe contagem zero observada (o mínimo é 1), 8.585 das 8.597 datas da fonte caem na janela e o grupo sem lista tem churn de 21,8% no treino, abaixo dos 27,2% de quem abriu um chamado. A mediana (2) colocaria esses clientes num grupo com 37% de churn. O zero é uma regra fixa, não um parâmetro aprendido. A etapa 6 continua mantendo a ausência, para que a auditoria distinga a lista vazia da contagem observada.

A mensalidade usa a mediana geral do treino, como na Aula 3, p. 4. O valor depende da fibra (mediana de 65,36 sem fibra e 97,09 com fibra); uma mediana por grupo de fibra fica registrada como refinamento opcional.

Um valor aprendido fora do dicionário interrompe o fluxo — por exemplo, uma mediana 0,5 em `atrasos_6m` —, em vez de ser arredondado silenciosamente. A verificação confere que os valores observados não mudaram, que cada ausência recebeu o valor do treino e que os tipos `Int64`, `Float64` e `string` foram mantidos. A aba `11_imputacao` registra cada célula preenchida, com conjunto, cliente, linha da fonte, campo, valor e estratégia.

O contrato de dados da Aula 2, p. 11, pede alerta quando a ausência de um campo passa de 20% no lote. A verificação calcula a taxa de cada campo em cada conjunto antes de imputar: só `chamados_suporte` passa do limiar (21,1% no treino, 22,8% na validação e 20,3% no teste). O alerta aparece no resumo, como quantidade de conjuntos acima do limiar, e em cada célula da aba `11_imputacao`; a imputação segue a regra do zero. O limiar fica no protocolo de imputação.

Validação e teste nunca participam do ajuste: um teste altera esses conjuntos e confirma que o treino imputado não muda. A aplicação recebe somente os preditores, sem exigir churn. Persistência do objeto ajustado e fluxo de previsão para dados novos ainda serão implementados.

## Relevância, redundância e ruído

A Aula 2, pp. 10 e 17 do PDF, distingue atributos irrelevantes (sem relação com o alvo), redundantes (duplicam outro preditor) e ruído (valores ou rótulos que distorcem a fronteira de decisão). Esta etapa é somente AED: nenhum modelo é treinado. `selecionar_atributos` mede os sinais no treino imputado, com correlação de Pearson e categorias em indicadores 0/1, como na Aula 3. Os limiares são convenções do projeto para sinalizar candidatos: |r| < 0,05 com churn e |r| ≥ 0,8 entre campos diferentes. Indicadores do mesmo campo não contam como redundância.

| Sinal | Resultado na AED do treino | Decisão aprovada |
| --- | --- | --- |
| Irrelevância | `forma_pagamento`: churn de 35,8% (Boleto), 34,8% (Cartão) e 35,7% (Pix); \|r\| ≤ 0,01 | Retirada do X nos três conjuntos; continua na base exportada para o benchmark com todas as variáveis na modelagem (Aula 2, p. 10) |
| Redundância | `mensalidade_rs` × `fibra_optica`, r = 0,84 | Manter as duas e registrar; a escolha pode ser revista na modelagem |
| Extremos | 74 clientes com tempo acima de 63 meses e 10 com mais de 6 chamados | Plausíveis dentro do dicionário; mantidos e documentados |
| Valores repetidos | 49,90 de mensalidade (61 clientes, o mínimo observado) e 72 meses de tempo (34 clientes, todos com aquisição em 21/09/2020) | Prováveis piso de plano e truncamento da data de aquisição na fonte; mantidos e registrados para investigação na origem |
| Rótulos conflitantes | Nenhum grupo de preditores iguais com churn diferente | Nada a tratar |

A verificação só aceita retirar um campo cujos indicadores tenham sido todos sinalizados como irrelevantes na AED do treino; pedir a retirada de `tempo_cliente_meses`, por exemplo, interrompe o fluxo. A retirada muda o papel da coluna, não seu valor.

Identificador, datas e controles de auditoria já estão fora do X desde a separação dos conjuntos. `data_ocorrencia_churn` é informação a posteriori e vazaria o alvo; `data_aquisicao_cliente` foi traduzida em `tempo_cliente_meses` (Aula 1, p. 16); `data_corte` é constante; `id_cliente` é o exemplo de irrelevante da Aula 2, p. 10. Esses campos permanecem como metadados para auditoria.

As decisões ficam em `preparacao_dados/definir_protocolo_atributos.py` e são exportadas para `00_protocolo`. A aba `12_atributos` traz uma linha por atributo, com correlação com churn, atributo mais correlacionado, valor mais frequente, limites IQR, situação e decisão.

## Estatística descritiva e gráficos da AED

A aba `13_descritiva` resume o treino imputado: média, desvio, quartis, assimetria e média por classe nas contagens e nos valores contínuos; frequência e taxa de churn por categoria e indicador binário. Por exemplo, o churn é de 46,6% no contrato mensal e de 17,5% no bienal; quem cancelou tinha em média 19,4 meses de casa e 2,25 chamados, contra 27,4 meses e 1,45 chamado de quem ficou.

Três gráficos do treino são gravados em `relatorios/graficos/`:

| Arquivo | Conteúdo |
| --- | --- |
| `correlacoes.png` | Matriz de Pearson entre numéricos, binários e churn |
| `distribuicoes.png` | Distribuição de tempo, mensalidade, chamados e atrasos por classe de churn |
| `churn_por_categoria.png` | Taxa de churn por contrato, pagamento, fibra e débito, com a média do treino |

Os gráficos incluem `forma_pagamento`, para mostrar a evidência da retirada. Usam o matplotlib, fixado em `requirements.txt`, e saem idênticos a cada execução.

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

Na base atual, há 3.917 contagens numéricas e 1.059 campos sem lista. Nesta etapa, estes permanecem ausentes: 1.045 já não tinham datas na entrada e 14 ficaram vazios quando datas anteriores à aquisição foram removidas. As listas que ainda contêm datas válidas são contadas, preservando o indicador de exclusão anterior. Portanto, o atributo mede os registros válidos disponíveis, não reconstrói eventos sem data confiável.

Uma lista vazia não é preenchida com zero nesta etapa; o zero é aplicado na imputação (etapa 11) e registrado como célula preenchida. Já uma lista preenchida cujos eventos estão todos fora dos 90 dias tem contagem histórica zero. Os dois casos são distintos.

Esta conversão não aprende estatísticas nem preenche os ausentes; a imputação acontece depois da divisão. Os valores imputados ficam identificáveis na aba `11_imputacao` e não são tratados como eventos observados.

## Tempo de cliente e de-para das categorias

A Aula 1, p. 7 do PDF (rodapé Slide 6), define `tempo_cliente_meses` como meses de ativação contínua. O projeto adota meses completos: calcula a diferença entre ano/mês da aquisição e do corte e desconta um mês quando o dia da aquisição ainda não foi alcançado no mês do corte. Essa fórmula é uma convenção aprovada do projeto, não uma fórmula explicitada no slide. O cálculo não divide dias por 30 nem utiliza a data de cancelamento.

Exemplo no corte de 21/09/2026: aquisição em 21/09/2025 resulta em 12 meses; aquisição em 22/09/2025 resulta em 11. A coluna usa `Int64`, é acrescentada após a aquisição e não substitui a data original. Os 4.976 cálculos ficam em `07_tempo_cliente`.

A Aula 2, p. 3 do PDF (rodapé Slide 4), define os domínios das categorias:

| Campo | Grafias reconhecidas na comparação | Saída |
| --- | --- | --- |
| `tipo_contrato` | `mensal`, `anual`, `bienal`, independentemente da caixa e de espaços externos | `Mensal`, `Anual`, `Bienal` |
| `forma_pagamento` | `boleto`, `cartao`/`cartão`, `pix`, independentemente da caixa e de espaços externos | `Boleto`, `Cartão`, `Pix` |

O slide pede remoção de acentos, mas apresenta `Cartão` no domínio. Por decisão do projeto, a comparação desconsidera acentos e a saída conserva a grafia `Cartão`. O mapa é fixo, definido pelo dicionário; não é um vocabulário aprendido com a base nem uma codificação numérica para modelos.

Na população atual, são padronizadas 169 células: 80 de contrato e 89 de pagamento. Os 25 contratos e 20 pagamentos vazios continuam ausentes. Uma categoria sem equivalência conhecida é convertida em ausência na base tratada e preservada integralmente na auditoria. Na fonte atual não há categorias desconhecidas após a comparação normalizada.

## Validação do dicionário e tratamento dos inválidos

`preparacao_dados/definir_dicionario_dados.py` é a fonte única de tipos, faixas e de-para fixos. O dicionário é o da Aula 2, p. 3 do PDF; os nomes das colunas seguem a VF2, incluindo `debito_automatico`, correspondente ao `debito_auto` do slide.

| Campo | Tipo no programa | Valores conhecidos permitidos |
| --- | --- | --- |
| `tempo_cliente_meses` | `Int64` | Inteiros entre 0 e 120 |
| `mensalidade_rs` | `Float64` | De 10 a 500, inclusive |
| `chamados_suporte` | `Int64` | Inteiros entre 0 e 50 |
| `atrasos_6m` | `Int64` | Inteiros entre 0 e 6 |
| `fibra_optica`, `debito_automatico` | `Int64` | 0 ou 1 |
| Contrato e pagamento | `string` | Categorias canônicas descritas acima |
| `churn` | Inteiro binário | 0 ou 1, sem ausência; corrupção bloqueia o fluxo |

Antes dos tratamentos do dicionário, `validar_estrutura_visao` confere colunas necessárias, índices, identificadores preenchidos, unicidade cliente/corte e alvo. A falta de uma coluna é diferente de uma célula ausente: a primeira impede a execução; a segunda é diagnosticada nos preditores. As regras temporais e de rastreabilidade continuam nas etapas anteriores.

Os preditores recebem estes tratamentos, sem excluir clientes:

- Grafia com equivalência conhecida: aplicar o de-para.
- Número válido armazenado como texto numérico: converter ao tipo declarado. A conversão usa representação numérica com ponto decimal; formatos monetários e convenções regionais não são inferidos.
- Ausência real, espaços ou marcadores textuais `NA`, `N/A`, `NaN`, `None`, `null`, independentemente da caixa: representar como `pd.NA`.
- Tipo não interpretável, valor não finito, contagem fracionária, número fora da faixa ou categoria desconhecida: substituir a célula por `pd.NA`, preservando valor, cliente, linha, situação e regra na auditoria.

`Int64`, `Float64` e `string` são tipos pandas que permitem ausências. Os inválidos não são corrigidos por valor absoluto, corte no limite ou arredondamento. Zero é válido em contagens e indicadores; em mensalidade, viola o mínimo de 10. Booleanos nativos não são interpretados automaticamente como indicadores 0/1.

A Aula 2, p. 10, recomenda investigar a origem ou remover outliers comprovados. A decisão aprovada neste projeto foi isolar a célula inválida como ausente quando não há correção confiável, conservando o cadastro e a evidência. O material não determina uma conversão universal de todo extremo em mediana. Valores incomuns dentro do domínio permanecem válidos; a etapa 12 os sinaliza sem alterá-los.

| Campo | Ausentes na entrada desta validação | Inválidos convertidos em ausência | Ausentes na saída |
| --- | ---: | ---: | ---: |
| Mensalidade | 120 | 12 (oito `-85` e quatro `9999`) | 132 |
| Atrasos | 35 | 8 (valor `99`) | 43 |
| Chamados | 1.059 | 0 | 1.059 |
| Contrato | 25 | 0 | 25 |
| Pagamento | 20 | 0 | 20 |

Tempo de cliente e indicadores binários não apresentam valores inválidos nem ausências nesta população. Os valores acima se referem aos 4.976 clientes participantes, depois das etapas temporais.

Obrigatoriedade é registrada no protocolo. Esta validação não preenche valores: as ausências da tabela acima seguem para a imputação da etapa 11, ajustada somente no treino.

## O que mudou nas colunas

As informações originais permanecem na fonte e na auditoria. Na base atual, `data_chamado` foi substituída por `chamados_suporte`, e os demais campos dos registros mantidos são preservados, exceto os tratamentos aprovados. A base também contém:

- `chamados_excluidos_por_cronologia`: quantidade de datas retiradas de cada cliente na etapa 3. Distingue uma lista esvaziada pelo tratamento de um campo originalmente sem chamados.
- `data_corte`: data de referência da fotografia.
- `churn`: alvo inteiro binário, armazenado como `Int64` no programa.
- `tempo_cliente_meses`: meses completos desde a aquisição até o corte, sem alterar o alvo ou os outros campos.

Antes das exclusões posteriores, 17 clientes tiveram todas as datas de chamados removidas, além de 1.048 campos originalmente sem chamados. Esses vazios permanecem ausentes até a imputação, quando recebem zero por regra. As contagens no relatório referem-se à entrada e à saída de cada etapa.

**Esta base ainda não é a matriz final dos modelos:** os preditores estão completos, mas as categorias continuam em texto e não há escala. `churn` é o alvo supervisionado. Churn, datas de cancelamento e outras informações derivadas do desfecho ficam fora dos preditores, inclusive do agrupamento não supervisionado. IDs e metadados serão preservados para auditoria e separados dos atributos de modelagem.

## Saídas e leitura do relatório

Por padrão, são gerados três arquivos e três gráficos:

| Arquivo | Uso |
| --- | --- |
| `dados/tratados/base_churn_imputada.xlsx` | Base atual, com preditores imputados, na aba `base_tratada` |
| `dados/tratados/conjuntos_churn.xlsx` | Abas `treino`, `validacao` e `teste`, com seus atributos imputados, alvo e metadados para conferência |
| `relatorios/diagnostico_preparacao.xlsx` | Resumo, protocolo e evidências; relatório versionado no Git neste marco |
| `relatorios/graficos/*.png` | Gráficos da AED do treino; versionados junto com o relatório |

O relatório tem **quinze abas**: resumo e protocolo globais, mais evidências. A validação do dicionário ocupa duas abas dedicadas: categorias e números. A divisão acrescenta uma aba com a atribuição dos clientes; a imputação, a seleção de atributos e a estatística descritiva acrescentam uma aba cada:

| Aba | O que procurar |
| --- | --- |
| `00_resumo` | Indicadores antes/depois por problema; comece por aqui |
| `00_protocolo` | Datas, hipóteses, regras aprovadas, domínios, obrigatoriedade e pendências |
| `01_duplicatas` | As 20 cópias removidas e a linha da ocorrência mantida |
| `02_datas` | Os 15 valores antes/depois da padronização |
| `03_chamados` | Uma linha por cliente afetado: datas excluídas, quantidade e lista antes/depois; também registra datas fora da janela histórica quando houver |
| `04_cancelamentos` | Os dez registros excluídos, com suas datas originais |
| `05_elegibilidade_alvo` | Uma avaliação por cliente da entrada desta etapa: histórico, participação, motivo e alvo |
| `06_contagem_chamados` | Uma linha por cliente participante, com lista de entrada, datas da janela, contagem observada, ausências e sinalização de exclusões anteriores |
| `07_tempo_cliente` | Aquisição, corte e meses completos calculados para cada cliente participante |
| `08_categorias` | Campo e valor antes/depois de cada grafia corrigida, ausência ou categoria desconhecida; filtre `situacao` |
| `09_numericos` | Campo, valor antes/depois e regra de cada ausência, conversão textual ou número inválido; filtre `situacao` e `campo` |
| `10_divisao` | Cliente, linha da fonte, corte, alvo e conjunto atribuído; uma linha por cliente participante |
| `11_imputacao` | Cada célula preenchida: conjunto, cliente, linha da fonte, campo, valor, estratégia, taxa de ausência do campo e alerta; filtre `campo` e `conjunto` |
| `12_atributos` | Uma linha por atributo do treino: correlação com churn, atributo mais correlacionado, valor mais frequente, limites IQR, situação e decisão |
| `13_descritiva` | Uma linha por campo numérico e por categoria: posição, dispersão, assimetria, médias por classe e taxa de churn |

Na aba `05_elegibilidade_alvo`, filtre `elegivel = False` para ver os 14 clientes fora da população. Os 4.990 clientes avaliados aparecem ali; apenas os 4.976 participantes aparecem na base atual.

Cada evidência inclui cliente, arquivo e linha Excel da fonte. A numeração considera o cabeçalho na linha 1. Os índices originais são preservados em memória, mesmo depois das exclusões.

Nas abas `08_categorias` e `09_numericos`, cada linha descreve uma célula auditada e informa seu conjunto. O mesmo cliente pode aparecer por campos diferentes; a coluna `campo` identifica o motivo de cada ocorrência. Para ver somente os valores numéricos invalidados, filtre `situacao` por `fora_faixa`, `nao_inteiro` ou `tipo_invalido`. A numeração das abas identifica os assuntos; a ordem da execução está na main.

As quinze abas são reconstruídas juntas em cada execução. Os resultados anteriores de cada problema continuam representados, sem acumular abas antigas ou duplicadas. A fonte permanece intacta. O relatório `relatorios/diagnostico_preparacao.xlsx` é versionado no Git como registro do marco; as bases tratadas permanecem fora do Git e são reproduzíveis pela execução do programa.

Os arquivos dos conjuntos e da base completa podem ser desligados separadamente em `main.py`, pelos argumentos `salvar_conjuntos=False` e `salvar_base_completa=False` de `exportar_resultados`. A separação em memória e a auditoria continuam existindo. As abas completas exportadas contêm também metadados; o uso em modelos deve ocorrer por `X`, que possui sete colunas; `forma_pagamento` fica nas tabelas exportadas para o benchmark.

As bases numeradas e os arquivos principais das versões anteriores, como `base_churn_com_contagem_chamados.xlsx` e `base_churn_com_dicionario_tratado.xlsx`, são saídas antigas. O resultado atual é o arquivo principal indicado acima. A entrada do programa continua sendo a fonte original. Para gerar as intermediárias opcionais das quatro primeiras etapas, altere `salvar_intermediarias = False` para `True` em `main.py`; elas serão salvas em `dados/tratados/intermediarios/`.

## Como os arquivos Python se dividem

`main.py` mostra as seis fases principais. As funções coordenadoras ficam em `fluxos/`; a divisão fica em `divisao/` e a imputação, em `imputacao/`. As funções de cada regra continuam separadas em diagnósticos e tratamentos. As operações de entrada e saída usam os exportadores existentes; nenhuma regra de limpeza foi reescrita dentro da main.

```text
main.py                                  # sequência explícita
preparacao_dados/
├── leitura_dados.py                      # entrada
├── definir_protocolo_temporal.py         # convenções aprovadas
├── definir_dicionario_dados.py           # tipos, faixas e categorias fixos
├── definir_protocolo_atributos.py        # retirada, limiares e decisões de AED
├── validar_estrutura_visao.py            # colunas, chaves e alvo antes das correções
├── montar_abas_relatorio.py              # montagem do relatório compacto
├── exportar_base_excel.py                # saída da base; intermediárias opcionais
├── exportar_relatorio_excel.py           # escrita e formatação do Excel
├── exportar_graficos_aed.py              # gráficos da AED do treino
├── apresentar_estrutura_base.py          # dimensões e colunas no terminal
├── fluxos/                              # coordenadores das fases e consolidação da auditoria
│   ├── construir_visao_analitica.py      # etapas temporais e população
│   ├── preparar_conjuntos.py            # qualidade por conjunto e separação de X/y
│   ├── imputar_conjuntos.py             # um ajuste no treino, transform nos três conjuntos
│   ├── selecionar_atributos.py          # AED do treino e retirada nos três conjuntos
│   ├── consolidar_diagnosticos_conjuntos.py # contagens e evidências em um relatório
│   └── exportar_resultados.py           # coordenação das saídas
├── divisao/
│   ├── definir_protocolo_divisao.py      # proporções e semente
│   ├── dividir_conjuntos.py             # divisão estratificada
│   ├── verificar_divisao.py             # cobertura, conteúdo e isolamento
│   └── separar_atributos_alvo.py        # X, y, metadados e ordem das colunas
├── imputacao/
│   ├── definir_protocolo_imputacao.py    # mediana, moda ou zero por preditor
│   ├── converter_ausencias_para_nan.py   # pd.NA no formato aceito pelo SimpleImputer
│   ├── ajustar_imputacao.py             # fit somente no treino
│   ├── aplicar_imputacao.py             # transform e tipos restaurados
│   └── verificar_imputacao.py           # observados preservados e células preenchidas
├── diagnosticos/
│   ├── identificar_ausencias.py          # reconhecimento comum de marcadores
│   ├── identificadores/                  # identificar cópias e referências
│   ├── datas/                            # datas, população, chamados e tempo de cliente
│   ├── categorias/                       # identificar de-para e desconhecidos
│   ├── numericos/                        # avaliar tipo, integralidade e faixa
│   └── atributos/                        # correlações, extremos e estatística descritiva no treino
└── tratamentos/
    ├── duplicatas/                       # remover cópias e verificar
    ├── datas_aquisicao/                  # aplicar de-para e verificar
    ├── chamados/                         # filtrar datas e verificar
    ├── cancelamentos/                    # excluir registros e verificar
    ├── elegibilidade/                    # selecionar participantes, acrescentar alvo e verificar
    ├── tempo_cliente/                    # acrescentar meses completos e verificar
    ├── categorias/                       # aplicar de-para, isolar inválidos e verificar
    ├── numericos/                        # aplicar tipos e ausências identificados e verificar
    └── atributos/                        # retirar os aprovados e verificar a seleção
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
| Datas | `identificar_tempo_cliente_meses` | Calcular meses completos usando o corte e as aquisições já interpretadas |
| Tempo de cliente | `adicionar_tempo_cliente_meses` | Acrescentar a coluna numérica sem retirar a aquisição |
| Tempo de cliente | `verificar_tempo_cliente_meses` | Conferir o atributo e registrar o cálculo, preservando os campos existentes |
| Categorias | `identificar_categorias_fora_padrao` | Comparar os dois campos com o dicionário fixo e identificar correções e pendências |
| Categorias | `padronizar_categorias` | Aplicar o de-para e normalizar ausências, incluindo categorias desconhecidas |
| Categorias | `verificar_padronizacao_categorias` | Conferir as células alteradas e registrar ausências e categorias desconhecidas |
| Dicionário | `definir_dicionario_dados` | Centralizar os tipos, limites, de-para e obrigatoriedade do material |
| Estrutura | `validar_estrutura_visao` | Bloquear esquema, chave ou alvo inválidos antes dos tratamentos corretivos |
| Ausências | `identificar_ausencias` | Usar os mesmos marcadores explícitos em números e categorias |
| Números | `avaliar_campo_numerico` | Classificar uma coluna por tipo, integralidade, faixa ou ausência |
| Números | `identificar_violacoes_numericas` | Reunir as avaliações por campo sem alterar a base |
| Números | `normalizar_valores_numericos` | Aplicar os valores e tipos já identificados aos preditores |
| Números | `verificar_normalizacao_numerica` | Conferir domínio e preservação dos demais campos e registrar evidências |
| Imputação | `definir_protocolo_imputacao` | Definir mediana, moda ou zero para cada preditor |
| Imputação | `converter_ausencias_para_nan` | Representar `pd.NA` como `np.nan` para o `SimpleImputer`, sem mudar valores |
| Imputação | `ajustar_imputacao` | Aprender os valores somente no treino e bloquear valor fora do dicionário |
| Imputação | `aplicar_imputacao` | Aplicar `transform` e restaurar os tipos da entrada |
| Imputação | `verificar_imputacao` | Conferir que só as ausências mudaram e registrar cada célula preenchida |
| Atributos | `definir_protocolo_atributos` | Registrar manter ou retirar por preditor, limiares e decisões de redundância e ruído |
| Atributos | `identificar_relevancia_redundancia_ruido` | Medir correlação com churn, correlação entre atributos e extremos no treino |
| Atributos | `descrever_atributos_treino` | Resumir posição, dispersão e taxa de churn por categoria no treino |
| Atributos | `retirar_atributos_irrelevantes` | Tirar do X os campos aprovados e guardá-los nos metadados |
| Atributos | `verificar_selecao_atributos` | Exigir evidência de irrelevância, conferir os três conjuntos e registrar a decisão de cada atributo |
| Gráficos | `exportar_graficos_aed` | Gravar correlações, distribuições e churn por categoria do treino |

Os tratamentos usam as ocorrências identificadas; não procuram novamente o mesmo problema. As verificações confirmam condições essenciais da saída. A interpretação de todas as datas não é repetida a cada tratamento.

Cada verificação devolve `resumo`, `evidencias`, `regra` e `decisao`. `montar_abas_relatorio` reúne esses resultados. Assim, uma nova regra pode ser acrescentada à sequência sem criar outro coordenador ou escritor Excel por tratamento.

Para acrescentar uma regra, siga uma etapa existente: implemente a identificação em `diagnosticos/`, a transformação e a verificação em `tratamentos/`, com uma função por arquivo. Acrescente as três chamadas ao coordenador adequado: regras temporais em `construir_visao_analitica`, qualidade fixa dos preditores em `preparar_conjuntos`. Guarde a verificação em `resultados`. A main só precisa de nova chamada quando houver uma nova fase principal. Parâmetros aprendidos ficam fora do laço de preparação dos conjuntos, como em `imputar_conjuntos`: um único `fit` no treino e `transform` nos três conjuntos.

Preserve o índice original dos registros: `linha_excel = indice + 2`, considerando a indexação a partir de zero e o cabeçalho na linha 1. Reiniciar os índices entre as etapas quebra essa referência. As datas interpretadas uma vez representam a fonte; etapas seguintes devem considerar os clientes que ainda participam e as exclusões já identificadas. As funções existentes de contagem e tempo de cliente mostram esse alinhamento.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os 36 testes cobrem os tratamentos anteriores, a divisão, a imputação, a seleção de atributos e a AED. Na divisão: tamanhos, estratificação, cobertura, ausência de clientes compartilhados, reordenação da entrada, classes insuficientes, separação de X/y/metadados e repetição do fluxo. Na imputação: mediana e moda aprendidas no treino, zero nos chamados, observados e tipos preservados, bloqueio de mediana fracionária, alerta de ausência acima de 20% e ajuste inalterado quando validação ou teste mudam. Na seleção: par redundante mantido, pagamento retirado e preservado nos metadados, bloqueio de retirada sem evidência, extremo, rótulo conflitante e estatística descritiva. Os gráficos são gravados em pasta temporária nos testes; nos testes do fluxo, as exportações são simuladas.

Os comentários seguem um padrão curto: a descrição da função informa sua finalidade; comentários antes de blocos explicam decisões como preservação do índice, janelas, ausências e conferências. Funções simples mantêm somente sua descrição. Os comentários não acrescentam regras de tratamento.

## Pendências e limites desta versão

- Preparar codificação (one-hot com `handle_unknown='ignore'`) e escala ajustadas no treino, adequadas a cada modelo (Aula 3, p. 4).
- Persistir o objeto de imputação ajustado e criar o fluxo de previsão para dados novos.
- Na modelagem, rodar o benchmark com todas as variáveis, incluindo `forma_pagamento`, e revisar a redundância entre mensalidade e fibra; investigar na origem o piso de 49,90 e o teto de 72 meses.
- Opcionais registrados: mediana de mensalidade por grupo de fibra, indicador de ausência ou `KNNImputer` (Aula 2, pp. 7 e 15), discretização e balanceamento somente no treino (Aula 3).
- A base atual tem uma fotografia temporal. Uma avaliação estritamente fora do tempo exige fotografias de outras datas; isso não é obtido simplesmente separando clientes desta mesma fotografia.
- A Aula 3 utiliza uma VF3 e tamanhos próprios do exemplo. Seus totais e métricas não são metas a copiar para a VF2 após os filtros deste projeto.
- Preparar os atributos adequados a cada tarefa, separar alvo e metadados e só então avançar para modelagem.

Até a etapa 9, as regras são fixas e aprovadas; a etapa 11 é a primeira com parâmetros aprendidos, sempre no treino. O marco atual encerra a preparação e a AED: três conjuntos completos, sete preditores selecionados, auditoria de cada estimativa e gráficos do treino. Codificação, escala e modelagem formam a próxima fase.
