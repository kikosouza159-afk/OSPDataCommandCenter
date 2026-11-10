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

## Segurança e login

O Cockpit não possui senha padrão. O acesso é configurado exclusivamente por variáveis
de ambiente no Render (ou no ambiente local):

- `OSP_SECRET_KEY`: chave aleatória de sessão, com pelo menos 48 caracteres.
- `OSP_AUTH_USERS_JSON`: objeto JSON associando cada usuário ao **hash scrypt**
  da senha, no formato de `werkzeug.security.generate_password_hash`.
- `OSP_COOKIE_SECURE`: opcional. Padrão `true` (produção HTTPS). Usar `false`
  apenas em testes locais com HTTP.

Credenciais e hashes **não devem ser versionados**. Alterar a chave de sessão
encerra as sessões ativas. Configuração ausente bloqueia a inicialização, sem
retornar a senhas antigas.

### Primeira entrada / troca obrigatória de senha

No primeiro login com a senha temporária individual, o usuário é redirecionado
para `/alterar-senha` e não consegue abrir telas ou APIs até escolher sua senha
pessoal. A nova senha precisa ter 14 a 128 caracteres, com letras maiúsculas,
minúsculas e números.

As senhas personalizadas são salvas **somente como hashes scrypt** na tabela
`assistpay.osp_usuarios_senhas` do Neon. A tabela é criada na primeira
autenticação e requer `ASSISTPAY_NEON_DATABASE_URL` configurada no Render.
Senhas alteradas têm prioridade sobre os hashes temporários do Render.

O usuário pode trocar novamente a senha pelo botão **Trocar senha** no menu
principal, informando a senha atual.

Se não houver acesso ao Neon, o login falha com segurança, sem recorrer a
senhas antigas, e a senha do usuário não é sobrescrita.

### Editar clientes visíveis de usuários existentes

Na aba `/admin/permissoes`, o card **Gerenciar acesso aos clientes** permite
selecionar qualquer usuário existente (contas legadas do Render ou criadas no
Admin), marcar/desmarcar os clientes e salvar as permissões. A interface inclui
busca, seleção em massa e confirmação quando todos os acessos são removidos.
Administradores mantêm acesso integral e não são editáveis neste card.

A configuração é persistida no Neon: contas criadas no Admin usam a coluna
`assistpay.osp_usuarios_cadastro.clientes`; contas legadas usam a tabela
`assistpay.osp_usuarios_clientes_override`. Nada é alterado nas senhas nem
nas permissões específicas das abas da SKY. A regra vale tanto para os cards
do Cockpit quanto para acesso direto às rotas e APIs dos clientes; em falhas
do banco de dados, o acesso de contas comuns falha de maneira restritiva.

### Cadastro de usuários pelo Admin

Administradores autorizados podem acessar `/admin/permissoes` para criar contas
novas com **e-mail e clientes autorizados**. O cadastro gera uma senha temporária
aleatória e a mostra uma única vez. Depois da primeira autenticação, a troca
da senha é obrigatória. O acesso a páginas e APIs de outras carteiras é bloqueado
no servidor, independentemente de filtros do navegador.

Os novos usuários e os hashes scrypt de suas senhas ficam persistidos na tabela
`assistpay.osp_usuarios_cadastro` do Neon. Nenhuma senha é gravada em
texto puro. Contas criadas não recebem privilégios administrativos e recebem,
na SKY, as visões Daily e Hora a Hora por padrão; um administrador pode ajustar
as visões pela mesma página. Os usuários existentes não são modificados.

Os acessos temporários de Rosangela e Claudinei foram configurados com
`OSP_SKY_EXTERNAL_HASHES_JSON` no Render e restritos ao cliente SKY.
As senhas definitivas passam a ser gerenciadas no Neon.

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
Configure primeiro as variáveis de ambiente de autenticação (acima). Para testes locais HTTP, defina `OSP_COOKIE_SECURE=false` somente no seu computador.

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


## V15 - Botão Mês/Dia no comparativo, mantendo modelo atual

- Mantido o layout atual, incluindo Projeção mês.
- Incluído botão Mês/Dia ao lado do Comparar.
- Mês mantém a leitura atual.
- Dia:
  - Campanha A = fixo total / dias trabalhados do mês.
  - Campanha B = média dos dias selecionados.


## V16 - Correção botão Mês/Dia

Correções:
- Botão Mês/Dia agora altera os valores corretamente.
- Removido conflito do input hidden `funil_visao`.
- Na visão Dia, a Projeção mês fica oculta.
- Na visão Mês, a Projeção mês continua aparecendo normalmente.


## V17 - Regra Mailing no comparativo

Ajuste aplicado na visão comparativa Sky:
- Visão Mês: Mailing da Campanha B = média dia.
- Visão Dia: Mailing da Campanha B = maior mailing diário do período selecionado.
- Demais indicadores da visão Dia continuam como média dos dias selecionados.


## V18 - Correção Mailing nas visões Mês/Dia

Correções:
- Visão Mês: o funil da Campanha B agora usa valores_b_view, garantindo Mailing B em média dia.
- Visão Dia: o Mailing da Campanha A permanece fixo total, sem dividir pelos dias do mês.
- Visão Dia: Mailing B permanece como maior Mailing diário do período selecionado.


## V19 - Mailing separado por faixa de atraso

Regra aplicada:
- Não usa mais `max` geral para Mailing.
- Daily: Mailing = soma dos valores distintos por DATA + Faixa_Atraso.
- Hora a Hora: Mailing = soma dos valores distintos por DATA + HOUR + Faixa_Atraso, consolidado por hora.
- Brasil/UF: Mailing = soma dos valores distintos por DATA + UF + Faixa_Atraso.
- Funil por faixa: Mailing = soma diária dos valores distintos de cada faixa.
- Comparativo Mês: Mailing B = média da soma diária das faixas distintas.
- Comparativo Dia: Mailing B = soma distinta das faixas do dia mais recente selecionado.


## V20 - Correção média do Mailing no Comparativo Mês

Correção aplicada:
- O Mailing deixa de usar `max` por Faixa_Atraso.
- Agora o cálculo remove duplicados por DATA + Faixa_Atraso + MAILING.
- Comparativo Mês: usa a média diária dessa soma distinta.
- Comparativo Dia: usa a soma distinta do dia mais recente selecionado.
- A mesma regra foi mantida para Daily, Hora a Hora e Brasil/UF.


## V21 - Correção erro groupby Mailing

Correção:
- Ajustado o helper `calcular_mailing_distinto_por_faixa`.
- As chaves de agrupamento agora são deduplicadas.
- Corrige o erro: `ValueError: Grouper for 'Faixa_Atraso' not 1-dimensional`.
- Mantém a regra de Mailing distinto por DATA + Faixa_Atraso + MAILING.
