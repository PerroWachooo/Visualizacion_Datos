# T1: Necesidades, inventario y diccionario

**Responsable:** José Marín
**Ítems del Word:** W1, W2, W3, límites de W6 · **Rúbrica:** "Audiencia y preguntas" (25 pts) y diccionario de "Reproducibilidad y claridad"
**Notebook de trabajo:** `E1/T1_inventario.ipynb`
**Productos:** `salidas/tablas/diccionario_revisado.csv` y las secciones §1, §2 y §6 de `diagnostico.md`
**Nota:** la integración (notebook final, PDF, unión de fichas y carpeta entregable) pasó a la [T5](T5_consolidacion.md) ([D-04](../decisiones.md)).

## Objetivo

Dejar claro **para quién y para qué** es el análisis, describir con precisión **qué contiene la fuente** y fijar **contratos de datos** que el resto pueda medir.
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

## Parte D: integración → pasó a la T5

La integración (elegir los hallazgos, redactar y exportar el diagnóstico, armar `E1_diagnostico.ipynb`, unir las fichas y armar el entregable) ahora es la [T5](T5_consolidacion.md). La T1 entrega sus partes A–C y los límites de interpretación (§6 de `diagnostico.md`). En la consolidación, T5 puede pedirle a T1 que ajuste esos textos.

## Terminado cuando

- [ ] §1 y §2 de `diagnostico.md` escritos, con 2 audiencias y 3 preguntas medibles con su acción.
- [ ] El inventario distingue filas físicas, entidades y exposición, con hash y procedencia.
- [ ] `diccionario_revisado.csv` tiene todas las filas y las columnas nuevas, con contratos verificables.
- [ ] §6 de `diagnostico.md` con al menos 2 límites de interpretación.
- [ ] Pendientes de T1 en la tabla del README cerrados (10.160 sector-horas; `minutos_interrupcion` discreta).

## No hacer

- No medir calidad (T2) ni cobertura (T3); solo referenciar sus resultados.
- No redactar hallazgos sin una cifra con denominador.

## Hallazgos candidatos

<!-- Usar el formato del README: H<n>, Observación, Gráfico o tabla, Período · unidad · población, Hipótesis, Decisión o acción, Limitación, Dimensión -->
