# Energisa | Comparativo diário AD × ADA

## Status
- Banco: Neon, projeto **Cockpit Indicadores**.
- Nova tabela: `assistpay.energisa_ad_ada_diario`.
- Base histórica atualizada em 13/11/2026: **2.368 linhas**, **17 campanhas**, **266 dias com dados**, de 02/01/2026 a 13/11/2026.
- Dados da Energisa NÃO estão presentes no repositório GitHub.
- A antiga tabela `assistpay.energisa_ad_ada_snapshot` foi preservada, mas não é mais a fonte do painel.

## Cockpit
- Card: **ENERGISA | AD × ADA**.
- Página: `/cliente/energisa/painel`.
- API privada: `/cliente/energisa/painel/api`.
- Código: `energisa_ad_ada.py` e `templates/energisa_ad_ada.html`.
- Reutiliza login, ACL por cliente, identidade visual OLOS e `ASSISTPAY_NEON_DATABASE_URL`.
- Usuários não administradores precisam ser autorizados ao cliente Energisa na aba Admin.
- A API retorna dados diários exclusivamente; a visão hora a hora está desativada aguardando fonte apropriada.

## Esquema SQL
```sql
CREATE TABLE IF NOT EXISTS assistpay.energisa_ad_ada_diario (
  data date NOT NULL,
  campaign_id integer NOT NULL,
  nome_campanha text NOT NULL,
  agente varchar(3) NOT NULL CHECK (agente IN ('AD', 'ADA')),
  logados integer NOT NULL DEFAULT 0,
  tentativas bigint NOT NULL DEFAULT 0,
  atendidas bigint NOT NULL DEFAULT 0,
  cpc bigint NOT NULL DEFAULT 0,
  voicemail bigint NOT NULL DEFAULT 0 CHECK (voicemail >= 0),
  acordo bigint NOT NULL DEFAULT 0,
  hangup bigint NOT NULL DEFAULT 0,
  mailing bigint NOT NULL DEFAULT 0,
  PRIMARY KEY (data,campaign_id),
  CHECK (logados>=0 AND tentativas>=0 AND atendidas>=0 AND
         cpc>=0 AND acordo>=0 AND hangup>=0 AND mailing>=0)
);
CREATE INDEX IF NOT EXISTS idx_energisa_ad_ada_agente_data
 ON assistpay.energisa_ad_ada_diario (agente,data DESC);
```

## Cálculos
- Origem: arquivo diário tabulado com 12 colunas (`Date`, `CampaignId`, `nomecampanha`, `Logados`, `Tentativas`, `Atendidas`, `Cpc`, `VoiceMail`, `Acordo`, `Hangup`, `Mailing`, `Agente`).
- A chave (data, campanha) impede repetição entre cargas. A base atual não continha chaves repetidas.
- Totais: soma por campanha e dia, após granularidade diária estabelecida.
- Mailing e Logados: a base diária já possui uma linha por campanha/dia, eliminando repetição de registros horários. O somatório entre campanhas pode contar os mesmos operadores, portanto não é um total de pessoas únicas.
- Média dia: para **cada indicador** o denominador corresponde somente aos dias com valor > 0. Zeros não entram.
- Taxas e produtividade: `Spin = tentativas / mailing`, `Hit Rate = atendidas / tentativas`, `Taxa CPC = cpc / atendidas`, `Conversão = acordo / cpc`, `VoiceMail / Atendidas % = voicemail / atendidas × 100`, `VoiceMail / CPC % = voicemail / cpc × 100`, `% Hangup = hangup / atendidas`, `Acordos por logado = acordo / logados`.
- Em Total, taxas calculadas sobre volumes consolidados. Em Média dia, **cada volume tem sua própria média sem zeros**, e as taxas são recalculadas a partir desses volumes médios (conforme benchmark executivo).
- A evolução mostra os valores reais por dia. As séries AD e ADA são alinhadas pelo número de dias decorridos desde o início de seus períodos independentes. Linhas tracejadas mostram a média mensal completa para cada campanha selecionada, mesmo quando o recorte atravessa vários meses.
- O popup mostra a data, valor do dia, média do mês calendário inteiro (para as campanhas selecionadas, sem zeros) e diferença percentual do dia. A média mensal continua constante mesmo ao selecionar uma semana; em meses diferentes cada trecho usa sua própria média. 
- Fórmula da eficiência: `Eficiência = Acordos / Mailing × 100` (não Acordos / Tentativas).
- Filtros independentes de **data inicial e final** e campanhas para AD e ADA, permitindo comparativos entre períodos e meses diferentes. Alterar uma data não modifica a outra tecnologia.
- Padrão inicial de benchmark: campanha AD 18 (01 a 30/09/2026) contra campanha ADA 383 (03 a 13/11/2026), conforme os dados disponíveis; cada intervalo pode ser personalizado.
- Matriz comparativa em tabela executiva AD/ADA com variações relativas, incluindo VoiceMail e seus dois percentuais.
- A seção "Insights executivos" foi removida conforme solicitado; as informações comparativas permanecem nos cards, matriz, funil e gráfico.
- CSV: exportação da base filtrada com as 12 colunas recebidas, incluindo VoiceMail após CPC.

