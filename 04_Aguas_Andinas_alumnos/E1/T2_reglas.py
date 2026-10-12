"""Reglas de calidad de la T2 (E1), reutilizables en E2 (antes/después) y E4 (reingesta).

Uso desde un notebook en E1/:

    import comun, T2_reglas as rq
    df = comun.parse_exploratorio(comun.cargar_lotes())
    ctx = rq.contexto()                      # catálogos y tablas complementarias
    ev = rq.evaluar_reglas(df, ctx)          # máscaras por fila: falla / evaluada
    matriz = rq.matriz_reglas(df, ev, ctx)   # producto matriz_reglas.csv
    perfil = rq.perfil_calidad(df, ev)       # producto perfil_calidad.csv

Todas las funciones son puras: no modifican `df` ni escriben archivos.
Las decisiones que no venían definidas en el Word están en decisiones.md (D-01, D-02, D-03).
"""
import numpy as np
import pandas as pd

import comun

UMBRAL_ATRASO_H = 2                 # D-01: "latency": 2 de metadatos.json interpretado en horas
SENSIBILIDAD_ATRASO_H = (1, 2, 3, 6)
META_CONTINUIDAD = 99.5             # metas_2025_ancho.csv, sentido mínimo (meta docente)
LOTES = comun.LOTES
PERIODO_LOTE = {                    # [inicio, fin) en UTC; ago–dic = lote ampliación
    "base": ("2025-01-01", "2025-07-01"),
    "actualizacion": ("2025-07-01", "2025-08-01"),
    "ampliacion": ("2025-08-01", "2026-01-01"),
}
COLS_ORIGINALES = ["medicion_id", "fecha", "sector_id", "volumen_entrada", "volumen_salida", "unidad_volumen",
                   "presion_bar", "energia_kwh", "minutos_interrupcion", "modo_operacion", "cargado_en"]
COLUMNAS_PLANTILLA = ["regla_id", "tabla", "campo", "condicion", "severidad", "denominador", "filas_evaluadas",
                      "filas_fallidas", "tratamiento", "justificacion", "impacto_KPI"]
TELEMETRIA = "telemetria_horaria"


def _ts(s):
    return pd.Timestamp(s, tz="UTC")


def contexto():
    """Catálogos y tablas complementarias tipadas que usan las reglas."""
    sectores = comun.cargar_tabla("dimensiones/sectores.csv")
    hist = comun.cargar_tabla("complementarios/sectores_historial.csv")
    for c in ["conexiones", "capacidad_m3_h"]:
        hist[c] = pd.to_numeric(hist[c])
    for c in ["vigente_desde", "vigente_hasta"]:
        hist[c] = pd.to_datetime(hist[c], utc=True)
    tarifas = comun.cargar_tabla("complementarios/tarifas_energia.csv")
    tarifas["tarifa_kwh_clp"] = pd.to_numeric(tarifas["tarifa_kwh_clp"], errors="coerce")
    return {
        "sectores": sectores,
        "historial": hist,
        "tarifas": tarifas,
        "metas_ancho": comun.cargar_tabla("dimensiones/metas_ancho.csv"),
        "metas_2025": comun.cargar_tabla("complementarios/metas_2025_ancho.csv"),
    }


def _capacidad_vigente(df, hist):
    """Capacidad m3/h vigente para cada fila (NaN si no hay sector o fecha válidos)."""
    base = df[["sector_id", "fecha"]].reset_index()
    base = base[base["fecha"].notna()]
    m = base.merge(hist[["sector_id", "vigente_desde", "vigente_hasta", "capacidad_m3_h"]], on="sector_id")
    m = m[(m["fecha"] >= m["vigente_desde"]) & (m["fecha"] < m["vigente_hasta"])]
    return m.set_index("index")["capacidad_m3_h"].reindex(df.index)


def _fuera_ric(valores, grupos):
    """True donde el valor cae fuera de [Q1 − 1,5·RIC, Q3 + 1,5·RIC] dentro de su grupo."""
    q1 = valores.groupby(grupos).transform(lambda s: s.quantile(0.25))
    q3 = valores.groupby(grupos).transform(lambda s: s.quantile(0.75))
    ric = q3 - q1
    return ((valores < q1 - 1.5 * ric) | (valores > q3 + 1.5 * ric)).fillna(False)


def evaluar_reglas(df, ctx):
    """Evalúa las reglas por fila. Devuelve {regla_id: (falla, evaluada)} como Series booleanas.

    Los denominadores son condicionales para no contar dos veces un problema: por ejemplo,
    RQ-CON-01 (salida > entrada) solo se evalúa donde ambos volúmenes son válidos y la entrada
    no es negativa, porque una entrada negativa ya falla RQ-VAL-07.
    """
    todas = pd.Series(True, index=df.index)
    sector_ok = df["sector_id"].isin(ctx["sectores"]["sector_id"])
    fecha_ok = df["fecha"].notna()
    copia = df[COLS_ORIGINALES].duplicated(keep="first")             # se compara el texto original
    ev = {}

    # Unicidad
    ev["RQ-UNI-01"] = (copia, todas)
    contenido = pd.util.hash_pandas_object(df[COLS_ORIGINALES], index=False)
    variantes = contenido.groupby(df["medicion_id"]).transform("nunique")
    ev["RQ-UNI-02"] = (variantes > 1, todas)
    base_gran = fecha_ok & sector_ok & ~copia
    rep = df.loc[base_gran, ["sector_id", "fecha"]].duplicated(keep="first")
    ev["RQ-UNI-03"] = (rep.reindex(df.index, fill_value=False), base_gran)

    # Validez
    ev["RQ-VAL-01"] = (df["_fecha_invalida"], todas)
    ev["RQ-VAL-02"] = (df["_fecha_formato_alt"], todas)
    fuera = pd.Series(False, index=df.index)
    for lote, (ini, fin) in PERIODO_LOTE.items():
        en_lote = df["lote"].eq(lote) & fecha_ok
        fuera |= en_lote & ((df["fecha"] < _ts(ini)) | (df["fecha"] >= _ts(fin)))
    ev["RQ-VAL-03"] = (fuera, fecha_ok)
    ev["RQ-VAL-04"] = (df["_decimal_coma"], todas)
    ve_texto = df["volumen_entrada_raw"].notna()
    ev["RQ-VAL-05"] = (ve_texto & df["volumen_entrada"].isna(), ve_texto)
    ev["RQ-VAL-06"] = (df["_unidad_desconocida"], todas)
    ve_num = df["volumen_entrada"].notna()
    ev["RQ-VAL-07"] = (ve_num & (df["volumen_entrada"] < 0), ve_num)
    min_num = df["minutos_interrupcion"].notna()
    ev["RQ-VAL-08"] = (min_num & ~df["minutos_interrupcion"].between(0, 60), min_num)
    modo_txt = df["modo_operacion_raw"].notna()
    ev["RQ-VAL-09"] = (modo_txt & ~df["modo_operacion_raw"].isin(["normal", "mantenimiento"]), modo_txt)
    ev["RQ-VAL-10"] = (~sector_ok, todas)

    # Consistencia entre campos
    vol_ok = df["volumen_entrada_m3"].notna() & df["volumen_salida_m3"].notna() & (df["volumen_entrada_m3"] >= 0)
    ev["RQ-CON-01"] = (vol_ok & (df["volumen_salida_m3"] > df["volumen_entrada_m3"]), vol_ok)

    # Completitud por campo (la cobertura de la grilla es RQ-COM-02, en cobertura())
    ev["RQ-COM-01"] = (df["volumen_entrada_raw"].isna(), todas)

    # Oportunidad
    fechas_ok = fecha_ok & df["cargado_en"].notna()
    atraso_h = (df["cargado_en"] - df["fecha"]).dt.total_seconds() / 3600
    ev["RQ-OPO-01"] = (fechas_ok & (atraso_h < 0), fechas_ok)
    ev["RQ-OPO-02"] = (fechas_ok & (atraso_h > UMBRAL_ATRASO_H), fechas_ok)

    # Plausibilidad: valores extremos (se marcan, no se borran)
    capacidad = _capacidad_vigente(df, ctx["historial"])
    con_cap = vol_ok & capacidad.notna()
    ev["RQ-EXT-01"] = (con_cap & (df["volumen_entrada_m3"] > capacidad), con_cap)
    usable = sector_ok & ~copia
    for regla, col, filtro in [("RQ-EXT-02", "volumen_entrada_m3", vol_ok),
                               ("RQ-EXT-03", "energia_kwh", df["energia_kwh"].notna()),
                               ("RQ-EXT-04", "presion_bar", df["presion_bar"].notna())]:
        base = usable & filtro
        marca = _fuera_ric(df.loc[base, col].astype(float), df.loc[base, "sector_id"])
        ev[regla] = (marca.reindex(df.index, fill_value=False), base)

    # Ausencia estructural: no hay tarifa antes de agosto (fuera de alcance, no es cero)
    ene_jul = fecha_ok & (df["fecha"] < _ts("2025-08-01"))
    ev["RQ-AUS-01"] = (ene_jul, ene_jul)
    return {k: (f.fillna(False).astype(bool), e.fillna(False).astype(bool)) for k, (f, e) in ev.items()}


