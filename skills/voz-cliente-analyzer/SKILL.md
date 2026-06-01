---
name: voz-cliente-analyzer
description: Use whenever the user types `/analizar`, dice "analiza estos audios", "subi entrevistas", "transcribe estas entrevistas", "procesa las grabaciones de clientes", o adjunta archivos de audio/video (`.mp3`, `.mp4`, `.m4a`, `.wav`, `.webm`) de entrevistas de Customer Experience de Gama Mobility. Transcribe cada audio con Whisper local (faster-whisper, español chileno, sin APIs externas), analiza cada transcripción con la taxonomía CX (schema `analysisResultSchema`), regenera el consolidado histórico por cliente y el consolidado global cross-cliente, actualiza `data/index.json`, y genera una presentación HTML standalone marca Gama Mobility lista para presentar. Activa aunque el usuario lo diga casual ("pásame el análisis de estas grabaciones", "tengo audios nuevos de clientes"). Source of truth: Sarai's CX Engine + Gama Mobility Design System.
---

# Voz del Cliente · Analyzer (Gama Mobility)

> **Misión:** convertir audios/videos de entrevistas de clientes en análisis CX estructurado, consolidados por cliente y global, y una presentación HTML marca Gama lista para mostrar a jefatura/comité — todo **local, sin APIs externas de IA**.

Esta skill se invoca por el comando `/analizar` del plugin `gama-cx`, o cuando la usuaria adjunta audios / pide procesar entrevistas en lenguaje natural.

---

## El contrato (no-negociable)

1. **Sin APIs externas de IA.** La transcripción la hace **Whisper local** (`scripts/transcribe.py`, faster-whisper). El análisis lo hacés **vos con tu propio razonamiento** aplicando los prompts de `references/`. Nunca llames a Gemini, OpenAI ni ningún servicio de IA, ni pidas API keys.
2. **Todo el output en español** (JSONs, narrativas, descripciones, citas). Código y nombres de variables en inglés.
3. **Contrato de datos.** Los `analisis.json`, `consolidado.json` e `index.json` que produzcas deben respetar **exactamente** los schemas de `references/` (`analysisResultSchema` y los consolidados). Esa compatibilidad es lo que mantiene vivo el dashboard Next.js de `sarai-cx`. No inventes campos ni cambies nombres de claves.
4. **Cero datos reales versionados.** Audios, transcripciones y análisis son **PII de clientes reales** (Ley 21.719, Chile). Viven locales en el sandbox/máquina de la usuaria, nunca se suben al repo del plugin.
5. **Idempotencia y no-destrucción.** Nunca sobrescribas un `analisis.json` existente sin avisar primero. Los slugs deben ser estables entre corridas para no romper enlaces del dashboard.

---

## Primera corrida · dependencias

La transcripción necesita `faster-whisper` e `imageio-ffmpeg`. En la **primera ejecución** (o si Whisper falla por dependencias):

```bash
pip install -r scripts/requirements.txt
```

> **Nota:** `faster-whisper` descarga el modelo `small` (~250 MB) la **primera vez** que transcribe. Es normal que la primera corrida tarde más mientras baja el modelo; las siguientes ya lo tienen en caché. Whisper `small` necesita ~2-3 GB de RAM libres y Python 3.9+. En CPU el rendimiento es aceptable para `small`; para mejor fidelidad chilena se puede usar `--model medium` (más lento).

Si `pip install` falla, reportá el error claro a la usuaria y verificá que tenga Python 3.9+ (`python --version`).

---

## El flujo, paso por paso

### Paso 1 · Escanear los audios adjuntos

Listá los archivos de audio/video que la usuaria adjuntó al sandbox de Cowork (extensiones `.mp4`, `.mp3`, `.m4a`, `.wav`, `.webm`). Si no hay ninguno, reportá "No encontré audios para procesar" y pedile que adjunte las entrevistas.

Agrupá los audios por **cliente**. Si la usuaria los organizó en subcarpetas (una por cliente), usá el nombre de la carpeta como cliente. Si los adjuntó sueltos, preguntale a qué cliente corresponde cada uno (o, si el nombre del archivo lo deja claro, proponé el mapeo y pedí confirmación).

### Paso 2 · Procesar cada cliente

Para cada cliente:

**a) Calcular el slug**
Convertí el nombre del cliente a slug: minúsculas, sin tildes/ñ, espacios → guiones, sin caracteres especiales. Ejemplos:
- `NOW SPA` → `now-spa`
- `Mövil 2000 S.A.` → `movil-2000-sa`

El slug debe ser **estable** (no cambiar entre corridas) para no romper enlaces del dashboard.

