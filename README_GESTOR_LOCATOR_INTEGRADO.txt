GESTOR LOCATOR INTEGRADO

Painel incluído no cockpit em /cliente/gestor-locator/painel.

Base Excel:
- data/base_gestor_locator.xlsx

Para atualizar o painel, substitua esse arquivo mantendo o cabeçalho.
Campos esperados principais:
Data, Hora, Cliente, NomeCampanha, CampaignId, WayInboundCampaignId, Mailing, AD, ATH, Tentativas, Atendidas, Transferencia, Sucesso_Negocio, Perda, Abandono, Custo.

Regra de Mailing/AD/ATH:
- máximo diário por Cliente + Locator + CampaignId + WayInboundCampaignId;
- quando houver mais de um dia, média dos máximos diários;
- consolidado soma o resultado por locator.