def atraso_horas(df):
    return (df["cargado_en"] - df["fecha"]).dt.total_seconds() / 3600


def lecturas_validas(df, ev):
    """Filas que cuentan como lectura recibida válida para la cobertura (KRI-01 / RQ-COM-02).

    Fecha válida dentro del período del lote, sector del catálogo, no es copia exacta y es la
    primera lectura de su sector-hora. T3 debe usar la misma definición (ver README, consolidación).
    """
    excluir = ["RQ-UNI-01", "RQ-UNI-03", "RQ-VAL-01", "RQ-VAL-03", "RQ-VAL-10"]
    malo = pd.concat([ev[r][0] for r in excluir], axis=1).any(axis=1)
    return ~malo


def cobertura(df, ev, ctx):
    """Sector-horas esperadas vs. con lectura válida, por lote (RQ-COM-02)."""
    n_sectores = ctx["sectores"]["sector_id"].nunique()
    validas = df[lecturas_validas(df, ev)]
    filas = []
    for lote, (ini, fin) in PERIODO_LOTE.items():
        horas = int((_ts(fin) - _ts(ini)) / pd.Timedelta(hours=1))
        esperadas = horas * n_sectores
        observadas = int((validas["lote"] == lote).sum())
        filas.append({"lote": lote, "sector_horas_esperadas": esperadas,
                      "sector_horas_con_lectura_valida": observadas,
                      "sector_horas_sin_lectura_valida": esperadas - observadas,
                      "cobertura_pct": round(100 * observadas / esperadas, 2)})
    return pd.DataFrame(filas)


