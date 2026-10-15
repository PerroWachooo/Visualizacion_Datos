# T3: Cobertura, continuidad y catálogos

**Responsable:** ____________
**Ítems del Word:** W4f (faltantes por segmento), P1, P3, S3 · **Rúbrica:** "EDA y granularidad" (30 pts) y el sesgo de faltantes de "Calidad y pertinencia"
**Notebook de trabajo:** `E1/T3_cobertura.ipynb`
**Módulo reutilizable:** `E1/T3_cobertura.py` · **Estado:** implementada y ejecutada desde un kernel nuevo.
**Productos:** `salidas/tablas/T3_cobertura_sector_semana.csv`, `salidas/tablas/T3_continuidad_sector_semana.csv`, `salidas/tablas/T3_por_sector.csv`, `salidas/tablas/T3_uniones.csv`, heatmap

## Objetivo

Responder **qué sector-horas están realmente observadas**, qué tan buena es la continuidad **considerando lo que no se sabe** (límites con 0 y 60 min en las horas ausentes) y si los catálogos se pueden unir a los hechos sin perder ni duplicar filas. Las horas ausentes deben quedar **visibles**: no desaparecen ni se rellenan con 0.

## Insumos

- `comun.parse_exploratorio(comun.cargar_lotes())`. Usar `fecha` tipada; las filas con `_fecha_invalida` quedan con `NaT` y se cuentan aparte.
- Tablas complementarias, todas vía `comun.cargar_tabla(...)`:
  - `dimensiones/sectores.csv`
  - `complementarios/sectores_historial.csv`: conexiones por vigencia, con corte el 2025-10-01.
  - `complementarios/tarifas_energia.csv`
  - `dimensiones/metas_ancho.csv` y `complementarios/metas_2025_ancho.csv`

## Parte A: grilla, cobertura y faltantes por segmento (W4f, S3)

1. Grilla esperada: calendario UTC horario × 30 `sector_id`, por lote según su período. Para ago–dic el enunciado da 110.160 sector-horas.
2. Left join **desde la grilla** a los hechos. Las lecturas cuentan como "válidas" si tienen fecha válida, sector del catálogo y clave única; **declarar** el criterio. El resultado es una columna `estado` ∈ {observada, ausente}.
3. Comparar filas recibidas vs. horas esperadas por lote. ¿En algún lote hay **más** filas que horas? Explicar por qué (duplicados, sector-horas repetidas con distinto `medicion_id`, `NO_EXISTE`, fechas imposibles).
4. **Faltantes por segmento:** cobertura por sector, semana, mes y hora del día. ¿Los huecos se **concentran** en algunos sectores? Eso es S3: el promedio de lecturas disponibles puede ocultar fallas.

## Parte B: continuidad con límites (P1)

Por **sector y semana** (y también por sector en el período del ranking), **ponderada por las conexiones vigentes en cada hora**. Las conexiones cambian el 2025-10-01; la unión es desde inclusivo y hasta exclusivo, con exactamente una versión por hecho.

```
peso_h = conexiones vigentes en la hora h
continuidad_obs = 1 − Σ_obs(min_h · peso_h) / Σ_obs(60 · peso_h)                       # solo horas observadas
continuidad_max = 1 − Σ_obs(min_h · peso_h) / Σ_todas(60 · peso_h)                     # supone 0 min en horas desconocidas
continuidad_min = 1 − [Σ_obs(min_h · peso_h) + Σ_desc(60 · peso_h)] / Σ_todas(60 · peso_h)   # supone 60 min en horas desconocidas
```

- Decidir y **declarar** si una hora con `minutos_interrupcion` fuera de 0–60 cuenta como "desconocida". Ese es un caso de S2 que mide T2.
- Comparar con la meta docente de continuidad (`metas_2025_ancho`, 99,5%, sentido mínimo). ¿Qué sectores no se pueden calificar porque el intervalo [mín, máx] cruza la meta?
- Salidas: `T3_continuidad_sector_semana.csv` y `T3_por_sector.csv` (contrato del [README](../README.md); preliminar el D-7).

## Parte C: mapa de calor con ausencia visible (P3)

- Heatmap de sector (filas) × semana o día (columnas), de interrupciones (o presión), con las **horas ausentes en un color propio** (`comun.PALETA["ausente"]`), nunca como 0. Usar `/grafico-diagnostico`.
- Analizar presión e interrupciones: ¿coinciden presiones bajas con interrupciones o con huecos? Una presión baja es **solo una señal operacional del escenario**, no un juicio sanitario.

## Parte D: catálogos y uniones

Generar `T3_uniones.csv`, con una fila por unión y las columnas: hechos evaluados, 0 coincidencias, 1 y más de 1. Revisar:
- **sector → catálogo:** aparece `NO_EXISTE`;
- **hecho → `sectores_historial`:** exactamente una vigencia por hecho;
- **hecho (ago–dic) → tarifas:** antes de agosto la tarifa está **fuera de alcance**, no es 0;
- **metas:** las dos versiones se reemplazan, no se concatenan. ¿Coinciden en ene–jul? Hay que dejar anotado el `melt` que se necesitará en la E2.

## Terminado cuando

- [x] Está la tabla de recibidas vs. esperadas para los 3 lotes, con la explicación de las diferencias.
- [x] Están la cobertura por sector y semana y los faltantes por segmento.
- [x] La continuidad observada, mínima y máxima está ponderada por conexiones, por sector y semana.
- [x] El heatmap tiene la ausencia visible y el análisis de presión e interrupciones.
- [x] Están `T3_por_sector.csv` (preliminar el D-7) y `T3_uniones.csv`.
- [x] 2–3 hallazgos candidatos escritos abajo.

