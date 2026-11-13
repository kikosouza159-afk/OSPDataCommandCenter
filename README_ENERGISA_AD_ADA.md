# Energisa | Comparativo diário AD × ADA

## Status
- Banco: Neon, projeto **Cockpit Indicadores**.
- Nova tabela: `assistpay.energisa_ad_ada_diario`.
- Base importada em 13/11/2026: **543 linhas**, **17 campanhas**, **64 dias**, de 01/09/2026 a 13/11/2026.
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

## Atualização
Importação inicial efetuada de 543 linhas em Neon. A API consulta o banco a cada acesso, sem arquivo estático.
Novas cargas devem usar `INSERT ... ON CONFLICT (data, campaign_id) DO UPDATE` validado e executado pelo ETL seguro para evitar duplicação. Não publicar dados de clientes no GitHub.
