"""Compatibilidade com o entry point integrado.

O projeto principal continua disponível em `app:app`. Este módulo apenas
reexporta o mesmo objeto Flask para ambientes que tenham sido configurados
temporariamente com `osp_app:app` durante a integração.
"""

from app import app


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
