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
- Origem: arquivo diário tabulado com 11 colunas (`Date`, `CampaignId`, `nomecampanha`, `Logados`, `Tentativas`, `Atendidas`, `Cpc`, `Acordo`, `Hangup`, `Mailing`, `Agente`).
- A chave (data, campanha) impede repetição entre cargas. A base atual não continha chaves repetidas.
- Totais: soma por campanha e dia, após granularidade diária estabelecida.
- Mailing e Logados: a base diária já possui uma linha por campanha/dia, eliminando repetição de registros horários. O somatório entre campanhas pode contar os mesmos operadores, portanto não é um total de pessoas únicas.
- Média dia: para **cada indicador** o denominador corresponde somente aos dias com valor > 0. Zeros não entram.
- Taxas e produtividade: `Spin = tentativas / mailing`, `Hit Rate = atendidas / tentativas`, `Taxa CPC = cpc / atendidas`, `Conversão = acordo / cpc`, `% Hangup = hangup / atendidas`, `Acordos por logado = acordo / logados`.
- Em Total, taxas calculadas sobre volumes consolidados. Em Média dia, **cada volume tem sua própria média sem zeros**, e as taxas são recalculadas a partir desses volumes médios (conforme benchmark executivo).
- Na evolução e detalhamento diário, pontos e linhas representam dados reais daquele dia; o gráfico mostra também a média do mês de cada tecnologia, excluindo zeros por indicador.
- O popup dos pontos do gráfico mostra a data, valor do dia, média mensal do respectivo mês (AD e ADA independentes) e diferença percentual do dia em relação à média. 
- Fórmula da eficiência: `Eficiência = Acordos / Mailing × 100` (não Acordos / Tentativas).
- Filtros independentes de mês e campanhas para AD e ADA, permitindo comparativos entre meses diferentes.
- Padrão inicial de benchmark: campanha AD 11 (setembro/2026) contra campanha ADA 385 (novembro/2026).
- Matriz AD × ADA com dias trabalhados, indicadores absolutos, taxas, eficiência e produtividade por agente.
- A seção "Insights executivos" foi removida conforme solicitado; as informações comparativas permanecem nos cards, matriz, funil e gráfico.
- CSV: exportação da base filtrada com as 11 colunas recebidas.

## Atualização
Importação inicial efetuada de 543 linhas em Neon. A API consulta o banco a cada acesso, sem arquivo estático.
Novas cargas devem usar `INSERT ... ON CONFLICT (data, campaign_id) DO UPDATE` validado e executado pelo ETL seguro para evitar duplicação. Não publicar dados de clientes no GitHub.
