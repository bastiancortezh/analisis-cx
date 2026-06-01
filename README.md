# gama-cx — Plugin Claude · Análisis CX Gama Mobility

Plugin de Claude para analizar la **Experiencia del Cliente (CX)** de Gama Mobility, sin servidores ni APIs externas de IA. Todo corre **local** en tu Cowork, con tus propios datos. Dos comandos `/`, dos flujos:

| Comando | Para qué sirve | Qué le entregás |
|---|---|---|
| **`/analizar-reclamos`** | Analiza reclamos de clientes: clasifica con la taxonomía oficial, separa la voz del cliente de la del equipo Gama, marca urgencia y dimensiones CX, y arma un **reporte HTML consolidado** con la marca. | Correos (`.eml`, `.msg`, `.txt`) e **imágenes** (capturas de correos o chats). |
| **`/analizar`** | Analiza la **voz del cliente** en audio/video: transcribe con Whisper local (en español chileno), analiza el CX, consolida por cliente y global, y arma una **presentación HTML** con la marca. | Audios o videos (`.mp3`, `.mp4`, `.m4a`, `.wav`). |

Lo **inteligente** lo hace Claude (leer las imágenes, analizar, redactar el HTML). Los scripts solo **traducen** lo que Claude no puede leer solo: el audio a texto, y los correos `.msg` de Outlook a texto.

---

## Qué genera

- Un **HTML standalone** con el brandbook Gama aplicado: se abre con doble clic, sin servidor, listo para compartir con jefatura, comité o el cliente.
- Archivos `analisis.json` por cada ítem analizado (correo o audio), guardados en una carpeta `data/` **local** en tu Cowork. Estos JSON son el "contrato de datos": un dashboard opcional (repo `sarai-cx`) puede leerlos para explorarlos, pero **no** son necesarios para usar el plugin.

---

## Instalación (para una usuaria no-dev)

> El plugin se instala desde un **marketplace de GitHub** dentro de Cowork. No necesitás clonar nada ni saber programar. Lo hacés **una vez** y queda disponible.

### Paso 1 · Conectar GitHub a Cowork (una sola vez)

1. Abrí Cowork.
2. Andá a **Settings → Connectors → GitHub**.
3. Apretá **Autorizar** y seguí el login de GitHub.
4. Asegurate de que el repo `bastiancortezh/analisis-cx` quede visible para la conexión. Si no lo ves, pedile a DEV que te dé acceso.

### Paso 2 · Agregar el plugin como complemento personal

1. En Cowork, andá a **Settings → Complementos personales** (o **Plugins**, según la versión).
2. Apretá **Agregar marketplace** / **Add plugin source** y pegá esta URL:
   ```
   https://github.com/bastiancortezh/analisis-cx
   ```
3. Cowork detecta el plugin **gama-cx** automáticamente. Apretá **Instalar** (toggle ON).

### Paso 3 · Probar

En una sesión nueva de Cowork, escribí `/analizar-reclamos` o `/analizar`. Si el comando aparece, ya está instalado.

> **Actualizaciones:** cuando DEV publique una versión nueva, la vas a ver en la misma pantalla de Complementos personales. Apretás actualizar y listo.

---

## Primera corrida — instalación de dependencias Python

La primera vez que uses cada comando, el plugin necesita instalar unas librerías de Python en tu Cowork. **Esto es automático**: la skill corre el `pip install` por vos. Solo tené en cuenta:

- **`/analizar-reclamos`**: instala una librería liviana para leer correos `.msg` de Outlook (`extract-msg`). Es rápido.
- **`/analizar`**: instala Whisper local (`faster-whisper`). La **primera vez** descarga el modelo de transcripción (~250 MB), así que esa corrida inicial puede tardar varios minutos. Las siguientes son mucho más rápidas porque el modelo ya queda en caché.

Si la instalación falla, la skill te avisa con un mensaje claro. En general basta con reintentar el comando.

---

## Privacidad y cumplimiento (importante)

- Los correos de reclamo y los audios son **datos personales de clientes reales** (PII). Quedan cubiertos por la **Ley 21.719** de protección de datos personales de Chile.
- Esos datos viven **solo en tu Cowork / tu máquina**, en la carpeta `data/` local. **Nunca** se suben al repositorio ni se comparten con servicios externos.
- El plugin **no usa APIs externas de IA**: todo el análisis y la transcripción ocurren localmente.
- El repositorio `analisis-cx` lleva **solo código, plantillas y logos**. **Cero datos reales de clientes.** El `.gitignore` está configurado para excluir cualquier `data/` real.
- Cada usuaria trabaja con sus propios datos, de forma independiente y sin sincronización entre cuentas.

> En resumen: lo sensible se queda contigo. El repo solo guarda la herramienta, no la información de los clientes.

---

## Requisitos

- **Claude Cowork** (o Claude Code) con soporte de plugins.
- Acceso al repo `bastiancortezh/analisis-cx` en GitHub.
- Cowork ejecuta Python y bash en su sandbox, por eso Whisper local y la lectura de `.msg` funcionan sin instalar nada en tu computador.

---

## Autoría

Plugin desarrollado para Gama Mobility · DEV team. Brandbook por Vicente Araos (2026).
Documento confidencial de Gama Mobility — prohibida su reproducción sin autorización.