## Layout executivo, inspirado no comparativo mensal AssistPay (13/11/2026)
- **6 cards**: Acordo, Eficiência %, Contato (Atendidas), CPC, VoiceMail e Agentes (média/dia).
- Cada card mostra AD → ADA, delta percentual relativo e sinalização visual, sem arredondar os dados antes de calcular os deltas.
- **Funil AD** azul e **Funil ADA** laranja, lado a lado no desktop, com 6 etapas: Mailing médio, Tentativas, Atendidas, CPC, VoiceMail e Acordo; taxas incluindo VM/Atendidas e VM/CPC e produtividade por AGV aparecem abaixo do funil.
- **Mailing médio no funil** é sempre média diária com zeros excluídos; os demais volumes refletem o modo Total / Média dia.
- Cada funil contém uma coluna de variação ADA × AD por etapa; as duas colunas permitem leitura de cada funil separadamente.
- **Visão comparativa dos indicadores** substitui a antiga matriz em barras por tabela executiva AD, ADA e variação relativa (%), com campanha, dias trabalhados, mês, volumes, taxas e produtividade.
- Indicadores reais disponíveis na base: Mailing, Tentativas, Atendidas, CPC, VoiceMail, Acordo, Hangup, Logados, Spin, Hit Rate, Taxa CPC, VoiceMail / Atendidas %, VoiceMail / CPC %, Conversão, Hangup %, Eficiência (Acordos/Mailing), e produtividade por agente. Pagamento não é exibido, pois não existe na fonte.
- Filtros AD e ADA de data inicial, final e campanhas continuam independentes; a evolução diária e o tooltip da média mensal permanecem abaixo dos funis.
- Base continua no Neon via API autenticada e controle de permissões. A coluna VoiceMail foi adicionada ao banco em 13/11/2026.

## Ajuste de indicadores ERO (13/11/2026)
- Benchmark padrão: AD campanha **18** (setembro/2026) versus ADA campanha **383** (novembro/2026), com filtros de período e campanhas editáveis.
- Média dia: cada volume é calculado como média dos dias com valor > 0, e as taxas são derivadas das médias não arredondadas.
- Renderização de contagens, Mailing, AGV e produtividade em números inteiros; Spin e demais percentuais com uma casa decimal, Eficiência % com duas casas. O delta percentual sempre usa os números originais, sem arredondamento prévio.
- Ordem da matriz ERO: Campanha; Dias Trabalhados; Média Dia; Mailing; Agentes; Tentativas; Atendidas; CPC; VoiceMail; Acordo; Spin; Hit %; CPC %; VoiceMail / Atendidas %; VoiceMail / CPC %; Acordo %; Efic %; Mailing / AGV; Tentativas / AGV; Atendidas / AGV; CPC / AGV; Acordo / AGV.
- Funil AD e ADA, do Mailing para baixo: Mailing médio → Tentativas → Atendidas → CPC → VoiceMail → Acordo. Agentes, taxas e produtividade por AGV exibidos no próprio painel do funil, abaixo das etapas.
- Pagamento retirado da versão executiva ERO, porque não existe dado de pagamento nessa tabela.
- Valores validados diretamente no Neon: AD 6 dias, Mailing 329.344, Agentes 21, Tentativas 189.551, Atendidas 7.961, CPC 5.381, Acordos 129; ADA 10 dias, Mailing 204.009, Agentes 23, Tentativas 215.800, Atendidas 13.166, CPC 8.784, Acordos 379.
- Código revisado em 13/11/2026: 6 cards, 6 etapas em cada funil, 7 indicadores na seção de taxas, matriz com VoiceMail e dois novos percentuais, gráfico diário e exportação CSV.

