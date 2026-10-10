---
name: revisar-entrega
description: Revisa una entrega del proyecto Aguas Andinas (E1–E4) contra su Word de instrucciones y rúbrica (entregas/), la checklist de E<n>/README.md y trazabilidad_curso.csv. Verifica en los archivos reales que cada requisito tenga evidencia, que los productos tengan el nombre exacto, que las cifras tengan denominador, que los gráficos estén interpretados, que el notebook corra desde cero y que el uso de IA esté declarado, y estima el puntaje por criterio de la rúbrica. Usar antes de cada checkpoint y el día previo a la entrega.
---

# Revisar entrega

Entrega: la que indique el usuario (E1–E4). Si no la indica, usar la carpeta `E<n>/` más reciente en `04_Aguas_Andinas_alumnos/`.

Es una revisión **de solo lectura**: no edites entregables, no corrijas textos y no completes `trazabilidad_curso.csv`, salvo que se pida explícitamente. El valor está en un reporte honesto: si algo falta, se dice que falta.

## Qué leer

1. **El Word de la entrega**, en `04_Aguas_Andinas_alumnos/entregas/` (por ejemplo `Aguas_Andinas_E1_Diagnostico.docx`). Se lee con `textutil -convert txt -stdout <archivo>.docx` en macOS, o con `pandoc -t plain <archivo>.docx` si no hay `textutil`. **Es la fuente principal:** productos, trabajo requerido, preguntas del caso, situaciones, rúbrica y "revisión antes de entregar". Si no existe, avisar y seguir solo con el README.
2. `04_Aguas_Andinas_alumnos/E<n>/README.md`: checklist (códigos W, P, S, R), tabla de productos, contrato de tablas y convenciones. Si contradice el Word, prevalece el Word: reportar la diferencia.
3. Las filas de `04_Aguas_Andinas_alumnos/trazabilidad_curso.csv` cuya columna `entrega` contenga `E<n>`.
4. `E<n>/tareas/*.md`, el documento principal (`E<n>/diagnostico.md` o el que indique el README), `E<n>/uso_ia.md`, `E<n>/salidas/` y los notebooks.

## Verificaciones

- **Productos con nombre exacto:** cada producto que lista el Word existe con ese nombre y en la ruta que indica el README. En la E1:
  - `E1_diagnostico.ipynb`, `Diagnostico.pdf`;
  - `diccionario_revisado.csv`, `perfil_calidad.csv`, `matriz_reglas.csv`;
  - `fichas_indicadores.csv` con 6 KPI y 6 métricas de calidad.
- **Evidencia por requisito:** para cada ítem del Word y de la checklist, comprobar que la ruta existe y **contiene** lo pedido. Que el archivo exista no basta: por ejemplo, contar que haya ≥ 6 análisis distintos, 3 preguntas medibles con su acción y ≥ 2 límites.
- **Datos intactos:** desde `E1/`, `../.venv/bin/python -c "import comun; comun.verificar_hashes()"`, y que `git status` no muestre cambios en `datos/`.
- **El notebook corre desde cero** (en una sesión nueva, como pide el Word). Desde la carpeta del notebook, por ejemplo en la E1:
  ```
  cd 04_Aguas_Andinas_alumnos/E1 && ../.venv/bin/jupyter nbconvert --to notebook --execute E1_diagnostico.ipynb --output-dir "$(mktemp -d)"
  ```
  El directorio temporal queda fuera del repo, así que no se sobrescribe el original. Reportar la primera celda que falle. En los notebooks por tarea, revisar que no queden salidas de error.
- **Hallazgos completos:** cada hallazgo indica gráfico o tabla, período, unidad, población y limitación, y separa **observación, hipótesis y decisión**.
- **Cifras con denominador:** buscar en el documento principal porcentajes o tasas sin su "n de N" cerca. Listar cada caso con la línea.
- **Gráficos interpretados:** cada figura en `salidas/figuras/` referenciada en el documento o el notebook tiene texto interpretativo (qué muestra, por qué importa, límite). También listar las figuras huérfanas.
- **Extensión:** usar el máximo de páginas del Word (E1: **5 páginas**). Si hay PDF, contar sus páginas, por ejemplo con PDFKit vía `osascript -l JavaScript`. Si no, estimar unas 450–500 palabras por página con tablas incluidas.
- **Declaraciones:** que aparezca "datos simulados"; que `uso_ia.md` tenga filas con el campo "cómo se verificó" completo; que no se afirme potabilidad, cumplimiento regulatorio ni causalidad.
- **Reglas del caso:**
  - no se comparan fechas con "hoy";
  - las horas ausentes no se tratan como 0 y una unidad desconocida no se adivina;
  - cero, nulo y ausente están diferenciados;
  - las metas no están concatenadas;
  - las conexiones se usan según vigencia;
  - las correlaciones son solo entre variables interpretables.

## Reporte (en la respuesta, no en archivos)

1. Tabla `# | requisito | estado (✅ / ⚠️ / ❌) | evidencia (ruta:línea) | qué falta`, con los códigos del README (W, P, S, R) y los productos.
2. **Puntaje estimado por criterio de la rúbrica del Word** (100 / 75 / 50 / 25 / 0% de los puntos de cada criterio), con el fundamento en una línea. Es una estimación para priorizar, no una nota.
3. Lista priorizada de lo que hay que arreglar antes de entregar, con el responsable según la tabla de tareas del README si está asignado.
4. Valores propuestos para la columna `ruta_o_pagina_evidencia` de `trazabilidad_curso.csv`, como bloque copiable.
