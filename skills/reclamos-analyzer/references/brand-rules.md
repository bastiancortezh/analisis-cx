# Brand rules — Reporte de Reclamos CX · Gama Mobility

> Subset operativo del brandbook oficial de Gama Mobility, aplicado específicamente a la generación del **reporte HTML consolidado de reclamos** (`assets/reporte-template.html`). Si entra en conflicto con el brandbook completo, el brandbook gana. Estas reglas se derivan del brandbook de `sarai-cx/CLAUDE.md` (sección "Outputs Gama-facing") y del reporte de referencia `reporte-reclamos.html`.

## Colores de marca (invariables · no cambian entre claro/oscuro)

| Token CSS       | Hex       | Rol en el reporte de reclamos                          |
|-----------------|-----------|--------------------------------------------------------|
| `--gama-red`    | `#FF3700` | Alertas, pendientes, "esta semana", acentos de portada |
| `--gama-orange` | `#FF5F00` | Urgencia alta, CTA, accent principal, barras dominantes |
| `--gama-purple` | `#870FE6` | Categóricos (tipo de reclamo), "este mes", agrupaciones |
| `--gama-green`  | `#22B260` | Estados resueltos / positivos (rara vez en reclamos)   |

Además, para **urgencia crítica** se usa `--error: #DC2626` (rojo de alerta, distinto del rojo de marca). Es el único color fuera de los 4 de marca permitido, y solo para señalizar criticidad.

## Mapeo semántico para reclamos

| Concepto del reporte        | Color                  |
|-----------------------------|------------------------|
| Urgencia **crítica**        | `--error` (#DC2626)    |
| Urgencia **alta**           | `var(--gama-orange)`   |
| Urgencia **media**          | gris (`--text-muted` / `#AAAAAA`) |
| Urgencia **baja**           | gris claro             |
| Tipo dominante (Servicio)   | `var(--gama-orange)`   |
| Tipos secundarios           | `var(--gama-purple)`, `var(--gama-red)` por orden de frecuencia |
| Sentimiento negativo        | `--error` / `--gama-red` |

## Tokens semánticos por modo

El reporte de reclamos de referencia se entrega en **modo claro** (fondo `#FAFAFA`). El atributo se fija en `<html data-theme="light">`. Tokens:

```css
[data-theme="light"] {
  --bg-page:        #FAFAFA;
  --bg-surface:     #F5F5F5;
  --bg-card:        #FFFFFF;
  --bg-hover:       #EFEFEF;
  --text-primary:   #323232;
  --text-secondary: #666666;
  --text-muted:     #999999;
  --border:         #E0E0E0;
  --border-subtle:  #EEEEEE;
  --error:          #DC2626;
}
```

> Nota: `--bg-card` es `#FFFFFF` solo para **tarjetas** sobre el fondo de página `#FAFAFA`. El fondo de página nunca es blanco puro.

## Spacing (base 4px)

`--space-xs:4px · --space-sm:8px · --space-md:16px · --space-lg:24px · --space-xl:32px · --space-2xl:48px · --space-3xl:64px`

**Nunca usar valores fuera de esta escala.**

## Radius

`--radius-sm:8px · --radius-md:12px · --radius-lg:16px (cards) · --radius-pill:9999px (badges)`

## Tipografía

- **Mont** (Bold 700) para titulares H1–H3 cuando esté disponible; fallback a **Montserrat** Bold.
- **Montserrat** (300/400/600/700) para todo lo demás. Cargada desde Google Fonts CDN.
- Tags y overlines (`.slide-tag`, `.kpi-label`): `text-transform: uppercase` + `letter-spacing: 2-3px`.

## Badges de estado (pills)

Son el mecanismo de diferenciación de urgencia/tipo. Siempre `border-radius: 9999px`, padding `3px 12px`, font 10px 600, tint 12% del color de marca:

```css
.badge        { display:inline-block; padding:3px 12px; border-radius:9999px; font-size:10px; font-weight:600; letter-spacing:0.5px; }
.badge-red    { color:var(--error);        background:rgba(239,68,68,0.12); }
.badge-orange { color:var(--gama-orange);  background:rgba(255,95,0,0.12); }
.badge-purple { color:var(--gama-purple);  background:rgba(135,15,230,0.12); }
.badge-green  { color:var(--gama-green);   background:rgba(34,178,96,0.12); }
.badge-gray   { color:var(--text-secondary); background:rgba(100,100,100,0.10); border:1px solid rgba(100,100,100,0.18); }
```

## Color strip Gama Full (obligatorio)

Strip de 12px con los 4 colores de marca al fondo de **cada slide** (es el uso principal del gradient Gama Full — sin gradientes en ningún otro lado):

```html
<div class="color-strip">
  <span style="background:#FF3700"></span>
  <span style="background:#FF5F00"></span>
  <span style="background:#870FE6"></span>
  <span style="background:#22B260"></span>
</div>
```

```css
.color-strip { position:absolute; bottom:0; left:0; right:0; height:12px; display:flex; }
.color-strip span { flex:1; }
```

## Logos

- Portada (slide cover): logo **horizontal largo** → `assets/logos/gamamobility-logo_hz-negocios-n.png` (variante para fondo claro). La variante para fondo oscuro es `*-b.png`.
- Header de cada slide interior: **icono** → `assets/logos/gamamobility-logo_ico-n.png` (claro) / `*-ico-b.png` (oscuro), altura `28px`.
- No recrear ni alterar los logos.

## Visualizaciones permitidas

- **Barras horizontales** (`.bar-row`, o divs con width en %) para distribución por tipo y por urgencia.
- **Árbol jerárquico** de 3 niveles (Tipo → Clasificación → Subclasificación) para la tipificación.
- **KPI cards** (`.kpi-card`) para totales.
- **Quote cards** y **client cards** para casos críticos y citas textuales del cliente.

## Anti-patterns explícitos (NO hacer)

| ❌ NO hacer | ✅ Sí hacer |
|---|---|
| **Pie charts**, donas, word clouds, dual-axis, 3D | Barras horizontales sólidas + KPI cards |
| Gradientes en fondos de página o en cards | Color sólido siempre; Gama Full gradient SOLO en el color strip de 12px |
| Fondo de página `#FFFFFF` | `#FAFAFA` en claro (`--bg-page`) |
| Hex hardcodeados de marca en lógica | Usar variables CSS (`var(--gama-orange)`) — los `<span>` del color strip son la única excepción literal |
| Estética "Diva" (rosa metálico, sparkles, Cinzel) | Esa estética es solo para la app interna; el reporte Gama-facing usa el brandbook |
| Badges con esquinas duras (`border-radius:3px`) | Pills `border-radius:9999px`, padding `3px 12px` |
| Inventar colores para un 4º o 5º tipo de reclamo | Reusar los 4 de marca por orden de frecuencia + grises para el resto |
| Omitir el color strip de 12px | Siempre presente al fondo de cada slide |
