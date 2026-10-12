# E1 Diagnóstico y necesidades: qué hay que hacer y cómo nos dividimos

**Grupo Aguas Andinas:** Byron, Bastian, Sepu, Jose
**Peso:** 10%, en equipo, semana 4
**Fecha de entrega:** `____/____/2026` (completar cuando se publique en el aula virtual)

## Fuente de los requisitos

La fuente principal es **[entregas/Aguas_Andinas_E1_Diagnostico.docx](../entregas/Aguas_Andinas_E1_Diagnostico.docx)** (instrucciones y rúbrica). Como complemento se usan la lámina 28 de [01_Datos_y_Diagnostico.pdf](../../01_Datos_y_Diagnostico.pdf) y [trazabilidad_curso.csv](../trazabilidad_curso.csv) (RA1, IL1.1–IL1.2). Si algo de este README contradice el Word, manda el Word.

**Objetivo (Word):** definir qué decisión debe apoyar el análisis y qué riesgos de calidad pueden distorsionarla. No se requiere un dashboard.

**Decisión:** priorizar **3 sectores para inspección** considerando continuidad, diferencia de volúmenes, energía y confiabilidad de la medición. Hay que separar la evidencia operacional de la incertidumbre de los sensores, sin inferir potabilidad ni cumplimiento regulatorio.

## Productos (nombres exactos del Word)

| Producto | Ruta en el repo | Dueño |
|---|---|---|
| `E1_diagnostico.ipynb`, ejecutado desde cero con los 3 lotes y las tablas complementarias | `E1/E1_diagnostico.ipynb` | T5 (integra) |
| `Diagnostico.pdf`, **máx. 5 páginas**: audiencia, decisión, hallazgos, límites y plan de limpieza | `E1/Diagnostico.pdf` (se exporta desde [diagnostico.md](diagnostico.md)) | T5 (§1, §2 y §6 de T1) |
| Diccionario revisado | `E1/salidas/tablas/diccionario_revisado.csv` | T1 |
| `perfil_calidad.csv` | `E1/salidas/tablas/perfil_calidad.csv` | T2 |
| `matriz_reglas.csv`: campo, regla, severidad, denominador, tratamiento propuesto, justificación | `E1/salidas/tablas/matriz_reglas.csv` | T2 |
| Fichas preliminares de **6 KPI** y **6 métricas de calidad**, con trazabilidad a columnas, poblaciones y decisiones | `E1/salidas/tablas/fichas_indicadores.csv` (une `T4_fichas_kpi.csv` + `T2_fichas_calidad.csv`) | T4 + T2; T5 las une |

## Rúbrica (100 puntos)

Cada criterio se califica con 100, 75, 50, 25 o 0% de sus puntos.

| Criterio | Pts | Para el puntaje completo | Tareas |
|---|---|---|---|
| Audiencia y preguntas | 25 | Audiencias, decisión y preguntas medibles conectadas al encargo | T1 |
| EDA y granularidad | 30 | EDA temporal y segmentado; claves y unidades correctas; **ceros y nulos diferenciados** | T4, T3 (+ inventario de T1) |
| Calidad y pertinencia | 30 | 6 métricas de calidad, **sesgo de faltantes**, reglas justificadas con impacto previsto en los KPI | T2, T3 |
| Reproducibilidad y claridad | 15 | Notebook reproducible, diccionario, rutas y límites consistentes | T5 + T1 (diccionario) |

## Checklist completa

Los códigos (W, P, S, R) siguen las secciones del Word.

### Trabajo requerido