## Nova carga com VoiceMail (13/11/2026)
- Arquivo revisado: 543 linhas, 17 campanhas, 64 dias (01/09 a 13/11/2026).
- Coluna nova: `voicemail BIGINT NOT NULL DEFAULT 0 CHECK (voicemail>=0)`.
- Carga realizada com `INSERT ... ON CONFLICT (data, campaign_id) DO UPDATE` para atualizar **todos os 543 registros**, não só a nova coluna.
- Validação no Neon: soma de VoiceMail **2.162.049**; Tentativas **80.357.818**; Atendidas **4.487.197**; CPC **2.725.771**; Acordos **120.065**; sem duplicidade de chave.
- Taxas: `taxaVoiceMailAtendidas = 100 * voicemail / atendidas`, `taxaVoiceMailCpc = 100 * voicemail / cpc` (se o denominador for zero, retorna 0).
- Na visão Média dia, cada volume (inclusive VoiceMail) exclui dias zerados; as duas taxas são recalculadas usando os respectivos volumes médios não arredondados.
- A API entrega `voicemail` aos clientes autorizados e o frontend exibe VoiceMail nos cards, funis, matriz, gráfico, detalhamento diário, por campanha e CSV.
- Não publicar o arquivo operacional no repositório público.

## Expansão do histórico (13/11/2026)
- Fonte: nova base colada `Texto colado(20261113-163938).txt`, com **2.368 linhas** de **17 campanhas** e **266 dias distintos** de 02/01/2026 a 13/11/2026.
- O histórico novo foi aplicado em **uma transação de sete lotes** via `INSERT ... ON CONFLICT (data,campaign_id) DO UPDATE`, com 2.368 linhas afetadas e sem remoção de registros pré-existentes.
- Foram normalizados **dois `NULL` na coluna Mailing para zero**, pois o campo no banco é obrigatório e o painel exclui zeros das médias.
- Validação SQL após carga: 2.368 registros, 2.368 chaves únicas, 17 campanhas, 266 datas.
- Totais validados contra a fonte: Tentativas `489.760.810`; Atendidas `20.469.274`; CPC `11.528.285`; VoiceMail `8.540.440`; Acordos `380.834`; Hangup `187.038`; Mailing `441.636.580`.
- Primeiro dia disponível em AD: **02/01/2026**. Primeiro dia disponível em ADA: **07/08/2026**.
- O painel já obtém os limites de data dinamicamente na API, portanto novos meses estão acessíveis nos seletores sem alteração de código ou deploy. O benchmark padrão permanece AD 18 em setembro versus ADA 383 em novembro.
- O teste de renderização com os 2.368 registros reais confirmou os seis cards, os dois funis, a tabela, o gráfico e seleção de janeiro no AD.
- Os dados brutos do cliente não são publicados no GitHub.

## Redesign tecnológico e interativo do painel (13/11/2026)
- **Fundo padrão preservado**: a página Energisa passou a incluir `templates/background.html`, o mesmo componente utilizado em `templates/dashboard.html`. A grade, as linhas elétricas, os orbes, o scanline e a chuva de dados mantêm seu aspecto original. A CSS está encapsulada no template Energisa; os outros clientes não foram alterados.
- **Interação do fundo**: adicionada paralaxe de baixa amplitude vinculada ao ponteiro apenas na Energisa, com `requestAnimationFrame`. Preferência de acessibilidade por movimentos reduzidos desativa as animações complementares.
- **Novo cabeçalho executivo** com status de fonte, último dia disponível calculado dos registros carregados, período selecionado e navegação rápida por Filtros, Visão geral, Funis, Evolução e Detalhamento.
- **Filtros preservados** para AD e ADA com datas/campanhas independentes; novos atalhos `Últimos 7 dias`, `Mês mais recente` e `Histórico` respeitam as campanhas selecionadas. Os filtros de data não são sincronizados entre tecnologias.
- **Cards executivos acionáveis** com 6 KPIs e gráficos de tendência AD azul × ADA laranja obtidos das últimas 16 linhas diárias reais de cada tecnologia. Não há valores simulados nem animação de dados fictícios. Ao clicar num card, o indicador correspondente é aberto no gráfico diário.
- **Funis interativos** mantêm as 6 etapas existentes e as cores por tecnologia. Cada etapa pode abrir sua série diária. VoiceMail aparece explicitamente como *classificação*, com conector visual pontilhado para não sugerir uma conversão sequencial CPC → VoiceMail → Acordo.
- **Matriz comparativa** agora permite abrir o indicador no gráfico por clique ou teclado; os deltas de VoiceMail e respectivas taxas utilizam sinalização visual favorável quando há queda.
- **Gráfico exploratório** ganhou 4 botões rápidos, controle independente de linhas das médias mensais, realce das curvas, navegação pela seleção de indicadores e o popup anterior comparando dia × média do mês calendário (mantido).
- **Performance e acessibilidade**: transições discretas, `prefers-reduced-motion`, estados de foco visíveis, controle de movimentos e animações locais sem bibliotecas externas.
- **Backend preservado**: nenhuma alteração em `energisa_ad_ada.py`, controle de acesso, banco Neon, estrutura diária, cálculos ou exportação CSV por causa do redesign.
- **Validação** com 2.368 registros reais do Neon: 6 cards, 6 sparklines, 6 etapas em cada funil, 25 linhas de matriz, popup e gráfico diário, filtro AD de janeiro/2026, atalhos de período, modo Total/Média dia e habilitar/desabilitar as linhas de média, sem erro de JavaScript no teste de renderização.
- **Deploy**: alterações estão no GitHub `main`; publicação no Render não foi verificada diretamente.

