from flask import Flask, render_template, request, redirect, url_for, session
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = "chave_secreta_cockpit_v1_3"

USUARIOS = {
    "admin": "123456",
    "gerber": "nicolas1616",
    "elvis.santos@olos.com.br": "olos@2026",
    "nubia.gomes@olos.com.br": "olos@2026",
    "eduardo.molina@olos.com.br": "olos@2026",
    "michele.silva@olos.com.br": "olos@2026",
    "amanda.nascimento@olos.com.br": "olos@2026",


    # Usuários restritos por cliente
    "sky": "sky123",
    "negocie_online": "negocie@2026",
    "talentos": "talentos123",
    "sky_talentos": "multi123",
    "link": "link123"
}


# ===== CONTROLE DE ACESSO POR CLIENTE =====
# Use o slug do cliente, o mesmo valor usado na URL /cliente/<slug>.
USUARIO_CLIENTES = {
    "admin": ["*"],
    "gerber": ["sky-negocie-online", "talentos", "link", "millennium", "nw-advogados", "renac", "setra", "syscob", "ferreira-e-chagas", "creditas", "aranha-e-ferreira", "gestor-locator", "rede-brasil", "kovi"],
    "elvis.santos@olos.com.br": ["sky-negocie-online", "talentos", "link", "millennium", "nw-advogados", "renac", "setra", "syscob", "ferreira-e-chagas", "creditas", "aranha-e-ferreira", "gestor-locator", "rede-brasil", "kovi"],
    "nubia.gomes@olos.com.br": ["sky-negocie-online", "talentos", "link", "millennium", "nw-advogados", "renac", "setra", "syscob", "ferreira-e-chagas", "creditas", "aranha-e-ferreira", "gestor-locator", "rede-brasil", "kovi"],
    "eduardo.molina@olos.com.br": ["sky-negocie-online", "talentos", "link", "millennium", "nw-advogados", "renac", "setra", "syscob", "ferreira-e-chagas", "creditas", "aranha-e-ferreira", "gestor-locator", "rede-brasil", "kovi"],
    "michele.silva@olos.com.br": ["sky-negocie-online", "talentos", "link", "millennium", "nw-advogados", "renac", "setra", "syscob", "ferreira-e-chagas", "creditas", "aranha-e-ferreira", "gestor-locator", "rede-brasil", "kovi"],
    "amanda.nascimento@olos.com.br": ["sky-negocie-online", "talentos", "link", "millennium", "nw-advogados", "renac", "setra", "syscob", "ferreira-e-chagas", "creditas", "aranha-e-ferreira", "gestor-locator", "rede-brasil", "kovi"],

    "sky": ["sky-negocie-online"],
    "negocie_online": ["sky-negocie-online"],
    "talentos": ["talentos"],
    "link": ["link"],
    "sky_talentos": ["sky-negocie-online", "talentos", "link", "gestor-locator", "rede-brasil"],
}


def usuario_pode_acessar_cliente(usuario, slug):
    """Valida se o usuário logado pode acessar o cliente informado."""
    if not usuario:
        return False
    permissoes = USUARIO_CLIENTES.get(usuario, [])
    if "*" in permissoes:
        return True
    return slug in permissoes


def clientes_permitidos(usuario):
    """Retorna somente os clientes que o usuário pode visualizar no cockpit."""
    if usuario_pode_acessar_cliente(usuario, "*"):
        return CLIENTES
    permissoes = USUARIO_CLIENTES.get(usuario, [])
    return [cliente for cliente in CLIENTES if cliente.get("slug") in permissoes]



# ===== ADMINISTRAÇÃO DE PERMISSÕES POR VISÃO =====
# A estrutura já suporta novos clientes/visões no futuro.
ADMIN_USUARIOS = {"admin", "gerber"}

DASHBOARD_VISOES = {
    "sky-negocie-online": [
        {"id": "daily", "nome": "Daily"},
        {"id": "hora", "nome": "Hora a Hora"},
        {"id": "mapa", "nome": "Mapa Brasil"},
        {"id": "funil", "nome": "Funil Comparativo"},
    ],
}

PERMISSOES_ARQUIVO = Path(__file__).resolve().parent / "data" / "permissoes_visoes.json"


def usuario_e_admin(usuario):
    return bool(usuario) and usuario in ADMIN_USUARIOS


def _permissoes_padrao():
    """Padrão seguro: administradores veem tudo; demais SKY veem Daily/Hora."""
    padrao = {}
    for usuario in USUARIOS:
        padrao[usuario] = {}
        for cliente, visoes in DASHBOARD_VISOES.items():
            if usuario_e_admin(usuario):
                permitidas = [v["id"] for v in visoes]
            elif usuario_pode_acessar_cliente(usuario, cliente):
                permitidas = ["daily", "hora"] if cliente == "sky-negocie-online" else [v["id"] for v in visoes]
            else:
                permitidas = []
            padrao[usuario][cliente] = permitidas
    return padrao


def carregar_permissoes_visoes():
    padrao = _permissoes_padrao()
    if not PERMISSOES_ARQUIVO.exists():
        return padrao
    try:
        dados = json.loads(PERMISSOES_ARQUIVO.read_text(encoding="utf-8"))
        if not isinstance(dados, dict):
            return padrao
        # Mescla com o padrão para novos usuários/novas visões não quebrarem o painel.
        for usuario, clientes in dados.items():
            if usuario not in padrao or not isinstance(clientes, dict):
                continue
            for cliente, permitidas in clientes.items():
                if cliente in padrao[usuario] and isinstance(permitidas, list):
                    ids_validos = {v["id"] for v in DASHBOARD_VISOES.get(cliente, [])}
                    padrao[usuario][cliente] = [v for v in permitidas if v in ids_validos]
        return padrao
    except Exception:
        return padrao


def salvar_permissoes_visoes(dados):
    PERMISSOES_ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    temporario = PERMISSOES_ARQUIVO.with_suffix('.json.tmp')
    temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    temporario.replace(PERMISSOES_ARQUIVO)


def visoes_permitidas(usuario, cliente):
    visoes = DASHBOARD_VISOES.get(cliente, [])
    if usuario_e_admin(usuario):
        return [v["id"] for v in visoes]
    if not usuario_pode_acessar_cliente(usuario, cliente):
        return []
    dados = carregar_permissoes_visoes()
    return dados.get(usuario, {}).get(cliente, [])


def usuario_pode_acessar_visao(usuario, cliente, visao):
    return visao in visoes_permitidas(usuario, cliente)


def filtrar_payload_sky_por_permissao(payload, usuario):
    """Remove dados das visões bloqueadas também no backend/API."""
    if not isinstance(payload, dict):
        return payload
    permitidas = set(visoes_permitidas(usuario, "sky-negocie-online"))
    if "mapa" not in permitidas:
        payload["mapa_html"] = ""
        payload["ranking_uf"] = []
    if "funil" not in permitidas:
        payload["funil_comparativo"] = {"cards": [], "tabela": []}
    if "hora" not in permitidas:
        payload["hora_a_hora"] = {"labels": [], "chart": {}, "tabela": []}
    return payload


def acesso_negado():
    """Tela simples de bloqueio para tentativas de acesso direto pela URL."""
    return """
    <!DOCTYPE html>
    <html lang='pt-br'>
    <head>
      <meta charset='UTF-8'>
      <title>Acesso negado</title>
      <style>
        body {
          margin:0;
          min-height:100vh;
          display:grid;
          place-items:center;
          font-family:Segoe UI,Arial,sans-serif;
          background:linear-gradient(135deg,#020814,#07172a);
          color:#e5e7eb;
        }
        .box {
          width:min(520px,calc(100% - 32px));
          padding:28px;
          border-radius:24px;
          background:rgba(6,18,34,.82);
          border:1px solid rgba(0,229,255,.22);
          box-shadow:0 0 42px rgba(0,229,255,.12);
          text-align:center;
        }
        h1 { margin:0 0 10px; font-size:28px; }
        p { color:#94a3b8; line-height:1.45; }
        a {
          display:inline-block;
          margin-top:14px;
          padding:11px 14px;
          border-radius:14px;
          text-decoration:none;
          color:#00111f;
          font-weight:900;
          background:linear-gradient(135deg,#00e5ff,#0077ff);
        }
      </style>
    </head>
    <body>
      <div class='box'>
        <h1>Acesso negado</h1>
        <p>Seu usuário não possui permissão para visualizar este cliente.</p>
        <a href='/dashboard'>Voltar ao cockpit</a>
      </div>
    </body>
    </html>
    """, 403

CLIENTES = [
    {
        "nome": "2SAFE",
        "slug": "2safe",
        "sigla": "2SA",
        "domain": "",
        "logo_url": "https://www.2safe.com/wp-content/uploads/2024/08/logo-2safe_branco-1024x384.png"
    },
    {
        "nome": "AADVANCE",
        "slug": "aadvance",
        "sigla": "AAD",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "ACTION LINE",
        "slug": "action-line",
        "sigla": "AL",
        "domain": "",
        "logo_url": "https://actionline.io/wp-content/themes/actionlinenew/images/logoVerde.svg"
    },
    {
        "nome": "AeC",
        "slug": "aec",
        "sigla": "AEC",
        "domain": "",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=aec.com.br"
    },
    {
        "nome": "ALERT BRASIL",
        "slug": "alert-brasil",
        "sigla": "AB",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "ALMA VIVA/CRC",
        "slug": "alma-viva-crc",
        "sigla": "AVC",
        "domain": "",
        "logo_url": "https://www.almavivaexperience.com.br/dcm_files/2024/07/Almaviva_Experience_500x136_bianco.png"
    },
    {
        "nome": "Aloha",
        "slug": "aloha",
        "sigla": "ALO",
        "domain": "",
        "logo_url": "https://alloha.com/wp-content/uploads/2022/08/logo_alloha_positivo-300x105.png"
    },
    {
        "nome": "ALPHAVOX",
        "slug": "alphavox",
        "sigla": "ALP",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "AMC",
        "slug": "amc",
        "sigla": "AMC",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "AMÉRICO ADVOGADOS",
        "slug": "americo-advogados",
        "sigla": "AA",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Ancora",
        "slug": "ancora",
        "sigla": "ANC",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "ANTONIO SAMUEL",
        "slug": "antonio-samuel",
        "sigla": "AS",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "AppMax",
        "slug": "appmax",
        "sigla": "APP",
        "domain": "appmax.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=appmax.com.br"
    },
    {
        "nome": "ARANHA E FERREIRA",
        "slug": "aranha-e-ferreira",
        "sigla": "AEF",
        "domain": "",
        "logo_url": "https://afalaw.com.br/wp-content/uploads/2024/12/afalaw-logo-cinza.png"
    },
    {
        "nome": "ARAUZ - SOLUCZ",
        "slug": "arauz-solucz",
        "sigla": "AS",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "ATENTO",
        "slug": "atento",
        "sigla": "ATE",
        "domain": "atento.com",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=atento.com"
    },
    {
        "nome": "ATENTO COLOMBIA",
        "slug": "atento-colombia",
        "sigla": "AC",
        "domain": "atento.com",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=atento.com"
    },
    {
        "nome": "ATENTO PERU",
        "slug": "atento-peru",
        "sigla": "AP",
        "domain": "atento.com",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=atento.com"
    },
    {
        "nome": "ATHENA SAÚDE",
        "slug": "athena-saude",
        "sigla": "AS",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "ATTITUDE",
        "slug": "attitude",
        "sigla": "ATT",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "AVAL",
        "slug": "aval",
        "sigla": "AVA",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Banco Senff",
        "slug": "banco-senff",
        "sigla": "BS",
        "domain": "senff.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=senff.com.br"
    },
    {
        "nome": "Base Telco",
        "slug": "base-telco",
        "sigla": "BT",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "BBTS",
        "slug": "bbts",
        "sigla": "BBT",
        "domain": "bbts.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=bbts.com.br"
    },
    {
        "nome": "BL BPO",
        "slug": "bl-bpo",
        "sigla": "BB",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Boticario",
        "slug": "boticario",
        "sigla": "BOT",
        "domain": "grupoboticario.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=grupoboticario.com.br"
    },
    {
        "nome": "BRISANET TELECOM",
        "slug": "brisanet-telecom",
        "sigla": "BT",
        "domain": "brisanet.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=brisanet.com.br"
    },
    {
        "nome": "Bruno Vanderlei Adv",
        "slug": "bruno-vanderlei-adv",
        "sigla": "BVA",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "CESEC",
        "slug": "cesec",
        "sigla": "CES",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "COBCRED",
        "slug": "cobcred",
        "sigla": "COB",
        "domain": "cobcred.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=cobcred.com.br"
    },
    {
        "nome": "COBEX",
        "slug": "cobex",
        "sigla": "COB",
        "domain": "cobex.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=cobex.com.br"
    },
    {
        "nome": "COBRAFIX",
        "slug": "cobrafix",
        "sigla": "COB",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "COBRART",
        "slug": "cobrart",
        "sigla": "COB",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "CONCENTRIX",
        "slug": "concentrix",
        "sigla": "CON",
        "domain": "concentrix.com",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=concentrix.com"
    },
    {
        "nome": "Concilig",
        "slug": "concilig",
        "sigla": "CON",
        "domain": "concilig.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=concilig.com.br"
    },
    {
        "nome": "CRED ALUGA",
        "slug": "cred-aluga",
        "sigla": "CA",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Creditas",
        "slug": "creditas",
        "sigla": "CRE",
        "domain": "creditas.com",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=creditas.com"
    },
    {
        "nome": "Credlar",
        "slug": "credlar",
        "sigla": "CRE",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "CRESPO CAIRES",
        "slug": "crespo-caires",
        "sigla": "CC",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "CSU",
        "slug": "csu",
        "sigla": "CSU",
        "domain": "csu.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=csu.com.br"
    },
    {
        "nome": "Daycoval",
        "slug": "daycoval",
        "sigla": "DAY",
        "domain": "daycoval.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=daycoval.com.br"
    },
    {
        "nome": "DEELO /EVOLTIS",
        "slug": "deelo-evoltis",
        "sigla": "DE",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Dellyz Food",
        "slug": "dellyz-food",
        "sigla": "DF",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "DMCARD",
        "slug": "dmcard",
        "sigla": "DMC",
        "domain": "dmcard.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=dmcard.com.br"
    },
    {
        "nome": "DNR",
        "slug": "dnr",
        "sigla": "DNR",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "DUNICE",
        "slug": "dunice",
        "sigla": "DUN",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Educa Mais",
        "slug": "educa-mais",
        "sigla": "EM",
        "domain": "educamaisbrasil.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=educamaisbrasil.com.br"
    },
    {
        "nome": "EGGER MESQUITA",
        "slug": "egger-mesquita",
        "sigla": "EM",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "EM DIA",
        "slug": "em-dia",
        "sigla": "ED",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "ENERGISA",
        "slug": "energisa",
        "sigla": "ENE",
        "domain": "energisa.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=energisa.com.br"
    },
    {
        "nome": "Espaço Laser",
        "slug": "espaco-laser",
        "sigla": "EL",
        "domain": "espacolaser.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=espacolaser.com.br"
    },
    {
        "nome": "EXITO",
        "slug": "exito",
        "sigla": "EXI",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "EXSEN",
        "slug": "exsen",
        "sigla": "EXS",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Fácil Resultado",
        "slug": "facil-resultado",
        "sigla": "FR",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "FALABELLA CHILE/COLOMBIA/PERU",
        "slug": "falabella-chile-colombia-peru",
        "sigla": "FCC",
        "domain": "falabella.com",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=falabella.com"
    },
    {
        "nome": "FAMA",
        "slug": "fama",
        "sigla": "FAM",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "FATTOR",
        "slug": "fattor",
        "sigla": "FAT",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "FERREIRA E CHAGAS",
        "slug": "ferreira-e-chagas",
        "sigla": "FEC",
        "domain": "",
        "logo_url": "https://ferreiraechagas.com.br/wp-content/uploads/2019/07/logo-fc-branca2.png"
    },
    {
        "nome": "Folha",
        "slug": "folha",
        "sigla": "FOL",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "FOUNDEVER",
        "slug": "foundever",
        "sigla": "FOU",
        "domain": "foundever.com",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=foundever.com"
    },
    {
        "nome": "FUNCHAL",
        "slug": "funchal",
        "sigla": "FUN",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "GLOBAL SOLUÇÕES",
        "slug": "global-solucoes",
        "sigla": "GS",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "GLOBALCOB",
        "slug": "globalcob",
        "sigla": "GLO",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "GOES E NICOLADELLI",
        "slug": "goes-e-nicoladelli",
        "sigla": "GEN",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "GRUPO DDM",
        "slug": "grupo-ddm",
        "sigla": "GD",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "GRUPO ELO",
        "slug": "grupo-elo",
        "sigla": "GE",
        "domain": "grupoelo.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=grupoelo.com.br"
    },
    {
        "nome": "Grupo Euro 17",
        "slug": "grupo-euro-17",
        "sigla": "GE1",
        "domain": "grupoeuro17.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=grupoeuro17.com.br"
    },
    {
        "nome": "GVC - Rodobens",
        "slug": "gvc-rodobens",
        "sigla": "GR",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Hcosta",
        "slug": "hcosta",
        "sigla": "HCO",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "HENRIQUE SCHROEDER",
        "slug": "henrique-schroeder",
        "sigla": "HS",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "I9TELL",
        "slug": "i9tell",
        "sigla": "I9T",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "I9X",
        "slug": "i9x",
        "sigla": "I9X",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "IAF",
        "slug": "iaf",
        "sigla": "IAF",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "INDRA",
        "slug": "indra",
        "sigla": "IND",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Itapeva",
        "slug": "itapeva",
        "sigla": "ITA",
        "domain": "itapeva.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=itapeva.com.br"
    },
    {
        "nome": "IVAN BITES",
        "slug": "ivan-bites",
        "sigla": "IB",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "IZZI",
        "slug": "izzi",
        "sigla": "IZZ",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "J.A REZENDE",
        "slug": "j-a-rezende",
        "sigla": "JR",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "JORGE VICENTE",
        "slug": "jorge-vicente",
        "sigla": "JV",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "KAINOS",
        "slug": "kainos",
        "sigla": "KAI",
        "domain": "kainos.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=kainos.com.br"
    },
    {
        "nome": "Kateto",
        "slug": "kateto",
        "sigla": "KAT",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "KONECTA",
        "slug": "konecta",
        "sigla": "KON",
        "domain": "konecta-group.com",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=konecta-group.com"
    },
    {
        "nome": "Líder Assessoria",
        "slug": "lider-assessoria",
        "sigla": "LA",
        "domain": "liderassessoria.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=liderassessoria.com.br"
    },
    {
        "nome": "LINK",
        "slug": "link",
        "sigla": "LIN",
        "domain": "",
        "logo_url": "https://www.linksolucoes.com.br/logos/logo.png"
    },
    {
        "nome": "LOCALCRED",
        "slug": "localcred",
        "sigla": "LOC",
        "domain": "localcred.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=localcred.com.br"
    },
    {
        "nome": "LOFT",
        "slug": "loft",
        "sigla": "LOF",
        "domain": "loft.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=loft.com.br"
    },
    {
        "nome": "M.L GOMES",
        "slug": "m-l-gomes",
        "sigla": "MG",
        "domain": "mlgomes.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=mlgomes.com.br"
    },
    {
        "nome": "MADM",
        "slug": "madm",
        "sigla": "MAD",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Martins e Copetti Advogados",
        "slug": "martins-e-copetti-advogados",
        "sigla": "MEC",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "MAX RECOVERY",
        "slug": "max-recovery",
        "sigla": "MR",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "MB Finance",
        "slug": "mb-finance",
        "sigla": "MF",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "MDR Cobrança",
        "slug": "mdr-cobranca",
        "sigla": "MC",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "MEIRELES E FREITAS",
        "slug": "meireles-e-freitas",
        "sigla": "MEF",
        "domain": "meirelesefreitas.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=meirelesefreitas.com.br"
    },
    {
        "nome": "Mentore Bank",
        "slug": "mentore-bank",
        "sigla": "MB",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Mercantil do Brasil",
        "slug": "mercantil-do-brasil",
        "sigla": "MDB",
        "domain": "mercantildobrasil.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=mercantildobrasil.com.br"
    },
    {
        "nome": "MILLENNIUM",
        "slug": "millennium",
        "sigla": "MIL",
        "domain": "",
        "logo_url": "https://www.millenniumcobrancas.com.br/wp-content/uploads/2022/06/cropped-logo_millennium02-ai.png"
    },
    {
        "nome": "Mutant",
        "slug": "mutant",
        "sigla": "MUT",
        "domain": "mutant.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=mutant.com.br"
    },
    {
        "nome": "NEO BPO",
        "slug": "neo-bpo",
        "sigla": "NB",
        "domain": "neobpo.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=neobpo.com.br"
    },
    {
        "nome": "NOVA GESTÕES",
        "slug": "nova-gestoes",
        "sigla": "NG",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "NOVA QUEST",
        "slug": "nova-quest",
        "sigla": "NQ",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "NW  ADVOGADOS",
        "slug": "nw-advogados",
        "sigla": "NA",
        "domain": "",
        "logo_url": "https://nwadv.com.br/wp-content/themes/nwadv/img/logo-header-nwadv.svg"
    },
    {
        "nome": "OLIVEIRA E ANTUNES",
        "slug": "oliveira-e-antunes",
        "sigla": "OEA",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "OLIVEIRA E RAMOS / RAMOS BENEDETTI",
        "slug": "oliveira-e-ramos-ramos-benedetti",
        "sigla": "OER",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "ORBITALL",
        "slug": "orbitall",
        "sigla": "ORB",
        "domain": "orbitall.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=orbitall.com.br"
    },
    {
        "nome": "PagBank",
        "slug": "pagbank",
        "sigla": "PAG",
        "domain": "pagbank.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=pagbank.com.br"
    },
    {
        "nome": "Palmeiras",
        "slug": "palmeiras",
        "sigla": "PAL",
        "domain": "palmeiras.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=palmeiras.com.br"
    },
    {
        "nome": "PASCHOALOTTO",
        "slug": "paschoalotto",
        "sigla": "PAS",
        "domain": "paschoalotto.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=paschoalotto.com.br"
    },
    {
        "nome": "PASQUALI / TSP",
        "slug": "pasquali-tsp",
        "sigla": "PT",
        "domain": "tsp.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=tsp.com.br"
    },
    {
        "nome": "PEREIRA OLIVEIRA",
        "slug": "pereira-oliveira",
        "sigla": "PO",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "PEREZ DE REZENDE",
        "slug": "perez-de-rezende",
        "sigla": "PDR",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Pés sem Dor",
        "slug": "pes-sem-dor",
        "sigla": "PSD",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "PESSOALIZE",
        "slug": "pessoalize",
        "sigla": "PES",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "PHERFIL",
        "slug": "pherfil",
        "sigla": "PHE",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "PROCRED",
        "slug": "procred",
        "sigla": "PRO",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Quero Quitar",
        "slug": "quero-quitar",
        "sigla": "QQ",
        "domain": "queroquitar.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=queroquitar.com.br"
    },
    {
        "nome": "Quinto Andar",
        "slug": "quinto-andar",
        "sigla": "QA",
        "domain": "quintoandar.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=quintoandar.com.br"
    },
    {
        "nome": "RAMA",
        "slug": "rama",
        "sigla": "RAM",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "REAL JURÍDICA",
        "slug": "real-juridica",
        "sigla": "RJ",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "REDE BRASIL",
        "slug": "rede-brasil",
        "sigla": "RB",
        "domain": "redebrasil.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=redebrasil.com.br"
    },
    {
        "nome": "Rede Uze",
        "slug": "rede-uze",
        "sigla": "RU",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Rede Vida",
        "slug": "rede-vida",
        "sigla": "RV",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "REIS ADVOGADOS",
        "slug": "reis-advogados",
        "sigla": "RA",
        "domain": "reis.adv.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=reis.adv.br"
    },
    {
        "nome": "RENAC",
        "slug": "renac",
        "sigla": "REN",
        "domain": "",
        "logo_url": "https://www.gruporenac.com.br/wp-content/themes/gruporenac/dist/images/logo.png?ver=1"
    },
    {
        "nome": "RENNER",
        "slug": "renner",
        "sigla": "REN",
        "domain": "lojasrenner.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=lojasrenner.com.br"
    },
    {
        "nome": "Renov",
        "slug": "renov",
        "sigla": "REN",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Return",
        "slug": "return",
        "sigla": "RET",
        "domain": "gruporecovery.com",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=gruporecovery.com"
    },
    {
        "nome": "RODRIGUES E MONEA",
        "slug": "rodrigues-e-monea",
        "sigla": "REM",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "RV TECNOLOGIA",
        "slug": "rv-tecnologia",
        "sigla": "RT",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "SANCHEZ E SANCHEZ",
        "slug": "sanchez-e-sanchez",
        "sigla": "SES",
        "domain": "sanchezesanchez.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=sanchezesanchez.com.br"
    },
    {
        "nome": "Serasa",
        "slug": "serasa",
        "sigla": "SER",
        "domain": "serasa.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=serasa.com.br"
    },
    {
        "nome": "SERCOM",
        "slug": "sercom",
        "sigla": "SER",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "SETRA",
        "slug": "setra",
        "sigla": "SET",
        "domain": "",
        "logo_url": "https://www.setrabpo.com.br/assets/Logo%20Setra%20BPO-CT7qy7uc.png"
    },
    {
        "nome": "SHULZE",
        "slug": "shulze",
        "sigla": "SHU",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Siccob",
        "slug": "siccob",
        "sigla": "SIC",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "SISCOM",
        "slug": "siscom",
        "sigla": "SIS",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "SOLUTIO",
        "slug": "solutio",
        "sigla": "SOL",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Supersim",
        "slug": "supersim",
        "sigla": "SUP",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "SYSCOB",
        "slug": "syscob",
        "sigla": "SYS",
        "domain": "",
        "logo_url": "https://syscob.com.br/images/logo_siscob.png"
    },
    {
        "nome": "TAHTO",
        "slug": "tahto",
        "sigla": "TAH",
        "domain": "tahto.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=tahto.com.br"
    },
    {
        "nome": "TALENTOS",
        "slug": "talentos",
        "sigla": "TAL",
        "domain": "",
        "logo_url": "https://www.grupotalentos.com.br/LogoTalentosAzul.png"
    },
    {
        "nome": "TEL TELEMATICA",
        "slug": "tel-telematica",
        "sigla": "TT",
        "domain": "tel.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=tel.com.br"
    },
    {
        "nome": "Tenda",
        "slug": "tenda",
        "sigla": "TEN",
        "domain": "tenda.com",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=tenda.com"
    },
    {
        "nome": "TRC TABORDA",
        "slug": "trc-taborda",
        "sigla": "TT",
        "domain": "trctaborda.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=trctaborda.com.br"
    },
    {
        "nome": "Ultragaz",
        "slug": "ultragaz",
        "sigla": "ULT",
        "domain": "ultragaz.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=ultragaz.com.br"
    },
    {
        "nome": "UNICONCOBRA",
        "slug": "uniconcobra",
        "sigla": "UNI",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "UNIJORGE",
        "slug": "unijorge",
        "sigla": "UNI",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "VELLOSO",
        "slug": "velloso",
        "sigla": "VEL",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Verisure",
        "slug": "verisure",
        "sigla": "VER",
        "domain": "verisure.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=verisure.com.br"
    },
    {
        "nome": "VERRESCHI",
        "slug": "verreschi",
        "sigla": "VER",
        "domain": "verreschi.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=verreschi.com.br"
    },
    {
        "nome": "Versuo",
        "slug": "versuo",
        "sigla": "VER",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "VGX",
        "slug": "vgx",
        "sigla": "VGX",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Vitalmed",
        "slug": "vitalmed",
        "sigla": "VIT",
        "domain": "vitalmed.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=vitalmed.com.br"
    },
    {
        "nome": "Votorantim",
        "slug": "votorantim",
        "sigla": "VOT",
        "domain": "bv.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=bv.com.br"
    },
    {
        "nome": "WAYBACK",
        "slug": "wayback",
        "sigla": "WAY",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "WINOVER",
        "slug": "winover",
        "sigla": "WIN",
        "domain": "winnover.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=winnover.com.br"
    },
    {
        "nome": "WMARCONI",
        "slug": "wmarconi",
        "sigla": "WMA",
        "domain": "",
        "logo_url": ""
    },
    {
        "nome": "Yamaha",
        "slug": "yamaha",
        "sigla": "YAM",
        "domain": "yamaha-motor.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=yamaha-motor.com.br"
    },
    {
        "nome": "NOVA GESTÕES",
        "slug": "nova-gestoes",
        "sigla": "NG",
        "domain": "",
        "logo_url": ""
    }
]



# Cliente Sky integrado ao Cockpit
if not any(c.get("slug") == "sky-negocie-online" for c in CLIENTES):
    CLIENTES.insert(0, {
        "nome": "Sky | Negocie Online",
        "slug": "sky-negocie-online",
        "sigla": "SKY",
        "domain": "",
        "logo_url": "https://skycms.s3.amazonaws.com/images/0/Logo-Menu.svg"
    })

# Painel Gestor Locator integrado ao Cockpit
if not any(c.get("slug") == "gestor-locator" for c in CLIENTES):
    CLIENTES.insert(1, {
        "nome": "GESTOR LOCATOR",
        "slug": "gestor-locator",
        "sigla": "GL",
        "domain": "",
        "logo_url": "https://i.imgur.com/15rWePl.png"
    })

# Cliente KOVI | Painel de Disparo WhatsApp
if not any(c.get("slug") == "kovi" for c in CLIENTES):
    CLIENTES.insert(2, {
        "nome": "KOVI",
        "slug": "kovi",
        "sigla": "KOV",
        "domain": "",
        "logo_url": "https://www.kovi.com.br/hubfs/Kovi-2024/Images/Logo%20preto%20-%20horizontal.svg"
    })

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            session["usuario"] = usuario

            # Login assíncrono: o navegador mantém a transição Olos visível
            # enquanto o servidor já prepara/renderiza o Cockpit em segundo plano.
            # Assim evitamos vídeo -> nova espera de carregamento.
            if request.headers.get("X-Olos-Async-Transition") == "1":
                session.pop("show_login_transition", None)
                return render_template(
                    "dashboard.html",
                    usuario=session["usuario"],
                    clientes=clientes_permitidos(session["usuario"]),
                    is_admin=usuario_e_admin(session["usuario"]),
                    show_login_transition=False,
                )

            # Fallback sem JavaScript: mantém o fluxo tradicional.
            session["show_login_transition"] = True
            return redirect(url_for("dashboard"))

        erro = "Usuário ou senha inválidos"
        if request.headers.get("X-Olos-Async-Transition") == "1":
            return render_template("login.html", erro=erro), 401
    return render_template("login.html", erro=erro)

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    show_login_transition = bool(session.pop("show_login_transition", False))
    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        clientes=clientes_permitidos(session["usuario"]),
        is_admin=usuario_e_admin(session["usuario"]),
        show_login_transition=show_login_transition,
    )


