---
description: Analiza la voz del cliente Gama Mobility desde audio o video (.mp3, .mp4, .m4a, .wav). Transcribe con Whisper local (español chileno), analiza la experiencia CX y genera analisis.json, consolidados por cliente y global, más un HTML de presentación con el brandbook.
argument-hint: "[opcional] ruta de la carpeta o de los archivos de audio/video a procesar — si se omite, se escanean los adjuntos disponibles en el espacio de trabajo"
---

El usuario invocó `/analizar`. Iniciá ahora mismo el flujo de análisis de voz del cliente Gama Mobility.

**Argumentos del usuario:** `$ARGUMENTS`

## Cómo proceder

1. Invocá la skill `voz-cliente-analyzer` (está en este mismo plugin) — ella contiene el flujo completo: escaneo de audios/videos, transcripción con Whisper local (faster-whisper, español chileno, prompt Gama), análisis CX, consolidado por cliente y global, persistencia del contrato de datos y generación del HTML de presentación con el brandbook.
2. Si `$ARGUMENTS` contiene una ruta o un conjunto de archivos, usalo como input directo a procesar; si está vacío, escaneá los adjuntos de audio/video disponibles en el espacio de trabajo de la usuaria antes de continuar.
3. No inventes lógica nueva ni APIs externas de IA: la transcripción la hace `scripts/transcribe.py` localmente y el análisis lo hace tu razonamiento. En la primera corrida instalá las dependencias con `pip install -r scripts/requirements.txt` (faster-whisper descarga el modelo ~250 MB la primera vez).
4. Persistí los resultados según el contrato de datos (`data/clientes/<slug>/...`, `data/global/`, actualización de `data/index.json`) y al final generá el HTML de presentación desde el template embebido en la skill (`skills/voz-cliente-analyzer/assets/presentacion-template.html`). Reportá la ruta de salida y sugerí abrirlo.

Si la skill por alguna razón no se carga, lee directamente `skills/voz-cliente-analyzer/SKILL.md` desde el mismo directorio del plugin y seguí esas instrucciones.