## Nova aba Visão dia a dia e sidebar recolhível (13/11/2026)
- Criada a aba **Visão dia a dia** ao lado de **Comparativo executivo**, preservando a estrutura executiva da aba existente, o fundo original `background.html`, as permissões e as campanhas/datas independentes AD/ADA.
- Gráfico AD azul versus ADA laranja com seletor de **22 indicadores** e atalhos para Acordos, CPC, VoiceMail, Hangup/Atendidas e Hangup/Discagens, incluindo popup por ponto e linhas tracejadas das médias do mês.
- **Heatmap com AD e ADA separados**, com cada indicador em uma linha e todos os dias do período nas colunas. Os cabeçalhos agrupam os dias por mês; dias sem dados aparecem explicitamente como lacunas.
- Grupos do heatmap: **Volumes (8)**, **Taxas (9)**, **Produtividade / AGV (5)** e **Todos (22)**. Cada célula mostra valor do dia, delta percentual vs média do mês; hover/foco/título informa as referências e clique abre seu indicador no gráfico. Cores mostram acima/próximo/abaixo da média, sem declarar automaticamente que uma elevação é boa.
- Cálculo da referência mensal considera **o mês calendário completo das campanhas selecionadas**, independente do recorte de data dos filtros. Volumes usam a média dos dias com valor positivo; taxas, Spin e produtividade são calculados como **razão dos totais mensais**, sem média simples dos percentuais.
- Incluídos os indicadores:
  - **Hangup / Atendidas (%)**: `100 × hangup / atendidas` (chave existente `taxaHangup`, agora com nome explícito).
  - **Hangup / Discagens (%)**: `100 × hangup / tentativas` (nova chave `taxaHangupTentativas`).
  - Em ambos os casos, denominador zero produz 0 e a média mensal é ponderada pelos respectivos volumes.
- Tabela analítica dia a dia: data, tecnologia, oito volumes, Spin, oito taxas percentuais e cinco indicadores por agente. Mostra valores reais do dia, independente da opção Total / Média dia do comparativo.
- Adicionado botão **Recolher / Expandir menu lateral** no canto superior do menu esquerdo, com ícone «/», classes CSS de largura compacta, rótulos acessíveis e preferência salva em `localStorage`. Não altera menu ou fundo de outras páginas.
- Os seletores de campanha e datas e o compartilhamento de dados Neon permanecem únicos entre as duas abas. A API `energisa_ad_ada.py` e a tabela Neon não foram alteradas nesta atualização de interface.
- Validação em JavaScript com os 2.368 registros: seis cards do comparativo, dois funis, a aba diária com 22 linhas de métricas nos heatmaps AD/ADA, o gráfico diário com os novos percentuais, filtro de taxa, troca de abas, grupos de heatmap e recolher/expandir menu. Executados sem erro de JavaScript.
- Verificação numérica diretamente no Neon: AD 18 (setembro) Hangup/Atendidas `0,1382%`, Hangup/Discagens `0,0058%`; ADA 383 (novembro) `0,5350%` e `0,0323%`, respectivamente.
- O deploy do Render não foi verificado diretamente; código publicado no GitHub `main`.

