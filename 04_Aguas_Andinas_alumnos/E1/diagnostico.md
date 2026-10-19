# Diagnóstico y necesidades: Aguas Andinas, continuidad y eficiencia operacional

**E1 · Grupo Aguas Andinas:** Byron, Bastian, Sepu, Jose · Visualización de Datos 2026 S2 · Prof. Viktor Tapia

*Datos y metas 100% simulados con fines docentes; no representan instalaciones ni resultados reales de la empresa. Fechas en UTC.*

## 1. Audiencias, decisión y preguntas

- **Audiencia ejecutiva:** jefatura ficticia de operaciones y planificación, que decide cómo asignar tres inspecciones y recursos; necesita prioridades comparables, cobertura e incertidumbre.
- **Audiencia operacional:** equipo ficticio de terreno, telemetría y mantenimiento, que define qué revisar y qué evidencia levantar; necesita detalle por sector y semana.
- **Decisión:** priorizar tres sectores para inspección.

| # | Pregunta medible | Indicador / cálculo | Período · población | Acción que cambia según la respuesta |
|---|---|---|---|---|
| 1 | ¿Qué sectores podrían quedar bajo la meta docente de continuidad considerando las horas desconocidas? | Continuidad ponderada por conexiones, observada y con límites 0/60 min; comparar con 99,5%. | Ene–dic 2025 · sector-horas por sector | Priorizar sectores cuyo límite superior queda bajo la meta; recopilar evidencia si el intervalo cruza la meta. |
| 2 | ¿Dónde es mayor la diferencia entre volumen de entrada y salida? | Σ(entrada − salida) / Σ entrada, en m³ tras convertir L; con volumen válido y denominador positivo. | Ene–dic 2025 · lecturas con ambos volúmenes convertibles | Revisar balance y medición, sin inferir causa solo por asociación. |
| 3 | ¿Qué tres sectores combinan señales operacionales y medición confiable para inspección? | Ranking de continuidad, diferencia, kWh/m³, costo CLP/m³ y calidad; con y sin filtro de cobertura mínima. | Ago–dic 2025 · 30 sectores | Asignar tres inspecciones y definir evidencia sobre operación y sensores según cambie el ranking. |

**Fuera de alcance:** potabilidad, cumplimiento regulatorio, causalidad, predicción.

## 2. Inventario de la fuente

| Tabla | Rol | Filas | Clave | Granularidad | Período / corte |
|---|---|---|---|---|---|
| `base/telemetria_horaria.csv` | Hecho | 130.972 | `medicion_id` | Sector-hora | Ene–jun 2025 · corte 2025-07-08 |
| `actualizacion/telemetria_horaria.csv` | Hecho | 22.432 | `medicion_id` | Sector-hora | Jul 2025 · corte 2025-08-08 |
| `ampliacion/telemetria_horaria.csv` | Hecho | 100.000 | `medicion_id` | Sector-hora | Ago–dic 2025 · corte 2026-01-08 |
| `dimensiones/sectores.csv` | Dimensión fuente | 30 | `sector_id` | Una fila por sector | Catálogo original |
| `dimensiones/metas_ancho.csv` | Dimensión fuente | 30 | `sector_id + indicador` | Meses en columnas | Ene–jul; reemplazada |
| `complementarios/sectores_historial.csv` | Dimensión con vigencia | 60 | `sector_id + vigente_desde` | Sector y versión | Corte de versión 2025-10-01 |
| `complementarios/tarifas_energia.csv` | Complementaria | 150 | `sector_id + mes` | Sector-mes | Ago–dic 2025 |
| `complementarios/metas_2025_ancho.csv` | Dimensión | 30 | `sector_id + indicador` | Meses en columnas | Ene–dic; hacer *melt* |

- **Filas físicas vs. entidades vs. exposición:** 253.404 filas de telemetría (incluyen repeticiones), 30 sectores válidos y 262.800 sector-horas esperadas (130.320 + 22.320 + 110.160). La grilla define la exposición para la cobertura; ago–dic recibió 100.000 filas para 110.160 sector-horas (10.160 nunca llegaron).
- **Hash y procedencia:** los ocho archivos se verifican con SHA-256 contra `metadatos.json`. Paquete v2, UTF-8, UTC, semillas 20260924 y 20261004, fecha de paquete 2026-10-01. Datos 100% sintéticos; el nombre de la empresa es contexto docente.

