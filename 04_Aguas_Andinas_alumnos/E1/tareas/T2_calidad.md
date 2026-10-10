# T2: Calidad de la telemetría

**Responsable:** ____________
**Cubre:** IL1.2 (estructura, ausencias, duplicados, calidad) y prepara IL5.2 para la E2–E3
**Notebook:** `E1/T2_calidad.ipynb`
**Skill de apoyo:** `/perfil-calidad telemetria_horaria` (Claude Code) o `$perfil-calidad telemetria_horaria` (Codex)

## Objetivo

Medir, **por lote y con denominador explícito**, qué tan confiables son las 253.404 filas de telemetría. Hay que evaluar unicidad, validez, completitud, oportunidad y consistencia entre campos de la misma fila, y proponer un tratamiento para la E2 **sin limpiar todavía**.

## Insumos

- `comun.cargar_lotes()` devuelve los datos crudos como strings.
- `comun.parse_exploratorio()` devuelve los datos tipados con flags:
  - `_decimal_coma`, `_fecha_formato_alt`, `_cargado_en_formato_alt`;
  - `_fecha_invalida`, `_numero_no_parseable`;
  - `_unidad_L`, `_unidad_desconocida`;
  - `_dup_medicion_id`.
- Las reglas esperadas están en [diccionario_datos.csv](../../diccionario_datos.csv) y en el [README del caso](../../README.md) (sección "Contrato"). No hace falta esperar el diccionario de T1.
- Las seis dimensiones de calidad están en la lámina 15 de la clase 01.

## Pistas detectadas al preparar la estructura

Hay que **verificar, cuantificar por lote y explicar** cada una:

| Dimensión | Pista |
|---|---|
| Estructura | Filas, columnas, tipos y rango de `fecha` por lote. ¿Coinciden con `metadatos.json`? |
| Unicidad | `medicion_id` repetido en base y actualización (ampliación no tiene). ¿Son copias exactas o claves con valores en conflicto? |
| Validez | Coma decimal en números de ampliación |
| Validez | Fechas `dd/mm/YYYY HH:MM:SS` en ampliación |
| Validez | Fechas **imposibles** (p. ej. `2025-02-30`) en los 3 lotes |
| Validez | `volumen_entrada` con texto (`PENDIENTE`) |
| Validez | `unidad_volumen` fuera de {m3, L} |
| Validez | `minutos_interrupcion` fuera de 0–60 |
| Validez | `volumen_entrada` negativo |
| Validez | `modo_operacion` con variantes de mayúsculas y espacios |
| Completitud | Nulos en `volumen_entrada`. ¿En qué lotes, sectores o meses se concentran? |
| Consistencia | `volumen_salida` > `volumen_entrada` en la misma fila |
| Oportunidad | Latencia `cargado_en` − `fecha`: distribución, casos negativos (carga antes del evento) y casos sobre lo esperado. `metadatos.json` declara `"latency": 2`; hay que justificar en qué unidad se interpreta. |

## Pasos sugeridos

1. Perfil de estructura por lote: `shape`, tipos, rango de fechas, `value_counts` de categóricas.
2. Una regla de calidad por cada pista. Para cada regla: `filas_evaluadas` (el **denominador**, que puede variar), `filas_fallidas` y `%`.
3. Separar los duplicados: copia exacta (todas las columnas iguales) vs. misma clave con distinto contenido.
4. Definir la severidad (alta, media o baja) según el impacto en la decisión. Por ejemplo, un volumen negativo afecta la diferencia de volúmenes y un `modo_operacion` mal escrito afecta los filtros.
5. Una figura: % de filas fallidas por regla y lote (barras horizontales desde 0). Usar `/grafico-diagnostico`.

## Entregables

- `E1/T2_calidad.ipynb`
- `E1/salidas/tablas/T2_reglas_calidad.csv`, con las mismas columnas que [plantilla_reglas_calidad.csv](../../plantilla_reglas_calidad.csv): `regla_id, tabla, campo, condicion, severidad, denominador, filas_evaluadas, filas_fallidas, tratamiento, justificacion, impacto_KPI`. El `tratamiento` es una **propuesta** para la E2.
- `E1/salidas/figuras/T2_*.png`, cada figura con 2–4 líneas de interpretación en el notebook.

## Terminado cuando

- [ ] Todas las pistas tienen una regla con cifras por lote.
- [ ] Cada % tiene su denominador escrito.
- [ ] El CSV respeta las columnas de la plantilla, porque se reutiliza en la E2.
- [ ] 2–3 hallazgos candidatos escritos abajo.

## No hacer

- No borrar, deduplicar ni imputar: eso es la E2. Aquí solo se mide y se propone.
- No calcular cobertura de horas ni cruzar con catálogos (T3).
- No comparar `cargado_en` con la fecha de hoy.

## Hallazgos candidatos

<!-- Usar el formato del README: H<n>, Evidencia, Figura o tabla, Límite, Acción propuesta, Dimensión -->
