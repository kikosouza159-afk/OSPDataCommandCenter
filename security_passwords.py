"""Autenticação do OSP: contas legadas via Render, contas criadas no Admin via Neon.

Nenhuma senha em texto puro é persistida. Toda alteração de senha fica no Neon.
"""
import json
import os

import psycopg
from psycopg.errors import UniqueViolation
from werkzeug.security import check_password_hash, generate_password_hash

_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS assistpay.osp_usuarios_senhas (
    usuario TEXT PRIMARY KEY,
    senha_hash TEXT NOT NULL,
    troca_obrigatoria BOOLEAN NOT NULL DEFAULT TRUE,
    alterado_em TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""
_USERS_SQL = """
CREATE TABLE IF NOT EXISTS assistpay.osp_usuarios_cadastro (
    usuario TEXT PRIMARY KEY,
    senha_hash TEXT NOT NULL,
    troca_obrigatoria BOOLEAN NOT NULL DEFAULT TRUE,
    clientes JSONB NOT NULL DEFAULT '[]'::jsonb,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_por TEXT NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    alterado_em TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


def _abrir_conexao():
    url = os.environ.get("ASSISTPAY_NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("Banco de autenticação indisponível")
    return psycopg.connect(url, connect_timeout=10, application_name="osp_data_command_center_auth")


def _preparar_tabela(conexao):
    with conexao.cursor() as cursor:
        cursor.execute(_TABLE_SQL)
        cursor.execute(_USERS_SQL)


def _buscar_conta(conexao, usuario):
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT senha_hash, troca_obrigatoria, clientes, ativo "
            "FROM assistpay.osp_usuarios_cadastro WHERE usuario = %s",
            (usuario,),
        )
        return cursor.fetchone()


def _hash_efetivo(conexao, usuario, hashes_iniciais):
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT senha_hash, troca_obrigatoria FROM assistpay.osp_usuarios_senhas WHERE usuario = %s",
            (usuario,),
        )
        registro = cursor.fetchone()
    # Se um administrador redefinir a senha, o novo hash do Neon tem prioridade.
    # A configuração inicial do Render só vale para contas que ainda não trocaram senha.
    if registro:
        return registro[0], bool(registro[1])
    return hashes_iniciais.get(usuario) or "", True


def autenticar_usuario(usuario, senha, hashes_iniciais):
    if not usuario or not senha:
        return False, False
    if usuario not in hashes_iniciais:
        # Evita consultas/DDL para e-mails aleatórios e usa falha genérica.
        with _abrir_conexao() as conexao:
            _preparar_tabela(conexao)
            conta = _buscar_conta(conexao, usuario)
            if not conta or not conta[3]:
                return False, False
            valido = check_password_hash(conta[0], senha)
            return valido, bool(conta[1]) if valido else False
    with _abrir_conexao() as conexao:
        _preparar_tabela(conexao)
        hash_efetivo, obrigatoria = _hash_efetivo(conexao, usuario, hashes_iniciais)
        valido = bool(hash_efetivo) and check_password_hash(hash_efetivo, senha)
        return valido, obrigatoria if valido else False


def senha_igual_atual(usuario, senha, hashes_iniciais):
    if not senha:
        return False
    with _abrir_conexao() as conexao:
        _preparar_tabela(conexao)
        if usuario in hashes_iniciais:
            hash_efetivo, _ = _hash_efetivo(conexao, usuario, hashes_iniciais)
        else:
            conta = _buscar_conta(conexao, usuario)
            if not conta or not conta[3]:
                return False
            hash_efetivo = conta[0]
        return bool(hash_efetivo) and check_password_hash(hash_efetivo, senha)


def gravar_nova_senha(usuario, senha):
    novo_hash = generate_password_hash(senha, method="scrypt")
    with _abrir_conexao() as conexao:
        _preparar_tabela(conexao)
        with conexao.cursor() as cursor:
            conta = _buscar_conta(conexao, usuario)
            if conta:
                if not conta[3]:
                    raise ValueError("Conta inativa")
                cursor.execute(
                    "UPDATE assistpay.osp_usuarios_cadastro "
                    "SET senha_hash = %s, troca_obrigatoria = FALSE, alterado_em = NOW() "
                    "WHERE usuario = %s AND ativo = TRUE",
                    (novo_hash, usuario),
                )
            else:
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


def listar_usuarios_cadastro():
    with _abrir_conexao() as conexao:
        _preparar_tabela(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT usuario, clientes, ativo, troca_obrigatoria, criado_em "
                "FROM assistpay.osp_usuarios_cadastro ORDER BY usuario"
            )
            return [
                {"usuario": u, "clientes": clients or [], "ativo": active,
                 "troca_obrigatoria": change, "criado_em": created}
                for u, clients, active, change, created in cursor.fetchall()
            ]


def obter_clientes_usuario(usuario):
    with _abrir_conexao() as conexao:
        _preparar_tabela(conexao)
        conta = _buscar_conta(conexao, usuario)
        if not conta or not conta[3]:
            return []
        return [v for v in (conta[2] or []) if isinstance(v, str)]


def criar_usuario_cadastro(usuario, senha_temporaria, clientes, criado_por):
    usuario = usuario.strip().lower()
    if not clientes:
        raise ValueError("Selecione pelo menos um cliente")
    senha_hash = generate_password_hash(senha_temporaria, method="scrypt")
    with _abrir_conexao() as conexao:
        _preparar_tabela(conexao)
        try:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO assistpay.osp_usuarios_cadastro "
                    "(usuario, senha_hash, troca_obrigatoria, clientes, ativo, criado_por) "
                    "VALUES (%s, %s, TRUE, %s::jsonb, TRUE, %s)",
                    (usuario, senha_hash, json.dumps(clientes), criado_por),
                )
        except UniqueViolation as exc:
            raise ValueError("Este usuário já está cadastrado") from exc
    return True