## 3. Calidad y pertinencia

Se evaluaron 27 reglas por lote (`matriz_reglas.csv`) y un perfil por lote, sector, mes y modo (`perfil_calidad.csv`). Cada problema se clasifica como:
- **Defecto:** incumple el contrato del dato. Se dividen en:
  - *recuperables*, porque el formato está documentado: coma decimal (600), fecha dd/mm (500), modo con espacios (1.567);
  - *no recuperables*: 764 copias exactas, 353 fechas imposibles, 609 filas de sector inexistente, 250 volúmenes `PENDIENTE`, 250 unidades desconocidas, 1.012 entradas negativas, 350 salidas > entrada, 350 interrupciones de 90 min y 3.732 volúmenes vacíos.
- **Extremo plausible**, que se marca y no se borra: 4.506 presiones y 146 energías fuera de 1,5 RIC de su sector, en su mayoría presiones bajas.
- **Ausencia estructural**, que no es defecto: no hay tarifas en ene–jul (153.251 filas) y `metas_ancho` no trae ago–dic.

**Métricas de calidad** (ene–dic, con denominador propio):

| Métrica | Valor |
|---|---|
| Cobertura de lecturas válidas | 251.682 de 262.800 sector-horas (95,8%) |
| Copias exactas | 764 de 253.404 filas (0,30%) |
| Unidad desconocida | 250 de 253.404 (0,10%) |
| Salida > entrada | 350 de 248.160 (0,14%) |
| Interrupción fuera de 0–60 min | 350 de 253.404 (0,14%) |
| Atraso de carga > 2 h | 34.016 de 253.051 (13,4%) |

**Sesgo de faltantes:** las horas sin lectura se concentran en A-S26 a A-S29, con 76% de cobertura. Por eso su continuidad solo se acota entre ≈ 72,5% (si las horas faltantes tuvieron 60 min de corte) y ≈ 97,6% (si tuvieron 0). Un promedio sobre lo disponible ocultaría esas horas.

**KPI más sensibles a un mal tratamiento** (ene–dic):
- Sumar litros como m³ hunde la intensidad energética en un 99,4% (0,265 → 0,0015 kWh/m³).
- Incluir entradas negativas y salida > entrada baja la diferencia de volúmenes de 16,1% a 15,3%.
- La continuidad cambia en décimas de punto si se usan los minutos > 60 (−0,21) o si las horas ausentes se cuentan como 0 min (+0,07). Esa diferencia importa frente a una meta de 99,5%.

**Pertinencia:** la fuente sirve para **comparar sectores entre sí** y priorizar. No sirve para afirmar el cumplimiento exacto de la meta en sectores con baja cobertura, ni para atribuir causas.

## 4. Hallazgos

### H1: El grupo A-S20 a A-S29 concentra la diferencia de volúmenes y los datos faltantes
- **Observación:**
  - En ago–dic, A-S20 a A-S29 pierden el 24,0% del volumen de entrada (29.002 lecturas con volumen válido), contra 15,0% del resto (67.048 lecturas), tanto en m³ como en L. El grupo saltó de 13% a 21% en abril y a 24% en agosto.
  - Ese mismo grupo tiene los 2.200 de 2.200 volúmenes vacíos de ago–dic (6,95% de sus 31.645 lecturas).
  - A-S26 a A-S29 reúnen 3.505 de las 10.660 sector-horas sin lectura válida, con 76,1% de cobertura (11.183 de 14.688).
- **Hipótesis:** un cambio de medición en la entrada o la salida, o una pérdida real. Estos datos no permiten separar ambas explicaciones.
- **Decisión:** priorizar inspecciones en este grupo, empezando por los medidores (D-02).
- *Figuras: `T4_d_segmentos.png`, `T2_nulos_por_sector.png`, `T3_cobertura_interrupciones.png` · ago–dic 2025 · % de m³ y % de lecturas · 30 sectores. Limitación: el grupo se identificó en los datos; no se atribuye fuga ni falla de sensor.*

### H2: La meta de continuidad no distingue sectores: los 30 quedan bajo 99,5%
- **Observación:**
  - Incluso suponiendo 0 minutos de corte en las horas desconocidas, la continuidad ponderada por conexiones va de 96,49% a 98,97% en ago–dic: 30 de 30 sectores bajo la meta.
  - Las horas en mantenimiento tienen interrupción en 6.206 de 6.206 casos, contra 4.596 de 245.126 en operación normal (1,9%).
