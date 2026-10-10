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

## Clasificación de cada problema

El Word de la E1 exige distinguir:
- **`defecto`:** incumple el contrato. Ejemplos: unidad desconocida, fecha imposible, salida > entrada, minutos > 60, clave repetida.
- **`extremo_plausible`:** raro pero posible; se marca y no se borra.
- **`ausencia_estructural`:** falta por diseño. Ejemplos: tarifas antes de agosto, metas fuera del período.

Las horas sin lectura en la grilla **no son** ausencia estructural por defecto: pueden ocultar fallas y hay que justificarlo.

Además, estimar **qué KPI se sesgan más y en qué dirección** (`impacto_KPI`).

## Salida

1. **`perfil_calidad.csv`**, perfil por lote y segmento, con las columnas:
   `lote, segmento_tipo, segmento_valor, campo, filas, nulos, pct_nulos, distintos, invalidos, pct_invalidos, min, p50, max`
   - `segmento_tipo` ∈ {total, sector, mes, modo_operacion}.
2. **`matriz_reglas.csv`**, con las columnas de `04_Aguas_Andinas_alumnos/plantilla_reglas_calidad.csv` y luego `lote, clasificacion`:
   `regla_id, tabla, campo, condicion, severidad, denominador, filas_evaluadas, filas_fallidas, tratamiento, justificacion, impacto_KPI, lote, clasificacion`
   - `regla_id` es estable entre entregas (`RQ-UNI-01`, `RQ-VAL-03`…), para comparar E1 con E2 con E4.
   - `severidad`: alta, media o baja, según el impacto en la decisión (continuidad, diferencia de volúmenes, energía o confiabilidad).
   - Una fila por regla × lote.
   - `tratamiento` alimenta el plan de limpieza del diagnóstico.
3. Rutas: en la E1, `E1/salidas/tablas/perfil_calidad.csv` y `E1/salidas/tablas/matriz_reglas.csv`, que son productos del Word con nombre exacto. En otras entregas, seguir lo que diga su Word o README; si no está claro, preguntar.
4. En la respuesta: una tabla resumida de las reglas con más filas fallidas o mayor severidad, y 2–3 hallazgos candidatos en el formato de `E1/README.md` (Observación, Gráfico o tabla, Período · unidad · población, Hipótesis, Decisión o acción, Limitación, Dimensión).

## Según la entrega

- **E1:** solo medir y proponer. Las 6 métricas de calidad preliminares salen de estas reglas (skill `ficha-indicador`).
- **E2:** correr dos veces (crudo y preparado) con los mismos `regla_id` y reportar el antes/después.
- **E3:** cerrar las 6 métricas de calidad del dashboard, con umbral y responsable (skill `ficha-indicador`).
- **E4:** reingesta. Volver a correr sobre los datos recargados y confirmar que los conteos no cambian (idempotencia).
