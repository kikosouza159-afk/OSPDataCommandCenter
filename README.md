# Cockpit V1.5

Login animado + menu executivo de clientes + painel TALENTOS integrado.

## O que mudou na V1.5
- O card TALENTOS agora abre o projeto `locator_dashboard_flask_v30_tabulacao` dentro do Cockpit.
- Rotas internas da TALENTOS:
  - `/cliente/talentos/painel`
  - `/cliente/talentos/painel/comparativo`
  - `/cliente/talentos/painel/tabulacao`
- Visual do painel TALENTOS ajustado para combinar com o fundo tecnológico do Cockpit.
- Botão de retorno para o menu principal.

## Login padrão
- Usuário: admin
- Senha: 123456

## Base de dados
Coloque o arquivo Excel em:

```bash
data/base.xlsx
```

Ou configure uma variável de ambiente:

```bash
EXCEL_PATH=C:\caminho\base.xlsx
```

## Rodar localmente
```bash
pip install -r requirements.txt
python app.py
```

Acesse:

```bash
http://127.0.0.1:5000
```

## Render
Build Command:
```bash
pip install -r requirements.txt
```

Start Command:
```bash
gunicorn app:app
```


## Ajuste V1.5
- Corrigido conflito CSS da classe `.grid` que deformava os gráficos.
- Containers de gráficos e tabelas travados para evitar estouro visual.


## Ajuste V2 rápido

Melhorias aplicadas no painel Sky:

- Cache da leitura do Excel. O arquivo só é lido novamente quando for alterado.
- Mapa Brasil carregado sob demanda, evitando montar Folium em todo filtro.
- Hora a Hora carregado sob demanda, evitando montar tabelas/gráficos quando a aba não está aberta.
- Gráficos Chart.js sem animação para troca/renderização mais rápida.
- Funil comparativo otimizado, consolidando CampaignId em uma única agregação.


## V3 - Campanha B fixa Churn / Pré Churn e correção Daily

Alterações:
- Campanha B do Funil Comparativo agora possui apenas as opções fixas: Churn Fixo e Pré Churn Fixo.
- Valores fixos da Campanha B estão chumbados no app.py usando a média dia do print.
- Campanha A usa CampaignId da base, com padrão 202 quando existir.
- Campanha A é calculada como média dia para comparar corretamente contra os fixos.
- Corrigido resize dos gráficos da visão Daily quando a aba é alternada.

Valores fixos B:
Churn: Mailing 41.370, Discado 133.923, Atendidas 4.108, CPC 837, Acordo 246.
Pré Churn: Mailing 23.113, Discado 34.501, Atendidas 1.766, CPC 500, Acordo 165.
