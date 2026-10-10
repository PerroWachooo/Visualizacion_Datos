# Declaración de uso de IA (E1)

El curso exige declarar **y verificar** el uso de IA. Cada integrante agrega una fila apenas la use, no al final.

| Fecha | Integrante | Herramienta | Para qué se usó | Cómo se verificó |
|---|---|---|---|---|
| 2026-10-10 | Byron | Claude Code (Claude Opus 5.5) | Generó la estructura de la carpeta `E1/` (README, tareas, plantilla del diagnóstico), el módulo `comun.py` y las skills de `.claude/skills/`. | Se ejecutó `comun.py` contra los datos: los hashes coinciden con `metadatos.json`, la carga da 253.404 filas y los conteos de flags se contrastaron con conteos hechos con `grep`/`awk` sobre los CSV originales. Las tareas se revisaron contra la lámina 28 de la clase 01 y `trazabilidad_curso.csv`. |
