# T1: Pregunta, audiencia, diccionario e integración

**Responsable:** ____________
**Cubre:** IL1.1 (audiencia, decisión, diccionario, tipos y escalas) + integración del diagnóstico
**Notebook:** no es necesario. Si se usa, va en `E1/T1_diccionario.ipynb`.

## Objetivo

Dejar claro **para quién y para qué** es el análisis, y documentar **qué significa cada campo** de las 8 tablas, para que el resto pueda interpretar los datos igual. Desde el D-4, convertir los hallazgos del equipo en el diagnóstico final.

## Insumos

- [00_Enunciado_general.docx](../../00_Enunciado_general.docx): decisión y alcance.
- [README del caso](../../README.md): contrato de datos.
- [metadatos.json](../../metadatos.json): filas, cortes, claves, formatos.
- [diccionario_datos.csv](../../diccionario_datos.csv): punto de partida del diccionario.
- [01_Datos_y_Diagnostico.pdf](../../../01_Datos_y_Diagnostico.pdf): láminas 6 (audiencia), 9–10 (tipos y escalas), 11 (fuentes), 12 (diccionario), 13 (granularidad), 24 (ejemplo de diagnóstico).

## Parte A: pregunta y audiencia (`diagnostico.md` §1)

Responder en forma breve y concreta:
- **Audiencia:** quién usará la información, qué sabe y qué tarea hace con ella.
- **Decisión:** priorizar 3 sectores para inspección, según el enunciado.
- **Objetivo:** el resultado que el análisis busca apoyar.
- **Período y población:** 2025 completo en UTC, con 3 cortes de lote y 30 sectores disjuntos.
- **Unidad de análisis vs. granularidad:** la fila es sector × hora, pero la decisión es por sector. Explicar qué implica para agregar.
- **Tres preguntas de negocio** respondibles con estos datos. Idealmente cada una se apoya en una dimensión de la decisión (continuidad, diferencia de volúmenes, energía) y la confiabilidad de la medición queda transversal.
- **Qué NO se puede responder:** potabilidad, cumplimiento regulatorio, causas.

## Parte B: ficha de la fuente (`diagnostico.md` §2)

Una tabla corta con las 8 tablas. Columnas sugeridas:
- tabla;
- rol (hecho, dimensión o complementaria);
- origen (interna/externa, primaria/secundaria, sintética);
- granularidad (qué es una fila);
- clave esperada;
- filas;
- período y corte;
- reemplaza a.

## Parte C: diccionario (`E1/diccionario_e1.csv`)

Extender `diccionario_datos.csv` con estas columnas: `archivo, campo, definicion, tipo_estadistico, escala, unidad, dominio_regla, es_clave, obligatorio_para_KPI, nulos_validos, observaciones`.
- `tipo_estadistico`: categórica nominal, categórica ordinal, cuantitativa discreta, cuantitativa continua, temporal o identificador.
- `escala`: nominal, ordinal, intervalo o razón.
- `dominio_regla`: regla **verificable**, por ejemplo "entero 0–60" o "`A-S00`…`A-S29` y presente en sectores".

Casos que requieren pensar, no copiar el formato del archivo:
- `medicion_id` y `sector_id` tienen dígitos, pero son identificadores y no se promedian.
- `volumen_*` viene en dos unidades según `unidad_volumen`.
- `fecha` vs. `cargado_en`: son dos eventos temporales distintos.
- `presion_bar`: decidir si es razón o intervalo y justificarlo.
- `m2025_01`…`m2025_12`: son **valores** de una variable "mes" guardados como columnas (formato ancho, no tidy).
- `conexiones`: es un peso que cambia según vigencia y no se suma por hora.

Las reglas de dominio de T2 salen del mismo `diccionario_datos.csv`, así que **no hay que esperar a T2**. Al final se puede agregar en `observaciones` el % de cumplimiento que midió T2.

## Parte D: integración (desde el D-4)

1. En el checkpoint del D-5, juntar los hallazgos candidatos de T2–T4 y elegir 3 con el equipo. Que cubran **calidad/confiabilidad**, **cobertura** y **negocio**.
2. Redactar [diagnostico.md](../diagnostico.md) en máx. 3 páginas.
3. Armar la sección E1 de `00_inicio.ipynb` (ver "Integración final" en el [README](../README.md)).
4. Completar [uso_ia.md](../uso_ia.md) con lo que declare cada uno.
5. Correr `/revisar-entrega E1`.

## Terminado cuando

- [ ] §1 y §2 de `diagnostico.md` escritos.
- [ ] `diccionario_e1.csv` con todas las filas de `diccionario_datos.csv` y las columnas nuevas completas.
- [ ] Los tipos y escalas dudosos tienen la justificación en `observaciones`.
- [ ] Diagnóstico de 3 páginas o menos y notebook integrado que corre de arriba a abajo.

## No hacer

- No medir calidad (T2) ni cobertura (T3); solo referenciar sus resultados.
- No redactar hallazgos sin una cifra con denominador.

## Hallazgos candidatos

<!-- Usar el formato del README: H<n>, Evidencia, Figura o tabla, Límite, Acción propuesta, Dimensión -->
