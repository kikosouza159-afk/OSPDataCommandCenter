============================================================
FUNIL 2 COMPARATIVO | CLIENTES LOCATOR
============================================================

Cada base Locator possui agora duas sheets:

1) Sheet1
   Base do Locator + transferência para operação humana.
   Mantém o layout já utilizado pelo painel Daily e Hora a Hora.

2) Funil_2
   Base da campanha humana / ativa usada no lado B do comparativo.

Cabeçalho obrigatório da sheet Funil_2:
DATA | NomeCampanha | Logados | Tentativas | Atendidas | Cpc | Sucesso_Negocio | HitRate | Loc | Conver | TMA_ATH

Regras do Funil 2:
- Logados: média diária caso existam múltiplas linhas da mesma campanha/data.
- Tentativas: soma.
- Atendidas: soma.
- CPC: soma.
- Sucesso_Negocio: soma.
- Hit Rate: Atendidas / Tentativas.
- Loc: CPC / Atendidas.
- Conversão: Sucesso_Negocio / CPC.
- TMA ATH: média ponderada por Atendidas.

Funil A | Locator:
Mailing -> Tentativas -> Atendidas -> Transferências -> Atend. humano -> Sucesso negócio

Funil B | Humano / campanha ativa:
Logados -> Tentativas -> Atendidas -> CPC -> Sucesso negócio

As conversões aparecem dentro das etapas dos dois funis.

Observação:
O projeto aceita também o nome Comparativo ou a segunda sheet do arquivo,
mas o nome recomendado é Funil_2.

ATUALIZAÇÃO V6 - CARDS COMPARATIVOS
A aba Comparativo agora exibe cards espelhados Locator x Campanha -1 para:
- Tentativas
- Atendidas
- Transferência / CPC
- Sucesso de negócio
- Sucesso de interação / % Loc
- % Sucesso de negócio
