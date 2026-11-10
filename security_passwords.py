"""Autenticação de usuários do Cockpit com senhas persistentes no Neon.

Somente hashes são armazenados. O Render fornece os hashes temporários iniciais.
A tabela mantém as senhas escolhidas pelos usuários, inclusive após deploy/restart.
"""
import os

import psycopg
from werkzeug.security import check_password_hash, generate_password_hash

_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS assistpay.osp_usuarios_senhas (
    usuario TEXT PRIMARY KEY,
    senha_hash TEXT NOT NULL,
    troca_obrigatoria BOOLEAN NOT NULL DEFAULT TRUE,
    alterado_em TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


def _abrir_conexao():
    url = os.environ.get("ASSISTPAY_NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("Banco de autenticação indisponível")
    return psycopg.connect(
        url,
        connect_timeout=10,
        application_name="osp_data_command_center_auth",
    )


def _preparar_tabela(conexao):
    with conexao.cursor() as cursor:
        cursor.execute(_TABLE_SQL)


def _hash_efetivo(conexao, usuario, hashes_iniciais):
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT senha_hash, troca_obrigatoria "
            "FROM assistpay.osp_usuarios_senhas WHERE usuario = %s",
            (usuario,),
        )
        registro = cursor.fetchone()
    # Enquanto a troca for obrigatória, as credenciais temporárias do Render
    # são a fonte de verdade. Após a troca, somente o hash do Neon é válido.
    if registro is None or registro[1]:
        return hashes_iniciais[usuario], True
    return registro[0], False


def autenticar_usuario(usuario, senha, hashes_iniciais):
    if usuario not in hashes_iniciais or not senha:
        return False, False
    with _abrir_conexao() as conexao:
        _preparar_tabela(conexao)
        senha_hash, obrigatoria = _hash_efetivo(conexao, usuario, hashes_iniciais)
        valido = check_password_hash(senha_hash, senha)
        return valido, obrigatoria if valido else False


def senha_igual_atual(usuario, senha, hashes_iniciais):
    if usuario not in hashes_iniciais:
        return False
    with _abrir_conexao() as conexao:
        _preparar_tabela(conexao)
        senha_hash, _ = _hash_efetivo(conexao, usuario, hashes_iniciais)
        return check_password_hash(senha_hash, senha)


def gravar_nova_senha(usuario, senha):
    novo_hash = generate_password_hash(senha, method="scrypt")
    with _abrir_conexao() as conexao:
        _preparar_tabela(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO assistpay.osp_usuarios_senhas "
                "(usuario, senha_hash, troca_obrigatoria, alterado_em) "
                "VALUES (%s, %s, FALSE, NOW()) "
                "ON CONFLICT (usuario) DO UPDATE SET "
                "senha_hash = EXCLUDED.senha_hash, "
                "troca_obrigatoria = FALSE, alterado_em = NOW()",
                (usuario, novo_hash),
            )
    return True