# Metadatos de cada regla: texto alineado con la columna `contrato` de diccionario_revisado.csv
REGLAS = [
    dict(regla_id="RQ-UNI-01", campo="medicion_id", clasificacion="defecto", severidad="alta",
         condicion="La fila es copia exacta (todas las columnas originales iguales) de otra con el mismo medicion_id",
         denominador="Filas del lote",
         tratamiento="Deduplicar: conservar una copia por medicion_id antes de agregar",
         justificacion="Contrato: medicion_id identifica una única medición. Las copias exactas no aportan información y duplican sumas.",
         impacto_KPI="Infla volúmenes, energía, costo y minutos de interrupción del sector afectado; sesga la continuidad si la hora tiene interrupción."),
    dict(regla_id="RQ-UNI-02", campo="medicion_id", clasificacion="defecto", severidad="alta",
         condicion="Un mismo medicion_id aparece con contenido distinto",
         denominador="Filas del lote",
         tratamiento="Si aparece: no elegir una versión sin evidencia; marcar la clave como conflictiva y excluirla de los KPI",
         justificacion="Distinguir una copia exacta de un conflicto, como pide el Word; sin evidencia no se sabe qué versión es la correcta.",
         impacto_KPI="Cualquier KPI del sector-hora afectado."),
    dict(regla_id="RQ-UNI-03", campo="sector_id + fecha", clasificacion="defecto", severidad="media",
         condicion="Más de una lectura para el mismo sector y hora (distinto medicion_id)",
         denominador="Filas con fecha y sector válidos que no son copia exacta",
         tratamiento="Conservar una lectura por sector-hora con un criterio documentado (p. ej., la primera cargada) y registrar el descarte en la bitácora",
         justificacion="La granularidad del hecho es sector × hora UTC: debe haber una lectura por sector-hora.",
         impacto_KPI="Doble conteo en sumas del sector; distorsiona la cobertura (más de 100% en esa hora)."),
    dict(regla_id="RQ-VAL-01", campo="fecha", clasificacion="defecto", severidad="alta",
         condicion="fecha no corresponde a un instante real (p. ej. 2025-02-30)",
         denominador="Filas del lote",
         tratamiento="Excluir del análisis temporal; no reconstruir la fecha porque no hay evidencia de la hora real",
         justificacion="Contrato: fecha parseable y dentro del período. Una fecha imposible no se puede ubicar en la grilla.",
         impacto_KPI="Baja la cobertura observada; esas lecturas no entran a continuidad ni a KPI semanales."),
    dict(regla_id="RQ-VAL-02", campo="fecha", clasificacion="defecto", severidad="baja",
         condicion="fecha en formato dd/mm/YYYY HH:MM:SS en lugar de ISO 8601",
         denominador="Filas del lote",
         tratamiento="Recuperable: parsear como dd/mm/YYYY en UTC (formato declarado en metadatos.json)",
         justificacion="metadatos.json declara el formato alternativo, así que la interpretación tiene evidencia.",
         impacto_KPI="Ninguno si se parsea bien; si se lee como ISO o mm/dd, las lecturas caen en otro día o se pierden."),
    dict(regla_id="RQ-VAL-03", campo="fecha", clasificacion="defecto", severidad="media",
         condicion="fecha válida pero fuera del período del lote",
         denominador="Filas con fecha válida",
         tratamiento="Excluir del lote y revisar si corresponde a otro corte",
         justificacion="Cada lote conserva su período y su fecha de corte; no se mezclan snapshots.",
         impacto_KPI="Mezclaría períodos entre lotes."),
    dict(regla_id="RQ-VAL-04", campo="volumen_entrada, volumen_salida, presion_bar, energia_kwh, minutos_interrupcion",
         clasificacion="defecto", severidad="baja",
         condicion="Número con coma decimal (p. ej. \"518,658\")",
         denominador="Filas del lote",
         tratamiento="Recuperable: reemplazar la coma por punto (no hay separador de miles, según metadatos.json)",
         justificacion="metadatos.json declara la excepción de formato.",
         impacto_KPI="Ninguno si se convierte; si se lee como texto o como miles, el valor queda nulo o se multiplica por 1000."),
    dict(regla_id="RQ-VAL-05", campo="volumen_entrada", clasificacion="defecto", severidad="alta",
         condicion="volumen_entrada con texto no numérico (p. ej. PENDIENTE)",
         denominador="Filas con volumen_entrada informado",
         tratamiento="Tratar como nulo; no imputar",
         justificacion="Contrato: volumen numérico. 'PENDIENTE' indica un valor que no llegó.",
         impacto_KPI="Esas horas no entran a la diferencia de volúmenes ni a kWh/m3."),
    dict(regla_id="RQ-VAL-06", campo="unidad_volumen", clasificacion="defecto", severidad="alta",
         condicion="unidad_volumen distinta de m3 y L",
         denominador="Filas del lote",
         tratamiento="Excluir los volúmenes de esas filas; la unidad desconocida no se adivina (Word, situación 1)",
         justificacion="Sin unidad no hay conversión válida a m3: un error de 1000× es posible.",
         impacto_KPI="Diferencia de volúmenes, kWh/m3 y costo por m3 de las horas afectadas."),
    dict(regla_id="RQ-VAL-07", campo="volumen_entrada", clasificacion="defecto", severidad="alta",
         condicion="volumen_entrada negativo",
         denominador="Filas con volumen_entrada numérico",
         tratamiento="Excluir de los KPI de volumen; no cambiar el signo sin evidencia",
         justificacion="Contrato: volumen no negativo. Un volumen negativo no tiene sentido físico en el modelo docente.",
         impacto_KPI="Sesga la diferencia de volúmenes (genera salida > entrada) y kWh/m3."),
    dict(regla_id="RQ-VAL-08", campo="minutos_interrupcion", clasificacion="defecto", severidad="alta",
         condicion="minutos_interrupcion fuera de [0, 60]",
         denominador="Filas con minutos numéricos",
         tratamiento="Tratar la hora como de interrupción desconocida (usar límites 0/60 de continuidad); no recortar a 60 sin evidencia",
         justificacion="Una hora tiene 60 minutos: el valor incumple el contrato (Word, situación 2).",
         impacto_KPI="Subestima la continuidad si se usa tal cual (90 min en una hora)."),
    dict(regla_id="RQ-VAL-09", campo="modo_operacion", clasificacion="defecto", severidad="baja",
         condicion="modo_operacion no canónico (mayúsculas o espacios, p. ej. ' NORMAL ')",
         denominador="Filas con modo_operacion informado",
         tratamiento="Recuperable: strip + minúsculas; luego verificar dominio {normal, mantenimiento}",
         justificacion="La variante es de formato; el valor normalizado pertenece al dominio.",
         impacto_KPI="Si no se normaliza, los filtros por modo pierden filas."),
    dict(regla_id="RQ-VAL-10", campo="sector_id", clasificacion="defecto", severidad="alta",
         condicion="sector_id no existe en el catálogo de sectores (p. ej. NO_EXISTE)",
         denominador="Filas del lote",
         tratamiento="Excluir de los KPI por sector; no asignar el sector sin evidencia",
         justificacion="Contrato: sector_id debe existir en el catálogo.",
         impacto_KPI="Lecturas que no se pueden asignar a ningún sector; bajan la cobertura del sector real (desconocido)."),
    dict(regla_id="RQ-CON-01", campo="volumen_salida, volumen_entrada", clasificacion="defecto", severidad="alta",
         condicion="volumen_salida > volumen_entrada (en m3)",
         denominador="Filas con ambos volúmenes válidos en m3 y entrada ≥ 0",
         tratamiento="Excluir de la diferencia de volúmenes y marcar el sector para revisar medidores",
         justificacion="El modelo omite almacenamiento y transferencias, así que estas filas incumplen su contrato (Word, situación 2).",
         impacto_KPI="Si se incluyen, la diferencia de volúmenes del sector baja (pérdidas negativas)."),
    dict(regla_id="RQ-COM-01", campo="volumen_entrada", clasificacion="defecto", severidad="media",
         condicion="volumen_entrada nulo",
         denominador="Filas del lote",
         tratamiento="Mantener como nulo; no imputar 0",
         justificacion="Nulo = la fila existe pero el valor no se capturó; no equivale a cero.",
         impacto_KPI="Reduce la base de la diferencia de volúmenes y de kWh/m3; si se concentra en algunos sectores, sesga su comparación."),
    dict(regla_id="RQ-COM-02", campo="sector-hora (grilla)", clasificacion="defecto", severidad="alta",
         condicion="Sector-hora esperada sin lectura válida (fecha válida, sector del catálogo, sin copia ni sector-hora repetida)",
         denominador="Sector-horas esperadas del período del lote (horas × 30 sectores)",
         tratamiento="Mantener visible como ausente; no imputar 0 de interrupción; reportar continuidad con límites 0/60",
         justificacion="El Word exige ausencias visibles: el promedio de las lecturas disponibles puede ocultar fallas.",
         impacto_KPI="Continuidad (puede sobreestimarse) y todo KPI sumado por sector."),
    dict(regla_id="RQ-OPO-01", campo="cargado_en", clasificacion="defecto", severidad="media",
         condicion="cargado_en anterior a fecha (carga antes de la hora medida)",
         denominador="Filas con fecha y cargado_en válidos",
         tratamiento="Marcar; no corregir la fecha. Revisar el reloj del sistema de carga",
         justificacion="Una lectura no puede cargarse antes de que ocurra la hora que mide.",
         impacto_KPI="Atraso negativo: distorsiona el indicador de oportunidad."),
    dict(regla_id="RQ-OPO-02", campo="cargado_en", clasificacion="defecto", severidad="media",
         condicion=f"Atraso de carga (cargado_en − fecha) mayor que {UMBRAL_ATRASO_H} horas",
         denominador="Filas con fecha y cargado_en válidos",
         tratamiento="No excluir del análisis histórico; reportar como métrica de oportunidad",
         justificacion=f"metadatos.json declara \"latency\": 2 sin unidad. Se interpreta como {UMBRAL_ATRASO_H} horas (decisión D-01, decisiones.md): calza con la telemetría horaria. Con 2 días ninguna lectura fallaría. Se informa la sensibilidad a 1, 3 y 6 h.",
         impacto_KPI="No cambia los KPI históricos; en operación retrasaría la detección de interrupciones."),
    dict(regla_id="RQ-EXT-01", campo="volumen_entrada", clasificacion="extremo_plausible", severidad="baja",
         condicion="volumen_entrada en m3 mayor que la capacidad_m3_h vigente del sector",
         denominador="Filas con volúmenes válidos y capacidad vigente",
         tratamiento="Marcar para revisión; no borrar",
         justificacion="La capacidad sintética sirve para detectar magnitudes anómalas.",
         impacto_KPI="Ninguno si no aparece; si aparece, inflaría volumen y bajaría kWh/m3."),
    dict(regla_id="RQ-EXT-02", campo="volumen_entrada", clasificacion="extremo_plausible", severidad="baja",
         condicion="volumen_entrada (m3) fuera de [Q1 − 1,5·RIC; Q3 + 1,5·RIC] de su sector",
         denominador="Filas con volúmenes válidos de sectores del catálogo",
         tratamiento="Marcar para revisión; no borrar (puede ser un caso real)",
         justificacion="Regla estadística de alerta (clase 01, lámina 23): orienta una revisión, no ordena eliminar.",
         impacto_KPI="Puede mover medias del sector; las medianas y razones de sumas son más robustas."),
    dict(regla_id="RQ-EXT-03", campo="energia_kwh", clasificacion="extremo_plausible", severidad="baja",
         condicion="energia_kwh fuera de [Q1 − 1,5·RIC; Q3 + 1,5·RIC] de su sector",
         denominador="Filas con energía numérica de sectores del catálogo",
         tratamiento="Marcar para revisión; no borrar",
         justificacion="Regla estadística de alerta; la energía alta puede ser real (bombeo).",
         impacto_KPI="kWh/m3 y costo por m3 del sector."),
    dict(regla_id="RQ-EXT-04", campo="presion_bar", clasificacion="extremo_plausible", severidad="baja",
         condicion="presion_bar fuera de [Q1 − 1,5·RIC; Q3 + 1,5·RIC] de su sector",
         denominador="Filas con presión numérica de sectores del catálogo",
         tratamiento="Marcar para revisión; no borrar. Una presión baja es solo una señal operacional del escenario",
         justificacion="Regla estadística de alerta; no es un criterio sanitario ni regulatorio.",
         impacto_KPI="Indicador de horas con presión baja."),
    dict(regla_id="RQ-AUS-01", campo="tarifa_kwh_clp", clasificacion="ausencia_estructural", severidad="baja",
         condicion="Hecho de ene–jul sin tarifa de energía",
         denominador="Filas con fecha válida en ene–jul",
         tratamiento="Calcular el costo solo en ago–dic; no rellenar con 0",
         justificacion="Las tarifas cubren ago–dic por diseño; la ausencia anterior está fuera de alcance (README del caso).",
         impacto_KPI="El costo por m3 solo es comparable en ago–dic."),
]