@app.route('/admin/permissoes', methods=['GET', 'POST'])
def admin_permissoes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if not usuario_e_admin(session.get('usuario')):
        return acesso_negado()

    dados = carregar_permissoes_visoes()
    mensagem = None
    erro = None

    usuario_sel = request.values.get('usuario_sel') or next((u for u in USUARIOS if not usuario_e_admin(u)), list(USUARIOS)[0])
    cliente_sel = request.values.get('cliente_sel') or 'sky-negocie-online'

    if request.method == 'POST':
        if usuario_sel not in USUARIOS:
            erro = 'Usuário inválido.'
        elif cliente_sel not in DASHBOARD_VISOES:
            erro = 'Dashboard inválido.'
        elif usuario_e_admin(usuario_sel):
            erro = 'Administradores mantêm acesso total às visões.'
        else:
            visoes_validas = {v['id'] for v in DASHBOARD_VISOES[cliente_sel]}
            selecionadas = [v for v in request.form.getlist('visoes') if v in visoes_validas]
            dados.setdefault(usuario_sel, {})[cliente_sel] = selecionadas
            try:
                salvar_permissoes_visoes(dados)
                mensagem = 'Permissões salvas com sucesso.'
                dados = carregar_permissoes_visoes()
            except Exception as exc:
                erro = f'Não foi possível salvar as permissões: {exc}'

    visoes_cliente = DASHBOARD_VISOES.get(cliente_sel, [])
    permitidas = set(dados.get(usuario_sel, {}).get(cliente_sel, []))
    clientes_admin = [
        {'slug': slug, 'nome': 'SKY - Negocie Online' if slug == 'sky-negocie-online' else slug}
        for slug in DASHBOARD_VISOES
    ]

    return render_template(
        'admin_permissoes.html',
        usuario=session.get('usuario'),
        usuarios=list(USUARIOS.keys()),
        usuario_sel=usuario_sel,
        cliente_sel=cliente_sel,
        clientes_admin=clientes_admin,
        visoes_cliente=visoes_cliente,
        permitidas=permitidas,
        admin_usuarios=ADMIN_USUARIOS,
        mensagem=mensagem,
        erro=erro,
    )


# ===== CLIENTES LOCATOR | Painel executivo compartilhado =====
# Cada cliente possui uma base Excel isolada em data/<arquivo>.
LOCATOR_CLIENTES_CONFIG = {
    "millennium": {"nome": "MILLENNIUM", "arquivo": "base_millennium.xlsx"},
    "nw-advogados": {"nome": "NW ADVOGADOS", "arquivo": "base_nw_advogados.xlsx"},
    "renac": {"nome": "RENAC", "arquivo": "base_renac.xlsx"},
    "setra": {"nome": "SETRA", "arquivo": "base_setra.xlsx"},
    "syscob": {"nome": "SYSCOB", "arquivo": "base_syscob.xlsx"},
    "ferreira-e-chagas": {"nome": "FERREIRA & CHAGAS", "arquivo": "base_ferreira_chagas.xlsx"},
    "creditas": {"nome": "CREDITAS", "arquivo": "base_creditas.xlsx"},
    "aranha-e-ferreira": {"nome": "ARANHA FERREIRA", "arquivo": "base_aranha_ferreira.xlsx"},
}

@app.route("/cliente/<slug>")
def cliente(slug):
    if "usuario" not in session:
        return redirect(url_for("login"))
    cliente_selecionado = next((c for c in CLIENTES if c["slug"] == slug), None)
    if not cliente_selecionado:
        return redirect(url_for("dashboard"))

    if not usuario_pode_acessar_cliente(session.get("usuario"), slug):
        return acesso_negado()

    if slug == "sky-negocie-online":
        return redirect(url_for("sky_negocie_online_index"))

    if slug == "talentos":
        return redirect(url_for("talentos_index"))

    if slug == "link":
        return redirect(url_for("link_index"))

    if slug == "gestor-locator":
        return redirect(url_for("gestor_locator_index"))

    if slug == "rede-brasil":
        return redirect(url_for("rede_brasil_locator_index"))

    if slug == "kovi":
        return redirect(url_for("kovi_whatsapp_index"))

    if slug in LOCATOR_CLIENTES_CONFIG:
        return redirect(url_for("locator_cliente_index", slug=slug))

    return render_template("cliente.html", usuario=session["usuario"], cliente=cliente_selecionado)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))




# ===== KOVI | Painel de Disparo WhatsApp =====
KOVI_WHATSAPP_EXCEL = Path(__file__).resolve().parent / 'data' / 'base_kovi_whatsapp.xlsx'


def _kovi_numero(valor):
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    s = str(valor).strip().replace('R$', '').replace('%', '').replace(' ', '')
    if not s:
        return 0.0
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except Exception:
        return 0.0


def _kovi_carregar_base():
    colunas = ['Arquivo', 'Data do Disparo', 'Entregues', 'Enviados', 'Taxa']
    if not KOVI_WHATSAPP_EXCEL.exists():
        return pd.DataFrame(columns=colunas + ['Empresa', 'Janela'])
    try:
        df = pd.read_excel(KOVI_WHATSAPP_EXCEL, sheet_name=0)
    except Exception:
        return pd.DataFrame(columns=colunas + ['Empresa', 'Janela'])

    df.columns = [str(c).strip() for c in df.columns]
    for c in colunas:
        if c not in df.columns:
            df[c] = None

    df['Data do Disparo'] = pd.to_datetime(df['Data do Disparo'], dayfirst=True, errors='coerce')
    df['Entregues'] = df['Entregues'].apply(_kovi_numero)
    df['Enviados'] = df['Enviados'].apply(_kovi_numero)
    df['Arquivo'] = df['Arquivo'].fillna('').astype(str).str.strip()

    # A praça e a janela são inferidas do nome do arquivo.
    nome_upper = df['Arquivo'].str.upper()
    df['Empresa'] = nome_upper.apply(lambda x: 'POA' if 'POA' in x else ('SP' if 'SP' in x else 'OUTROS'))
    df['Janela'] = df['Arquivo'].str.extract(r'(\d{1,2}:\d{2})', expand=False).fillna('Sem janela')
    df = df[df['Data do Disparo'].notna()].copy()
    return df


def _kovi_fmt_int(v):
    return f"{int(round(float(v or 0))):,}".replace(',', '.')


def _kovi_fmt_pct(v):
    return f"{float(v or 0):.1f}%".replace('.', ',')


