# E1 Diagnóstico: qué hay que hacer y cómo nos dividimos

**Grupo Aguas Andinas:** Byron, Bastian, Sepu, Jose
**Peso:** 10%, en equipo, semana 4
**Fecha de entrega:** `____/____/2026` (completar cuando se publique en el aula virtual)

## Qué pide la E1

No tenemos el Word de `entregas/`, así que los requisitos se armaron con estas fuentes:
- **Lámina 28 de [01_Datos_y_Diagnostico.pdf](../../01_Datos_y_Diagnostico.pdf)**: "Taller: diagnóstico para la entrega E1".
- **Lámina 10 del programa del curso**: entregables y extensión.
- **[trazabilidad_curso.csv](../trazabilidad_curso.csv)**: IL1.1 e IL1.2.
- **[00_Enunciado_general.docx](../00_Enunciado_general.docx)**: decisión y alcance del caso.

Si aparece el Word con la rúbrica, hay que contrastarlo con esta lista.

**Entregables:**
- Notebook: sección E1 de [00_inicio.ipynb](../00_inicio.ipynb).
- Diccionario de datos.
- Diagnóstico de **hasta 3 páginas**.

**Decisión que guía todo:** priorizar **3 sectores para inspección** considerando continuidad, diferencia de volúmenes, energía y confiabilidad de la medición. Hay que separar la evidencia operacional de la incertidumbre de los sensores, sin inferir potabilidad ni cumplimiento regulatorio.

### Checklist

| # | Requisito | IL | Tarea | Evidencia (ruta) |
|---|---|---|---|---|
| 1 | Audiencia, decisión, objetivo, período y población de interés | 1.1 | T1 | `diagnostico.md` §1 |
| 2 | Tres preguntas de negocio | 1.1 | T1 | `diagnostico.md` §1 |
| 3 | Ficha de la fuente: origen, unidad de cada fila, clave, cobertura, cortes | 1.1 | T1 | `diagnostico.md` §2 |
| 4 | Diccionario con variables, tipo, escala, unidad y regla/dominio | 1.1 | T1 | `diccionario_e1.csv` |
| 5 | Estructura por lote: filas, columnas, tipos, período | 1.2 | T2 | `T2_calidad.ipynb` |
| 6 | Ausencias por campo, con denominador | 1.2 | T2 | `salidas/tablas/T2_reglas_calidad.csv` |
| 7 | Duplicados de clave: copia exacta vs. conflicto | 1.2 | T2 | ídem |
| 8 | Validez: formatos de fecha y número, unidades, dominios | 1.2 | T2 | ídem |
| 9 | Oportunidad: latencia `cargado_en` − `fecha` | 1.2 | T2 | ídem |
| 10 | Granularidad y cobertura contra la grilla esperada (sector × hora) | 1.2 | T3 | `T3_cobertura.ipynb` |
| 11 | Consistencia con catálogos, vigencias, tarifas y metas | 1.2 | T3 | ídem |
| 12 | EDA univariado: distribuciones y medidas descriptivas | 1.2 | T4 | `T4_eda_negocio.ipynb` |
| 13 | EDA bivariado: al menos una relación pertinente para la decisión | 1.2 | T4 | ídem |
| 14 | Atípicos revisados (alerta ≠ borrar) | 1.2 | T4 | ídem |
| 15 | Tres hallazgos con evidencia | 1.2 | T1 (integra) | `diagnostico.md` §4 |
| 16 | Límites, pertinencia y acciones propuestas | 1.2 | T1 (integra) | `diagnostico.md` §5–6 |
| 17 | Gráficos **interpretados** (no capturas de código); cifras con denominador; datos simulados declarados | — | Todos | figuras + texto |
| 18 | Sección E1 de `00_inicio.ipynb` corre de arriba a abajo desde los originales | — | T1 (integra) | `00_inicio.ipynb` |
| 19 | Uso de IA declarado y verificado | — | Todos | `uso_ia.md` |
| 20 | Diagnóstico de 3 páginas o menos | — | T1 | `diagnostico.md` |

## División del trabajo

Las cuatro tareas arrancan el mismo día y no se esperan entre sí. La única dependencia común (cargar los datos) ya está resuelta en [comun.py](comun.py).

| Tarea | Foco | Entregable principal | Responsable |
|---|---|---|---|
| [T1](tareas/T1_pregunta_diccionario.md) | Pregunta, audiencia, ficha de la fuente, diccionario + **integración final** | `diccionario_e1.csv`, `diagnostico.md`, sección E1 de `00_inicio.ipynb` | |
| [T2](tareas/T2_calidad.md) | Calidad de la telemetría: unicidad, validez, completitud, oportunidad | `salidas/tablas/T2_reglas_calidad.csv` | |
| [T3](tareas/T3_cobertura_catalogos.md) | Cobertura (grilla esperada), granularidad, catálogos y vigencias | heatmap de cobertura + tabla de horas ausentes | |
| [T4](tareas/T4_eda_negocio.md) | EDA de variables de negocio: univariado, bivariado, atípicos | figuras de distribuciones y relación | |

T1 tiene menos código y por eso se encarga de integrar. Si alguien termina antes, apoya a T1 en la integración o revisa con `/revisar-entrega E1`.

### Por qué no se bloquean