NOMBRE_CORTO = {
    "RQ-UNI-01": "Copia exacta de fila", "RQ-UNI-02": "Clave con contenido distinto",
    "RQ-UNI-03": "Sector-hora repetida", "RQ-VAL-01": "Fecha imposible",
    "RQ-VAL-02": "Fecha dd/mm (recuperable)", "RQ-VAL-03": "Fecha fuera del lote",
    "RQ-VAL-04": "Coma decimal (recuperable)", "RQ-VAL-05": "Volumen con texto (PENDIENTE)",
    "RQ-VAL-06": "Unidad desconocida", "RQ-VAL-07": "Volumen de entrada negativo",
    "RQ-VAL-08": "Interrupción > 60 min", "RQ-VAL-09": "Modo con mayúsculas/espacios (recuperable)",
    "RQ-VAL-10": "Sector inexistente", "RQ-CON-01": "Salida > entrada",
    "RQ-COM-01": "Volumen de entrada vacío", "RQ-COM-02": "Sector-hora sin lectura válida",
    "RQ-OPO-01": "Carga antes de la hora medida", "RQ-OPO-02": f"Atraso de carga > {UMBRAL_ATRASO_H} h",
    "RQ-EXT-01": "Volumen > capacidad", "RQ-EXT-02": "Volumen extremo (1,5 RIC)",
    "RQ-EXT-03": "Energía extrema (1,5 RIC)", "RQ-EXT-04": "Presión extrema (1,5 RIC)",
    "RQ-AUS-01": "Sin tarifa ene–jul (estructural)",
}


def matriz_reglas(df, ev, ctx):
    """Producto matriz_reglas.csv: columnas de la plantilla + lote + clasificacion."""
    meta = {r["regla_id"]: r for r in REGLAS}
    filas = []
    for regla_id, (falla, evaluada) in ev.items():
        r = meta[regla_id]
        tabla = "tarifas_energia × telemetria_horaria" if regla_id == "RQ-AUS-01" else TELEMETRIA
        for lote in LOTES:
            en = df["lote"].eq(lote)
            filas.append({**{k: r[k] for k in ["regla_id", "campo", "condicion", "severidad", "denominador",
                                                "tratamiento", "justificacion", "impacto_KPI", "clasificacion"]},
                          "tabla": tabla, "lote": lote,
                          "filas_evaluadas": int((evaluada & en).sum()),
                          "filas_fallidas": int((falla & en).sum())})
    cob = cobertura(df, ev, ctx)
    r = meta["RQ-COM-02"]
    for _, c in cob.iterrows():
        filas.append({**{k: r[k] for k in ["regla_id", "campo", "condicion", "severidad", "denominador",
                                            "tratamiento", "justificacion", "impacto_KPI", "clasificacion"]},
                      "tabla": TELEMETRIA + " vs. grilla esperada", "lote": c["lote"],
                      "filas_evaluadas": int(c["sector_horas_esperadas"]),
                      "filas_fallidas": int(c["sector_horas_sin_lectura_valida"])})
    filas += reglas_catalogo(ctx)
    orden = [r["regla_id"] for r in REGLAS] + [r["regla_id"] for r in REGLAS_CATALOGO]
    m = pd.DataFrame(filas)
    m["_o"] = m["regla_id"].map({k: i for i, k in enumerate(dict.fromkeys(orden))})
    m = m.sort_values(["_o", "lote"]).drop(columns="_o")
    return m[COLUMNAS_PLANTILLA + ["lote", "clasificacion"]].reset_index(drop=True)