| # | Requisito | Tarea | Evidencia |
|---|---|---|---|
| W1 | Audiencia **ejecutiva y operacional**, **3 preguntas medibles** y qué acción podría cambiar con cada respuesta | T1 | `diagnostico.md` §1 |
| W2 | Inventario: archivos, filas, claves, granularidad, períodos, cortes. Diferenciar **filas físicas, entidades y exposición**. Registrar **hash y procedencia** | T1 | `diagnostico.md` §2 + notebook |
| W3 | Variables por tipo, escala, unidad y nulabilidad. Revisar ID, fecha de negocio y fecha de carga. **Proponer contratos de datos** | T1 | `diccionario_revisado.csv` |
| W4 | **≥ 6 análisis:** (a) distribución, (b) categorías, (c) evolución temporal, (d) comparación de segmentos, (e) relación bivariada, (f) faltantes por segmento. Correlación solo entre variables interpretables | T4 (a–e), T3 (f) | notebook + figuras |
| W5 | Calidad **por lote y segmento**. Distinguir **defecto, valor extremo plausible y ausencia estructural**. Estimar qué indicadores sufrirían más sesgo | T2 | `perfil_calidad.csv`, `matriz_reglas.csv` |
| W6 | **6 KPI** (T4) y **6 métricas de calidad** (T2), con denominadores. **≥ 2 límites de interpretación** (T1) | T4, T2, T1 | `fichas_indicadores.csv`, `diagnostico.md` §6 |

### Preguntas y riesgos del caso

| # | Requisito | Tarea | Evidencia |
|---|---|---|---|
| P1 | Continuidad observada y cobertura **por sector y semana**. Límites de continuidad suponiendo **0 y 60 min** de interrupción en las horas desconocidas, **ponderados por conexiones** | T3 | `T3_continuidad_sector_semana.csv` + figura |
| P2 | Costo por m3: separar el efecto del **cambio de unidad**, de **mayor energía** y de la **tarifa**. Presentar **razón de sumas vs. promedio de razones** | T4 | figura + tabla `T4_costo_m3.csv` |
| P3 | **Mapa de calor con ausencia visible**; análisis de presión e interrupciones (una presión baja es solo una señal operacional) | T3 | heatmap |
| P4 | Proponer **3 inspecciones**; comparar el ranking **con y sin filtro de cobertura mínima**; justificar el umbral, las prioridades y la evidencia a recolectar | T2 (fase 2) | `T2_ranking.csv` + `diagnostico.md` §5 |

### Situaciones que deben diagnosticarse

| # | Requisito | Tarea |
|---|---|---|
| S1 | Unidades L y m3 válidas en distintas horas, más unidades desconocidas: normalizar antes de sumar. **Una unidad desconocida no se adivina** | T2 |
| S2 | Salida > entrada e interrupción > 60 min: **incumplen el contrato** (el modelo omite almacenamiento y transferencias) | T2 |
| S3 | Huecos concentrados en algunos sectores: el promedio de lecturas disponibles puede ocultar fallas. **No imputar 0 de interrupción** en horas ausentes | T3 |

### Revisión antes de entregar

| # | Requisito | Quién |
|---|---|---|
| R1 | Un compañero ejecuta `E1_diagnostico.ipynb` **desde una sesión nueva** sin errores | Alguien que no sea Byron (T5) |
| R2 | Cada hallazgo señala gráfico o tabla, período, unidad, población y una limitación | T5 |
| R3 | Se separan **observación, hipótesis y decisión** | T5 |
| R4 | Uso de IA declarado y verificado ([uso_ia.md](uso_ia.md)) | Todos |

## División del trabajo

| Tarea | Foco | Ítems del Word | Responsable |
|---|---|---|---|
| [T1](tareas/T1_pregunta_diccionario.md) | Necesidades, inventario, diccionario y contratos | W1, W2, W3, límites de W6 | José |
| [T2](tareas/T2_calidad.md) | Calidad por lote y segmento, 6 métricas de calidad + código del **ranking de inspección** | W5, W6 (calidad), S1, S2, P4 | Byron |
| [T3](tareas/T3_cobertura_catalogos.md) | Cobertura, continuidad con límites 0/60, heatmap, catálogos y vigencias | W4f, P1, P3, S3 | |
| [T4](tareas/T4_eda_negocio.md) | EDA de negocio (5 análisis), costo por m3, 6 KPI | W4a–e, P2, W6 (KPI) | |
| [T5](tareas/T5_consolidacion.md) | **Consolidación:** pendientes de T1–T4, ranking real, notebook final, PDF, fichas unidas y carpeta entregable ([T5_consolidar.py](T5_consolidar.py)) | 4 productos, R1–R4, P4 (ranking real) | Byron |

### Contrato de tablas por sector (para que el ranking no espere a nadie)

