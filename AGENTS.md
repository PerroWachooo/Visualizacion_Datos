# AGENTS.md

This file provides guidance to OpenAI Codex (and other AGENTS.md-compatible agents) when working with code in this repository.

## Contexto

Repositorio del grupo **Aguas Andinas** para la asignatura Visualización de Datos (2026 S2, prof. Viktor Tapia). Es un proyecto de análisis de datos y dashboard; no es una aplicación de software. Todo el trabajo vive en [04_Aguas_Andinas_alumnos/](04_Aguas_Andinas_alumnos/). Los PDF de la raíz son material del curso (programa, tópicos, clase 01).

Los datos son **100% sintéticos** (semilla 20260924 / 20261004). No inferir potabilidad, cumplimiento regulatorio ni resultados reales de la empresa; las metas y presiones son supuestos docentes.

**Decisión de negocio que debe responder todo el análisis:** priorizar tres sectores para inspección considerando continuidad, diferencia de volúmenes (entrada − salida), energía y confiabilidad de medición, separando la evidencia operacional de la incertidumbre de los sensores.

## Entorno y comandos

Todo se ejecuta desde `04_Aguas_Andinas_alumnos/` (el notebook usa `Path.cwd()` como base). Python ≥ 3.11; el Python del sistema no trae pandas, así que hay que crear un entorno:

```bash
cd 04_Aguas_Andinas_alumnos
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter lab 00_inicio.ipynb          # notebook de inicio del curso; el entregable de cada E vive en E<n>/ (E1: E1/E1_diagnostico.ipynb)
streamlit run <app>.py               # dashboard de E3 (streamlit está en requirements)
```

Al entregar se deben registrar las versiones de paquetes probadas (`pip freeze`). No hay tests ni linter configurados.

La primera celda de `00_inicio.ipynb` verifica el SHA-256 de cada archivo contra `metadatos.json` y carga los tres lotes con `dtype="string"`. **Los CSV de `datos/` no deben modificarse nunca**: si se editan, falla esa verificación. Toda limpieza va en código, y cada transformación se registra en la bitácora.

## Modelo de datos

Hecho principal: `telemetria_horaria`, donde cada fila es un sector durante una hora UTC (`fecha` = inicio de la hora). PK nominal `medicion_id`, FK `sector_id` (30 sectores `A-S00`…`A-S29`, disjuntos).

| Lote | Período | Corte UTC | Filas |
|---|---|---|---|
| `datos/base/` | ene–jun 2025 | 2025-07-08 | 130.972 |
| `datos/actualizacion/` | jul 2025 | 2025-08-08 | 22.432 |
| `datos/ampliacion/` | ago–dic 2025 | 2026-01-08 | 100.000 |

Los tres lotes se usan desde E1. Cada lote conserva su fecha de corte: la incorporación de un lote no actualiza retroactivamente los snapshots anteriores.

Tablas complementarias (son dimensiones, **no** se concatenan como observaciones):
- `complementarios/sectores_historial.csv`: SCD con `vigente_desde` (inclusivo) y `vigente_hasta` (exclusivo). Se une por sector + `fecha` dentro de la vigencia, y debe haber exactamente una coincidencia por hecho. Las `conexiones` cambian desde octubre y son el peso para ponderar continuidad; no se suman como clientes únicos por hora. Reemplaza analíticamente a `dimensiones/sectores.csv`, que se conserva como fuente.
- `complementarios/tarifas_energia.csv`: N:1 por `sector_id` + `mes` (`YYYY-MM`), **solo ago–dic**. Costo energía = `energia_kwh × tarifa_kwh_clp`. La ausencia antes de agosto queda fuera de alcance; no se rellena con ceros.
- `complementarios/metas_2025_ancho.csv`: formato ancho (`m2025_01`…`m2025_12`), único indicador `continuidad_pct` con sentido `minimo`. Hay que hacerle `melt` a formato largo. **Sustituye** a `dimensiones/metas_ancho.csv` (ene–jul): no concatenar ambas.

**Grilla esperada:** calendario UTC horario × 30 sectores, con left join hacia los hechos limpios. Las horas sin lectura deben quedar visibles en la cobertura (ago–dic espera 110.160 sector-horas y llegan 100.000).

## Problemas de calidad conocidos en los datos crudos

