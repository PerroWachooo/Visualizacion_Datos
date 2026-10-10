# T4: EDA de negocio, costo por m3 y KPI

**Responsable:** ____________
**Ítems del Word:** W4a–e (5 de los 6 análisis), P2, W6 (6 KPI) · **Rúbrica:** "EDA y granularidad" (30 pts)
**Notebook de trabajo:** `E1/T4_eda_negocio.ipynb`
**Productos:** `salidas/tablas/T4_costo_m3.csv`, `salidas/tablas/T4_fichas_kpi.csv`, `salidas/tablas/T4_por_sector.csv`, figuras
**Skills:** `/grafico-diagnostico`, `/ficha-indicador` (Codex: `$grafico-diagnostico`, `$ficha-indicador`)

## Objetivo

Describir cómo se comportan las variables de la decisión (volúmenes, energía, presión e interrupciones) en el tiempo y entre segmentos, explicar qué mueve el **costo por m3** y **definir los 6 KPI** del caso.

## Insumos

- `comun.parse_exploratorio(comun.cargar_lotes())`. Usar **`volumen_entrada_m3` y `volumen_salida_m3`**, nunca `volumen_*` sin convertir. Con unidad desconocida quedan en NA, **no se adivinan**.
- `comun.cargar_tabla("complementarios/tarifas_energia.csv")` (solo ago–dic) y `comun.cargar_tabla("dimensiones/sectores.csv")`.
- Láminas 16–23 de la clase 01: medidas descriptivas, percentiles, boxplot, asociación y atípicos.

## Exclusiones que deben quedar declaradas

`parse_exploratorio` no elimina filas, así que tú decides qué excluir **para cada análisis**. Hay que escribirlo con la cantidad y el denominador, y mostrar **cuánto cambia el resultado** al incluir o excluir. Casos que vas a encontrar:
- volúmenes en NA (nulos, `PENDIENTE` o unidad desconocida);
- `volumen_entrada` negativo;
- salida > entrada;
- minutos > 60;
- `_dup_medicion_id`.

T2 mide estos casos como reglas de calidad. No hay que esperarlo.

**Cero ≠ nulo:** `minutos_interrupcion = 0` es "sin interrupción medida", mientras que un volumen nulo es "no se sabe". La rúbrica pide diferenciarlos.

## Parte A: cinco análisis del Word (W4a–e)

| # | Análisis | Sugerencia |
|---|---|---|
| a | **Distribución** | Volumen de entrada (m3), diferencia entrada − salida, `presion_bar`, `energia_kwh`, `minutos_interrupcion` (casi siempre 0: mostrar la proporción de horas con interrupción y la distribución de las que sí tienen), con n, media, mediana, P25/P75 y RIC |
| b | **Categorías** | `modo_operacion` (normal vs. mantenimiento, tras normalizar) y `unidad_volumen` por lote: frecuencias y proporciones |
| c | **Evolución temporal** | Series semanales o mensuales de volumen, energía, kWh/m3 e interrupciones, de ene a dic, marcando los cortes de lote |
| d | **Comparación de segmentos** | Sectores entre sí (ordenados por valor) y normal vs. mantenimiento |
| e | **Relación bivariada** | Energía vs. volumen de entrada, o diferencia de volúmenes vs. presión. **Correlación solo entre variables interpretables**; una asociación no demuestra efecto |

El sexto análisis (f, faltantes por segmento) lo hace T3.

Para los atípicos se usa la regla de 1,5 RIC por sector y la comparación contra `capacidad_m3_h`. Hay que distinguir un **extremo plausible** de un **defecto**: la alerta indica que hay que revisar, no que hay que borrar.

## Parte B: costo por m3 (P2 → `T4_costo_m3.csv` + figura)

En ago–dic, costo de energía = `energia_kwh × tarifa_kwh_clp` (N:1 por sector y mes). Hay que separar tres efectos:
1. **Cambio de unidad:** el costo/m3 calculado **sin** convertir L → m3 (incorrecto) vs. convertido. Cuantificar la distorsión.
2. **Mayor energía:** kWh/m3 por mes y sector.
3. **Tarifa:** CLP/kWh por mes y sector. Como costo/m3 = (kWh/m3) × (CLP/kWh), la variación entre meses se puede descomponer en esos dos factores.

Además, comparar la **razón de sumas** (Σ costo / Σ m3) con el **promedio de razones** (media de costo_h / m3_h) y explicar por qué difieren y cuál corresponde al KPI.

## Parte C: 6 KPI (W6 → `T4_fichas_kpi.csv`)

Con `/ficha-indicador`. Propuesta inicial, que se cierra en el checkpoint:
1. **Continuidad ponderada por conexiones (%)**: la fórmula y los límites 0/60 los calcula T3 (P1). Tú escribes la ficha; meta docente 99,5%.
2. **Diferencia de volúmenes (%)** = Σ(entrada − salida) / Σ entrada, en m3 y como razón de sumas.
3. **Intensidad energética (kWh/m3)** = Σ kWh / Σ m3 de entrada.
4. **Costo de energía por m3 (CLP/m3)** = Σ(kWh × tarifa) / Σ m3 de entrada, solo ago–dic.
5. **Horas con interrupción (%)** = sector-horas observadas con minutos > 0 / sector-horas observadas.
6. **Horas con presión baja (%)**: umbral docente a definir y justificar. Es una señal operacional.

## Parte D: tabla por sector

`T4_por_sector.csv` sigue el contrato del [README](../README.md): `sector_id, m3_entrada, dif_volumen_pct, kwh_por_m3, costo_clp_por_m3`, para el período del ranking. Se publica una versión preliminar el D-7 para que T2 pruebe el ranking.

## Terminado cuando

- [ ] Los 5 análisis (a–e) tienen su figura interpretada, con n, período y unidad.
- [ ] Las exclusiones están declaradas, con cifras y su efecto en los resultados.
- [ ] El costo por m3 está descompuesto (unidad, energía, tarifa), con la razón de sumas vs. el promedio de razones.
- [ ] Hay 6 fichas de KPI.
- [ ] Está `T4_por_sector.csv` (preliminar el D-7).
- [ ] 2–3 hallazgos candidatos escritos abajo.

## No hacer

- No sumar `conexiones` por hora como si fueran clientes.
- No usar tarifas fuera de ago–dic, ni tratar su ausencia como 0.
- No decidir el ranking final: eso es T2, con tu tabla por sector.

## Hallazgos candidatos

<!-- Usar el formato del README: H<n>, Observación, Gráfico o tabla, Período · unidad · población, Hipótesis, Decisión o acción, Limitación, Dimensión -->