- **Hipótesis:** el modo de mantenimiento registra cortes planificados.
- **Decisión:** priorizar por posición relativa (percentiles) y no por cumplimiento de la meta; separar mantenimiento de operación normal en el KPI de interrupciones.
- *Figura: `T3_continuidad_limites.png` · ago–dic 2025 · % de minutos-conexión · 30 sectores. Limitación: los límites 0/60 son escenarios extremos, no probabilidades; la meta es docente.*

### H3: Ago–dic, el período del ranking, es el lote menos confiable
- **Observación:**
  - 21.379 de 99.800 lecturas (21,4%) llegan con más de 2 h de atraso, contra 10.801 de 130.841 (8,3%) en ene–jun. Ago–dic es peor también con umbrales de 1, 3 y 6 h.
  - Ago–dic trae 7 tipos de defecto que no existían en ene–jul.
  - Le faltan 10.660 de 110.160 sector-horas válidas (9,7%), contra 0,3% en ene–jul.
- **Hipótesis:** otro proceso de captura o de transmisión en ago–dic. No es verificable con estos datos.
- **Decisión:** reportar cada KPI de ago–dic junto a su cobertura. En un tablero, advertir que las horas recientes pueden estar incompletas.
- *Figuras: `T2_atraso_carga.png`, `T2_reglas_por_lote.png` · ene–dic 2025 por lote · % de filas · 253.051 lecturas con ambas fechas válidas. Limitación: el % exacto depende de interpretar `"latency": 2` como horas (D-01); la comparación entre lotes no depende de ello.*

### H4: El costo por m³ sube 15,8% por la tarifa, y no convertir unidades lo distorsiona todo
- **Observación:**
  - El costo de energía por m³ sube de 34,89 a 40,40 CLP entre agosto y diciembre. El 96% del alza (5,28 de 5,51 CLP/m³) se explica por la tarifa y no por la energía por m³.
  - La razón de sumas da 37,61 CLP/m³ y el promedio de razones horarias, 38,28.
  - Sin convertir litros, el costo daría 0,15 CLP/m³.
- **Hipótesis:** el alza refleja el cambio de tarifa del escenario, no un cambio de la operación.
- **Decisión:**
  - usar la razón de sumas como KPI;
  - separar los efectos de energía y de tarifa;
  - convertir L → m³ antes de sumar y excluir la unidad desconocida.
- *Figuras: `T4_costo_m3.png`, `T2_sesgo_kpi.png` · ago–dic 2025 · CLP/m³ · 96.050 lecturas con volumen válido y tarifa. Limitación: no hay tarifas antes de agosto y su ausencia no es 0.*

## 5. Propuesta de inspección

**Método:**
- **Puntaje:** promedio de los percentiles de continuidad observada, diferencia de volúmenes y energía (kWh/m³ y CLP/m³, promediados como un solo criterio).
- **Tipo de inspección:** la confiabilidad del dato decide si se revisa el **sensor primero** (más de 2 × la mediana de filas con defecto, ≈ 4,6%) o la **operación** (D-02).
- **Filtro de cobertura:** **80%**. Excluye solo a A-S26 a A-S29 (≈ 76%), cuya continuidad es demasiado incierta para compararla. Con filtros de 80, 85 y 90% el resultado es idéntico, y ningún sector llega a 95% (el máximo es 93,3%).

| # | Sector | Por qué (percentiles, 1 = peor) | ¿Cambia con el filtro? | Inspección y evidencia a recolectar |
|---|---|---|---|---|
| 1 | **A-S20** | Continuidad 0,96 (96,3% observada); diferencia 0,96 (24,0%); energía 0,69. Cobertura 92,0% | No | **Sensor primero:** 316 de 3.386 lecturas con defecto (9,3%). Contrastar los medidores de entrada y salida y la transmisión de volumen; después, la operación |
| 2 | **A-S25** | Continuidad 0,85 (96,9%); diferencia 0,88 (24,0%); energía 0,85 (0,304 kWh/m³). Cobertura 92,8% | No | **Sensor primero:** 311 de 3.416 lecturas con defecto (9,1%). Mismo contraste de medidores y revisión de la presión |
| 3 | **A-S10** | Energía 0,92: 0,324 kWh/m³ y 43,7 CLP/m³, contra medianas de 0,263 y 38,6. Continuidad 0,69; diferencia 0,77 (15,1%) | No | **Operación:** 80 de 3.424 lecturas con defecto (2,3%). Revisar bombeo, horario de las bombas y presión |

