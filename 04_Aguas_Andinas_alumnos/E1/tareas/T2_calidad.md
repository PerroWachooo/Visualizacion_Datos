# T2: Calidad, métricas de calidad y ranking de inspección

**Responsable:** ____________
**Ítems del Word:** W5, W6 (6 métricas de calidad), S1, S2, P4 · **Rúbrica:** "Calidad y pertinencia" (30 pts)
**Notebook de trabajo:** `E1/T2_calidad.ipynb`
**Productos:** `salidas/tablas/perfil_calidad.csv`, `salidas/tablas/matriz_reglas.csv`, `salidas/tablas/T2_fichas_calidad.csv`, `salidas/tablas/T2_por_sector.csv`, `salidas/tablas/T2_ranking.csv`
**Skills:** `/perfil-calidad`, `/ficha-indicador` (Codex: `$perfil-calidad`, `$ficha-indicador`)

## Objetivo

1. Medir, **por lote y por segmento**, qué tan confiables son las 253.404 filas de telemetría, clasificando cada problema y estimando qué indicadores quedarían más sesgados.
2. Proponer las **6 métricas de calidad**.
3. En la fase 2 (desde el D-5), construir el **ranking de las 3 inspecciones** (P4) con las tablas por sector de T2, T3 y T4.

## Insumos

- `comun.parse_exploratorio(comun.cargar_lotes())`, con flags:
  - `_decimal_coma`, `_fecha_formato_alt`;
  - `_fecha_invalida`, `_numero_no_parseable`;
  - `_unidad_L`, `_unidad_desconocida`;
  - `_dup_medicion_id`.
  Las columnas originales quedan como `*_raw`.
- Reglas esperadas: [diccionario_datos.csv](../../diccionario_datos.csv) y la sección "Contrato" del [README del caso](../../README.md). No hace falta esperar los contratos de T1; después se alinea el texto.
- Las seis dimensiones de calidad están en la lámina 15 de la clase 01.

## Parte A: perfil y matriz de reglas (W5, S1, S2)

Pistas detectadas al preparar la estructura. Hay que **verificar, cuantificar por lote y segmento y clasificar** cada una:

| Dimensión | Pista |
|---|---|
| Estructura | Filas, columnas, tipos y rango de `fecha` por lote. ¿Coinciden con `metadatos.json`? |
| Unicidad | `medicion_id` repetido en base y actualización. ¿Copia exacta o clave con valores en conflicto? |
| Validez (S1) | `unidad_volumen`: L y m3 son válidos; hay además una unidad desconocida (`unidad?`), que **no se adivina** |
| Validez | Coma decimal y fechas `dd/mm/YYYY` en ampliación; fechas **imposibles** (p. ej. `2025-02-30`) en los 3 lotes; texto `PENDIENTE` en `volumen_entrada`; `volumen_entrada` negativo; `modo_operacion` con variantes |
| Consistencia (S2) | `volumen_salida` > `volumen_entrada`; `minutos_interrupcion` > 60. **Incumplen el contrato**, porque el modelo omite almacenamiento y transferencias |
| Completitud | Nulos en `volumen_entrada`: ¿en qué lote, sector o mes se concentran? |
| Oportunidad | Latencia `cargado_en` − `fecha`: distribución, cargas antes del evento y cargas sobre lo esperado. `metadatos.json` declara `"latency": 2`; hay que justificar en qué unidad se interpreta |

**Clasificación obligatoria** (columna `clasificacion` en la matriz):
- `defecto`: incumple el contrato, por ejemplo una unidad desconocida o una fecha imposible.
- `extremo_plausible`: valor raro pero posible; se marca y no se borra.
- `ausencia_estructural`: falta por diseño. Ejemplos: tarifas antes de agosto o columnas de metas fuera del período.

**Sesgo en los KPI:** en `impacto_KPI` y en el texto, indicar qué KPI se sesgarían más y en qué dirección. Ejemplos:
- excluir filas con salida > entrada sube la diferencia de volúmenes;
- sumar litros como m3 infla el volumen.

### Formatos

- `perfil_calidad.csv`: `lote, segmento_tipo, segmento_valor, campo, filas, nulos, pct_nulos, distintos, invalidos, pct_invalidos, min, p50, max`.
  - `segmento_tipo` ∈ {total, sector, mes, modo_operacion}.
- `matriz_reglas.csv`: las columnas de [plantilla_reglas_calidad.csv](../../plantilla_reglas_calidad.csv), más `lote` y `clasificacion` al final:
  - plantilla: `regla_id, tabla, campo, condicion, severidad, denominador, filas_evaluadas, filas_fallidas, tratamiento, justificacion, impacto_KPI`;
  - el `tratamiento` es **propuesto**, porque se aplica en la E2;
  - esta matriz alimenta el **plan de limpieza** del diagnóstico.

## Parte B: 6 métricas de calidad (W6 → `T2_fichas_calidad.csv`)

Con `/ficha-indicador`. Propuesta inicial, que el equipo puede ajustar en el checkpoint:
1. Cobertura de lecturas válidas = sector-horas con lectura válida / sector-horas esperadas. T3 entrega el cálculo; tú escribes la ficha.
2. Unicidad de clave = filas con `medicion_id` repetido / filas.
3. Validez de unidad = filas con unidad ∉ {m3, L} / filas.
4. Consistencia de volúmenes = filas con salida > entrada / filas con ambos volúmenes.
5. Validez de interrupción = filas con minutos ∉ [0, 60] / filas.
6. Oportunidad = filas con latencia negativa o sobre el umbral / filas con ambas fechas válidas.

## Parte C: ranking de inspección (P4, fase 2)

- Desde el día 1, escribir el código del ranking contra el **contrato de tablas por sector** del [README](../README.md), usando datos de prueba.
- Al recibir `T3_por_sector.csv` y `T4_por_sector.csv` (versión preliminar el D-7), unir con `T2_por_sector.csv` y:
  1. definir y **justificar** los criterios y su prioridad (continuidad, diferencia de volúmenes, energía, confiabilidad);
  2. hacer el ranking **sin filtro** y **con filtro de cobertura mínima**, justificando el umbral;
  3. mostrar qué sectores cambian de posición y por qué;
  4. proponer **3 inspecciones** y la **evidencia a recolectar** en cada una. Separar lo que es operación de lo que es incertidumbre del sensor.
- Salida: `T2_ranking.csv` + una figura (`/grafico-diagnostico`) + el texto para `diagnostico.md` §5.

## Terminado cuando

- [ ] Todas las pistas tienen su regla, con cifras por lote, denominador y clasificación.
- [ ] Están `perfil_calidad.csv` y `matriz_reglas.csv` con los formatos de arriba.
- [ ] Hay 6 fichas de métricas de calidad.
- [ ] Están `T2_por_sector.csv` (preliminar el D-7) y el ranking con y sin filtro, con las 3 inspecciones justificadas.
- [ ] 2–3 hallazgos candidatos escritos abajo.

## No hacer

- No borrar, deduplicar ni imputar: eso es la E2. Aquí solo se mide y se propone.
- No calcular cobertura ni continuidad (T3); usar su tabla por sector.
- No comparar `cargado_en` con la fecha de hoy.

## Hallazgos candidatos

<!-- Usar el formato del README: H<n>, Observación, Gráfico o tabla, Período · unidad · población, Hipótesis, Decisión o acción, Limitación, Dimensión -->
