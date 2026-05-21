Projeto gerado a partir do cockpit_v1_5_corrige_percentual_abandono_v2 com integração do cliente Sky | Negocie Online.

O que foi incluído:
- Cliente Sky | Negocie Online no cockpit.
- Template templates/sky_negocie_online.html.
- Rotas:
  /cliente/sky-negocie-online
  /cliente/sky-negocie-online/painel
  /cliente/sky-negocie-online/painel/api
- Controle de acesso por usuário/cliente preservando admin e gerber com acesso total.
- Dependências adicionais no requirements.txt: numpy, folium e branca.

Importante:
- A base esperada para o painel da Sky é data/Base_Dashboard_Sky.xlsx.
- A correção do percentual de abandono do cockpit base foi mantida.

V2.5 - Funil Comparativo Sky
- Incluída nova aba "Funil Comparativo" dentro do painel Sky Negocie Online.
- A visão compara dois CampaignId usando os filtros atuais de data e faixa de atraso.
- Os selects Campanha A e Campanha B usam os CampaignId disponíveis na base Excel.
- Métricas calculadas: Mailing, Discado, Atendidas, CPC, Acordo, Variação B/A - 1, Hit Rate, LOC, Conversão e Acordo/Mailing.