Sin filtro, A-S27 quedaba 5.º. A-S26 a A-S29 requieren primero recuperar su transmisión de datos, para poder evaluarlos. **Advertencia:** los percentiles amplifican diferencias pequeñas entre los sectores cercanos a 15% de diferencia de volúmenes (14,9–15,1%). La elección de A-S10 descansa sobre todo en su energía, que es claramente mayor.

## 6. Límites de interpretación

1. Los datos y metas son sintéticos; no permiten inferir potabilidad, cumplimiento regulatorio ni resultados reales de la empresa.
2. Los faltantes generan límites de continuidad y pueden cambiar el ranking; un promedio sobre lecturas disponibles no representa necesariamente el sector completo.
3. Una asociación entre presión, energía, interrupciones o diferencia de volúmenes no demuestra causalidad; el modelo omite almacenamiento y transferencias.
4. Dos umbrales son decisiones del grupo y no vienen dados por la fuente: el atraso > 2 h (D-01) y la presión baja < 3,0 bar (D-08). Sus resultados se informan con sensibilidad.

## 7. Plan de limpieza para la E2

Cada paso queda en la bitácora, y los originales no se modifican.

| Acción | Casos |
|---|---|
| **Recuperar con regla documentada** | Coma decimal → punto; fecha dd/mm → UTC; `modo_operacion` con strip y minúsculas; L → m³ (43.020 filas) |
| **Deduplicar** | 764 copias exactas, conservando una por `medicion_id` |
| **Excluir sin imputar** de los KPI afectados | Fechas imposibles, sector inexistente, `PENDIENTE`, unidad desconocida (no se adivina), entrada negativa, salida > entrada, volúmenes vacíos |
| **Tratar como desconocido** | Interrupciones > 60 min: la hora entra a los límites 0/60, no se recorta a 60 |
| **Marcar sin borrar** | Extremos de presión y energía; lecturas atrasadas y cargas anteriores a la hora medida |
| **Respetar ausencias estructurales** | Tarifas solo ago–dic; usar `metas_2025_ancho` con *melt* (sin concatenar versiones); horas ausentes visibles en la grilla |

## 8. KPI y métricas de calidad

Las 12 fichas están en `fichas_indicadores.csv`, con fórmula, numerador, denominador, población, tratamiento de nulos, umbral y acción. Valores de ago–dic:

| KPI | Fórmula | Valor |
|---|---|---|
| KPI-01 Continuidad ponderada | 1 − min. interrumpidos / min. de conexión (límites 0/60) | 30 de 30 sectores bajo 99,5% |
| KPI-02 Diferencia de volúmenes | Σ(entrada − salida) / Σ entrada | 18,2% (96.050 lecturas) |
| KPI-03 Intensidad energética | Σ kWh / Σ m³ de entrada | 0,264 kWh/m³ |
| KPI-04 Costo de energía | Σ(kWh × tarifa) / Σ m³ | 37,61 CLP/m³ |
| KPI-05 Horas con interrupción | horas con min > 0 / horas válidas | 5,0% (de 99.150) |
| KPI-06 Horas con presión baja | horas < 3,0 bar / lecturas válidas | 2,2% (de 99.500) |

Las 6 métricas de calidad (KRI-01 a KRI-06) están en la sección 3.

## 9. Declaración de uso de IA

Se usaron:
- **Claude Code**, en T2, T5 y la estructura;
- **Codex**, en T1 y T3;
- **OpenCode con Claude Haiku**, en T4.

En todos los casos se verificó:
- ejecutando cada notebook desde un kernel nuevo, sin errores;
- contrastando las cifras entre tareas (por ejemplo, 99.500 lecturas válidas de ago–dic en T2, T3 y T4);
- comprobando los hashes de los datos originales;
- revisando las figuras a mano.

Una revisión cruzada corrigió errores de la IA, como una ficha con un tipo mal escrito y un notebook con un error guardado. El detalle por integrante está en `uso_ia.md`.
