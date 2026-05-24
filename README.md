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


## V5 - Funil Realizado e Projeção Linear

Alteração na visão Funil Comparativo da Sky:

- Campanha A permanece com valores fixos de referência.
- Campanha B passa a usar a somatória dos dias selecionados no filtro.
- Incluído um terceiro funil de projeção linear.
- Fórmula: Projeção = soma Campanha B / dias selecionados × dias trabalhados do mês, considerando segunda a sábado.


## V6 - Projeção lado a lado

A visão Funil Comparativo foi ajustada para manter o funil de projeção no mesmo estilo visual dos demais funis.

Alterações:
- O funil de projeção saiu do formato horizontal e passou para formato vertical/trapezoidal.
- A projeção agora fica ao lado do funil comparativo, deixando a leitura mais visual.
- A lógica de cálculo não foi alterada.
- Campanha A continua fixa, Campanha B continua como soma dos dias selecionados e Projeção continua como média dia x dias trabalhados do mês.


## V8 - Soma dos fixos no comparativo

Incluída a opção **Churn + Pré Churn Fixo** nos filtros de Campanha A e Campanha B.

Valores usados:

- Mailing: 64.483
- Discado: 168.424
- Atendidas/Alô: 5.874
- CPC: 1.337
- Acordo/Promessa: 411

Essa opção permite comparar a Campanha A também contra a soma das duas referências fixas.


## V9 - Alinhamento das linhas

Ajustado o CSS da visão Funil Comparativo para manter Campanha A, Etapa, Campanha B, Projeção e Variação no mesmo trilho de linhas fixas.


## V12
- Na projeção, somente o Mailing exibe a média dia da Campanha B.
- As demais etapas continuam com projeção linear mensal.


## V12 + Funil por Faixa de Atraso no Daily
- Base mantida: V12 mailing média projeção.
- Replicada somente a visão de Funil por faixa de atraso do arquivo `cockpit_sky_sem_graficos_faixa_atraso`.
- Removido o bloco de gráficos do Daily que não estava aparecendo.
- Funil comparativo/projeção permanecem da V12.


## V13 - Mailing médio no comparativo + performance

Ajustes:
- No Funil Comparativo, o Mailing da Campanha B agora é exibido como média dia.
- Demais etapas da Campanha B continuam como somatória dos dias selecionados.
- Mantida a regra da projeção: Mailing em média dia; demais etapas em projeção linear.
- Cache na leitura do Excel.
- Mapa Brasil e Hora a Hora carregados sob demanda.
- Animações dos gráficos desativadas para renderização mais rápida.


## V14 - Correção definitiva Mailing B média dia

Correção aplicada:
- Mailing da Campanha B no comparativo agora é calculado dentro da montagem das etapas.
- Isso garante que o card superior e o funil laranja usem média dia.
- As demais etapas da Campanha B continuam como soma dos dias selecionados.