Se deben resolver en el pipeline y documentar como reglas de calidad:
- `medicion_id` duplicados: 652 en base y 112 en actualización (253.404 filas vs. 252.640 claves distintas). Las 764 repeticiones son copias exactas de fila. Entre sectores válidos no hay sector-horas repetidas con distinto `medicion_id`: las 17 repeticiones aparentes de `sector_id` + `fecha` son filas `NO_EXISTE`.
- `unidad_volumen` mezcla `m3` y `L`, y en ampliación aparece `unidad?`: dividir L por 1000 antes de sumar o comparar; con unidad desconocida no hay conversión válida.
- `volumen_entrada` tiene nulos, el texto `PENDIENTE` y valores negativos; en algunas filas `volumen_salida` > `volumen_entrada`.
- `modo_operacion` trae variantes de mayúsculas y espacios (`" NORMAL "`, `" MANTENIMIENTO "`) en los tres lotes.
- En ampliación algunos números vienen con coma decimal entre comillas (`"518,658"`, sin separador de miles), así que hay que leer con un parser CSV real y no con `split(',')`. Además, unas 500 fechas vienen como `dd/mm/YYYY HH:MM:SS` (UTC) en vez de ISO 8601. En los tres lotes hay fechas imposibles (`2025-02-30`, `2025-11-31`).
- `sector_id = NO_EXISTE` en algunas filas, sin match en el catálogo.
- `minutos_interrupcion` debe estar entre 0 y 60, pero hay valores de hasta 90. `capacidad_m3_h` sirve para detectar magnitudes anómalas.
- `cargado_en` indica la **primera** carga; sirve para medir latencia contra `fecha` (latencia esperada: 2). Hay cargas anteriores al evento. Nunca se compara la antigüedad con la fecha actual.

Los catálogos complementarios están limpios: `sectores_historial` tiene 2 versiones por sector con corte el 2025-10-01; las tarifas tienen 30 × 5 meses sin duplicados; las dos tablas de metas coinciden en ene–jul (todo 99,5).

## Entregables y plantillas

E1 Diagnóstico (10%), E2 Preparación (15%), E3 Dashboard (25%), E4 Defensa individual (10%), que deben cubrir lo pedido en `trazabilidad_curso.csv` (RA/IL por entrega). Requisitos transversales: 6 KPI de negocio, 6 métricas de calidad, entre 4 y 6 gráficos, sin modelos predictivos. El uso de IA debe declararse y verificarse, y las pruebas con usuarios deben ser reales (no inventar datos de participantes). E4 prueba una reingesta idempotente y un cambio de filtro, fórmula, política o vigencia.

Las plantillas `plantilla_*.csv` (bitácora, fichas de indicadores, pruebas de usuarios, reglas de calidad) definen las columnas exactas que deben tener esos entregables. `diccionario_datos.csv` documenta cada campo.

Las instrucciones y rúbricas de cada entrega van en `04_Aguas_Andinas_alumnos/entregas/` y **son la fuente principal de requisitos**: mandan sobre el programa y las láminas. Se leen con `textutil -convert txt -stdout <archivo>.docx`.
- **E1:** está `entregas/Aguas_Andinas_E1_Diagnostico.docx`. Productos: `E1_diagnostico.ipynb`, `Diagnostico.pdf` (máx. 5 páginas), diccionario revisado, `perfil_calidad.csv`, `matriz_reglas.csv` y fichas de 6 KPI + 6 métricas de calidad. Rúbrica de 100 puntos.
- **E2–E4:** si su Word todavía no está, pedirlo antes de asumir requisitos.

Los PDF de la raíz se pueden leer sin poppler con PDFKit: `osascript -l JavaScript -e "ObjC.import('PDFKit'); \$.PDFDocument.alloc.initWithURL(\$.NSURL.fileURLWithPath('<ruta absoluta>')).string.js"`.

## Trabajo del grupo (4 integrantes: Byron, Bastian, Sepu, Jose)

