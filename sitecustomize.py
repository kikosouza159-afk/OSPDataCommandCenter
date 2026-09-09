"""Compatibilidade do filtro Carteira para o painel SKY.

Este módulo é carregado automaticamente pelo Python na inicialização. Ele mantém
os arquivos monolíticos atuais intactos e adiciona o filtro Carteira à SKY sem
alterar o comportamento existente do filtro Faixa.

Regras:
- Prechurn: clientes em faixas de atraso até 90 dias.
- Churn: clientes em faixas acima de 90 dias.
"""

from __future__ import annotations

import re
import unicodedata


def _normalizar_texto(valor) -> str:
    texto = "" if valor is None else str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.strip().lower()


def _eh_prechurn_faixa(valor) -> bool:
    texto = _normalizar_texto(valor)
    if not texto or texto in {"nan", "none", "sem faixa"}:
        return False

    numeros = [int(n) for n in re.findall(r"\d+", texto)]
    if not numeros:
        return False

    # Qualquer faixa explicitamente acima de um limite >= 90 pertence ao Churn.
    if "acima" in texto or "+" in texto:
        return max(numeros) < 90

    return max(numeros) <= 90


def _eh_churn_faixa(valor) -> bool:
    texto = _normalizar_texto(valor)
    if not texto or texto in {"nan", "none", "sem faixa"}:
        return False

    numeros = [int(n) for n in re.findall(r"\d+", texto)]
    if not numeros:
        return False

    if "acima" in texto or "+" in texto:
        return max(numeros) >= 90

    return max(numeros) > 90


def _instalar_patch_request_args():
    """Converte Carteira em um marcador interno quando Faixa não foi escolhida."""
    try:
        from werkzeug.datastructures import ImmutableMultiDict
    except Exception:
        return

    if getattr(ImmutableMultiDict.get, "_sky_carteira_patch", False):
        return

    original_get = ImmutableMultiDict.get

    def get_com_carteira(self, key, default=None, type=None):
        if key == "faixa":
            faixa_atual = original_get(self, "faixa", default="", type=None)
            carteira = original_get(self, "carteira", default="", type=None)
            if not faixa_atual:
                carteira_norm = _normalizar_texto(carteira)
                if carteira_norm == "prechurn":
                    faixa_atual = "__SKY_PRECHURN__"
                elif carteira_norm == "churn":
                    faixa_atual = "__SKY_CHURN__"

            if type is not None and faixa_atual is not None:
                try:
                    return type(faixa_atual)
                except (ValueError, TypeError):
                    return default
            return faixa_atual if faixa_atual is not None else default

        return original_get(self, key, default=default, type=type)

    get_com_carteira._sky_carteira_patch = True
    ImmutableMultiDict.get = get_com_carteira


def _instalar_patch_faixa_pandas():
    """Faz o marcador interno funcionar no filtro exato já usado por aplicar_filtros."""
    try:
        import pandas as pd
    except Exception:
        return

    if getattr(pd.Series.__eq__, "_sky_carteira_patch", False):
        return

    original_eq = pd.Series.__eq__

    def eq_com_carteira(self, other):
        if getattr(self, "name", None) == "Faixa_Atraso" and other in {
            "__SKY_PRECHURN__",
            "__SKY_CHURN__",
        }:
            regra = _eh_prechurn_faixa if other == "__SKY_PRECHURN__" else _eh_churn_faixa
            return self.astype(str).map(regra)
        return original_eq(self, other)

    eq_com_carteira._sky_carteira_patch = True
    pd.Series.__eq__ = eq_com_carteira


