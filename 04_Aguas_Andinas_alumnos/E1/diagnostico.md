# Diagnóstico y necesidades: Aguas Andinas, continuidad y eficiencia operacional

**E1 · Grupo Aguas Andinas:** Byron, Bastian, Sepu, Jose · Visualización de Datos 2026 S2 · Prof. Viktor Tapia
*Datos y metas 100% simulados con fines docentes; no representan instalaciones ni resultados reales de la empresa.*

<!--
Se exporta a E1/Diagnostico.pdf. MÁXIMO 5 PÁGINAS.
Cada cifra va con su denominador ("n de N, x%"). Cada hallazgo debe indicar gráfico o tabla, período, unidad,
población y limitación, y separar observación, hipótesis y decisión (Word, "Revisión antes de entregar").
Los comentarios indican qué tarea aporta el insumo; se borran antes de exportar.
-->

## 1. Audiencias, decisión y preguntas
<!-- T1 Parte A · W1 · Rúbrica "Audiencia y preguntas" (25 pts) -->
- **Audiencia ejecutiva:** jefatura ficticia de operaciones y planificación, que decide cómo asignar tres inspecciones y recursos; necesita prioridades comparables, cobertura e incertidumbre.
- **Audiencia operacional:** equipo ficticio de terreno, telemetría y mantenimiento, que define qué revisar y qué evidencia levantar; necesita detalle por sector y semana.
- **Decisión:** priorizar tres sectores para inspección.

| # | Pregunta medible | Indicador / cálculo | Período · población | Acción que cambia según la respuesta |
|---|---|---|---|---|
| 1 | ¿Qué sectores podrían quedar bajo la meta docente de continuidad considerando las horas desconocidas? | Continuidad ponderada por conexiones, observada y con límites 0/60 min; comparar con 99,5%. | Ene–dic 2025 UTC · sector-horas por sector | Priorizar sectores cuyo límite superior queda bajo la meta; recopilar evidencia si el intervalo cruza la meta. |
| 2 | ¿Dónde es mayor la diferencia entre volumen de entrada y salida? | Σ(entrada − salida) / Σ entrada, en m³ tras convertir L; con volumen válido y denominador positivo. | Ene–dic 2025 UTC · lecturas con ambos volúmenes convertibles | Revisar balance y medición, sin inferir causa solo por asociación. |
| 3 | ¿Qué tres sectores combinan señales operacionales y medición confiable para inspección? | Ranking de continuidad, diferencia, kWh/m³, costo CLP/m³ disponible y calidad; con y sin filtro de cobertura mínima. | Ago–dic 2025 UTC · 30 sectores | Asignar tres inspecciones y definir evidencia sobre operación y sensores según cambie el ranking. |

**Fuera de alcance:** potabilidad, cumplimiento regulatorio, causalidad, predicción.

## 2. Inventario de la fuente
<!-- T1 Parte B · W2. Tabla corta; el detalle va en el notebook y en diccionario_revisado.csv -->

| Tabla | Rol | Filas | Clave | Granularidad | Período / corte |
|---|---|---|---|---|---|
| `datos/base/telemetria_horaria.csv` | Hecho | 130.972 | `medicion_id` | Sector-hora UTC | Ene–jun 2025 · corte 2025-07-08 |
| `datos/actualizacion/telemetria_horaria.csv` | Hecho | 22.432 | `medicion_id` | Sector-hora UTC | Jul 2025 · corte 2025-08-08 |
| `datos/ampliacion/telemetria_horaria.csv` | Hecho | 100.000 | `medicion_id` | Sector-hora UTC | Ago–dic 2025 · corte 2026-01-08 |
| `datos/dimensiones/sectores.csv` | Dimensión fuente | 30 | `sector_id` | Una fila por sector | Catálogo original |
| `datos/dimensiones/metas_ancho.csv` | Dimensión fuente | 30 | `sector_id + indicador` | Sector-indicador; meses en columnas | Ene–jul; reemplazada analíticamente |
| `datos/complementarios/sectores_historial.csv` | Dimensión SCD | 60 | `sector_id + vigente_desde` | Sector y versión vigente | Vigencia desde ene 2025; corte de versión 2025-10-01 |
| `datos/complementarios/tarifas_energia.csv` | Complementaria | 150 | `sector_id + mes` | Tarifa sector-mes | Ago–dic 2025 |
| `datos/complementarios/metas_2025_ancho.csv` | Dimensión | 30 | `sector_id + indicador` | Sector-indicador; meses en columnas | Ene–dic; hacer melt |

- **Filas físicas vs. entidades vs. exposición:** 253.404 filas de telemetría (incluyen repeticiones), 30 sectores válidos y 262.800 sector-horas esperadas (130.320 base + 22.320 actualización + 110.160 ampliación). No son medidas intercambiables; la grilla define la exposición para cobertura.
- **Hash y procedencia:** los ocho archivos se verifican con SHA-256 contra `metadatos.json` desde `comun.verificar_hashes()`. Paquete v2, UTF-8, UTC, semillas 20260924 y 20261004, fecha de paquete 2026-10-01. Datos 100% sintéticos; el nombre de empresa es contexto docente.

## 3. Calidad y pertinencia
<!-- T2 (perfil_calidad, matriz_reglas) + T3 (cobertura, uniones) · W5 · Rúbrica "Calidad y pertinencia" (30 pts)
     Solo lo que importa para la decisión: defectos vs. extremos plausibles vs. ausencias estructurales, sesgo de faltantes, KPI más afectados -->

## 4. Hallazgos
<!-- Elegidos en el checkpoint del D-5. Cada uno con el formato del README -->

### Hallazgo 1:
- **Observación:**
- **Hipótesis:**
- **Decisión o acción:**
- *Figura o tabla · período · unidad · población · limitación:*

### Hallazgo 2:

### Hallazgo 3:

## 5. Propuesta de inspección
<!-- T2 Parte C · P4: ranking con y sin filtro de cobertura mínima, umbral justificado, 3 sectores, evidencia a recolectar -->

| Prioridad | Sector | Por qué (criterios) | ¿Cambia con el filtro de cobertura? | Evidencia a recolectar |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

## 6. Límites de interpretación (mínimo 2)
<!-- T1 · W6 -->
1. Los datos y metas son sintéticos; no permiten inferir potabilidad, cumplimiento regulatorio ni resultados reales de la empresa.
2. Los faltantes generan límites de continuidad y pueden cambiar el ranking; un promedio sobre lecturas disponibles no representa necesariamente el sector completo.
3. Asociación entre presión, energía, interrupciones o diferencia de volúmenes no demuestra causalidad; el modelo omite almacenamiento y transferencias.

## 7. Plan de limpieza para la E2
<!-- Desde matriz_reglas.csv (columna tratamiento): qué se corrige, qué se excluye, qué se marca y qué NO se recupera por falta de evidencia -->

## 8. KPI y métricas de calidad
<!-- Resumen de fichas_indicadores.csv: 6 KPI (T4) + 6 métricas de calidad (T2), con fórmula y denominador -->

## 9. Declaración de uso de IA
<!-- Resumen de uso_ia.md -->
