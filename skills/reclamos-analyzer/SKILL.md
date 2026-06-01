---
name: reclamos-analyzer
description: Úsala cuando la usuaria escribe `/analizar-reclamos`, dice "analiza estos reclamos", "procesa estos correos", "tengo correos de reclamo", "clasifica estas quejas de clientes", o adjunta archivos de reclamos en formato `.txt`, `.eml`, `.msg` o imágenes (`.png`/`.jpg`/`.jpeg` — capturas de correos o chats de reclamo). Decodifica cada formato a texto (los `.eml`/`.msg` con `scripts/extract_email.py`, las imágenes leyéndolas por visión), analiza cada correo con la taxonomía oficial Gama Mobility de 3 niveles + separación de voces cliente-externo vs `@gamamobility.cl` + urgencia + dimensiones CX, persiste `data/reclamos/<id>/analisis.json` y actualiza `data/index.json`, y genera un reporte HTML consolidado marca Gama (brandbook) listo para presentar. Actívate aunque lo pida de forma casual ("revisa estos reclamos que me llegaron", "métele a estos correos"). Sin APIs externas de IA — todo el análisis lo haces tú. Fuente de verdad de marca: Gama Mobility Design System.
---

# Reclamos Analyzer · Gama Mobility

> **Misión:** convertir un lote de correos de reclamo de clientes (en cualquier formato: texto, `.eml`, `.msg` o captura de pantalla) en análisis estructurado con la taxonomía oficial de Gama Mobility, persistido como `analisis.json`, y un reporte HTML consolidado marca Gama listo para mostrar a jefatura, comité o cliente.

Esta skill se invoca por el comando `/analizar-reclamos` del mismo plugin, o cuando la usuaria pide algo equivalente en lenguaje natural y/o adjunta archivos de reclamos.

---

## Principio rector

Lo **inteligente** lo haces **tú** (Claude): la lectura de imágenes por visión, el análisis, la clasificación según taxonomía, la separación de voces y la generación del HTML. Los **scripts solo traducen** lo que no puedes leer solo: el binario `.msg` y el MIME del `.eml` → `scripts/extract_email.py`.

**Sin APIs externas de IA** (regla dura heredada de sarai-cx: nunca Gemini, OpenAI ni similares, nunca pedir API keys). Todo el output en español; código y nombres de variables en inglés.

---

## El contrato (no-negociable)

1. **Ingesta robusta de formatos.** Acepta `.txt`, `.eml`, `.msg` e imágenes. Cada formato se normaliza a texto antes de analizar. Un `.msg` **nunca** se trata como texto plano basura — se decodifica con la librería `extract-msg`.
2. **Separación de voces SIEMPRE.** Ninguna frase de un correo `@gamamobility.cl` puede aparecer como `cita` del cliente. Las citas son palabras del cliente externo, copiadas textualmente. Ver `references/analisis-reclamos.md`.
3. **Taxonomía oficial 3 niveles.** Tipo → Clasificación → Subclasificación, usando **exclusivamente** los valores de `references/taxonomia-reclamos.json`. Si nada calza exacto, elige lo más cercano y nótalo en el `resumen`.
4. **El JSON debe pasar el schema** `reclamoAnalysisResultSchema` (definido en `references/analisis-reclamos.md`, compatible con `sarai-cx/src/lib/validation.ts`). Forma: `{ cliente_identificado, sentimiento_general, resumen_general, reclamos: [...] }`.
5. **Cero datos reales en el repo.** Los correos y los `analisis.json` son **PII de clientes reales** (Ley 21.719, Chile). Viven locales en el sandbox/máquina de la usuaria, **nunca** se commitean al repo del plugin.
6. **HTML marca Gama.** El reporte consolidado sigue el brandbook — ver `references/brand-rules.md` — usando `assets/reporte-template.html` como base estructural.

---

## El flujo, paso por paso

### Paso 0 · Setup de dependencias (solo primera corrida)

Si vas a procesar algún `.msg`, la librería `extract-msg` debe estar instalada. En la **primera corrida** (o si `extract_email.py` falla con error de dependencia), corre:

```bash
pip install -r scripts/requirements.txt
```

Debe ser idempotente: si ya está instalada, no pasa nada. Si falla, repórtalo con mensaje claro (verifica Python 3.9+). Si el lote no tiene `.msg`, este paso es opcional.

### Paso 1 · Recolectar inputs

Reúne los archivos de reclamos que la usuaria adjuntó o dejó en el directorio de trabajo del sandbox. Acepta:

- **Texto:** `.txt`
- **Correo MIME:** `.eml`
- **Correo Outlook binario:** `.msg`
- **Imágenes:** `.png`, `.jpg`, `.jpeg` (capturas de correos o de chats de reclamo)

Si no hay nada que procesar, repórtalo ("No encontré reclamos para analizar") y termina. Si un archivo no es ninguno de estos formatos, sáltalo y avísalo.

### Paso 2 · Normalizar a texto (por formato)

