ADMINISTRAÇÃO DE PERMISSÕES POR VISÃO

Acesso:
- Usuários administradores: admin e gerber
- No Dashboard principal aparece o botão "⚙ Admin"
- Rota direta: /admin/permissoes

Configuração inicial SKY:
- admin: Daily, Hora a Hora, Mapa Brasil, Funil Comparativo
- gerber: Daily, Hora a Hora, Mapa Brasil, Funil Comparativo
- demais usuários com acesso à SKY: Daily e Hora a Hora

Na tela Admin é possível selecionar:
1. Usuário
2. Dashboard / Cliente
3. Visões permitidas
4. Salvar permissões

As permissões ficam em:
data/permissoes_visoes.json

O bloqueio é aplicado tanto na interface quanto no backend/API da SKY.
A estrutura DASHBOARD_VISOES em app.py permite cadastrar novas visões/clientes no futuro.

Observação de deploy:
Se o projeto for executado em uma hospedagem com filesystem efêmero, alterações feitas pela tela podem ser perdidas em restart/redeploy. Nesse cenário, o próximo passo recomendado é persistir as permissões no PostgreSQL/Neon.