**b) Crear el cliente si es nuevo**
Si `data/clientes/<slug>/` no existe:
- Creá la carpeta y `data/clientes/<slug>/sesiones/`.
- Generá `data/clientes/<slug>/perfil.json`:
  ```json
  {
    "slug": "<slug>",
    "nombre": "<nombre original tal como vino el cliente>",
    "fecha_alta": "<hoy en yyyy-mm-dd>",
    "segmento": null,
    "notas": null
  }
  ```

**c) Procesar cada audio del cliente**
Para cada archivo `.mp4|.mp3|.m4a|.wav|.webm` del cliente:

1. **Determinar la fecha-slug de la sesión**:
   - Si el filename empieza con `yyyy-mm-dd-`, usá ese prefijo.
   - Si no, usá la fecha de modificación del archivo + slug del resto del nombre.
   - Ejemplo: `2026-02-12-conversacion.mp4` → `2026-02-12-conversacion`.

2. **Crear `data/clientes/<slug>/sesiones/<fecha-slug>/`** y mover/copiar el audio adentro como `audio.<extensión>`.

3. **Transcribir** ejecutando:
   ```bash
   python scripts/transcribe.py "data/clientes/<slug>/sesiones/<fecha-slug>/audio.<ext>" --output "data/clientes/<slug>/sesiones/<fecha-slug>/transcripcion.txt"
   ```
   > Si Whisper falla por dependencias, corré primero `pip install -r scripts/requirements.txt` (ver sección "Primera corrida") y reintentá. El script ya viene configurado para español chileno con prompt de contexto Gama Mobility — no lo modifiques.

4. **Analizar el transcript**:
   - Leé `transcripcion.txt` y `references/analisis-cx.md`.
   - Aplicá el prompt al transcript usando **tu propio razonamiento** (no llames APIs externas).
   - Generá el JSON estructurado siguiendo el **schema exacto** (`analysisResultSchema`): `resumen`, `sentimiento_general`, `temas_clave`, `puntos_de_dolor[]`, `citas_relevantes[]`, `recomendaciones[]`, `sentimiento_detallado`.
   - Las **citas textuales** deben ser literales del cliente, copiadas de la transcripción.
   - Guardá en `data/clientes/<slug>/sesiones/<fecha-slug>/analisis.json`.
   - Si un transcript es muy corto (<100 caracteres) o está vacío, **saltá el análisis** y reportá el problema (audio inaudible o vacío).

### Paso 3 · Re-generar consolidado por cliente

Para cada cliente que tuvo sesiones nuevas (o si nunca se generó):

- Leé `references/consolidado-cliente.md`.
- Leé **todas** las `analisis.json` del cliente (`data/clientes/<slug>/sesiones/*/analisis.json`), ordenadas cronológicamente por fecha de sesión.
- Generá el consolidado histórico siguiendo el schema (`salud_actual`, `evolucion_dimensional`, `puntos_de_dolor_persistentes`, `temas_recurrentes`, `logros_y_mejoras`, `acciones_recomendadas`, `narrativa`).
- Guardá en `data/clientes/<slug>/consolidado.json`.

### Paso 4 · Re-generar consolidado global

- Leé `references/consolidado-global.md`.
- Leé **todos** los `data/clientes/*/consolidado.json` y `data/clientes/*/perfil.json`.
- Generá la vista global cross-cliente (`snapshot`, `salud_global`, `dimensiones_globales`, `top_puntos_de_dolor`, `patrones_emergentes`, `competencia`, `iniciativas_priorizadas`, `narrativa`). Las menciones a competidores (Movilidad, Awto, Mobi, Kovi, Cabify, Uber, etc.) van en el bloque `competencia`.
- Guardá en `data/global/consolidado.json`.

### Paso 5 · Actualizar `data/index.json`

Regenerá el índice maestro:
```json
{
  "actualizado": "<timestamp ISO>",
  "clientes": [
    {
      "slug": "<slug>",
      "nombre": "<nombre>",
      "total_sesiones": 0,
      "ultima_sesion": "yyyy-mm-dd",
      "sentimiento_actual": "positivo | neutro | negativo",
      "riesgo_churn": "alto | medio | bajo"
    }
  ],
  "totales": {
    "clientes": 0,
    "sesiones": 0
  }
}
```

### Paso 6 · Generar la presentación HTML (brandbook Gama)

Generá **un solo archivo HTML standalone** (doble clic, sin servidor) usando `assets/presentacion-template.html`. Leé el template cada vez antes de generar (puede haber sido actualizado).

1. **Determinar el alcance** con la usuaria (o inferirlo de su request):
   - Status actual de un cliente → `data/clientes/<slug>/consolidado.json`
   - Status global de toda la base → `data/global/consolidado.json`
   - Evolución histórica de un cliente → `data/clientes/<slug>/sesiones/*/analisis.json` ordenado cronológicamente
   - Comparativo entre clientes → múltiples `data/clientes/*/consolidado.json`
