---
name: revisar-entrega
description: Revisa una entrega del proyecto Aguas Andinas (E1–E4) contra su checklist (E<n>/README.md) y trazabilidad_curso.csv, verificando en los archivos reales que cada requisito tenga evidencia, que las cifras tengan denominador, que los gráficos estén interpretados, que el notebook corra y que el uso de IA esté declarado. Usar antes de cada checkpoint y el día previo a la entrega.
---

# Revisar entrega

Entrega: la que indique el usuario (E1–E4). Si no la indica, usar la carpeta `E<n>/` más reciente en `04_Aguas_Andinas_alumnos/`.

Es una revisión **de solo lectura**: no edites entregables, no corrijas textos y no completes `trazabilidad_curso.csv`, salvo que se pida explícitamente. El valor está en un reporte honesto: si algo falta, se dice que falta.

## Qué leer

1. `04_Aguas_Andinas_alumnos/E<n>/README.md`: la checklist ("Checklist") y las convenciones.
2. Las filas de `04_Aguas_Andinas_alumnos/trazabilidad_curso.csv` cuya columna `entrega` contenga `E<n>`.
3. Si existe, el Word de la entrega en `04_Aguas_Andinas_alumnos/entregas/` (con `textutil -convert txt -stdout <archivo>.docx`). Si contradice el README, prevalece el Word: reportar la diferencia.
4. `E<n>/tareas/*.md`, `E<n>/diagnostico.md` (u otro documento principal), `E<n>/uso_ia.md`, `E<n>/salidas/` y los notebooks.

## Verificaciones

- **Evidencia por requisito:** para cada ítem de la checklist, comprobar que la ruta indicada existe y **contiene** lo pedido. Que el archivo exista no basta.
- **Datos intactos:** desde `E1/`, `../.venv/bin/python -c "import comun; comun.verificar_hashes()"`, y que `git status` no muestre cambios en `datos/`.
- **El notebook corre:**
  ```
  ../.venv/bin/jupyter nbconvert --to notebook --execute ../00_inicio.ipynb --output-dir "$(mktemp -d)"
  ```
  El directorio temporal queda fuera del repo, así que no se sobrescribe el original. Reportar la primera celda que falle. En los notebooks por tarea, revisar que no queden salidas de error.
- **Cifras con denominador:** buscar en el documento principal porcentajes o tasas sin su "n de N" cerca. Listar cada caso con la línea.
- **Gráficos interpretados:** cada figura en `salidas/figuras/` referenciada en el documento o el notebook debe tener texto interpretativo (qué muestra, por qué importa, límite). También listar las figuras huérfanas.
- **Extensión:** E1 tiene un máximo de 3 páginas. Estimar unas 450–500 palabras por página con tablas incluidas, y advertir si supera unas 1.400 palabras.
- **Declaraciones:** que aparezca "datos simulados"; que `uso_ia.md` tenga filas con el campo "cómo se verificó" completo; que no se afirme potabilidad, cumplimiento regulatorio ni causalidad.
- **Reglas del caso:** que no se comparen fechas con "hoy"; que las horas ausentes no se traten como 0; que las metas no estén concatenadas; que se usen las conexiones según vigencia (E2+).

## Reporte (en la respuesta, no en archivos)

1. Tabla `# | requisito | estado (✅ / ⚠️ / ❌) | evidencia (ruta:línea) | qué falta`.
2. Lista priorizada de lo que hay que arreglar antes de entregar, con el responsable según la tabla de tareas del README si está asignado.
3. Valores propuestos para la columna `ruta_o_pagina_evidencia` de `trazabilidad_curso.csv`, como bloque copiable.
