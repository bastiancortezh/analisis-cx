# Prompt: Consolidado global cross-cliente

A partir de **todos** los `consolidado.json` de los clientes en `data/clientes/*/`, genera la vista global que alimenta `/general` y `/competencia`.

## Reglas

1. **Solo JSON** — sin texto adicional.
2. **Todo en español**.
3. Las menciones a competidores (Movilidad, Awto, Mobi, Kovi, Cabify, Uber, etc.) van en el bloque `competencia`.

## Schema

```json
{
  "snapshot": {
    "fecha_generacion": "yyyy-mm-dd",
    "total_clientes": 0,
    "total_sesiones": 0,
    "rango_temporal": {
      "desde": "yyyy-mm-dd",
      "hasta": "yyyy-mm-dd"
    }
  },
  "salud_global": {
    "puntuacion_promedio": 0,
    "distribucion_sentimiento": {
      "positivo": 0,
      "neutro": 0,
      "negativo": 0
    },
    "distribucion_riesgo_churn": {
      "alto": 0,
      "medio": 0,
      "bajo": 0
    }
  },
  "dimensiones_globales": [
    {
      "dimension": "calidad_de_servicio | tiempos_de_espera | condicion_vehicular | comunicacion | precio_y_valor",
      "puntuacion_promedio": 0,
      "tendencia": "positiva | neutra | negativa",
      "clientes_afectados": 0
    }
  ],
  "top_puntos_de_dolor": [
    {
      "descripcion": "string — patrón consolidado, no copia textual",
      "clientes_afectados": 0,
      "impacto_promedio": 0,
      "severidad_dominante": "alta | media | baja"
    }
  ],
  "patrones_emergentes": [
    {
      "patron": "string — observación cross-cliente",
      "evidencia": ["string — ejemplos breves"],
      "implicacion": "string"
    }
  ],
  "competencia": {
    "competidores_mencionados": [
      {
        "nombre": "string",
        "menciones": 0,
        "contexto_dominante": "comparacion_favorable | comparacion_desfavorable | neutro",
        "razones": ["string"]
      }
    ],
    "amenazas": ["string"],
    "oportunidades": ["string"]
  },
  "iniciativas_priorizadas": [
    {
      "titulo": "string — nombre corto de la iniciativa",
      "descripcion": "string",
      "impacto_estimado": "alto | medio | bajo",
      "esfuerzo_estimado": "alto | medio | bajo",
      "clientes_beneficiados": 0,
      "categoria": "experiencia | producto | comunicacion | precio | servicio"
    }
  ],
  "narrativa": "string — relato global de 5-7 frases sobre el estado de la base de clientes"
}
```
