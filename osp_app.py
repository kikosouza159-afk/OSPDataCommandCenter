"""Entry point integrado do OSP Data Command Center.

Mantém o Cockpit existente intacto e registra o cliente Voice Performance
como uma extensão do mesmo Flask, preservando login, permissões e transições.
"""

from flask import redirect, session, url_for

import app as core
from voice_performance import register_voice_performance

VOICE_CLIENT_SLUG = "voice-performance"
VOICE_CLIENT = {
    "nome": "Voice Performance",
    "slug": VOICE_CLIENT_SLUG,
    "sigla": "VP",
    "domain": "olos.com.br",
    "logo_url": "https://www.olos.com.br/wp-content/uploads/2022/12/logo-olos-laranja.png",
}

# Insere o novo cliente no mesmo menu executivo já usado pelo Cockpit.
if not any(c.get("slug") == VOICE_CLIENT_SLUG for c in core.CLIENTES):
    core.CLIENTES.insert(0, VOICE_CLIENT)

# Perfis internos que já possuem visão ampla do Cockpit recebem o novo cliente.
# Usuários específicos de clientes continuam isolados.
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
    """Entrada do card do menu, usando o fluxo de acesso padrão do Cockpit."""
    if "usuario" not in session:
        return redirect(url_for("login"))
    if not core.usuario_pode_acessar_cliente(session.get("usuario"), VOICE_CLIENT_SLUG):
        return core.acesso_negado()
    return redirect(url_for("voice_performance_index"))


# A rota estática tem prioridade sobre /cliente/<slug> e, por isso,
# o card usa exatamente a mesma transição do menu atual.
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