El ranking (P4) cruza criterios de tres tareas. Para no bloquearse, **se acuerda el formato de las tablas, no los valores**. T2, T3 y T4 publican `E1/salidas/tablas/T<n>_por_sector.csv`, con **una fila por `sector_id` (30 filas)**, para el período de ranking. **Propuesta: ago–dic 2025 UTC**, porque es el único período con tarifas y conexiones con vigencia; confirmarlo en el kickoff.

| Archivo | Columnas mínimas |
|---|---|
| `T2_por_sector.csv` | `sector_id, filas, filas_con_defecto, pct_filas_con_defecto` |
| `T3_por_sector.csv` | `sector_id, horas_esperadas, horas_observadas, cobertura_pct, continuidad_obs_pct, continuidad_min_pct, continuidad_max_pct` |
| `T4_por_sector.csv` | `sector_id, m3_entrada, dif_volumen_pct, kwh_por_m3, costo_clp_por_m3` |

Cada tarea publica una **versión preliminar a más tardar el D-7**, aunque los valores cambien después. T2 puede escribir el código del ranking desde el día 1 con datos de prueba en ese formato.

## Cronograma (días relativos a la entrega)

| Día | Qué | Quién |
|---|---|---|
| D-10 | Kickoff de 15 min: repartir T1–T4 (anotar los nombres arriba), confirmar el período del ranking y que todos corran el setup | Todos |
| D-10 a D-5 | Trabajo en paralelo. **D-7:** versión preliminar de `T<n>_por_sector.csv` | Cada uno |
| **D-5** | **Checkpoint:** hallazgos candidatos, cierre de la lista de 6 KPI + 6 métricas de calidad y ranking preliminar | Todos |
| D-4 a D-2 | **T5:** ranking real, unión de fichas, diagnóstico y notebook final. T1–T4 ajustan lo que T5 les pida y pulen figuras y textos | T5 + todos |
| D-1 | R1 (otro compañero ejecuta el notebook desde una sesión nueva), `/revisar-entrega E1`, exportar `Diagnostico.pdf` y `T5_consolidar.py --empaquetar` + `--probar` | T5 + quien esté libre |
| D-0 | Entrega | T5 |

## Setup (una vez por persona)

```bash
cd 04_Aguas_Andinas_alumnos
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd E1 && jupyter lab
```

Cada uno crea su notebook de trabajo en `E1/` (por ejemplo `T2_calidad.ipynb`), con esta primera celda:

```python
import comun
comun.verificar_hashes()
crudo = comun.cargar_lotes()             # 253.404 filas, todo string, columna `lote`
df = comun.parse_exploratorio(crudo)     # tipado + flags (_decimal_coma, _fecha_invalida, _unidad_desconocida, _dup_medicion_id, ...)
```

## Convenciones

- **No editar nada en `datos/`.** El hash se verifica y la limpieza va en código.
- **Archivos propios:** cada uno trabaja en su notebook (`E1/T<n>_<tema>.ipynb`) y no edita notebooks ajenos. `E1_diagnostico.ipynb` lo arma solo T1.
- **Nombres de archivos:** las salidas intermedias llevan el prefijo `T<n>_`. Los **productos del Word** usan el nombre exacto y tienen un solo dueño.
- **Cifras con denominador** ("3.214 de 130.972 filas, 2,5%").
- **Cero ≠ nulo ≠ ausente:**
  - 0 es un valor medido;
  - nulo es una fila que existe pero sin valor;
  - ausente es una hora sin fila (se ve en la grilla).
  La rúbrica lo exige.
- **No adivinar ni imputar sin evidencia:** una unidad desconocida no se convierte, una hora ausente no es 0 de interrupción y las tarifas antes de agosto no son 0.
- **Correlación solo entre variables interpretables** (nunca con IDs). Una asociación no demuestra efecto.
- **Presión baja = señal operacional del escenario;** nunca potabilidad ni cumplimiento regulatorio.
- **Fechas en UTC.** `cargado_en` se compara contra `fecha`, **nunca** contra la fecha actual.
- **Datos simulados:** cada figura lleva la nota (`comun.NOTA_FUENTE`).
- **Uso de IA:** se registra en [uso_ia.md](uso_ia.md) apenas se usa.

### Formato de hallazgo candidato

Cada tarea los escribe al final de su `tareas/T<n>_*.md`. Cumple R2 y R3:

