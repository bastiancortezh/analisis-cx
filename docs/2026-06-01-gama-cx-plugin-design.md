# Spec — Plugin `gama-cx` (Análisis CX Gama Mobility)

**Fecha:** 2026-06-01 · **Autor:** Gama Mobility — DEV · **Estado:** Diseño aprobado, en implementación

## 1. Propósito

Un **plugin de Claude** (modelo Cowork/marketplace, distribuido por GitHub) que entrega el análisis de Customer Experience de Gama Mobility a **2 usuarias no-dev** (colegas de Vicente Araos), cada una trabajando de forma independiente con sus propios datos locales.

Reemplaza el modelo "clonar repo + correr Claude Code" por **instalar un plugin** desde un marketplace de GitHub (igual que `gama-gantt`). Cada usuaria lo instala en su Cowork y lo invoca con comandos `/`.

## 2. Contexto y origen

- **Fuente de verdad a portar:** `github.com/bastiancortezh/sarai-cx` (Next.js + Whisper Python + comandos Claude). Se **portan las piezas probadas**, no se clona el repo completo.
- **Patrón de plugin a calcar:** `github.com/bastiancortezh/gama-gantt` (estructura `.claude-plugin/` + `commands/` + `skills/`).
- **Hecho habilitante:** Claude Cowork es una VM Linux en sandbox sobre la máquina de la usuaria; **ejecuta Python y bash**. Las skills con scripts corren en Cowork (y Claude Code), no en el chat web. Por eso Whisper local y la decodificación de `.msg` son viables.

## 3. Alcance

Un plugin, **dos skills / dos comandos**:

| Comando | Skill | Inputs | Qué hace |
|---|---|---|---|
| `/analizar-reclamos` | `reclamos-analyzer` | `.eml`, `.msg`, `.txt`, **imágenes** (capturas de correos/chats) adjuntas | Decodifica → analiza con taxonomía oficial + separación de voces → `analisis.json` + HTML consolidado |
| `/analizar` | `voz-cliente-analyzer` | audio/video (`.mp3`, `.mp4`, `.m4a`, `.wav`) | Transcribe con Whisper local → analiza CX → `analisis.json` + consolidados + HTML presentación |

**Fuera de alcance (por ahora):** `.pst` (buzón completo Outlook) — futuro, se suma al mismo `extract_email.py`. Conector Outlook/Gmail — no se usa; el input son archivos adjuntos.

## 4. Principio rector

Lo **inteligente** lo hace Claude (análisis, lectura de imágenes por visión, generación de HTML). Los **scripts solo traducen** lo que Claude no puede leer solo:
- audio → `transcribe.py` (faster-whisper)
- `.msg` binario → `extract_email.py` (librería `extract-msg`)

**Sin APIs externas de IA** (regla dura heredada de sarai-cx). Todo el output en español; código/variables en inglés.

## 5. Estructura del repo

```
gama-cx/
├── .claude-plugin/
│   ├── plugin.json          # name: gama-cx, version, description, author, license
│   └── marketplace.json     # source github → bastiancortezh/analisis-cx
├── commands/
│   ├── analizar-reclamos.md # fino → invoca reclamos-analyzer
│   └── analizar.md          # fino → invoca voz-cliente-analyzer
├── skills/
│   ├── reclamos-analyzer/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── extract_email.py     # .eml (stdlib email) + .msg (extract-msg)
│   │   │   └── requirements.txt     # extract-msg
│   │   ├── references/
│   │   │   ├── analisis-reclamos.md     # portado de sarai-cx/prompts/
│   │   │   ├── taxonomia-reclamos.json  # portado tal cual
│   │   │   └── brand-rules.md           # subset brandbook para HTML
│   │   └── assets/
│   │       ├── reporte-template.html    # portado de reporte-reclamos.html
│   │       └── logos/                    # PNGs Gama necesarios
│   └── voz-cliente-analyzer/
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── transcribe.py            # portado de transcripcion/transcribe.py
│       │   └── requirements.txt         # faster-whisper, imageio-ffmpeg
│       ├── references/
│       │   ├── analisis-cx.md           # portado
│       │   ├── consolidado-cliente.md   # portado
│       │   └── consolidado-global.md    # portado
│       └── assets/
│           ├── presentacion-template.html
│           └── logos/
├── README.md
└── .gitignore                # CERO datos reales de clientes
```

## 6. Las skills en detalle

### 6.1 `reclamos-analyzer` (`/analizar-reclamos`)

Porta la lógica de `.claude/commands/analizar-reclamos.md` + `prompts/analisis-reclamos.md` + `taxonomia-reclamos.json`. Cambio real respecto a sarai-cx: **ingesta robusta de formatos**.

