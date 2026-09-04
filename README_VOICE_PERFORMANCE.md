# Voice Performance no OSP Data Command Center

Integração do **Voice Performance Cockpit** como um novo cliente do menu executivo do OSP Data Command Center.

## Como executar

O entry point histórico foi preservado. Não é necessário trocar o comando do projeto.

Local:

```bash
pip install -r requirements.txt
python app.py
```

Render / Gunicorn:

```bash
gunicorn app:app
```

O `app.py` agora funciona como uma camada fina de integração e carrega o Cockpit original de `core_app.py`. Assim o código do Cockpit existente permanece preservado, enquanto o Voice Performance é registrado no mesmo Flask.

A integração mantém:

- login e sessão existentes;
- menu executivo de clientes;
- transição OLOS ao abrir e voltar do cliente;
- controle de acesso por usuário;
- demais clientes e rotas atuais;
- mesmo comando de inicialização do projeto.

## Rotas

- `/cliente/voice-performance`
- `/cliente/voice-performance/painel`
- `/cliente/voice-performance/painel/api/filters`
- `/cliente/voice-performance/painel/api/data`
- `/cliente/voice-performance/painel/api/refresh`

## Banco PostgreSQL

As credenciais não ficam no repositório. Configure no ambiente:

```env
PGHOST=seu_host
PGPORT=5432
PGDATABASE=postgres
PGUSER=seu_usuario
PGPASSWORD=sua_senha
PGSSLMODE=require
APP_TIMEZONE=America/Sao_Paulo
```

O painel consulta o PostgreSQL somente quando o usuário clica em **Carregar / Atualizar data**. A navegação normal utiliza o cache SQLite em `data/voice_performance_cache.db`.

## Regras dos dados

- Horário convertido explicitamente para `America/Sao_Paulo`.
- Antes de `03/09/2026`, tenant e campanha entram como `CONSOLIDADO`.
- Sucesso é calculado a partir de `score_sum`:

```sql
CASE
    WHEN COALESCE(score_sum, 0) > 0 THEN score_sum
    ELSE 0
END
```

- Taxa de sucesso = `SUM(sucessos) / SUM(feedbacks) * 100`.

## Identidade do cliente

O card **Voice Performance** usa o logo oficial solicitado:

`https://www.olos.com.br/wp-content/uploads/2022/12/logo-olos-laranja.png`
