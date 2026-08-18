OPCIONAL - VIDEO DE TRANSICAO KOVI

A versao atual usa a animacao leve HTML/CSS/SVG.
Para trocar futuramente por um video IA:
1. Salve o arquivo como static/video/kovi_transition.webm (recomendado, sem audio).
2. No template dashboard.html, altere data-video-url="" para:
   data-video-url="{{ url_for('static', filename='video/kovi_transition.webm') }}"
3. O JavaScript tentara reproduzir o video e, se houver erro, voltara automaticamente para a animacao leve.

Recomendacao: 1,2 a 1,8 s, 1920x1080 ou 1280x720, bitrate baixo/moderado, sem audio, movimento lateral do carro.
