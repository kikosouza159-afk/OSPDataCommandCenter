import os
import sqlite3
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import psycopg2
from flask import jsonify, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
CACHE_DB = BASE_DIR / "data" / "voice_performance_cache.db"
APP_TIMEZONE = os.getenv("APP_TIMEZONE", "America/Sao_Paulo")


def now_local():
    return datetime.now(ZoneInfo(APP_TIMEZONE))


def pg_config():
    return {
        "host": os.getenv("PGHOST", ""),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.getenv("PGDATABASE", "postgres"),
        "user": os.getenv("PGUSER", ""),
        "password": os.getenv("PGPASSWORD", ""),
        "sslmode": os.getenv("PGSSLMODE", "require"),
        "connect_timeout": 10,
    }


def cache_conn():
    CACHE_DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(CACHE_DB)
    con.row_factory = sqlite3.Row
    return con


def init_cache():
    con = cache_conn()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback_cache (
            tenant TEXT NOT NULL,
            campaign TEXT NOT NULL,
            data TEXT NOT NULL,
            hora INTEGER NOT NULL,
            ranking_hora INTEGER NOT NULL,
            voz TEXT NOT NULL,
            feedbacks INTEGER NOT NULL,
            sucessos INTEGER NOT NULL,
            taxa_sucesso_pct REAL NOT NULL,
            snapshot_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_feedback_cache_scope
        ON feedback_cache (data, tenant, campaign, hora, voz)
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cache_control (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            last_refresh TEXT,
            last_refresh_date TEXT,
            row_count INTEGER DEFAULT 0,
            status TEXT,
            message TEXT
        )
    """)
    cur.execute("""
        INSERT OR IGNORE INTO cache_control
        (id, last_refresh, last_refresh_date, row_count, status, message)
        VALUES (1, NULL, NULL, 0, 'empty', 'Cache ainda não atualizado')
    """)
    con.commit()
    con.close()


def fetch_from_postgres(target_date):
    cfg = pg_config()
    missing = [k for k in ("host", "user", "password") if not cfg.get(k)]
    if missing:
        raise RuntimeError(
            "Credenciais PostgreSQL não configuradas. "
            "Configure PGHOST, PGUSER e PGPASSWORD no ambiente."
        )

    # score_sum é a fonte de sucesso. Somente valores > 0 entram no numerador.
    # A hora é normalizada para São Paulo antes de filtrar e agrupar.
    sql = """
        WITH origem AS (
            SELECT
                CASE
                    WHEN (hour AT TIME ZONE 'America/Sao_Paulo')::date < DATE '2026-09-03'
                        THEN 'CONSOLIDADO'
                    ELSE COALESCE(NULLIF(BTRIM(tenant), ''), 'CONSOLIDADO')
                END AS tenant,
                CASE
                    WHEN (hour AT TIME ZONE 'America/Sao_Paulo')::date < DATE '2026-09-03'
                        THEN 'CONSOLIDADO'
                    ELSE COALESCE(NULLIF(BTRIM(campaign), ''), 'CONSOLIDADO')
                END AS campaign,
                (hour AT TIME ZONE 'America/Sao_Paulo')::date AS data,
                EXTRACT(HOUR FROM (hour AT TIME ZONE 'America/Sao_Paulo'))::int AS hora,
                voice AS voz,
                feedbacks,
                CASE
                    WHEN COALESCE(score_sum, 0) > 0 THEN score_sum
                    ELSE 0
                END AS sucessos
            FROM public.feedback_hourly
            WHERE (hour AT TIME ZONE 'America/Sao_Paulo') >= %s::date
              AND (hour AT TIME ZONE 'America/Sao_Paulo') < %s::date + INTERVAL '1 day'
        ),
        base AS (
            SELECT
                tenant,
                campaign,
                data,
                hora,
                voz,
                SUM(feedbacks) AS feedbacks,
                SUM(sucessos) AS sucessos,
                ROUND(
                    SUM(sucessos)::numeric / NULLIF(SUM(feedbacks), 0) * 100,
                    2
                ) AS taxa_sucesso_pct
            FROM origem
            GROUP BY tenant, campaign, data, hora, voz
        ),
        ranking AS (
            SELECT
                *,
                DENSE_RANK() OVER (
                    PARTITION BY tenant, campaign, data, hora
                    ORDER BY taxa_sucesso_pct DESC
                ) AS ranking_hora
            FROM base
        )
        SELECT
            tenant, campaign, data, hora, ranking_hora, voz,
            feedbacks, sucessos, taxa_sucesso_pct
        FROM ranking
        ORDER BY tenant, campaign, hora, ranking_hora, voz
    """

    con = psycopg2.connect(**cfg)
    try:
        df = pd.read_sql_query(sql, con, params=(target_date, target_date))
    finally:
        con.close()

    if not df.empty:
        df["data"] = pd.to_datetime(df["data"]).dt.strftime("%Y-%m-%d")
        df["campaign"] = df["campaign"].astype(str)
        df["tenant"] = df["tenant"].astype(str)
        df["voz"] = df["voz"].astype(str)
        for col in ["ranking_hora", "hora", "feedbacks", "sucessos"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        df["taxa_sucesso_pct"] = pd.to_numeric(
            df["taxa_sucesso_pct"], errors="coerce"
        ).fillna(0.0)
    return df


def save_snapshot(df, target_date):
    now = now_local().isoformat(timespec="seconds")
    con = cache_conn()
    cur = con.cursor()
    cur.execute("DELETE FROM feedback_cache WHERE data = ?", (target_date,))
    if not df.empty:
        payload = [
            (
                row.tenant, row.campaign, row.data, int(row.hora),
                int(row.ranking_hora), row.voz, int(row.feedbacks),
                int(row.sucessos), float(row.taxa_sucesso_pct), now,
            )
            for row in df.itertuples(index=False)
        ]
        cur.executemany("""
            INSERT INTO feedback_cache (
                tenant, campaign, data, hora, ranking_hora, voz,
                feedbacks, sucessos, taxa_sucesso_pct, snapshot_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, payload)
    cur.execute("""
        UPDATE cache_control
        SET last_refresh = ?, last_refresh_date = ?, row_count = ?,
            status = 'ok', message = 'Atualização concluída'
        WHERE id = 1
    """, (now, target_date, len(df)))
    con.commit()
    con.close()


def load_cache(target_date=None, tenant=None, campaigns=None):
    con = cache_conn()
    where, params = [], []
    if target_date:
        where.append("data = ?")
        params.append(target_date)
    if tenant:
        where.append("tenant = ?")
        params.append(tenant)
    if campaigns:
        placeholders = ",".join("?" for _ in campaigns)
        where.append(f"campaign IN ({placeholders})")
        params.extend(campaigns)
    sql = "SELECT * FROM feedback_cache"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY tenant, campaign, hora, ranking_hora, voz"
    df = pd.read_sql_query(sql, con, params=params)
    con.close()
    return df


def control_status():
    con = cache_conn()
    row = con.execute("SELECT * FROM cache_control WHERE id = 1").fetchone()
    con.close()
    if not row:
        return {}
    status = dict(row)
    raw = status.get("last_refresh")
    status["last_refresh_local"] = None
    if raw:
        try:
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            dt = dt.astimezone(ZoneInfo(APP_TIMEZONE))
            status["last_refresh_local"] = dt.strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            status["last_refresh_local"] = raw
    return status


def register_voice_performance(app, usuario_pode_acessar_cliente, acesso_negado):
    init_cache()

    def web_access():
        if "usuario" not in session:
            return redirect(url_for("login"))
        if not usuario_pode_acessar_cliente(session.get("usuario"), "voice-performance"):
            return acesso_negado()
        return None

    def api_access():
        if "usuario" not in session:
            return jsonify({"error": "unauthorized"}), 401
        if not usuario_pode_acessar_cliente(session.get("usuario"), "voice-performance"):
            return jsonify({"error": "forbidden"}), 403
        return None

    @app.get("/cliente/voice-performance/painel")
    def voice_performance_index():
        access = web_access()
        if access is not None:
            return access
        return render_template(
            "voice_performance.html",
            usuario=session.get("usuario"),
            show_login_transition=False,
        )

    @app.get("/cliente/voice-performance/painel/api/filters")
    def voice_performance_api_filters():
        access = api_access()
        if access is not None:
            return access
        df = load_cache()
        if df.empty:
            return jsonify({
                "dates": [], "tenants": [], "campaigns": {},
                "control": control_status(),
            })
        dates = sorted(df["data"].dropna().astype(str).unique().tolist(), reverse=True)
        tenants = sorted(df["tenant"].dropna().astype(str).unique().tolist())
        campaigns = {
            tenant: sorted(
                df.loc[df["tenant"] == tenant, "campaign"]
                .dropna().astype(str).unique().tolist()
            )
            for tenant in tenants
        }
        return jsonify({
            "dates": dates,
            "tenants": tenants,
            "campaigns": campaigns,
            "control": control_status(),
        })

    @app.get("/cliente/voice-performance/painel/api/data")
    def voice_performance_api_data():
        access = api_access()
        if access is not None:
            return access
        target_date = request.args.get("date")
        tenant = request.args.get("tenant")
        campaigns = request.args.getlist("campaign")
        df = load_cache(
            target_date=target_date or None,
            tenant=tenant or None,
            campaigns=campaigns or None,
        )
        if df.empty:
            return jsonify({
                "rows": [],
                "kpis": {"feedbacks": 0, "sucessos": 0, "taxa": 0, "vozes": 0, "campanhas": 0},
                "control": control_status(),
            })
        feedbacks = int(df["feedbacks"].sum())
        sucessos = int(df["sucessos"].sum())
        taxa = round((sucessos / feedbacks * 100), 2) if feedbacks else 0
        return jsonify({
            "rows": df.to_dict(orient="records"),
            "kpis": {
                "feedbacks": feedbacks,
                "sucessos": sucessos,
                "taxa": taxa,
                "vozes": int(df["voz"].nunique()),
                "campanhas": int(df["campaign"].nunique()),
            },
            "control": control_status(),
        })

    @app.post("/cliente/voice-performance/painel/api/refresh")
    def voice_performance_api_refresh():
        access = api_access()
        if access is not None:
            return access
        payload = request.get_json(silent=True) or {}
        target_date = payload.get("date") or date.today().isoformat()
        try:
            df = fetch_from_postgres(target_date)
            save_snapshot(df, target_date)
            return jsonify({
                "ok": True,
                "rows": len(df),
                "date": target_date,
                "message": "Cache atualizado com sucesso.",
                "control": control_status(),
            })
        except Exception as exc:
            con = cache_conn()
            now = now_local().isoformat(timespec="seconds")
            con.execute("""
                UPDATE cache_control
                SET last_refresh = ?, status = 'error', message = ?
                WHERE id = 1
            """, (now, str(exc)))
            con.commit()
            con.close()
            return jsonify({
                "ok": False,
                "message": str(exc),
                "control": control_status(),
            }), 500
