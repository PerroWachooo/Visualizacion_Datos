# T1: Necesidades, inventario, diccionario e integración

**Responsable:** José Marín
**Ítems del Word:** W1, W2, W3, límites de W6, R2, R3 · **Rúbrica:** "Audiencia y preguntas" (25 pts) y "Reproducibilidad y claridad" (15 pts)
**Notebook de trabajo:** `E1/T1_inventario.ipynb`
**Productos:** `salidas/tablas/diccionario_revisado.csv`, `Diagnostico.pdf`, `E1_diagnostico.ipynb`, `salidas/tablas/fichas_indicadores.csv` (unión)

## Objetivo

Dejar claro **para quién y para qué** es el análisis, describir con precisión **qué contiene la fuente** y fijar **contratos de datos** que el resto pueda medir. Desde el D-4, convertir el trabajo del equipo en el diagnóstico y en el notebook entregable.

## Insumos

- [Word de la E1](../../entregas/Aguas_Andinas_E1_Diagnostico.docx) y [00_Enunciado_general.docx](../../00_Enunciado_general.docx).
- [README del caso](../../README.md): contrato de datos, cortes y vigencias.
- [metadatos.json](../../metadatos.json): filas, columnas, sha256, semillas, cortes y formatos.
- [diccionario_datos.csv](../../diccionario_datos.csv): punto de partida del diccionario.
- [01_Datos_y_Diagnostico.pdf](../../../01_Datos_y_Diagnostico.pdf): láminas 6 (audiencia), 9–10 (tipos y escalas), 11 (fuentes), 12 (diccionario), 13 (granularidad) y 24 (ejemplo de diagnóstico).

## Parte A: audiencias y preguntas (W1 → `diagnostico.md` §1)

- **Dos audiencias:** una **ejecutiva** y una **operacional**. Para cada una: quién es, qué decide y qué nivel de detalle necesita.
- **Decisión:** priorizar 3 sectores para inspección.
- **Tres preguntas medibles.** Cada una debe tener:
  - indicador o cálculo que la responde;
  - período;
  - población;
  - **qué acción cambiaría según la respuesta**.
  Por ejemplo: "si la continuidad mínima de un sector cae bajo la meta, entra a la lista de inspección".
- **Qué NO se puede responder:** potabilidad, cumplimiento regulatorio, causas y predicción.

## Parte B: inventario (W2 → `diagnostico.md` §2 + notebook)

- Una tabla con las 8 tablas: archivo, rol (hecho, dimensión o complementaria), filas, columnas, clave esperada, granularidad, período, corte y "reemplaza a".
- **Filas físicas vs. entidades vs. exposición.** Tres números distintos que no se deben confundir:
  - filas del CSV (incluye duplicados);
  - entidades: los 30 sectores, con sus conexiones;
  - exposición: las sector-horas esperadas, y las conexión-horas si se pondera.
- **Hash y procedencia:**
  - `sha256` de cada archivo (`metadatos.json`, verificado con `comun.verificar_hashes()`);
  - versión del paquete;
  - semillas;
  - fecha del paquete (1 de octubre de 2026);
  - carácter sintético de los datos.

## Parte C: diccionario revisado y contratos (W3 → `salidas/tablas/diccionario_revisado.csv`)

Extender `diccionario_datos.csv` con estas columnas: `archivo, campo, definicion, tipo_estadistico, escala, unidad, nulabilidad, es_clave, contrato, observaciones`.
- `tipo_estadistico`: categórica nominal, categórica ordinal, cuantitativa discreta, cuantitativa continua, temporal o identificador.
- `escala`: nominal, ordinal, intervalo o razón.
- `nulabilidad`: si se permite nulo y qué significa (falta, no aplica o no capturado).
- `contrato`: regla **verificable** que el dato debe cumplir. Ejemplos:
  - "entero 0–60";
  - "`m3` o `L`; otra unidad → no se convierte";
  - "`volumen_salida` ≤ `volumen_entrada`";
  - "existe en sectores".
  T2 mide estos contratos. Pónganse de acuerdo en el texto, pero **T2 no te espera**: parte desde el README del caso y `diccionario_datos.csv`.

Revisar en especial **ID, fecha de negocio y fecha de carga** (lo pide el Word):
- `medicion_id` y `sector_id` tienen dígitos, pero son identificadores y no se promedian.
- `fecha` (inicio de la hora, negocio) vs. `cargado_en` (primera carga): son dos eventos distintos.
- `volumen_*` viene en dos unidades según `unidad_volumen`.
- `presion_bar`: decidir si es razón o intervalo y justificarlo.
- `m2025_01`…`m2025_12`: son **valores** de una variable "mes" guardados como columnas (formato ancho, no tidy).
- `conexiones`: es un peso con vigencia y no se suma por hora.

## Parte D: integración (desde el D-4)

1. Elegir los hallazgos con el equipo en el checkpoint del D-5. Cada uno debe tener observación, hipótesis, decisión, gráfico o tabla, período, unidad, población y limitación (R2, R3).
2. Redactar [diagnostico.md](../diagnostico.md), con **≥ 2 límites de interpretación** (W6) y el **plan de limpieza** (desde `matriz_reglas.csv`), y exportar a `E1/Diagnostico.pdf` (**máx. 5 páginas**).
3. Armar `E1/E1_diagnostico.ipynb` (ver "Integración final" en el [README](../README.md)).
4. Unir `T4_fichas_kpi.csv` + `T2_fichas_calidad.csv` → `fichas_indicadores.csv`.
5. Completar [uso_ia.md](../uso_ia.md). Pedir a otra persona que ejecute el notebook desde una sesión nueva (R1). Correr `/revisar-entrega E1`.

## Terminado cuando

- [ ] §1 y §2 de `diagnostico.md` escritos, con 2 audiencias y 3 preguntas medibles con su acción.
- [ ] El inventario distingue filas físicas, entidades y exposición, con hash y procedencia.
- [ ] `diccionario_revisado.csv` tiene todas las filas y las columnas nuevas, con contratos verificables.
- [ ] `Diagnostico.pdf` de 5 páginas o menos; `E1_diagnostico.ipynb` corre desde una sesión nueva; fichas unidas.

## No hacer

- No medir calidad (T2) ni cobertura (T3); solo referenciar sus resultados.
- No redactar hallazgos sin una cifra con denominador.

## Hallazgos candidatos

<!-- Usar el formato del README: H<n>, Observación, Gráfico o tabla, Período · unidad · población, Hipótesis, Decisión o acción, Limitación, Dimensión -->
