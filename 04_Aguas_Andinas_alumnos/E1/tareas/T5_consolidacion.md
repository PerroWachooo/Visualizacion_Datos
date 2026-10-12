# T5: Consolidación y entregable

**Responsable:** Byron
**Ítems del Word:** los 4 productos, R1–R4 ("Revisión antes de entregar") y P4 (ranking real) · **Rúbrica:** "Reproducibilidad y claridad" (15 pts) y la coherencia del conjunto
**Script:** [T5_consolidar.py](../T5_consolidar.py) (se ejecuta desde `E1/` con el venv del caso)
**Decisión:** [D-04](../decisiones.md): la consolidación es una tarea propia y la integración sale de la T1.

## Objetivo

Convertir el trabajo de T1–T4 en **lo que se sube al profe**: los 4 productos del Word, completos, coherentes entre sí y en una carpeta que el profe pueda ejecutar desde cero.

## Cuándo

Desde el checkpoint del **D-5**, cuando T1–T4 marquen "listo" en su tarea. Los pasos 1 y 2 se pueden adelantar en cualquier momento, para saber qué falta.

## Pasos

| # | Paso | Cómo | Resultado |
|---|---|---|---|
| 1 | **Cerrar los pendientes de T1–T4** | Recorrer la tabla "Pendientes entre tareas" del [README](../README.md#pendientes-y-consolidación) y confirmar con cada dueño que cerró lo suyo (p. ej., T1: 10.160 sector-horas y `minutos_interrupcion` discreta) | Tabla de pendientes sin filas abiertas |
| 2 | **Ver qué falta** | `python T5_consolidar.py` | Estado ✅/🟡/❌ de insumos y productos |
| 3 | **Ranking real (P4)** | `python T5_consolidar.py --ranking` cuando existan `T3_por_sector.csv` y `T4_por_sector.csv`. Después, elegir y justificar el umbral de cobertura y los 3 sectores ([D-02](../decisiones.md)) | `T2_ranking.csv` + `diagnostico.md` §5 |
| 4 | **Cruzar cifras entre tareas** | Cobertura de T2 (RQ-COM-02 / KRI-01) vs. la de T3; totales de filas. Anotar y explicar las diferencias | Cifras coherentes en el notebook y el PDF |
| 5 | **Unir las fichas** | `python T5_consolidar.py --unir-fichas` | `salidas/tablas/fichas_indicadores.csv` (6 KPI + 6 KRI) |
| 6 | **Diagnóstico** | En el checkpoint se eligen los hallazgos (formato del README: observación, hipótesis, decisión, gráfico, período, unidad, población, limitación). Completar [diagnostico.md](../diagnostico.md): §3 calidad, §4 hallazgos, §5 inspección, §7 plan de limpieza (columna `tratamiento` de `matriz_reglas.csv`), §8 KPI y métricas, §9 IA. Exportar a `E1/Diagnostico.pdf` | PDF de **máx. 5 páginas** |
| 7 | **Notebook final** | Armar `E1/E1_diagnostico.ipynb` con las celdas de T1–T4 en el orden del README, con texto interpretativo entre ellas. Puede importar `comun`, `T2_reglas` y los módulos de T3/T4 | Notebook ejecutado de arriba a abajo |
| 8 | **Versiones** | `python T5_consolidar.py --versiones` | `versiones_probadas.txt` |
| 9 | **Reproducibilidad (R1)** | **Otra persona** (no Byron) ejecuta `E1_diagnostico.ipynb` desde una sesión nueva. Además: `python T5_consolidar.py --empaquetar` y luego `--probar` | Notebook corre en otro computador y desde el .zip |
| 10 | **Revisión final** | `/revisar-entrega E1` (Codex: `$revisar-entrega E1`) y corregir lo que marque | Reporte sin ❌ |
| 11 | **Empaquetar y subir** | `python T5_consolidar.py --empaquetar` (solo funciona si todo está ✅). Subir según lo que confirme el profe | `E1/entregable/Entrega_E1_AguasAndinas.zip` + `Diagnostico.pdf` |

**Antes de subir, confirmar con el profe:** el formato (.zip, archivos sueltos o link al repo) y la fecha de entrega.

## Qué se entrega y qué no

**Se entrega** (lo arma `--empaquetar` en `E1/entregable/Entrega_E1_AguasAndinas/`):

| Producto del Word | Archivo en el entregable |
|---|---|
| 1. Notebook ejecutado desde cero | `E1/E1_diagnostico.ipynb` + los módulos que importa (`comun.py`, `T2_reglas.py`, …) + `datos/`, `metadatos.json`, `diccionario_datos.csv` y las plantillas, para que corra solo |
| 2. Diagnóstico ≤ 5 páginas | `Diagnostico.pdf` (también conviene subirlo suelto) |
| 3. Diccionario, perfil y matriz | `E1/salidas/tablas/diccionario_revisado.csv`, `perfil_calidad.csv`, `matriz_reglas.csv` |
| 4. Fichas de 6 KPI + 6 métricas de calidad | `E1/salidas/tablas/fichas_indicadores.csv` |
| Versiones probadas (README del caso) | `versiones_probadas.txt` + `requirements.txt` |
| Declaración de IA | §9 del PDF (resumen de `uso_ia.md`) |

Además van `LEEME.md` (cómo ejecutar) y las figuras de `salidas/figuras/`.

**No se entrega** (es material interno del grupo): `README.md`, `tareas/`, `decisiones.md` (aunque conviene tenerlo para la defensa E4), los notebooks de trabajo `T1`–`T4` y `T5_consolidar.py`.

## Terminado cuando

- [ ] `python T5_consolidar.py` muestra todo en ✅.
- [ ] El ranking real está corrido y el §5 del diagnóstico tiene los 3 sectores, el umbral justificado y la evidencia a recolectar.
- [ ] Las cifras compartidas entre tareas coinciden, o su diferencia está explicada.
- [ ] Otra persona ejecutó el notebook desde una sesión nueva, y `--probar` pasa.
- [ ] `/revisar-entrega E1` sin ❌.
- [ ] El entregable está subido según el formato que confirmó el profe.

## No hacer

- No correr el ranking con datos de prueba ([D-03](../decisiones.md)).
- No editar `datos/` ni los notebooks de trabajo de otros: si algo de T1–T4 está mal, se le pide al dueño o se corrige en el notebook final, dejándolo anotado.
- No empaquetar con `--forzar` para la entrega real: esa opción es solo para probar.
