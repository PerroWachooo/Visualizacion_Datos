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

## D-04: La consolidación es una tarea propia (T5), a cargo de Byron

- **Fecha / quién:** 2026-10-11 · Byron
- **Qué era ambiguo:** la integración final (notebook, PDF, unión de fichas) estaba dentro de la T1 (José), el ranking real en la T2 y los pasos de cierre repartidos en el README, sin una persona responsable de que todo calce ni de armar lo que se sube al profe.
- **Alternativas:**
  - (a) mantener la integración en la T1;
  - (b) crear una T5 de consolidación con un responsable.
- **Decisión:** (b). La T5 la lleva Byron e incluye: cerrar los pendientes de T1–T4, ranking real, cruce de cifras entre tareas, unión de fichas, diagnóstico y PDF, notebook final, versiones probadas y carpeta entregable. La T1 queda con sus partes A–C y los límites (§6). Se agrega el script `T5_consolidar.py`, que revisa qué falta y arma y prueba el .zip.
- **Consecuencias:** como Byron integra, la prueba R1 (ejecutar el notebook desde una sesión nueva) la hace otra persona del grupo.
- **Dónde se aplica:** `tareas/T5_consolidacion.md`, `tareas/T1_pregunta_diccionario.md`, `README.md` (división, productos, cronograma y consolidación).

## D-05: Período y calendario de la T3

- **Fecha / quién:** 2026-10-14 · Bastian (T3), según su plan aprobado, con asistencia de Codex.
- **Qué era ambiguo:** período definitivo del resumen del ranking y límites de las semanas.
- **Alternativas:** resumen anual o ago–dic; semanas separadas por lote o calendario continuo.
- **Decisión:** explorar los tres lotes durante 2025; `T3_por_sector.csv` resume ago–dic, compatible con T2 y con la disponibilidad de tarifas de T4. Semanas de lunes 00:00 a lunes 00:00 UTC, con fin exclusivo; las semanas de los extremos se recortan a 2025. Se agregan horas directamente aunque una semana cruce lote, mes o vigencia.
- **Evidencia:** calendario anual 262.800 sector-horas; ampliación 110.160 (3.672 por sector). La tabla de T2 usa ago–dic.
- **Consecuencias:** no promediar porcentajes semanales para producir indicadores del período; usar las exposiciones originales.
- **Dónde se aplica:** `T3_cobertura.py`, notebook T3 y tablas de cobertura/continuidad.

## D-06: Recepción de lectura e interrupción conocida son estados diferentes

- **Fecha / quién:** 2026-10-14 · Bastian (T3), según su plan aprobado, con asistencia de Codex.
- **Qué era ambiguo:** tratamiento de una lectura recibida con interrupción nula, no numérica o fuera de 0–60.
- **Alternativas:** eliminar toda la lectura de cobertura, recortar minutos a 60 o considerar solo su interrupción como desconocida.
- **Decisión:** reutilizar `T2_reglas.lecturas_validas` para cobertura; conservar la recepción de esas filas y tratar la interrupción inválida como desconocida. No recortar ni imputar. El calendario completo recibe exactamente una vigencia histórica, aun en horas ausentes. O usa solo interrupciones conocidas; U = E − O incluye horas ausentes e interrupciones inválidas.
- **Evidencia:** 350 lecturas válidas para cobertura tienen interrupción inválida, todas en ampliación. Así, hay 99.500 lecturas válidas y 99.150 horas con interrupción conocida en ago–dic.
- **Consecuencias:** la continuidad observada tiene un denominador distinto de cobertura. Si O = 0, observada nula y límites 0–100%. Máximo < meta significa bajo la meta; mínimo ≥ meta significa cumplimiento asegurado; el resto es incierto. La meta 99,5% se obtiene de la tabla anual, no de una norma real.
- **Dónde se aplica:** `incorporar_exposiciones`, `resumir_continuidad`, CSV semanales y resumen del ranking.

## D-07: Ausencia visible en figuras agregadas por día

- **Fecha / quién:** 2026-10-14 · Bastian (T3), según su plan aprobado, con asistencia de Codex.
- **Qué era ambiguo:** un sector-día puede contener algunas lecturas y algunas horas desconocidas.
- **Alternativas:** ocultar el faltante al mostrar solo la media conocida, o acompañar la media con cobertura y marcas de información parcial.
- **Decisión:** mapa de calor doble: cobertura de lecturas e interrupción media conocida. Gris significa celda sin información; puntos rojos indican horas sin lectura en el primer panel y exposición de interrupción desconocida en el segundo. Se exportan ambos denominadores diarios. El gráfico presión–interrupción usa las mismas horas válidas para ambas variables, sin nuevo umbral de presión baja.
- **Evidencia:** 3.941 de 4.590 sector-días tienen recepción parcial y ninguno carece de lecturas todo el día. Una media diaria por sí sola ocultaría esas ausencias.
- **Consecuencias:** no interpretar días con algún par válido como días completos; las correlaciones diarias son descriptivas y no causales.
- **Dónde se aplica:** `generar_figuras`, `T3_resumen_sector_dia.csv` e interpretaciones del notebook.

## D-08: Umbral de presión baja (KPI-06) y sensibilidad

- **Fecha / quién:** 2026-10-17 · Sepu (Benjamín Sepúlveda, T4), con asistencia de OpenCode.
- **Qué era ambiguo:** el Word pide "horas con presión baja" como señal operacional, pero no define el umbral. Los datos no traen una norma de presión mínima.
- **Alternativas:** usar un percentil (p. ej. P5 de la distribución propia), o un umbral fijo docente. Un percentil oculta si la red entera baja de presión.
- **Decisión:** umbral fijo de 3,0 bar, marcado como supuesto docente a validar con el profesor. Se informan sensibilidades de 2,5 y 3,5 bar.
- **Evidencia:** en ago–dic, 2,2% de horas bajo 3,0 bar; 0,7% con 2,5 bar y 18,8% con 3,5 bar. El resultado cambia de orden de magnitud con el umbral.
- **Consecuencias:** KPI-06 no se compara entre períodos ni con otras entregas sin fijar el umbral. Es una señal operacional, nunca criterio sanitario.
- **Dónde se aplica:** T4_eda.PRESION_BAJA_BAR, T4_fichas_kpi.csv (KPI-06), figuras (c) y (a) del notebook.

## D-09: Costo por m³ como razón de sumas y descomposición con identidad

- **Fecha / quién:** 2026-10-17 · Sepu (Benjamín Sepúlveda, T4), con asistencia de OpenCode.
- **Qué era ambiguo:** el Word pide presentar la razón de sumas frente al promedio de razones, sin fijar cuál es el KPI.
- **Alternativas:** promedio de razones horarias (cada hora pesa igual, aunque tenga poco volumen), o razón de sumas (Σ costo / Σ m³).
- **Decisión:** KPI-04 = Σ costo / Σ m³ (razón de sumas). El promedio de razones se informa como comparación. La variación entre meses se descompone en energía por m³ y tarifa, con la identidad costo/m³ = (kWh/m³) × (CLP/kWh) y sin residuo.
- **Evidencia:** 37,61 frente a 38,28 CLP/m³ (+1,8%). Del cambio de agosto a diciembre, 96% es tarifa.
- **Consecuencias:** el KPI no depende del número de horas con poco volumen. La tarifa explica casi todo el alza; no se atribuye a la operación de la red.
- **Dónde se aplica:** T4_eda.costo_m3, T4_costo_m3.csv, KPI-04 y figura de costo.