---
name: grafico-diagnostico
description: Crea un gráfico del caso Aguas Andinas con las convenciones del curso (título que afirma un hallazgo respaldado por un cálculo, unidades, período UTC, denominador, barras desde cero, nota de datos simulados, paleta común) y lo acompaña de una interpretación de 2–4 líneas. Usar en E1–E3 para cualquier figura de notebook, del diagnóstico o del dashboard, y para el par "gráfico deficiente vs. corregido" (IL3.1).
---

# Gráfico de diagnóstico

Pedido: lo que el usuario quiere mostrar y, si lo indica, la tarea (T1–T4) y la entrega (E1–E4). Si la tarea no está clara, preguntar antes de guardar, porque define el prefijo del archivo.

## Antes de graficar

1. Escribir en una línea **la pregunta que responde el gráfico** y **la cifra que respalda el título**. Calcularla primero en una celda propia, con numerador y denominador.
2. Elegir la forma según la pregunta:
   - comparar sectores → barras horizontales ordenadas por valor;
   - evolución → línea con meses en orden cronológico;
   - distribución → histograma o boxplot (n visible);
   - relación → dispersión (con transparencia si hay más de 1.000 puntos, o hexbin);
   - cobertura sector × tiempo → heatmap.
   Evitar torta con más de 3 categorías, 3D y doble eje Y.
3. Usar las columnas ya convertidas (`volumen_*_m3`, `fecha` en UTC) que entrega `comun.parse_exploratorio`. Declarar las exclusiones con cifra en el texto, no esconderlas.

## Convenciones visuales (obligatorias)

- **Título = hallazgo**, no descripción. Patrón: "<sujeto> <verbo> <cifra> (<n> de <N>)", por ejemplo "La ampliación tiene lectura válida en X de 110.160 sector-horas esperadas (Y%)". No sirve "Cobertura de la ampliación".
- **Subtítulo:** unidad, período UTC y n o denominador. Por ejemplo: "Sector-horas · ago–dic 2025 UTC · N = 110.160 esperadas".
- **Ejes con unidad**; barras y áreas **desde 0**; números con separador de miles chileno en el texto (`110.160`, `90,8%`).
- **Color con intención**, usando `comun.PALETA`:
  - `neutro` para todo y `acento` solo para lo que afirma el título;
  - `alerta` para problemas de calidad o incumplimiento de meta;
  - `ausente` para horas sin lectura, **nunca pintadas como 0**;
  - colores fijos por lote: `base`, `actualizacion`, `ampliacion`.
- **Nota al pie:** `comun.NOTA_FUENTE` + el corte del lote si aplica.
- E1–E2 usan matplotlib/seaborn (estático). E3 (dashboard Streamlit) usa plotly con la misma paleta y textos.

## Guardar

`fig.savefig(f"salidas/figuras/T<n>_<id>.png", dpi=150, bbox_inches="tight")` desde la carpeta `E<n>/`. `<id>` es corto y descriptivo (`cobertura_heatmap`, `latencia_hist`). No sobrescribir figuras con el prefijo de otra tarea.

## Interpretación (siempre, en una celda Markdown bajo el gráfico)

2–4 líneas, separando **observación, hipótesis y decisión** como pide el Word de la E1:
1. **Observación:** el patrón principal, con la cifra y su denominador, el período, la unidad y la población.
2. **Hipótesis** (si la hay): posible explicación, redactada como tal y no como hecho.
3. **Por qué importa para la decisión:** continuidad, diferencia de volúmenes, energía o confiabilidad.
4. **Límite:** qué no permite afirmar (causa, sectores con baja cobertura, datos simulados…).

El curso pide "gráficos interpretados, no solo capturas de código". Un gráfico sin estas líneas no está terminado.

## Par deficiente vs. corregido (IL3.1, E2–E3)

Generar ambas versiones lado a lado. La deficiente lleva **un error de codificación concreto y nombrado**, por ejemplo eje truncado, color sin significado, orden alfabético en vez de por valor, o horas ausentes pintadas como 0. Bajo el par se explica el error, su efecto en la lectura y la corrección aplicada.
