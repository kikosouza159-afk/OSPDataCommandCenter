KOVI - Painel de Disparo WhatsApp

Base: data/base_kovi_whatsapp.xlsx
Aba: Disparos_WhatsApp (a primeira aba também é aceita)

Colunas esperadas:
- Arquivo
- Data do Disparo
- Entregues
- Enviados
- Taxa

Empresa/Praça e Janela são derivadas automaticamente do campo Arquivo.
Exemplo: OLLOS SP - 13:00 -> Empresa SP, Janela 13:00.

Rota: /cliente/kovi/painel
Filtros: período, empresa, arquivo e janela.
