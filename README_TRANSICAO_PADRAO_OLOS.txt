TRANSIÇÃO PADRÃO OLOS - CAPIVARA + CARREGAMENTO PARALELO
=========================================================

Atualização desta versão
------------------------
A transição não é mais apenas uma espera visual.

1. LOGIN
- Ao enviar usuário e senha, a transição Olos aparece imediatamente.
- A autenticação e a renderização do menu Cockpit acontecem via fetch enquanto o vídeo roda.
- Se o acesso for válido, ao fim da transição o Cockpit já está renderizado e é exibido sem uma segunda espera.
- Se usuário/senha forem inválidos, o erro volta imediatamente sem obrigar o usuário a assistir o vídeo completo.
- Existe fallback para o POST tradicional se JavaScript/fetch falhar.

2. CLIQUE EM CLIENTE
- Ao clicar em qualquer card de cliente, a transição aparece imediatamente.
- Em paralelo, o navegador já faz a requisição ao endpoint do cliente.
- Redirecionamentos Flask são seguidos pelo fetch, então o processamento do painel já acontece durante o vídeo.
- A troca de tela só ocorre quando duas condições forem atendidas:
  a) o tempo mínimo da transição terminou;
  b) o HTML do painel está pronto.
- O HTML já baixado é usado diretamente, evitando uma segunda requisição ao painel.
- Se o painel demorar mais que o vídeo, a transição permanece na tela até os dados terminarem.
- Se houver falha no pré-carregamento, o sistema usa navegação normal como fallback.

Arquivos principais
-------------------
static/video/olos_capybara_loading.mp4
static/css/olos_transition.css
static/js/olos_transition.js
templates/_olos_transition.html
templates/login.html
templates/dashboard.html
app.py

Fluxo esperado
--------------
Login -> vídeo + autenticação/renderização paralela -> Cockpit pronto
Cliente -> vídeo + carregamento/processamento paralelo -> Painel pronto
