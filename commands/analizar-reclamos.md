---
description: Analiza reclamos de clientes Gama Mobility desde correos y capturas (.eml, .msg, .txt e imágenes). Decodifica cada archivo, aplica la taxonomía oficial con separación de voces y genera un analisis.json más un HTML consolidado con el brandbook.
argument-hint: "[opcional] ruta de la carpeta o de los archivos de reclamos a procesar — si se omite, se escanean los adjuntos disponibles en el espacio de trabajo"
---

El usuario invocó `/analizar-reclamos`. Iniciá ahora mismo el flujo de análisis de reclamos de clientes Gama Mobility.

**Argumentos del usuario:** `$ARGUMENTS`

## Cómo proceder

1. Invocá la skill `reclamos-analyzer` (está en este mismo plugin) — ella contiene el flujo completo: ingesta de formatos (`.txt`, `.eml`, `.msg`, imágenes), normalización a texto, análisis con la taxonomía oficial de 3 niveles, separación de voces (cliente externo vs `@gamamobility.cl`), persistencia del contrato de datos y generación del HTML consolidado con el brandbook.
2. Si `$ARGUMENTS` contiene una ruta o un conjunto de archivos, usalo como input directo a procesar; si está vacío, escaneá los adjuntos disponibles en el espacio de trabajo de la usuaria antes de continuar.
3. No inventes lógica nueva ni APIs externas de IA: lo inteligente lo hace tu razonamiento y la visión para las imágenes; los scripts (`scripts/extract_email.py`) solo traducen lo que no podés leer directamente. En la primera corrida instalá las dependencias con `pip install -r scripts/requirements.txt`.
4. Persistí los resultados según el contrato de datos (`data/reclamos/<id>/analisis.json`, copia del original, actualización de `data/index.json`) y al final generá el HTML consolidado del batch desde el template embebido en la skill (`skills/reclamos-analyzer/assets/reporte-template.html`). Reportá la ruta de salida y sugerí abrirlo.

Si la skill por alguna razón no se carga, lee directamente `skills/reclamos-analyzer/SKILL.md` desde el mismo directorio del plugin y seguí esas instrucciones.