## Visão diária individual por campanha e correção do seletor (13/11/2026)
- O gráfico da aba **Visão dia a dia** exibe **uma campanha por vez**, sem comparar AD e ADA no mesmo gráfico. O dropdown **Campanha / tecnologia** fica ao lado do seletor de indicador e lista somente as campanhas escolhidas nos filtros gerais (AD e ADA).
- O gráfico usa a data real dos registros disponíveis para definir o eixo horizontal, evitando espaço vazio de dias sem produção nas pontas. Cores permanecem **AD azul / ADA laranja**; rótulos dos valores aparecem junto aos pontos (amostrados em recortes mais longos para não poluir a leitura).
- Popup individual: **data**, **nome completo da campanha**, **indicador**, **valor do dia**, **média do mês calendário completo dessa campanha** e **delta percentual**. O cálculo não mistura campanhas diferentes.
- Médias mensais do gráfico: volumes calculados pela **média de dias com valor positivo**; taxas, conversões, Spin e produtividade por agente calculados pela **razão dos volumes totais mensais**, usando todos os dias do mês mesmo quando o intervalo filtrado for menor.
- Quatro cards do gráfico agora tratam **apenas da campanha selecionada**: Último dia, Média do mês, Maior valor diário e Dias com registro.
- Os **22 indicadores** estão disponíveis nos botões rápidos em três grupos (Volumes, Taxas/Conversões e Produtividade/AGV), além do dropdown completo de indicadores. Ambos permanecem sincronizados.
- **Hotfix de sobreposição visual:** o painel de filtros usa camada superior às abas, com `z-index` explícito, dropdown com camada elevada e regra para `.campaign-picker[open]`. Assim o menu de seleção de campanhas abre por cima de **Comparativo executivo / Visão dia a dia**, sem ficar encoberto.
- Funis, gráfico comparativo anterior, heatmaps AD e ADA, tabela analítica, permissões e API de dados são preservados sem alteração.
- Teste em mock DOM com os **2.368 registros reais do Neon** confirmou campanha AD 18 com 6 pontos, ADA 383 com 10 pontos, gráfico com uma única série, 22 filtros rápidos, popup individual e Hangup/Discagens com média de novembro `0,032278...`%, em conformidade com cálculo do banco.
- Código atualizado na branch `main`. O deploy no Render e a revisão visual no navegador de produção ainda não foram confirmados.

## Regra de sinalização VoiceMail: Energisa (13/11/2026)
- **VoiceMail é contato válido e conta como CPC para a Energisa**. Crescimento de VoiceMail é considerado favorável e deve usar **verde**. Redução deve aparecer em **vermelho**. Volume, VoiceMail/Atendidas e VoiceMail/CPC usam a mesma lógica de sinalização de variação positiva/negativa no painel.
- Corrigidas inversões antigas nas funções `renderKpis`, `renderMatrix` e `renderFunnel` do template `templates/energisa_ad_ada.html`. Ajustados os textos do funil e tooltip para refletir o significado comercial do indicador.
- **Não somar VoiceMail ao CPC novamente**: o dado de CPC da fonte já inclui essa classificação. A mudança é de interpretação e apresentação, não de totalização ou da regra de ingestão no Neon.
- A participação VoiceMail/Atendidas permanece informativa. No relatório executivo, uma redução dessa participação não é classificada automaticamente como ganho de qualidade; o principal sinal favorável é o aumento de contatos válidos.
- Relatório HTML da análise executiva de 12/11/2026 foi atualizado com narrativas compatíveis e cores favoráveis para crescimento de VoiceMail.
- Validação da ERO (campanhas AD 18 vs ADA 383, médias diárias dos filtros padrão): VoiceMail aproximadamente `4.317` vs `7.491`, crescimento de `73,5%` em verde, inclusive nas duas taxas da matriz.

## Atualização
Importação inicial de 543 registros de setembro a novembro e atualização histórica posterior para 2.368 registros de janeiro a novembro de 2026. A API consulta o Neon a cada acesso, sem arquivo estático.
Novas cargas devem usar `INSERT ... ON CONFLICT (data, campaign_id) DO UPDATE` validado e executado pelo ETL seguro para evitar duplicação. Não publicar dados de clientes no GitHub.