Para cada archivo, obtén su contenido como texto limpio según su tipo:

| Formato | Cómo normalizarlo |
|---|---|
| `.txt` | Léelo tal cual con `Read`. |
| `.eml` | `python scripts/extract_email.py "<ruta>"` → imprime headers (From/To/Cc/Subject/Date) + cuerpo en texto plano (decodifica quoted-printable/base64, prioriza `text/plain` y limpia `text/html`). |
| `.msg` | `python scripts/extract_email.py "<ruta>"` → usa la librería `extract-msg` para extraer remitente, destinatarios, asunto, fecha y cuerpo. |
| `.png` / `.jpg` / `.jpeg` | **Léela tú con visión** (`Read` sobre la imagen). Transcribe el texto del reclamo que ves: quién escribe (remitente/dominio si aparece), a quién, y el cuerpo de la queja. Esa transcripción es el "correo" que luego analizas. |

> El script imprime a stdout; opcionalmente acepta `--output <archivo>`. Para análisis directo, captura su stdout. Si `extract_email.py` falla por falta de `extract-msg`, vuelve al Paso 0.

### Paso 3 · Calcular el ID y guardar el original

Para cada correo normalizado:

**a) ID del reclamo** (estable entre corridas — no cambia si el mismo archivo reaparece):
- Si el filename empieza con `yyyy-mm-dd-`, usa ese prefijo.
- Si no, usa la fecha de hoy + slug del filename (minúsculas, sin tildes/ñ, espacios → guiones, sin caracteres especiales).
- Ejemplos: `2026-05-18-empresa-abc.eml` → `2026-05-18-empresa-abc` · `reclamo taller sucio.png` → `2026-06-01-reclamo-taller-sucio`.

**b) Carpeta + copia del original:**
- Crea `data/reclamos/<id>/`.
- Guarda el texto normalizado en `data/reclamos/<id>/email.txt` y conserva una copia del archivo original (`.eml`/`.msg`/imagen) en la misma carpeta.

### Paso 4 · Analizar cada correo (con tu razonamiento — sin APIs)

1. Lee `references/analisis-reclamos.md` (prompt + reglas + separación de voces + schema + criterios de urgencia y dimensiones).
2. Lee `references/taxonomia-reclamos.json` para verificar que cada `tipo_reclamo` / `clasificacion` / `subclasificacion` es un valor válido.
3. Aplica el análisis. Presta especial atención a:
   - **Separación de voces:** distingue la voz del cliente externo de la voz interna `@gamamobility.cl`. Las citas y puntos de dolor salen **solo** del cliente externo; lo interno es solo contexto (urgencia percibida, recomendaciones).
   - **Múltiples reclamos por correo:** un correo puede tener más de un problema diferenciado → un objeto por reclamo en el array `reclamos`. No inventes reclamos que no existen.
   - **Urgencia:** `critica` / `alta` / `media` / `baja` según los criterios del reference.
   - **Dimensiones CX:** usa las 5 dimensiones (`calidad_de_servicio`, `tiempos_de_espera`, `condicion_vehicular`, `comunicacion`, `precio_y_valor`) — mismas que las entrevistas, para habilitar análisis cruzado.
   - **Emociones:** detecta las emociones del cliente externo según la taxonomía de 8 (`frustracion`, `enojo`, `indignacion`, `decepcion`, `preocupacion`, `impotencia`, `desconfianza`, `resignacion`), cada una con `intensidad` 0-100 y `cita` textual; fija `emocion_dominante` (la de mayor intensidad). Solo de la voz del cliente. Úsala como insumo para la `urgencia` (ver `references/analisis-reclamos.md`).
4. Valida mentalmente contra `reclamoAnalysisResultSchema`. Guarda el resultado en `data/reclamos/<id>/analisis.json`.

### Paso 5 · Actualizar `data/index.json`

Lee el `data/index.json` existente (si no existe, créalo) y agrega/actualiza la sección de reclamos:

```json
{
  "actualizado": "<timestamp ISO>",
  "clientes": [],
  "totales": {
    "clientes": 0,
    "sesiones": 0,
    "reclamos": 0,
    "reclamos_criticos": 0,
    "reclamos_pendientes": 0
  },
  "reclamos_resumen": {
    "ultima_fecha": "yyyy-mm-dd",
    "por_urgencia": { "critica": 0, "alta": 0, "media": 0, "baja": 0 },
    "por_tipo": {
      "servicio": 0, "entrega_nueva": 0, "entrega_spot": 0,
      "atencion_personal": 0, "ti": 0, "facturacion": 0, "cobranza": 0
    }
  }
}
```

Para los conteos, lee **todos** los `data/reclamos/*/analisis.json` (no solo los recién procesados). Cada archivo tiene un array `reclamos[]` — cuenta los **elementos individuales** (suma de `reclamos.length`), no el número de correos. `por_urgencia` y `por_tipo` se calculan por reclamo individual.

### Paso 6 · Generar el HTML consolidado

