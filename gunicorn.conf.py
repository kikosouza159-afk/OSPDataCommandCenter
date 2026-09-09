"""Configuração do Gunicorn para o OSP Data Command Center.

Garante que as extensões de compatibilidade do cockpit sejam carregadas antes
do módulo Flask principal. Em especial, ativa o filtro Carteira da SKY no
ambiente de produção (Render/gunicorn), sem depender do carregamento implícito
do sitecustomize pelo interpretador.
"""

# Import explícito e intencional. O módulo é idempotente e aplica os patches
# antes de `app.py` importar `render_template` e antes de receber requisições.
import sitecustomize  # noqa: F401
