SKY | VISÃO UNIQUE
==================

A visão Daily passa a exibir, logo abaixo do fluxo inicial, o bloco "Visão Unique".

Aba esperada em data/Base_Dashboard_Sky.xlsx:
  Unique

Aliases também aceitos:
  Funil_Unique
  Visao_Unique
  Visão Unique

Estrutura esperada:
DATA | Mailing | Discado | Contato | Cpc | Acordo | Valor_Acordo | Penetracao | Alo | Loc | Conversao

Exemplo:
2026-08-01 | 33149 | 33149 | 7923 | 1693 | 130 | R$ 24.646,35 | 100% | 23,9% | 21,37% | 7,68%

Regras:
- O filtro de DATA da visão Daily também filtra a visão Unique.
- Faixa de atraso e CampaignId não são aplicados à Unique, pois não existem na estrutura informada.
- No consolidado de vários dias, volumes e Valor_Acordo são somados.
- Penetração = Discado / Mailing
- Alô = Contato / Discado
- Localização = CPC / Contato
- Conversão = Acordo / CPC
- Se a aba Unique ainda não existir, o painel continua funcionando e mostra apenas um aviso no bloco Unique.
