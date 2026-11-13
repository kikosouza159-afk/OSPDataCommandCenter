"""Visão diária AD × ADA da Energisa no Cockpit OLOS.

Dados privados na tabela assistpay.energisa_ad_ada_diario do Neon.
A API não disponibiliza dados sem login e permissão no cliente Energisa.
"""
import os
from flask import current_app, jsonify, redirect, render_template, session, url_for


def install_energisa_ad_ada(app, can_access, is_admin):
    def autorizado():
        usuario = session.get("usuario")
        return bool(usuario) and can_access(usuario, "energisa")

    @app.route("/cliente/energisa")
    def energisa_inicio():
        if not session.get("usuario"):
            return redirect(url_for("login"))
        if not autorizado():
            return ("Acesso negado", 403)
        return redirect(url_for("energisa_painel"))

    @app.route("/cliente/energisa/painel")
    def energisa_painel():
        if not session.get("usuario"):
            return redirect(url_for("login"))
        if not autorizado():
            return ("Acesso negado", 403)
        return render_template("energisa_ad_ada.html", usuario=session["usuario"])

    @app.route("/cliente/energisa/painel/api")
    def energisa_api():
        if not session.get("usuario"):
            return jsonify(error="authentication_required"), 401
        if not autorizado():
            return jsonify(error="forbidden"), 403

        # Usa a mesma conexão validada pela autenticação do Cockpit.
        # Evita URL secundária divergente e parâmetros de startup não suportados
        # pelo pooler do Neon.
        database_url = os.environ.get("ASSISTPAY_NEON_DATABASE_URL", "").strip()
        if not database_url:
            current_app.logger.error("Neon não configurado para painel Energisa")
            return jsonify(error="data_source_unavailable"), 503
        try:
            import psycopg
            from psycopg.rows import dict_row
            with psycopg.connect(
                database_url,
                connect_timeout=10,
                application_name="osp_cockpit_energisa_ad_ada",
                row_factory=dict_row,
            ) as con:
                with con.cursor() as cur:
                    # Diagnóstico de banco/ambiente: não expõe URL nem credenciais.
                    cur.execute(
                        "SELECT current_database() AS db, "
                        "to_regclass('assistpay.energisa_ad_ada_diario')::text AS tabela"
                    )
                    verificacao = cur.fetchone()
                    if not verificacao["tabela"]:
                        current_app.logger.error(
                            "Energisa: tabela não encontrada no banco de dados configurado: %s",
                            verificacao["db"],
                        )
                        return jsonify(error="table_not_found"), 503
                    cur.execute("""
                        SELECT data::text AS data,
                               campaign_id, nome_campanha, agente, logados,
                               tentativas, atendidas, cpc, acordo, hangup, mailing
                        FROM assistpay.energisa_ad_ada_diario
                        ORDER BY data, agente, campaign_id
                    """)
                    rows = cur.fetchall()
        except Exception as exc:
            current_app.logger.exception("Falha ao consultar Energisa diário no Neon")
            sqlstate = getattr(exc, "sqlstate", "")
            if sqlstate == "42501":
                code = "database_permission_denied"
            elif sqlstate == "42P01":
                code = "table_not_found"
            elif type(exc).__name__ in ("OperationalError", "InterfaceError"):
                code = "database_connection_failed"
            else:
                code = "data_source_unavailable"
            return jsonify(error=code), 503

        if not rows:
            return jsonify(error="no_data"), 404

        resposta = jsonify({
            "rows": rows,
            "meta": {
                "date_min": rows[0]["data"],
                "date_max": rows[-1]["data"],
                "records": len(rows),
                "granularity": "daily",
                "source": "assistpay.energisa_ad_ada_diario",
            },
        })
        resposta.headers["Cache-Control"] = "private, no-store, max-age=0"
        resposta.headers["Pragma"] = "no-cache"
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        return resposta
