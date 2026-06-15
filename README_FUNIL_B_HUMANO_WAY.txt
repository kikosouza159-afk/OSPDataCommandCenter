COCKPIT LOCATOR | ESTRUTURA DAS SHEETS COMPARATIVAS
===================================================

A estrutura comparativa agora é separada por tipo de jornada.

1) Sheet1
   Base principal do Locator usada no Funil A, Daily e Hora a Hora.

2) Funil_2
   Usada exclusivamente quando o filtro Tipo Funil B = Humano/AD.

   Cabeçalho recomendado:
   Data | NomeCampanha | Mailing | Logados | Tentativas | Atendidas | Cpc | Sucesso_Negocio | HitRate | Loc | Conver | TMA_ATH

   Funil exibido:
   Mailing > Tentativas > Atendidas > CPC > Acordo

3) Funil_3
   Usada exclusivamente quando o filtro Tipo Funil B = Way.

   Cabeçalho recomendado:
   Data | NomeCampanha | Mailing | AD | ATH | Tentativas | Atendidas | Transferencia | Atend_ATH | Sucesso_Negocio | TMA_LOCATOR | TMA_ATH | HitRate | SucessoInteracao | Perda | %Perda | Abandono | %Abandono | SLA | Custo

   Funil exibido:
   Mailing > Tentativas > Atendidas > Transferencias > Atend. humano > Sucesso negocio

Observacoes:
- No modo Way, a coluna Hora nao e necessaria. O comparativo consolida os dados por periodo.
- No modo Way, os campos Perda, %Perda, Abandono, %Abandono, SLA e Custo podem ficar vazios quando nao estiverem disponiveis.
- O painel cria valores padrao para campos opcionais ausentes para evitar erro de carregamento.
- Os periodos do Funil A e Funil B continuam independentes.
