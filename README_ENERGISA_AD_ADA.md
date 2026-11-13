# Energisa | Comparativo AD × ADA (Cockpit OLOS)

## Tela
- Menu do Cockpit: **ENERGISA | AD × ADA**
- URL: `/cliente/energisa/painel`
- API autenticada: `/cliente/energisa/painel/api`
- Logo oficial da OLOS: `static/img/logo-olos-laranja.png`
- Acesso: controle central de clientes do Cockpit. Administradores têm acesso; demais usuários dependem de liberação na aba Admin.

## Dados e segurança
- Fonte atual: planilha Energisa de 13/11/2026, com 8.005 registros e 25 campanhas.
- Armazenamento: Neon (mesma base já usada pelo Cockpit), tabela `assistpay.energisa_ad_ada_snapshot`.
- Estrutura: uma linha `snapshot_id=1`, `payload jsonb` contendo `meta`, `campaigns` e `rows`.
- Os registros individuais **não** estão versionados no GitHub; a API exige sessão/autorização e responde com `Cache-Control: no-store`.
- Banco: conexão `ASSISTPAY_NEON_DATABASE_URL`, já utilizada pelo Cockpit.

## Regras
- **Total:** soma por hora das métricas de volume, com Mailing/Logados iguais ao MAX por campanha/dia.
- **Média dia:** média de cada métrica por tecnologia, calculada apenas sobre dias em que o valor diário daquela métrica é **maior que zero**. O denominador pode diferir entre métricas.
- **Taxas e TMA na média dia:** média aritmética dos valores diários válidos (>0), não média das taxas horárias e não divisão dos totais médios.
- **Hora a hora no modo média:** cada hora mostra sua média entre os dias em que aquele indicador foi positivo, com os registros de Mailing/Logados deduplicados por campanha/dia/hora.
- O seletor vale para cards, funil, indicadores, linha horária e CSV. No detalhamento diário, cada linha continua representando seu próprio dia.
- Telecom e %Hangup seguem sinalizados como dados a validar.

## Atualização futura
Esta versão consulta um snapshot no Neon, sem ETL automático. Para atualizar o banco com próximas versões da planilha, implemente uma carga autenticada no ETL_Cockpit ou processo de atualização controlado, mantendo a mesma estrutura JSON e sem publicar a planilha no repositório.

## Validações efetuadas
- Sintaxe JavaScript aprovada
- Teste numérico de média com zero excluído e Mailing deduplicado aprovado
- Estrutura da tabela no Neon validada
- Publicação do código na branch main
- Deploy Render: depende da configuração de deploy automático e não foi verificado via workspace Render.
