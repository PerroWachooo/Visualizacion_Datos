"""Genera el diccionario T1 desde el diccionario fuente y metadatos del paquete."""
from pathlib import Path
import csv

BASE = Path(__file__).resolve().parents[1]
E1 = BASE / "E1"
OUT = E1 / "salidas" / "tablas"
OUT.mkdir(parents=True, exist_ok=True)

tipos = {
    "medicion_id": ("identificador", "nominal", "id de medición", "Identificador único; no se promedia."),
    "sector_id": ("identificador", "nominal", "id de sector", "Debe existir en el catálogo; no se promedia."),
    "fecha": ("temporal", "intervalo", "fecha-hora UTC", "Inicio de la hora de negocio; parseable y dentro del período del lote."),
    "cargado_en": ("temporal", "intervalo", "fecha-hora UTC", "Primera carga; comparar contra fecha, no contra la fecha actual."),
    "vigente_desde": ("temporal", "intervalo", "fecha UTC", "Límite inclusivo de vigencia."),
    "vigente_hasta": ("temporal", "intervalo", "fecha UTC", "Límite exclusivo; cada hecho debe coincidir con exactamente una vigencia."),
    "mes": ("temporal", "intervalo", "mes YYYY-MM", "Debe ser un mes calendario válido y único con sector."),
    "unidad_volumen": ("categórica nominal", "nominal", "categoría", "m3 o L; otra unidad no se convierte."),
    "modo_operacion": ("categórica nominal", "nominal", "categoría", "Normalizar espacios y mayúsculas; valores esperados normal o mantenimiento."),
    "indicador": ("categórica nominal", "nominal", "categoría", "Indicador definido por catálogo."),
    "unidad": ("categórica nominal", "nominal", "categoría", "Unidad declarada de la meta."),
    "sentido": ("categórica nominal", "nominal", "categoría", "mínimo o máximo según definición de meta."),
    "nombre_sector": ("categórica nominal", "nominal", "etiqueta", "Nombre sintético; no identifica infraestructura real."),
    "comuna_referencia": ("categórica nominal", "nominal", "etiqueta", "Etiqueta de contexto; no implica ubicación real."),
    "conexiones": ("cuantitativa discreta", "razón", "conexiones", "Entero positivo; peso vigente para ponderar continuidad, no sumar por hora como clientes."),
    "capacidad_m3_h": ("cuantitativa continua", "razón", "m³/h", "Capacidad sintética no negativa para evaluar magnitudes."),
    "volumen_entrada": ("cuantitativa continua", "razón", "m³ o L según unidad_volumen", "No negativo y numérico; convertir L a m³ dividiendo por 1000 antes de agregar."),
    "volumen_salida": ("cuantitativa continua", "razón", "m³ o L según unidad_volumen", "No negativo y numérico; misma unidad que entrada; salida ≤ entrada bajo el modelo docente."),
    "presion_bar": ("cuantitativa continua", "razón", "bar", "Valor numérico no negativo; señal operacional sintética, no sanitaria."),
    "energia_kwh": ("cuantitativa continua", "razón", "kWh", "Energía no negativa; costo solo donde hay tarifa."),
    "minutos_interrupcion": ("cuantitativa continua", "razón", "minutos", "Número entre 0 y 60; 0 es una lectura observada."),
    "tarifa_kwh_clp": ("cuantitativa continua", "razón", "CLP/kWh", "Tarifa no negativa para sector-mes; disponible solo ago–dic."),
}

def contrato(archivo, campo):
    if campo in tipos:
        return tipos[campo][3]
    if campo.startswith("m2025_"):
        return "Meta numérica docente; mes representado por el nombre de columna. Aplicar melt para análisis mensual."
    return "Campo presente según esquema fuente; validar tipo y dominio antes de usar."