Cada entrega vive en `04_Aguas_Andinas_alumnos/E<n>/`. La E1 está organizada así:
- `E1/README.md`: lo que pide el Word organizado en una checklist (códigos W, P, S, R), tabla de productos con su dueño, rúbrica, tareas T1–T4, **contrato de tablas por sector** (`T<n>_por_sector.csv`, para que el ranking de inspección no espere a nadie), cronograma relativo, convenciones y el formato de hallazgo (observación, hipótesis, decisión).
- `E1/tareas/T<n>_*.md`: una tarea por persona, diseñadas para no bloquearse entre sí. Cada una escribe solo en sus propios archivos (`E1/T<n>_*.ipynb`, `E1/salidas/{figuras,tablas}/T<n>_*`). Los productos del Word usan el nombre exacto y tienen un solo dueño.
- `E1/comun.py`: única dependencia compartida.
  - `verificar_hashes()`, `cargar_lotes()` (strings + columna `lote`) y `cargar_tabla()`.
  - `parse_exploratorio()`: tipado sin borrar filas, columnas `volumen_*_m3`, columnas `*_raw` y flags `_…` por cada problema de formato.
  - `PALETA` y `NOTA_FUENTE` para los gráficos.
  - Los notebooks van en `E1/` para que `import comun` funcione directo.
- T1 integra el notebook entregable en `E1/E1_diagnostico.ipynb`. `E1/diagnostico.md` se exporta a `E1/Diagnostico.pdf` (máx. 5 páginas). `E1/uso_ia.md` es la declaración de IA y se actualiza cada vez que se usa IA.
- **Dependencias entre tareas y cierre:** la sección "Pendientes y consolidación" de `E1/README.md` lista lo que espera resultados de otra tarea (por ejemplo, el ranking P4 de T2 espera `T3_por_sector.csv` y `T4_por_sector.csv`) Hay que revisarla antes de dar una tarea por terminada y actualizar su "Estado".
- **T5, consolidación (Byron, D-04):** `E1/tareas/T5_consolidacion.md` cierra los pendientes, corre el ranking real, une las fichas, arma el diagnóstico y el notebook final, y empaqueta. El script `E1/T5_consolidar.py` se corre desde `E1/`:
  - sin flags, muestra el estado ✅/❌ de insumos y productos;
  - `--unir-fichas`, `--ranking`, `--versiones`: preparan productos;
  - `--empaquetar`: arma `E1/entregable/` + .zip, ignorado por git; solo funciona si todo está ✅, salvo con `--forzar`;
  - `--probar`: ejecuta el notebook desde el .zip descomprimido;
  - `--notebook X.ipynb`: elige el notebook a revisar o empaquetar.
- `E1/decisiones.md`: registro, en el que solo se agregan entradas, de las decisiones que no definía el Word (D-01 atraso de carga = 2 h, D-02 la confiabilidad define el tipo de inspección, D-03 el ranking espera a T3 y T4). Cada decisión nueva o ambigüedad resuelta se agrega ahí.

Skills del proyecto, reutilizables en E1–E4. Se invocan con `/nombre` en Claude Code y con `$nombre` en Codex, que también las activa solo según su descripción:
- `perfil-calidad`: `perfil_calidad.csv` y `matriz_reglas.csv` por lote y segmento, con denominadores y la clasificación defecto / extremo plausible / ausencia estructural.
- `ficha-indicador`: fichas de KPI y métricas de calidad en el formato de `plantilla_fichas_indicadores.csv`; verifica que la fórmula sea computable.
- `grafico-diagnostico`: convenciones de gráficos e interpretación obligatoria (observación, hipótesis, decisión).
- `revisar-entrega E<n>`: auditoría de solo lectura contra el Word, la checklist y la rúbrica.

Pendiente para cuando llegue la E2: `bitacora`.

## Claude Code y Codex en paralelo

Parte del grupo usa Codex, así que la configuración de agentes está duplicada y **debe mantenerse sincronizada**:
- **Instrucciones:** `CLAUDE.md` (Claude Code) y `AGENTS.md` (Codex) tienen el mismo contenido salvo el encabezado. Si editas uno, aplica el mismo cambio en el otro.
- **Skills:** `.claude/skills/` (Claude Code) y `.agents/skills/` (Codex, la ruta de skills de repositorio en la documentación oficial) son copias idénticas. Se edita una y se replica con `rsync -a --delete .claude/skills/ .agents/skills/` (o al revés). Hay que verificar con `diff -r .claude/skills .agents/skills`.
- Las skills usan solo frontmatter `name` y `description`, y no usan `$ARGUMENTS` ni otra sintaxis exclusiva de un agente, para que el mismo `SKILL.md` funcione en ambos.
