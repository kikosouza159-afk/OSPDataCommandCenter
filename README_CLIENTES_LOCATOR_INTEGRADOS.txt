CLIENTES LOCATOR INTEGRADOS
============================

Painel compartilhado com visões Comparativo, Daily consolidado e Hora a hora.
Cada cliente possui leitura isolada em data/<arquivo>.

- MILLENNIUM: data/base_millennium.xlsx | rota /cliente/millennium/painel
- NW ADVOGADOS: data/base_nw_advogados.xlsx | rota /cliente/nw-advogados/painel
- RENAC: data/base_renac.xlsx | rota /cliente/renac/painel
- SETRA: data/base_setra.xlsx | rota /cliente/setra/painel
- SYSCOB: data/base_syscob.xlsx | rota /cliente/syscob/painel
- FERREIRA & CHAGAS: data/base_ferreira_chagas.xlsx | rota /cliente/ferreira-e-chagas/painel
- CREDITAS: data/base_creditas.xlsx | rota /cliente/creditas/painel
- ARANHA FERREIRA: data/base_aranha_ferreira.xlsx | rota /cliente/aranha-e-ferreira/painel

Regra %Abandono Daily: média das horas válidas da coluna %Abandono já calculada na base.
Regra de alerta: %Perda ou %Abandono acima de 5% ativa efeito visual piscante.