## No hacer

- No rellenar horas ausentes con 0 ni interpolar.
- No concatenar las dos tablas de metas.
- No sumar `conexiones` por hora como si fueran clientes únicos: son un peso.
- No medir reglas de formato (T2); aquí solo interesan para explicar la cobertura.

## Hallazgos candidatos

<!-- Usar el formato del README: H<n>, Observación, Gráfico o tabla, Período · unidad · población, Hipótesis, Decisión o acción, Limitación, Dimensión -->


### H1: Cuatro sectores concentran 3.505 de las 10.660 horas sin lectura válida
- **Observación:** en ago–dic se observan 99.500 de 110.160 sector-horas esperadas (90,32%). A-S26 a A-S29 reúnen 3.505 de las 10.660 horas ausentes (32,88%), pese a ser 4 de 30 sectores. Su cobertura conjunta es 76,14% (11.183 / 14.688).
- **Gráfico o tabla:** `salidas/figuras/T3_cobertura_interrupciones.png`, `salidas/tablas/T3_cobertura_sector_mes.csv`, `T3_continuidad_sector_ago_dic.csv`.
- **Período · unidad · población:** ago–dic 2025 UTC · sector-horas · calendario de 30 sectores.
- **Hipótesis:** diferencias de captura o transmisión podrían explicar la concentración; los datos no prueban el mecanismo.
- **Decisión o acción:** acompañar los KPI de esos sectores con su cobertura y contrastar el ranking con filtros de cobertura; recolectar evidencia sobre medición y operación.
- **Limitación:** 10.160 es la diferencia entre calendario y filas recibidas, no la ausencia de lecturas válidas. Tras descartar 500 filas por fecha/sector, la ausencia válida es 10.660. Los problemas por lote pueden solaparse y no deben sumarse sin controlar doble conteo.
- **Dimensión:** confiabilidad y continuidad.

### H2: Los 30 sectores quedan bajo 99,5% incluso con 0 interrupción en horas desconocidas
- **Observación:** 30 de 30 sectores tienen continuidad máxima menor que 99,5% en ago–dic. Los máximos van de 96,49% a 98,97%; ningún intervalo cruza la meta en el agregado del período. Las 350 lecturas recibidas con interrupción fuera de dominio cuentan para cobertura, pero se incluyen como exposición desconocida al calcular los límites.
- **Gráfico o tabla:** `salidas/figuras/T3_continuidad_limites.png`, `salidas/tablas/T3_continuidad_sector_semana.csv`, `T3_continuidad_sector_ago_dic.csv`.
- **Período · unidad · población:** ago–dic 2025 UTC · % de minutos-conexión · 30 sectores, ponderados por conexiones vigentes en cada hora.
- **Hipótesis:** no se atribuye una causa. Es una comparación con una meta docente bajo escenarios explícitos.
- **Decisión o acción:** la meta por sí sola no distingue tres candidatos; T5 debe combinar continuidad con volúmenes, energía y confiabilidad, usando las tablas oficiales de T3 y T4.
- **Limitación:** los límites 0/60 son escenarios extremos, no probabilidades ni valores imputados. La clasificación del período no implica idéntica clasificación en cada semana, ni resultados reales de Aguas Andinas.
- **Dimensión:** continuidad.

### H3: La asociación diaria presión–interrupción es inversa, r = −0,210
- **Observación:** 4.590 de 4.590 sector-días tienen al menos una hora pareada; hay 99.150 de 110.160 pares horarios válidos. Las otras 11.010 horas son 10.660 ausencias más 350 interrupciones inválidas. La correlación entre mediana de presión y media de interrupciones, calculadas sobre las mismas horas de cada sector-día, es −0,210; presión–cobertura diaria es 0,030.
- **Gráfico o tabla:** `salidas/figuras/T3_presion_interrupciones.png`, `salidas/tablas/T3_resumen_sector_dia.csv`.
- **Período · unidad · población:** ago–dic 2025 UTC · bar y min/h · resúmenes diarios de horas pareadas de 30 sectores.
- **Hipótesis:** pueden intervenir operación y selección de horas observadas; no se identifica un efecto causal.
- **Decisión o acción:** contrastar presión e interrupciones junto a cobertura; no introducir un umbral de presión baja distinto del que documente T4.
- **Limitación:** un día con algún par válido no está necesariamente completo. Hay 3.941 de 4.590 sector-días con recepción parcial, ninguno completamente ausente. No se conoce la presión de las horas faltantes ni se puede inferir potabilidad.
- **Dimensión:** continuidad y confiabilidad.

## Integración en T5

- Importar `T3_cobertura` desde `E1/`; el módulo reutiliza `comun` y `T2_reglas`, que deben acompañarlo.
- `T3_por_sector.csv` tiene las siete columnas exactas del contrato, 30 sectores únicos y el período ago–dic 2025 UTC. T4 sigue pendiente; no se genera el ranking con datos inventados.
- Para recalcular desde `E1/`: `../.venv/bin/python -m nbconvert --to notebook --execute T3_cobertura.ipynb --inplace --ExecutePreprocessor.kernel_name=python3`.
- Las funciones de cálculo no escriben. `exportar` guarda únicamente CSV y PNG `T3_`; repetir la ejecución regenera esos productos.
- Se validaron los ejemplos completo, parcial, sin horas conocidas, pesos cambiantes, interrupción inválida y copia adicional; también los límites semanales, la frontera de octubre y la coincidencia con T2.