def _kovi_dashboard():
    df = _kovi_carregar_base()
    if df.empty:
        return {
            'vazio': True,
            'filtros': {'datas': [], 'empresas': [], 'arquivos': [], 'janelas': []},
            'selecionado': {}, 'cards': {}, 'diario': [], 'pracas': [], 'chart': {'points': [], 'labels': []}
        }

    data_min = df['Data do Disparo'].min().date()
    data_max = df['Data do Disparo'].max().date()
    inicio_txt = request.args.get('inicio') or data_min.isoformat()
    fim_txt = request.args.get('fim') or data_max.isoformat()
    try:
        inicio = pd.to_datetime(inicio_txt, errors='raise').date()
    except Exception:
        inicio = data_min
    try:
        fim = pd.to_datetime(fim_txt, errors='raise').date()
    except Exception:
        fim = data_max
    if inicio > fim:
        inicio, fim = fim, inicio

    empresa = (request.args.get('empresa') or 'Todas').strip()
    arquivo = (request.args.get('arquivo') or 'Todos').strip()
    janela = (request.args.get('janela') or 'Todos').strip()

    mask = (df['Data do Disparo'].dt.date >= inicio) & (df['Data do Disparo'].dt.date <= fim)
    filtrado = df.loc[mask].copy()
    if empresa != 'Todas':
        filtrado = filtrado[filtrado['Empresa'] == empresa]
    if arquivo != 'Todos':
        filtrado = filtrado[filtrado['Arquivo'] == arquivo]
    if janela != 'Todos':
        filtrado = filtrado[filtrado['Janela'] == janela]

    enviados = float(filtrado['Enviados'].sum())
    entregues = float(filtrado['Entregues'].sum())
    taxa = (entregues / enviados * 100) if enviados else 0.0
    janelas = int(filtrado[['Data do Disparo', 'Arquivo']].drop_duplicates().shape[0])

    # Mantém a data como coluna real antes do groupby.
    # Isso evita o FutureWarning do pandas e garante que o campo exista
    # depois da agregação, independentemente da versão instalada.
    diario_base = filtrado.assign(Data_Dia=filtrado['Data do Disparo'].dt.normalize())
    diario_df = (
        diario_base
        .groupby('Data_Dia', as_index=False)[['Enviados', 'Entregues']]
        .sum()
        .sort_values('Data_Dia')
    )
    diario = []
    for _, r in diario_df.iterrows():
        data_dia = pd.Timestamp(r['Data_Dia'])
        ev = float(r['Enviados'])
        et = float(r['Entregues'])
        tx = (et/ev*100) if ev else 0.0
        diario.append({
            'data_iso': data_dia.date().isoformat(),
            'data': data_dia.strftime('%d/%m/%Y'),
            'data_curta': data_dia.strftime('%d/%m'),
            'enviados': _kovi_fmt_int(ev),
            'entregues': _kovi_fmt_int(et),
            'taxa': _kovi_fmt_pct(tx),
            'taxa_num': round(tx, 2),
        })

    pracas = []
    for praca, g in filtrado.groupby('Empresa'):
        ev = float(g['Enviados'].sum())
        et = float(g['Entregues'].sum())
        tx = (et/ev*100) if ev else 0.0
        pracas.append({
            'nome': praca,
            'enviados': _kovi_fmt_int(ev),
            'entregues': _kovi_fmt_int(et),
            'taxa': _kovi_fmt_pct(tx),
            'taxa_num': round(tx,2),
            'bom': tx >= taxa if enviados else True,
        })
    pracas.sort(key=lambda x: x['taxa_num'], reverse=True)

    # Coordenadas do gráfico em um plano fixo para evitar distorção visual.
    taxas = [d['taxa_num'] for d in diario]
    chart_points = []
    chart_ticks = []
    avg_taxa = round((sum(taxas) / len(taxas)), 2) if taxas else 0.0
    best_day = max(diario, key=lambda x: x['taxa_num']) if diario else None
    worst_day = min(diario, key=lambda x: x['taxa_num']) if diario else None

    chart_w = 780
    chart_h = 280
    pad_l = 58
    pad_r = 24
    pad_t = 18
    pad_b = 42

    if taxas:
        min_tx = min(taxas)
        max_tx = max(taxas)
        lo = max(0, (int((min_tx - 1.0) // 1) - 1))
        hi = min(100, (int((max_tx + 1.0) // 1) + 2))
        if (hi - lo) < 8:
            centro = (hi + lo) / 2
            lo = max(0, round(centro - 4))
            hi = min(100, round(centro + 4))
        plot_w = chart_w - pad_l - pad_r
        plot_h = chart_h - pad_t - pad_b
        n = len(taxas)
        for i, tx in enumerate(taxas):
            x = pad_l + (plot_w * i / max(1, n - 1))
            ratio = 0 if hi == lo else ((tx - lo) / (hi - lo))
            y = pad_t + plot_h - (ratio * plot_h)
            chart_points.append({
                'x': round(x, 2),
                'y': round(y, 2),
                'taxa': _kovi_fmt_pct(tx),
                'label': diario[i]['data_curta'],
            })
        tick_count = 5
        for idx in range(tick_count):
            tick_value = lo + ((hi - lo) * idx / (tick_count - 1))
            tick_y = pad_t + plot_h - ((tick_value - lo) / (hi - lo) * plot_h if hi != lo else 0)
            chart_ticks.append({'y': round(tick_y, 2), 'value': _kovi_fmt_pct(round(tick_value, 1))})
    else:
        lo, hi = 75, 90

    return {
        'vazio': False,
        'filtros': {
            'empresas': sorted([x for x in df['Empresa'].dropna().unique().tolist() if x]),
            'arquivos': sorted([x for x in df['Arquivo'].dropna().unique().tolist() if x]),
            'janelas': sorted([x for x in df['Janela'].dropna().unique().tolist() if x]),
        },
        'selecionado': {
            'inicio': inicio.isoformat(), 'fim': fim.isoformat(), 'empresa': empresa,
            'arquivo': arquivo, 'janela': janela,
            'periodo': f"{inicio.strftime('%d/%m/%Y')} - {fim.strftime('%d/%m/%Y')}"
        },
        'cards': {
            'enviados': _kovi_fmt_int(enviados), 'entregues': _kovi_fmt_int(entregues),
            'taxa': _kovi_fmt_pct(taxa), 'taxa_num': round(taxa,2), 'janelas': _kovi_fmt_int(janelas),
        },
        'diario': diario, 'pracas': pracas,
        'chart': {
            'points': chart_points,
            'ticks': chart_ticks,
            'lo': round(lo,1),
            'hi': round(hi,1),
            'avg_taxa': _kovi_fmt_pct(avg_taxa),
            'avg_taxa_num': avg_taxa,
            'best_day': best_day,
            'worst_day': worst_day,
            'viewbox': f'0 0 {chart_w} {chart_h}',
            'width': chart_w,
            'height': chart_h,
            'pad_l': pad_l,
            'pad_r': pad_r,
            'pad_t': pad_t,
            'pad_b': pad_b,
            'base_y': chart_h - pad_b,
        }
    }


@app.route('/cliente/kovi/painel')
def kovi_whatsapp_index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if not usuario_pode_acessar_cliente(session.get('usuario'), 'kovi'):
        return acesso_negado()
    return render_template('kovi_whatsapp.html', usuario=session.get('usuario'), dashboard=_kovi_dashboard())


# ===== TALENTOS | Locator Dashboard integrado na V1.4 =====
import os
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from flask import render_template, request, session, redirect, url_for

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_EXCEL = BASE_DIR / 'data' / 'base.xlsx'
EXCEL_PATH = Path(os.getenv('EXCEL_PATH', DEFAULT_EXCEL))


COLUMN_ALIASES = {
    'dt': 'Dt',
    'data': 'Dt',
    'hour': 'Hour',
    'hora': 'Hour',
    'nomecampanha': 'NomeCampanha',
    'campanha': 'NomeCampanha',
    'ad': 'AD',
    'ath': 'ATH',
    'mailing': 'Mailing',
    'discado': 'Discado',
    'atendidas': 'Atendidas',
    'transferencia': 'Transferencia',
    'transferidas': 'Transferencia',
    'recebidas': 'Recebidas',
    'cpc': 'Cpc',
    'acordo': 'Acordo',
    'tma_locator': 'TMA_LOCATOR',
    'tma_ath': 'TMA_ATH',
    'hitrate': 'HitRate',
    'hitrate%': 'HitRate',
    'loc': 'Loc',
    'conversao': 'Conversao',
    'spin': 'Spin',
    '%abandono': '%Abandono',
    'abandono': '%Abandono',
    'perda': 'Perda',
    '%perda': '%Perda',
    'custo': 'Custo',
    'custotelecom': 'Custo',
    'custodetelecom': 'Custo',
}

REQUIRED_COLUMNS = [
    'Dt', 'Hour', 'NomeCampanha', 'Discado', 'Atendidas', 'Transferencia', 'Recebidas', 'Cpc', 'Acordo'
]

FLOW_ORDER = [
    ('Discado', '📞'),
    ('Atendidas', '🟢'),
    ('Transferencia', '🤖'),
    ('Perda', '⚠️'),
    ('Recebidas', '🎧'),
    ('Cpc', '✅'),
    ('Acordo', '💰'),
    ('Custo', '📡'),
]

COMPARE_METRICS = [
    ('Mailing', 'Mailing', '🗂️', 'higher'),
    ('AD', 'Logados AD', '🤖', 'higher'),
    ('ATH', 'Logados ATH', '👤', 'higher'),
    ('Discado', 'Discado', '📞', 'higher'),
    ('Atendidas', 'Atendidas', '🟢', 'higher'),
    ('Transferencia', 'CPC AD / Transferidas', '✅', 'higher'),
    ('Acordo', 'Acordo', '💰', 'higher'),
    ('Custo', 'Custo Telecom', '📡', 'lower'),
    ('HitRate', 'Hit Rate', '🎯', 'higher'),
    ('TxTransferencia', 'Tx Transferência', '🔁', 'higher'),
    ('Conversao', 'Conversão Acordo', '🏁', 'higher'),
]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        key = str(col).strip().lower().replace(' ', '')
        if key in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[key]
    return df.rename(columns=rename_map)


def parse_percent_series(series: pd.Series) -> pd.Series:
    """
    Normaliza percentuais para escala 0-100.

    Aceita os formatos mais comuns vindos do Excel:
    - texto: "11,81%"  -> 11.81
    - texto: "11.81%"  -> 11.81
    - número: 0.1181   -> 11.81
    - número: 11.81    -> 11.81

    A versão anterior removia todo ponto antes de converter.
    Por isso valores como 2.88 viravam 288.00%.
    """
    if pd.api.types.is_numeric_dtype(series):
        out = pd.to_numeric(series, errors='coerce')
        mask = out.abs().le(1) & out.notna()
        out.loc[mask] = out.loc[mask] * 100
        return out

    raw = series.astype(str).str.strip()
    raw = raw.replace({'': None, 'nan': None, 'None': None, '-': None, '--': None})

    def _parse(value):
        if value is None or pd.isna(value):
            return None
        txt = str(value).strip().replace('%', '').strip()
        if not txt:
            return None

        # Formato brasileiro com vírgula decimal: 1.234,56 ou 11,81
        if ',' in txt:
            txt = txt.replace('.', '').replace(',', '.')
        # Formato padrão com ponto decimal: 11.81. Não remover o ponto.
        try:
            num = float(txt)
        except Exception:
            return None

        # Excel às vezes traz percentual como fração: 0.1181 = 11,81%
        if abs(num) <= 1:
            num *= 100
        return num

    return raw.map(_parse).astype(float)


def weighted_percent(df: pd.DataFrame, col: str, weight_col: str | None = None):
    if col not in df.columns:
        return None
    s = pd.to_numeric(df[col], errors='coerce')
    valid = s.notna()
    if not valid.any():
        return None
    if weight_col and weight_col in df.columns:
        w = pd.to_numeric(df.loc[valid, weight_col], errors='coerce').fillna(0)
        if w.sum() > 0:
            return float((s.loc[valid] * w).sum() / w.sum())
    return float(s.loc[valid].mean())


def load_data() -> pd.DataFrame:
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            f'Arquivo Excel não encontrado em: {EXCEL_PATH}. Coloque sua base em data/base.xlsx ou defina EXCEL_PATH.'
        )

    if EXCEL_PATH.suffix.lower() in {'.xlsx', '.xls'}:
        df = pd.read_excel(EXCEL_PATH)
    elif EXCEL_PATH.suffix.lower() == '.csv':
        df = pd.read_csv(EXCEL_PATH, sep=None, engine='python')
    else:
        raise ValueError('Formato de arquivo não suportado. Use .xlsx, .xls ou .csv')

    df = normalize_columns(df)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f'Colunas obrigatórias ausentes: {", ".join(missing)}')

    df['Dt'] = pd.to_datetime(df['Dt'], errors='coerce')
    df['Hour'] = pd.to_numeric(df['Hour'], errors='coerce').fillna(0).astype(int)
    df['NomeCampanha'] = df['NomeCampanha'].astype(str)

    numeric_cols = ['AD', 'ATH', 'Mailing', 'Discado', 'Atendidas', 'Transferencia', 'Perda', 'Recebidas', 'Cpc', 'Acordo', 'Spin', 'Custo']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0.0

    percent_cols = ['HitRate', 'Loc', 'Conversao', '%Abandono', '%Perda']
    for col in percent_cols:
        if col in df.columns:
            df[col] = parse_percent_series(df[col])

    for tma_col in ['TMA_LOCATOR', 'TMA_ATH']:
        if tma_col in df.columns:
            df[tma_col] = df[tma_col].fillna('--').astype(str)

    df = df.dropna(subset=['Dt']).copy()
    df['DtStr'] = df['Dt'].dt.strftime('%Y-%m-%d')
    return df


def safe_pct(num: float, den: float) -> float:
    if not den:
        return 0.0
    return (num / den) * 100


def fmt_int(v: float | int) -> str:
    return f"{int(round(v)):,}".replace(',', '.')


def fmt_pct(v: float | int) -> str:
    return f"{v:,.2f}%".replace(',', 'X').replace('.', ',').replace('X', '.')


def fmt_currency(v: float | int) -> str:
    return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def classify_abandonment(v: float) -> str:
    if v <= 3:
        return 'verde'
    if v <= 9:
        return 'amarelo'
    return 'vermelho'


def classify_delta(delta_pct: float, preference: str) -> str:
    positive = delta_pct >= 0 if preference == 'higher' else delta_pct <= 0
    return 'positivo' if positive else 'negativo'


def calc_summary(df: pd.DataFrame, use_peak_logados: bool = False) -> Dict[str, float]:
    ad_value = (
        float(df['AD'].max()) if use_peak_logados and not df.empty
        else float(df.loc[df['AD'] > 0, 'AD'].mean()) if (df['AD'] > 0).any()
        else float(df['AD'].mean()) if not df.empty else 0.0
    )
    ath_value = (
        float(df['ATH'].max()) if use_peak_logados and not df.empty
        else float(df.loc[df['ATH'] > 0, 'ATH'].mean()) if (df['ATH'] > 0).any()
        else float(df['ATH'].mean()) if not df.empty else 0.0
    )

    totals = {
        'Mailing': float(df['Mailing'].max()) if not df.empty else 0.0,
        'AD': ad_value,
        'ATH': ath_value,
        'Discado': float(df['Discado'].sum()),
        'Atendidas': float(df['Atendidas'].sum()),
        'Transferencia': float(df['Transferencia'].sum()),
        'Recebidas': float(df['Recebidas'].sum()),
        'Cpc': float(df['Cpc'].sum()),
        'Acordo': float(df['Acordo'].sum()),
        'Perda': float(df['Perda'].sum()),
        'Custo': float(df['Custo'].sum()),
        'Spin': float(df['Spin'].mean()) if not df.empty else 0.0,
    }
    perda_from_base = weighted_percent(df, '%Perda', 'Transferencia')
    abandono_from_base = weighted_percent(df, '%Abandono', 'Transferencia')
    totals['PerdaPct'] = perda_from_base if perda_from_base is not None else safe_pct(totals['Perda'], totals['Transferencia'])
    totals['Abandono'] = abandono_from_base if abandono_from_base is not None else safe_pct(totals['Transferencia'] - totals['Recebidas'], totals['Transferencia'])
    totals['HitRate'] = safe_pct(totals['Atendidas'], totals['Discado'])
    totals['TxTransferencia'] = safe_pct(totals['Transferencia'], totals['Atendidas'])
    totals['TxRecebimento'] = safe_pct(totals['Recebidas'], totals['Transferencia'])
    totals['TxCpc'] = safe_pct(totals['Cpc'], totals['Recebidas'])
    totals['Conversao'] = safe_pct(totals['Acordo'], totals['Cpc'])
    return totals


def summarize_main(df: pd.DataFrame) -> Dict[str, Any]:
    totals = calc_summary(df, use_peak_logados=True)

    capacity = [
        {'label': 'AD Logados', 'icon': '🤖', 'value': fmt_int(totals['AD']), 'ratio': 'Pico no período'},
        {'label': 'ATH Logados', 'icon': '👤', 'value': fmt_int(totals['ATH']), 'ratio': 'Pico no período'},
        {'label': 'Mailing', 'icon': '🗂️', 'value': fmt_int(totals['Mailing']), 'ratio': 'Base disponível'},
    ]

    flow = []
    prior = None
    for key, icon in FLOW_ORDER:
        value = totals[key]
        if key == 'Custo':
            formatted = fmt_currency(value)
            ratio = 'Custo acumulado'
        elif key == 'Perda':
            formatted = fmt_int(value)
            ratio = fmt_pct(totals['PerdaPct'])
        else:
            formatted = fmt_int(value)
            if prior is None:
                ratio = 'Base do fluxo'
            elif key == 'Atendidas':
                ratio = fmt_pct(safe_pct(totals['Atendidas'], totals['Discado']))
            elif key == 'Transferencia':
                ratio = fmt_pct(safe_pct(totals['Transferencia'], totals['Atendidas']))
            elif key == 'Recebidas':
                ratio = fmt_pct(safe_pct(totals['Recebidas'], totals['Transferencia']))
            elif key == 'Cpc':
                ratio = fmt_pct(safe_pct(totals['Cpc'], totals['Recebidas']))
            elif key == 'Acordo':
                ratio = fmt_pct(safe_pct(totals['Acordo'], totals['Cpc']))
            else:
                ratio = ''
        flow.append({'label': {'Perda': 'Perda', 'Transferencia': 'Transferidas (CPC AD)', 'Recebidas': 'Recebidas Operador', 'Cpc': 'CPC Operador', 'Custo': 'Custo Telecom'}.get(key, key), 'icon': icon, 'value': formatted, 'ratio': ratio})
        prior = key

    base_group = df.groupby(['DtStr', 'Hour'], as_index=False).agg({
        'Mailing': 'max', 'AD': 'max', 'ATH': 'max', 'Discado': 'sum', 'Atendidas': 'sum',
        'Transferencia': 'sum', 'Perda': 'sum', 'Recebidas': 'sum', 'Cpc': 'sum', 'Acordo': 'sum', 'Custo': 'sum', 'Spin': 'mean'
    }).sort_values(['DtStr', 'Hour'])

    base_group['Hit Rate'] = base_group.apply(lambda x: safe_pct(x['Atendidas'], x['Discado']), axis=1)
    base_group['Tx Transferência'] = base_group.apply(lambda x: safe_pct(x['Transferencia'], x['Atendidas']), axis=1)
    base_group['Taxa Perda'] = base_group.apply(lambda x: safe_pct(x['Perda'], x['Transferencia']), axis=1)
    base_group['Taxa Abandono'] = base_group.apply(lambda x: safe_pct(x['Transferencia'] - x['Recebidas'], x['Transferencia']), axis=1)

    # Quando a base já traz %Perda e %Abandono, usar estes campos como fonte.
    # A agregação usa média ponderada por Transferencia para não distorcer campanhas/horários.
    pct_base = []
    for keys, grp in df.groupby(['DtStr', 'Hour']):
        pct_base.append({
            'DtStr': keys[0],
            'Hour': keys[1],
            'Taxa Perda Base': weighted_percent(grp, '%Perda', 'Transferencia'),
            'Taxa Abandono Base': weighted_percent(grp, '%Abandono', 'Transferencia'),
        })
    if pct_base:
        pct_base_df = pd.DataFrame(pct_base)
        base_group = base_group.merge(pct_base_df, on=['DtStr', 'Hour'], how='left')
        base_group['Taxa Perda'] = base_group['Taxa Perda Base'].combine_first(base_group['Taxa Perda'])
        base_group['Taxa Abandono'] = base_group['Taxa Abandono Base'].combine_first(base_group['Taxa Abandono'])
    base_group['Tx Recebimento'] = base_group.apply(lambda x: safe_pct(x['Recebidas'], x['Transferencia']), axis=1)
    base_group['Tx CPC Operador'] = base_group.apply(lambda x: safe_pct(x['Cpc'], x['Recebidas']), axis=1)
    base_group['Conv. Acordo'] = base_group.apply(lambda x: safe_pct(x['Acordo'], x['Cpc']), axis=1)

    by_hour = base_group.groupby('Hour', as_index=False).agg({
        'Discado': 'sum', 'Atendidas': 'sum', 'Transferencia': 'sum', 'Perda': 'sum', 'Recebidas': 'sum', 'Cpc': 'sum', 'Acordo': 'sum',
        'Spin': 'mean'
    }).sort_values('Hour')
    by_hour['Hit Rate'] = by_hour.apply(lambda x: safe_pct(x['Atendidas'], x['Discado']), axis=1)
    by_hour['Taxa Perda'] = by_hour.apply(lambda x: safe_pct(x['Perda'], x['Transferencia']), axis=1)
    by_hour['Taxa Abandono'] = by_hour.apply(lambda x: safe_pct(x['Transferencia'] - x['Recebidas'], x['Transferencia']), axis=1)

    pct_hour = []
    for hour_key, grp in df.groupby('Hour'):
        pct_hour.append({
            'Hour': hour_key,
            'Taxa Perda Base': weighted_percent(grp, '%Perda', 'Transferencia'),
            'Taxa Abandono Base': weighted_percent(grp, '%Abandono', 'Transferencia'),
        })
    if pct_hour:
        pct_hour_df = pd.DataFrame(pct_hour)
        by_hour = by_hour.merge(pct_hour_df, on='Hour', how='left')
        by_hour['Taxa Perda'] = by_hour['Taxa Perda Base'].combine_first(by_hour['Taxa Perda'])
        by_hour['Taxa Abandono'] = by_hour['Taxa Abandono Base'].combine_first(by_hour['Taxa Abandono'])
    by_hour['Tx Recebimento'] = by_hour.apply(lambda x: safe_pct(x['Recebidas'], x['Transferencia']), axis=1)
    by_hour['Tx CPC Operador'] = by_hour.apply(lambda x: safe_pct(x['Cpc'], x['Recebidas']), axis=1)
    by_hour['Conv. Acordo'] = by_hour.apply(lambda x: safe_pct(x['Acordo'], x['Cpc']), axis=1)
    by_hour['Tx Transferência'] = by_hour.apply(lambda x: safe_pct(x['Transferencia'], x['Atendidas']), axis=1)

    chart_labels = [f"{int(h):02d}:00" for h in by_hour['Hour'].tolist()]
    chart_series = {
        'discado': by_hour['Discado'].round(0).astype(int).tolist(),
        'atendidas': by_hour['Atendidas'].round(0).astype(int).tolist(),
        'transferidas': by_hour['Transferencia'].round(0).astype(int).tolist(),
        'perda': by_hour['Perda'].round(0).astype(int).tolist(),
        'recebidas': by_hour['Recebidas'].round(0).astype(int).tolist(),
        'cpc': by_hour['Cpc'].round(0).astype(int).tolist(),
        'acordo': by_hour['Acordo'].round(0).astype(int).tolist(),
        'spin': by_hour['Spin'].round(2).tolist(),
        'hit_rate': by_hour['Hit Rate'].round(2).tolist(),
        'perda_pct': by_hour['Taxa Perda'].round(2).tolist(),
        'abandono': by_hour['Taxa Abandono'].round(2).tolist(),
        'tx_recebimento': by_hour['Tx Recebimento'].round(2).tolist(),
        'tx_cpc': by_hour['Tx CPC Operador'].round(2).tolist(),
        'conversao': by_hour['Conv. Acordo'].round(2).tolist(),
    }

    hourly_table = []
    for _, row in base_group.iterrows():
        hourly_table.append({
            'Data': row['DtStr'],
            'Hour': f"{int(row['Hour']):02d}:00",
            'Mailing': fmt_int(row['Mailing']),
            'AD': fmt_int(row['AD']),
            'ATH': fmt_int(row['ATH']),
            'Discado': fmt_int(row['Discado']),
            'Atendidas': fmt_int(row['Atendidas']),
            'Transferencia': fmt_int(row['Transferencia']),
            'Perda': fmt_int(row['Perda']),
            'Recebidas': fmt_int(row['Recebidas']),
            'Cpc': fmt_int(row['Cpc']),
            'Acordo': fmt_int(row['Acordo']),
            'Custo': fmt_currency(row['Custo']),
            'Hit Rate': fmt_pct(row['Hit Rate']),
            'Tx Transferência': fmt_pct(row['Tx Transferência']),
            'Taxa Perda': fmt_pct(row['Taxa Perda']),
            'Taxa Abandono': fmt_pct(row['Taxa Abandono']),
            'Tx Recebimento': fmt_pct(row['Tx Recebimento']),
            'Tx CPC Operador': fmt_pct(row['Tx CPC Operador']),
            'Conv. Acordo': fmt_pct(row['Conv. Acordo']),
        })

    extras = {
        'Taxa Atendimento': fmt_pct(totals['HitRate']),
        'Taxa Transferência': fmt_pct(totals['TxTransferencia']),
        'Taxa Recebimento': fmt_pct(totals['TxRecebimento']),
        'Taxa CPC Operador': fmt_pct(totals['TxCpc']),
        'Conversão Acordo': fmt_pct(totals['Conversao']),
    }

    metric_charts = [
        {'id': 'chartDiscado', 'title': 'Discado x Spin', 'bar_label': 'Discado', 'line_label': 'Spin', 'bar_key': 'discado', 'line_key': 'spin'},
        {'id': 'chartAtendidas', 'title': 'Atendidas x Hit Rate', 'bar_label': 'Atendidas', 'line_label': 'Hit Rate', 'bar_key': 'atendidas', 'line_key': 'hit_rate'},
        {'id': 'chartTransferidas', 'title': 'Transferidas x Taxa de Abandono', 'bar_label': 'Transferidas', 'line_label': 'Taxa de Abandono', 'bar_key': 'transferidas', 'line_key': 'abandono'},
        {'id': 'chartRecebidas', 'title': 'Recebidas x Taxa de Recebimento', 'bar_label': 'Recebidas', 'line_label': 'Taxa de Recebimento', 'bar_key': 'recebidas', 'line_key': 'tx_recebimento'},
        {'id': 'chartCpc', 'title': 'CPC x Taxa de CPC Operador', 'bar_label': 'CPC', 'line_label': 'Taxa de CPC Operador', 'bar_key': 'cpc', 'line_key': 'tx_cpc'},
        {'id': 'chartAcordo', 'title': 'Acordo x Taxa de Conversão', 'bar_label': 'Acordo', 'line_label': 'Taxa de Conversão', 'bar_key': 'acordo', 'line_key': 'conversao'},
    ]

    return {
        'capacity': capacity,
        'flow': flow,
        'extras': extras,
        'perda': {'label': 'Taxa Perda', 'value': fmt_pct(totals['PerdaPct']), 'class': classify_abandonment(totals['PerdaPct'])},
        'abandono': {'label': 'Taxa Abandono', 'value': fmt_pct(totals['Abandono']), 'class': classify_abandonment(totals['Abandono'])},
        'chart_labels': chart_labels,
        'chart_series': chart_series,
        'metric_charts': metric_charts,
        'hourly_table': hourly_table,
    }


def build_compare_card(label: str, icon: str, preference: str, a_val: float, b_val: float, kind: str = 'number') -> Dict[str, Any]:
    delta_abs = a_val - b_val
    delta_pct = 0.0 if b_val == 0 else ((a_val / b_val) - 1) * 100
    css = classify_delta(delta_pct, preference)

    if kind == 'currency':
        fa, fb, dabs = fmt_currency(a_val), fmt_currency(b_val), fmt_currency(delta_abs)
    elif kind == 'percent':
        fa, fb, dabs = fmt_pct(a_val), fmt_pct(b_val), fmt_pct(delta_abs)
    else:
        fa, fb, dabs = fmt_int(a_val), fmt_int(b_val), fmt_int(delta_abs)

    return {
        'label': label,
        'icon': icon,
        'a': fa,
        'b': fb,
        'delta_pct': fmt_pct(delta_pct),
        'delta_abs': dabs,
        'class': css,
    }


def summarize_comparison(df_a: pd.DataFrame, df_b: pd.DataFrame, campaign_a: str, campaign_b: str) -> Dict[str, Any]:
    sum_a = calc_summary(df_a, use_peak_logados=True)
    sum_b = calc_summary(df_b, use_peak_logados=True)

    # Regra do cenário comparativo:
    # a campanha B representa a operação ativa, então a conversão deve ser Acordo / Transferidas.
    sum_b['Conversao'] = safe_pct(sum_b['Acordo'], sum_b['Transferencia'])

    cards = []
    for key, label, icon, preference in COMPARE_METRICS:
        kind = 'number'
        if key in {'Abandono', 'HitRate', 'TxTransferencia', 'TxRecebimento', 'TxCpc', 'Conversao'}:
            kind = 'percent'
        elif key == 'Custo':
            kind = 'currency'
        cards.append(build_compare_card(label, icon, preference, sum_a.get(key, 0.0), sum_b.get(key, 0.0), kind))

    funil_a = [
        {'label': 'Mailing', 'value': fmt_int(sum_a['Mailing']), 'hint': 'Base consolidada', 'icon': '🗂️'},
        {'label': 'Discado', 'value': fmt_int(sum_a['Discado']), 'hint': f"Spin {sum_a['Spin']:.2f}".replace('.', ','), 'icon': '📞'},
        {'label': 'Atendidas', 'value': fmt_int(sum_a['Atendidas']), 'hint': f"Hit {fmt_pct(sum_a['HitRate'])}", 'icon': '🟢'},
        {'label': 'CPC AD', 'value': fmt_int(sum_a['Transferencia']), 'hint': f"Tx {fmt_pct(sum_a['TxTransferencia'])}", 'icon': '🤖'},
        {'label': 'Acordo', 'value': fmt_int(sum_a['Acordo']), 'hint': f"Conv {fmt_pct(sum_a['Conversao'])}", 'icon': '💰'},
    ]
    funil_b = [
        {'label': 'Mailing', 'value': fmt_int(sum_b['Mailing']), 'hint': 'Base consolidada', 'icon': '🗂️'},
        {'label': 'Discado', 'value': fmt_int(sum_b['Discado']), 'hint': f"Spin {sum_b['Spin']:.2f}".replace('.', ','), 'icon': '📞'},
        {'label': 'Atendidas', 'value': fmt_int(sum_b['Atendidas']), 'hint': f"Hit {fmt_pct(sum_b['HitRate'])}", 'icon': '🟢'},
        {'label': 'CPC AD', 'value': fmt_int(sum_b['Transferencia']), 'hint': f"Tx {fmt_pct(sum_b['TxTransferencia'])}", 'icon': '🤖'},
        {'label': 'Acordo', 'value': fmt_int(sum_b['Acordo']), 'hint': f"Conv {fmt_pct(sum_b['Conversao'])}", 'icon': '💰'},
    ]

    insight = None
    if sum_a['Acordo'] > sum_b['Acordo'] and sum_a['Custo'] > sum_b['Custo']:
        insight = f'{campaign_a} gera mais acordos no período, porém com custo telecom acima de {campaign_b}. Vale equilibrar eficiência e custo por conversão.'
    elif sum_a['Acordo'] > sum_b['Acordo'] and sum_a['Custo'] <= sum_b['Custo']:
        insight = f'{campaign_a} combina melhor resultado e disciplina de custo no período filtrado, com mais acordos e custo controlado frente a {campaign_b}.'
    elif sum_b['Acordo'] > sum_a['Acordo'] and sum_b['Custo'] <= sum_a['Custo']:
        insight = f'{campaign_b} apresenta o melhor equilíbrio entre conversão e custo telecom no período analisado.'
    elif sum_a['HitRate'] > sum_b['HitRate'] and sum_a['TxTransferencia'] > sum_b['TxTransferencia']:
        insight = f'{campaign_a} está mais eficiente no topo do funil, com melhor conexão e melhor passagem para a etapa seguinte.'
    elif sum_b['HitRate'] > sum_a['HitRate'] and sum_b['TxTransferencia'] > sum_a['TxTransferencia']:
        insight = f'{campaign_b} ganha tração no topo do funil e merece atenção como referência operacional para o período filtrado.'
    else:
        insight = f'As campanhas mostram comportamentos diferentes. O melhor recorte para decisão está no equilíbrio entre acordos, custo telecom e taxa de transferência.'

    return {
        'campaign_a': campaign_a,
        'campaign_b': campaign_b,
        'funil_a': funil_a,
        'funil_b': funil_b,
        'cards': cards,
        'insight': insight,
    }


def apply_main_filters(df: pd.DataFrame, campaign: str, date: str) -> pd.DataFrame:
    out = df.copy()
    if campaign != 'Todos':
        out = out[out['NomeCampanha'] == campaign]
    if date != 'Todos':
        out = out[out['DtStr'] == date]
    return out


def apply_range_filters(
    df: pd.DataFrame,
    campaign: str,
    start_date: str,
    end_date: str,
    start_hour: str = '',
    end_hour: str = '',
) -> pd.DataFrame:
    out = df.copy()
    if campaign != 'Todos':
        out = out[out['NomeCampanha'] == campaign]
    if start_date:
        out = out[out['DtStr'] >= start_date]
    if end_date:
        out = out[out['DtStr'] <= end_date]

    # Filtro único de horário para a visão comparativa.
    # Quando preenchido, ele afeta as campanhas A e B ao mesmo tempo.
    if start_hour != '':
        out = out[out['Hour'] >= int(start_hour)]
    if end_hour != '':
        out = out[out['Hour'] <= int(end_hour)]
    return out


# ===== Aba de Tabulacao =====
TAB_COLUMN_ALIASES = {
    'data': 'data',
    'dt': 'data',
    'hora': 'Hora',
    'hour': 'Hora',
    'nomecampanha': 'NomeCampanha',
    'campanha': 'NomeCampanha',
    'origem_tabulacao': 'Origem_Tabulacao',
    'origem_tabulação': 'Origem_Tabulacao',
    'origemtabulacao': 'Origem_Tabulacao',
    'origemtabulação': 'Origem_Tabulacao',
    'tipo': 'Origem_Tabulacao',
    'tabulacao': 'Tabulacao',
    'tabulação': 'Tabulacao',
    'classificacao': 'Classificacao',
    'classificação': 'Classificacao',
    'class_loc': 'Class_Loc',
    'classloc': 'Class_Loc',
    'class_loca': 'Class_Loc',
    'class_rec': 'Class_Rec',
    'classrec': 'Class_Rec',
    'quantidade': 'Quantidade',
    'qtd': 'Quantidade',
    'tempo_total_tabulacao': 'Tempo_Total_Tabulacao',
    'tempo_total_tabulação': 'Tempo_Total_Tabulacao',
    'tempototaltabulacao': 'Tempo_Total_Tabulacao',
    'tempototaltabulação': 'Tempo_Total_Tabulacao',
    'tempo_total': 'Tempo_Total_Tabulacao',
    'tma': 'TMA',
    'tma_loc': 'TMA_LOC',
    'tmaloc': 'TMA_LOC',
    'tma_locator': 'TMA_LOC',
    'tma_rec': 'TMA_REC',
    'tmarec': 'TMA_REC',
}


def clean_key(value: Any) -> str:
    return str(value).strip().lower().replace(' ', '').replace('-', '').replace('_', '')


def normalize_tabulacao_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    tempo_seen = 0
    for col in df.columns:
        raw = str(col).strip()
        key = raw.lower().replace(' ', '').replace('-', '').replace('_', '')
        key_alias = raw.strip().lower().replace(' ', '_')

        if key.startswith('tempota'):
            tempo_seen += 1
            rename_map[col] = 'Tempo_LOC' if tempo_seen == 1 else 'Tempo_REC'
        elif key_alias in TAB_COLUMN_ALIASES:
            rename_map[col] = TAB_COLUMN_ALIASES[key_alias]
        elif key in TAB_COLUMN_ALIASES:
            rename_map[col] = TAB_COLUMN_ALIASES[key]
        elif key.endswith('horas'):
            digits = ''.join(ch for ch in key if ch.isdigit())
            if digits:
                rename_map[col] = f'{int(digits)}horas'
    return df.rename(columns=rename_map)


def time_to_seconds(value: Any) -> float:
    if pd.isna(value):
        return 0.0
    if hasattr(value, 'hour') and hasattr(value, 'minute') and hasattr(value, 'second'):
        return float(value.hour * 3600 + value.minute * 60 + value.second)
    text = str(value).strip()
    if text in {'', '--', '::', 'nan', 'NaT'}:
        return 0.0
    try:
        td = pd.to_timedelta(text)
        return float(td.total_seconds())
    except Exception:
        parts = text.split(':')
        if len(parts) == 3:
            try:
                return float(int(parts[0]) * 3600 + int(parts[1]) * 60 + int(float(parts[2])))
            except Exception:
                return 0.0
    return 0.0


def fmt_time(seconds: float) -> str:
    seconds = int(round(seconds or 0))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f'{h:02d}:{m:02d}:{s:02d}'


def weighted_tma_seconds(df: pd.DataFrame, tma_col: str = 'TMA_Seg') -> float:
    if df.empty or 'Quantidade' not in df.columns:
        return 0.0
    weight = pd.to_numeric(df['Quantidade'], errors='coerce').fillna(0)
    tma = pd.to_numeric(df[tma_col], errors='coerce').fillna(0)
    den = float(weight.sum())
    if den <= 0:
        return float(tma.mean()) if len(tma) else 0.0
    return float((tma * weight).sum() / den)


def load_tabulacao_data() -> pd.DataFrame:
    """Carrega a aba de tabulação.

    Suporta dois layouts:
    1) Novo layout linha a linha:
       data, Hora, NomeCampanha, Origem_Tabulação, Tabulacao, Classificacao,
       Quantidade, Tempo_Total_Tabulação, TMA.
    2) Layout antigo com Class_Loc/Class_Rec e colunas 8horas, 9horas...
    """
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f'Arquivo Excel nao encontrado em: {EXCEL_PATH}.')
    if EXCEL_PATH.suffix.lower() not in {'.xlsx', '.xls'}:
        raise ValueError('A aba de tabulacao precisa estar em um Excel com sheets.')

    sheet_env = os.getenv('TABULACAO_SHEET', '').strip()
    if sheet_env:
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_env)
    else:
        xls = pd.ExcelFile(EXCEL_PATH)
        if len(xls.sheet_names) < 2:
            raise ValueError('Crie uma segunda aba no Excel para a base de tabulacao ou defina TABULACAO_SHEET.')
        df = pd.read_excel(EXCEL_PATH, sheet_name=xls.sheet_names[1])

    df = normalize_tabulacao_columns(df)

    required = ['data', 'NomeCampanha', 'Tabulacao', 'Quantidade']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f'Colunas obrigatorias da aba de tabulacao ausentes: {", ".join(missing)}')

    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = df.dropna(subset=['data']).copy()
    df['DataStr'] = df['data'].dt.strftime('%Y-%m-%d')
    df['NomeCampanha'] = df['NomeCampanha'].astype(str)
    df['Tabulacao'] = df['Tabulacao'].fillna('Sem tabulacao').astype(str)
    df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce').fillna(0)

    # Novo layout: usa Origem_Tabulação para separar Locator x Receptivo.
    if 'Origem_Tabulacao' in df.columns:
        df['Tipo'] = df['Origem_Tabulacao'].fillna('').astype(str).str.strip()
        df['Tipo'] = df['Tipo'].apply(lambda x: 'Locator' if 'locator' in x.lower() else ('Receptivo' if 'receptivo' in x.lower() else x))
        df.loc[~df['Tipo'].isin(['Locator', 'Receptivo']), 'Tipo'] = df.loc[~df['Tipo'].isin(['Locator', 'Receptivo']), 'NomeCampanha'].apply(
            lambda x: 'Locator' if 'locator' in str(x).lower() else 'Receptivo'
        )
    else:
        # Layout antigo: fallback por nome da campanha.
        df['Tipo'] = df['NomeCampanha'].apply(lambda x: 'Locator' if 'locator' in str(x).lower() else 'Receptivo')

    if 'Classificacao' in df.columns:
        df['Classificacao'] = df['Classificacao'].fillna('Sem classificacao').astype(str)
    else:
        df['Class_Loc'] = df['Class_Loc'].fillna('Sem classificacao').astype(str) if 'Class_Loc' in df.columns else 'Sem classificacao'
        df['Class_Rec'] = df['Class_Rec'].fillna('Sem classificacao').astype(str) if 'Class_Rec' in df.columns else 'Sem classificacao'
        df['Classificacao'] = df.apply(lambda r: r['Class_Loc'] if r['Tipo'] == 'Locator' else r['Class_Rec'], axis=1)

    if 'Hora' in df.columns:
        df['Hora'] = pd.to_numeric(df['Hora'], errors='coerce')
        df = df.dropna(subset=['Hora']).copy()
        df['Hora'] = df['Hora'].astype(int)

    # Novo layout: TMA único por linha.
    if 'TMA' in df.columns:
        df['TMA_Seg'] = df['TMA'].apply(time_to_seconds)
    else:
        for col in ['TMA_LOC', 'TMA_REC', 'Tempo_LOC', 'Tempo_REC']:
            if col not in df.columns:
                df[col] = '00:00:00'
            df[col + '_Seg'] = df[col].apply(time_to_seconds)
        df['TMA_Seg'] = df.apply(lambda r: r['TMA_LOC_Seg'] if r['Tipo'] == 'Locator' else r['TMA_REC_Seg'], axis=1)

    if 'Tempo_Total_Tabulacao' in df.columns:
        df['Tempo_Total_Seg'] = df['Tempo_Total_Tabulacao'].apply(time_to_seconds)
    else:
        df['Tempo_Total_Seg'] = df['TMA_Seg'] * df['Quantidade']

    # Layout antigo com colunas 8horas, 9horas...
    hour_cols = []
    for col in df.columns:
        c = str(col).lower()
        if c.endswith('horas') and ''.join(ch for ch in c if ch.isdigit()):
            hour_cols.append(col)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df.attrs['hour_cols'] = sorted(hour_cols, key=lambda x: int(''.join(ch for ch in str(x) if ch.isdigit())))
    return df


def apply_tabulacao_filters(df: pd.DataFrame, date: str, campaign: str = 'Todos') -> pd.DataFrame:
    """Filtro da aba de Tabulação por data e NomeCampanha.
    Locator e Receptivo continuam aparecendo lado a lado, mas agora podem ser
    separados por campanha/receptivo conforme o campo NomeCampanha da base.
    """
    out = df.copy()
    if date != 'Todos':
        out = out[out['DataStr'] == date]
    if campaign != 'Todos' and 'NomeCampanha' in out.columns:
        out = out[out['NomeCampanha'].astype(str) == str(campaign)]
    return out


def tab_group_payload(df: pd.DataFrame, tipo: str, top_n: int = 12) -> Dict[str, Any]:
    part = df[df['Tipo'] == tipo].copy()
    if part.empty:
        return {'labels': [], 'volume': [], 'tma': [], 'tma_fmt': []}
    grouped = part.groupby('Tabulacao', as_index=False).apply(
        lambda g: pd.Series({'Quantidade': g['Quantidade'].sum(), 'TMA_Seg': weighted_tma_seconds(g)})
    ).reset_index(drop=True)
    grouped = grouped.sort_values('Quantidade', ascending=False).head(top_n)
    return {
        'labels': grouped['Tabulacao'].tolist(),
        'volume': grouped['Quantidade'].round(0).astype(int).tolist(),
        'tma': grouped['TMA_Seg'].round(0).astype(int).tolist(),
        'tma_fmt': [fmt_time(v) for v in grouped['TMA_Seg'].tolist()],
    }


def class_payload(df: pd.DataFrame) -> Dict[str, Any]:
    rows = []
    labels = sorted([x for x in df['Classificacao'].dropna().unique().tolist() if str(x).strip()])
    for cls in labels:
        loc = df[(df['Tipo'] == 'Locator') & (df['Classificacao'] == cls)]
        rec = df[(df['Tipo'] == 'Receptivo') & (df['Classificacao'] == cls)]
        loc_tma = weighted_tma_seconds(loc)
        rec_tma = weighted_tma_seconds(rec)
        rows.append({
            'Classificacao': cls,
            'Volume Locator': fmt_int(loc['Quantidade'].sum()),
            'TMA Locator': fmt_time(loc_tma),
            'Volume Receptivo': fmt_int(rec['Quantidade'].sum()),
            'TMA Receptivo': fmt_time(rec_tma),
            'loc_tma_sec': int(round(loc_tma)),
            'rec_tma_sec': int(round(rec_tma)),
        })
    rows = sorted(rows, key=lambda r: (r['loc_tma_sec'] + r['rec_tma_sec']), reverse=True)
    return {
        'labels': [r['Classificacao'] for r in rows],
        'locator_tma': [r['loc_tma_sec'] for r in rows],
        'receptivo_tma': [r['rec_tma_sec'] for r in rows],
        'rows': rows,
    }


def hour_columns(df: pd.DataFrame) -> list[str]:
    cols = []
    for col in df.columns:
        c = str(col).lower()
        if c.endswith('horas') and ''.join(ch for ch in c if ch.isdigit()):
            cols.append(col)
    return sorted(cols, key=lambda x: int(''.join(ch for ch in str(x) if ch.isdigit())))


def hourly_tma_payload(df: pd.DataFrame, selected_class: str) -> Dict[str, Any]:
    work = df.copy()
    if selected_class and selected_class != 'Todos':
        work = work[work['Classificacao'] == selected_class]

    # Novo layout: já vem uma coluna Hora linha a linha.
    if 'Hora' in work.columns:
        all_hours = sorted([int(h) for h in work['Hora'].dropna().unique().tolist()])
        labels = [f'{h:02d}:00' for h in all_hours]

        def series_for(tipo: str) -> list[int]:
            part = work[work['Tipo'] == tipo]
            values = []
            for h in all_hours:
                ph = part[part['Hora'] == h]
                values.append(int(round(weighted_tma_seconds(ph))) if not ph.empty else 0)
            return values

        return {
            'labels': labels,
            'locator': series_for('Locator'),
            'receptivo': series_for('Receptivo'),
            'selected_class': selected_class,
        }

    # Layout antigo: usa colunas 8horas, 9horas...
    hcols = hour_columns(work)
    labels = [f"{int(''.join(ch for ch in str(c) if ch.isdigit())):02d}:00" for c in hcols]

    def series_for(tipo: str) -> list[int]:
        part = work[work['Tipo'] == tipo]
        values = []
        for col in hcols:
            if part.empty:
                values.append(0)
                continue
            vol = pd.to_numeric(part[col], errors='coerce').fillna(0)
            tma = pd.to_numeric(part['TMA_Seg'], errors='coerce').fillna(0)
            den = float(vol.sum())
            values.append(int(round(float((vol * tma).sum() / den))) if den > 0 else 0)
        return values

    return {
        'labels': labels,
        'locator': series_for('Locator'),
        'receptivo': series_for('Receptivo'),
        'selected_class': selected_class,
    }


def weighted_tma_operacional(df: pd.DataFrame, tipo: str) -> float:
    """TMA consolidado dos cards principais considerando apenas Contato e CPC.

    Isso evita que grandes volumes de Discado com TMA 00:00:00 derrubem o TMA ponderado do Locator.
    """
    part = df[df['Tipo'] == tipo].copy()
    if part.empty:
        return 0.0
    cls = part['Classificacao'].astype(str).str.strip().str.lower()
    part = part[cls.isin(['contato', 'cpc'])]
    part = part[pd.to_numeric(part['TMA_Seg'], errors='coerce').fillna(0) > 0]
    return weighted_tma_seconds(part)


def classification_card_payload(df: pd.DataFrame, tipo: str, classificacoes: list[str]) -> list[Dict[str, Any]]:
    """Cards de classificação exibem somente o TMA consolidado de cada etapa."""
    part = df[df['Tipo'] == tipo]
    cards = []
    icons = {'Contato': '🤝', 'Cpc': '✅', 'CPC': '✅', 'Acordo': '💰'}
    for cls in classificacoes:
        cls_part = part[part['Classificacao'].astype(str).str.lower() == cls.lower()]
        tma = weighted_tma_seconds(cls_part)
        cards.append({
            'label': cls.upper() if cls.lower() == 'cpc' else cls,
            'icon': icons.get(cls, '📌'),
            'value': fmt_time(tma),
            'hint': 'TMA consolidado',
        })
    return cards


def summarize_tabulacao(df: pd.DataFrame, selected_class: str = 'Todos', locator_class: str = 'Todos', receptivo_class: str = 'Todos') -> Dict[str, Any]:
    loc = df[df['Tipo'] == 'Locator']
    rec = df[df['Tipo'] == 'Receptivo']
    total_qtd = float(df['Quantidade'].sum())

    locator_cards = [
        {'label': 'TMA Locator', 'icon': '⏱️', 'value': fmt_time(weighted_tma_operacional(df, 'Locator')), 'hint': 'Contato + CPC'},
    ]
    receptivo_cards = [
        {'label': 'TMA Receptivo', 'icon': '🎧', 'value': fmt_time(weighted_tma_operacional(df, 'Receptivo')), 'hint': 'Contato + CPC'},
    ]

    ranking = df.groupby(['Tipo', 'Tabulacao', 'Classificacao'], as_index=False).apply(
        lambda g: pd.Series({'Quantidade': g['Quantidade'].sum(), 'TMA_Seg': weighted_tma_seconds(g)})
    ).reset_index(drop=True).sort_values('Quantidade', ascending=False).head(20)
    ranking_rows = [{
        'Tipo': r['Tipo'],
        'Tabulacao': r['Tabulacao'],
        'Classificacao': r['Classificacao'],
        'Quantidade': fmt_int(r['Quantidade']),
        'TMA': fmt_time(r['TMA_Seg']),
    } for _, r in ranking.iterrows()]

    return {
        'locator_cards': locator_cards,
        'receptivo_cards': receptivo_cards,
        'locator_class_cards': classification_card_payload(df, 'Locator', ['Contato', 'Cpc']),
        'receptivo_class_cards': classification_card_payload(df, 'Receptivo', ['Contato', 'Cpc', 'Acordo']),
        'locator': tab_group_payload(df if locator_class == 'Todos' else df[(df['Tipo'] != 'Locator') | (df['Classificacao'] == locator_class)], 'Locator'),
        'receptivo': tab_group_payload(df if receptivo_class == 'Todos' else df[(df['Tipo'] != 'Receptivo') | (df['Classificacao'] == receptivo_class)], 'Receptivo'),
        'classes': class_payload(df),
        'hourly_tma': hourly_tma_payload(df, selected_class),
        'ranking_rows': ranking_rows,
    }


@app.route('/cliente/talentos/painel/tabulacao')
def talentos_tabulacao() -> str:
    if 'usuario' not in session:
        return redirect(url_for('login'))
    error = None
    context: Dict[str, Any] = {
        'page': 'tabulacao',
        'dates': [],
        'campaigns': [],
        'class_options': [],
        'selected_date': 'Todos',
        'selected_campaign': 'Todos',
        'selected_class': 'Todos',
        'selected_locator_class': 'Todos',
        'selected_receptivo_class': 'Todos',
        'locator_class_options': [],
        'receptivo_class_options': [],
        'summary': None,
    }
    try:
        df = load_tabulacao_data()
        dates = sorted(df['DataStr'].dropna().unique().tolist(), reverse=True)
        campaigns = sorted([x for x in df['NomeCampanha'].dropna().astype(str).unique().tolist() if str(x).strip()]) if 'NomeCampanha' in df.columns else []
        class_options = sorted([x for x in df['Classificacao'].dropna().unique().tolist() if str(x).strip()])
        locator_class_options = sorted([x for x in df.loc[df['Tipo'] == 'Locator', 'Classificacao'].dropna().unique().tolist() if str(x).strip()])
        receptivo_class_options = sorted([x for x in df.loc[df['Tipo'] == 'Receptivo', 'Classificacao'].dropna().unique().tolist() if str(x).strip()])

        selected_date = request.args.get('date', dates[0] if dates else 'Todos')
        selected_campaign = request.args.get('campanha', 'Todos')
        selected_class = request.args.get('classificacao', 'Todos')
        selected_locator_class = request.args.get('locator_class', 'Todos')
        selected_receptivo_class = request.args.get('receptivo_class', 'Todos')

        filtered = apply_tabulacao_filters(df, selected_date, selected_campaign)
        context.update({
            'dates': dates,
            'campaigns': campaigns,
            'class_options': class_options,
            'locator_class_options': locator_class_options,
            'receptivo_class_options': receptivo_class_options,
            'selected_date': selected_date,
            'selected_campaign': selected_campaign,
            'selected_class': selected_class,
            'selected_locator_class': selected_locator_class,
            'selected_receptivo_class': selected_receptivo_class,
            'summary': summarize_tabulacao(filtered, selected_class, selected_locator_class, selected_receptivo_class) if not filtered.empty else None,
        })
    except Exception as exc:
        error = str(exc)
    return render_template('tabulacao.html', error=error, **context)

@app.route('/cliente/talentos/painel')
def talentos_index() -> str:
    if 'usuario' not in session:
        return redirect(url_for('login'))
    error = None
    context: Dict[str, Any] = {
        'page': 'dashboard',
        'campaigns': [],
        'dates': [],
        'selected_campaign': 'Todos',
        'selected_date': 'Todos',
        'summary': None,
    }
    try:
        df = load_data()
        campaigns = sorted(df['NomeCampanha'].dropna().unique().tolist())
        dates = sorted(df['DtStr'].dropna().unique().tolist(), reverse=True)
        selected_campaign = request.args.get('campaign', 'Todos')
        selected_date = request.args.get('date', 'Todos')
        filtered = apply_main_filters(df, selected_campaign, selected_date)
        context.update({
            'campaigns': campaigns,
            'dates': dates,
            'selected_campaign': selected_campaign,
            'selected_date': selected_date,
            'summary': summarize_main(filtered) if not filtered.empty else None,
        })
    except Exception as exc:
        error = str(exc)
    return render_template('index.html', error=error, **context)


@app.route('/cliente/talentos/painel/comparativo')
def talentos_comparativo() -> str:
    if 'usuario' not in session:
        return redirect(url_for('login'))
    error = None
    context: Dict[str, Any] = {
        'page': 'comparativo',
        'campaigns': [],
        'comparison': None,
        'campaign_a': 'Todos',
        'campaign_b': 'Todos',
        'start_date': '',
        'end_date': '',
        'start_hour': '',
        'end_hour': '',
        'hour_options': list(range(24)),
    }
    try:
        df = load_data()
        campaigns = sorted(df['NomeCampanha'].dropna().unique().tolist())
        dates = sorted(df['DtStr'].dropna().unique().tolist())
        default_start = dates[0] if dates else ''
        default_end = dates[-1] if dates else ''
        campaign_a = request.args.get('campaign_a', campaigns[0] if campaigns else 'Todos')
        campaign_b = request.args.get('campaign_b', campaigns[1] if len(campaigns) > 1 else (campaigns[0] if campaigns else 'Todos'))
        start_date = request.args.get('start_date', default_start)
        end_date = request.args.get('end_date', default_end)
        start_hour = request.args.get('start_hour', '')
        end_hour = request.args.get('end_hour', '')

        df_a = apply_range_filters(df, campaign_a, start_date, end_date, start_hour, end_hour)
        df_b = apply_range_filters(df, campaign_b, start_date, end_date, start_hour, end_hour)

        comparison = None
        if not df_a.empty or not df_b.empty:
            comparison = summarize_comparison(df_a, df_b, campaign_a, campaign_b)

        context.update({
            'campaigns': campaigns,
            'campaign_a': campaign_a,
            'campaign_b': campaign_b,
            'start_date': start_date,
            'end_date': end_date,
            'start_hour': start_hour,
            'end_hour': end_hour,
            'hour_options': list(range(24)),
            'comparison': comparison,
        })
    except Exception as exc:
        error = str(exc)
    return render_template('comparativo.html', error=error, **context)



# ===== SKY | Negocie Online integrado no Cockpit V1.6 =====
import re
import numpy as np
import folium
from flask import jsonify

SKY_DATA_DIR = Path(__file__).resolve().parent / "data"
SKY_ARQUIVO_BASE = SKY_DATA_DIR / "Base_Dashboard_Sky.xlsx"

DDD_UF = {
    11:"SP",12:"SP",13:"SP",14:"SP",15:"SP",16:"SP",17:"SP",18:"SP",19:"SP",
    21:"RJ",22:"RJ",24:"RJ",
    27:"ES",28:"ES",
    31:"MG",32:"MG",33:"MG",34:"MG",35:"MG",37:"MG",38:"MG",
    41:"PR",42:"PR",43:"PR",44:"PR",45:"PR",46:"PR",
    47:"SC",48:"SC",49:"SC",
    51:"RS",53:"RS",54:"RS",55:"RS",
    61:"DF",
    62:"GO",64:"GO",
    63:"TO",
    65:"MT",66:"MT",
    67:"MS",
    68:"AC",
    69:"RO",
    71:"BA",73:"BA",74:"BA",75:"BA",77:"BA",
    79:"SE",
    81:"PE",87:"PE",
    82:"AL",
    83:"PB",
    84:"RN",
    85:"CE",88:"CE",
    86:"PI",89:"PI",
    91:"PA",93:"PA",94:"PA",
    92:"AM",97:"AM",
    95:"RR",
    96:"AP",
    98:"MA",99:"MA"
}

UF_COORDS = {
    "AC": [-8.77, -70.55],
    "AL": [-9.62, -36.82],
    "AP": [1.41, -51.77],
    "AM": [-3.47, -65.10],
    "BA": [-12.96, -41.70],
    "CE": [-5.20, -39.53],
    "DF": [-15.83, -47.86],
    "ES": [-19.19, -40.34],
    "GO": [-15.98, -49.86],
    "MA": [-5.42, -45.44],
    "MT": [-12.64, -55.42],
    "MS": [-20.51, -54.54],
    "MG": [-18.10, -44.38],
    "PA": [-3.79, -52.48],
    "PB": [-7.28, -36.72],
    "PR": [-24.89, -51.55],
    "PE": [-8.38, -37.86],
    "PI": [-6.60, -42.28],
    "RJ": [-22.25, -42.66],
    "RN": [-5.81, -36.59],
    "RS": [-30.17, -53.50],
    "RO": [-10.83, -63.34],
    "RR": [1.99, -61.33],
    "SC": [-27.45, -50.95],
    "SP": [-22.19, -48.79],
    "SE": [-10.57, -37.45],
    "TO": [-10.25, -48.25],
}

TODAS_UFS = list(UF_COORDS.keys())


def safe_div(a, b):
    try:
        if b == 0 or pd.isna(b):
            return 0
        return float(a) / float(b)
    except Exception:
        return 0


def br_number(value, decimals=0):
    try:
        if pd.isna(value) or np.isinf(value):
            value = 0
        return f"{float(value):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0"


def br_money(value):
    try:
        if pd.isna(value) or np.isinf(value):
            value = 0
        return "R$ " + f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def br_percent(value):
    try:
        if pd.isna(value) or np.isinf(value):
            value = 0
        return f"{float(value) * 100:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00%"


def seconds_to_hhmmss(seconds):
    try:
        seconds = int(seconds or 0)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        return "00:00:00"




def calcular_mailing_distinto_por_faixa(base, chave_distinta, chave_final=None):
    """Calcula Mailing sem duplicar linhas de tabulação/DDD.

    Regra:
    - Remove duplicidades por chave_distinta + Faixa_Atraso + MAILING.
    - Depois soma os valores distintos para a chave_final.

    Observação técnica:
    - As listas de chaves são deduplicadas para evitar erro de pandas:
      "Grouper for 'Faixa_Atraso' not 1-dimensional".
    """
    def _unique(seq):
        out = []
        for item in seq:
            if item not in out:
                out.append(item)
        return out

    chave_distinta = _unique(list(chave_distinta))
    chave_final = _unique(list(chave_final or chave_distinta))

    if base is None or base.empty:
        return pd.DataFrame(columns=chave_final + ["MAILING"])

    df_mail = base.copy()

    if "MAILING" not in df_mail.columns:
        df_mail["MAILING"] = 0

    df_mail["MAILING"] = pd.to_numeric(df_mail["MAILING"], errors="coerce").fillna(0)

    for col in _unique(chave_distinta + chave_final):
        if col not in df_mail.columns:
            df_mail[col] = ""

    for col in _unique(chave_distinta + chave_final):
        if str(col).upper() == "DATA":
            df_mail[col] = pd.to_datetime(df_mail[col], errors="coerce").dt.normalize()

    if "Faixa_Atraso" not in df_mail.columns:
        df_mail["Faixa_Atraso"] = "Sem faixa"

    df_mail["Faixa_Atraso"] = (
        df_mail["Faixa_Atraso"]
        .fillna("Sem faixa")
        .astype(str)
        .str.strip()
    )
    df_mail.loc[
        df_mail["Faixa_Atraso"].eq("") | df_mail["Faixa_Atraso"].str.lower().eq("nan"),
        "Faixa_Atraso"
    ] = "Sem faixa"

    # Evita duplicar Faixa_Atraso quando ela já está na chave.
    cols_distintos = _unique(chave_distinta + ["Faixa_Atraso", "MAILING"])

    distintos = (
        df_mail[cols_distintos]
        .drop_duplicates()
        .copy()
    )

    if not len(distintos):
        return pd.DataFrame(columns=chave_final + ["MAILING"])

    return (
        distintos.groupby(chave_final, as_index=False)
                 .agg({"MAILING": "sum"})
    )


def normalizar_colunas(df):
    renomear = {}
    for col in df.columns:
        original = str(col).strip()
        key = (
            original
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace(".", "_")
            .replace("/", "_")
        )

        mapa = {
            "data": "DATA",
            "dt": "DATA",
            "date": "DATA",

            "hour": "HOUR",
            "hours": "HOUR",
            "hora": "HOUR",
            "hr": "HOUR",
            "h": "HOUR",

            "campaignid": "CampaignId",
            "campaign_id": "CampaignId",
            "campaign": "CampaignId",
            "campanhaid": "CampaignId",
            "campanha_id": "CampaignId",
            "idcampanha": "CampaignId",
            "id_campanha": "CampaignId",

            "uf": "UF",
            "uf_ddd": "UF_DDD",
            "ddd": "UF_DDD",
            "prefix": "UF_DDD",
            "prefixo": "UF_DDD",

            "faixa_atraso": "Faixa_Atraso",
            "faixa": "Faixa_Atraso",

            "tabulacao": "Tabulacao",
            "tabulação": "Tabulacao",

            "classificado": "Classificado",
            "classificacao": "Classificado",
            "classificação": "Classificado",

            "mailing": "MAILING",
            "base": "MAILING",

            "discado": "Discado",
            "discagem": "Discado",

            "contato": "Contato",
            "atendidas": "Contato",
            "atendida": "Contato",

            "cpc": "Cpc",
            "ndoc": "NDOC",
            "acordo": "Acordo",

            "hangup": "HangUp",
            "%hangup": "PctHangUp",
            "hang_up": "HangUp",

            "tempo": "Tempo",
            "segundos": "Tempo",

            "custo_telecom": "Custo_Telecom",
            "custo": "Custo_Telecom",
        }

        if key in mapa:
            renomear[col] = mapa[key]

    return df.rename(columns=renomear)



# Cache simples para evitar reler o Excel a cada filtro/aba.
# O arquivo só é recarregado quando a data de modificação muda.
SKY_BASE_CACHE = {
    "mtime": None,
    "bases": None
}

SKY_SHEETS = {
    "daily": "Funil_Sumarizado",
    "hora": "Funil_Hora",
    "uf": "Funil_UF_Dia",
    # Visão de indicadores únicos. O carregador também aceita aliases como
    # Funil_Unique e Visao_Unique para facilitar a manutenção do Excel.
    "unique": "Unique",
}

SKY_SHEET_ALIASES = {
    "unique": ["Unique", "Funil_Unique", "Visao_Unique", "Visão Unique"],
}

def _normalizar_nome_sheet(nome):
    return str(nome or "").strip().lower().replace(" ", "_").replace("-", "_")

def _resolver_sheet(xls, nome_preferido, aliases=None):
    candidatos = [nome_preferido] + list(aliases or [])
    alvos = {_normalizar_nome_sheet(nome) for nome in candidatos}
    for sheet in xls.sheet_names:
        if _normalizar_nome_sheet(sheet) in alvos:
            return sheet
    return None

def _valor_percentual_para_decimal(serie):
    def conv(v):
        if pd.isna(v):
            return 0
        if isinstance(v, str):
            txt = v.strip().replace("%", "").replace(".", "").replace(",", ".")
            if txt in ["", "nan", "None", "%"]:
                return 0
            try:
                num = float(txt)
                return num / 100 if "%" in v or num > 1 else num
            except Exception:
                return 0
        try:
            num = float(v)
            return num / 100 if num > 1 else num
        except Exception:
            return 0
    return serie.apply(conv)

def _tempo_para_segundos(valor):
    if pd.isna(valor):
        return 0
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return float(valor)
    txt = str(valor).strip()
    if not txt or txt in ["::", "nan", "NaT"]:
        return 0
    partes = txt.split(":")
    try:
        if len(partes) == 3:
            return int(float(partes[0])) * 3600 + int(float(partes[1])) * 60 + int(float(partes[2]))
        if len(partes) == 2:
            return int(float(partes[0])) * 60 + int(float(partes[1]))
        return float(txt.replace(",", "."))
    except Exception:
        return 0


def _valor_monetario_para_float(valor):
    if pd.isna(valor):
        return 0.0
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return float(valor)
    txt = str(valor).strip().replace("R$", "").replace(" ", "")
    if not txt or txt.lower() in ["nan", "none"]:
        return 0.0
    # Formato brasileiro: 24.646,35 -> 24646.35
    if "," in txt:
        txt = txt.replace(".", "").replace(",", ".")
    try:
        return float(txt)
    except Exception:
        return 0.0


def preparar_base_unique_sky(df):
    """Normaliza a aba Unique sem exigir colunas das demais visões SKY."""
    df = normalizar_colunas(df.copy())

    # Colunas específicas da visão Unique que não fazem parte do normalizador geral.
    mapa_extra = {}
    for col in df.columns:
        key = _normalizar_nome_sheet(col)
        if key in ["valor_acordo", "valor_do_acordo", "valoracordo"]:
            mapa_extra[col] = "Valor_Acordo"
        elif key in ["penetracao", "penetração"]:
            mapa_extra[col] = "Penetracao"
        elif key in ["alo", "alô"]:
            mapa_extra[col] = "Alo"
        elif key in ["loc", "localizacao", "localização"]:
            mapa_extra[col] = "Loc"
        elif key in ["conversao", "conversão"]:
            mapa_extra[col] = "Conversao"
        elif key in ["abertura", "tipo_abertura", "visao", "visão"]:
            mapa_extra[col] = "Abertura"
    if mapa_extra:
        df = df.rename(columns=mapa_extra)

    colunas = ["DATA", "MAILING", "Discado", "Contato", "Cpc", "Acordo", "Valor_Acordo", "Penetracao", "Alo", "Loc", "Conversao", "Abertura"]
    for col in colunas:
        if col not in df.columns:
            df[col] = "" if col == "Abertura" else 0

    df["Abertura"] = df["Abertura"].fillna("").astype(str).str.strip()

    # A coluna DATA da aba Unique aceita dois formatos:
    #   Unique Dia -> 01/08/2026 (data normal)
    #   Unique Mês -> 202608 (AAAAMM)
    # Normalizamos o mensal para o primeiro dia do mês apenas internamente,
    # preservando a referência correta para os filtros do painel.
    def _parse_data_unique(valor, abertura):
        if pd.isna(valor):
            return pd.NaT
        txt = str(valor).strip()
        abertura_norm = str(abertura or "").strip().lower()

        # Excel pode entregar 202608 como número/float (202608.0).
        txt_num = re.sub(r"\.0+$", "", txt)
        if abertura_norm in ["unique mês", "unique mes"] and re.fullmatch(r"\d{6}", txt_num):
            try:
                return pd.Timestamp(year=int(txt_num[:4]), month=int(txt_num[4:6]), day=1)
            except Exception:
                return pd.NaT

        # Também aceita AAAAMM mesmo se Abertura vier com grafia diferente.
        if re.fullmatch(r"\d{6}", txt_num):
            try:
                return pd.Timestamp(year=int(txt_num[:4]), month=int(txt_num[4:6]), day=1)
            except Exception:
                return pd.NaT

        return pd.to_datetime(valor, errors="coerce", dayfirst=True)

    df["DATA"] = [
        _parse_data_unique(valor, abertura)
        for valor, abertura in zip(df["DATA"], df["Abertura"])
    ]
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df.dropna(subset=["DATA"]).copy()

    for col in ["MAILING", "Discado", "Contato", "Cpc", "Acordo"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("float64")
    df["Valor_Acordo"] = df["Valor_Acordo"].apply(_valor_monetario_para_float).astype("float64")
    for col in ["Penetracao", "Alo", "Loc", "Conversao"]:
        df[col] = _valor_percentual_para_decimal(df[col]).astype("float64")

    return df.sort_values("DATA")


def _datas_selecionadas_sky():
    datas = request.args.get("datas", "").strip()
    if not datas:
        return []
    partes = [p.strip() for p in re.split(r"[;,]", datas) if p.strip()]
    resultado = []
    for p in partes:
        dt = pd.to_datetime(p, errors="coerce", dayfirst=True)
        if pd.notna(dt):
            normalizada = dt.normalize()
            if normalizada not in resultado:
                resultado.append(normalizada)
    return resultado


def _normalizar_abertura_unique(series):
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace("ê", "e", regex=False)
        .str.replace("é", "e", regex=False)
        .str.replace("ã", "a", regex=False)
        .str.replace("ç", "c", regex=False)
    )


def aplicar_filtro_data_unique_sky(df):
    """
    Regra da Visão Unique:
    - o filtro de Mês é obrigatório quando houver mais de um mês na aba Unique;
    - com Mês selecionado + exatamente 1 data marcada -> Unique Dia daquela data;
    - com Mês selecionado + nenhuma data ou 2+ datas marcadas -> Unique Mes;
    - Faixa/Campanha e demais filtros não zeram nem alteram a Unique.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=df.columns if isinstance(df, pd.DataFrame) else []), "Unique Mês", "sem_base"

    mes = request.args.get("mes", "").strip()
    if not mes:
        # Não escolhemos automaticamente o mês mais recente, pois a base Unique
        # pode conter vários consolidados mensais. O usuário deve indicar o mês.
        return df.iloc[0:0].copy(), "Unique Mês", "selecione_mes"

    work = df.copy()
    datas_convertidas = _datas_selecionadas_sky()
    modo_dia = len(datas_convertidas) == 1
    abertura_alvo = "unique dia" if modo_dia else "unique mes"

    if "Abertura" in work.columns and work["Abertura"].fillna("").astype(str).str.strip().ne("").any():
        abertura_norm = _normalizar_abertura_unique(work["Abertura"])
        work = work[abertura_norm == abertura_alvo].copy()

    try:
        periodo = pd.Period(mes, freq="M")
        work = work[work["DATA"].dt.to_period("M") == periodo]
    except Exception:
        pass

    if modo_dia:
        data_alvo = datas_convertidas[0]
        work = work[work["DATA"].dt.normalize() == data_alvo]

    return work.copy(), ("Unique Dia" if modo_dia else "Unique Mês"), "ok"


def _linhas_detalhe_unique(df_detalhe):
    linhas = []
    if df_detalhe is None or df_detalhe.empty:
        return linhas

    for _, r in df_detalhe.sort_values("DATA", ascending=False).iterrows():
        penetracao = r["Penetracao"] if r["Penetracao"] > 0 else safe_div(r["Discado"], r["MAILING"])
        alo = r["Alo"] if r["Alo"] > 0 else safe_div(r["Contato"], r["Discado"])
        loc = r["Loc"] if r["Loc"] > 0 else safe_div(r["Cpc"], r["Contato"])
        conv = r["Conversao"] if r["Conversao"] > 0 else safe_div(r["Acordo"], r["Cpc"])
        linhas.append({
            "data": r["DATA"].strftime("%d/%m/%Y"),
            "mailing": br_number(r["MAILING"]),
            "discado": br_number(r["Discado"]),
            "contato": br_number(r["Contato"]),
            "cpc": br_number(r["Cpc"]),
            "acordo": br_number(r["Acordo"]),
            "valor_acordo": br_money(r["Valor_Acordo"]),
            "penetracao": br_percent(penetracao),
            "alo": br_percent(alo),
            "loc": br_percent(loc),
            "conversao": br_percent(conv),
        })
    return linhas


def montar_visao_unique_sky(df_unique):
    if not isinstance(df_unique, pd.DataFrame) or df_unique.empty:
        return {
            "disponivel": False, "cards": [], "eficiencia": [], "linhas": [],
            "periodo": "-", "modo": "Unique Mês", "motivo": "sem_base"
        }

    dfu, modo, motivo = aplicar_filtro_data_unique_sky(df_unique)
    if motivo == "selecione_mes":
        return {
            "disponivel": False, "cards": [], "eficiencia": [], "linhas": [],
            "periodo": "-", "modo": modo, "motivo": motivo
        }

    if dfu.empty:
        return {
            "disponivel": False, "cards": [], "eficiencia": [], "linhas": [],
            "periodo": "-", "modo": modo, "motivo": "sem_dados"
        }

    totais = {
        "MAILING": float(dfu["MAILING"].sum()),
        "Discado": float(dfu["Discado"].sum()),
        "Contato": float(dfu["Contato"].sum()),
        "Cpc": float(dfu["Cpc"].sum()),
        "Acordo": float(dfu["Acordo"].sum()),
        "Valor_Acordo": float(dfu["Valor_Acordo"].sum()),
    }
    totais["Penetracao"] = safe_div(totais["Discado"], totais["MAILING"])
    totais["Alo"] = safe_div(totais["Contato"], totais["Discado"])
    totais["Loc"] = safe_div(totais["Cpc"], totais["Contato"])
    totais["Conversao"] = safe_div(totais["Acordo"], totais["Cpc"])

    cards = [
        {"label": "Mailing Unique", "value": br_number(totais["MAILING"]), "icon": "database"},
        {"label": "Discado Unique", "value": br_number(totais["Discado"]), "icon": "phone-outgoing"},
        {"label": "Contato Unique", "value": br_number(totais["Contato"]), "icon": "users"},
        {"label": "CPC Unique", "value": br_number(totais["Cpc"]), "icon": "badge-check"},
        {"label": "Acordo Unique", "value": br_number(totais["Acordo"]), "icon": "handshake"},
        {"label": "Valor Acordo", "value": br_money(totais["Valor_Acordo"]), "icon": "circle-dollar-sign"},
    ]
    eficiencia = [
        {"label": "Penetração", "value": br_percent(totais["Penetracao"]), "desc": "Discado / Mailing"},
        {"label": "Alô", "value": br_percent(totais["Alo"]), "desc": "Contato / Discado"},
        {"label": "Localização", "value": br_percent(totais["Loc"]), "desc": "CPC / Contato"},
        {"label": "Conversão", "value": br_percent(totais["Conversao"]), "desc": "Acordo / CPC"},
    ]

    # O card pode estar no consolidado mensal, mas o detalhamento sempre deve
    # mostrar as linhas Unique Dia do mês escolhido. Em modo diário, mantém só
    # o dia selecionado para o detalhe acompanhar o card.
    mes = request.args.get("mes", "").strip()
    detalhe = df_unique.copy()
    if "Abertura" in detalhe.columns and detalhe["Abertura"].fillna("").astype(str).str.strip().ne("").any():
        detalhe = detalhe[_normalizar_abertura_unique(detalhe["Abertura"]) == "unique dia"].copy()
    try:
        periodo_mes = pd.Period(mes, freq="M")
        detalhe = detalhe[detalhe["DATA"].dt.to_period("M") == periodo_mes]
    except Exception:
        pass
    if modo == "Unique Dia":
        datas_convertidas = _datas_selecionadas_sky()
        if len(datas_convertidas) == 1:
            detalhe = detalhe[detalhe["DATA"].dt.normalize() == datas_convertidas[0]]

    linhas = _linhas_detalhe_unique(detalhe)

    if modo == "Unique Mês":
        periodo_texto = pd.Period(mes, freq="M").strftime("%m/%Y") if mes else "-"
    else:
        periodo_texto = f"{dfu['DATA'].min().strftime('%d/%m/%Y')} até {dfu['DATA'].max().strftime('%d/%m/%Y')}"

    return {
        "disponivel": True,
        "cards": cards,
        "eficiencia": eficiencia,
        "linhas": linhas,
        "periodo": periodo_texto,
        "modo": modo,
        "motivo": "ok",
    }

def preparar_base_sky(df, origem="daily"):
    df = normalizar_colunas(df.copy())

    # Fallback extra para hora quando o Excel vier com Hour/Hora.
    if "HOUR" not in df.columns:
        for col_hora in ["Hour", "hour", "Hora", "hora", "HR", "hr"]:
            if col_hora in df.columns:
                df["HOUR"] = df[col_hora]
                break

    colunas = [
        "DATA", "HOUR", "CampaignId", "UF", "UF_DDD", "Faixa_Atraso", "Tabulacao", "Classificado",
        "MAILING", "Discado", "Contato", "Cpc", "NDOC", "Acordo", "HangUp", "Tempo", "Custo_Telecom"
    ]

    for col in colunas:
        if col not in df.columns:
            if col in ["Faixa_Atraso", "Tabulacao", "Classificado", "UF"]:
                df[col] = ""
            else:
                df[col] = 0

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df.dropna(subset=["DATA"]).copy()

    # A nova base da Sky já vem sumarizada. Mantemos o padrão antigo de nomes para não quebrar o HTML.
    for col in ["HOUR", "CampaignId", "UF_DDD", "MAILING", "Discado", "Contato", "Cpc", "NDOC", "Acordo", "HangUp", "Tempo", "Custo_Telecom"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Quando Tempo vier zerado mas existir TMA_GERAL, estima Tempo = TMA * Contato.
    if "TMA_GERAL" in df.columns:
        tma_seg = df["TMA_GERAL"].apply(_tempo_para_segundos)
        df["Tempo"] = np.where(df["Tempo"].fillna(0) <= 0, tma_seg * df["Contato"], df["Tempo"])

    if "HitRate" in df.columns:
        df["HitRate"] = _valor_percentual_para_decimal(df["HitRate"])
    if "Loc" in df.columns:
        df["Loc"] = _valor_percentual_para_decimal(df["Loc"])
    if "Conversao" in df.columns:
        df["Conversao"] = _valor_percentual_para_decimal(df["Conversao"])
    if "PctHangUp" in df.columns:
        df["PctHangUp"] = _valor_percentual_para_decimal(df["PctHangUp"])

    # Reduz tipos numéricos para deixar filtros/agregações mais leves.
    for col in ["HOUR", "CampaignId", "UF_DDD"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int32")
    for col in ["MAILING", "Discado", "Contato", "Cpc", "NDOC", "Acordo", "HangUp", "Tempo", "Custo_Telecom"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("float64")

    df["Faixa_Atraso"] = df["Faixa_Atraso"].fillna("Sem faixa").astype(str).str.strip()
    df.loc[df["Faixa_Atraso"].eq("") | df["Faixa_Atraso"].str.lower().eq("nan"), "Faixa_Atraso"] = "Sem faixa"

    return df

def carregar_bases_sky():
    if not SKY_ARQUIVO_BASE.exists():
        rows = []
        dias = pd.date_range("2026-05-14", periods=6, freq="D")
        ddds = [11,21,31,41,51,71,81,85,61,62,91,92,65,67,98,86,84,27,68,69,96]
        faixas = ["B.31 a 60 Dias", "C.61 a 90 Dias", "D.91 a 120 Dias", "E.Acima de 120 Dias"]
        for d in dias:
            for hour in range(8, 18):
                for ddd in ddds:
                    rows.append({
                        "DATA": d, "HOUR": hour, "CampaignId": 202, "UF_DDD": ddd,
                        "Faixa_Atraso": faixas[(ddd + hour) % len(faixas)],
                        "MAILING": 1000, "Discado": 100, "Contato": 20, "Cpc": 8, "NDOC": 3, "Acordo": 2,
                        "HangUp": 1, "Tempo": 800, "Custo_Telecom": 3.2
                    })
        demo = preparar_base_sky(pd.DataFrame(rows))
        return {"daily": demo, "hora": demo, "uf": demo, "unique": pd.DataFrame()}

    mtime = SKY_ARQUIVO_BASE.stat().st_mtime
    if SKY_BASE_CACHE.get("bases") is not None and SKY_BASE_CACHE.get("mtime") == mtime:
        return {k: v.copy() for k, v in SKY_BASE_CACHE["bases"].items()}

    xls = pd.ExcelFile(SKY_ARQUIVO_BASE)
    bases = {}
    for chave, sheet_preferida in SKY_SHEETS.items():
        sheet_real = _resolver_sheet(xls, sheet_preferida, SKY_SHEET_ALIASES.get(chave, []))
        if sheet_real is None:
            # A visão Unique é opcional para manter compatibilidade com bases antigas.
            if chave == "unique":
                bases[chave] = pd.DataFrame()
                continue
            raise ValueError(f"Aba obrigatória da SKY não encontrada: {sheet_preferida}")
        raw = pd.read_excel(SKY_ARQUIVO_BASE, sheet_name=sheet_real)
        bases[chave] = preparar_base_unique_sky(raw) if chave == "unique" else preparar_base_sky(raw, origem=chave)

    # Fallbacks para qualquer aba ausente/vazia.
    if bases.get("daily", pd.DataFrame()).empty:
        bases["daily"] = bases.get("hora", pd.DataFrame()).copy()
    if bases.get("hora", pd.DataFrame()).empty:
        bases["hora"] = bases.get("daily", pd.DataFrame()).copy()
    if bases.get("uf", pd.DataFrame()).empty:
        bases["uf"] = bases.get("daily", pd.DataFrame()).copy()

    SKY_BASE_CACHE["mtime"] = mtime
    SKY_BASE_CACHE["bases"] = {k: v.copy() for k, v in bases.items()}
    return {k: v.copy() for k, v in bases.items()}

def carregar_base():
    # Mantido por compatibilidade: a visão Daily/Comparativo usa a sheet Funil_Sumarizado.
    return carregar_bases_sky()["daily"]

def adicionar_uf(df):
    df = df.copy()

    # Se já existir UF em formato SP/RJ/MG, usa direto.
    if "UF" in df.columns:
        uf_txt = df["UF"].fillna("").astype(str).str.strip().str.upper()
        uf_valida = uf_txt.where(uf_txt.isin(TODAS_UFS), "")
        if uf_valida.ne("").any():
            df["UF"] = uf_valida.replace("", "NI")
            return df

        # Na base nova, a coluna UF pode vir com DDD numérico.
        uf_num = pd.to_numeric(df["UF"], errors="coerce")
        if uf_num.notna().any():
            df["UF"] = uf_num.fillna(0).astype(int).map(DDD_UF).fillna("NI")
            return df

    if "UF_DDD" not in df.columns:
        df["UF_DDD"] = 0

    ddd = pd.to_numeric(df["UF_DDD"], errors="coerce").fillna(0).astype(int)
    df["DDD_INT"] = ddd
    df["UF"] = ddd.map(DDD_UF).fillna("NI")
    return df


def aplicar_filtros(df):
    datas = request.args.get("datas", "").strip()
    mes = request.args.get("mes", "").strip()
    faixa = request.args.get("faixa", "")
    campaign_id = request.args.get("campaign_id", "")

    if mes:
        try:
            periodo = pd.Period(mes, freq="M")
            df = df[df["DATA"].dt.to_period("M") == periodo]
        except Exception:
            pass

    if datas:
        partes = [p.strip() for p in re.split(r"[;,]", datas) if p.strip()]
        datas_convertidas = []
        for p in partes:
            dt = pd.to_datetime(p, errors="coerce", dayfirst=True)
            if pd.notna(dt):
                datas_convertidas.append(dt.normalize())

        if datas_convertidas:
            df = df[df["DATA"].dt.normalize().isin(datas_convertidas)]

    if faixa:
        df = df[df["Faixa_Atraso"].astype(str) == faixa]

    if campaign_id and "CampaignId" in df.columns:
        df = df[df["CampaignId"].astype(float).astype(int).astype(str) == str(campaign_id)]

    return df


def cor_intensidade(intensidade):
    if intensidade <= 0:
        return "#64748b"
    if intensidade <= .25:
        return "#38bdf8"
    if intensidade <= .50:
        return "#3b82f6"
    if intensidade <= .75:
        return "#14b8a6"
    return "#22c55e"


def criar_mapa_folium(uf_df):
    mapa = folium.Map(
        location=[-14.2, -51.9],
        zoom_start=4,
        tiles="CartoDB dark_matter",
        control_scale=True,
        prefer_canvas=True
    )

    folium.TileLayer("CartoDB positron", name="Claro").add_to(mapa)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(mapa)

    max_cpc = max(uf_df["Cpc"].max(), 1) if len(uf_df) else 1

    for uf in TODAS_UFS:
        row = uf_df[uf_df["UF"] == uf]
        if row.empty:
            vals = {
                "Discado":0, "Contato":0, "Cpc":0, "Acordo":0,
                "Hit":0, "CpcPerc":0, "Conversao":0, "TMA":0, "Custo_Telecom":0
            }
        else:
            vals = row.iloc[0].to_dict()

        lat, lon = UF_COORDS[uf]
        intensidade = safe_div(vals["Cpc"], max_cpc)
        cor = cor_intensidade(intensidade)
        raio = 7 + (intensidade * 22)

        tooltip = f"""
        <div style="font-family:Segoe UI,Arial;min-width:220px;">
            <div style="font-size:17px;font-weight:800;margin-bottom:6px;color:#0f172a;">{uf}</div>
            <div><b>Discado:</b> {br_number(vals['Discado'])}</div>
            <div><b>Contato:</b> {br_number(vals['Contato'])}</div>
            <div><b>CPC:</b> {br_number(vals['Cpc'])}</div>
            <div><b>Acordo:</b> {br_number(vals['Acordo'])}</div>
            <div><b>HIT%:</b> {br_percent(vals['Hit'])}</div>
            <div><b>CPC%:</b> {br_percent(vals['CpcPerc'])}</div>
            <div><b>Conversão:</b> {br_percent(vals['Conversao'])}</div>
            <div><b>TMA:</b> {seconds_to_hhmmss(vals['TMA'])}</div>
        </div>
        """

        folium.CircleMarker(
            location=[lat, lon],
            radius=raio,
            color="#e0f2fe",
            weight=2,
            fill=True,
            fill_color=cor,
            fill_opacity=0.78,
            tooltip=folium.Tooltip(tooltip, sticky=True),
            popup=folium.Popup(tooltip, max_width=280)
        ).add_to(mapa)

        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style="
                    color:white;
                    font-weight:900;
                    font-size:11px;
                    text-shadow:0 1px 4px rgba(0,0,0,.9);
                    transform:translate(-8px,-7px);
                    font-family:Segoe UI,Arial;">
                    {uf}
                </div>
            """)
        ).add_to(mapa)

    legenda = """
    <div style="
        position: fixed;
        bottom: 28px;
        left: 28px;
        z-index: 9999;
        background: rgba(15,23,42,.88);
        color: white;
        padding: 12px 14px;
        border-radius: 14px;
        border: 1px solid rgba(125,211,252,.35);
        box-shadow: 0 10px 30px rgba(0,0,0,.35);
        font-family: Segoe UI, Arial;
        font-size: 12px;
    ">
      <div style="font-weight:800;margin-bottom:8px;">Intensidade por CPC</div>
      <div><span style="display:inline-block;width:12px;height:12px;background:#64748b;border-radius:50%;margin-right:6px;"></span>Sem CPC</div>
      <div><span style="display:inline-block;width:12px;height:12px;background:#38bdf8;border-radius:50%;margin-right:6px;"></span>Baixo</div>
      <div><span style="display:inline-block;width:12px;height:12px;background:#3b82f6;border-radius:50%;margin-right:6px;"></span>Médio</div>
      <div><span style="display:inline-block;width:12px;height:12px;background:#14b8a6;border-radius:50%;margin-right:6px;"></span>Alto</div>
      <div><span style="display:inline-block;width:12px;height:12px;background:#22c55e;border-radius:50%;margin-right:6px;"></span>Muito alto</div>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(legenda))
    folium.LayerControl(position="topright").add_to(mapa)

    return mapa._repr_html_()



def montar_visao_hora_a_hora(df):
    """Monta a visão hora a hora para o dashboard Sky."""
    if df.empty:
        return {"labels": [], "chart": {}, "tabela": []}

    base = df.copy()

    if "HangUp" not in base.columns:
        base["HangUp"] = np.where(
            base["Tabulacao"].astype(str).str.strip().str.lower() == "hangup",
            base["Discado"],
            0
        )
    else:
        base["HangUp"] = pd.to_numeric(base["HangUp"], errors="coerce").fillna(0)

    if "HOUR" not in base.columns:
        for col_hora in ["Hour", "hour", "Hora", "hora", "HR", "hr"]:
            if col_hora in base.columns:
                base["HOUR"] = base[col_hora]
                break

    if "HOUR" not in base.columns:
        base["HOUR"] = 0

    # Aceita 8, 08, 08:00 ou 08:00:00
    hora_txt = base["HOUR"].astype(str).str.strip()
    hora_extraida = hora_txt.str.extract(r"(\d{1,2})")[0]
    base["HOUR"] = pd.to_numeric(hora_extraida, errors="coerce").fillna(0).astype(int)
    base["HOUR"] = base["HOUR"].clip(lower=0, upper=23)

    hourly_metricas = (
        base.groupby("HOUR", as_index=False)
            .agg({
                "Discado": "sum",
                "Contato": "sum",
                "Cpc": "sum",
                "NDOC": "sum",
                "Acordo": "sum",
                "HangUp": "sum",
                "Tempo": "sum"
            })
            .sort_values("HOUR")
    )

    # Mailing por hora: soma os mailings distintos por DATA + HOUR + Faixa_Atraso.
    mailing_hora = calcular_mailing_distinto_por_faixa(
        base,
        chave_distinta=["DATA", "HOUR"],
        chave_final=["HOUR"]
    )

    hourly = hourly_metricas.merge(mailing_hora, on="HOUR", how="left")
    hourly["MAILING"] = hourly["MAILING"].fillna(0)
    cols_hourly = ["HOUR", "MAILING", "Discado", "Contato", "Cpc", "NDOC", "Acordo", "HangUp", "Tempo"]
    hourly = hourly[cols_hourly].sort_values("HOUR")

    hourly["Spin"] = hourly.apply(lambda x: safe_div(x["Discado"], x["MAILING"]), axis=1)
    hourly["Hit"] = hourly.apply(lambda x: safe_div(x["Contato"], x["Discado"]), axis=1)
    hourly["CpcPerc"] = hourly.apply(lambda x: safe_div(x["Cpc"], x["Contato"]), axis=1)
    hourly["Conversao"] = hourly.apply(lambda x: safe_div(x["Acordo"], x["Cpc"]), axis=1)
    hourly["HangUpPerc"] = hourly.apply(lambda x: safe_div(x["HangUp"], x["Discado"]), axis=1)
    hourly["TMA"] = hourly.apply(lambda x: safe_div(x["Tempo"], x["Contato"]), axis=1)

    labels = [f"{int(h):02d}:00" for h in hourly["HOUR"]]

    chart = {
        "labels": labels,
        "mailing": hourly["MAILING"].round(0).astype(int).tolist(),
        "discado": hourly["Discado"].round(0).astype(int).tolist(),
        "spin": (hourly["Spin"] * 100).round(2).tolist(),
        "contato": hourly["Contato"].round(0).astype(int).tolist(),
        "hit": (hourly["Hit"] * 100).round(2).tolist(),
        "cpc": hourly["Cpc"].round(0).astype(int).tolist(),
        "cpcPerc": (hourly["CpcPerc"] * 100).round(2).tolist(),
        "acordo": hourly["Acordo"].round(0).astype(int).tolist(),
        "conversao": (hourly["Conversao"] * 100).round(2).tolist(),
        "hangup": hourly["HangUp"].round(0).astype(int).tolist(),
        "hangupPerc": (hourly["HangUpPerc"] * 100).round(2).tolist(),
    }

    indicadores = [
        ("Mailing", "MAILING", "number"),
        ("Discado", "Discado", "number"),
        ("Spin", "Spin", "percent"),
        ("Contato", "Contato", "number"),
        ("HIT %", "Hit", "percent"),
        ("CPC", "Cpc", "number"),
        ("NDOC", "NDOC", "number"),
        ("CPC %", "CpcPerc", "percent"),
        ("Acordo", "Acordo", "number"),
        ("Conversão %", "Conversao", "percent"),
        ("HangUp", "HangUp", "number"),
        ("HangUp %", "HangUpPerc", "percent"),
        ("TMA", "TMA", "time"),
    ]

    tabela = []
    for label, coluna, tipo in indicadores:
        linha = {"indicador": label, "valores": []}
        for _, row in hourly.iterrows():
            value = row[coluna]
            if tipo == "percent":
                linha["valores"].append(br_percent(value))
            elif tipo == "time":
                linha["valores"].append(seconds_to_hhmmss(value))
            else:
                linha["valores"].append(br_number(value))
        tabela.append(linha)

    return {"labels": labels, "chart": chart, "tabela": tabela}




# ===== VALORES FIXOS PARA CAMPANHA A - TOTAL DO PERÍODO =====
# Esses valores ficam chumbados somente na Campanha A.
# São valores totais, sem média dia.
FUNIL_FIXO_REFERENCIA = {
    "churn": {
        "label": "Churn Fixo",
        "values": {
            "MAILING": 41370,
            "Discado": 3214157,
            "Contato": 98590,
            "Cpc": 20091,
            "Acordo": 5905,
        }
    },
    "pre_churn": {
        "label": "Pré Churn Fixo",
        "values": {
            "MAILING": 23113,
            "Discado": 828029,
            "Contato": 42392,
            "Cpc": 12001,
            "Acordo": 3956,
        }
    },
    "churn_pre_churn": {
        "label": "Churn + Pré Churn Fixo",
        "values": {
            "MAILING": 64483,
            "Discado": 4042186,
            "Contato": 140982,
            "Cpc": 32092,
            "Acordo": 9861,
        }
    }
}

FUNIL_B_SEGMENTOS_202 = {
    "202_pre_churn": {
        "label": "Campanha 202 · Pré Churn até 90 dias",
        "campaign_id": 202,
        "segmento": "pre_churn"
    },
    "202_churn": {
        "label": "Campanha 202 · Churn acima de 90 dias",
        "campaign_id": 202,
        "segmento": "churn"
    }
}


def classificar_faixa_funil(valor):
    """Classifica a faixa de atraso para o funil comparativo.

    Regra aplicada:
    - até 90 dias => Pré Churn
    - acima de 90 dias => Churn
    """
    texto = str(valor or "").strip().lower()
    if not texto:
        return ""

    # Casos explícitos do arquivo, como "E.Acima de 120 Dias".
    if "acima" in texto or ">" in texto:
        return "churn"

    import re
    nums = [int(n) for n in re.findall(r"\d+", texto)]
    if not nums:
        return ""

    maior_dia = max(nums)
    return "pre_churn" if maior_dia <= 90 else "churn"

# ===== FUNIL COMPARATIVO SKY A x B =====

def dias_uteis_seg_a_sab_do_mes(data_ref):
    """Conta os dias trabalhados do mês considerando segunda a sábado."""
    import calendar
    try:
        data_ref = pd.to_datetime(data_ref)
        ano = int(data_ref.year)
        mes = int(data_ref.month)
    except Exception:
        hoje = pd.Timestamp.today()
        ano = int(hoje.year)
        mes = int(hoje.month)

    ultimo_dia = calendar.monthrange(ano, mes)[1]
    dias = pd.date_range(f"{ano}-{mes:02d}-01", f"{ano}-{mes:02d}-{ultimo_dia:02d}", freq="D")
    return int(sum(1 for d in dias if d.weekday() <= 5))


def build_funil_options_a():
    """Opções fixas da Campanha A.

    Regra solicitada:
    - Campanha A deve ter apenas Churn, Pré Churn e Churn + Pré Churn.
    - Esses valores são totais fixos, sem média.
    """
    return [
        {"key": "fixo:churn", "label": "Churn Fixo", "tipo": "fixo", "fixo": "churn"},
        {"key": "fixo:pre_churn", "label": "Pré Churn Fixo", "tipo": "fixo", "fixo": "pre_churn"},
        {"key": "fixo:churn_pre_churn", "label": "Churn + Pré Churn Fixo", "tipo": "fixo", "fixo": "churn_pre_churn"},
    ]


def build_funil_options_b(df):
    """Opções da Campanha B correlacionadas às campanhas existentes na base.

    Campanha B fica apenas com opções da base:
    - Campanha N · Total selecionado
    - Campanha N · Pré Churn até 90 dias
    - Campanha N · Churn acima de 90 dias
    """
    options = []

    if df is None or df.empty or "CampaignId" not in df.columns:
        return options

    base = df.copy()
    base["CampaignId"] = pd.to_numeric(base["CampaignId"], errors="coerce").fillna(0).astype(int)
    campaigns = sorted([int(c) for c in base["CampaignId"].dropna().unique().tolist() if int(c) != 0])

    for cid in campaigns:
        options.append({
            "key": f"camp:{cid}:total",
            "label": f"Campanha {cid} · Total selecionado",
            "tipo": "campanha",
            "campaign_id": cid,
            "segmento": "total"
        })
        options.append({
            "key": f"camp:{cid}:pre_churn",
            "label": f"Campanha {cid} · Pré Churn até 90 dias",
            "tipo": "campanha",
            "campaign_id": cid,
            "segmento": "pre_churn"
        })
        options.append({
            "key": f"camp:{cid}:churn",
            "label": f"Campanha {cid} · Churn acima de 90 dias",
            "tipo": "campanha",
            "campaign_id": cid,
            "segmento": "churn"
        })

    return options

def get_funil_option(options, key, default_key):
    mapa = {o["key"]: o for o in options}
    if key in mapa:
        return mapa[key]
    if default_key in mapa:
        return mapa[default_key]
    return options[0] if options else {"key": "fixo:churn", "label": "Churn Fixo", "tipo": "fixo", "fixo": "churn"}


# ===== FUNIL COMPARATIVO SKY A x B + PROJEÇÃO =====
def montar_funil_comparativo_sky(df):
    """Monta o comparativo do funil.

    Campanha A usa somente valores fixos totais.
    Campanha B usa campanhas da base, total ou segmentadas por faixa de atraso:
      até 90 dias => Pré Churn; acima de 90 dias => Churn.

    Campanha B segue como somatória dos dias selecionados quando for campanha da base.
    Projeção = Campanha B / dias trabalhados selecionados * dias trabalhados do mês (seg a sáb).
    """
    etapas_def = [
        ("Mailing", "MAILING", "users"),
        ("Discado", "Discado", "phone"),
        ("Atendidas", "Contato", "headset"),
        ("CPC", "Cpc", "mouse-pointer-click"),
        ("Acordo", "Acordo", "handshake"),
    ]

    options_a = build_funil_options_a()
    options_b = build_funil_options_b(df)

    default_a = "fixo:churn"
    default_b = "camp:202:churn"
    if default_b not in {o["key"] for o in options_b}:
        default_b = options_b[0]["key"] if options_b else "camp:0:total"

    selected_a_key = request.args.get("funil_a", default_a).strip()
    selected_b_key = request.args.get("funil_b", default_b).strip()
    funil_visao = (request.args.getlist("funil_visao")[-1] if request.args.getlist("funil_visao") else "mes").strip().lower()
    if funil_visao not in ["mes", "dia"]:
        funil_visao = "mes"

    opt_a = get_funil_option(options_a, selected_a_key, default_a)
    opt_b = get_funil_option(options_b, selected_b_key, default_b) if options_b else {"key": "camp:0:total", "label": "Sem campanha disponível", "tipo": "campanha", "campaign_id": 0, "segmento": "total"}

    payload_vazio = {
        "fixos_a": options_a,
        "segmentos_b": options_b,
        "campanha_a": opt_a["key"],
        "campanha_b": opt_b["key"],
        "campanha_a_label": opt_a["label"],
        "campanha_b_label": opt_b["label"],
        "etapas": [],
        "etapas_projecao": [],
        "cards_topo": [],
        "cards_bottom": [],
        "dias_selecionados": 0,
        "dias_mes_trabalhados": 0,
        "mes_projecao": "",
        "funil_visao": funil_visao,
        "funil_visao_label": "Dia" if funil_visao == "dia" else "Mês",
        "tem_dados": False,
        "mensagem": "Sem dados suficientes para comparar as opções selecionadas."
    }

    if df is None or df.empty:
        return payload_vazio

    base = df.copy()
    if "CampaignId" in base.columns:
        base["CampaignId"] = pd.to_numeric(base["CampaignId"], errors="coerce").fillna(0).astype(int)
    else:
        base["CampaignId"] = 0

    def consolidar_opcao(opcao):
        """Retorna valores consolidados e metadados da opção selecionada."""
        valores_zerados = {col: 0 for _, col, _ in etapas_def}
        meta = {"dias_selecionados": 0, "data_ref": None, "tem_base": False, "valores_media_dia": {}, "mailing_dia_distinto": 0}

        if opcao.get("tipo") == "fixo":
            fixo_key = opcao.get("fixo", "churn")
            cfg = FUNIL_FIXO_REFERENCIA.get(fixo_key, FUNIL_FIXO_REFERENCIA["churn"])
            return cfg["values"].copy(), meta

        cid = int(opcao.get("campaign_id", 0) or 0)
        segmento = opcao.get("segmento", "total")
        filtro = base[base["CampaignId"] == cid].copy()

        if filtro.empty:
            return valores_zerados, meta

        if segmento in ["pre_churn", "churn"]:
            if "Faixa_Atraso" in filtro.columns:
                filtro["SegmentoFunil"] = filtro["Faixa_Atraso"].apply(classificar_faixa_funil)
                filtro = filtro[filtro["SegmentoFunil"] == segmento]
            else:
                filtro = filtro.iloc[0:0]

        if filtro.empty:
            return valores_zerados, meta

        daily_metricas = (
            filtro.groupby(["DATA"], as_index=False)
                .agg({
                    "Discado": "sum",
                    "Contato": "sum",
                    "Cpc": "sum",
                    "Acordo": "sum",
                })
        )

        # Mailing do comparativo:
        # soma distinta das faixas por dia, sem usar máximo geral.
        mailing_daily = calcular_mailing_distinto_por_faixa(
            filtro,
            chave_distinta=["DATA"],
            chave_final=["DATA"]
        )

        daily = daily_metricas.merge(mailing_daily, on="DATA", how="left")
        daily["MAILING"] = daily["MAILING"].fillna(0)
        daily = daily.sort_values("DATA")

        valores = valores_zerados.copy()
        for _, col, _ in etapas_def:
            valores[col] = float(daily[col].sum()) if col in daily.columns and len(daily) else 0

        meta["dias_selecionados"] = int(daily["DATA"].dt.normalize().nunique()) if len(daily) else 0
        meta["data_ref"] = daily["DATA"].max() if len(daily) else None
        meta["tem_base"] = True
        if meta["dias_selecionados"]:
            meta["valores_media_dia"] = {k: (v / meta["dias_selecionados"]) for k, v in valores.items()}
            # Regra visão Dia:
            # usa a soma distinta das faixas do dia mais recente selecionado.
            if "MAILING" in daily.columns and len(daily):
                meta["mailing_dia_distinto"] = float(daily.sort_values("DATA").iloc[-1]["MAILING"])
        return valores, meta

    valores_a, meta_a = consolidar_opcao(opt_a)
    valores_b, meta_b = consolidar_opcao(opt_b)

    dias_selecionados = int(meta_b.get("dias_selecionados") or 0)
    data_ref = meta_b.get("data_ref") or meta_a.get("data_ref") or (base["DATA"].max() if "DATA" in base.columns and len(base) else pd.Timestamp.today())
    dias_mes_trabalhados = dias_uteis_seg_a_sab_do_mes(data_ref)
    mes_projecao = pd.to_datetime(data_ref).strftime("%m/%Y") if data_ref is not None else ""

    # Visão do comparativo:
    # Mês mantém a leitura atual.
    # Dia transforma A fixo em média dia do mês e B em média dos dias selecionados.
    valores_a_view = valores_a.copy()
    valores_b_view = valores_b.copy()

    if funil_visao == "dia":
        divisor_a = dias_mes_trabalhados or 1
        valores_a_view = {k: (float(v) / divisor_a) for k, v in valores_a.items()}
        # Ajuste solicitado: na visão Dia, o Mailing fixo da Campanha A não deve virar média.
        valores_a_view["MAILING"] = float(valores_a.get("MAILING", 0))

        if meta_b.get("tem_base") and dias_selecionados:
            # Demais etapas = média dos dias selecionados.
            valores_b_view = {k: (float(v) / dias_selecionados) for k, v in valores_b.items()}
            # Mailing = soma distinta das faixas do dia mais recente selecionado.
            valores_b_view["MAILING"] = float(meta_b.get("mailing_dia_distinto") or valores_b_view.get("MAILING", 0))
    else:
        # Mês mantém a regra vigente: A fixo total e B realizado,
        # com Mailing da B em média dia.
        if meta_b.get("tem_base") and dias_selecionados:
            valores_b_view["MAILING"] = float(valores_b.get("MAILING", 0)) / float(dias_selecionados or 1)

    valores_projecao = {col: 0 for _, col, _ in etapas_def}
    for _, col, _ in etapas_def:
        if meta_b.get("tem_base") and dias_selecionados:
            media_dia = valores_b[col] / dias_selecionados
            # Regra final solicitada:
            # - Mailing na projeção mostra somente a média dia da Campanha B.
            # - Demais etapas seguem com projeção linear do mês.
            if col == "MAILING":
                valores_projecao[col] = media_dia
            else:
                valores_projecao[col] = media_dia * dias_mes_trabalhados
        else:
            # Se a Campanha B for fixa, mantém o valor como referência para não quebrar o layout.
            valores_projecao[col] = valores_b[col]

    def pct(num, den):
        return safe_div(num, den)

    def variacao(a, b):
        return safe_div(b, a) - 1 if a else 0

    def montar_etapas(valores_b_local, modo="realizado"):
        etapas = []
        for idx, (label, col, icon) in enumerate(etapas_def):
            a = float(valores_a_view.get(col, 0))
            b = float(valores_b_local.get(col, 0))

            if idx == 0:
                conv_a = 1
                conv_b = 1
            else:
                col_prev = etapas_def[idx - 1][1]
                conv_a = pct(a, float(valores_a_view.get(col_prev, 0)))
                conv_b = pct(b, float(valores_b_local.get(col_prev, 0)))

            var = variacao(a, b)
            etapas.append({
                "label": label,
                "icon": icon,
                "a": a,
                "b": b,
                "a_fmt": br_number(a),
                "b_fmt": br_number(b),
                "conv_a": conv_a,
                "conv_b": conv_b,
                # Na linha Discado, a razão Discado/Mailing representa Spin e deve aparecer como decimal.
                "conv_a_fmt": br_number(conv_a, 2) if label == "Discado" else br_percent(conv_a),
                "conv_b_fmt": br_number(conv_b, 2) if label == "Discado" else br_percent(conv_b),
                "variacao": var,
                "variacao_fmt": br_percent(var),
                "classe_var": "pos" if var >= 0 else "neg",
                "modo": modo,
            })
        return etapas

    etapas = montar_etapas(valores_b_view, "realizado")
    etapas_projecao = montar_etapas(valores_projecao, "projecao")

    mailing_a = float(valores_a_view.get("MAILING", 0))
    mailing_b = float(valores_b_view.get("MAILING", 0))
    discado_a = float(valores_a_view.get("Discado", 0))
    discado_b = float(valores_b_view.get("Discado", 0))
    atendidas_a = float(valores_a_view.get("Contato", 0))
    atendidas_b = float(valores_b_view.get("Contato", 0))
    cpc_a = float(valores_a_view.get("Cpc", 0))
    cpc_b = float(valores_b_view.get("Cpc", 0))
    acordo_a = float(valores_a_view.get("Acordo", 0))
    acordo_b = float(valores_b_view.get("Acordo", 0))

    metricas_bottom = [
        # Spin = Discado / Mailing. Deve ser exibido em decimal, não em percentual.
        ("Spin", "rotate-cw", pct(discado_a, mailing_a), pct(discado_b, mailing_b), "decimal"),
        ("Hit Rate", "target", pct(atendidas_a, discado_a), pct(atendidas_b, discado_b), "percent"),
        ("LOC", "pie-chart", pct(cpc_a, atendidas_a), pct(cpc_b, atendidas_b), "percent"),
        ("Conversão", "chart-no-axes-combined", pct(acordo_a, cpc_a), pct(acordo_b, cpc_b), "percent"),
    ]

    cards_bottom = []
    for label, icon, a, b, formato in metricas_bottom:
        var = variacao(a, b)
        cards_bottom.append({
            "label": label,
            "icon": icon,
            "a_fmt": br_number(a, 2) if formato == "decimal" else br_percent(a),
            "b_fmt": br_number(b, 2) if formato == "decimal" else br_percent(b),
            "variacao": var,
            "variacao_fmt": br_percent(var),
            "classe_var": "pos" if var >= 0 else "neg",
        })

    top_labels = {"Mailing", "Discado", "CPC", "Acordo"}
    cards_topo = [e for e in etapas if e["label"] in top_labels]

    max_a = max([e["a"] for e in etapas] + [1])
    max_b = max([e["b"] for e in etapas] + [1])
    max_proj = max([e["b"] for e in etapas_projecao] + [1])
    for e in etapas:
        e["width_a"] = 40 + (safe_div(e["a"], max_a) * 60)
        e["width_b"] = 40 + (safe_div(e["b"], max_b) * 60)
    for e in etapas_projecao:
        e["width_b"] = 40 + (safe_div(e["b"], max_proj) * 60)

    return {
        "fixos_a": options_a,
        "segmentos_b": options_b,
        "campanha_a": opt_a["key"],
        "campanha_b": opt_b["key"],
        "campanha_a_label": opt_a["label"],
        "campanha_b_label": opt_b["label"],
        "etapas": etapas,
        "etapas_projecao": etapas_projecao,
        "cards_topo": cards_topo,
        "cards_bottom": cards_bottom,
        "dias_selecionados": dias_selecionados,
        "dias_mes_trabalhados": dias_mes_trabalhados,
        "mes_projecao": mes_projecao,
        "funil_visao": funil_visao,
        "funil_visao_label": "Dia" if funil_visao == "dia" else "Mês",
        "tem_dados": True,
        "mensagem": ""
    }

def montar_faixa_atraso(df):
    """Monta uma visão executiva do funil por faixa de atraso para a Sky."""
    if df is None or df.empty or "Faixa_Atraso" not in df.columns:
        return {"cards": [], "tabela": []}

    base = df.copy()
    base["Faixa_Atraso"] = base["Faixa_Atraso"].fillna("Não informado").astype(str).str.strip()
    base.loc[base["Faixa_Atraso"].eq("") | base["Faixa_Atraso"].str.lower().eq("nan"), "Faixa_Atraso"] = "Não informado"

    if "HangUp" not in base.columns:
        base["HangUp"] = np.where(
            base.get("Tabulacao", "").astype(str).str.strip().str.lower() == "hangup",
            base.get("Discado", 0),
            0
        )

    for col in ["MAILING", "Discado", "Contato", "Cpc", "Acordo", "HangUp", "Tempo"]:
        if col not in base.columns:
            base[col] = 0
        base[col] = pd.to_numeric(base[col], errors="coerce").fillna(0)

    faixa_metricas = (
        base.groupby("Faixa_Atraso", as_index=False)
            .agg({
                "Discado": "sum",
                "Contato": "sum",
                "Cpc": "sum",
                "Acordo": "sum",
                "HangUp": "sum",
                "Tempo": "sum",
            })
    )

    # Mailing por faixa: soma o mailing distinto por DATA + Faixa_Atraso.
    mailing_faixa = calcular_mailing_distinto_por_faixa(
        base,
        chave_distinta=["DATA", "Faixa_Atraso"],
        chave_final=["Faixa_Atraso"]
    )

    faixa_df = faixa_metricas.merge(mailing_faixa, on="Faixa_Atraso", how="left")
    faixa_df["MAILING"] = faixa_df["MAILING"].fillna(0)

    def _ordem_faixa(valor):
        txt = str(valor).lower()
        numeros = re.findall(r"\d+", txt)
        if numeros:
            return int(numeros[0])
        if "acima" in txt or ">" in txt:
            return 9999
        return 99999

    faixa_df["Hit"] = faixa_df.apply(lambda x: safe_div(x["Contato"], x["Discado"]), axis=1)
    faixa_df["CpcPerc"] = faixa_df.apply(lambda x: safe_div(x["Cpc"], x["Contato"]), axis=1)
    faixa_df["Conversao"] = faixa_df.apply(lambda x: safe_div(x["Acordo"], x["Cpc"]), axis=1)
    faixa_df["Spin"] = faixa_df.apply(lambda x: safe_div(x["Discado"], x["MAILING"]), axis=1)
    faixa_df["TMA"] = faixa_df.apply(lambda x: safe_div(x["Tempo"], x["Contato"]), axis=1)
    faixa_df["ordem"] = faixa_df["Faixa_Atraso"].apply(_ordem_faixa)
    faixa_df = faixa_df.sort_values(["ordem", "Faixa_Atraso"]).drop(columns=["ordem"])

    total_discado = float(faixa_df["Discado"].sum())
    total_cpc = float(faixa_df["Cpc"].sum())
    max_cpc = float(faixa_df["Cpc"].max()) if len(faixa_df) else 0
    max_discado = float(faixa_df["Discado"].max()) if len(faixa_df) else 0
    denominador_barra = max(max_cpc, max_discado, 1)

    cards = []
    tabela = []
    for _, r in faixa_df.iterrows():
        largura = 6 + (safe_div(max(float(r["Cpc"]), float(r["Discado"])), denominador_barra) * 94)
        item = {
            "faixa": str(r["Faixa_Atraso"]),
            "mailing": br_number(r["MAILING"]),
            "discado": br_number(r["Discado"]),
            "contato": br_number(r["Contato"]),
            "cpc": br_number(r["Cpc"]),
            "acordo": br_number(r["Acordo"]),
            "hit": br_percent(r["Hit"]),
            "loc": br_percent(r["CpcPerc"]),
            "conversao": br_percent(r["Conversao"]),
            "spin": br_number(r["Spin"], 2),
            "tma": seconds_to_hhmmss(r["TMA"]),
            "share_discado_fmt": br_percent(safe_div(r["Discado"], total_discado)),
            "share_cpc_fmt": br_percent(safe_div(r["Cpc"], total_cpc)),
            "width": round(min(100, max(6, largura)), 2),
        }
        cards.append(item)
        tabela.append({
            "Faixa": item["faixa"],
            "Mailing": item["mailing"],
            "Discado": item["discado"],
            "Contato": item["contato"],
            "CPC": item["cpc"],
            "Acordo": item["acordo"],
            "HIT %": item["hit"],
            "CPC %": item["loc"],
            "Conversão": item["conversao"],
            "Spin": item["spin"],
            "TMA": item["tma"],
        })

    return {"cards": cards, "tabela": tabela}

def consolidar(df):
    # A Sky agora usa 3 sheets sumarizadas:
    # Daily/Comparativo -> Funil_Sumarizado
    # Hora a Hora       -> Funil_Hora
    # Mapa/UF           -> Funil_UF_Dia
    if isinstance(df, dict):
        bases = df
        df = bases.get("daily", pd.DataFrame()).copy()
        df_hora_base = bases.get("hora", df).copy()
        df_uf_base = bases.get("uf", df).copy()
        df_unique_base = bases.get("unique", pd.DataFrame()).copy()
    else:
        df = df.copy()
        df_hora_base = df.copy()
        df_uf_base = df.copy()
        df_unique_base = pd.DataFrame()

    df = adicionar_uf(df)
    df_hora_base = adicionar_uf(df_hora_base)
    df_uf_base = adicionar_uf(df_uf_base)

    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    periodos_mes = sorted(df["DATA"].dropna().dt.to_period("M").unique(), reverse=True) if len(df) else []
    filtros = {
        "min_data": df["DATA"].min().strftime("%Y-%m-%d") if len(df) else "",
        "max_data": df["DATA"].max().strftime("%Y-%m-%d") if len(df) else "",
        "meses": [
            {"value": str(p), "label": f"{meses_pt.get(p.month, p.month)} / {p.year}"}
            for p in periodos_mes
        ],
        "faixas": sorted([f for f in df["Faixa_Atraso"].dropna().astype(str).unique().tolist() if f]),
        "campaigns": sorted([str(int(c)) for c in df["CampaignId"].dropna().unique().tolist() if pd.notna(c) and float(c) != 0]) if "CampaignId" in df.columns else []
    }

    df = aplicar_filtros(df)
    df_hora_filtrado = aplicar_filtros(df_hora_base)
    df_uf_filtrado = aplicar_filtros(df_uf_base)

    # HangUp para os cards do fluxo.
    # Caso a base não tenha a coluna HangUp, calcula pelo volume Discado das linhas tabuladas como HangUp.
    if "HangUp" not in df.columns:
        df["HangUp"] = np.where(
            df["Tabulacao"].astype(str).str.strip().str.lower() == "hangup",
            df["Discado"],
            0
        )
    else:
        df["HangUp"] = pd.to_numeric(df["HangUp"], errors="coerce").fillna(0)

    if df.empty:
        return {
            "cards": [], "capacity": [], "flow": [], "extras": {},
            "datas": [], "tabela": [], "chart": {},
            "insight": "Sem dados para os filtros selecionados.",
            "periodo": "-", "mapa_html": "", "ranking_uf": [], "filtros": filtros, "totais": {}, "faixa_atraso": {"cards": [], "tabela": []}, "hora_a_hora": {"labels": [], "chart": {}, "tabela": []}, "funil_comparativo": montar_funil_comparativo_sky(df), "unique": montar_visao_unique_sky(df_unique_base)
        }

    daily_metricas = (
        df.groupby("DATA", as_index=False)
          .agg({
              "Discado":"sum", "Contato":"sum", "Cpc":"sum", "NDOC":"sum",
              "Acordo":"sum", "HangUp":"sum", "Tempo":"sum", "Custo_Telecom":"sum"
          })
          .sort_values("DATA")
    )

    # Daily: soma os Mailings distintos de cada faixa por dia.
    mailing_daily = calcular_mailing_distinto_por_faixa(
        df,
        chave_distinta=["DATA"],
        chave_final=["DATA"]
    )

    daily = daily_metricas.merge(mailing_daily, on="DATA", how="left")
    daily["MAILING"] = daily["MAILING"].fillna(0)
    daily = daily[["DATA", "MAILING", "Discado", "Contato", "Cpc", "NDOC", "Acordo", "HangUp", "Tempo", "Custo_Telecom"]].sort_values("DATA")

    daily["Spin"] = daily.apply(lambda x: safe_div(x["Discado"], x["MAILING"]), axis=1)
    daily["Hit"] = daily.apply(lambda x: safe_div(x["Contato"], x["Discado"]), axis=1)
    daily["CpcPerc"] = daily.apply(lambda x: safe_div(x["Cpc"], x["Contato"]), axis=1)
    daily["Conversao"] = daily.apply(lambda x: safe_div(x["Acordo"], x["Cpc"]), axis=1)
    daily["TMA"] = daily.apply(lambda x: safe_div(x["Tempo"], x["Contato"]), axis=1)
    daily["CustoPorChamada"] = daily.apply(lambda x: safe_div(x["Custo_Telecom"], x["Discado"]), axis=1)
    daily["CustoPorCpc"] = daily.apply(lambda x: safe_div(x["Custo_Telecom"], x["Cpc"]), axis=1)
    daily["CustoPorAcordo"] = daily.apply(lambda x: safe_div(x["Custo_Telecom"], x["Acordo"]), axis=1)

    total = {
        "MAILING": daily["MAILING"].sum(),
        "Discado": daily["Discado"].sum(),
        "Contato": daily["Contato"].sum(),
        "Cpc": daily["Cpc"].sum(),
        "NDOC": daily["NDOC"].sum(),
        "Acordo": daily["Acordo"].sum(),
        "HangUp": daily["HangUp"].sum(),
        "Tempo": daily["Tempo"].sum(),
        "Custo_Telecom": daily["Custo_Telecom"].sum()
    }
    total["Spin"] = safe_div(total["Discado"], total["MAILING"])
    total["Hit"] = safe_div(total["Contato"], total["Discado"])
    total["CpcPerc"] = safe_div(total["Cpc"], total["Contato"])
    total["Conversao"] = safe_div(total["Acordo"], total["Cpc"])
    total["TMA"] = safe_div(total["Tempo"], total["Contato"])
    total["CustoPorChamada"] = safe_div(total["Custo_Telecom"], total["Discado"])
    total["CustoPorCpc"] = safe_div(total["Custo_Telecom"], total["Cpc"])
    total["CustoPorAcordo"] = safe_div(total["Custo_Telecom"], total["Acordo"])

    cards = [
        {"label": "Mailing", "value": br_number(total["MAILING"]), "icon": "database"},
        {"label": "Discado", "value": br_number(total["Discado"]), "icon": "phone-call"},
        {"label": "Contato", "value": br_number(total["Contato"]), "icon": "headset"},
        {"label": "CPC", "value": br_number(total["Cpc"]), "icon": "target"},
        {"label": "Acordo", "value": br_number(total["Acordo"]), "icon": "handshake"},
        {"label": "Spin", "value": br_number(total["Spin"], 2), "icon": "rotate-cw"},
        {"label": "HIT %", "value": br_percent(total["Hit"]), "icon": "activity"},
        {"label": "CPC %", "value": br_percent(total["CpcPerc"]), "icon": "crosshair"},
        {"label": "Conversão %", "value": br_percent(total["Conversao"]), "icon": "trending-up"},
        {"label": "TMA", "value": seconds_to_hhmmss(total["TMA"]), "icon": "timer"},
    ]

    capacity = []

    flow = [
        {"label": "Mailing", "icon": "🗂️", "value": br_number(total["MAILING"]), "ratio": "Base disponível"},
        {"label": "Discado", "icon": "📞", "value": br_number(total["Discado"]), "ratio": f"Spin {br_number(total['Spin'], 2)}"},
        {"label": "Contato", "icon": "🟢", "value": br_number(total["Contato"]), "ratio": br_percent(total["Hit"])},
        {"label": "CPC", "icon": "✅", "value": br_number(total["Cpc"]), "ratio": br_percent(total["CpcPerc"])},
        {"label": "Acordo", "icon": "💰", "value": br_number(total["Acordo"]), "ratio": br_percent(total["Conversao"])},
        {"label": "HangUp", "icon": "☎️", "value": br_number(total["HangUp"]), "ratio": br_percent(safe_div(total["HangUp"], total["Discado"]))},
    ]

    extras = {
        "HIT %": br_percent(total["Hit"]),
        "CPC %": br_percent(total["CpcPerc"]),
        "Conversão": br_percent(total["Conversao"]),
        "Contato / Mailing": br_percent(safe_div(total["Contato"], total["MAILING"])),
        "CPC / Discado": br_percent(safe_div(total["Cpc"], total["Discado"])),
        "Acordo / Discado": br_percent(safe_div(total["Acordo"], total["Discado"])),
        "TMA": seconds_to_hhmmss(total["TMA"]),
    }

    # Mantido para compatibilidade, mas o HTML usa o funil Plotly.
    funnel = [
        {"label":"Mailing", "value":total["MAILING"], "percent":1},
        {"label":"Discado", "value":total["Discado"], "percent":safe_div(total["Discado"], total["MAILING"])},
        {"label":"Contato", "value":total["Contato"], "percent":safe_div(total["Contato"], total["Discado"])},
        {"label":"CPC", "value":total["Cpc"], "percent":safe_div(total["Cpc"], total["Contato"])},
        {"label":"Acordo", "value":total["Acordo"], "percent":safe_div(total["Acordo"], total["Cpc"])},
    ]
    for item in funnel:
        item["value_fmt"] = br_number(item["value"])
        item["percent_fmt"] = br_percent(item["percent"])

    indicadores = [
        ("Mailing","MAILING","number"),
        ("Discado","Discado","number"),
        ("Contato","Contato","number"),
        ("CPC","Cpc","number"),
        ("NDOC","NDOC","number"),
        ("Acordo","Acordo","number"),
        ("HangUp","HangUp","number"),
        ("Spin","Spin","decimal"),
        ("HIT %","Hit","percent"),
        ("CPC %","CpcPerc","percent"),
        ("Conversão %","Conversao","percent"),
        ("TMA","TMA","time"),
    ]

    datas = [d.strftime("%d/%m") for d in daily["DATA"]]
    tabela = []
    for _, row in daily.sort_values("DATA", ascending=False).iterrows():
        tabela.append({
            "data": row["DATA"].strftime("%d/%m/%Y"),
            "mailing": br_number(row["MAILING"]),
            "discado": br_number(row["Discado"]),
            "contato": br_number(row["Contato"]),
            "cpc": br_number(row["Cpc"]),
            "ndoc": br_number(row["NDOC"]),
            "acordo": br_number(row["Acordo"]),
            "hangup": br_number(row["HangUp"]),
            "spin": br_number(row["Spin"], 2),
            "hit": br_percent(row["Hit"]),
            "cpc_perc": br_percent(row["CpcPerc"]),
            "conversao": br_percent(row["Conversao"]),
            "tma": seconds_to_hhmmss(row["TMA"]),
        })

    chart = {
        "labels": datas,
        "cpc": daily["Cpc"].round(0).astype(int).tolist(),
        "localizacao": (daily["CpcPerc"] * 100).round(2).tolist(),
        "acordo": daily["Acordo"].round(0).astype(int).tolist(),
        "hangup": daily["HangUp"].round(0).astype(int).tolist(),
        "conversao": (daily["Conversao"] * 100).round(2).tolist(),
        "discado": daily["Discado"].round(0).astype(int).tolist(),
        "hit": (daily["Hit"] * 100).round(2).tolist(),
        "custo": daily["Custo_Telecom"].round(2).tolist(),
        "custoPorAcordo": daily["CustoPorAcordo"].round(2).tolist(),
    }

    base_uf_visao = df_uf_filtrado.copy()
    if base_uf_visao.empty:
        base_uf_visao = df.copy()

    uf_metricas = (
        base_uf_visao.groupby("UF", as_index=False)
          .agg({
              "Discado":"sum", "Contato":"sum", "Cpc":"sum", "NDOC":"sum",
              "Acordo":"sum", "HangUp":"sum", "Tempo":"sum", "Custo_Telecom":"sum"
          })
    )

    # Brasil/UF: soma Mailing distinto por DATA + UF + Faixa_Atraso.
    mailing_uf = calcular_mailing_distinto_por_faixa(
        base_uf_visao,
        chave_distinta=["DATA", "UF"],
        chave_final=["UF"]
    )

    uf_df = uf_metricas.merge(mailing_uf, on="UF", how="left")
    uf_df["MAILING"] = uf_df["MAILING"].fillna(0)
    uf_df = uf_df[uf_df["UF"].isin(TODAS_UFS)].copy()
    uf_df["Hit"] = uf_df.apply(lambda x: safe_div(x["Contato"], x["Discado"]), axis=1)
    uf_df["CpcPerc"] = uf_df.apply(lambda x: safe_div(x["Cpc"], x["Contato"]), axis=1)
    uf_df["Conversao"] = uf_df.apply(lambda x: safe_div(x["Acordo"], x["Cpc"]), axis=1)
    uf_df["TMA"] = uf_df.apply(lambda x: safe_div(x["Tempo"], x["Contato"]), axis=1)

    ranking_uf = []
    for _, r in uf_df.sort_values(["Cpc", "Acordo"], ascending=False).head(10).iterrows():
        ranking_uf.append({
            "uf": r["UF"],
            "discado": br_number(r["Discado"]),
            "contato": br_number(r["Contato"]),
            "cpc": br_number(r["Cpc"]),
            "acordo": br_number(r["Acordo"]),
            "hit": br_percent(r["Hit"]),
            "cpcPerc": br_percent(r["CpcPerc"]),
            "conversao": br_percent(r["Conversao"]),
            "tma": seconds_to_hhmmss(r["TMA"]),
        })

    melhor_uf = ranking_uf[0]["uf"] if ranking_uf else "-"
    insight = (
        f"No período selecionado, a operação realizou {br_number(total['Discado'])} discagens, "
        f"gerou {br_number(total['Contato'])} contatos, {br_number(total['Cpc'])} CPCs e "
        f"{br_number(total['Acordo'])} acordos. A localização ficou em {br_percent(total['CpcPerc'])} "
        f"e a conversão em {br_percent(total['Conversao'])}. No mapa regional, o maior volume de CPC está em {melhor_uf}."
    )

    active_tab = request.args.get("tab", "daily")

    # Performance: Folium é a parte mais pesada. Só monta o mapa quando a aba Mapa está ativa.
    if active_tab == "mapa":
        mapa_html = criar_mapa_folium(uf_df)
    else:
        mapa_html = """
        <div class='mapa-placeholder'>
          <div>
            <strong>Mapa carregado sob demanda</strong>
            <span>Clique na aba Mapa Brasil para carregar a visão regional.</span>
          </div>
        </div>
        """

    # Hora a hora também monta vários gráficos/tabelas. Carrega apenas quando a aba estiver ativa.
    hora_a_hora = montar_visao_hora_a_hora(df_hora_filtrado) if active_tab == "hora" else {"labels": [], "chart": {}, "tabela": []}

    # Visão Unique, alimentada pela aba dedicada do Excel e filtrada pelas datas do Daily.
    unique = montar_visao_unique_sky(df_unique_base)

    # Funil por faixa de atraso usado na visão Daily.
    faixa_atraso = montar_faixa_atraso(df)

    # Funil comparativo é leve após otimização e mantém os filtros prontos.
    funil_comparativo = montar_funil_comparativo_sky(df)

    return {
        "cards": cards,
        "capacity": capacity,
        "flow": flow,
        "extras": extras,
        "datas": datas,
        "tabela": tabela,
        "chart": chart,
        "hora_a_hora": hora_a_hora,
        "funil_comparativo": funil_comparativo,
        "faixa_atraso": faixa_atraso,
        "unique": unique,
        "insight": insight,
        "periodo": f"{df['DATA'].min().strftime('%d/%m/%Y')} até {df['DATA'].max().strftime('%d/%m/%Y')}",
        "mapa_html": mapa_html,
        "ranking_uf": ranking_uf,
        "filtros": filtros,
        "totais": {
            "discado": br_number(total["Discado"]),
            "contato": br_number(total["Contato"]),
            "cpc": br_number(total["Cpc"]),
            "acordo": br_number(total["Acordo"]),
            "hit": br_percent(total["Hit"]),
            "cpcPerc": br_percent(total["CpcPerc"]),
            "conversao": br_percent(total["Conversao"]),
            "tma": seconds_to_hhmmss(total["TMA"]),
            "custo": br_money(total["Custo_Telecom"]),
        }
    }


@app.route('/cliente/sky-negocie-online/painel')
def sky_negocie_online_index() -> str:
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if not usuario_pode_acessar_cliente(session.get('usuario'), 'sky-negocie-online'):
        return acesso_negado()
    usuario = session.get('usuario')
    permitidas = visoes_permitidas(usuario, 'sky-negocie-online')
    active_tab = request.args.get('tab', 'daily')
    if active_tab not in permitidas:
        fallback = next((v for v in ['daily', 'hora', 'mapa', 'funil'] if v in permitidas), None)
        if fallback is None:
            return acesso_negado()
        args = request.args.to_dict(flat=False)
        args['tab'] = [fallback]
        flat_args = {k: (v if len(v) > 1 else v[0]) for k, v in args.items()}
        return redirect(url_for('sky_negocie_online_index', **flat_args))
    bases = carregar_bases_sky()
    dashboard = filtrar_payload_sky_por_permissao(consolidar(bases), usuario)
    return render_template('sky_negocie_online.html', dashboard=dashboard, usuario=usuario, visoes_permitidas=permitidas, is_admin=usuario_e_admin(usuario))


@app.route('/cliente/sky-negocie-online/painel/api')
def sky_negocie_online_api():
    if 'usuario' not in session:
        return jsonify({"error": "unauthorized"}), 401
    if not usuario_pode_acessar_cliente(session.get('usuario'), 'sky-negocie-online'):
        return jsonify({"error": "forbidden"}), 403
    usuario = session.get('usuario')
    active_tab = request.args.get('tab')
    if active_tab and active_tab in {'daily', 'hora', 'mapa', 'funil'} and not usuario_pode_acessar_visao(usuario, 'sky-negocie-online', active_tab):
        return jsonify({"error": "forbidden_view"}), 403
    bases = carregar_bases_sky()
    return jsonify(filtrar_payload_sky_por_permissao(consolidar(bases), usuario))



# ===== LINK | Locator + ATH Dashboard integrado =====
# Base independente: data/base_link.xlsx
LINK_ARQUIVO_BASE = Path(os.getenv("LINK_EXCEL_PATH", BASE_DIR / "data" / "base_link.xlsx"))
LINK_BASE_CACHE = {"mtime": None, "df": None}

LINK_COLUMNS = [
    "Data", "Hora", "CampaignId", "WayInboundCampaignId", "NomeCampanha", "Mailing", "AD", "ATH",
    "Tentativas", "Atendidas", "Transferencia", "Perda", "Atend_ATH", "Sucesso_Negocio",
    "TMA_LOCATOR", "TMA_ATH", "HitRate", "SucessoInteracao", "%Perda", "Abandono", "%Abandono",
    "SLA", "Custo"
]

# Segunda aba opcional dentro de cada base Locator.
# Nome recomendado: Funil_2. Aceita também Comparativo ou a segunda sheet do arquivo.
FUNIL2_COLUMNS = [
    "Data", "Hora", "NomeCampanha", "Mailing", "Logados", "AD", "ATH", "Tentativas", "Atendidas", "Cpc",
    "Transferencia", "Perda", "Atend_ATH", "Sucesso_Negocio", "TMA_LOCATOR", "TMA_ATH", "HitRate", "SucessoInteracao",
    "Loc", "Conver", "%Perda", "Abandono", "%Abandono", "Custo"
]
FUNIL2_SHEET_NAMES = ["Funil_2", "Comparativo", "Sheet2"]
FUNIL3_COLUMNS = [
    "Data", "NomeCampanha", "Mailing", "AD", "ATH", "Tentativas", "Atendidas", "Transferencia",
    "Perda", "Atend_ATH", "Sucesso_Negocio", "TMA_LOCATOR", "TMA_ATH", "HitRate", "SucessoInteracao",
    "%Perda", "Abandono", "%Abandono", "SLA", "Custo"
]
FUNIL3_SHEET_NAMES = ["Funil_3", "Way", "Sheet3"]
FUNIL2_CACHE = {}
FUNIL3_CACHE = {}


def _link_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def _link_num(valor):
    if pd.isna(valor):
        return 0.0
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return float(valor)
    txt = str(valor).strip()
    if txt in ["", "::", "%", "nan", "NaT", "None"]:
        return 0.0
    txt = txt.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(txt)
    except Exception:
        return 0.0


def _link_pct(valor):
    """Retorna percentual na escala visual 0-100. Ex.: '12,5%' -> 12.5."""
    if pd.isna(valor):
        return np.nan
    if isinstance(valor, (int, float, np.integer, np.floating)):
        num = float(valor)
        # Excel pode entregar percentuais como 0.125 ou 12.5.
        return num * 100 if 0 < abs(num) <= 1 else num
    txt = str(valor).strip()
    if txt in ["", "::", "%", "nan", "NaT", "None"]:
        return np.nan
    tinha_percentual = "%" in txt
    txt = txt.replace("%", "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        num = float(txt)
        if not tinha_percentual and 0 < abs(num) <= 1:
            return num * 100
        return num
    except Exception:
        return np.nan


def _link_segundos(valor):
    if pd.isna(valor):
        return np.nan
    if isinstance(valor, pd.Timedelta):
        return float(valor.total_seconds())
    if isinstance(valor, (int, float, np.integer, np.floating)):
        num = float(valor)
        # Horários do Excel normalmente chegam como fração de dia.
        return num * 86400 if 0 < num < 1 else num
    txt = str(valor).strip()
    if txt in ["", "::", "nan", "NaT", "None"]:
        return np.nan
    partes = txt.split(":")
    try:
        if len(partes) == 3:
            return int(float(partes[0])) * 3600 + int(float(partes[1])) * 60 + float(partes[2].replace(",", "."))
        if len(partes) == 2:
            return int(float(partes[0])) * 60 + float(partes[1].replace(",", "."))
        return float(txt.replace(",", "."))
    except Exception:
        return np.nan


def _link_tempo_fmt(valor):
    try:
        if pd.isna(valor):
            return "00:00"
        total = int(round(float(valor)))
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
    except Exception:
        return "00:00"


def _link_num_fmt(valor, decimais=0):
    try:
        formato = f"{{:,.{decimais}f}}"
        return formato.format(float(valor or 0)).replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0"


def _link_pct_fmt(valor):
    try:
        if pd.isna(valor):
            return "0,00%"
        return _link_num_fmt(valor, 2) + "%"
    except Exception:
        return "0,00%"


def _link_money_fmt(valor):
    return "R$ " + _link_num_fmt(valor, 2)


def preparar_base_link(df):
    df = df.copy()
    aliases = {
        "dt": "Data", "data": "Data", "date": "Data",
        "hour": "Hora", "hora": "Hora",
        "campaignid": "CampaignId", "campaign_id": "CampaignId",
        "wayinboundcampaignid": "WayInboundCampaignId", "way_inbound_campaign_id": "WayInboundCampaignId",
        "nomecampanha": "NomeCampanha", "nome_campanha": "NomeCampanha", "campanha": "NomeCampanha",
        "mailing": "Mailing", "ad": "AD", "ath": "ATH", "tentativas": "Tentativas", "discado": "Tentativas",
        "atendidas": "Atendidas", "contato": "Atendidas", "transferencia": "Transferencia", "transferência": "Transferencia",
        "perda": "Perda", "atend_ath": "Atend_ATH", "atendath": "Atend_ATH", "sucesso_negocio": "Sucesso_Negocio",
        "sucessonegocio": "Sucesso_Negocio", "tma_locator": "TMA_LOCATOR", "tmalocator": "TMA_LOCATOR",
        "tma_ath": "TMA_ATH", "tmaath": "TMA_ATH", "hitrate": "HitRate", "hit_rate": "HitRate",
        "sucessointeracao": "SucessoInteracao", "sucesso_interacao": "SucessoInteracao", "%perda": "%Perda",
        "pctperda": "%Perda", "pct_perda": "%Perda", "abandono": "Abandono", "%abandono": "%Abandono",
        "pctabandono": "%Abandono", "pct_abandono": "%Abandono", "sla": "SLA", "custo": "Custo"
    }
    renomear = {}
    for col in df.columns:
        chave = str(col).strip().lower().replace(" ", "_").replace("-", "_").replace(".", "_")
        renomear[col] = aliases.get(chave, str(col).strip())
    df = df.rename(columns=renomear)

    for col in LINK_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan if col in ["TMA_LOCATOR", "TMA_ATH", "HitRate", "SucessoInteracao", "%Perda", "%Abandono", "SLA"] else 0

    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"]).copy()
    df["Hora"] = pd.to_numeric(df["Hora"], errors="coerce").fillna(0).astype(int)
    for col in ["Mailing", "AD", "ATH", "Tentativas", "Atendidas", "Transferencia", "Perda", "Atend_ATH", "Sucesso_Negocio", "Abandono", "Custo"]:
        df[col] = df[col].apply(_link_num)
    for col in ["HitRate", "SucessoInteracao", "%Perda", "%Abandono", "SLA"]:
        df[col] = df[col].apply(_link_pct)
    for col in ["TMA_LOCATOR", "TMA_ATH"]:
        df[col] = df[col].apply(_link_segundos)
    df["NomeCampanha"] = df["NomeCampanha"].fillna("").astype(str).str.strip()
    df["CampaignId"] = df["CampaignId"].fillna("").astype(str).str.replace(".0", "", regex=False).str.strip()
    df["WayInboundCampaignId"] = df["WayInboundCampaignId"].fillna("").astype(str).str.replace(".0", "", regex=False).str.strip()
    return df


def preparar_base_funil2(df):
    """Normaliza a aba Funil_2 usada como campanha B do comparativo executivo.
    Aceita tanto uma estrutura Humano/AD quanto uma estrutura Way semelhante ao Locator.
    """
    df = df.copy()
    aliases = {
        "dt": "Data", "data": "Data", "date": "Data",
        "hour": "Hora", "hora": "Hora",
        "nomecampanha": "NomeCampanha", "nome_campanha": "NomeCampanha", "campanha": "NomeCampanha",
        "mailing": "Mailing",
        "logados": "Logados", "logado": "Logados",
        "ad": "AD", "ath": "ATH",
        "tentativas": "Tentativas", "discado": "Tentativas",
        "atendidas": "Atendidas", "contato": "Atendidas",
        "cpc": "Cpc", "cpc_": "Cpc",
        "transferencia": "Transferencia", "transferência": "Transferencia",
        "atend_ath": "Atend_ATH", "atendath": "Atend_ATH",
        "sucesso_negocio": "Sucesso_Negocio", "sucessonegocio": "Sucesso_Negocio", "acordo": "Sucesso_Negocio",
        "tma_locator": "TMA_LOCATOR", "tmalocator": "TMA_LOCATOR",
        "tma_ath": "TMA_ATH", "tmaath": "TMA_ATH",
        "hitrate": "HitRate", "hit_rate": "HitRate",
        "sucessointeracao": "SucessoInteracao", "sucesso_interacao": "SucessoInteracao",
        "loc": "Loc", "localizacao": "Loc", "localização": "Loc",
        "conver": "Conver", "conversao": "Conver", "conversão": "Conver",
        "%perda": "%Perda", "pctperda": "%Perda", "pct_perda": "%Perda",
        "abandono": "Abandono", "%abandono": "%Abandono", "pctabandono": "%Abandono", "pct_abandono": "%Abandono",
        "custo": "Custo"
    }
    renomear = {}
    for col in df.columns:
        chave = str(col).strip().lower().replace(" ", "_").replace("-", "_").replace(".", "_")
        renomear[col] = aliases.get(chave, str(col).strip())
    df = df.rename(columns=renomear)
    for col in FUNIL2_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan if col in ["TMA_LOCATOR", "TMA_ATH", "HitRate", "SucessoInteracao", "Loc", "Conver", "%Perda", "%Abandono"] else 0
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"]).copy()
    df["Hora"] = pd.to_numeric(df["Hora"], errors="coerce").fillna(0).astype(int)
    df["NomeCampanha"] = df["NomeCampanha"].fillna("").astype(str).str.strip()
    for col in ["Mailing", "Logados", "AD", "ATH", "Tentativas", "Atendidas", "Cpc", "Transferencia", "Perda", "Atend_ATH", "Sucesso_Negocio", "Abandono", "Custo"]:
        df[col] = df[col].apply(_link_num)
    for col in ["HitRate", "SucessoInteracao", "Loc", "Conver", "%Perda", "%Abandono"]:
        df[col] = df[col].apply(_link_pct)
    for col in ["TMA_LOCATOR", "TMA_ATH"]:
        df[col] = df[col].apply(_link_segundos)
    return df


def preparar_base_funil3(df):
    """Normaliza a aba Funil_3 usada como campanha B no modo Way.
    A coluna Hora não é necessária: o comparativo Way consolida por período.
    """
    df = df.copy()
    aliases = {
        "dt": "Data", "data": "Data", "date": "Data",
        "nomecampanha": "NomeCampanha", "nome_campanha": "NomeCampanha", "campanha": "NomeCampanha",
        "mailing": "Mailing", "ad": "AD", "ath": "ATH",
        "tentativas": "Tentativas", "discado": "Tentativas",
        "atendidas": "Atendidas", "contato": "Atendidas",
        "transferencia": "Transferencia", "transferência": "Transferencia",
        "perda": "Perda", "atend_ath": "Atend_ATH", "atendath": "Atend_ATH",
        "sucesso_negocio": "Sucesso_Negocio", "sucessonegocio": "Sucesso_Negocio", "acordo": "Sucesso_Negocio",
        "tma_locator": "TMA_LOCATOR", "tmalocator": "TMA_LOCATOR",
        "tma_ath": "TMA_ATH", "tmaath": "TMA_ATH",
        "hitrate": "HitRate", "hit_rate": "HitRate",
        "sucessointeracao": "SucessoInteracao", "sucesso_interacao": "SucessoInteracao",
        "%perda": "%Perda", "pctperda": "%Perda", "pct_perda": "%Perda",
        "abandono": "Abandono", "%abandono": "%Abandono", "pctabandono": "%Abandono", "pct_abandono": "%Abandono",
        "sla": "SLA", "custo": "Custo"
    }
    renomear = {}
    for col in df.columns:
        chave = str(col).strip().lower().replace(" ", "_").replace("-", "_").replace(".", "_")
        renomear[col] = aliases.get(chave, str(col).strip())
    df = df.rename(columns=renomear)
    for col in FUNIL3_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan if col in ["TMA_LOCATOR", "TMA_ATH", "HitRate", "SucessoInteracao", "%Perda", "%Abandono", "SLA"] else 0
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"]).copy()
    df["NomeCampanha"] = df["NomeCampanha"].fillna("").astype(str).str.strip()
    for col in ["Mailing", "AD", "ATH", "Tentativas", "Atendidas", "Transferencia", "Perda", "Atend_ATH", "Sucesso_Negocio", "Abandono", "Custo"]:
        df[col] = df[col].apply(_link_num)
    for col in ["HitRate", "SucessoInteracao", "%Perda", "%Abandono", "SLA"]:
        df[col] = df[col].apply(_link_pct)
    for col in ["TMA_LOCATOR", "TMA_ATH"]:
        df[col] = df[col].apply(_link_segundos)
    return df


def carregar_base_funil2_arquivo(arquivo, cache_key):
    """Lê a segunda sheet da base do cliente para alimentar o Funil B."""
    vazio = preparar_base_funil2(pd.DataFrame(columns=FUNIL2_COLUMNS))
    if not arquivo.exists():
        return vazio
    mtime = arquivo.stat().st_mtime
    cache = FUNIL2_CACHE.setdefault(cache_key, {"mtime": None, "df": None})
    if cache.get("df") is not None and cache.get("mtime") == mtime:
        return cache["df"].copy()
    try:
        excel = pd.ExcelFile(arquivo)
        sheet = next((nome for nome in FUNIL2_SHEET_NAMES if nome in excel.sheet_names), None)
        if sheet is None and len(excel.sheet_names) > 1:
            sheet = excel.sheet_names[1]
        if sheet is None:
            return vazio
        df = pd.read_excel(arquivo, sheet_name=sheet)
        df = preparar_base_funil2(df)
        cache["mtime"] = mtime
        cache["df"] = df.copy()
        return df.copy()
    except Exception:
        return vazio


def carregar_base_funil3_arquivo(arquivo, cache_key):
    """Lê a terceira sheet da base do cliente para alimentar o Funil B no modo Way."""
    vazio = preparar_base_funil3(pd.DataFrame(columns=FUNIL3_COLUMNS))
    if not arquivo.exists():
        return vazio
    mtime = arquivo.stat().st_mtime
    cache = FUNIL3_CACHE.setdefault(cache_key, {"mtime": None, "df": None})
    if cache.get("df") is not None and cache.get("mtime") == mtime:
        return cache["df"].copy()
    try:
        excel = pd.ExcelFile(arquivo)
        sheet = next((nome for nome in FUNIL3_SHEET_NAMES if nome in excel.sheet_names), None)
        if sheet is None and len(excel.sheet_names) > 2:
            sheet = excel.sheet_names[2]
        if sheet is None:
            return vazio
        df = pd.read_excel(arquivo, sheet_name=sheet)
        df = preparar_base_funil3(df)
        cache["mtime"] = mtime
        cache["df"] = df.copy()
        return df.copy()
    except Exception:
        return vazio


def agregar_funil2(df):
    """Consolida a campanha humana/AD da aba Funil_2 por data/campanha."""
    if df is None or df.empty:
        return {
            "mailing": 0, "logados": 0, "tentativas": 0, "atendidas": 0, "cpc": 0, "sucesso": 0,
            "tentativas_logado": 0, "hit": 0, "loc": 0, "conver": 0, "tma_ath_sec": 0
        }
    mailing_diario = (
        df.assign(_DATA_DIA=df["Data"].dt.normalize())
          .groupby("_DATA_DIA", dropna=True)["Mailing"]
          .max()
    ) if "Mailing" in df.columns else pd.Series(dtype=float)
    total = {
        "mailing": float(mailing_diario.sum()) if len(mailing_diario) else float(df["Mailing"].max()) if "Mailing" in df.columns else 0,
        "logados": _link_media_valida(df["Logados"]),
        "tentativas": float(df["Tentativas"].sum()),
        "atendidas": float(df["Atendidas"].sum()),
        "cpc": float(df["Cpc"].sum()),
        "sucesso": float(df["Sucesso_Negocio"].sum()),
    }
    total["tentativas_logado"] = total["tentativas"] / total["logados"] if total["logados"] else 0
    total["hit"] = total["atendidas"] / total["tentativas"] * 100 if total["tentativas"] else _link_media_valida(df["HitRate"])
    total["loc"] = total["cpc"] / total["atendidas"] * 100 if total["atendidas"] else _link_media_valida(df["Loc"])
    total["conver"] = total["sucesso"] / total["cpc"] * 100 if total["cpc"] else _link_media_valida(df["Conver"])
    total["tma_ath_sec"] = _link_tma_ponderado(df, "TMA_ATH", "Atendidas")
    return total


def agregar_funil2_way(df):
    """Consolida a campanha Way da aba Funil_2 no mesmo conceito do Locator.
    Workbooks antigos podem não possuir campos opcionais como Perda, Abandono ou Custo.
    Esses campos são preenchidos com zero para manter compatibilidade sem quebrar o painel.
    """
    if df is None:
        return agregar_link_periodo(df)
    df = df.copy()
    defaults_zero = [
        "Mailing", "AD", "ATH", "Tentativas", "Atendidas", "Transferencia", "Perda",
        "Atend_ATH", "Sucesso_Negocio", "Abandono", "Custo"
    ]
    defaults_nan = ["%Perda", "%Abandono", "TMA_LOCATOR", "TMA_ATH"]
    for col in defaults_zero:
        if col not in df.columns:
            df[col] = 0.0
    for col in defaults_nan:
        if col not in df.columns:
            df[col] = np.nan
    return agregar_link_periodo(df)


def _funil2_card(total):
    return {
        **total,
        "mailing_fmt": _link_num_fmt(total.get("mailing", 0)),
        "logados_fmt": _link_num_fmt(total.get("logados", 0), 2),
        "tentativas_fmt": _link_num_fmt(total.get("tentativas", 0)),
        "atendidas_fmt": _link_num_fmt(total.get("atendidas", 0)),
        "cpc_fmt": _link_num_fmt(total.get("cpc", 0)),
        "sucesso_fmt": _link_num_fmt(total.get("sucesso", 0)),
        "tentativas_logado_fmt": _link_num_fmt(total.get("tentativas_logado", 0), 2),
        "hit_fmt": _link_pct_fmt(total.get("hit", 0)),
        "loc_fmt": _link_pct_fmt(total.get("loc", 0)),
        "conver_fmt": _link_pct_fmt(total.get("conver", 0)),
        "tma_ath_fmt": _link_tempo_fmt(total.get("tma_ath_sec", 0)),
    }


def _comparativo_variacao(valor_a, valor_b, tem_b):
    """Calcula a variação percentual solicitada: (A / B) - 1."""
    try:
        a = float(valor_a or 0)
        b = float(valor_b or 0)
    except Exception:
        a, b = 0.0, 0.0
    if not tem_b or b == 0:
        return {"valor": None, "fmt": "--", "classe": "neutro"}
    variacao = (a / b - 1) * 100
    sinal = "+" if variacao > 0 else ""
    classe = "positivo" if variacao > 0 else "negativo" if variacao < 0 else "neutro"
    return {"valor": variacao, "fmt": sinal + _link_num_fmt(variacao, 2) + "%", "classe": classe}


def _comparativo_variacoes(comp_a, comp_b, tem_b, modo_b="humano_ad"):
    if modo_b == "way":
        return {
            "tentativas": _comparativo_variacao(comp_a.get("tentativas"), comp_b.get("tentativas"), tem_b),
            "atendidas": _comparativo_variacao(comp_a.get("atendidas"), comp_b.get("atendidas"), tem_b),
            "transferencia": _comparativo_variacao(comp_a.get("transferencia"), comp_b.get("transferencia"), tem_b),
            "atend_humano": _comparativo_variacao(comp_a.get("atend_ath"), comp_b.get("atend_ath"), tem_b),
            "sucesso": _comparativo_variacao(comp_a.get("sucesso"), comp_b.get("sucesso"), tem_b),
            "conversao": _comparativo_variacao(comp_a.get("conversao"), comp_b.get("conversao"), tem_b),
        }
    return {
        "tentativas": _comparativo_variacao(comp_a.get("tentativas"), comp_b.get("tentativas"), tem_b),
        "atendidas": _comparativo_variacao(comp_a.get("atendidas"), comp_b.get("atendidas"), tem_b),
        "transferencia_cpc": _comparativo_variacao(comp_a.get("transferencia"), comp_b.get("cpc"), tem_b),
        "sucesso": _comparativo_variacao(comp_a.get("sucesso"), comp_b.get("sucesso"), tem_b),
        "interacao_loc": _comparativo_variacao(comp_a.get("interacao"), comp_b.get("loc"), tem_b),
        "conversao": _comparativo_variacao(comp_a.get("conversao"), comp_b.get("conver"), tem_b),
    }


def _comparativo_metric_meta(modo_b="humano_ad"):
    if modo_b == "way":
        return {
            "tentativas": {"titulo": "Tentativas", "a_key": "tentativas_fmt", "b_key": "tentativas_fmt"},
            "atendidas": {"titulo": "Atendidas", "a_key": "atendidas_fmt", "b_key": "atendidas_fmt"},
            "transferencia": {"titulo": "Transferências", "a_key": "transferencia_fmt", "b_key": "transferencia_fmt"},
            "atend_humano": {"titulo": "Atend. humano", "a_key": "atend_ath_fmt", "b_key": "atend_ath_fmt"},
            "sucesso": {"titulo": "Sucesso negócio", "a_key": "sucesso_fmt", "b_key": "sucesso_fmt"},
            "conversao": {"titulo": "% Sucesso de negócio", "a_key": "conversao_fmt", "b_key": "conversao_fmt"},
        }
    return {
        "tentativas": {"titulo": "Tentativas", "a_key": "tentativas_fmt", "b_key": "tentativas_fmt"},
        "atendidas": {"titulo": "Atendidas", "a_key": "atendidas_fmt", "b_key": "atendidas_fmt"},
        "transferencia_cpc": {"titulo": "Transferência / CPC", "a_key": "transferencia_fmt", "b_key": "cpc_fmt"},
        "sucesso": {"titulo": "Sucesso negócio", "a_key": "sucesso_fmt", "b_key": "sucesso_fmt"},
        "interacao_loc": {"titulo": "Sucesso de interação / % Loc", "a_key": "interacao_fmt", "b_key": "loc_fmt"},
        "conversao": {"titulo": "% Sucesso de negócio", "a_key": "conversao_fmt", "b_key": "conver_fmt"},
    }


def _comparativo_exec(comp_a, comp_b, tem_b, variacoes, modo_b="humano_ad"):
    meta = _comparativo_metric_meta(modo_b)
    cards = []
    delta_labels = []
    delta_values = []
    for key, cfg in meta.items():
        var = variacoes.get(key, {"valor": None, "fmt": "--", "classe": "neutro"})
        cards.append({
            "titulo": cfg["titulo"],
            "a_valor": comp_a.get(cfg["a_key"], "--"),
            "b_valor": comp_b.get(cfg["b_key"], "--") if tem_b else "--",
            "variacao": var,
            "leitura": "melhor" if var.get("valor") is not None and var.get("valor") > 0 else "atenção" if var.get("valor") is not None and var.get("valor") < 0 else "sem base",
        })
        delta_labels.append(cfg["titulo"])
        delta_values.append(var.get("valor"))

    valid_vars = [(k, v) for k, v in variacoes.items() if v.get("valor") is not None]
    if valid_vars:
        best_key, best = max(valid_vars, key=lambda kv: kv[1]["valor"])
        worst_key, worst = min(valid_vars, key=lambda kv: kv[1]["valor"])
        best_title = meta[best_key]["titulo"]
        worst_title = meta[worst_key]["titulo"]
        ganho = {"titulo": best_title, "valor_fmt": best["fmt"], "texto": f"Maior vantagem do Locator em {best_title.lower()}."}
        atencao = {"titulo": worst_title, "valor_fmt": worst["fmt"], "texto": f"Ponto de atenção do Locator em {worst_title.lower()}."}
    else:
        ganho = {"titulo": "Aguardando Campanha -1", "valor_fmt": "--", "texto": "Preencha a sheet Funil_2 para habilitar a comparação executiva."}
        atencao = {"titulo": "Sem base comparativa", "valor_fmt": "--", "texto": "A variação percentual aparece quando houver campanha e data válidas nos dois lados."}

    conv = variacoes.get("conversao", {}).get("valor")
    tent = variacoes.get("tentativas", {}).get("valor")
    meio_key = "interacao_loc" if modo_b != "way" else "transferencia"
    meio = variacoes.get(meio_key, {}).get("valor")
    if conv is not None and conv > 0:
        oportunidade = {"titulo": "Escalar eficiência", "valor_fmt": variacoes["conversao"]["fmt"], "texto": "O Locator está convertendo melhor no fundo do funil e pode ganhar escala com monitoramento de hit rate."}
    elif meio is not None and meio > 0:
        oportunidade = {"titulo": "Ajustar topo do funil", "valor_fmt": variacoes[meio_key]["fmt"], "texto": "A jornada do Locator é eficiente no meio do funil; a oportunidade é elevar atendidas sem perder qualidade."}
    elif tent is not None and tent > 0:
        oportunidade = {"titulo": "Manter pressão", "valor_fmt": variacoes["tentativas"]["fmt"], "texto": "O Locator pressiona mais a base; revise discurso e targeting para capturar mais atendidas."}
    else:
        oportunidade = {"titulo": "Revisar estratégia", "valor_fmt": "--", "texto": "Compare outros dias ou campanhas para identificar a melhor alavanca executiva."}

    def _safe_pct(v):
        try:
            return float(v or 0)
        except Exception:
            return 0.0
    def _norm(a, b):
        m = max(float(a or 0), float(b or 0), 1.0)
        return round(float(a or 0) / m * 100, 2), round(float(b or 0) / m * 100, 2)

    alc_a, alc_b = _norm(comp_a.get("tentativas"), comp_b.get("tentativas"))
    suc_a, suc_b = _norm(comp_a.get("sucesso"), comp_b.get("sucesso"))
    hit_a, hit_b = _norm(_safe_pct(comp_a.get("hit")), _safe_pct(comp_b.get("hit")))
    if modo_b == "way":
        meio_a, meio_b = _norm(_safe_pct(comp_a.get("interacao")), _safe_pct(comp_b.get("interacao")))
        conv_a, conv_b = _norm(_safe_pct(comp_a.get("conversao")), _safe_pct(comp_b.get("conversao")))
        radar_labels = ["Alcance", "Hit Rate", "Interação", "Conversão final", "Velocidade ATH", "Volume sucesso"]
    else:
        meio_a, meio_b = _norm(_safe_pct(comp_a.get("interacao")), _safe_pct(comp_b.get("loc")))
        conv_a, conv_b = _norm(_safe_pct(comp_a.get("conversao")), _safe_pct(comp_b.get("conver")))
        radar_labels = ["Alcance", "Hit Rate", "Interação", "Conversão final", "Velocidade ATH", "Volume sucesso"]
    tma_a = float(comp_a.get("tma_ath_sec") or 0)
    tma_b = float(comp_b.get("tma_ath_sec") or 0)
    if tma_a <= 0 and tma_b <= 0:
        vel_a = vel_b = 0.0
    else:
        valid = [x for x in [tma_a, tma_b] if x > 0]
        min_tma = min(valid) if valid else 1.0
        vel_a = round((min_tma / tma_a) * 100, 2) if tma_a > 0 else 0.0
        vel_b = round((min_tma / tma_b) * 100, 2) if tma_b > 0 else 0.0

    radar = {"labels": radar_labels, "a": [alc_a, hit_a, meio_a, conv_a, vel_a, suc_a], "b": [alc_b, hit_b, meio_b, conv_b, vel_b, suc_b]}

    resumo = []
    leituras = {
        "tentativas": "maior pressão de discagem",
        "atendidas": "capacidade de localizar contatos",
        "transferencia_cpc": "avanço no meio do funil",
        "transferencia": "avanço no meio do funil",
        "atend_humano": "recebimento no humano",
        "sucesso": "resultado absoluto do dia",
        "interacao_loc": "eficiência da localização/interação",
        "conversao": "aproveitamento no fundo do funil",
    }
    for key, cfg in meta.items():
        resumo.append({
            "indicador": cfg["titulo"],
            "a_valor": comp_a.get(cfg["a_key"], "--"),
            "b_valor": comp_b.get(cfg["b_key"], "--") if tem_b else "--",
            "variacao": variacoes.get(key, {"fmt": "--", "classe": "neutro"}),
            "leitura": leituras.get(key, "leitura executiva") if tem_b else "aguardando base comparativa",
        })

    matriz = [
        {"titulo": "Alcance", "classe": variacoes.get("tentativas", {}).get("classe", "neutro"), "valor_fmt": variacoes.get("tentativas", {}).get("fmt", "--"), "texto": "Compara a pressão de tentativas entre Locator e Campanha -1."},
        {"titulo": "Localização", "classe": variacoes.get("atendidas", {}).get("classe", "neutro"), "valor_fmt": variacoes.get("atendidas", {}).get("fmt", "--"), "texto": "Mostra quem gera mais atendidas no período comparado."},
        {"titulo": "Interação", "classe": variacoes.get(meio_key, {}).get("classe", "neutro"), "valor_fmt": variacoes.get(meio_key, {}).get("fmt", "--"), "texto": "Lê a eficiência do meio do funil na jornada comparada."},
        {"titulo": "Conversão final", "classe": variacoes.get("conversao", {}).get("classe", "neutro"), "valor_fmt": variacoes.get("conversao", {}).get("fmt", "--"), "texto": "Compara o aproveitamento do fundo do funil em cada jornada."},
    ]

    return {
        "cards": cards,
        "delta": {"labels": delta_labels, "values": delta_values},
        "radar": radar,
        "insights": {"ganho": ganho, "atencao": atencao, "oportunidade": oportunidade},
        "resumo": resumo,
        "matriz": matriz,
    }


def carregar_base_link():
    if not LINK_ARQUIVO_BASE.exists():
        return preparar_base_link(pd.DataFrame(columns=LINK_COLUMNS))
    mtime = LINK_ARQUIVO_BASE.stat().st_mtime
    if LINK_BASE_CACHE.get("df") is not None and LINK_BASE_CACHE.get("mtime") == mtime:
        return LINK_BASE_CACHE["df"].copy()
    df = pd.read_excel(LINK_ARQUIVO_BASE)
    df = preparar_base_link(df)
    LINK_BASE_CACHE["mtime"] = mtime
    LINK_BASE_CACHE["df"] = df.copy()
    return df.copy()


def _link_media_valida(serie):
    serie = pd.to_numeric(serie, errors="coerce").dropna()
    return float(serie.mean()) if len(serie) else 0.0


def _link_tma_ponderado(df, col_tma, col_volume):
    base = df[[col_tma, col_volume]].copy()
    base[col_tma] = pd.to_numeric(base[col_tma], errors="coerce")
    base[col_volume] = pd.to_numeric(base[col_volume], errors="coerce").fillna(0)
    base = base.dropna(subset=[col_tma])
    peso = float(base[col_volume].sum())
    if peso > 0:
        return float((base[col_tma] * base[col_volume]).sum() / peso)
    return _link_media_valida(base[col_tma])


def agregar_link(df):
    if df is None or df.empty:
        return {
            "mailing": 0, "ad": 0, "ath": 0, "tentativas": 0, "atendidas": 0, "transferencia": 0,
            "perda": 0, "atend_ath": 0, "sucesso": 0, "abandono": 0, "custo": 0,
            "spin": 0, "hit": 0, "interacao": 0, "recebimento": 0, "conversao": 0, "pct_perda": 0, "pct_abandono": 0,
            "tma_locator_sec": 0, "tma_ath_sec": 0
        }
    total = {
        "mailing": float(df["Mailing"].max()),
        # AD e ATH representam capacidade por hora. Nos cards e consolidados, usar média horária, não soma.
        "ad": _link_media_valida(df["AD"]), "ath": _link_media_valida(df["ATH"]),
        "tentativas": float(df["Tentativas"].sum()), "atendidas": float(df["Atendidas"].sum()),
        "transferencia": float(df["Transferencia"].sum()), "perda": float(df["Perda"].sum()),
        "atend_ath": float(df["Atend_ATH"].sum()), "sucesso": float(df["Sucesso_Negocio"].sum()),
        "abandono": float(df["Abandono"].sum()), "custo": float(df["Custo"].sum()),
    }
    total["spin"] = total["tentativas"] / total["mailing"] if total["mailing"] else 0
    total["hit"] = total["atendidas"] / total["tentativas"] * 100 if total["tentativas"] else 0
    total["interacao"] = total["transferencia"] / total["atendidas"] * 100 if total["atendidas"] else 0
    total["recebimento"] = total["atend_ath"] / total["transferencia"] * 100 if total["transferencia"] else 0
    total["conversao"] = total["sucesso"] / total["atend_ath"] * 100 if total["atend_ath"] else 0
    # Perda consolidada: usa o percentual já entregue pela base, por média horária, quando disponível.
    total["pct_perda"] = _link_media_valida(df["%Perda"])
    # Regra solicitada: %Abandono já vem calculado na base. O card Daily deve usar média das horas válidas.
    total["pct_abandono"] = _link_media_valida(df["%Abandono"])
    total["tma_locator_sec"] = _link_tma_ponderado(df, "TMA_LOCATOR", "Atendidas")
    total["tma_ath_sec"] = _link_tma_ponderado(df, "TMA_ATH", "Atend_ATH")
    return total


def _link_card_total(total):
    return {
        **total,
        "mailing_fmt": _link_num_fmt(total["mailing"]), "ad_fmt": _link_num_fmt(total["ad"], 2), "ath_fmt": _link_num_fmt(total["ath"], 2),
        "tentativas_fmt": _link_num_fmt(total["tentativas"]), "atendidas_fmt": _link_num_fmt(total["atendidas"]),
        "transferencia_fmt": _link_num_fmt(total["transferencia"]), "atend_ath_fmt": _link_num_fmt(total["atend_ath"]), "sucesso_fmt": _link_num_fmt(total["sucesso"]),
        "abandono_fmt": _link_num_fmt(total["abandono"]), "perda_fmt": _link_num_fmt(total["perda"]),
        "spin_fmt": _link_num_fmt(total["spin"], 2), "hit_fmt": _link_pct_fmt(total["hit"]),
        "interacao_fmt": _link_pct_fmt(total["interacao"]), "recebimento_fmt": _link_pct_fmt(total["recebimento"]),
        "conversao_fmt": _link_pct_fmt(total["conversao"]), "pct_perda_fmt": _link_pct_fmt(total["pct_perda"]),
        "pct_abandono_fmt": _link_pct_fmt(total["pct_abandono"]), "tma_locator_fmt": _link_tempo_fmt(total["tma_locator_sec"]),
        "tma_ath_fmt": _link_tempo_fmt(total["tma_ath_sec"]), "custo_fmt": _link_money_fmt(total["custo"]),
        "alerta_perda": total["pct_perda"] > 5, "alerta_abandono": total["pct_abandono"] > 5,
    }


def _link_daily(df):
    dados = []
    if df is None or df.empty:
        return dados
    for data, grupo in df.groupby(df["Data"].dt.normalize()):
        total = _link_card_total(agregar_link(grupo))
        dados.append({"data": data.strftime("%Y-%m-%d"), "label": data.strftime("%d/%m"), **total})
    return sorted(dados, key=lambda x: x["data"])


def _link_hourly(df):
    dados = []
    if df is None or df.empty:
        return dados
    for hora, grupo in df.groupby("Hora"):
        total = _link_card_total(agregar_link(grupo))
        dados.append({"hora": int(hora), "label": f"{int(hora):02d}h", **total})
    return sorted(dados, key=lambda x: x["hora"])


def _link_data_arg(nome, padrao=""):
    """Valida datas YYYY-MM-DD recebidas pela URL e aplica fallback seguro."""
    valor = str(request.args.get(nome) or "").strip()
    try:
        return pd.to_datetime(valor, format="%Y-%m-%d", errors="raise").strftime("%Y-%m-%d") if valor else padrao
    except Exception:
        return padrao


def _link_periodo_ordenado(data_inicio, data_fim):
    """Garante que o intervalo esteja em ordem crescente."""
    if not data_inicio and not data_fim:
        return "", ""
    if not data_inicio:
        data_inicio = data_fim
    if not data_fim:
        data_fim = data_inicio
    return (data_inicio, data_fim) if data_inicio <= data_fim else (data_fim, data_inicio)


def _link_filtrar_periodo(df, data_inicio, data_fim):
    if df is None or df.empty or not data_inicio or not data_fim:
        return df.iloc[0:0].copy() if df is not None else pd.DataFrame()
    serie_data = df["Data"].dt.strftime("%Y-%m-%d")
    return df[(serie_data >= data_inicio) & (serie_data <= data_fim)].copy()


def _link_periodo_label(data_inicio, data_fim):
    def fmt(valor):
        try:
            return pd.to_datetime(valor).strftime("%d/%m/%Y")
        except Exception:
            return "--"
    return fmt(data_inicio) if data_inicio == data_fim else f"{fmt(data_inicio)} a {fmt(data_fim)}"

def _tipo_funil_b_arg():
    valor = str(request.args.get("tipo_b") or "humano_ad").strip().lower()
    return "way" if valor == "way" else "humano_ad"


def _tipo_funil_b_label(valor):
    return "Way" if valor == "way" else "Humano/AD"


def agregar_link_periodo(df):
    """Consolida um intervalo do Locator. Mailing soma o maior valor diário por campanha."""
    if df is None or df.empty:
        return agregar_link(df)
    total = agregar_link(df)
    mailing_diario = (
        df.assign(_DATA_DIA=df["Data"].dt.normalize())
          .groupby("_DATA_DIA", dropna=True)["Mailing"]
          .max()
    )
    total["mailing"] = float(mailing_diario.sum()) if len(mailing_diario) else 0.0
    total["spin"] = total["tentativas"] / total["mailing"] if total["mailing"] else 0
    return total


def montar_dashboard_link():
    base = carregar_base_link()
    base_funil2 = carregar_base_funil2_arquivo(LINK_ARQUIVO_BASE, "link")
    base_funil3 = carregar_base_funil3_arquivo(LINK_ARQUIVO_BASE, "link")
    if base.empty:
        return {"erro": f"Base não encontrada ou vazia: {LINK_ARQUIVO_BASE}", "filtros": {}, "daily": [], "hourly": []}

    datas = sorted(base["Data"].dt.strftime("%Y-%m-%d").dropna().unique().tolist())
    campanhas = sorted([c for c in base["NomeCampanha"].dropna().unique().tolist() if str(c).strip()])
    locator = [c for c in campanhas if "locator" in c.lower()]
    tipo_b = _tipo_funil_b_arg()
    base_funil_b = base_funil3 if tipo_b == "way" else base_funil2
    datas_b = sorted(base_funil_b["Data"].dt.strftime("%Y-%m-%d").dropna().unique().tolist()) if not base_funil_b.empty else []
    ativas = sorted([c for c in base_funil_b["NomeCampanha"].dropna().unique().tolist() if str(c).strip()]) if not base_funil_b.empty else []
    campanha_a = request.args.get("campanha_a") or (locator[0] if locator else (campanhas[0] if campanhas else ""))
    campanha_b = request.args.get("campanha_b") or (ativas[0] if ativas else "")
    padrao_a = datas[-1] if datas else ""
    padrao_b = padrao_a if padrao_a in datas_b else (datas_b[-1] if datas_b else "")
    data_a_ini = _link_data_arg("date_a_ini", _link_data_arg("date_a", padrao_a))
    data_a_fim = _link_data_arg("date_a_fim", _link_data_arg("date_a", padrao_a))
    data_b_ini = _link_data_arg("date_b_ini", _link_data_arg("date_b", padrao_b))
    data_b_fim = _link_data_arg("date_b_fim", _link_data_arg("date_b", padrao_b))
    data_a_ini, data_a_fim = _link_periodo_ordenado(data_a_ini, data_a_fim)
    data_b_ini, data_b_fim = _link_periodo_ordenado(data_b_ini, data_b_fim)

    df_a_hist = base[base["NomeCampanha"] == campanha_a].copy() if campanha_a else base.iloc[0:0].copy()
    df_a_periodo = _link_filtrar_periodo(df_a_hist, data_a_ini, data_a_fim)
    df_a_dia = df_a_hist[df_a_hist["Data"].dt.strftime("%Y-%m-%d") == data_a_fim].copy()
    df_b_base = base_funil_b[base_funil_b["NomeCampanha"] == campanha_b].copy() if campanha_b else base_funil_b.iloc[0:0].copy()
    df_b_periodo = _link_filtrar_periodo(df_b_base, data_b_ini, data_b_fim)

    current = _link_card_total(agregar_link(df_a_dia))
    comp_a = _link_card_total(agregar_link_periodo(df_a_periodo))
    if tipo_b == "way":
        comp_b = _link_card_total(agregar_funil2_way(df_b_periodo))
    else:
        comp_b = _funil2_card(agregar_funil2(df_b_periodo))
    tem_b = bool(campanha_b and not df_b_periodo.empty)
    variacoes = _comparativo_variacoes(comp_a, comp_b, tem_b, tipo_b)
    comparativo_exec = _comparativo_exec(comp_a, comp_b, tem_b, variacoes, tipo_b)
    daily = _link_daily(df_a_hist)
    hourly = _link_hourly(df_a_dia)

    def funnel_a(total):
        return [
            {"label": "Mailing", "value": total["mailing_fmt"], "taxa": "Base diária"},
            {"label": "Tentativas", "value": total["tentativas_fmt"], "taxa": "Spin " + total["spin_fmt"]},
            {"label": "Atendidas", "value": total["atendidas_fmt"], "taxa": "Hit " + total["hit_fmt"]},
            {"label": "Transferências", "value": total["transferencia_fmt"], "taxa": "Interação " + total["interacao_fmt"]},
            {"label": "Atend. humano", "value": total["atend_ath_fmt"], "taxa": "Recebimento " + total["recebimento_fmt"]},
            {"label": "Sucesso negócio", "value": total["sucesso_fmt"], "taxa": "Conversão " + total["conversao_fmt"]},
        ]

    def funnel_b(total):
        if tipo_b == "way":
            return [
                {"label": "Mailing", "value": total["mailing_fmt"], "taxa": "Base do período"},
                {"label": "Tentativas", "value": total["tentativas_fmt"], "taxa": "Spin " + total["spin_fmt"]},
                {"label": "Atendidas", "value": total["atendidas_fmt"], "taxa": "Hit " + total["hit_fmt"]},
                {"label": "Transferências", "value": total["transferencia_fmt"], "taxa": "Interação " + total["interacao_fmt"]},
                {"label": "Atend. humano", "value": total["atend_ath_fmt"], "taxa": "Recebimento " + total["recebimento_fmt"]},
                {"label": "Sucesso negócio", "value": total["sucesso_fmt"], "taxa": "Conversão " + total["conversao_fmt"]},
            ]
        return [
            {"label": "Mailing", "value": total["mailing_fmt"], "taxa": "Base do período"},
            {"label": "Tentativas", "value": total["tentativas_fmt"], "taxa": "Tent./logado " + total["tentativas_logado_fmt"]},
            {"label": "Atendidas", "value": total["atendidas_fmt"], "taxa": "Hit " + total["hit_fmt"]},
            {"label": "CPC", "value": total["cpc_fmt"], "taxa": "% Loc " + total["loc_fmt"]},
            {"label": "Acordo", "value": total["sucesso_fmt"], "taxa": "Conversão " + total["conver_fmt"]},
        ]

    campanha_ids = sorted([x for x in df_a_hist["CampaignId"].unique().tolist() if x])
    inbound_ids = sorted([x for x in df_a_hist["WayInboundCampaignId"].unique().tolist() if x])
    return {
        "cliente_nome": "LINK", "arquivo_base": "base_link.xlsx",
        "erro": None,
        "filtros": {"datas": datas, "datas_b": datas_b, "campanhas": campanhas, "locator": locator, "ativas": ativas, "data": data_a_fim, "data_a": data_a_fim, "data_b": data_b_fim, "data_a_ini": data_a_ini, "data_a_fim": data_a_fim, "data_b_ini": data_b_ini, "data_b_fim": data_b_fim, "periodo_a_label": _link_periodo_label(data_a_ini, data_a_fim), "periodo_b_label": _link_periodo_label(data_b_ini, data_b_fim), "campanha_a": campanha_a, "campanha_b": campanha_b, "tipo_b": tipo_b, "tipo_b_label": _tipo_funil_b_label(tipo_b)},
        "campaign_ids": campanha_ids, "inbound_ids": inbound_ids,
        "current": current, "daily": daily, "hourly": hourly,
        "comparativo": {"a": comp_a, "b": comp_b, "funnel_a": funnel_a(comp_a), "funnel_b": funnel_b(comp_b), "tem_b": tem_b, "tem_sheet": not base_funil_b.empty, "tem_sheet_funil2": not base_funil2.empty, "tem_sheet_funil3": not base_funil3.empty, "tipo_b": tipo_b, "tipo_b_label": _tipo_funil_b_label(tipo_b), "variacoes": variacoes, "exec": comparativo_exec},
        "alerta_daily_perda": any(x["pct_perda"] > 5 for x in daily),
        "alerta_daily_abandono": any(x["pct_abandono"] > 5 for x in daily),
        "alerta_hour_perda": any(x["pct_perda"] > 5 for x in hourly),
        "alerta_hour_abandono": any(x["pct_abandono"] > 5 for x in hourly),
    }


@app.route('/cliente/link/painel')
def link_index() -> str:
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if not usuario_pode_acessar_cliente(session.get('usuario'), 'link'):
        return acesso_negado()
    dashboard = montar_dashboard_link()
    return render_template('link_cockpit.html', dashboard=dashboard, usuario=session.get('usuario'))


@app.route('/cliente/link/painel/api')
def link_api():
    if 'usuario' not in session:
        return jsonify({"error": "unauthorized"}), 401
    if not usuario_pode_acessar_cliente(session.get('usuario'), 'link'):
        return jsonify({"error": "forbidden"}), 403
    return jsonify(montar_dashboard_link())


# ===== CLIENTES LOCATOR COMPARTILHADOS | Funil híbrido + Daily + Hora a hora =====
# Reaproveita as regras validadas da LINK, mantendo cache e Excel independentes por cliente.
LOCATOR_CLIENTES_CACHE = {}


def _locator_cliente_arquivo(slug):
    config = LOCATOR_CLIENTES_CONFIG.get(slug, {})
    arquivo = config.get("arquivo", "")
    return BASE_DIR / "data" / arquivo


def carregar_base_locator_cliente(slug):
    arquivo = _locator_cliente_arquivo(slug)
    if not arquivo.exists():
        return preparar_base_link(pd.DataFrame(columns=LINK_COLUMNS))
    mtime = arquivo.stat().st_mtime
    cache = LOCATOR_CLIENTES_CACHE.setdefault(slug, {"mtime": None, "df": None})
    if cache.get("df") is not None and cache.get("mtime") == mtime:
        return cache["df"].copy()
    df = pd.read_excel(arquivo)
    df = preparar_base_link(df)
    cache["mtime"] = mtime
    cache["df"] = df.copy()
    return df.copy()


def carregar_base_funil2_locator_cliente(slug):
    arquivo = _locator_cliente_arquivo(slug)
    return carregar_base_funil2_arquivo(arquivo, slug)


def carregar_base_funil3_locator_cliente(slug):
    arquivo = _locator_cliente_arquivo(slug)
    return carregar_base_funil3_arquivo(arquivo, slug)


def montar_dashboard_locator_cliente(slug):
    config = LOCATOR_CLIENTES_CONFIG.get(slug)
    if not config:
        return {"erro": "Cliente não configurado.", "filtros": {}, "daily": [], "hourly": []}
    base = carregar_base_locator_cliente(slug)
    base_funil2 = carregar_base_funil2_locator_cliente(slug)
    base_funil3 = carregar_base_funil3_locator_cliente(slug)
    arquivo = config["arquivo"]
    metadata = {"cliente_slug": slug, "cliente_nome": config["nome"], "arquivo_base": arquivo}
    if base.empty:
        return {**metadata, "erro": f"Base não encontrada ou vazia: data/{arquivo}", "filtros": {}, "daily": [], "hourly": []}

    datas = sorted(base["Data"].dt.strftime("%Y-%m-%d").dropna().unique().tolist())
    campanhas = sorted([c for c in base["NomeCampanha"].dropna().unique().tolist() if str(c).strip()])
    locator = [c for c in campanhas if "locator" in c.lower()]
    tipo_b = _tipo_funil_b_arg()
    base_funil_b = base_funil3 if tipo_b == "way" else base_funil2
    datas_b = sorted(base_funil_b["Data"].dt.strftime("%Y-%m-%d").dropna().unique().tolist()) if not base_funil_b.empty else []
    ativas = sorted([c for c in base_funil_b["NomeCampanha"].dropna().unique().tolist() if str(c).strip()]) if not base_funil_b.empty else []
    campanha_a = request.args.get("campanha_a") or (locator[0] if locator else (campanhas[0] if campanhas else ""))
    campanha_b = request.args.get("campanha_b") or (ativas[0] if ativas else "")
    padrao_a = datas[-1] if datas else ""
    padrao_b = padrao_a if padrao_a in datas_b else (datas_b[-1] if datas_b else "")
    data_a_ini = _link_data_arg("date_a_ini", _link_data_arg("date_a", padrao_a))
    data_a_fim = _link_data_arg("date_a_fim", _link_data_arg("date_a", padrao_a))
    data_b_ini = _link_data_arg("date_b_ini", _link_data_arg("date_b", padrao_b))
    data_b_fim = _link_data_arg("date_b_fim", _link_data_arg("date_b", padrao_b))
    data_a_ini, data_a_fim = _link_periodo_ordenado(data_a_ini, data_a_fim)
    data_b_ini, data_b_fim = _link_periodo_ordenado(data_b_ini, data_b_fim)

    df_a_hist = base[base["NomeCampanha"] == campanha_a].copy() if campanha_a else base.iloc[0:0].copy()
    df_a_periodo = _link_filtrar_periodo(df_a_hist, data_a_ini, data_a_fim)
    df_a_dia = df_a_hist[df_a_hist["Data"].dt.strftime("%Y-%m-%d") == data_a_fim].copy()
    df_b_base = base_funil_b[base_funil_b["NomeCampanha"] == campanha_b].copy() if campanha_b else base_funil_b.iloc[0:0].copy()
    df_b_periodo = _link_filtrar_periodo(df_b_base, data_b_ini, data_b_fim)

    current = _link_card_total(agregar_link(df_a_dia))
    comp_a = _link_card_total(agregar_link_periodo(df_a_periodo))
    if tipo_b == "way":
        comp_b = _link_card_total(agregar_funil2_way(df_b_periodo))
    else:
        comp_b = _funil2_card(agregar_funil2(df_b_periodo))
    tem_b = bool(campanha_b and not df_b_periodo.empty)
    variacoes = _comparativo_variacoes(comp_a, comp_b, tem_b, tipo_b)
    comparativo_exec = _comparativo_exec(comp_a, comp_b, tem_b, variacoes, tipo_b)
    daily = _link_daily(df_a_hist)
    hourly = _link_hourly(df_a_dia)

    def funnel_a(total):
        return [
            {"label": "Mailing", "value": total["mailing_fmt"], "taxa": "Base diária"},
            {"label": "Tentativas", "value": total["tentativas_fmt"], "taxa": "Spin " + total["spin_fmt"]},
            {"label": "Atendidas", "value": total["atendidas_fmt"], "taxa": "Hit " + total["hit_fmt"]},
            {"label": "Transferências", "value": total["transferencia_fmt"], "taxa": "Interação " + total["interacao_fmt"]},
            {"label": "Atend. humano", "value": total["atend_ath_fmt"], "taxa": "Recebimento " + total["recebimento_fmt"]},
            {"label": "Sucesso negócio", "value": total["sucesso_fmt"], "taxa": "Conversão " + total["conversao_fmt"]},
        ]

    def funnel_b(total):
        if tipo_b == "way":
            return [
                {"label": "Mailing", "value": total["mailing_fmt"], "taxa": "Base do período"},
                {"label": "Tentativas", "value": total["tentativas_fmt"], "taxa": "Spin " + total["spin_fmt"]},
                {"label": "Atendidas", "value": total["atendidas_fmt"], "taxa": "Hit " + total["hit_fmt"]},
                {"label": "Transferências", "value": total["transferencia_fmt"], "taxa": "Interação " + total["interacao_fmt"]},
                {"label": "Atend. humano", "value": total["atend_ath_fmt"], "taxa": "Recebimento " + total["recebimento_fmt"]},
                {"label": "Sucesso negócio", "value": total["sucesso_fmt"], "taxa": "Conversão " + total["conversao_fmt"]},
            ]
        return [
            {"label": "Mailing", "value": total["mailing_fmt"], "taxa": "Base do período"},
            {"label": "Tentativas", "value": total["tentativas_fmt"], "taxa": "Tent./logado " + total["tentativas_logado_fmt"]},
            {"label": "Atendidas", "value": total["atendidas_fmt"], "taxa": "Hit " + total["hit_fmt"]},
            {"label": "CPC", "value": total["cpc_fmt"], "taxa": "% Loc " + total["loc_fmt"]},
            {"label": "Acordo", "value": total["sucesso_fmt"], "taxa": "Conversão " + total["conver_fmt"]},
        ]

    campanha_ids = sorted([x for x in df_a_hist["CampaignId"].unique().tolist() if x])
    inbound_ids = sorted([x for x in df_a_hist["WayInboundCampaignId"].unique().tolist() if x])
    return {
        **metadata,
        "erro": None,
        "filtros": {"datas": datas, "datas_b": datas_b, "campanhas": campanhas, "locator": locator, "ativas": ativas, "data": data_a_fim, "data_a": data_a_fim, "data_b": data_b_fim, "data_a_ini": data_a_ini, "data_a_fim": data_a_fim, "data_b_ini": data_b_ini, "data_b_fim": data_b_fim, "periodo_a_label": _link_periodo_label(data_a_ini, data_a_fim), "periodo_b_label": _link_periodo_label(data_b_ini, data_b_fim), "campanha_a": campanha_a, "campanha_b": campanha_b, "tipo_b": tipo_b, "tipo_b_label": _tipo_funil_b_label(tipo_b)},
        "campaign_ids": campanha_ids, "inbound_ids": inbound_ids,
        "current": current, "daily": daily, "hourly": hourly,
        "comparativo": {"a": comp_a, "b": comp_b, "funnel_a": funnel_a(comp_a), "funnel_b": funnel_b(comp_b), "tem_b": tem_b, "tem_sheet": not base_funil_b.empty, "tem_sheet_funil2": not base_funil2.empty, "tem_sheet_funil3": not base_funil3.empty, "tipo_b": tipo_b, "tipo_b_label": _tipo_funil_b_label(tipo_b), "variacoes": variacoes, "exec": comparativo_exec},
        "alerta_daily_perda": any(x["pct_perda"] > 5 for x in daily),
        "alerta_daily_abandono": any(x["pct_abandono"] > 5 for x in daily),
        "alerta_hour_perda": any(x["pct_perda"] > 5 for x in hourly),
        "alerta_hour_abandono": any(x["pct_abandono"] > 5 for x in hourly),
    }


@app.route('/cliente/<slug>/painel')
def locator_cliente_index(slug):
    if slug not in LOCATOR_CLIENTES_CONFIG:
        return redirect(url_for('dashboard'))
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if not usuario_pode_acessar_cliente(session.get('usuario'), slug):
        return acesso_negado()
    dashboard = montar_dashboard_locator_cliente(slug)
    return render_template('locator_cliente_cockpit.html', dashboard=dashboard, usuario=session.get('usuario'))


@app.route('/cliente/<slug>/painel/api')
def locator_cliente_api(slug):
    if slug not in LOCATOR_CLIENTES_CONFIG:
        return jsonify({"error": "not_found"}), 404
    if 'usuario' not in session:
        return jsonify({"error": "unauthorized"}), 401
    if not usuario_pode_acessar_cliente(session.get('usuario'), slug):
        return jsonify({"error": "forbidden"}), 403
    return jsonify(montar_dashboard_locator_cliente(slug))


# ===== GESTOR LOCATOR | Visão geral integrada =====
GESTOR_LOCATOR_EXCEL = Path(os.getenv("GESTOR_LOCATOR_EXCEL_PATH", BASE_DIR / "data" / "base_gestor_locator.xlsx"))
GESTOR_LOCATOR_CACHE = {"mtime": None, "records": None, "status": None}


def _gestor_locator_clean_value(valor):
    if pd.isna(valor):
        return None
    if hasattr(valor, "strftime"):
        try:
            return valor.strftime("%Y-%m-%d")
        except Exception:
            return str(valor)
    if isinstance(valor, (np.integer,)):
        return int(valor)
    if isinstance(valor, (np.floating,)):
        return float(valor)
    return valor


def _gestor_locator_norm_col(col):
    """Normaliza cabeçalho do Excel para evitar painel vazio por acento/espaço."""
    import unicodedata
    txt = str(col or "").strip()
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("ascii")
    return "".join(ch for ch in txt.lower() if ch.isalnum())


def _gestor_locator_read_excel():
    """Lê a primeira aba com dados da base do Gestor Locator."""
    xls = pd.ExcelFile(GESTOR_LOCATOR_EXCEL)
    for sheet in xls.sheet_names:
        df = pd.read_excel(GESTOR_LOCATOR_EXCEL, sheet_name=sheet)
        if not df.empty:
            return df, sheet
    return pd.DataFrame(), (xls.sheet_names[0] if xls.sheet_names else "")


def _gestor_locator_records():
    if not GESTOR_LOCATOR_EXCEL.exists():
        GESTOR_LOCATOR_CACHE["status"] = {"ok": False, "msg": f"Arquivo não encontrado: {GESTOR_LOCATOR_EXCEL}", "rows": 0}
        return []

    mtime = GESTOR_LOCATOR_EXCEL.stat().st_mtime
    if GESTOR_LOCATOR_CACHE.get("records") is not None and GESTOR_LOCATOR_CACHE.get("mtime") == mtime:
        return list(GESTOR_LOCATOR_CACHE["records"])

    try:
        df, sheet_name = _gestor_locator_read_excel()
    except Exception as exc:
        GESTOR_LOCATOR_CACHE["mtime"] = mtime
        GESTOR_LOCATOR_CACHE["records"] = []
        GESTOR_LOCATOR_CACHE["status"] = {"ok": False, "msg": f"Erro ao ler Excel: {exc}", "rows": 0}
        return []

    # Remove colunas totalmente vazias e espaços nos nomes.
    df = df.dropna(axis=1, how="all")
    df.columns = [str(c).strip() for c in df.columns]

    aliases_norm = {
        "dt": "Data", "data": "Data", "date": "Data", "dia": "Data",
        "hora": "Hora", "hour": "Hora", "hr": "Hora",
        "campaignid": "CampaignId", "idcampanha": "CampaignId",
        "wayinboundcampaignid": "WayInboundCampaignId", "wayid": "WayInboundCampaignId", "wayinboundid": "WayInboundCampaignId",
        "nomecampanha": "NomeCampanha", "campanha": "NomeCampanha", "nomecamp": "NomeCampanha", "locator": "NomeCampanha",
        "mailing": "Mailing", "ad": "AD", "ath": "ATH",
        "tentativas": "Tentativas", "discado": "Tentativas", "discadas": "Tentativas",
        "atendidas": "Atendidas", "atendida": "Atendidas", "atendimento": "Atendidas",
        "transferencia": "Transferencia", "transferencias": "Transferencia", "transferida": "Transferencia",
        "perda": "Perda", "perdas": "Perda",
        "atendath": "Atend_ATH", "atendidasath": "Atend_ATH",
        "sucesso": "Sucesso_Negocio", "sucessonegocio": "Sucesso_Negocio", "sucessodenegocio": "Sucesso_Negocio", "sucessos": "Sucesso_Negocio",
        "tmalocator": "TMA_LOCATOR", "tmaath": "TMA_ATH",
        "hitrate": "HitRate",
        "sucessointeracao": "SucessoInteracao", "sucessointeracao": "SucessoInteracao",
        "perda": "Perda", "percentualperda": "%Perda", "perdapct": "%Perda",
        "abandono": "Abandono", "abandonos": "Abandono", "percentualabandono": "%Abandono", "abandonopct": "%Abandono",
        "sla": "SLA", "custo": "Custo", "cliente": "Cliente", "clientes": "Cliente",
    }

    rename_map = {}
    for c in df.columns:
        canonical = aliases_norm.get(_gestor_locator_norm_col(c))
        if canonical:
            rename_map[c] = canonical
    df = df.rename(columns=rename_map)

    # Algumas bases podem vir com duas colunas que viram o mesmo nome após tratar acento/espaço
    # (ex.: "Sucesso" e "Sucesso_Negocio"). Isso fazia df[col] virar DataFrame e quebrava o painel.
    if df.columns.duplicated().any():
        dedup = pd.DataFrame(index=df.index)
        for col in dict.fromkeys(df.columns):
            bloco = df.loc[:, df.columns == col]
            if bloco.shape[1] == 1:
                dedup[col] = bloco.iloc[:, 0]
            else:
                dedup[col] = bloco.bfill(axis=1).iloc[:, 0]
        df = dedup

    expected = ["Data", "Hora", "CampaignId", "WayInboundCampaignId", "NomeCampanha", "Mailing", "AD", "ATH", "Tentativas", "Atendidas", "Transferencia", "Perda", "Atend_ATH", "Sucesso_Negocio", "TMA_LOCATOR", "TMA_ATH", "HitRate", "SucessoInteracao", "%Perda", "Abandono", "%Abandono", "SLA", "Custo", "Cliente"]
    for col in expected:
        if col not in df.columns:
            df[col] = None

    # Se não existir Cliente na base, deixa um nome padrão para não sumir no agrupamento.
    df["Cliente"] = df["Cliente"].apply(lambda x: "Gestor Locator" if pd.isna(x) or str(x).strip() == "" else str(x).strip())
    df["NomeCampanha"] = df["NomeCampanha"].apply(lambda x: "Sem Campanha" if pd.isna(x) or str(x).strip() == "" else str(x).strip())

    df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True).dt.strftime("%Y-%m-%d")
    df = df[df["Data"].notna()].copy()

    numeric_cols = ["Hora", "CampaignId", "WayInboundCampaignId", "Mailing", "AD", "ATH", "Tentativas", "Atendidas", "Transferencia", "Perda", "Atend_ATH", "Sucesso_Negocio", "HitRate", "SucessoInteracao", "%Perda", "Abandono", "%Abandono", "SLA", "Custo"]
    for col in numeric_cols:
        df[col] = df[col].apply(_link_num)

    records = []
    for row in df[expected].to_dict(orient="records"):
        records.append({k: _gestor_locator_clean_value(v) for k, v in row.items()})

    GESTOR_LOCATOR_CACHE["mtime"] = mtime
    GESTOR_LOCATOR_CACHE["records"] = records
    GESTOR_LOCATOR_CACHE["status"] = {"ok": True, "msg": f"Base carregada: {sheet_name}", "rows": len(records), "arquivo": "data/base_gestor_locator.xlsx"}
    return list(records)


def _gestor_locator_status():
    _gestor_locator_records()
    return dict(GESTOR_LOCATOR_CACHE.get("status") or {})


@app.route('/cliente/gestor-locator/painel')
def gestor_locator_index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if not usuario_pode_acessar_cliente(session.get('usuario'), 'gestor-locator'):
        return acesso_negado()
    records = _gestor_locator_records()
    return render_template('gestor_locator_cockpit.html', raw_data=records, base_status=_gestor_locator_status(), usuario=session.get('usuario'))


@app.route('/cliente/gestor-locator/painel/api')
def gestor_locator_api():
    if 'usuario' not in session:
        return jsonify({"error": "unauthorized"}), 401
    if not usuario_pode_acessar_cliente(session.get('usuario'), 'gestor-locator'):
        return jsonify({"error": "forbidden"}), 403
    return jsonify({"data": _gestor_locator_records(), "status": _gestor_locator_status(), "arquivo_base": "data/base_gestor_locator.xlsx"})



# ===== REDE BRASIL | Locator x Campanha Comparativa =====
# Integrado a partir do projeto painel_locator_comparativo_osp.
REDE_BRASIL_EXCEL = Path(os.getenv("REDE_BRASIL_EXCEL_PATH", BASE_DIR / "data" / "base_rede_brasil.xlsx"))
REDE_BRASIL_CACHE = {"mtime": None, "locator": None, "comparativo": None, "status": None}


def _rb_parse_number(value):
    if value is None:
        return 0.0
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return 0.0
    text = text.replace("R$", "").replace("%", "").strip()
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except Exception:
        return 0.0


def _rb_fmt_int(value):
    try:
        return f"{int(round(float(value))):,}".replace(",", ".")
    except Exception:
        return "0"


def _rb_fmt_dec(value, casas=1):
    try:
        return f"{float(value):.{casas}f}".replace(".", ",")
    except Exception:
        return "0"


def _rb_fmt_pct(value, casas=2):
    return f"{_rb_fmt_dec(value, casas)}%"


def _rb_fmt_money(value):
    try:
        return "R$ " + f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def _rb_avg_time(series):
    seconds = []
    for item in series.dropna().astype(str):
        parts = item.strip().split(":")
        if len(parts) != 3:
            continue
        try:
            h, m, s = [int(float(p)) for p in parts]
            seconds.append(h * 3600 + m * 60 + s)
        except Exception:
            continue
    if not seconds:
        return "00:00:00"
    avg = int(round(sum(seconds) / len(seconds)))
    return f"{avg // 3600:02d}:{(avg % 3600) // 60:02d}:{avg % 60:02d}"


def _rb_prepare_locator(df):
    if df.empty:
        return df
    df = df.copy()
    for col in ["Hora", "CampaignId", "WayInboundCampaignId", "Mailing", "AD", "ATH", "Tentativas", "Atendidas", "Transferencia", "Perda", "Atend_ATH", "Sucesso_Negocio", "Custo"]:
        if col in df.columns:
            df[col] = df[col].apply(_rb_parse_number)
    for col in ["HitRate", "SucessoInteracao", "%Perda", "%Abandono", "SLA"]:
        if col in df.columns:
            df[col + "_num"] = df[col].apply(_rb_parse_number)
    if "Custo" in df.columns:
        df["Custo_num"] = df["Custo"].apply(_rb_parse_number)
    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def _rb_prepare_comparativo(df):
    if df.empty:
        return df
    df = df.copy()
    for col in ["Hora", "CampaignId", "Logados", "Mailing", "Tentativas", "Atendidas", "Cpc", "Acordo", "TELECOM"]:
        if col in df.columns:
            df[col] = df[col].apply(_rb_parse_number)
    for col in ["HitRate", "Loc", "Conver"]:
        if col in df.columns:
            df[col + "_num"] = df[col].apply(_rb_parse_number)
    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def _rb_load_bases():
    if not REDE_BRASIL_EXCEL.exists():
        return pd.DataFrame(), pd.DataFrame(), {"ok": False, "msg": "Base Rede Brasil não encontrada.", "base_dir": str(REDE_BRASIL_EXCEL), "arquivos_lidos": 0, "source": "excel"}
    mtime = REDE_BRASIL_EXCEL.stat().st_mtime
    if REDE_BRASIL_CACHE.get("mtime") == mtime and REDE_BRASIL_CACHE.get("locator") is not None:
        return REDE_BRASIL_CACHE["locator"].copy(), REDE_BRASIL_CACHE["comparativo"].copy(), dict(REDE_BRASIL_CACHE["status"])
    try:
        xls = pd.ExcelFile(REDE_BRASIL_EXCEL)
        locator = pd.read_excel(REDE_BRASIL_EXCEL, sheet_name="Locator")
        comparativo = pd.read_excel(REDE_BRASIL_EXCEL, sheet_name="Comparativo")
        locator.columns = [str(c).strip() for c in locator.columns]
        comparativo.columns = [str(c).strip() for c in comparativo.columns]
        locator = _rb_prepare_locator(locator)
        comparativo = _rb_prepare_comparativo(comparativo)
        status = {"ok": True, "msg": "Base Rede Brasil carregada", "base_dir": "data/base_rede_brasil.xlsx", "arquivos_lidos": 1, "source": "excel", "sheets": xls.sheet_names}
        REDE_BRASIL_CACHE.update({"mtime": mtime, "locator": locator.copy(), "comparativo": comparativo.copy(), "status": status})
        return locator, comparativo, dict(status)
    except Exception as exc:
        return pd.DataFrame(), pd.DataFrame(), {"ok": False, "msg": str(exc), "base_dir": "data/base_rede_brasil.xlsx", "arquivos_lidos": 0, "source": "excel"}


def _rb_filter(df, data=None, campanha=None, hora=None):
    if df.empty:
        return df
    out = df.copy()
    if data and "Data" in out.columns:
        out = out[out["Data"] == data]
    if campanha and campanha != "__all__" and "NomeCampanha" in out.columns:
        out = out[out["NomeCampanha"] == campanha]
    if hora and hora != "__all__" and "Hora" in out.columns:
        out = out[out["Hora"].fillna(-1).astype(int).astype(str) == str(hora)]
    return out


def _rb_list(df, col):
    if df.empty or col not in df.columns:
        return []
    return sorted(df[col].dropna().astype(str).unique().tolist())


def _rb_choose(df, requested):
    items = _rb_list(df, "NomeCampanha")
    if not items:
        return "__all__"
    if requested in items:
        return requested
    mode = df["NomeCampanha"].mode()
    return str(mode.iloc[0]) if len(mode) else items[0]


def _rb_locator_summary(df):
    if df.empty:
        raw = {}
        return {"Mailing":"0","AD médio":"0","ATH médio":"0","Tentativas":"0","Atendidas":"0","Transferências":"0","Atendidas ATH":"0","Sucesso Negócio":"0","Hit Rate":"0,00%","Sucesso Interação":"0,00%","% Perda":"0,00%","% Abandono":"0,00%","SLA":"0,00%","Custo":"R$ 0,00","TMA Locator":"00:00:00","TMA ATH":"00:00:00","_raw":raw}
    raw = {
        "Mailing": df["Mailing"].max() if "Mailing" in df else 0,
        "AD médio": df["AD"].mean() if "AD" in df else 0,
        "ATH médio": df["ATH"].mean() if "ATH" in df else 0,
        "Tentativas": df["Tentativas"].sum() if "Tentativas" in df else 0,
        "Atendidas": df["Atendidas"].sum() if "Atendidas" in df else 0,
        "Transferências": df["Transferencia"].sum() if "Transferencia" in df else 0,
        "Atendidas ATH": df["Atend_ATH"].sum() if "Atend_ATH" in df else 0,
        "Sucesso Negócio": df["Sucesso_Negocio"].sum() if "Sucesso_Negocio" in df else 0,
        "Hit Rate": df["HitRate_num"].mean() if "HitRate_num" in df else 0,
        "Sucesso Interação": df["SucessoInteracao_num"].mean() if "SucessoInteracao_num" in df else 0,
        "% Perda": df["%Perda_num"].mean() if "%Perda_num" in df else 0,
        "% Abandono": df["%Abandono_num"].mean() if "%Abandono_num" in df else 0,
        "SLA": df["SLA_num"].mean() if "SLA_num" in df else 0,
        "Custo": df["Custo_num"].sum() if "Custo_num" in df else 0,
    }
    return {"Mailing":_rb_fmt_int(raw["Mailing"]),"AD médio":_rb_fmt_dec(raw["AD médio"]),"ATH médio":_rb_fmt_dec(raw["ATH médio"]),"Tentativas":_rb_fmt_int(raw["Tentativas"]),"Atendidas":_rb_fmt_int(raw["Atendidas"]),"Transferências":_rb_fmt_int(raw["Transferências"]),"Atendidas ATH":_rb_fmt_int(raw["Atendidas ATH"]),"Sucesso Negócio":_rb_fmt_int(raw["Sucesso Negócio"]),"Hit Rate":_rb_fmt_pct(raw["Hit Rate"]*100 if abs(raw["Hit Rate"]) <= 1 else raw["Hit Rate"]),"Sucesso Interação":_rb_fmt_pct(raw["Sucesso Interação"]*100 if abs(raw["Sucesso Interação"]) <= 1 else raw["Sucesso Interação"]),"% Perda":_rb_fmt_pct(raw["% Perda"]*100 if abs(raw["% Perda"]) <= 1 else raw["% Perda"]),"% Abandono":_rb_fmt_pct(raw["% Abandono"]*100 if abs(raw["% Abandono"]) <= 1 else raw["% Abandono"]),"SLA":_rb_fmt_pct(raw["SLA"]*100 if abs(raw["SLA"]) <= 1 else raw["SLA"]),"Custo":_rb_fmt_money(raw["Custo"]),"TMA Locator":_rb_avg_time(df["TMA_LOCATOR"]) if "TMA_LOCATOR" in df else "00:00:00","TMA ATH":_rb_avg_time(df["TMA_ATH"]) if "TMA_ATH" in df else "00:00:00","_raw":raw}


def _rb_comp_summary(df):
    if df.empty:
        return {"Mailing":"0","Logados médios":"0","Tentativas":"0","Atendidas":"0","CPC":"0","Acordo":"0","Hit Rate":"0,00%","LOC":"0,00%","Conversão":"0,00%","TMA":"00:00:00","_raw":{}}
    raw={"Mailing":df["Mailing"].max() if "Mailing" in df else 0,"Logados médios":df["Logados"].mean() if "Logados" in df else 0,"Tentativas":df["Tentativas"].sum() if "Tentativas" in df else 0,"Atendidas":df["Atendidas"].sum() if "Atendidas" in df else 0,"CPC":df["Cpc"].sum() if "Cpc" in df else 0,"Acordo":df["Acordo"].sum() if "Acordo" in df else 0,"Hit Rate":df["HitRate_num"].mean() if "HitRate_num" in df else 0,"LOC":df["Loc_num"].mean() if "Loc_num" in df else 0,"Conversão":df["Conver_num"].mean() if "Conver_num" in df else 0}
    pct=lambda v:_rb_fmt_pct(v*100 if abs(v)<=1 else v)
    return {"Mailing":_rb_fmt_int(raw["Mailing"]),"Logados médios":_rb_fmt_dec(raw["Logados médios"]),"Tentativas":_rb_fmt_int(raw["Tentativas"]),"Atendidas":_rb_fmt_int(raw["Atendidas"]),"CPC":_rb_fmt_int(raw["CPC"]),"Acordo":_rb_fmt_int(raw["Acordo"]),"Hit Rate":pct(raw["Hit Rate"]),"LOC":pct(raw["LOC"]),"Conversão":pct(raw["Conversão"]),"TMA":_rb_avg_time(df["TMA"]) if "TMA" in df else "00:00:00","_raw":raw}


def _rb_variation(loc_raw, comp_raw):
    """Comparação executiva entre Locator e campanha espelho.

    No Locator, Transferências representam o CPC entregue para o atendimento humano
    e Sucesso Negócio representa o Acordo, deixando os dois funis comparáveis.
    """
    rows=[]
    indicadores = [
        ("ATH / Logados", "ATH médio", "Logados médios"),
        ("Mailing", "Mailing", "Mailing"),
        ("Tentativas", "Tentativas", "Tentativas"),
        ("Atendidas", "Atendidas", "Atendidas"),
        ("CPC", "Transferências", "CPC"),
        ("Acordo", "Sucesso Negócio", "Acordo"),
    ]
    for label, lk, ck in indicadores:
        lv=float(loc_raw.get(lk,0) or 0)
        cv=float(comp_raw.get(ck,0) or 0)
        delta=((lv-cv)/cv*100) if cv else (100.0 if lv > 0 else 0.0)
        txt=f"{'+' if delta>=0 else ''}{_rb_fmt_dec(delta,1)}%"
        rows.append({
            "indicador":label,
            "locator":_rb_fmt_int(lv),
            "comparativa":_rb_fmt_int(cv),
            "variacao":txt,
            "sinal":"up" if delta>=0 else "down"
        })
    return rows


def _rb_comp_hourly_consolidated(df):
    """Consolidado hora a hora da campanha espelho selecionada."""
    if df.empty or "Hora" not in df.columns:
        return {"rows": [], "total": {}}

    agg = {}
    for col in ["Logados", "Tentativas", "Atendidas", "Cpc", "Acordo"]:
        if col in df.columns:
            agg[col] = "sum" if col != "Logados" else "mean"
    if "Mailing" in df.columns:
        agg["Mailing"] = "max"

    g = df.groupby("Hora", dropna=True).agg(agg).reset_index().sort_values("Hora")

    def calc_row(row):
        logados = float(row.get("Logados", 0) or 0)
        mailing = float(row.get("Mailing", 0) or 0)
        cpc = float(row.get("Cpc", 0) or 0)
        acordo = float(row.get("Acordo", 0) or 0)
        return {
            "Hora": str(int(row.get("Hora", 0))),
            "Logados": _rb_fmt_dec(logados, 1),
            "Mailing": _rb_fmt_int(mailing),
            "Tentativas": _rb_fmt_int(row.get("Tentativas", 0)),
            "Atendidas": _rb_fmt_int(row.get("Atendidas", 0)),
            "CPC": _rb_fmt_int(cpc),
            "Acordo": _rb_fmt_int(acordo),
            "CPC/Logados": _rb_fmt_dec(cpc / logados, 2) if logados else "0,00",
            "Acordo/Logados": _rb_fmt_dec(acordo / logados, 2) if logados else "0,00",
            "Acordo/Mailing": _rb_fmt_pct((acordo / mailing) * 100, 3) if mailing else "0,000%",
        }

    rows = [calc_row(r) for _, r in g.iterrows()]

    logados_medio = float(df["Logados"].mean()) if "Logados" in df.columns and len(df) else 0
    mailing_dia = float(df["Mailing"].max()) if "Mailing" in df.columns and len(df) else 0
    tentativas = float(df["Tentativas"].sum()) if "Tentativas" in df.columns else 0
    atendidas = float(df["Atendidas"].sum()) if "Atendidas" in df.columns else 0
    cpc = float(df["Cpc"].sum()) if "Cpc" in df.columns else 0
    acordo = float(df["Acordo"].sum()) if "Acordo" in df.columns else 0

    total = {
        "Hora": "TOTAL DIA",
        "Logados": _rb_fmt_dec(logados_medio, 1),
        "Mailing": _rb_fmt_int(mailing_dia),
        "Tentativas": _rb_fmt_int(tentativas),
        "Atendidas": _rb_fmt_int(atendidas),
        "CPC": _rb_fmt_int(cpc),
        "Acordo": _rb_fmt_int(acordo),
        "CPC/Logados": _rb_fmt_dec(cpc / logados_medio, 2) if logados_medio else "0,00",
        "Acordo/Logados": _rb_fmt_dec(acordo / logados_medio, 2) if logados_medio else "0,00",
        "Acordo/Mailing": _rb_fmt_pct((acordo / mailing_dia) * 100, 3) if mailing_dia else "0,000%",
    }
    return {"rows": rows, "total": total}


def _rb_hourly(df):
    if df.empty or "Hora" not in df.columns:
        return {"horas":[],"tentativas":[],"atendidas":[],"transferencias":[],"sucesso_negocio":[]}
    cols={c:"sum" for c in ["Tentativas","Atendidas","Transferencia","Sucesso_Negocio"] if c in df.columns}
    g=df.groupby("Hora",dropna=True).agg(cols).reset_index().sort_values("Hora")
    def vals(c): return [int(x) for x in g[c].tolist()] if c in g.columns else []
    return {"horas":[str(int(h)) for h in g["Hora"].tolist()],"tentativas":vals("Tentativas"),"atendidas":vals("Atendidas"),"transferencias":vals("Transferencia"),"sucesso_negocio":vals("Sucesso_Negocio")}


@app.route('/cliente/rede-brasil/painel')
def rede_brasil_locator_index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if not usuario_pode_acessar_cliente(session.get('usuario'), 'rede-brasil'):
        return acesso_negado()
    return render_template('rede_brasil_locator.html', usuario=session.get('usuario'))


@app.route('/cliente/rede-brasil/painel/api/options')
def rede_brasil_locator_options():
    if 'usuario' not in session:
        return jsonify({"error":"unauthorized"}),401
    if not usuario_pode_acessar_cliente(session.get('usuario'),'rede-brasil'):
        return jsonify({"error":"forbidden"}),403
    loc,comp,meta=_rb_load_bases()
    datas=sorted(set(_rb_list(loc,"Data")+_rb_list(comp,"Data")))
    horas=sorted(set([str(int(h)) for h in loc.get("Hora",pd.Series(dtype=float)).dropna().tolist()]+[str(int(h)) for h in comp.get("Hora",pd.Series(dtype=float)).dropna().tolist()]), key=lambda x:int(x))
    return jsonify({"datas":datas,"clientes":["REDE BRASIL"],"locator_campaigns":_rb_list(loc,"NomeCampanha"),"comparativa_campaigns":_rb_list(comp,"NomeCampanha"),"horas":horas,"meta":meta})


@app.route('/cliente/rede-brasil/painel/api/data')
def rede_brasil_locator_data():
    if 'usuario' not in session:
        return jsonify({"error":"unauthorized"}),401
    if not usuario_pode_acessar_cliente(session.get('usuario'),'rede-brasil'):
        return jsonify({"error":"forbidden"}),403
    data=request.args.get("data"); loc_req=request.args.get("locator_campaign"); comp_req=request.args.get("comparativa_campaign"); hora="__all__"
    loc,comp,meta=_rb_load_bases()
    if not data:
        dates=sorted(set(_rb_list(loc,"Data")+_rb_list(comp,"Data"))); data=dates[-1] if dates else None
    loc_pool=_rb_filter(loc,data); comp_pool=_rb_filter(comp,data)
    loc_camp=_rb_choose(loc_pool,loc_req); comp_camp=_rb_choose(comp_pool,comp_req)
    loc_f=_rb_filter(loc,data,loc_camp,hora); comp_f=_rb_filter(comp,data,comp_camp,hora)
    loc_sum=_rb_locator_summary(loc_f); comp_sum=_rb_comp_summary(comp_f)
    # Consolidado do dia da campanha espelho: respeita data e campanha, mas não o filtro de hora.
    comp_day_selected = _rb_filter(comp, data, comp_camp, "__all__")
    hourly_consolidated = _rb_comp_hourly_consolidated(comp_day_selected)
    horas=sorted(set([str(int(h)) for h in loc_pool.get("Hora",pd.Series(dtype=float)).dropna().tolist()]+[str(int(h)) for h in comp_pool.get("Hora",pd.Series(dtype=float)).dropna().tolist()]), key=lambda x:int(x))
    return jsonify({"selected":{"data":data,"cliente":"REDE BRASIL","locator_campaign":loc_camp,"comparativa_campaign":comp_camp,"hora":hora},"available":{"locator_campaigns":_rb_list(loc_pool,"NomeCampanha"),"comparativa_campaigns":_rb_list(comp_pool,"NomeCampanha"),"horas":horas},"locator":loc_sum,"comparativa":comp_sum,"variation":_rb_variation(loc_sum["_raw"],comp_sum["_raw"]),"hourly":_rb_hourly(loc_f),"hourly_consolidated":hourly_consolidated,"meta":meta})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