source = BASE / "diccionario_datos.csv"
with source.open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
fields = ["archivo", "campo", "definicion", "tipo_estadistico", "escala", "unidad", "nulabilidad", "es_clave", "contrato", "observaciones"]
with (OUT / "diccionario_revisado.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in rows:
        campo = r["campo"]
        tipo, escala, unidad, obs = tipos.get(campo, ("cuantitativa continua", "razón", "valor de meta", "Columna ancha; no representa observaciones independientes."))
        nullable = "Sí: falta de captura; contar como nulo" if campo in {"volumen_entrada", "volumen_salida", "presion_bar", "energia_kwh", "minutos_interrupcion", "cargado_en"} else "No previsto; nulo indica defecto" 
        if campo == "vigente_hasta":
            nullable = "Sí solo para vigencia abierta; ausencia estructural según contrato"
        if campo.startswith("m2025_"):
            nullable = "No previsto; validar meta definida para el mes"
        if campo == "tarifa_kwh_clp":
            nullable = "Ausencia estructural fuera de ago–dic; dentro del alcance no prevista"
        w.writerow({"archivo": r["archivo"], "campo": campo, "definicion": r["definicion"], "tipo_estadistico": tipo, "escala": escala, "unidad": unidad, "nulabilidad": nullable, "es_clave": "Sí" if r["clave"].strip().lower() == "true" else "No", "contrato": contrato(r["archivo"], campo), "observaciones": obs})

import json
def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.splitlines(keepends=True)}
def code(s):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": s.splitlines(keepends=True)}

