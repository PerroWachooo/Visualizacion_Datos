# T3: Cobertura, granularidad y catálogos

**Responsable:** ____________
**Cubre:** IL1.2 (granularidad, pertinencia, consistencia con catálogos)
**Notebook:** `E1/T3_cobertura.ipynb`

## Objetivo

Responder **qué horas y sectores están realmente observados** y si las tablas complementarias se pueden unir a los hechos sin perder ni duplicar filas. El enunciado lo exige: las horas ausentes deben quedar **visibles** en la cobertura, no desaparecer.

## Insumos

- `comun.parse_exploratorio(comun.cargar_lotes())`: usar `fecha` ya tipada. Las filas con `_fecha_invalida` quedan con `NaT` y hay que contarlas aparte.
- Tablas complementarias, todas vía `comun.cargar_tabla(...)`:
  - `dimensiones/sectores.csv`
  - `complementarios/sectores_historial.csv`
  - `complementarios/tarifas_energia.csv`
  - `dimensiones/metas_ancho.csv`
  - `complementarios/metas_2025_ancho.csv`
- La sección "Contrato" y "Modelo de datos" del [README del caso](../../README.md) y del enunciado.

## Pistas detectadas al preparar la estructura

Hay que **verificar y cuantificar**:

| Tema | Pista |
|---|---|
| Grilla esperada | Calendario UTC horario × 30 sectores por lote: ene–jun, jul y ago–dic. El enunciado da 110.160 sector-horas esperadas para ago–dic contra 100.000 lecturas. Hay que calcular también base y actualización y comparar filas recibidas vs. esperadas (¿hay **más** filas que horas en algún lote? ¿por qué?). |
| Granularidad | ¿Existe exactamente una lectura por sector-hora? Hay pares sector + `fecha` repetidos con **distinto** `medicion_id`. |
| Hechos sin lugar en la grilla | Filas con `fecha` imposible (NaT) y filas cuyo `sector_id` no existe en el catálogo (aparece `NO_EXISTE`). |
| Vigencias | `sectores_historial` tiene 2 versiones por sector (corte 2025-10-01, desde inclusivo y hasta exclusivo). Verificar que **cada hecho calza exactamente con una versión** y medir cuántas `conexiones` cambian en octubre. |
| Tarifas | N:1 por `sector_id` + `mes`, solo ago–dic. Verificar que todo hecho de ago–dic encuentre tarifa. Antes de agosto la tarifa está **fuera de alcance**, no es 0. |
| Metas | `metas_2025_ancho` (ene–dic) reemplaza a `metas_ancho` (ene–jul). Verificar si coinciden en los meses comunes, describir por qué el formato ancho no es tidy y qué `melt` hará falta en la E2. |

## Pasos sugeridos

1. Construir la grilla con `pd.date_range(..., freq="h", tz="UTC")` × los 30 `sector_id` del catálogo, por lote según su período.
2. Hacer un left join **desde la grilla** a los hechos (deduplicados solo para este conteo, y declararlo) y marcar `observada` = sí/no.
3. Calcular la cobertura por lote, mes y sector: horas observadas / horas esperadas. Escribir siempre ambos números.
4. Heatmap de cobertura, sector (filas) × día o semana (columnas), al menos para la ampliación. Usar `/grafico-diagnostico`.
5. Revisar si los huecos se concentran en sectores, meses u horas del día específicos. Eso afecta qué sectores se pueden comparar con justicia.
6. Hacer las uniones de prueba con historial y tarifas: contar 0 coincidencias, 1 coincidencia y más de una.

## Entregables

- `E1/T3_cobertura.ipynb`
- `E1/salidas/tablas/T3_cobertura_sector_mes.csv`, con columnas `sector_id, mes, horas_esperadas, horas_observadas, cobertura_pct`.
- `E1/salidas/tablas/T3_uniones.csv`: una fila por unión (historial, tarifas, catálogo) con hechos evaluados, con 0, 1 y más de 1 coincidencia.
- `E1/salidas/figuras/T3_*.png`, como mínimo el heatmap de cobertura, con su interpretación.

## Terminado cuando

- [ ] Hay una tabla de filas recibidas vs. esperadas para los 3 lotes, con la explicación de las diferencias.
- [ ] El heatmap muestra las horas ausentes, que no se rellenan con 0.
- [ ] Cada unión tiene el conteo de 0, 1 y más de 1 coincidencia.
- [ ] 2–3 hallazgos candidatos escritos abajo.

## No hacer

- No rellenar horas ausentes con 0 ni interpolar.
- No concatenar las dos tablas de metas.
- No medir reglas de formato ni duplicados exactos (T2); aquí solo interesan para explicar la cobertura.

## Hallazgos candidatos

<!-- Usar el formato del README: H<n>, Evidencia, Figura o tabla, Límite, Acción propuesta, Dimensión -->