- **T2 no espera a T1:** las reglas de dominio ya están en [diccionario_datos.csv](../diccionario_datos.csv) y en el [README del caso](../README.md). Después, T1 referencia lo que mide T2.
- **T4 no espera a T1:** la decisión ya viene dada por el enunciado.
- **T3 y T4 no esperan a T2:** `comun.parse_exploratorio` ya resuelve formatos (coma decimal, fechas dd/mm, litros) sin borrar filas, y deja flags para que T2 los cuente.
- **Archivos separados:** cada uno escribe solo en sus propios archivos (prefijo `T<n>_`), así que no hay conflictos de git.

## Cronograma (días relativos a la entrega)

| Día | Qué | Quién |
|---|---|---|
| D-10 | Kickoff de 15 min: repartir T1–T4 (anotar nombres arriba) y que todos corran el setup | Todos |
| D-10 a D-5 | Trabajo en paralelo en cada tarea | Cada uno |
| **D-5** | **Checkpoint:** cada uno trae 2–3 hallazgos candidatos (formato abajo) y se eligen los 3 del diagnóstico | Todos |
| D-4 a D-2 | T1 redacta `diagnostico.md` e integra el notebook; T2–T4 pulen figuras y escriben la interpretación | Todos |
| D-1 | `/revisar-entrega E1` y corrección final; reejecutar `00_inicio.ipynb` completo | T1 + quien esté libre |
| D-0 | Entrega | T1 |

Si hay menos de 10 días, se comprime el trabajo paralelo y se mantienen el checkpoint y el D-1.

## Setup (una vez por persona)

```bash
cd 04_Aguas_Andinas_alumnos
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd E1 && jupyter lab
```

Cada uno crea su notebook en `E1/` (por ejemplo `T2_calidad.ipynb`), con esta primera celda:

```python
import comun
comun.verificar_hashes()
crudo = comun.cargar_lotes()             # 253.404 filas, todo string, columna `lote`
df = comun.parse_exploratorio(crudo)     # tipado + flags (_decimal_coma, _fecha_formato_alt, _unidad_L, _dup_medicion_id)
```

## Convenciones

- **No editar nada en `datos/`.** El hash se verifica y la limpieza va en código.
- **Un notebook por tarea** (`E1/T<n>_<tema>.ipynb`); no se editan notebooks ajenos.
- **Salidas con prefijo:** `salidas/figuras/T<n>_<id>.png` y `salidas/tablas/T<n>_<id>.csv`.
- **Cifras con denominador** ("3.214 de 130.972 filas, 2,5%"), no solo el porcentaje.
- **Fechas en UTC.** `cargado_en` se compara contra `fecha`, **nunca** contra la fecha actual.
- **Ausente ≠ cero:** horas sin lectura y tarifas antes de agosto no se rellenan con 0.
- **Datos simulados:** cada figura lleva la nota "Datos simulados docentes".
- **Uso de IA:** se registra en [uso_ia.md](uso_ia.md) apenas se usa, no al final.

### Formato de hallazgo candidato

Cada tarea los escribe al final de su `tareas/T<n>_*.md`:

```markdown
### H<n>: <afirmación en una línea>
- Evidencia: <cifra> (<numerador> / <denominador>, lote o período)
- Figura o tabla: salidas/figuras/T<n>_<id>.png
- Límite: <qué NO permite afirmar>
- Acción propuesta: <qué hacer en la E2 o para la decisión>
- Dimensión de la decisión: continuidad | volúmenes | energía | confiabilidad
```

## Integración final (T1, desde D-4)

1. Se eligen los 3 hallazgos en el checkpoint y se redactan en [diagnostico.md](diagnostico.md) (máx. 3 páginas).
2. Se copian a la sección E1 de `00_inicio.ipynb` las celdas que respaldan cada requisito de la checklist, con texto interpretativo entre ellas. Ese notebook se abre desde `04_Aguas_Andinas_alumnos/`, así que antes de `import comun` va `import sys; sys.path.append("E1")`.
3. Reiniciar el kernel y ejecutar todo; debe correr sin errores desde los originales.
4. Los notebooks por tarea quedan en `E1/` como trabajo de soporte.

## Skills (Claude Code y Codex)

Las mismas tres skills están en dos carpetas: [.claude/skills/](../../.claude/skills/) para Claude Code y [.agents/skills/](../../.agents/skills/) para Codex.

| Skill | Claude Code | Codex | Para qué |
|---|---|---|---|
| perfil-calidad | `/perfil-calidad telemetria_horaria` | `$perfil-calidad telemetria_horaria` | Reglas de calidad con denominadores, en el formato de `plantilla_reglas_calidad.csv` |
| grafico-diagnostico | `/grafico-diagnostico <qué mostrar>` | `$grafico-diagnostico <qué mostrar>` | Gráfico con las convenciones del curso + interpretación |
| revisar-entrega | `/revisar-entrega E1` | `$revisar-entrega E1` | Contrasta esta checklist con lo que realmente está en el repo |

Codex también puede activarlas solo cuando el pedido calza con la descripción. Las instrucciones generales del repo están en `CLAUDE.md` (Claude Code) y `AGENTS.md` (Codex), con el mismo contenido.

**Si editas una skill o las instrucciones, sincroniza la otra copia** (desde la raíz del repo):

```bash
rsync -a --delete .claude/skills/ .agents/skills/   # o al revés si editaste la de Codex
diff -r .claude/skills .agents/skills               # no debe mostrar diferencias
```

Con `CLAUDE.md` y `AGENTS.md` aplica el mismo cambio en ambos (solo difieren en el encabezado).
