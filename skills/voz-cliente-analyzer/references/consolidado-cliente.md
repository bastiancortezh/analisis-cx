# Prompt: Consolidado histórico por cliente

A partir de **todas** las `analisis.json` de un cliente (ordenadas cronológicamente por `fecha_sesion`), genera un consolidado histórico que resume la trayectoria del cliente.

## Reglas

1. **Solo JSON** — sin texto adicional, sin markdown.
2. **Todo en español**.
3. La **tendencia** se calcula comparando las primeras vs. las últimas sesiones (¿mejora, empeora, se mantiene?).

## Schema

```json
{
  "cliente": {
    "slug": "string",
    "nombre": "string",
    "total_sesiones": 0,
    "primera_sesion": "yyyy-mm-dd",
    "ultima_sesion": "yyyy-mm-dd"
  },
  "salud_actual": {
    "sentimiento": "positivo | neutro | negativo",
    "puntuacion_global": 0,
    "tendencia": "mejorando | estable | deteriorando",
    "riesgo_churn": "alto | medio | bajo"
  },
  "evolucion_dimensional": [
    {
      "dimension": "calidad_de_servicio | tiempos_de_espera | condicion_vehicular | comunicacion | precio_y_valor",
      "puntuacion_inicial": 0,
      "puntuacion_actual": 0,
      "delta": 0,
      "tendencia": "positiva | neutra | negativa"
    }
  ],
  "puntos_de_dolor_persistentes": [
    {
      "descripcion": "string",
      "veces_mencionado": 0,
      "impacto_promedio": 0,
      "primera_aparicion": "yyyy-mm-dd",
      "estado": "abierto | resuelto | recurrente"
    }
  ],
  "temas_recurrentes": [
    { "tema": "string", "frecuencia": 0 }
  ],
  "logros_y_mejoras": ["string — cosas que mejoraron entre sesiones"],
  "acciones_recomendadas": [
    {
      "accion": "string",
      "prioridad": "alta | media | baja",
      "justificacion": "string"
    }
  ],
  "narrativa": "string — resumen de 4-5 frases de la trayectoria del cliente con Gama"
}
```

## Cálculo del riesgo de churn

- **Alto**: sentimiento negativo + tendencia deteriorando, o múltiples puntos de dolor de severidad alta sin resolver.
- **Medio**: sentimiento neutro con dolores persistentes, o positivo con tendencia deteriorando.
- **Bajo**: sentimiento positivo + tendencia estable o mejorando.