Lee `assets/reporte-template.html` (puede haber sido actualizado — léelo cada vez). Es un deck brandbook con marcadores `{{...}}` para la portada y el resumen ejecutivo, y un marcador `{{SLIDES}}` donde inyectas los slides de contenido.

1. Reemplaza los marcadores de portada/resumen: `{{TOTAL_RECLAMOS}}`, `{{TOTAL_CLIENTES}}`, `{{TOTAL_CRITICOS}}`, `{{PCT_PENDIENTES}}`, `{{PERIODO}}`, `{{FECHA}}`, los badges de urgencia, tipo dominante, sentimiento global y la cita de alerta crítica (cita textual del cliente, no de Gama).
2. Genera los slides de contenido siguiendo `references/brand-rules.md` e inyéctalos en `{{SLIDES}}` (sugeridos: distribución por tipo/urgencia, **mapa emocional del batch** —distribución de emociones dominantes con intensidad promedio, barras horizontales—, tipificación 3 niveles, ranking de clientes, casos de mayor riesgo, patrones sistémicos, acciones prioritarias). En los slides de detalle por reclamo, muestra la `emocion_dominante` como chip con su intensidad. Cada slide es `<div class="slide" id="slide-N"> … <div class="color-strip">…</div> </div>`.
3. Ajusta `{{TOTAL_SLIDES}}` al número total de slides.
4. Escribe el HTML en `data/reclamos/` (o donde la usuaria prefiera) y **reporta la ruta absoluta**, sugiriendo abrirlo con doble clic.

### Paso 7 · Reportar al usuario

Imprime un resumen claro:
- Cuántos reclamos nuevos procesados y de qué formatos venían.
- IDs generados y cliente identificado en cada uno.
- Destaca con ⚠ los de urgencia `critica` o `alta`.
- Tipo de reclamo más frecuente del batch.
- Ruta absoluta del HTML generado.

---

## Reglas críticas

- **NUNCA** sobrescribas un `analisis.json` existente sin avisar primero.
- Los **IDs son estables** entre corridas (no cambian si el mismo archivo reaparece).
- Si el contenido es muy corto (<50 caracteres) o claramente no es un reclamo, repórtalo y sáltalo.
- Todo el output (JSONs, narrativas, HTML) **en español**. Código en inglés.
- **Nunca** commitees `data/` real al repo del plugin: son PII de clientes.
- Los puntos de dolor y dimensiones deben ser **comparables** con los de las entrevistas (skill `voz-cliente-analyzer`) — mismos criterios, misma escala — para el análisis cruzado.

---

## Antipatrones (no hagas esto)

| Antipatrón | Por qué no |
|---|---|
| Tratar un `.msg` como texto plano | Sale basura binaria. Usa `extract_email.py` (librería `extract-msg`). |
| Pedir una API key o restaurar Gemini/OpenAI | Regla dura: toda la inteligencia es Claude local. Sin APIs externas de IA. |
| Citar una frase `@gamamobility.cl` como voz del cliente | Rompe la separación de voces. Las citas son del cliente externo, textuales. |
| Inventar una `subclasificacion` que no está en la taxonomía | Usa solo los valores de `taxonomia-reclamos.json`; si nada calza, lo más cercano + nota. |
| Contar correos en vez de reclamos individuales en `index.json` | Un correo puede tener varios reclamos. Cuenta elementos de `reclamos[]`. |
| Pie charts, donas, gradientes en fondos, estética Diva (rosa metálico) | Prohibido por brandbook. Barras sólidas + KPI cards + color strip de 12px. |
| Commitear correos o `analisis.json` reales al repo | Son PII (Ley 21.719). Viven locales, nunca en el repo del plugin. |
| Generar el HTML sin reemplazar todos los `{{...}}` | Quedan marcadores visibles. Sustituye todos antes de escribir. |

---

## Archivos del skill

- `scripts/extract_email.py` — CLI Python: `.eml` (stdlib `email`) + `.msg` (librería `extract-msg`) → texto limpio a stdout (o `--output`).
- `scripts/requirements.txt` — dependencia `extract-msg` (instalar en primera corrida).
- `references/analisis-reclamos.md` — Prompt completo: reglas, separación de voces, taxonomía textual, criterios de urgencia, dimensiones CX y schema `reclamoAnalysisResultSchema`. Léelo cada análisis.
- `references/taxonomia-reclamos.json` — Taxonomía oficial Gama Mobility de 3 niveles (fuente de verdad para clasificar).
- `references/brand-rules.md` — Subset del brandbook aplicado al reporte de reclamos: colores, tipografía, badges, color strip, antipatrones.
- `assets/reporte-template.html` — Template HTML brandbook con marcadores `{{...}}`. Funciona con doble clic, sin servidor. Léelo cada vez antes de generar.
- `assets/logos/` — Logos Gama Mobility: horizontal largo (`gamamobility-logo_hz-negocios-n.png` claro / `-b.png` oscuro) e icono (`gamamobility-logo_ico-n.png` claro / `-b.png` oscuro). No recrear ni alterar.
