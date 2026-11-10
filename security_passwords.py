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

# Permissões editáveis das contas legadas mantidas no Render.
# Conta criada no Admin usa diretamente a coluna "clientes" do cadastro.
_LEGACY_ACL_SQL = """
CREATE TABLE IF NOT EXISTS assistpay.osp_usuarios_clientes_override (
    usuario TEXT PRIMARY KEY,
    clientes JSONB NOT NULL DEFAULT '[]'::jsonb,
    atualizado_por TEXT NOT NULL,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT now()
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
        cursor.execute(_LEGACY_ACL_SQL)


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


def listar_permissoes_clientes_legacy():
    """Retorna overrides persistentes: lista vazia significa acesso revogado."""
    with _abrir_conexao() as conexao:
        _preparar_tabela(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT usuario, clientes FROM assistpay.osp_usuarios_clientes_override"
            )
            return {
                usuario: [slug for slug in (clientes or []) if isinstance(slug, str)]
                for usuario, clientes in cursor.fetchall()
            }


def salvar_permissoes_clientes_usuario(usuario, clientes, alterado_por, dinamico):
    """Aplica a lista completa de carteiras com validação e persistência Neon.

    Contas criadas no Admin têm seu cadastro atualizado; contas legadas recebem
    override sem alterar as credenciais e permissões de visão existentes.
    """
    if (not isinstance(usuario, str) or not usuario or
        not isinstance(alterado_por, str) or not alterado_por or
        not isinstance(clientes, list) or
        len(clientes) != len(set(clientes)) or
        any(not isinstance(v, str) or not v or v == "*" for v in clientes)):
        raise ValueError("Lista de clientes inválida")

    with _abrir_conexao() as conexao:
        _preparar_tabela(conexao)
        with conexao.cursor() as cursor:
            if dinamico:
                cursor.execute(
                    "UPDATE assistpay.osp_usuarios_cadastro "
                    "SET clientes = %s::jsonb, alterado_em = NOW() "
                    "WHERE usuario = %s AND ativo = TRUE RETURNING usuario",
                    (json.dumps(clientes), usuario),
                )
                if cursor.fetchone() is None:
                    raise ValueError("Usuário não encontrado ou inativo")
            else:
                cursor.execute(
                    "INSERT INTO assistpay.osp_usuarios_clientes_override "
                    "(usuario, clientes, atualizado_por, atualizado_em) "
                    "VALUES (%s, %s::jsonb, %s, NOW()) "
                    "ON CONFLICT (usuario) DO UPDATE SET "
                    "clientes = EXCLUDED.clientes, "
                    "atualizado_por = EXCLUDED.atualizado_por, "
                    "atualizado_em = NOW()",
                    (usuario, json.dumps(clientes), alterado_por),
                )
    return True