def _instalar_patch_template_sky():
    """Inclui o select Carteira no filtro global e o preserva no Funil."""
    try:
        import flask
    except Exception:
        return

    if getattr(flask.render_template, "_sky_carteira_patch", False):
        return

    original_render_template = flask.render_template

    def render_template_com_carteira(template_name_or_list, *args, **kwargs):
        html = original_render_template(template_name_or_list, *args, **kwargs)

        template_name = (
            template_name_or_list
            if isinstance(template_name_or_list, str)
            else " ".join(str(x) for x in template_name_or_list)
        )
        if "sky_negocie_online.html" not in template_name or not isinstance(html, str):
            return html

        try:
            carteira = flask.request.args.get("carteira", "")
        except Exception:
            carteira = ""
        carteira_norm = _normalizar_texto(carteira)

        pre_selected = " selected" if carteira_norm == "prechurn" else ""
        churn_selected = " selected" if carteira_norm == "churn" else ""

        campo_carteira = f"""
        <div class=\"field\">
          <label>Carteira</label>
          <select name=\"carteira\" id=\"filtro-carteira-sky\">
            <option value=\"\">Todas</option>
            <option value=\"Prechurn\"{pre_selected}>Prechurn</option>
            <option value=\"Churn\"{churn_selected}>Churn</option>
          </select>
        </div>
        """

        # Insere ao lado do campo Faixa, antes do botão Aplicar filtros.
        alvo_botao = '<div class="field">\n          <button type="submit">Aplicar filtros</button>\n        </div>'
        if 'id="filtro-carteira-sky"' not in html and alvo_botao in html:
            html = html.replace(alvo_botao, campo_carteira + alvo_botao, 1)

        # Preserva a Carteira ao aplicar o filtro específico do Funil Comparativo.
        if 'class="panel funil-filter-panel"' in html:
            valor_hidden = carteira if carteira_norm in {"prechurn", "churn"} else ""
            hidden = f'<input type="hidden" name="carteira" value="{valor_hidden}">'
            marcador_form = '<form class="panel funil-filter-panel" method="get">'
            trecho_inicial_funil = html.split(marcador_form, 1)[1][:500] if marcador_form in html else ""
            if 'name="carteira"' not in trecho_inicial_funil:
                html = html.replace(marcador_form, marcador_form + "\n          " + hidden, 1)

        # O filtro passa de 4 para 5 campos: Mês, Datas, Faixa, Carteira e Aplicar.
        # O card ocupa toda a largura disponível para manter o botão dentro do painel.
        css = """
        <style id=\"sky-carteira-filter-style\">
          .filters.filters-compact {
            width: 100% !important;
            max-width: 100% !important;
            padding: 14px 16px !important;
            overflow: visible !important;
          }
          .filters.filters-compact .filter-grid {
            display: grid !important;
            grid-template-columns: minmax(180px,1fr) minmax(220px,1.2fr) minmax(180px,.9fr) minmax(150px,.8fr) minmax(170px,.9fr) !important;
            gap: 12px !important;
            align-items: end !important;
          }
          .filters.filters-compact .field {
            min-width: 0 !important;
            width: 100% !important;
          }
          .filters.filters-compact .field.dates {
            width: 100% !important;
            min-width: 0 !important;
          }
          .filters.filters-compact .field input,
          .filters.filters-compact .field select,
          .filters.filters-compact .field button {
            height: 42px !important;
            min-height: 42px !important;
            width: 100% !important;
            box-sizing: border-box !important;
            margin: 0 !important;
          }
          .filters.filters-compact .field button {
            margin-top: 20px !important;
            border-radius: 14px !important;
          }
          @media (max-width: 1100px) {
            .filters.filters-compact .filter-grid {
              grid-template-columns: repeat(2,minmax(0,1fr)) !important;
            }
            .filters.filters-compact .field button {
              margin-top: 0 !important;
            }
          }
          @media (max-width: 860px) {
            .filters.filters-compact .filter-grid {
              grid-template-columns: 1fr !important;
            }
          }
        </style>
        """
        if 'id="sky-carteira-filter-style"' not in html:
            html = html.replace("</head>", css + "\n</head>", 1)

        return html

    render_template_com_carteira._sky_carteira_patch = True
    flask.render_template = render_template_com_carteira


_instalar_patch_request_args()
_instalar_patch_faixa_pandas()
_instalar_patch_template_sky()
