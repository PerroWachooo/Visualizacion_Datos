# Entrega E1 · Diagnóstico y necesidades · Grupo Aguas Andinas

Integrantes: Byron Caices, Bastián Brito, Benjamín Sepúlveda, José Marin · Visualización de Datos 2026 S2 · Prof. Viktor Tapia
Datos 100% simulados con fines docentes.

## Contenido
- `Diagnostico.pdf`: diagnóstico (máx. 5 páginas).
- `E1/E1_diagnostico.ipynb`: notebook ejecutado desde cero con los 3 lotes y las tablas complementarias.
- `E1/salidas/tablas/`: diccionario_revisado.csv, perfil_calidad.csv, matriz_reglas.csv, fichas_indicadores.csv y tablas de apoyo.
- `E1/salidas/figuras/`: figuras del notebook.
- `versiones_probadas.txt`: versiones de Python y paquetes con que se probó.

## Cómo ejecutar el notebook
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd E1 && jupyter lab E1_diagnostico.ipynb     # o: jupyter nbconvert --to notebook --execute E1_diagnostico.ipynb
```
El notebook verifica al inicio que los CSV de `datos/` no fueron modificados (SHA-256 vs `metadatos.json`).
