---
name: ficha-indicador
description: Redacta fichas de KPI de negocio o de métricas de calidad del caso Aguas Andinas en el formato de plantilla_fichas_indicadores.csv, con fórmula, numerador, denominador, población, tratamiento de nulos y ausentes, y trazabilidad a columnas y decisiones; verifica que la fórmula sea computable con los datos. Usar en E1 (fichas preliminares de 6 KPI y 6 métricas de calidad), E3 (fichas finales con umbral y responsable) y E4 (cambio de fórmula, filtro o umbral).
---

# Ficha de indicador

Pedido: el KPI o métrica que indique el usuario, o el conjunto completo (6 KPI o 6 métricas de calidad). Las listas propuestas para la E1 están en `04_Aguas_Andinas_alumnos/E1/tareas/T4_eda_negocio.md` (KPI) y `T2_calidad.md` (calidad).

## Formato

Columnas exactas de `04_Aguas_Andinas_alumnos/plantilla_fichas_indicadores.csv`:

`id, tipo_KPI_KRI_visual, objetivo, formula, numerador, denominador, unidad, granularidad, fuente_columnas, filtros, periodo_corte, tratamiento_nulos, umbral, version_umbral, responsable, accion`

| Columna | Cómo llenarla en este caso |
|---|---|
| `id` | Estable entre entregas: `KPI-01`…`KPI-06`, `KRI-01`…`KRI-06` |
| `tipo_KPI_KRI_visual` | `KPI` (negocio), `KRI` (calidad o riesgo del dato) o `visual` (efectividad del dashboard, E3) |
| `objetivo` | Qué pregunta de la audiencia responde y a qué dimensión de la decisión apunta (continuidad, diferencia de volúmenes, energía o confiabilidad) |
| `formula` | Explícita y agregada. Para cocientes, decir si es **razón de sumas** (Σa/Σb) o **promedio de razones** (media de a/b) y por qué |
| `numerador` / `denominador` | Con unidad y población. El denominador nunca es implícito |
| `granularidad` | A qué nivel se calcula y a cuál se reporta, por ejemplo sector-hora → sector × semana |
| `fuente_columnas` | Columnas y tablas exactas, incluidas las convertidas (`volumen_entrada_m3`) y la unión con `sectores_historial` o `tarifas_energia` si aplica |
| `filtros` | Población: lotes, período, exclusiones (filas que incumplen el contrato, unidad desconocida…) con su criterio |
| `periodo_corte` | Período UTC y corte del lote (2025-07-08, 2025-08-08, 2026-01-08) |
| `tratamiento_nulos` | Distinguir **cero, nulo y hora ausente**. Nunca imputar 0 de interrupción ni tarifa 0. Una unidad desconocida no se convierte. Si aplica, usar los límites 0/60 de continuidad |
| `umbral` | Meta docente si existe (continuidad 99,5%, sentido mínimo, `metas_2025_ancho.csv`); si no, "por definir (E3)" o un umbral justificado |
| `version_umbral` | `v0-E1` para las fichas preliminares; se sube la versión en cada cambio (E4) |
| `responsable` | Rol o integrante que hace el seguimiento |
| `accion` | Qué decisión cambia si el indicador cruza el umbral, por ejemplo "entra a la lista de inspección" |

## Reglas del caso

- **Volúmenes en m3:** litros / 1000. Con una unidad desconocida no hay conversión.
- **Continuidad:** ponderada por las `conexiones` **vigentes en cada hora** (`sectores_historial`, desde inclusivo y hasta exclusivo). Las conexiones no se suman como clientes únicos.
- **Costo de energía:** `energia_kwh × tarifa_kwh_clp`, solo ago–dic. Antes de agosto está fuera de alcance, no es 0.
- **Presión baja:** es una señal operacional del escenario. No es un criterio sanitario ni regulatorio.

## Verificación

Antes de entregar la ficha, **calcular el indicador una vez** con `comun.parse_exploratorio(...)` (E1) o con el pipeline vigente. Se reporta en la respuesta el valor global, con su numerador y denominador, para demostrar que la fórmula es computable con las columnas declaradas. Si no lo es, corregir la ficha.

## Salida

- Ruta: `E<n>/salidas/tablas/T<n>_fichas_<kpi|calidad>.csv`, una fila por indicador, con el prefijo de la tarea de quien lo pide.
- En la E1, T1 une las fichas en `E1/salidas/tablas/fichas_indicadores.csv`.
- En la respuesta: una tabla `id | nombre | fórmula | valor preliminar (n/N)` y cualquier supuesto que el equipo deba confirmar.