REGLAS_CATALOGO = [
    dict(regla_id="RQ-CAT-01", campo="clave", clasificacion="defecto", severidad="alta",
         condicion="Clave esperada repetida en la tabla (metadatos.json, clave_esperada)",
         denominador="Filas de la tabla",
         tratamiento="Si aparece: no unir hasta resolver la duplicidad",
         justificacion="Una clave repetida en una dimensión duplica hechos al unir.",
         impacto_KPI="Todo KPI que use la dimensión (conexiones, tarifas, metas)."),
    dict(regla_id="RQ-CAT-02", campo="vigente_desde, vigente_hasta", clasificacion="defecto", severidad="alta",
         condicion="Vigencias del sector con solape o hueco dentro de 2025 (desde inclusivo, hasta exclusivo)",
         denominador="Sectores del historial",
         tratamiento="Si aparece: corregir con evidencia antes de ponderar por conexiones",
         justificacion="Debe haber exactamente una versión vigente por hecho (README del caso).",
         impacto_KPI="Continuidad ponderada por conexiones."),
    dict(regla_id="RQ-CAT-03", campo="tarifa_kwh_clp", clasificacion="defecto", severidad="media",
         condicion="Tarifa no numérica o ≤ 0",
         denominador="Filas de tarifas",
         tratamiento="Si aparece: excluir ese sector-mes del costo",
         justificacion="Contrato: tarifa no negativa para sector-mes.",
         impacto_KPI="Costo por m3."),
    dict(regla_id="RQ-AUS-02", campo="m2025_08 … m2025_12", clasificacion="ausencia_estructural", severidad="baja",
         condicion="metas_ancho.csv no tiene metas para ago–dic",
         denominador="Filas de metas_ancho.csv (sector × indicador)",
         tratamiento="Usar metas_2025_ancho.csv, que la sustituye; no concatenar ambas versiones",
         justificacion="La versión 2025 reemplaza analíticamente a la original (README del caso).",
         impacto_KPI="Comparación de continuidad con la meta en ago–dic."),
]


def reglas_catalogo(ctx):
    """Reglas sobre catálogos y complementarias (lote = 'catalogo')."""
    meta = {r["regla_id"]: r for r in REGLAS_CATALOGO}
    claves = {"sectores": ["sector_id"], "historial": ["sector_id", "vigente_desde"],
              "tarifas": ["sector_id", "mes"], "metas_2025": ["sector_id", "indicador"]}
    nombres = {"sectores": "sectores", "historial": "sectores_historial", "tarifas": "tarifas_energia",
               "metas_2025": "metas_2025_ancho"}
    filas = []

    def fila(regla_id, tabla, evaluadas, fallidas):
        r = meta[regla_id]
        filas.append({**{k: r[k] for k in ["regla_id", "campo", "condicion", "severidad", "denominador",
                                            "tratamiento", "justificacion", "impacto_KPI", "clasificacion"]},
                      "tabla": tabla, "lote": "catalogo",
                      "filas_evaluadas": int(evaluadas), "filas_fallidas": int(fallidas)})

    for k, cols in claves.items():
        t = ctx[k]
        fila("RQ-CAT-01", nombres[k], len(t), t.duplicated(cols, keep="first").sum())
    h = ctx["historial"].sort_values(["sector_id", "vigente_desde"])
    malos = 0
    for _, g in h.groupby("sector_id"):
        ok = (g["vigente_desde"].iloc[0] == _ts("2025-01-01")) and (g["vigente_hasta"].iloc[-1] >= _ts("2026-01-01"))
        ok &= bool((g["vigente_desde"].iloc[1:].values == g["vigente_hasta"].iloc[:-1].values).all())
        malos += not ok
    fila("RQ-CAT-02", "sectores_historial", h["sector_id"].nunique(), malos)
    t = ctx["tarifas"]["tarifa_kwh_clp"]
    fila("RQ-CAT-03", "tarifas_energia", len(t), (t.isna() | (t <= 0)).sum())
    m = ctx["metas_ancho"]
    faltan = [f"m2025_{i:02d}" for i in range(8, 13) if f"m2025_{i:02d}" not in m.columns]
    fila("RQ-AUS-02", "metas_ancho", len(m), len(m) if faltan else 0)
    return filas


# ---------------------------------------------------------------------------------------------
# Perfil por lote y segmento
# ---------------------------------------------------------------------------------------------
_INVALIDO_POR_CAMPO = {
    "medicion_id": ["RQ-UNI-01", "RQ-UNI-02"],
    "fecha": ["RQ-VAL-01", "RQ-VAL-03"],
    "sector_id": ["RQ-VAL-10"],
    "volumen_entrada": ["RQ-VAL-05", "RQ-VAL-07"],
    "unidad_volumen": ["RQ-VAL-06"],
    "minutos_interrupcion": ["RQ-VAL-08"],
    "cargado_en": ["RQ-OPO-01"],
}
_NUMERICO = {"volumen_entrada": "volumen_entrada_m3", "volumen_salida": "volumen_salida_m3",
             "presion_bar": "presion_bar", "energia_kwh": "energia_kwh",
             "minutos_interrupcion": "minutos_interrupcion"}


def _invalidos(df, ev):
    inv = {}
    for campo in COLS_ORIGINALES:
        reglas = _INVALIDO_POR_CAMPO.get(campo, [])
        m = pd.Series(False, index=df.index)
        for r in reglas:
            m |= ev[r][0]
        if campo in ("volumen_salida", "presion_bar", "energia_kwh"):
            raw = df[f"{campo}_raw"]
            m |= (raw.notna() & df[campo].isna()) | (df[campo] < 0)
        if campo == "modo_operacion":
            m |= df["modo_operacion"].notna() & ~df["modo_operacion"].isin(["normal", "mantenimiento"])
        if campo == "cargado_en":
            m |= df["cargado_en_raw"].notna() & df["cargado_en"].isna()
        inv[campo] = m
    return pd.DataFrame(inv)