Flujo:
1. **Recolectar inputs** adjuntos por la usuaria (en el sandbox de Cowork).
2. **Normalizar a texto** por archivo:
   - `.txt` → tal cual.
   - `.eml` → `extract_email.py` (parse MIME, cuerpo en texto plano, decodifica quoted-printable/base64).
   - `.msg` → `extract_email.py` (librería `extract-msg`, extrae remitente, asunto, cuerpo).
   - imágenes (`.png`/`.jpg`/`.jpeg`) → Claude las lee con **visión** y transcribe el texto del reclamo.
3. **Analizar** cada correo con tu razonamiento (no APIs): separación de voces (cliente externo vs `@gamamobility.cl`), taxonomía oficial 3 niveles, urgencia, dimensiones CX, múltiples reclamos por correo. Schema `reclamoAnalysisResultSchema`.
4. **Persistir**: `data/reclamos/<id>/analisis.json` + copia del original. Actualizar `data/index.json` (sección reclamos).
5. **HTML consolidado** del batch usando `assets/reporte-template.html` (brandbook). Reporta ruta y sugiere abrirlo.

Primera corrida: la skill instala deps con `pip install -r scripts/requirements.txt`.

### 6.2 `voz-cliente-analyzer` (`/analizar`)

Porta `.claude/commands/analizar.md` + `transcribe.py` + `prompts/analisis-cx.md` + consolidados. Sin cambios de lógica respecto a sarai-cx (ya está bien); solo se reempaqueta como skill.

Flujo: escanear audios adjuntos → `transcribe.py` (faster-whisper, español chileno, prompt Gama) → analizar con `analisis-cx.md` (schema `analysisResultSchema`) → consolidado por cliente y global → `data/clientes/<slug>/...` + `data/global/` + `data/index.json` → HTML presentación (`presentacion-template.html`).

Primera corrida: `pip install -r scripts/requirements.txt` (faster-whisper descarga modelo ~250 MB la primera vez).

## 7. Resultados / visores ("ambos")

- **HTML standalone** (brandbook, doble clic, sin servidor): lo genera cada skill desde su template. Para compartir fuera de la pantalla (jefatura/comité/cliente).
- **Dashboard Next.js** (repo `sarai-cx`, aparte y opcional): lee los mismos `data/*.json`. El plugin **escribe el contrato de datos** (mismos schemas que `src/lib/validation.ts`); el dashboard solo visualiza. El plugin queda esbelto; el dashboard sigue disponible para quien quiera explorar local.

**Contrato de datos (crítico):** los `analisis.json`, `consolidado.json` e `index.json` que produce el plugin deben pasar los schemas Zod de `sarai-cx/src/lib/validation.ts`. Esa compatibilidad es lo que mantiene vivo el dashboard.

## 8. Privacidad y cumplimiento

- El repo `gama-cx` lleva **solo código, plantillas y logos**. **Cero datos reales de clientes.**
- Los correos de reclamo y audios son **PII de clientes reales** (Ley 21.719 de datos personales, Chile). Viven **locales** en el sandbox/máquina de cada usuaria, nunca en el repo.
- `.gitignore` excluye cualquier `data/` real. (Nota: en `sarai-cx`, `data/reclamos/` quedó versionado con correos reales — error de privacidad que NO se replica aquí.)

## 9. Distribución para 2 personas

1. Se publica `gama-cx` en GitHub (privado).
2. `marketplace.json` apunta al repo.
3. Cada usuaria agrega el marketplace y **instala el plugin** desde la UI de Cowork (Complementos personales).
4. Cada una trabaja con sus propios datos locales. Independientes, sin sincronización.
5. Actualizaciones: se publica nueva versión en GitHub; cada usuaria actualiza desde la UI.

## 10. Criterios de aceptación

- [ ] El plugin instala desde el marketplace de GitHub y aparece como complemento personal.
- [ ] `/analizar-reclamos` procesa `.txt`, `.eml`, `.msg` e imágenes, y genera HTML consolidado brandbook.
- [ ] `.msg` se decodifica correctamente (no como texto plano basura).
- [ ] `/analizar` transcribe audio con Whisper local y genera presentación brandbook.
- [ ] Los JSON producidos pasan los schemas Zod de sarai-cx (dashboard los lee sin error).
- [ ] El repo no contiene ningún dato real de clientes.
- [ ] README explica instalación, uso y setup de deps para una usuaria no-dev.

## 11. Riesgos / a validar en implementación

- **Puente sandbox↔host de archivos**: confirmar cómo llegan los adjuntos al sandbox y cómo salen los HTML/JSON al disco de la usuaria (y al dashboard).
- **Rendimiento de Whisper** en el sandbox Linux (CPU): aceptable para `small`; documentar expectativa de tiempos.
- **Instalación de deps** en el sandbox en primera corrida: debe ser idempotente y con mensaje claro si falla.
- **`extract-msg`** con hilos complejos / adjuntos anidados: validar con `.msg` reales de Gama.
