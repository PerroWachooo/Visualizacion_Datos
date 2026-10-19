"""T4 · EDA de negocio, costo por m3 y 6 KPI (E1).

Lo usa E1/T4_eda_negocio.ipynb. Todo se calcula sobre lecturas válidas
(T2_reglas.lecturas_validas), con la misma referencia que T2 (sesgo_kpi):
volúmenes en m3 con unidad conocida, entrada >= 0, salida <= entrada, minutos en [0, 60].
Nada se imputa: las exclusiones se cuentan y se informan (exclusiones()).

Período de KPI y ranking: ago–dic 2025 UTC (único con tarifas y conexiones vigentes).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import comun
import T2_reglas as rq

E1 = Path(__file__).resolve().parent
TABLAS = E1 / "salidas" / "tablas"
FIGURAS = E1 / "salidas" / "figuras"
INICIO_AGO_DIC = pd.Timestamp("2025-08-01", tz="UTC")
FIN_AGO_DIC = pd.Timestamp("2026-01-01", tz="UTC")
PRESION_BAJA_BAR = 3.0           # supuesto docente de KPI-06 (sensibilidad: 2.5 y 3.5)
META_CONTINUIDAD = 99.5          # metas_2025_ancho.csv, sentido mínimo
CORTES = {"2025-07-08": "corte base", "2025-08-08": "corte actualización", "2026-01-08": "corte ampliación"}
SEMILLA = 20260924


def _b(mascara):
    return mascara.fillna(False).astype(bool)


def preparar():
    """Telemetría parseada, contexto de T2 y máscaras de población para T4."""
    df = comun.parse_exploratorio(comun.cargar_lotes())
    ctx = rq.contexto()
    ev = rq.evaluar_reglas(df, ctx)
    valida = _b(rq.lecturas_validas(df, ev))
    e, s = df["volumen_entrada_m3"], df["volumen_salida_m3"]
    vol_ok = _b(valida & e.notna() & s.notna() & (e >= 0) & (s <= e))
    min_ok = _b(valida & df["minutos_interrupcion"].between(0, 60))
    en_ago_dic = _b(df["fecha"].ge(INICIO_AGO_DIC) & df["fecha"].lt(FIN_AGO_DIC))
    df = df.assign(valida=valida, vol_ok=vol_ok, min_ok=min_ok,
                   ago_dic=_b(valida & en_ago_dic), mes=df["fecha"].dt.strftime("%Y-%m"))
    return df, ctx, ev


# ---------------------------------------------------------------------------------------------
# Exclusiones declaradas (T4: cantidad, denominador y efecto)
# ---------------------------------------------------------------------------------------------
def exclusiones(df):
    """Cuántas lecturas válidas quedan fuera de cada análisis, en ene–dic y ago–dic."""
    filas = []
    for pop, mask in [("ene–dic 2025", df["valida"]), ("ago–dic 2025", df["ago_dic"])]:
        v = df[mask]
        e, s, m = v["volumen_entrada_m3"], v["volumen_salida_m3"], v["minutos_interrupcion"]
        desconocida = v["_unidad_desconocida"]
        conds = [
            ("Lecturas válidas (denominador)", pd.Series(True, index=v.index)),
            ("Volumen de entrada no convertible (unidad desconocida)", desconocida),
            ("Volumen de entrada nulo o PENDIENTE (unidad conocida)", e.isna() & ~desconocida),
            ("Volumen de salida no convertible", s.isna() & e.notna()),
            ("Volumen de entrada negativo", e < 0),
            ("Salida mayor que entrada", (s > e) & (e >= 0)),
            ("Minutos de interrupción fuera de 0–60", ~m.between(0, 60)),
        ]
        n_base = len(v)
        for nombre, cond in conds:
            n = int(_b(cond).sum())
            filas.append({"poblacion": pop, "concepto": nombre, "n": n, "denominador": n_base,
                          "pct": round(100 * n / n_base, 3)})
        filas.append({"poblacion": pop, "concepto": "Lecturas que entran a vol_ok (volúmenes)",
                      "n": int(v["vol_ok"].sum()), "denominador": n_base,
                      "pct": round(100 * v["vol_ok"].sum() / n_base, 3)})
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------------------------
# Análisis (a)–(e)
# ---------------------------------------------------------------------------------------------
def distribucion(df):
    """(a) Medidas descriptivas de las variables de decisión, con n y RIC."""
    v = df[df["vol_ok"]]
    vars_ = {
        "volumen_entrada_m3 (m3 por hora)": v["volumen_entrada_m3"].astype(float),
        "diferencia entrada − salida (m3 por hora)": (v["volumen_entrada_m3"] - v["volumen_salida_m3"]).astype(float),
        "presion_bar": df.loc[df["valida"], "presion_bar"].astype(float),
        "energia_kwh (por hora)": df.loc[df["valida"], "energia_kwh"].astype(float),
        "minutos_interrupcion (solo horas con 0–60)": df.loc[df["min_ok"], "minutos_interrupcion"].astype(float),
    }
    filas = []
    for nombre, s in vars_.items():
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        filas.append({"variable": nombre, "n": int(s.count()), "media": s.mean(), "mediana": s.median(),
                      "p25": q1, "p75": q3, "ric": q3 - q1, "min": s.min(), "max": s.max()})
    return pd.DataFrame(filas)


def proporcion_interrupcion(df):
    """(a, detalle) Cero ≠ nulo: horas sin interrupción medida vs. con interrupción."""
    m = df.loc[df["min_ok"], "minutos_interrupcion"]
    n = len(m)
    return {"n": n, "sin_interrupcion": int((m == 0).sum()), "con_interrupcion": int((m > 0).sum()),
            "pct_con_interrupcion": 100 * (m > 0).mean(),
            "mediana_si_hay": m[m > 0].median(), "p90_si_hay": m[m > 0].quantile(0.9)}


def categorias(df):
    """(b) modo_operacion y unidad_volumen por lote (proporciones dentro de cada lote)."""
    modo = (df.groupby("lote")["modo_operacion"].value_counts(normalize=True)
            .rename("proporcion").reset_index())
    modo["variable"] = "modo_operacion (normalizado)"
    modo = modo.rename(columns={"modo_operacion": "categoria"})
    unidad = (df.groupby("lote")["unidad_volumen"].value_counts(normalize=True)
              .rename("proporcion").reset_index())
    unidad["variable"] = "unidad_volumen (crudo)"
    unidad = unidad.rename(columns={"unidad_volumen": "categoria"})
    out = pd.concat([modo, unidad], ignore_index=True)
    out["proporcion"] = out["proporcion"].round(5)
    return out[["variable", "lote", "categoria", "proporcion"]]


def serie_semanal(df):
    """(c) Evolución semanal (lunes UTC). Cada cifra usa su propio denominador."""
    v = df[df["valida"] & df["fecha"].notna()].copy()
    v["semana"] = v["fecha"].dt.tz_localize(None).dt.to_period("W-SUN").dt.start_time
    vol = v[v["vol_ok"]]
    mi = v[v["min_ok"]]
    g_vol = vol.groupby("semana")
    out = pd.DataFrame({
        "horas_validas": v.groupby("semana").size(),
        "entrada_m3_media_por_hora": g_vol["volumen_entrada_m3"].mean().astype(float),
        "kwh_por_m3": g_vol["energia_kwh"].sum() / g_vol["volumen_entrada_m3"].sum().astype(float),
        "pct_horas_con_interrupcion": 100 * mi.groupby("semana")["minutos_interrupcion"].apply(lambda s: (s > 0).mean()),
        "pct_horas_presion_baja": 100 * v.groupby("semana")["presion_bar"].apply(lambda s: (s < PRESION_BAJA_BAR).mean()),
    })
    return out.reset_index()


def comparar_segmentos(df):
    """(d) Sectores y modo de operación. Modo: ene–dic, lecturas válidas (vol_ok para volúmenes)."""
    filas = []
    for modo, g in df[df["valida"]].groupby("modo_operacion"):
        vol = g[g["vol_ok"]]
        mi = g[g["min_ok"]]
        filas.append({
            "modo_operacion": modo,
            "horas_validas": len(g),
            "horas_con_volumen_ok": len(vol),
            "kwh_por_m3": vol["energia_kwh"].sum() / vol["volumen_entrada_m3"].sum(),
            "dif_volumen_pct": 100 * (vol["volumen_entrada_m3"] - vol["volumen_salida_m3"]).sum() / vol["volumen_entrada_m3"].sum(),
            "presion_mediana_bar": g["presion_bar"].median(),
            "pct_horas_con_interrupcion": 100 * (mi["minutos_interrupcion"] > 0).mean(),
            "horas_con_interrupcion": int((mi["minutos_interrupcion"] > 0).sum()),
        })
    return pd.DataFrame(filas)


def correlaciones(df):
    """(e) Solo variables interpretables. Asociación ≠ efecto."""
    v = df[df["vol_ok"]].copy()
    v["dif_m3"] = (v["volumen_entrada_m3"] - v["volumen_salida_m3"]).astype(float)
    v["entrada_m3"] = v["volumen_entrada_m3"].astype(float)
    v["energia"] = v["energia_kwh"].astype(float)
    v["presion"] = v["presion_bar"].astype(float)
    pares = [("energia_kwh vs volumen_entrada_m3", "energia", "entrada_m3"),
             ("presion_bar vs diferencia entrada − salida (m3)", "presion", "dif_m3")]
    filas = []
    for nombre, x, y in pares:
        par = v[[x, y]].dropna()
        filas.append({"par": nombre, "n": len(par),
                      "pearson": par[x].corr(par[y], method="pearson"),
                      "spearman": par[x].rank().corr(par[y].rank(), method="pearson")})  # Spearman sin scipy
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------------------------
# Costo por m3 (P2): unidad, energía y tarifa
# ---------------------------------------------------------------------------------------------
def _costo_horas(df, ctx):
    t = ctx["tarifas"][["sector_id", "mes", "tarifa_kwh_clp"]].copy()
    t["mes"] = t["mes"].astype(str)
    d = df[df["ago_dic"] & df["vol_ok"] & df["energia_kwh"].notna()].copy()
    d["mes"] = d["mes"].astype(str)
    d = d.merge(t, on=["sector_id", "mes"], how="left", validate="m:1")
    assert d["tarifa_kwh_clp"].notna().all(), "hay sector-mes sin tarifa dentro de ago–dic"
    d["kwh"] = d["energia_kwh"].astype(float)
    d["m3"] = d["volumen_entrada_m3"].astype(float)
    d["m3_sin_convertir"] = d["volumen_entrada"].astype(float)   # litros tratados como m3 (error a evitar)
    d["costo"] = d["kwh"] * d["tarifa_kwh_clp"].astype(float)
    d["razon_h"] = np.where(d["m3"] > 0, d["costo"] / d["m3"].where(d["m3"] > 0), np.nan)
    return d


def _resumen_costo(d):
    kwh, m3, costo = d["kwh"].sum(), d["m3"].sum(), d["costo"].sum()
    return pd.Series({
        "filas": len(d), "m3_entrada": m3, "kwh": kwh, "costo_clp": costo,
        "kwh_por_m3": kwh / m3, "tarifa_clp_kwh_ponderada": costo / kwh,
        "costo_clp_por_m3": costo / m3,
        "costo_clp_por_m3_sin_convertir_litros": costo / d["m3_sin_convertir"].sum(),
        "costo_clp_por_m3_promedio_razones_horarias": d["razon_h"].mean(),
        "horas_sin_m3_positivo": int((d["m3"] <= 0).sum()),
    })


def costo_m3(df, ctx):
    """Tabla T4_costo_m3: por mes y total. Descomposición contra agosto:
    Δcosto/m3 = efecto_energia (kWh/m3) + efecto_tarifa (CLP/kWh), sin residuo."""
    d = _costo_horas(df, ctx)
    meses = sorted(d["mes"].unique())
    filas = []
    base = None
    for mes in meses:
        r = _resumen_costo(d[d["mes"] == mes])
        if base is None:
            base = r
        ef_e = (r["kwh_por_m3"] - base["kwh_por_m3"]) * base["tarifa_clp_kwh_ponderada"]
        ef_t = r["kwh_por_m3"] * (r["tarifa_clp_kwh_ponderada"] - base["tarifa_clp_kwh_ponderada"])
        filas.append({"bloque": "mes", "clave": mes, **r.to_dict(),
                      "delta_vs_agosto_clp_m3": r["costo_clp_por_m3"] - base["costo_clp_por_m3"],
                      "efecto_energia_clp_m3": ef_e, "efecto_tarifa_clp_m3": ef_t})
    total = _resumen_costo(d)
    filas.append({"bloque": "total", "clave": "ago–dic", **total.to_dict(),
                  "delta_vs_agosto_clp_m3": np.nan, "efecto_energia_clp_m3": np.nan, "efecto_tarifa_clp_m3": np.nan})
    out = pd.DataFrame(filas)
    cols = ["bloque", "clave", "filas", "m3_entrada", "kwh", "costo_clp", "kwh_por_m3", "tarifa_clp_kwh_ponderada",
            "costo_clp_por_m3", "costo_clp_por_m3_sin_convertir_litros", "costo_clp_por_m3_promedio_razones_horarias",
            "horas_sin_m3_positivo", "delta_vs_agosto_clp_m3", "efecto_energia_clp_m3", "efecto_tarifa_clp_m3"]
    return out[cols]


# ---------------------------------------------------------------------------------------------
# KPI (W6) y tabla por sector (contrato del README)
# ---------------------------------------------------------------------------------------------
def kpi_valores(df, ctx):
    """Valores de los KPI de ago–dic (y su denominador). KPI-01 se toma de T3."""
    a = df[df["ago_dic"]]
    vol = a[a["vol_ok"]]
    mi = a[a["min_ok"]]
    d = _costo_horas(df, ctx)
    t3 = pd.read_csv(TABLAS / "T3_continuidad_sector_ago_dic.csv")
    horas_obs = t3["horas_observadas"].sum()
    return {
        "KPI-01 continuidad (T3, sectores bajo meta con límite superior)": int((t3["continuidad_max_pct"] < META_CONTINUIDAD).sum()),
        "KPI-02 diferencia de volúmenes (%)": 100 * (vol["volumen_entrada_m3"] - vol["volumen_salida_m3"]).sum() / vol["volumen_entrada_m3"].sum(),
        "KPI-03 intensidad energética (kWh/m3)": vol["energia_kwh"].sum() / vol["volumen_entrada_m3"].sum(),
        "KPI-04 costo de energía (CLP/m3)": d["costo"].sum() / vol["volumen_entrada_m3"].sum(),
        "KPI-05 horas con interrupción (%)": 100 * (mi["minutos_interrupcion"] > 0).mean(),
        "KPI-06 horas con presión baja (%)": 100 * (a["presion_bar"] < PRESION_BAJA_BAR).mean(),
        "KPI-06 sensibilidad 2,5 bar (%)": 100 * (a["presion_bar"] < 2.5).mean(),
        "KPI-06 sensibilidad 3,5 bar (%)": 100 * (a["presion_bar"] < 3.5).mean(),
        "denominador KPI-02/03/04 (lecturas con volumen válido)": len(vol),
        "denominador KPI-05/06 (horas observadas válidas, ago–dic)": len(mi),
        "horas observadas T3 (ago–dic)": horas_obs,
    }


def por_sector(df, ctx):
    """T4_por_sector.csv: contrato del README (30 filas, ago–dic)."""
    vol = df[df["ago_dic"] & df["vol_ok"]].copy()
    vol["e"] = vol["volumen_entrada_m3"].astype(float)
    vol["s"] = vol["volumen_salida_m3"].astype(float)
    g = vol.groupby("sector_id").agg(entrada_total=("e", "sum"),
                                     salida_total=("s", "sum"), kwh=("energia_kwh", "sum"))
    g["m3_entrada"] = g["entrada_total"]
    g["dif_volumen_pct"] = 100 * (g["entrada_total"] - g["salida_total"]) / g["entrada_total"]
    g["kwh_por_m3"] = g["kwh"] / g["m3_entrada"]
    c = _costo_horas(df, ctx).groupby("sector_id")["costo"].sum()
    g["costo_clp_por_m3"] = c / g["m3_entrada"]
    g = g.reindex(sorted(ctx["sectores"]["sector_id"]))
    return g.reset_index()[["sector_id", "m3_entrada", "dif_volumen_pct", "kwh_por_m3", "costo_clp_por_m3"]]


FICHAS_KPI = [
    {"id": "KPI-01", "tipo_KPI_KRI_visual": "KPI · barras con intervalo por sector (0/60 min)",
     "objetivo": "Continuidad ponderada por conexiones del servicio, con horas desconocidas acotadas entre 0 y 60 min. Responde si un sector cumple la meta docente con lo observado.",
     "formula": "Observada = 100 × (1 − min. interrumpidos / min. de conexión observados); límite superior = 100 × (1 − interrumpidos / esperados) [horas ausentes = 0 min]; límite inferior = 100 × (1 − (interrumpidos + desconocidos) / esperados) [horas ausentes = 60 min]. Minutos ponderados por conexiones vigentes",
     "numerador": "Minutos de conexión interrumpidos (observados); para el límite inferior, más minutos de conexión de horas ausentes (60 min × conexiones)",
     "denominador": "Minutos de conexión esperados = Σ conexiones vigentes × 60 min por hora del calendario UTC (observada: minutos observados)",
     "unidad": "%", "granularidad": "Sector × ago–dic 2025 (ranking); semanal en T3",
     "fuente_columnas": "telemetria_horaria: fecha, sector_id, minutos_interrupcion; complementarios/sectores_historial.csv: conexiones (vigencia por fecha)",
     "filtros": "Lecturas válidas (T2_reglas.lecturas_validas); minutos en [0, 60]; cálculo oficial en T3 (P1)",
     "periodo_corte": "ago–dic 2025 UTC (corte del lote ampliación: 2026-01-08)",
     "tratamiento_nulos": "Hora sin lectura = AUSENTE: no se imputa 0; se reporta como intervalo [0 min, 60 min]",
     "umbral": "99,5", "version_umbral": "v0-E1 (meta docente de metas_2025_ancho.csv)",
     "responsable": "T4 (por confirmar) · cálculo oficial T3",
     "accion": "Si el límite superior queda bajo la meta, el sector se prioriza; si el intervalo cruza la meta, primero recolectar evidencia de transmisión."},
    {"id": "KPI-02", "tipo_KPI_KRI_visual": "KPI · barras por sector ordenadas",
     "objetivo": "Balance hídrico: cuánto del volumen de entrada no sale del sector. Responde dónde el balance es más desfavorable para revisar medición y fugas.",
     "formula": "100 × Σ(entrada − salida) / Σ entrada (razón de sumas)",
     "numerador": "Σ (volumen_entrada_m3 − volumen_salida_m3) en lecturas con volumen válido",
     "denominador": "Σ volumen_entrada_m3 en las mismas lecturas",
     "unidad": "%", "granularidad": "Sector × período; total de red",
     "fuente_columnas": "telemetria_horaria: volumen_entrada, volumen_salida, unidad_volumen (L → m3 ÷ 1000)",
     "filtros": "Lecturas válidas; unidad conocida; entrada ≥ 0; salida ≤ entrada (misma referencia que T2 sesgo_kpi)",
     "periodo_corte": "ago–dic 2025 UTC (ranking); ene–dic 2025 como contexto",
     "tratamiento_nulos": "Volumen nulo, PENDIENTE o unidad 'unidad?' = NA: se excluye y se cuenta; nunca se adivina la unidad",
     "umbral": "sin meta docente", "version_umbral": "v0-E1",
     "responsable": "T4 (por confirmar)",
     "accion": "Sectores con mayor diferencia: revisar medición de entrada y salida antes de atribuir pérdidas a fugas."},
    {"id": "KPI-03", "tipo_KPI_KRI_visual": "KPI · barras por sector y serie mensual",
     "objetivo": "Energía por unidad de agua entregada. Responde qué sectores consumen más energía por m3.",
     "formula": "Σ energia_kwh / Σ volumen_entrada_m3",
     "numerador": "Σ energia_kwh en lecturas con volumen válido",
     "denominador": "Σ volumen_entrada_m3 en las mismas lecturas",
     "unidad": "kWh/m3", "granularidad": "Sector × mes; total de red",
     "fuente_columnas": "telemetria_horaria: energia_kwh, volumen_entrada (unidad)",
     "filtros": "Lecturas válidas con volumen válido (vol_ok)",
     "periodo_corte": "ago–dic 2025 UTC",
     "tratamiento_nulos": "Energía sin valor no ocurre en lecturas válidas; volumen NA excluye la lectura de numerador y denominador",
     "umbral": "sin meta docente", "version_umbral": "v0-E1",
     "responsable": "T4 (por confirmar)",
     "accion": "Sectores con kWh/m3 alto frente al resto: revisar bombeo y presión antes de atribuir ineficiencia."},
    {"id": "KPI-04", "tipo_KPI_KRI_visual": "KPI · barras por sector y descomposición mensual",
     "objetivo": "Costo de energía por m3 entregado. Responde qué sectores tienen mayor costo unitario de energía.",
     "formula": "Σ (energia_kwh × tarifa_kwh_clp) / Σ volumen_entrada_m3 (razón de sumas)",
     "numerador": "Σ costo de energía por hora (kWh × tarifa del sector-mes)",
     "denominador": "Σ volumen_entrada_m3 en las mismas lecturas",
     "unidad": "CLP/m3", "granularidad": "Sector × mes; total de red",
     "fuente_columnas": "telemetria_horaria: energia_kwh, volumen_entrada; complementarios/tarifas_energia.csv: tarifa_kwh_clp por sector + mes",
     "filtros": "Lecturas con volumen válido; solo ago–dic (tarifas N:1 por sector y mes)",
     "periodo_corte": "ago–dic 2025 UTC",
     "tratamiento_nulos": "Tarifa ausente antes de agosto = fuera de alcance (no es 0); sector-mes sin tarifa dentro de ago–dic no ocurre (se verifica con assert)",
     "umbral": "sin meta docente", "version_umbral": "v0-E1",
     "responsable": "T4 (por confirmar)",
     "accion": "Separar si el costo sube por energía (kWh/m3) o por tarifa (CLP/kWh) antes de proponer medidas."},
    {"id": "KPI-05", "tipo_KPI_KRI_visual": "KPI · barra de proporción por sector",
     "objetivo": "Frecuencia de horas con interrupción observada. Responde en qué sectores la interrupción aparece con mayor frecuencia.",
     "formula": "100 × horas observadas con minutos_interrupcion > 0 / horas observadas válidas",
     "numerador": "Horas válidas con minutos_interrupcion > 0",
     "denominador": "Horas observadas válidas (minutos en [0, 60])",
     "unidad": "%", "granularidad": "Sector × período",
     "fuente_columnas": "telemetria_horaria: minutos_interrupcion, fecha, sector_id",
     "filtros": "Lecturas válidas; minutos en [0, 60] (los > 60 se cuentan aparte, RQ-VAL-08)",
     "periodo_corte": "ago–dic 2025 UTC",
     "tratamiento_nulos": "0 = sin interrupción medida (dato). Hora ausente NO entra en el denominador: se informa con cobertura de T3",
     "umbral": "sin meta docente", "version_umbral": "v0-E1",
     "responsable": "T4 (por confirmar)",
     "accion": "Sectores con frecuencia alta: cruzar con continuidad (T3) antes de inspeccionar."},
    {"id": "KPI-06", "tipo_KPI_KRI_visual": "KPI · serie semanal con umbral",
     "objetivo": "Frecuencia de presión baja en la red. Es una señal operacional del escenario, no un criterio sanitario.",
     "formula": "100 × horas observadas válidas con presion_bar < 3,0 / horas observadas válidas",
     "numerador": "Horas válidas con presion_bar < 3,0 bar",
     "denominador": "Horas observadas válidas",
     "unidad": "%", "granularidad": "Sector × semana",
     "fuente_columnas": "telemetria_horaria: presion_bar, fecha, sector_id",
     "filtros": "Lecturas válidas (sin copias ni sector-horas repetidas)",
     "periodo_corte": "ago–dic 2025 UTC",
     "tratamiento_nulos": "Presión sin valor no ocurre en lecturas válidas; horas ausentes no entran al denominador",
     "umbral": "3,0 bar (supuesto docente; sensibilidad 2,5 y 3,5)", "version_umbral": "v0-E1 (a validar con el profesor)",
     "responsable": "T4 (por confirmar)",
     "accion": "Concentraciones de presión baja: revisar telemetría de presión del sector antes de atribuir causas hidráulicas."},
]


def fichas_kpi():
    return pd.DataFrame(FICHAS_KPI)


def tablas_t4(df, ctx):
    """Todas las tablas de T4 (sin escribir nada)."""
    return {
        "T4_exclusiones": exclusiones(df),
        "T4_costo_m3": costo_m3(df, ctx),
        "T4_fichas_kpi": fichas_kpi(),
        "T4_por_sector": por_sector(df, ctx),
    }


def exportar_tablas(tablas):
    """Escribe los productos de T4 en salidas/tablas (solo los nombres del README)."""
    TABLAS.mkdir(parents=True, exist_ok=True)
    for nombre, tabla in tablas.items():
        tabla.to_csv(TABLAS / f"{nombre}.csv", index=False, encoding="utf-8")


# ---------------------------------------------------------------------------------------------
# Figuras (convenciones de grafico-diagnostico: título con hallazgo, unidades, nota de datos simulados)
# ---------------------------------------------------------------------------------------------
BLOQUE_ALTO = [f"A-S{i}" for i in range(20, 30)]   # sectores con diferencia ~24% (ver H2)


def _limpio(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)


def _pie(fig, texto=None):
    fig.text(0.01, 0.005, comun.NOTA_FUENTE + ("\n" + texto if texto else ""), fontsize=8, color="#555555", va="bottom")


def fig_a_distribucion(df):
    """(a) Volumen, presión e interrupciones: las horas con interrupción son minoría y se separan."""
    v = df[df["vol_ok"]]
    p = df.loc[df["valida"], "presion_bar"].astype(float)
    m = df.loc[df["min_ok"], "minutos_interrupcion"].astype(float)
    fig, ax = plt.subplots(1, 3, figsize=(13, 4.2))
    ax[0].hist(v["volumen_entrada_m3"].astype(float), bins=60, color=comun.PALETA["acento"])
    ax[0].set(title="Volumen de entrada: mediana 593 m³/h", xlabel="m³ por hora (ene–dic 2025)", ylabel="horas")
    ax[1].hist(p, bins=60, color=comun.PALETA["neutro"])
    ax[1].axvline(PRESION_BAJA_BAR, color=comun.PALETA["alerta"], ls="--")
    ax[1].text(PRESION_BAJA_BAR + 0.05, ax[1].get_ylim()[1] * 0.9, "3,0 bar (supuesto)", color=comun.PALETA["alerta"], fontsize=9)
    ax[1].set(title="Presión: 2,2% de horas bajo 3,0 bar (ago–dic)", xlabel="bar", ylabel="horas")
    cero = (m == 0).sum()
    ax[2].bar(["0 min\n(sin interrupción)", ">0 min\n(con interrupción)"], [cero, (m > 0).sum()],
              color=[comun.PALETA["neutro"], comun.PALETA["alerta"]])
    ax[2].set(title="Interrupción: 4,3% de horas > 0 min", ylabel="horas válidas (0–60 min)")
    for a in ax:
        _limpio(a)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    _pie(fig, "Denominador: lecturas válidas. Volúmenes en m³ con unidad conocida, entrada ≥ 0, salida ≤ entrada.")
    return fig


def fig_b_categorias(df):
    """(b) Modo de operación y unidad por lote (proporción dentro de cada lote)."""
    cat = categorias(df)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    modo = cat[cat["variable"].str.startswith("modo")].pivot(index="lote", columns="categoria", values="proporcion")
    modo = modo.loc[["base", "actualizacion", "ampliacion"]]
    modo.plot(kind="bar", stacked=True, ax=ax[0], color=[comun.PALETA["neutro"], comun.PALETA["alerta"]], rot=0)
    ax[0].set(title="Modo: ~2,5% de horas en mantenimiento en cada lote", xlabel="", ylabel="proporción")
    ax[0].legend(title="modo (normalizado)", loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    uni = cat[cat["variable"].str.startswith("unidad")].pivot(index="lote", columns="categoria", values="proporcion")
    uni = uni.loc[["base", "actualizacion", "ampliacion"]].fillna(0)
    uni.plot(kind="bar", stacked=True, ax=ax[1], color=[comun.PALETA["acento"], comun.PALETA["alerta"], "#BBBBBB"], rot=0)
    ax[1].set(title="Unidad: L sube de 11% (base) a 25% (ampliación)", xlabel="", ylabel="proporción de filas")
    ax[1].legend(title="unidad (cruda)", loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    for a in ax:
        _limpio(a)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    _pie(fig, "Denominador: filas físicas de cada lote (253.404 en total). Modo sobre filas tras normalizar espacios y mayúsculas.")
    return fig


def fig_c_evolucion(serie):
    """(c) Evolución semanal: la energía por m3 es estable; la interrupción y la presión baja cambian."""
    fig, ax = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    ax[0].plot(serie["semana"], serie["kwh_por_m3"], color=comun.PALETA["acento"])
    ax[0].set(title="Red: kWh/m³ baja en abril (0,27 → 0,26) por un grupo de 10 sectores", ylabel="kWh/m³")
    ax[1].plot(serie["semana"], serie["pct_horas_con_interrupcion"], color=comun.PALETA["alerta"])
    ax[1].set(title="Horas con interrupción: de ~3,5% a ~5% desde abril (% de horas válidas)", ylabel="%")
    ax[2].plot(serie["semana"], serie["pct_horas_presion_baja"], color=comun.PALETA["neutro"])
    ax[2].set(title="Horas con presión < 3,0 bar: de ~1,2% a ~2,3% desde abril (% de horas válidas)", ylabel="%")
    for a in ax:
        _limpio(a)
        for corte, etiqueta in CORTES.items():
            a.axvline(pd.Timestamp(corte), color="#777777", ls=":", lw=1)
    ax[0].text(pd.Timestamp("2025-07-08"), ax[0].get_ylim()[1], " cortes de lote", fontsize=8, color="#555555", va="top")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _pie(fig, "Semanas lunes–domingo UTC; la última y primera pueden estar incompletas. Ver tabla T4_evolucion_semanal.")
    return fig


def fig_d_segmentos(df, ps):
    """(d) Sectores ordenados y quiebre temporal de la diferencia de volúmenes por grupo."""
    fig, ax = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1.1, 1]})
    ordenado = ps.sort_values("dif_volumen_pct")
    colores = [comun.PALETA["alerta"] if s in BLOQUE_ALTO else comun.PALETA["neutro"] for s in ordenado["sector_id"]]
    ax[0].barh(ordenado["sector_id"], ordenado["dif_volumen_pct"], color=colores)
    ax[0].set(title="Diferencia de volúmenes ago–dic: 10 sectores en ~24% vs ~15%", xlabel="% (Σ entrada − salida) / Σ entrada")
    ax[0].tick_params(axis="y", labelsize=7)
    v = df[df["vol_ok"]].copy()
    v["grupo"] = np.where(v["sector_id"].isin(BLOQUE_ALTO), "A-S20 a A-S29", "resto (20 sectores)")
    v["e"] = v["volumen_entrada_m3"].astype(float)
    v["s"] = v["volumen_salida_m3"].astype(float)
    mensual = v.groupby(["mes", "grupo"]).apply(lambda g: 100 * (g["e"] - g["s"]).sum() / g["e"].sum(), include_groups=False).unstack()
    for grupo, color in [("A-S20 a A-S29", comun.PALETA["alerta"]), ("resto (20 sectores)", comun.PALETA["neutro"])]:
        ax[1].plot(pd.to_datetime(mensual.index), mensual[grupo], marker="o", color=color, label=grupo)
    ax[1].set(title="Quiebres en abril y agosto 2025, no en octubre", ylabel="% diferencia de volúmenes", ylim=(0, 30))
    ax[1].tick_params(axis="x", rotation=45)
    ax[1].legend(loc="lower right")
    for a in ax:
        _limpio(a)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _pie(fig, "Izq.: ago–dic 2025 por sector. Der.: ene–dic 2025 por mes UTC. Lecturas con volumen válido.")
    return fig


def fig_e_bivariada(df):
    """(e) Energía vs volumen (asociación alta, esperable por el modelo) y presión vs diferencia (sin asociación)."""
    v = df[df["vol_ok"]].sample(20000, random_state=SEMILLA)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    ax[0].scatter(v["volumen_entrada_m3"].astype(float), v["energia_kwh"].astype(float), s=4, alpha=0.3, color=comun.PALETA["acento"])
    ax[0].set(title="Energía y volumen de entrada: r = 0,96", xlabel="volumen de entrada (m³/h)", ylabel="energía (kWh/h)")
    dif = (v["volumen_entrada_m3"] - v["volumen_salida_m3"]).astype(float)
    ax[1].scatter(v["presion_bar"].astype(float), dif, s=4, alpha=0.3, color=comun.PALETA["neutro"])
    ax[1].set(title="Presión y diferencia de volúmenes: r ≈ 0", xlabel="presión (bar)", ylabel="entrada − salida (m³/h)")
    for a in ax:
        _limpio(a)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    _pie(fig, "Muestra aleatoria de 20.000 de 246.096 horas con volumen válido (semilla 20260924). Asociación, no causalidad.")
    return fig


def fig_costo(costo):
    """Costo por m3 por mes: la variación viene de la tarifa, no de la energía por m3."""
    m = costo[costo["bloque"] == "mes"].copy()
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    x = m["clave"]
    ax[0].bar(x, m["costo_clp_por_m3"], color=comun.PALETA["neutro"])
    ax[0].plot(x, m["costo_clp_por_m3_promedio_razones_horarias"], color=comun.PALETA["alerta"], marker="o", label="promedio de razones horarias")
    ax[0].set(title="Costo de energía por m³: 34,9 → 40,4 CLP (ago → dic)", ylabel="CLP/m³", ylim=(0, 48))
    ax[0].legend(loc="lower right")
    ancho = 0.4
    idx = np.arange(len(x))
    ax[1].bar(idx - ancho / 2, m["efecto_energia_clp_m3"], ancho, color=comun.PALETA["acento"], label="efecto energía (kWh/m³)")
    ax[1].bar(idx + ancho / 2, m["efecto_tarifa_clp_m3"], ancho, color=comun.PALETA["alerta"], label="efecto tarifa (CLP/kWh)")
    ax[1].set_xticks(idx, x)
    ax[1].set(title="Descomposición del cambio vs agosto: casi todo es tarifa", ylabel="CLP/m³")
    ax[1].legend(loc="upper left")
    for a in ax:
        _limpio(a)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    _pie(fig, "Razón de sumas (Σ costo / Σ m³). Costo = kWh × tarifa del sector-mes; ago–dic 2025 UTC.")
    return fig


def generar_figuras(df, ctx, tablas, serie):
    """Genera las 6 figuras de T4 en salidas/figuras (una por análisis)."""
    FIGURAS.mkdir(parents=True, exist_ok=True)
    figs = {
        "T4_a_distribucion": fig_a_distribucion(df),
        "T4_b_categorias": fig_b_categorias(df),
        "T4_c_evolucion": fig_c_evolucion(serie),
        "T4_d_segmentos": fig_d_segmentos(df, tablas["T4_por_sector"]),
        "T4_e_bivariada": fig_e_bivariada(df),
        "T4_costo_m3": fig_costo(tablas["T4_costo_m3"]),
    }
    for nombre, fig in figs.items():
        fig.savefig(FIGURAS / f"{nombre}.png", dpi=150)
        plt.close(fig)
    return list(figs)

def ejecutar():
    """Corre T4 completo: tablas en salidas/tablas y figuras en salidas/figuras."""
    df, ctx, _ = preparar()
    tablas = tablas_t4(df, ctx)
    tablas["T4_evolucion_semanal"] = serie_semanal(df)
    exportar_tablas(tablas)
    generar_figuras(df, ctx, tablas, tablas["T4_evolucion_semanal"])
    return df, ctx, tablas


if __name__ == "__main__":
    ejecutar()
    print("T4 listo: tablas en", TABLAS, "y figuras en", FIGURAS)