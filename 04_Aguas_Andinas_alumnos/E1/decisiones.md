# Registro de decisiones (E1)

Aquí se anotan las decisiones del grupo que **no estaban definidas** en el Word, el enunciado o los metadatos, o que tenían más de una interpretación posible. Sirve para que todos apliquen el mismo criterio y para poder justificar cada decisión en la defensa individual (E4).

**Reglas:**
- Solo se agregan entradas al final; no se borran.
- Si una decisión cambia, se agrega una entrada nueva que reemplaza a la anterior y se dice cuál reemplaza.
- Formato: ID, fecha, quién, qué era ambiguo, alternativas, evidencia, decisión, consecuencias y dónde se aplica.

---

## D-01: Umbral de atraso de carga = 2 horas

- **Fecha / quién:** 2026-10-11 · Byron (T2)
- **Qué era ambiguo:** cada lectura tiene `fecha` (la hora medida) y `cargado_en` (cuándo llegó a la base de datos). La diferencia es el **atraso de carga**, y sirve para medir la dimensión de calidad *oportunidad*. `metadatos.json` declara `"latency": 2`, pero **no indica la unidad** (¿horas? ¿días?). Ni el Word ni el README del caso la aclaran.
- **Alternativas:**
  - (a) 2 horas;
  - (b) 2 días.
- **Evidencia** (calculada con `comun.parse_exploratorio` sobre los 3 lotes):
  - Atraso de las lecturas con ambas fechas válidas (253.051): mediana de 0,55 h en base y actualización y de 0,90 h en ampliación; máximo de 13,7 h.
  - Con (a), 34.016 de 253.051 lecturas (13,4%) superan el umbral.
  - Con (b), **ninguna** lo supera, así que el indicador siempre daría 100% y no distinguiría nada.
- **Decisión:** (a) 2 horas. Calza con la telemetría horaria y produce un indicador que discrimina entre lotes y sectores. Se informa también la **sensibilidad a 1, 3 y 6 horas**, para mostrar cuánto depende el resultado del umbral.
- **Consecuencias:**
  - El % de lecturas atrasadas depende de esta interpretación y debe presentarse como tal.
  - Si el profesor aclara otra unidad, se cambia el umbral en `T2_reglas.py` (`UMBRAL_ATRASO_H`) y se recalculan RQ-OPO-02 y KRI-06.
- **Dónde se aplica:**
  - `justificacion` de RQ-OPO-02 en `salidas/tablas/matriz_reglas.csv`;
  - ficha KRI-06 en `salidas/tablas/T2_fichas_calidad.csv`;
  - límite de interpretación candidato para `diagnostico.md` §6.

## D-02: La confiabilidad del dato define el tipo de inspección, no la prioridad

- **Fecha / quién:** 2026-10-11 · Byron (T2)
- **Qué era ambiguo:** el Word pide priorizar 3 sectores considerando continuidad, diferencia de volúmenes, energía **y** confiabilidad de la medición, pero no dice cómo combinar los cuatro criterios.
- **Alternativas:**
  - (A) el puntaje de prioridad usa solo las señales operacionales, y la confiabilidad decide si se inspecciona la operación o el sensor;
  - (B) un único puntaje con los cuatro criterios.
- **Evidencia:** el Word pide *"separar evidencia de operación de incertidumbre por sensores"*. Con (B), un sector podría quedar entre los 3 primeros solo por tener muchas lecturas defectuosas, sin señales operacionales reales.
- **Decisión:** (A).
  - **Puntaje operacional:** continuidad, diferencia de volúmenes y energía (kWh/m3 y CLP/m3 promediados como un solo criterio, porque costo = kWh × tarifa).
  - **Tipo de inspección:**
    - "sensor primero" si el % de filas con defecto del sector supera **2 veces la mediana** de los 30 sectores;
    - "operación" en caso contrario.
  - **Por qué ese umbral:** es una regla relativa ("el doble de defectos que un sector típico"). Se descartó el percentil 75 porque en ago–dic hay 10 sectores con 8,1–9,6% de defectos y 20 con 1,7–2,7%: el percentil 75 (8,7%) partiría en dos un grupo homogéneo. Con los datos actuales, 2 × mediana ≈ 4,6% separa ambos grupos.
- **Consecuencias:** cada inspección propuesta indica qué evidencia recolectar (operación o medición).
- **Dónde se aplica:** función `ranking` de `T2_reglas.py`, `T2_ranking.csv` y `diagnostico.md` §5.

## D-03: El ranking de inspección espera las tablas oficiales de T3 y T4

- **Fecha / quién:** 2026-10-11 · Byron (T2)
- **Qué era ambiguo:** el ranking (P4) necesita continuidad y cobertura (T3) y volúmenes y energía (T4). T2 podía armar un ranking preliminar con cálculos propios o esperar las cifras oficiales.
- **Alternativas:**
  - (a) ranking preliminar propio;
  - (b) esperar a T3 y T4;
  - (c) sacar el ranking de la T2.
- **Decisión:** (b). El código del ranking queda listo y probado con **datos de prueba inventados** (no se publica ningún ranking con ellos). Se ejecuta con datos reales en la **tarea de consolidación**.
- **Consecuencias:** el ranking queda registrado como pendiente en la sección "Pendientes y consolidación" del [README](README.md).
- **Dónde se aplica:** `README.md` (pendientes y consolidación) y `tareas/T2_calidad.md`.