def perfil_calidad(df, ev):
    """Producto perfil_calidad.csv: un perfil por lote × segmento × campo.

    - nulos: campo vacío en el archivo original (texto).
    - invalidos: el valor existe pero incumple su contrato (reglas de validez/unicidad del campo).
      Los formatos recuperables (coma decimal, fecha dd/mm, modo con espacios) NO cuentan como inválidos.
    - min/p50/max: volúmenes en m3 convertidos (sin unidad desconocida); fechas en ISO UTC.
    """
    inv = _invalidos(df, ev)
    seg = pd.DataFrame({
        "total": "total",
        "sector": df["sector_id"].fillna("sin_sector"),
        "mes": df["fecha"].dt.strftime("%Y-%m").fillna("sin_fecha_valida"),
        "modo_operacion": df["modo_operacion"].fillna("sin_modo"),
    }, index=df.index)
    raw = {c: (df[f"{c}_raw"] if f"{c}_raw" in df.columns else df[c]) for c in COLS_ORIGINALES}
    filas = []
    for lote in LOTES:
        en = df["lote"].eq(lote)
        for tipo in seg.columns:
            for valor, idx in seg.loc[en, tipo].groupby(seg.loc[en, tipo]).groups.items():
                for campo in COLS_ORIGINALES:
                    r = raw[campo].loc[idx]
                    n, nulos = len(idx), int(r.isna().sum())
                    invalidos = int(inv.loc[idx, campo].sum())
                    fila = {"lote": lote, "segmento_tipo": tipo, "segmento_valor": valor, "campo": campo,
                            "filas": n, "nulos": nulos, "pct_nulos": round(100 * nulos / n, 3),
                            "distintos": int(r.nunique()), "invalidos": invalidos,
                            "pct_invalidos": round(100 * invalidos / n, 3), "min": None, "p50": None, "max": None}
                    if campo in _NUMERICO:
                        v = df.loc[idx, _NUMERICO[campo]].astype(float)
                        if campo == "volumen_entrada":
                            v = v[v >= 0]
                        if v.notna().any():
                            fila.update(min=round(v.min(), 3), p50=round(v.median(), 3), max=round(v.max(), 3))
                    elif campo in ("fecha", "cargado_en"):
                        v = df.loc[idx, campo].dropna()
                        if len(v):
                            fila.update(min=v.min().isoformat(), p50=v.sort_values().iloc[len(v) // 2].isoformat(),
                                        max=v.max().isoformat())
                    filas.append(fila)
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------------------------
# Sesgo en KPI: cuánto cambian los indicadores según cómo se tratan los datos defectuosos
# ---------------------------------------------------------------------------------------------
def _kpis(d, horas_esperadas=None):
    e, s = d["_e"].astype(float), d["_s"].astype(float)
    ok_vol = e.notna() & s.notna()
    e_sum = e[ok_vol].sum()
    out = {
        "diferencia_volumenes_pct": 100 * (e[ok_vol] - s[ok_vol]).sum() / e_sum if e_sum else np.nan,
        "kwh_por_m3": d.loc[e.notna(), "energia_kwh"].sum() / e[e.notna()].sum() if e[e.notna()].sum() else np.nan,
    }
    minutos = d["_min"].astype(float).dropna()
    horas = horas_esperadas if horas_esperadas is not None else len(minutos)
    out["continuidad_simple_pct"] = 100 * (1 - minutos.sum() / (60 * horas)) if horas else np.nan
    return out


def sesgo_kpi(df, ev, ctx):
    """Compara 3 KPI calculados con una referencia vs. escenarios con tratamientos incorrectos.

    Referencia (provisional; la fórmula final de cada KPI es de T4): lecturas válidas (fecha, sector,
    sin copias ni sector-hora repetida), volúmenes en m3 con unidad conocida, entrada ≥ 0,
    salida ≤ entrada, minutos en [0, 60]; razón de sumas; continuidad simple (sin ponderar por
    conexiones) sobre horas observadas.
    """
    validas = lecturas_validas(df, ev)
    # mismas condiciones que una lectura válida, pero sin descartar copias ni sector-horas repetidas
    con_copias = ~(ev["RQ-VAL-01"][0] | ev["RQ-VAL-03"][0] | ev["RQ-VAL-10"][0])
    unidad_conocida = ~ev["RQ-VAL-06"][0]
    vol_bueno = unidad_conocida & ~ev["RQ-VAL-07"][0] & ~ev["RQ-CON-01"][0]
    min_bueno = ~ev["RQ-VAL-08"][0]
    todas = pd.Series(True, index=df.index)

    def armar(filtro, e="volumen_entrada_m3", s="volumen_salida_m3", vol_ok=vol_bueno, min_ok=min_bueno):
        d = pd.DataFrame({"_e": df[e].where(vol_ok), "_s": df[s].where(vol_ok),
                          "_min": df["minutos_interrupcion"].where(min_ok), "energia_kwh": df["energia_kwh"]})
        return d[filtro]

    cob = cobertura(df, ev, ctx).set_index("lote")
    filas = []
    for alcance in ["total"] + LOTES:
        en = todas if alcance == "total" else df["lote"].eq(alcance)
        esperadas = int(cob["sector_horas_esperadas"].sum() if alcance == "total"
                        else cob.loc[alcance, "sector_horas_esperadas"])
        resultados = {
            "Referencia (tratamiento correcto)": _kpis(armar(validas & en)),
            "Sin convertir litros a m3": _kpis(armar(validas & en, "volumen_entrada", "volumen_salida")),
            "Sin deduplicar copias exactas": _kpis(armar(con_copias & en)),
            "Incluyendo entrada negativa y salida > entrada": _kpis(armar(validas & en, vol_ok=unidad_conocida)),
            "Incluyendo minutos > 60": _kpis(armar(validas & en, min_ok=todas)),
            "Horas sin lectura tratadas como 0 min de interrupción": {
                "continuidad_simple_pct": _kpis(armar(validas & en), horas_esperadas=esperadas)["continuidad_simple_pct"]},
        }
        ref = resultados["Referencia (tratamiento correcto)"]
        for nombre, kp in resultados.items():
            for kpi, valor in kp.items():
                filas.append({"alcance": alcance, "kpi": kpi, "escenario": nombre, "valor": round(valor, 4),
                              "referencia": round(ref[kpi], 4), "delta": round(valor - ref[kpi], 4),
                              "delta_relativo_pct": round(100 * (valor - ref[kpi]) / ref[kpi], 2) if ref[kpi] else np.nan})
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------------------------
# Tabla por sector (contrato del README) y métricas de calidad
# ---------------------------------------------------------------------------------------------
DEFECTOS_FILA = ["RQ-UNI-01", "RQ-UNI-02", "RQ-UNI-03", "RQ-VAL-01", "RQ-VAL-03", "RQ-VAL-05", "RQ-VAL-06",
                 "RQ-VAL-07", "RQ-VAL-08", "RQ-CON-01", "RQ-COM-01", "RQ-OPO-01"]
FORMATO_RECUPERABLE = ["RQ-VAL-02", "RQ-VAL-04", "RQ-VAL-09"]


def por_sector(df, ev, ctx, lote="ampliacion"):
    """T2_por_sector.csv: confiabilidad por sector en el período del ranking (ago–dic = lote ampliación).

    filas_con_defecto: la fila falla al menos una regla de DEFECTOS_FILA (queda inutilizable para algún KPI).
    Los formatos recuperables y el atraso (RQ-OPO-02) van en columnas aparte y no cuentan como defecto.
    Las filas con sector fuera del catálogo no se pueden asignar a un sector y no aparecen aquí.
    """
    en = df["lote"].eq(lote) & df["sector_id"].isin(ctx["sectores"]["sector_id"])
    defecto = pd.concat([ev[r][0] for r in DEFECTOS_FILA], axis=1).any(axis=1)
    formato = pd.concat([ev[r][0] for r in FORMATO_RECUPERABLE], axis=1).any(axis=1)
    atraso, atraso_eval = ev["RQ-OPO-02"]
    d = pd.DataFrame({"sector_id": df["sector_id"], "defecto": defecto, "formato": formato,
                      "atraso": atraso, "atraso_eval": atraso_eval})[en]
    t = d.groupby("sector_id").agg(filas=("defecto", "size"), filas_con_defecto=("defecto", "sum"),
                                   filas_formato_recuperable=("formato", "sum"),
                                   atrasadas=("atraso", "sum"), con_fechas=("atraso_eval", "sum"))
    t = t.reindex(sorted(ctx["sectores"]["sector_id"]), fill_value=0)
    t["pct_filas_con_defecto"] = (100 * t["filas_con_defecto"] / t["filas"]).round(3)
    t["pct_atrasadas"] = (100 * t["atrasadas"] / t["con_fechas"]).round(3)
    t = t.reset_index()
    return t[["sector_id", "filas", "filas_con_defecto", "pct_filas_con_defecto",
              "filas_formato_recuperable", "pct_atrasadas"]]


def valores_kri(matriz):
    """Valor global de las 6 métricas de calidad, calculado desde la matriz (numerador / denominador)."""
    tel = matriz[matriz["lote"].isin(LOTES)]

    def tot(regla):
        r = tel[tel["regla_id"] == regla]
        return int(r["filas_fallidas"].sum()), int(r["filas_evaluadas"].sum())

    com_f, com_e = tot("RQ-COM-02")
    filas = [("KRI-01", "Cobertura de lecturas válidas", com_e - com_f, com_e, True)]
    for kri, nombre, regla in [("KRI-02", "Unicidad de clave (copias)", "RQ-UNI-01"),
                               ("KRI-03", "Unidad desconocida", "RQ-VAL-06"),
                               ("KRI-04", "Salida > entrada", "RQ-CON-01"),
                               ("KRI-05", "Minutos fuera de [0, 60]", "RQ-VAL-08"),
                               ("KRI-06", f"Lecturas con atraso > {UMBRAL_ATRASO_H} h", "RQ-OPO-02")]:
        f, e = tot(regla)
        filas.append((kri, nombre, f, e, False))
    return pd.DataFrame([{"id": k, "metrica": n, "numerador": a, "denominador": b,
                          "valor_pct": round(100 * a / b, 3)} for k, n, a, b, _ in filas])


FICHAS_CALIDAD = [
    dict(id="KRI-01", tipo_KPI_KRI_visual="KRI",
         objetivo="Confiabilidad: qué parte de las sector-horas esperadas tiene una lectura válida. Responde si un sector se puede calificar con lo observado.",
         formula="100 × sector-horas con lectura válida / sector-horas esperadas",
         numerador="Sector-horas con lectura válida: fecha válida dentro del período del lote, sector del catálogo, sin copia exacta, una por sector-hora",
         denominador="Sector-horas esperadas = horas del período del lote × 30 sectores (grilla calendario UTC)",
         unidad="%", granularidad="Sector-hora → sector × semana y lote",
         fuente_columnas="telemetria_horaria: fecha, sector_id, medicion_id; dimensiones/sectores.csv: sector_id; grilla calendario UTC",
         filtros="Los 3 lotes; excluye RQ-UNI-01, RQ-UNI-03, RQ-VAL-01, RQ-VAL-03, RQ-VAL-10",
         periodo_corte="Por lote: ene–jun (corte 2025-07-08), jul (2025-08-08), ago–dic (2026-01-08)",
         tratamiento_nulos="Una hora sin lectura es AUSENTE: no se imputa ni se cuenta como 0 de interrupción; se reporta la continuidad con límites 0/60",
         umbral="≥ 95% por sector (propuesta a validar en E3)", version_umbral="v0-E1",
         responsable="T2 (Byron); en operación: equipo de telemetría",
         accion="Bajo el umbral, el sector no se califica solo con lo observado (usar límites 0/60) y se revisa la transmisión de sus sensores"),
    dict(id="KRI-02", tipo_KPI_KRI_visual="KRI",
         objetivo="Confiabilidad: detectar lecturas duplicadas que inflan las sumas",
         formula="100 × filas que son copia exacta de otra con el mismo medicion_id / filas",
         numerador="Filas copia exacta (RQ-UNI-01)", denominador="Filas de telemetría del lote",
         unidad="%", granularidad="Fila → lote", fuente_columnas="telemetria_horaria: las 11 columnas originales",
         filtros="Los 3 lotes; texto original sin parsear", periodo_corte="Por lote, según su corte",
         tratamiento_nulos="Los nulos se comparan como iguales entre copias",
         umbral="0%", version_umbral="v0-E1", responsable="T2 (Byron); en operación: responsable de la carga",
         accion="Si es > 0%, deduplicar antes de calcular cualquier KPI (E2) y revisar la carga del lote"),
    dict(id="KRI-03", tipo_KPI_KRI_visual="KRI",
         objetivo="Confiabilidad de volúmenes: lecturas cuyo volumen no se puede convertir a m3",
         formula="100 × filas con unidad_volumen distinta de m3 y L / filas",
         numerador="Filas con unidad desconocida (RQ-VAL-06)", denominador="Filas de telemetría del lote",
         unidad="%", granularidad="Fila → sector × mes", fuente_columnas="telemetria_horaria: unidad_volumen",
         filtros="Los 3 lotes", periodo_corte="Por lote, según su corte",
         tratamiento_nulos="La unidad desconocida no se adivina: el volumen de esa fila queda fuera de los KPI de volumen",
         umbral="0%", version_umbral="v0-E1", responsable="T2 (Byron); en operación: equipo de telemetría",
         accion="Si es > 0%, excluir esos volúmenes y pedir la corrección en origen; si se concentra en un sector, inspección de sensor"),
    dict(id="KRI-04", tipo_KPI_KRI_visual="KRI",
         objetivo="Consistencia del balance: horas donde sale más agua de la que entra",
         formula="100 × filas con volumen_salida > volumen_entrada (m3) / filas con ambos volúmenes válidos y entrada ≥ 0",
         numerador="Filas que fallan RQ-CON-01",
         denominador="Filas con ambos volúmenes numéricos, unidad conocida, convertidos a m3 y entrada ≥ 0",
         unidad="%", granularidad="Fila → sector × mes",
         fuente_columnas="telemetria_horaria: volumen_entrada, volumen_salida, unidad_volumen (→ volumen_*_m3)",
         filtros="Los 3 lotes; excluye entrada negativa (ya cuenta en RQ-VAL-07)", periodo_corte="Por lote, según su corte",
         tratamiento_nulos="Volúmenes nulos o no numéricos quedan fuera del denominador",
         umbral="0% (el modelo omite almacenamiento y transferencias)", version_umbral="v0-E1",
         responsable="T2 (Byron); en operación: equipo de medición",
         accion="Si es > 0%, excluir esas horas de la diferencia de volúmenes y revisar los medidores del sector"),
    dict(id="KRI-05", tipo_KPI_KRI_visual="KRI",
         objetivo="Validez de la continuidad: minutos de interrupción imposibles",
         formula="100 × filas con minutos_interrupcion fuera de [0, 60] / filas con minutos numéricos",
         numerador="Filas que fallan RQ-VAL-08", denominador="Filas con minutos_interrupcion numérico",
         unidad="%", granularidad="Fila → sector × semana", fuente_columnas="telemetria_horaria: minutos_interrupcion",
         filtros="Los 3 lotes", periodo_corte="Por lote, según su corte",
         tratamiento_nulos="La hora afectada se trata como de interrupción desconocida (límites 0/60), no se recorta a 60",
         umbral="0%", version_umbral="v0-E1", responsable="T2 (Byron); en operación: equipo de telemetría",
         accion="Si es > 0%, tratar esas horas como desconocidas en la continuidad y revisar el registro de interrupciones"),
    dict(id="KRI-06", tipo_KPI_KRI_visual="KRI",
         objetivo="Oportunidad: lecturas que llegan tarde a la base de datos",
         formula=f"100 × filas con (cargado_en − fecha) > {UMBRAL_ATRASO_H} h / filas con fecha y cargado_en válidos",
         numerador="Filas que fallan RQ-OPO-02", denominador="Filas con fecha y cargado_en válidos",
         unidad="%", granularidad="Fila → sector × lote", fuente_columnas="telemetria_horaria: fecha, cargado_en",
         filtros="Los 3 lotes", periodo_corte="Por lote, según su corte; nunca se compara con la fecha actual",
         tratamiento_nulos="Fechas inválidas fuera del denominador",
         umbral=f"≤ 10% de lecturas con atraso > {UMBRAL_ATRASO_H} h (propuesta; unidad del umbral según D-01)",
         version_umbral="v0-E1", responsable="T2 (Byron); en operación: responsable de la integración de datos",
         accion="Sobre el umbral, revisar el canal de transmisión de los sectores con más atraso; en un dashboard, advertir que los datos recientes pueden estar incompletos"),
]


def fichas_calidad():
    """T2_fichas_calidad.csv con las columnas exactas de plantilla_fichas_indicadores.csv."""
    columnas = pd.read_csv(comun.RAIZ / "plantilla_fichas_indicadores.csv", nrows=0).columns.tolist()
    return pd.DataFrame(FICHAS_CALIDAD)[columnas]


# ---------------------------------------------------------------------------------------------
# Ranking de inspección (P4). D-02: la confiabilidad define el tipo de inspección.
# D-03: se ejecuta con datos reales solo en la consolidación, cuando existan T3 y T4.
# ---------------------------------------------------------------------------------------------
COLUMNAS_CONTRATO = {
    "t2": ["sector_id", "filas", "filas_con_defecto", "pct_filas_con_defecto"],
    "t3": ["sector_id", "horas_esperadas", "horas_observadas", "cobertura_pct", "continuidad_obs_pct",
           "continuidad_min_pct", "continuidad_max_pct"],
    "t4": ["sector_id", "m3_entrada", "dif_volumen_pct", "kwh_por_m3", "costo_clp_por_m3"],
}


def validar_contrato(t2, t3, t4):
    for nombre, t in {"t2": t2, "t3": t3, "t4": t4}.items():
        faltan = set(COLUMNAS_CONTRATO[nombre]) - set(t.columns)
        assert not faltan, f"{nombre}_por_sector no cumple el contrato; faltan {sorted(faltan)}"
        assert t["sector_id"].is_unique and len(t) == 30, f"{nombre}_por_sector debe tener 30 sectores únicos"


def ranking(t2, t3, t4, cobertura_min=None, umbral_defecto=None, meta=META_CONTINUIDAD):
    """Ranking de prioridad de inspección.

    Puntaje operacional = promedio de 3 criterios en percentil (1 = peor):
      continuidad observada (más baja = peor), diferencia de volúmenes % (más alta = peor),
      energía = promedio de los percentiles de kWh/m3 y CLP/m3 (un solo criterio, porque costo = kWh × tarifa).
    Con cobertura_min, los sectores bajo ese % de cobertura quedan fuera y los percentiles se recalculan.
    tipo_inspeccion: 'sensor primero' si pct_filas_con_defecto > umbral_defecto; si no, 'operación'.
    Por defecto el umbral es 2 × la mediana de los 30 sectores: una regla relativa que marca a los sectores
    con el doble de defectos que un sector típico (un percentil fijo podría partir un grupo homogéneo).
    """
    validar_contrato(t2, t3, t4)
    d = t2.merge(t3, on="sector_id").merge(t4, on="sector_id")
    if umbral_defecto is None:
        umbral_defecto = 2 * d["pct_filas_con_defecto"].median()
    d["elegible"] = True if cobertura_min is None else d["cobertura_pct"] >= cobertura_min
    e = d[d["elegible"]].copy()
    e["p_continuidad"] = (-e["continuidad_obs_pct"]).rank(pct=True)
    e["p_diferencia"] = e["dif_volumen_pct"].rank(pct=True)
    e["p_energia"] = (e["kwh_por_m3"].rank(pct=True) + e["costo_clp_por_m3"].rank(pct=True)) / 2
    e["puntaje"] = e[["p_continuidad", "p_diferencia", "p_energia"]].mean(axis=1)
    e["posicion"] = e["puntaje"].rank(ascending=False, method="min").astype(int)
    e["tipo_inspeccion"] = np.where(e["pct_filas_con_defecto"] > umbral_defecto, "sensor primero", "operación")
    e["continuidad_vs_meta"] = np.select(
        [e["continuidad_max_pct"] < meta, e["continuidad_min_pct"] < meta],
        ["bajo la meta incluso en el mejor caso", "el intervalo cruza la meta"], "sobre la meta")
    e["filtro_cobertura"] = "sin filtro" if cobertura_min is None else f"cobertura ≥ {cobertura_min}%"
    e["umbral_defecto_pct"] = round(umbral_defecto, 3)
    return e.sort_values("posicion").reset_index(drop=True)


def comparar_rankings(t2, t3, t4, umbrales=(None, 80, 85, 90, 95)):
    """Rankings con y sin filtro de cobertura (sensibilidad del umbral)."""
    return pd.concat([ranking(t2, t3, t4, cobertura_min=u) for u in umbrales], ignore_index=True)


def datos_de_prueba(semilla=20261011):
    """DATOS DE PRUEBA INVENTADOS (D-03): solo para verificar que el ranking corre. No publicar."""
    rng = np.random.default_rng(semilla)
    sectores = [f"A-S{i:02d}" for i in range(30)]
    filas = rng.integers(3000, 3700, 30)
    defectos = (filas * rng.uniform(0.005, 0.06, 30)).astype(int)
    t2 = pd.DataFrame({"sector_id": sectores, "filas": filas, "filas_con_defecto": defectos,
                       "pct_filas_con_defecto": 100 * defectos / filas})
    esperadas = np.full(30, 3672)
    obs = (esperadas * rng.uniform(0.75, 1.0, 30)).astype(int)
    cont = rng.uniform(99.0, 99.95, 30)
    t3 = pd.DataFrame({"sector_id": sectores, "horas_esperadas": esperadas, "horas_observadas": obs,
                       "cobertura_pct": 100 * obs / esperadas, "continuidad_obs_pct": cont,
                       "continuidad_min_pct": cont - 100 * (1 - obs / esperadas),
                       "continuidad_max_pct": np.minimum(cont + 0.05, 100)})
    t4 = pd.DataFrame({"sector_id": sectores, "m3_entrada": rng.uniform(1e6, 3e6, 30),
                       "dif_volumen_pct": rng.uniform(10, 35, 30), "kwh_por_m3": rng.uniform(0.2, 0.35, 30),
                       "costo_clp_por_m3": rng.uniform(25, 45, 30)})
    return t2, t3, t4