cells = [
    md("# T1 · Necesidades, inventario y diccionario\n\nE1 · Diagnóstico del caso Aguas Andinas. Datos y metas sintéticos para docencia; no representan operaciones reales. Ejecutar desde `E1/` para que `import comun` funcione."),
    code("from pathlib import Path\nimport hashlib\nimport pandas as pd\nimport comun\n\ncomun.verificar_hashes()\ncrudo = comun.cargar_lotes()\ndf = comun.parse_exploratorio(crudo)\nprint(f'{len(crudo):,} filas físicas; {crudo.medicion_id.nunique():,} mediciones distintas')"),
    md("## Decisión, audiencias y preguntas\n\n**Decisión:** priorizar tres sectores sintéticos para inspección considerando continuidad, diferencia de volúmenes, energía y confiabilidad de medición. Las señales operacionales se distinguen de la incertidumbre del sensor. El análisis no permite inferir potabilidad, cumplimiento regulatorio, causalidad ni resultados reales.\n\n| Audiencia | Decisión y nivel de detalle |\n|---|---|\n| Ejecutiva | Jefatura ficticia de operaciones y planificación: asignar tres inspecciones y recursos. Necesita comparación de sectores, prioridades, incertidumbre y efecto del filtro de cobertura. |\n| Operacional | Equipo ficticio de terreno, telemetría y mantenimiento: definir qué revisar y qué evidencia levantar. Necesita detalle por sector y semana, continuidad con límites, balance de volúmenes, energía y alertas de medición. |\n\n| Pregunta medible | Cálculo y período/población | Acción que puede cambiar |\n|---|---|---|\n| ¿Qué sectores podrían quedar bajo la meta docente de continuidad? | Continuidad ponderada por conexiones y límites suponiendo 0 o 60 min en horas desconocidas; comparar intervalo con 99,5%, ene–dic 2025 UTC por sector. | Priorizar sectores cuyo máximo esté bajo la meta; si el intervalo la cruza, levantar evidencia antes de calificarlos. |\n| ¿Dónde es mayor la diferencia entre entrada y salida? | Σ(entrada − salida)/Σ entrada en m³, ene–dic 2025 UTC, lecturas con ambos volúmenes convertibles y denominador positivo; informar faltantes y casos salida > entrada. | Revisar balance y medición en los sectores destacados, sin atribuir una causa por asociación. |\n| ¿Qué tres sectores combinan señales operacionales y medición confiable para inspección? | Ranking de continuidad, diferencia de volúmenes, kWh/m³ y costo CLP/m³ disponible, junto a calidad; ago–dic 2025 UTC por sector, con y sin filtro de cobertura mínima. | Asignar tres inspecciones y definir evidencia para distinguir condición operacional de incertidumbre de sensor. |\n\nCero minutos es una lectura observada; nulo es un campo sin dato en una fila existente; ausente es una sector-hora sin fila."),
    md("## Inventario de fuentes y exposición\n\nEl hecho tiene granularidad sector-hora UTC (`fecha` inicia la hora) y clave nominal `medicion_id`. Los lotes conservan sus cortes independientes. Las dimensiones no se concatenan con las observaciones. La tabla de metas complementaria sustituye a la fuente anterior; las tarifas solo cubren agosto–diciembre."),
    code("meta = comun.META\nfilas = []\nfor item in meta['files']:\n    rel = item['archivo']\n    path = comun.RAIZ / rel\n    contenido = path.read_bytes().replace(bytes([13, 10]), bytes([10]))\n    sha = hashlib.sha256(contenido).hexdigest()\n    filas.append({'archivo': rel, 'filas': item['filas'], 'columnas': item['columnas'], 'sha256': sha})\ninventario = pd.DataFrame(filas)\ninventario"),
    md("| Archivo | Rol, clave y granularidad | Período y corte UTC |\n|---|---|---|\n| `datos/base/telemetria_horaria.csv` | Hecho; `medicion_id`; sector-hora | Ene–jun 2025; 2025-07-08 |\n| `datos/actualizacion/telemetria_horaria.csv` | Hecho; `medicion_id`; sector-hora | Jul 2025; 2025-08-08 |\n| `datos/ampliacion/telemetria_horaria.csv` | Hecho; `medicion_id`; sector-hora | Ago–dic 2025; 2026-01-08 |\n| `datos/dimensiones/sectores.csv` | Dimensión fuente; `sector_id`; una fila por sector | Catálogo estático original |\n| `datos/dimensiones/metas_ancho.csv` | Dimensión fuente; sector + indicador; meses en columnas | Ene–jul; reemplazada analíticamente |\n| `datos/complementarios/sectores_historial.csv` | Dimensión SCD; sector + inicio de vigencia | 60 filas, dos versiones por sector; corte 2025-10-01 |\n| `datos/complementarios/tarifas_energia.csv` | Complementaria; sector + mes | Ago–dic; 150 filas |\n| `datos/complementarios/metas_2025_ancho.csv` | Dimensión; sector + indicador, meses en columnas | Ene–dic; hacer melt y usar en lugar de la anterior |\n\n**Filas físicas:** 130.972 base + 22.432 actualización + 100.000 ampliación = 253.404. **Entidades:** 30 sectores válidos. **Exposición calendario:** 130.320 sector-horas base (181 × 24 × 30), 22.320 actualización (31 × 24 × 30) y 110.160 ampliación (153 × 24 × 30); total 262.800 sector-horas. Filas físicas pueden exceder la exposición por repetición, sector desconocido o fecha inválida; la cobertura se calcula desde la grilla esperada. El paquete declara 10.000 sector-horas sin recepción en ago–dic.\n\n**Procedencia:** paquete v2, UTF-8, zona UTC, semillas 20260924 y 20261004, fecha del paquete 2026-10-01. Empresa usada solo como contexto; datos 100% sintéticos. SHA-256 de cada uno de los ocho archivos: tabla generada arriba y comprobación contra `metadatos.json` al inicio."),
    md("## Diccionario y contratos\n\nEl diccionario revisado extiende las 75 filas de `diccionario_datos.csv` con tipo estadístico, escala, unidad, nulabilidad, condición de clave, contrato verificable y observaciones. Los identificadores no se promedian; `fecha` representa el evento de negocio y `cargado_en` la primera carga. `presion_bar` usa escala de razón porque tiene cero físico y las razones entre magnitudes son interpretables dentro del escenario sintético; no implica criterio sanitario. Las metas mensuales están en columnas y deben pasar a formato largo. `conexiones` es un peso con vigencia, no clientes nuevos por hora.\n\nLa generación preserva una fila por campo de la fuente. Se revisará el texto de contratos junto con T2, que medirá las reglas; cualquier nulo observado se cuenta según su significado y no se completa automáticamente."),
    code("diccionario = pd.read_csv(comun.RAIZ / 'E1/salidas/tablas/diccionario_revisado.csv', dtype='string')\nprint(f'{len(diccionario)} campos documentados; {diccionario.archivo.nunique()} archivos; columnas: {list(diccionario.columns)}')\ndiccionario.head(12)"),
    md("## Límites de interpretación\n\n1. Las metas de continuidad, capacidades, presiones y registros son supuestos docentes sintéticos; una comparación con la meta no acredita cumplimiento regulatorio ni desempeño real.\n2. Las horas sin lectura producen un intervalo de continuidad, no un valor conocido; la concentración de faltantes puede cambiar el orden de prioridades.\n3. Una diferencia entre entrada y salida o una asociación con presión/energía no identifica la causa; el modelo no incluye almacenamiento ni transferencias y no sustituye una inspección.\n4. La tarifa existe solo para ago–dic y no se debe tratar su ausencia anterior como costo cero.\n\n**Reproducibilidad:** hashes verificados contra `metadatos.json`; lectura original como texto y parseo exploratorio sin borrar, deduplicar ni imputar filas. La limpieza corresponde a E2."),
]
nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.11+"}}, "nbformat": 4, "nbformat_minor": 5}
(E1 / "T1_inventario.ipynb").write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

