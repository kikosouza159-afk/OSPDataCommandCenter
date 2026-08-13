SKY - VISÃO UNIQUE COM ABERTURA
===============================

Na aba Unique da Base_Dashboard_Sky.xlsx, adicionar a coluna:

Abertura

Valores esperados:
- Unique Dia
- Unique Mes

Estrutura sugerida:
DATA | Abertura | Mailing | Discado | Contato | Cpc | Acordo | Valor_Acordo | Penetracao | Alo | Loc | Conversao

Regra aplicada no painel Daily:
1. Nenhuma data selecionada: usa somente linhas Abertura = Unique Mes.
2. Exatamente uma data selecionada: usa somente Abertura = Unique Dia e a data selecionada.
3. Duas ou mais datas selecionadas: usa somente linhas Abertura = Unique Mes.
4. O filtro de Mês continua sendo respeitado.

Observação:
O sistema aceita o valor "Unique Mês" com acento também, mas o padrão solicitado é "Unique Mes".
