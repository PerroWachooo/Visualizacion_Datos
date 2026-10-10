---
name: perfil-calidad
description: Perfila la calidad de una tabla del caso Aguas Andinas (telemetría, catálogos, tarifas, metas) según las seis dimensiones del curso, con denominadores explícitos, y produce reglas en el formato de plantilla_reglas_calidad.csv. Usar en E1 (diagnóstico), E2 (antes/después de limpiar), E3 (métricas de calidad del dashboard) y E4 (reingesta).
---

# Perfil de calidad

Objetivo: la tabla (o ruta en `datos/`) y la entrega que indique el usuario. Si no se indica tabla, usar `telemetria_horaria` (los 3 lotes). Si no se indica entrega, deducirla de la carpeta en que se trabaja (`04_Aguas_Andinas_alumnos/E<n>/`).

## Reglas que no se negocian

- **Nunca modificar `04_Aguas_Andinas_alumnos/datos/`.** Antes de empezar, correr `comun.verificar_hashes()` (en `E1/comun.py`), o en la E2+ el módulo de carga que la reemplace.
- **Todo porcentaje lleva denominador**: `filas_fallidas / filas_evaluadas`. El denominador cambia por regla. Por ejemplo, la validez de volumen se evalúa sobre filas con volumen no nulo.
- **Medir por lote** (`base`, `actualizacion`, `ampliacion`) además del total; cada lote tiene su corte y no se mezclan snapshots.
- **Una alerta no implica borrar.** En E1, `tratamiento` es una *propuesta*. En E2, el tratamiento aplicado se registra también en `plantilla_bitacora.csv`.
- **Duplicados:** separar la copia exacta (todas las columnas iguales) de la misma clave con contenido distinto. Revisar además la granularidad: un `sector_id` + `fecha` debe tener una sola lectura.
- **Ausente ≠ cero:** horas sin lectura, tarifas antes de agosto y nulos de volumen no son 0.
- **Oportunidad:** `cargado_en` − `fecha`. Nunca comparar contra la fecha actual.

## Dimensiones y controles del caso

| Dimensión | Controles mínimos en telemetría |
|---|---|
| Completitud | Nulos por campo crítico (`metadatos.json["critical"]`); horas esperadas vs. observadas (grilla sector × hora UTC) |
| Unicidad | `medicion_id` repetido (exacto vs. conflicto); `sector_id` + `fecha` repetido |
| Validez | Fechas imposibles o en formato `dd/mm/YYYY`; números con coma decimal o texto (`PENDIENTE`); `unidad_volumen` fuera de {m3, L}; `minutos_interrupcion` fuera de 0–60; volúmenes negativos; `modo_operacion` fuera de {normal, mantenimiento} tras normalizar |
| Consistencia | `volumen_salida` > `volumen_entrada`; `sector_id` ausente del catálogo; exactamente una vigencia de `sectores_historial` por hecho; tarifa única por sector y mes |
| Oportunidad | Distribución de la latencia de carga, cargas antes del evento, cargas sobre la latencia esperada (`metadatos.json["latency"]`, declarar la unidad asumida) |
| Exactitud | No es verificable sin una fuente externa: declararlo. Como proxy, volumen vs. `capacidad_m3_h` |

Para catálogos, tarifas y metas: unicidad de la clave esperada (`metadatos.json["files_originales"][*]["clave_esperada"]`), cobertura del período y solapes o huecos de vigencia.

`comun.parse_exploratorio` ya entrega flags (`_decimal_coma`, `_fecha_formato_alt`, `_fecha_invalida`, `_numero_no_parseable`, `_unidad_L`, `_unidad_desconocida`, `_dup_medicion_id`). Hay que usarlos en vez de reimplementar el parseo.

## Salida

1. Un CSV con **exactamente** las columnas de `04_Aguas_Andinas_alumnos/plantilla_reglas_calidad.csv`:
   `regla_id, tabla, campo, condicion, severidad, denominador, filas_evaluadas, filas_fallidas, tratamiento, justificacion, impacto_KPI`
   - `regla_id` es estable entre entregas (`RQ-UNI-01`, `RQ-VAL-03`…), para comparar E1 con E2 con E4.
   - `severidad`: alta, media o baja, según el impacto en la decisión (continuidad, diferencia de volúmenes, energía o confiabilidad).
   - Si se mide por lote, una fila por regla × lote (se agrega `lote` en `condicion` o en `denominador`).
   - Ruta: `E<n>/salidas/tablas/T<n>_reglas_calidad.csv`, con el prefijo de la tarea de quien lo pide. Si no está claro, preguntar.
2. En la respuesta: una tabla resumida de las reglas con más filas fallidas o mayor severidad, y 2–3 hallazgos candidatos en el formato del `E1/README.md` (Evidencia, Figura o tabla, Límite, Acción propuesta, Dimensión).

## Según la entrega

- **E1:** solo medir y proponer.
- **E2:** correr dos veces (crudo y preparado) con los mismos `regla_id` y reportar el antes/después.
- **E3:** elegir las 6 métricas de calidad del dashboard entre estas reglas, con umbral y responsable (`plantilla_fichas_indicadores.csv`).
- **E4:** reingesta. Volver a correr sobre los datos recargados y confirmar que los conteos no cambian (idempotencia).
