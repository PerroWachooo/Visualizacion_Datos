# T4: EDA de variables de negocio

**Responsable:** ____________
**Cubre:** IL1.2 (EDA univariado y bivariado, atípicos)
**Notebook:** `E1/T4_eda_negocio.ipynb`

## Objetivo

Describir cómo se comportan las variables que alimentan la decisión (continuidad, diferencia de volúmenes y energía), mostrar **al menos una relación pertinente** y levantar señales preliminares de qué sectores podrían destacar. El ranking final **no se cierra en la E1**.

## Insumos

- `comun.parse_exploratorio(comun.cargar_lotes())`. Usar **`volumen_entrada_m3` y `volumen_salida_m3`**, nunca `volumen_*` sin convertir, porque hay filas en litros.
- `comun.cargar_tabla("dimensiones/sectores.csv")` para `capacidad_m3_h` y el nombre del sector.
- Láminas 16–23 de la clase 01: medidas descriptivas, percentiles, boxplot, asociación y atípicos.

## Decisiones de exploración que deben quedar declaradas

`parse_exploratorio` no elimina filas, así que tú decides qué excluir **para explorar** y lo escribes en el notebook, con la cantidad y el denominador. Casos que vas a encontrar:
- volúmenes nulos, con texto o con unidad desconocida (`volumen_*_m3` en NA);
- `volumen_entrada` negativo;
- `volumen_salida` > `volumen_entrada`;
- `minutos_interrupcion` > 60;
- `medicion_id` duplicado (`_dup_medicion_id`).

T2 mide estos casos como reglas de calidad. Tú solo muestras **cuánto cambian los resultados** si se incluyen o se excluyen. No hay que esperar a T2.

## Pasos sugeridos

1. **Univariado** para volumen de entrada (m3), diferencia entrada − salida (m3 y % de la entrada), `presion_bar`, `energia_kwh` y `minutos_interrupcion`:
   - n (el denominador cambia según la variable), media, mediana, desviación, P25, P75 y RIC;
   - histograma o boxplot.
   - `minutos_interrupcion` es casi siempre 0: elegir un resumen que lo muestre bien (proporción de horas con interrupción, y la distribución solo de las horas con interrupción).
2. **Por grupo:** por lote o mes, por sector y por `modo_operacion` (normal vs. mantenimiento).
3. **Bivariado:** al menos una relación pertinente para la decisión. Ejemplos:
   - energía vs. volumen de entrada (¿hay sectores con más kWh por m3?);
   - minutos de interrupción vs. modo de operación;
   - diferencia de volúmenes vs. presión.
   Recordar que una asociación no implica causa.
4. **Atípicos:** regla de 1,5 RIC (por sector, no solo global) y contraste contra `capacidad_m3_h`. Una alerta indica que hay que revisar, no que hay que borrar.
5. **Señales por sector:** una tabla resumen con una fila por sector y estas columnas:
   - continuidad preliminar: 1 − minutos interrumpidos / minutos observados (el denominador es horas **observadas**, no esperadas; T3 dirá cuántas faltan);
   - diferencia de volúmenes en %;
   - kWh/m3;
   - % de filas con algún flag de calidad (proxy de confiabilidad).
   Es preliminar: la ponderación por `conexiones` y la meta de 99,5% se formalizan en la E2–E3.

## Entregables

- `E1/T4_eda_negocio.ipynb`
- `E1/salidas/tablas/T4_resumen_sector.csv`: la tabla de señales por sector.
- `E1/salidas/figuras/T4_*.png`: 3–4 figuras como máximo (distribuciones, comparación por grupo y la relación bivariada), cada una con su interpretación. Usar `/grafico-diagnostico`.

## Terminado cuando

- [ ] Cada variable de negocio tiene su resumen con n y una figura interpretada.
- [ ] Hay una relación bivariada justificada respecto de la decisión.
- [ ] Las exclusiones están declaradas, con cifras.
- [ ] La tabla por sector está lista para el checkpoint.
- [ ] 2–3 hallazgos candidatos escritos abajo.

## No hacer

- No sumar `conexiones` por hora como si fueran clientes.
- No usar tarifas fuera de ago–dic. El costo de energía es opcional en la E1.
- No declarar "los 3 sectores a inspeccionar": en la E1 solo se reportan señales y sus límites.

## Hallazgos candidatos

<!-- Usar el formato del README: H<n>, Evidencia, Figura o tabla, Límite, Acción propuesta, Dimensión -->
