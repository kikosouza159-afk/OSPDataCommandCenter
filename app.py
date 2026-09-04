"""OSP Data Command Center integrado.

Este arquivo mantém o entry point histórico `app:app`, carrega o Cockpit
original de `core_app.py` e registra o cliente Voice Performance sem alterar
a lógica interna dos demais clientes.
"""

from flask import redirect, session, url_for

import core_app as core
from voice_performance import register_voice_performance

VOICE_CLIENT_SLUG = "voice-performance"
VOICE_CLIENT = {
    "nome": "Voice Performance",
    "slug": VOICE_CLIENT_SLUG,
    "sigla": "VP",
    "domain": "olos.com.br",
    "logo_url": "https://www.olos.com.br/wp-content/uploads/2022/12/logo-olos-laranja.png",
}

# Novo card no mesmo CLIENTES usado pelo menu executivo.
if not any(c.get("slug") == VOICE_CLIENT_SLUG for c in core.CLIENTES):
    core.CLIENTES.insert(0, VOICE_CLIENT)

# Libera o novo cliente somente para perfis internos com visão ampla.
# Contas específicas de outros clientes permanecem isoladas.
for usuario in (
    "gerber",
    "elvis.santos@olos.com.br",
    "nubia.gomes@olos.com.br",
    "eduardo.molina@olos.com.br",
    "michele.silva@olos.com.br",
    "amanda.nascimento@olos.com.br",
):
    permissoes = core.USUARIO_CLIENTES.setdefault(usuario, [])
    if "*" not in permissoes and VOICE_CLIENT_SLUG not in permissoes:
        permissoes.append(VOICE_CLIENT_SLUG)


def voice_performance_client_entry():
    """Entrada do card usando autenticação e autorização do Cockpit."""
    if "usuario" not in session:
        return redirect(url_for("login"))
    if not core.usuario_pode_acessar_cliente(session.get("usuario"), VOICE_CLIENT_SLUG):
        return core.acesso_negado()
    return redirect(url_for("voice_performance_index"))


# A rota literal tem prioridade sobre a rota genérica /cliente/<slug>.
# O link do menu continua usando data-olos-transition-link e, portanto,
# mantém exatamente a transição já existente no Command Center.
core.app.add_url_rule(
    "/cliente/voice-performance",
    endpoint="voice_performance_client_entry",
    view_func=voice_performance_client_entry,
    methods=["GET"],
)

register_voice_performance(
    core.app,
    core.usuario_pode_acessar_cliente,
    core.acesso_negado,
)

app = core.app


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
