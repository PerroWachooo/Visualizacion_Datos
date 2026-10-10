# T3: Cobertura, continuidad y catálogos

**Responsable:** ____________
**Ítems del Word:** W4f (faltantes por segmento), P1, P3, S3 · **Rúbrica:** "EDA y granularidad" (30 pts) y el sesgo de faltantes de "Calidad y pertinencia"
**Notebook de trabajo:** `E1/T3_cobertura.ipynb`
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

- [ ] Está la tabla de recibidas vs. esperadas para los 3 lotes, con la explicación de las diferencias.
- [ ] Están la cobertura por sector y semana y los faltantes por segmento.
- [ ] La continuidad observada, mínima y máxima está ponderada por conexiones, por sector y semana.
- [ ] El heatmap tiene la ausencia visible y el análisis de presión e interrupciones.
- [ ] Están `T3_por_sector.csv` (preliminar el D-7) y `T3_uniones.csv`.
- [ ] 2–3 hallazgos candidatos escritos abajo.

## No hacer

- No rellenar horas ausentes con 0 ni interpolar.
- No concatenar las dos tablas de metas.
- No sumar `conexiones` por hora como si fueran clientes únicos: son un peso.
- No medir reglas de formato (T2); aquí solo interesan para explicar la cobertura.

## Hallazgos candidatos

<!-- Usar el formato del README: H<n>, Observación, Gráfico o tabla, Período · unidad · población, Hipótesis, Decisión o acción, Limitación, Dimensión -->