2. **Sustituir los marcadores `{{...}}`** del template con los datos del alcance elegido (cover, TL;DR, KPI cards de dimensiones, slides de pain points, citas, acciones).
3. **Guardar** en `data/presentaciones/<yyyy-mm-dd>-<scope-slug>.html`. Ejemplo: `data/presentaciones/2026-06-01-status-now-spa.html`.
4. **Reglas brandbook (no-negociables):**
   - Slides 1280×720, padding 64px.
   - Color strip Gama Full (12px, `#FF3700` / `#FF5F00` / `#870FE6` / `#22B260`) al fondo de cada slide — siempre presente.
   - Tipografía: Mont (H1-H3) + Montserrat (body). Montserrat desde Google Fonts.
   - Logo header con swap claro/oscuro (variantes `*.png` light / `*-NN.png` dark) desde `assets/logos/`. No rotar, estirar ni recolorear el logo.
   - KPI cards: border-radius 16px, **sin** `border-left` coloreado, cada KPI con delta/contexto.
   - Badges (pills): `border-radius: 9999px`, tint 12% del color. Mapeo CX: sentimiento positivo / riesgo bajo / tendencia mejorando → verde; neutro / medio / estable → naranja o púrpura; negativo / alto / deteriorando → rojo.
   - ❌ Prohibido: pie charts, word clouds, dual-axis, eje Y que no parta en 0, 3D, gradientes en fondos extensos, estética Diva (rosa metálico), `#FFFFFF` como bg de página (usar `#FAFAFA` light / `#0A0A0A` dark).
   - Charts (si se necesitan): SVG inline, bar charts para comparar, line charts para evolución, stacked bars para distribución. Sin librerías externas.
   - Si no hay suficientes datos para una sección, **no la incluyas** (mejor menos slides bien hechos).

### Paso 7 · Reportar a la usuaria

Imprimí un resumen claro:
- Cuántas sesiones nuevas se procesaron y cuántos clientes nuevos se crearon.
- Qué consolidados se regeneraron.
- Ruta del HTML de presentación generado, y cómo abrirlo: `start data/presentaciones/<nombre>.html` (Windows) / `open ...` (Mac).
- Errores (si hubo) con instrucciones de qué hacer.

---

## Reglas críticas

- **NUNCA** restaures Gemini, OpenAI ni ninguna API externa de IA. Toda la inteligencia es tu razonamiento local + Whisper local.
- **NUNCA** sobrescribas un `analisis.json` existente sin avisar a la usuaria primero. Para re-analizar una sesión, borrá su `analisis.json` y volvé a correr `/analizar`.
- **NUNCA** dejes un audio sin procesar a medias: o se transcribe y analiza completo, o se reporta el error.
- Si un transcript es muy corto (<100 caracteres) o vacío, saltá el análisis y reportá el problema.
- Todo el output (JSONs, narrativas, descripciones, citas) **en español**. Slugs estables entre corridas.
- Idioma: español neutro/chileno. Tuteo (`puedes`, `tienes`, `mira`), nunca voseo argentino.

---

## Antipatrones (no hagas esto)

| Antipatrón | Por qué no |
|---|---|
| Llamar a una API de IA para transcribir o analizar | Regla dura heredada de sarai-cx: todo es local. Whisper transcribe, vos analizás. |
| Inventar campos o renombrar claves del JSON | Rompe el contrato de datos; el dashboard Next.js deja de leer los archivos. |
| Sobrescribir un `analisis.json` existente sin avisar | Se pierde trabajo y trazabilidad. Avisá primero. |
| Cambiar el slug de un cliente entre corridas | Rompe los enlaces del dashboard. Los slugs son estables. |
| Pie charts, gradientes de fondo o estética Diva en la presentación | Brandbook Gama lo prohíbe para outputs corporativos. |
| Versionar audios, transcripciones o análisis en el repo | Es PII de clientes reales (Ley 21.719). Solo vive local. |
| Modificar `scripts/transcribe.py` para cambiar idioma o modelo por defecto | Está calibrado para español chileno + contexto Gama. Usá `--model` por CLI si hace falta. |

---

## Archivos del skill

- `scripts/transcribe.py` — Transcripción local con faster-whisper (español chileno, prompt Gama). Portado tal cual de sarai-cx.
- `scripts/requirements.txt` — `faster-whisper`, `imageio-ffmpeg`. Instalar en primera corrida.
- `references/analisis-cx.md` — Prompt + schema `analysisResultSchema` para el análisis por sesión.
- `references/consolidado-cliente.md` — Prompt + schema del consolidado histórico por cliente.
- `references/consolidado-global.md` — Prompt + schema del consolidado global cross-cliente.
- `assets/presentacion-template.html` — Template HTML brandbook con marcadores `{{...}}`. Léelo cada vez antes de generar.
- `assets/logos/` — Logos Gama Mobility en variantes claro/oscuro. No alterar.