```markdown
### H<n>: <afirmación en una línea>
- Observación: <qué se ve, con cifra (numerador / denominador)>
- Gráfico o tabla: salidas/figuras/T<n>_<id>.png
- Período · unidad · población: <p. ej. ago–dic 2025 UTC · m3 · sector-horas observadas de 30 sectores>
- Hipótesis: <posible explicación, sin afirmarla>
- Decisión o acción: <qué cambia en la priorización o en la limpieza>
- Limitación: <qué NO permite afirmar>
- Dimensión: continuidad | volúmenes | energía | confiabilidad
```

## Pendientes y consolidación

Hay trabajo que **no se puede cerrar dentro de una sola tarea**, porque necesita resultados de otra. Todo eso se registra aquí, para que el grupo sepa qué falta y quién lo hace. **Cada uno actualiza la columna "Estado" de sus filas al avanzar.** Las decisiones que no venían definidas en el Word están en [decisiones.md](decisiones.md).

### Pendientes entre tareas

| Pendiente | Depende de | Dueño | Estado |
|---|---|---|---|
| Ranking real de las 3 inspecciones (P4), con y sin filtro de cobertura | `T3_por_sector.csv` y `T4_por_sector.csv` | T2 (Byron) | Bloqueado: el código está listo y probado con datos de prueba ([D-03](decisiones.md)) |
| Valor oficial de KRI-01 (cobertura) y cruce de RQ-COM-02 con la cobertura de T3 (misma definición de "lectura válida") | Cobertura de T3 | T2 + T3 | Pendiente |
| Corregir "10.000" → **10.160** sector-horas sin recepción en ago–dic (110.160 − 100.000) en `T1_inventario.ipynb` / `T1_preparar.py`; `minutos_interrupcion` es cuantitativa **discreta** (todos sus valores son enteros) | — | T1 (José) | Pendiente |
| Unir `T4_fichas_kpi.csv` + `T2_fichas_calidad.csv` → `fichas_indicadores.csv` | T2 y T4 | T5 | Pendiente |
| Elegir los hallazgos finales del diagnóstico | T1–T4 | Todos (checkpoint) | Pendiente |

### Tarea de consolidación → [T5](tareas/T5_consolidacion.md)

La consolidación es la **T5** (responsable: Byron, [D-04](decisiones.md)). Sus pasos, comandos y la lista de lo que se entrega están en [tareas/T5_consolidacion.md](tareas/T5_consolidacion.md). Para ver en cualquier momento qué falta para entregar:

```bash
cd 04_Aguas_Andinas_alumnos/E1 && ../.venv/bin/python T5_consolidar.py
```

## Skills (Claude Code y Codex)

Las mismas skills están en dos carpetas: [.claude/skills/](../../.claude/skills/) para Claude Code y [.agents/skills/](../../.agents/skills/) para Codex.

| Skill | Claude Code | Codex | Para qué |
|---|---|---|---|
| perfil-calidad | `/perfil-calidad telemetria_horaria` | `$perfil-calidad telemetria_horaria` | `perfil_calidad.csv` y `matriz_reglas.csv` por lote y segmento |
| ficha-indicador | `/ficha-indicador <KPI o métrica>` | `$ficha-indicador <KPI o métrica>` | Ficha en el formato de `plantilla_fichas_indicadores.csv` |
| grafico-diagnostico | `/grafico-diagnostico <qué mostrar>` | `$grafico-diagnostico <qué mostrar>` | Gráfico con las convenciones del curso + interpretación |
| revisar-entrega | `/revisar-entrega E1` | `$revisar-entrega E1` | Contrasta el Word, la checklist y la rúbrica con lo que realmente está en el repo |

Codex también puede activarlas solo cuando el pedido calza con la descripción. Las instrucciones generales del repo están en `CLAUDE.md` (Claude Code) y `AGENTS.md` (Codex), con el mismo contenido.

**Si editas una skill o las instrucciones, sincroniza la otra copia** (desde la raíz del repo):

```bash
rsync -a --delete .claude/skills/ .agents/skills/   # o al revés si editaste la de Codex
diff -r .claude/skills .agents/skills               # no debe mostrar diferencias
```

Con `CLAUDE.md` y `AGENTS.md` aplica el mismo cambio en ambos (solo difieren en el encabezado).
