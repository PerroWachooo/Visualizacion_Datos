# T2: Calidad, métricas de calidad y ranking de inspección

**Responsable:** Byron
**Ítems del Word:** W5, W6 (6 métricas de calidad), S1, S2, P4 · **Rúbrica:** "Calidad y pertinencia" (30 pts)
**Notebook de trabajo:** `E1/T2_calidad.ipynb` · **Módulo:** `E1/T2_reglas.py` (reglas reutilizables en E2 y E4)
**Decisiones:** [D-01 atraso = 2 h](../decisiones.md), [D-02 tipo de inspección](../decisiones.md), [D-03 el ranking espera a T3 y T4](../decisiones.md)

## Estado

| Parte | Estado |
|---|---|
| A. Perfil y matriz de reglas | **Listo:** `matriz_reglas.csv` (76 filas, 27 reglas), `perfil_calidad.csv` (1.287 filas), `T2_sesgo_kpi.csv` y 4 figuras `T2_*.png`. Todo se genera al ejecutar `T2_calidad.ipynb` |
| B. 6 métricas de calidad | **Listo:** `T2_fichas_calidad.csv` (KRI-01…06, `v0-E1`), con valores calculados en el notebook (sección 6) |
| Tabla por sector | **Listo:** `T2_por_sector.csv` (30 sectores, ago–dic, contrato del README) |
| C. Ranking de inspección | **Bloqueada por T3/T4:** el código (`T2_reglas.ranking` / `comparar_rankings`) está listo y probado con datos de prueba; se ejecuta en la consolidación (ver [README](../README.md#pendientes-y-consolidación)) |

**Nota sobre la cobertura:** la regla RQ-COM-02 y la métrica KRI-01 usan una cobertura simple por lote (lectura válida = fecha válida dentro del período, sector del catálogo, sin copia ni sector-hora repetida). No reemplaza el análisis de cobertura de T3; se cruza con el de T3 en la consolidación.
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

### H1: Ago–dic es el lote menos confiable y llega 2,6 veces más atrasado
- **Observación:**
  - 21.379 de 99.800 lecturas de ago–dic (21,4%) llegan con más de 2 h de atraso, contra 10.801 de 130.841 en ene–jun (8,3%). Ago–dic es peor con cualquier umbral (1, 3 o 6 h).
  - Ago–dic trae además 7 tipos de defecto que no existían en ene–jul (coma decimal, fecha dd/mm, `PENDIENTE`, unidad desconocida, 90 min de interrupción, salida > entrada, carga antes de la hora medida).
  - Ago–dic tiene 10.660 de 110.160 sector-horas sin lectura válida (9,7%), contra 0,3% en ene–jul. Esta cifra se cruza con T3 en la consolidación.
- **Gráfico o tabla:** `salidas/figuras/T2_atraso_carga.png`, `salidas/figuras/T2_reglas_por_lote.png`, `salidas/tablas/matriz_reglas.csv`
- **Período · unidad · población:** ene–dic 2025 UTC por lote · % de filas · lecturas con fecha y `cargado_en` válidos (253.051)
- **Hipótesis:** el lote de ampliación pasó por otro proceso de captura o integración (otros formatos, demora de transmisión, problema de reloj). Los datos no permiten afirmarlo.
- **Decisión o acción:**
  - los KPI de ago–dic, que es el período del ranking, deben reportarse con su cobertura;
  - en la E2, convertir los formatos recuperables con su regla documentada y excluir los defectos sin imputar.
- **Limitación:** el % exacto de atraso depende de interpretar `"latency": 2` como horas ([D-01](../decisiones.md)). La comparación entre lotes no depende de esa decisión.
- **Dimensión:** confiabilidad

### H2: En ago–dic los volúmenes vacíos son de 10 sectores (A-S20 a A-S29), candidatos a "sensor primero"
- **Observación:**
  - los 2.200 volúmenes de entrada vacíos de ago–dic están **todos** en A-S20 a A-S29: son 2.200 de sus 31.645 lecturas (6,95%), y en los otros 20 sectores hay 0;
  - en ene–jul, en cambio, los nulos se reparten parejo (≈ 1% por sector);
  - por eso A-S20 a A-S29 tienen entre 8,1% y 9,6% de filas con defecto, contra 1,7–2,7% del resto;
  - A-S26 a A-S29 además tienen menos filas (≈ 2.800 vs. ≈ 3.400), lo que sugiere menor cobertura (a confirmar con T3).
- **Gráfico o tabla:** `salidas/figuras/T2_nulos_por_sector.png`, `salidas/tablas/T2_por_sector.csv`
- **Período · unidad · población:** ago–dic 2025 UTC (vs. ene–jul) · % de lecturas del sector · lecturas de los 30 sectores del catálogo
- **Hipótesis:** una falla de medición o transmisión que afecta a ese grupo de sectores desde agosto.
- **Decisión o acción:** según D-02, si alguno de estos sectores queda entre los 3 prioritarios, se inspecciona **primero el sensor** (umbral: 2 × la mediana de % de defectos ≈ 4,6%). En la E2, los nulos no se imputan.
- **Limitación:** un volumen vacío no dice si el sector tuvo problemas operacionales. El promedio de las lecturas disponibles de esos sectores puede ocultar justamente las horas con fallas.
- **Dimensión:** confiabilidad

### H3: Sumar litros como m3 hunde kWh/m3 en un 99,4%; los demás errores mueven la continuidad en décimas que importan frente a la meta
- **Observación** (ene–dic, lecturas válidas):
  - 43.020 de 253.404 filas (17,0%) vienen en litros; si no se convierten, kWh/m3 cae de 0,265 a 0,0015 (−99,4%);
  - incluir las entradas negativas y salida > entrada baja la diferencia de volúmenes de 16,10% a 15,33% (−0,77 puntos; −0,90 en ago–dic);
  - en la continuidad simple, incluir los minutos > 60 la baja 0,21 puntos (0,52 en ago–dic), y tratar las horas sin lectura como 0 minutos sin agua la sube 0,07 puntos (0,20 en ago–dic).
- **Gráfico o tabla:** `salidas/figuras/T2_sesgo_kpi.png`, `salidas/tablas/T2_sesgo_kpi.csv`
- **Período · unidad · población:** ene–dic 2025 UTC (y ago–dic) · kWh/m3, % y puntos porcentuales · lecturas válidas de los 3 lotes
- **Hipótesis:** no aplica. Es un cálculo de sensibilidad del tratamiento, no una observación del negocio.
- **Decisión o acción** (plan de limpieza para la E2):
  - convertir L → m3 antes de cualquier suma y excluir la unidad desconocida;
  - excluir entradas negativas y salida > entrada;
  - tratar las horas con minutos > 60 como desconocidas;
  - reportar la continuidad con límites 0/60 (T3) en lugar de suponer 0 minutos en las horas ausentes.
- **Limitación:** la referencia es provisional (las fórmulas oficiales son de T4), y la continuidad simple no pondera por conexiones (la oficial es de T3).
- **Dimensión:** energía, volúmenes y continuidad
