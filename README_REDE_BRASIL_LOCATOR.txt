REDE BRASIL - LOCATOR INTEGRADO AO OSP DATA COMMAND CENTER

Base:
  data/base_rede_brasil.xlsx

Abas esperadas:
  - Locator
  - Comparativo

Ajustes desta versão:
  - Removido o quadro Ranking de campanhas comparativas.
  - Incluído Consolidado do dia - Hora a hora da campanha espelho selecionada.
  - Novos cálculos no consolidado:
      CPC / Logados
      Acordo / Logados
      Acordo / Mailing
  - Linha TOTAL DIA usando Logados médios e Mailing máximo do período.
  - Quadro Comparativo com campanha espelho limitado aos indicadores:
      Mailing
      Tentativas
      Atendidas
      CPC
      Acordo
  - Para equivalência do Locator:
      CPC = Transferencia
      Acordo = Sucesso_Negocio

O consolidado hora a hora respeita Data e Campanha Comparativa selecionadas,
mas permanece com todas as horas mesmo quando o filtro geral Hora é utilizado.
