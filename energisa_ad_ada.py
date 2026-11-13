"""Painel AD × ADA Energisa integrado ao Cockpit OLOS.

A base operacional fica em Neon, nunca em static/ ou no GitHub público.
"""
import os

from flask import jsonify, redirect, render_template, session, url_for, current_app


def install_energisa_ad_ada(app, can_access, is_admin):
    """Instala rotas no Flask existente, preservando login e ACL do Cockpit."""

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

        database_url = os.environ.get("ASSISTPAY_NEON_DATABASE_URL", "").strip()
        if not database_url:
            current_app.logger.error("Neon não configurado para painel Energisa")
            return jsonify(error="data_source_unavailable"), 503

        try:
            import psycopg
            with psycopg.connect(
                database_url,
                connect_timeout=10,
                options="-c statement_timeout=20000",
                application_name="osp_cockpit_energisa_ad_ada",
            ) as con:
                with con.cursor() as cur:
                    cur.execute(
                        "SELECT payload FROM assistpay.energisa_ad_ada_snapshot "
                        "WHERE snapshot_id = 1"
                    )
                    item = cur.fetchone()
        except Exception:
            current_app.logger.exception("Falha ao consultar snapshot Energisa no Neon")
            return jsonify(error="data_source_unavailable"), 503

        if not item:
            return jsonify(error="no_data"), 404

        resposta = jsonify(item[0])
        resposta.headers["Cache-Control"] = "private, no-store, max-age=0"
        resposta.headers["Pragma"] = "no-cache"
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        return resposta
