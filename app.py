from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "chave_secreta_cockpit_v1_3"

USUARIOS = {
    "admin": "123456",
    "gerber": "nicolas1616",
    "elvis.santos@olos.com.br": "olos@2026",
    "nubia.gomes@olos.com.br": "olos@2026",
    "eduardo.molina@olos.com.br": "olos@2026",
    "michele.silva@olos.com.br": "olos@2026",


    # Usuários restritos por cliente
    "sky": "sky123",
    "negocie_online": "negocie@2026",
    "talentos": "talentos123",
    "sky_talentos": "multi123"
}


# ===== CONTROLE DE ACESSO POR CLIENTE =====
# Use o slug do cliente, o mesmo valor usado na URL /cliente/<slug>.
USUARIO_CLIENTES = {
    "admin": ["*"],
    "gerber": ["sky-negocie-online", "talentos"],
    "elvis.santos@olos.com.br": ["sky-negocie-online", "talentos"],
    "nubia.gomes@olos.com.br": ["sky-negocie-online", "talentos"],
    "eduardo.molina@olos.com.br": ["sky-negocie-online", "talentos"],
    "michele.silva@olos.com.br": ["sky-negocie-online", "talentos"],

    "sky": ["sky-negocie-online"],
    "negocie_online": ["sky-negocie-online"],
    "talentos": ["talentos"],
    "sky_talentos": ["sky-negocie-online", "talentos"],
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
        "logo_url": ""
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
        "logo_url": ""
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
        "logo_url": ""
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
        "logo_url": ""
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
        "logo_url": ""
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
        "domain": "renac.com.br",
        "logo_url": "https://www.google.com/s2/favicons?sz=128&domain=renac.com.br"
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
        "logo_url": ""
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
        "logo_url": ""
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

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            session["usuario"] = usuario
            return redirect(url_for("dashboard"))
        erro = "Usuário ou senha inválidos"
    return render_template("login.html", erro=erro)

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", usuario=session["usuario"], clientes=clientes_permitidos(session["usuario"]))

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

    return render_template("cliente.html", usuario=session["usuario"], cliente=cliente_selecionado)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



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


def apply_tabulacao_filters(df: pd.DataFrame, date: str) -> pd.DataFrame:
    """Na aba de Tabulação, mantemos apenas filtro de data.
    Locator e Receptivo sempre aparecem lado a lado.
    """
    out = df.copy()
    if date != 'Todos':
        out = out[out['DataStr'] == date]
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
        'class_options': [],
        'selected_date': 'Todos',
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
        class_options = sorted([x for x in df['Classificacao'].dropna().unique().tolist() if str(x).strip()])
        locator_class_options = sorted([x for x in df.loc[df['Tipo'] == 'Locator', 'Classificacao'].dropna().unique().tolist() if str(x).strip()])
        receptivo_class_options = sorted([x for x in df.loc[df['Tipo'] == 'Receptivo', 'Classificacao'].dropna().unique().tolist() if str(x).strip()])

        selected_date = request.args.get('date', dates[0] if dates else 'Todos')
        selected_class = request.args.get('classificacao', 'Todos')
        selected_locator_class = request.args.get('locator_class', 'Todos')
        selected_receptivo_class = request.args.get('receptivo_class', 'Todos')

        filtered = apply_tabulacao_filters(df, selected_date)
        context.update({
            'dates': dates,
            'class_options': class_options,
            'locator_class_options': locator_class_options,
            'receptivo_class_options': receptivo_class_options,
            'selected_date': selected_date,
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
            "acordo": "Acordo",

            "hangup": "HangUp",
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
    "df": None
}

def carregar_base():
    if not SKY_ARQUIVO_BASE.exists():
        rows = []
        dias = pd.date_range("2026-05-14", periods=6, freq="D")
        ddds = [11,21,31,41,51,71,81,85,61,62,91,92,65,67,98,86,84,27,68,69,96]
        faixas = ["B.31 a 60 Dias", "C.61 a 90 Dias", "D.91 a 120 Dias", "E.Acima de 120 Dias"]
        tabs = [
            ("ADA_Aceita pagamento com desconto", "Acordo"),
            ("ADA_Ja pagou_Template", "Cpc"),
            ("ADA_Pergunta quem fala_Template", "Contato"),
            ("Announcement", "Discado"),
            ("CarrierMessage", "Discado"),
            ("NoAnswer", "Discado"),
        ]
        for d in dias:
            for hour in range(8, 18):
                for ddd in ddds:
                    for i, (tab, clas) in enumerate(tabs):
                        peso = (ddd % 9) + 1
                        disc = ([1, 2, 1, 4, 12, 3][i] + peso)
                        contato = disc if clas in ["Contato", "Cpc", "Acordo"] else 0
                        cpc = disc if clas in ["Cpc", "Acordo"] else 0
                        acordo = max(0, disc // 2) if clas == "Acordo" else 0
                        mailing = 0
                        rows.append({
                            "DATA": d,
                            "HOUR": hour,
                            "CampaignId": 202,
                            "UF_DDD": ddd,
                            "Faixa_Atraso": faixas[(ddd + hour) % len(faixas)],
                            "Tabulacao": tab,
                            "Classificado": clas,
                            "MAILING": mailing,
                            "Discado": disc,
                            "Contato": contato,
                            "Cpc": cpc,
                            "Acordo": acordo,
                            "Tempo": contato * (80 + (ddd % 7) * 15),
                            "Custo_Telecom": disc * 0.032
                        })
        return pd.DataFrame(rows)

    mtime = SKY_ARQUIVO_BASE.stat().st_mtime
    if SKY_BASE_CACHE.get("df") is not None and SKY_BASE_CACHE.get("mtime") == mtime:
        return SKY_BASE_CACHE["df"].copy()

    df = pd.read_excel(SKY_ARQUIVO_BASE)
    df = normalizar_colunas(df)

    # Fallback extra para hora quando o Excel vier com Hour/Hora.
    if "HOUR" not in df.columns:
        for col_hora in ["Hour", "hour", "Hora", "hora", "HR", "hr"]:
            if col_hora in df.columns:
                df["HOUR"] = df[col_hora]
                break

    colunas = [
        "DATA","HOUR","CampaignId","UF_DDD","Faixa_Atraso","Tabulacao","Classificado",
        "MAILING","Discado","Contato","Cpc","Acordo","Tempo","Custo_Telecom"
    ]

    for col in colunas:
        if col not in df.columns:
            df[col] = "" if col in ["Faixa_Atraso","Tabulacao","Classificado"] else 0

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df.dropna(subset=["DATA"])

    for col in ["HOUR","CampaignId","UF_DDD","MAILING","Discado","Contato","Cpc","Acordo","Tempo","Custo_Telecom"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Reduz tipos numéricos para deixar filtros/agregações mais leves.
    for col in ["HOUR","CampaignId","UF_DDD"]:
        df[col] = df[col].astype("int32")
    for col in ["MAILING","Discado","Contato","Cpc","Acordo","Tempo","Custo_Telecom"]:
        df[col] = df[col].astype("float64")

    SKY_BASE_CACHE["mtime"] = mtime
    SKY_BASE_CACHE["df"] = df.copy()

    return df.copy()

def adicionar_uf(df):
    df = df.copy()
    df["DDD_INT"] = df["UF_DDD"].astype(float).astype(int)
    df["UF"] = df["DDD_INT"].map(DDD_UF).fillna("NI")
    return df


def aplicar_filtros(df):
    datas = request.args.get("datas", "").strip()
    faixa = request.args.get("faixa", "")
    campaign_id = request.args.get("campaign_id", "")

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

    hourly = (
        base.groupby("HOUR", as_index=False)
            .agg({
                "MAILING": "max",
                "Discado": "sum",
                "Contato": "sum",
                "Cpc": "sum",
                "Acordo": "sum",
                "HangUp": "sum",
                "Tempo": "sum"
            })
            .sort_values("HOUR")
    )

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
        meta = {"dias_selecionados": 0, "data_ref": None, "tem_base": False, "valores_media_dia": {}, "mailing_max_dia": 0}

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

        daily = (
            filtro.groupby(["DATA"], as_index=False)
                .agg({
                    "MAILING": "max",
                    "Discado": "sum",
                    "Contato": "sum",
                    "Cpc": "sum",
                    "Acordo": "sum",
                })
        )

        valores = valores_zerados.copy()
        for _, col, _ in etapas_def:
            valores[col] = float(daily[col].sum()) if col in daily.columns and len(daily) else 0

        meta["dias_selecionados"] = int(daily["DATA"].dt.normalize().nunique()) if len(daily) else 0
        meta["data_ref"] = daily["DATA"].max() if len(daily) else None
        meta["tem_base"] = True
        if meta["dias_selecionados"]:
            meta["valores_media_dia"] = {k: (v / meta["dias_selecionados"]) for k, v in valores.items()}
            # Regra visão Dia: usar o maior Mailing diário dentro do período selecionado.
            if "MAILING" in daily.columns and len(daily):
                meta["mailing_max_dia"] = float(daily["MAILING"].max())
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
            # Mailing = maior Mailing diário do período selecionado.
            valores_b_view["MAILING"] = float(meta_b.get("mailing_max_dia") or valores_b_view.get("MAILING", 0))
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

    faixa_df = (
        base.groupby("Faixa_Atraso", as_index=False)
            .agg({
                "MAILING": "max",
                "Discado": "sum",
                "Contato": "sum",
                "Cpc": "sum",
                "Acordo": "sum",
                "HangUp": "sum",
                "Tempo": "sum",
            })
    )

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
    df = adicionar_uf(df)

    filtros = {
        "min_data": df["DATA"].min().strftime("%Y-%m-%d") if len(df) else "",
        "max_data": df["DATA"].max().strftime("%Y-%m-%d") if len(df) else "",
        "faixas": sorted([f for f in df["Faixa_Atraso"].dropna().astype(str).unique().tolist() if f]),
        "campaigns": sorted([str(int(c)) for c in df["CampaignId"].dropna().unique().tolist() if pd.notna(c) and float(c) != 0]) if "CampaignId" in df.columns else []
    }

    df = aplicar_filtros(df)

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
            "periodo": "-", "mapa_html": "", "ranking_uf": [], "filtros": filtros, "totais": {}, "faixa_atraso": {"cards": [], "tabela": []}, "funil_comparativo": montar_funil_comparativo_sky(df)
        }

    daily = (
        df.groupby("DATA", as_index=False)
          .agg({
              "MAILING":"max", "Discado":"sum", "Contato":"sum", "Cpc":"sum",
              "Acordo":"sum", "HangUp":"sum", "Tempo":"sum", "Custo_Telecom":"sum"
          })
          .sort_values("DATA")
    )

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
    for label, coluna, tipo in indicadores:
        linha = {"indicador": label, "valores": []}
        for _, row in daily.iterrows():
            value = row[coluna]
            if tipo == "money":
                linha["valores"].append(br_money(value))
            elif tipo == "percent":
                linha["valores"].append(br_percent(value))
            elif tipo == "decimal":
                linha["valores"].append(br_number(value, 2))
            elif tipo == "time":
                linha["valores"].append(seconds_to_hhmmss(value))
            else:
                linha["valores"].append(br_number(value))
        tabela.append(linha)

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

    uf_df = (
        df.groupby("UF", as_index=False)
          .agg({
              "MAILING":"max", "Discado":"sum", "Contato":"sum", "Cpc":"sum",
              "Acordo":"sum", "HangUp":"sum", "Tempo":"sum", "Custo_Telecom":"sum"
          })
    )
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
    hora_a_hora = montar_visao_hora_a_hora(df) if active_tab == "hora" else {"labels": [], "chart": {}, "tabela": []}

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
    df = carregar_base()
    dashboard = consolidar(df)
    return render_template('sky_negocie_online.html', dashboard=dashboard, usuario=session.get('usuario'))


@app.route('/cliente/sky-negocie-online/painel/api')
def sky_negocie_online_api():
    if 'usuario' not in session:
        return jsonify({"error": "unauthorized"}), 401
    if not usuario_pode_acessar_cliente(session.get('usuario'), 'sky-negocie-online'):
        return jsonify({"error": "forbidden"}), 403
    df = carregar_base()
    return jsonify(consolidar(df))



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
