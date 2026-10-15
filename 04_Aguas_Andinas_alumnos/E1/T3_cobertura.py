"""T3: cobertura y continuidad con incertidumbre. Datos simulados docentes.

Las funciones de cálculo no escriben ni modifican sus entradas. Solo exportar()
escribe tablas y figuras T3. Uso desde E1/:
    crudo, df, ctx, ev = preparar_datos()
    grilla = construir_grilla(df, ctx, ev)
    tablas = generar_tablas(df, ctx, ev, grilla)
    validar_resultados(df, ctx, ev, grilla, tablas)
    figuras = generar_figuras(tablas)
    exportar(tablas, figuras)
"""
from pathlib import Path

import numpy as np
import pandas as pd

import comun
import T2_reglas as rq

E1 = Path(__file__).resolve().parent
CLAVE = ["sector_id", "fecha"]
CONTRATO = rq.COLUMNAS_CONTRATO["t3"]


def preparar_datos():
    """Verifica originales y conserva crudo separado del dataframe exploratorio."""
    comun.verificar_hashes()
    crudo = comun.cargar_lotes()
    df = comun.parse_exploratorio(crudo)
    ctx = rq.contexto()
    ev = rq.evaluar_reglas(df, ctx)
    return crudo, df, ctx, ev


def metas_largas(ctx, nombre="metas_2025"):
    """Exploración del formato ancho; no se concatenan versiones de metas."""
    ancho = ctx[nombre]
    meses = [c for c in ancho.columns if c.startswith("m2025_")]
    largo = ancho.melt(id_vars=["sector_id", "indicador", "unidad", "sentido"],
                       value_vars=meses, var_name="mes", value_name="meta_pct")
    largo["mes"] = largo["mes"].str.replace("m2025_", "2025-", regex=False)
    largo["meta_pct"] = pd.to_numeric(largo["meta_pct"], errors="raise")
    if largo.duplicated(["sector_id", "indicador", "mes"]).any():
        raise ValueError("Las metas contienen claves repetidas.")
    if not largo["sentido"].eq("minimo").all() or not largo["indicador"].eq("continuidad_pct").all():
        raise ValueError("Revisar indicador y sentido de las metas antes de comparar continuidad.")
    if not largo["meta_pct"].between(0, 100).all():
        raise ValueError("Meta fuera del dominio porcentual.")
    return largo


def _matches_historial(base, historial):
    b = base[["sector_id", "fecha"]].copy().reset_index(drop=True)
    b["_fila"] = np.arange(len(b))
    candidatos = b[b["fecha"].notna()].merge(historial, on="sector_id", how="inner")
    dentro = candidatos["fecha"].ge(candidatos["vigente_desde"]) & candidatos["fecha"].lt(candidatos["vigente_hasta"])
    coincidencias = candidatos.loc[dentro].copy()
    cuentas = coincidencias.groupby("_fila").size().reindex(b["_fila"], fill_value=0)
    return coincidencias, cuentas


def incorporar_exposiciones(grilla):
    """Separa recepción de lectura, interrupción conocida y exposición desconocida.

    Los ceros de las contribuciones sumables son identidades de suma, no valores
    imputados: minutos_interrupcion y presion_bar se mantienen sin rellenar.
    """
    g = grilla.copy()
    pesos = g["conexiones"].astype(float)
    if not (np.isfinite(pesos) & pesos.gt(0)).all():
        raise ValueError("Cada hora necesita conexiones vigentes positivas y finitas.")
    minutos = g["minutos_interrupcion"].astype(float)
    presion = g["presion_bar"].astype(float)
    g["interrupcion_conocida"] = g["observada"] & np.isfinite(minutos) & minutos.between(0, 60)
    g["lectura_sin_interrupcion_valida"] = g["observada"] & ~g["interrupcion_conocida"]
    g["E"] = 60.0 * pesos
    g["O"] = g["E"].where(g["interrupcion_conocida"], 0.0)
    g["I"] = (minutos * pesos).where(g["interrupcion_conocida"], 0.0)
    g["U"] = g["E"] - g["O"]
    g["dia"] = g["fecha"].dt.floor("D")
    g["semana_inicio"] = g["dia"] - pd.to_timedelta(g["fecha"].dt.dayofweek, unit="D")
    g["mes"] = g["fecha"].dt.strftime("%Y-%m")
    g["hora_utc"] = g["fecha"].dt.hour
    g["par_valido"] = g["interrupcion_conocida"] & np.isfinite(presion) & presion.ge(0)
    g["presion_pareada"] = presion.where(g["par_valido"])
    g["minutos_pareados"] = minutos.where(g["par_valido"])
    return g


def construir_grilla(df, ctx, ev=None, periodos=None):
    """Calendario UTC con una fila por sector-hora, pesos y meta vigente."""
    if ev is None:
        ev = rq.evaluar_reglas(df, ctx)
    if ev["RQ-UNI-02"][0].any():
        raise ValueError("Hay claves con contenido conflictivo; revisar con T2 antes de elegir una lectura.")
    validas = df.loc[rq.lecturas_validas(df, ev)].copy()
    if validas["fecha"].isna().any() or validas["fecha"].ne(validas["fecha"].dt.floor("h")).any():
        raise ValueError("Las lecturas deben tener fecha válida alineada a una hora UTC.")
    if validas.duplicated(CLAVE).any():
        raise ValueError("La máscara de T2 dejó más de una lectura por sector-hora.")
    sectores = ctx["sectores"]["sector_id"]
    if sectores.isna().any() or sectores.duplicated().any():
        raise ValueError("El catálogo debe tener sectores únicos y no nulos.")
    calendarios = []
    for lote, (inicio, fin) in (rq.PERIODO_LOTE if periodos is None else periodos).items():
        horas = pd.date_range(inicio, fin, freq="h", tz="UTC", inclusive="left")
        calendario = pd.MultiIndex.from_product([sorted(sectores), horas], names=CLAVE).to_frame(index=False)
        calendarios.append(calendario.assign(lote=lote))
    g = pd.concat(calendarios, ignore_index=True)
    if g.duplicated(CLAVE).any():
        raise ValueError("Los calendarios de lotes se solapan.")
    columnas = ["lote", *CLAVE, "medicion_id", "minutos_interrupcion", "presion_bar"]
    g = g.merge(validas[columnas], on=["lote", *CLAVE], how="left", validate="one_to_one", indicator=True)
    g["observada"] = g.pop("_merge").eq("both")
    g["estado"] = np.where(g["observada"], "observada", "ausente")
    if g["observada"].sum() != len(validas):
        raise ValueError("Hay lecturas válidas que no encontraron su lugar en el calendario.")
    coincidencias, cuentas = _matches_historial(g, ctx["historial"])
    if not cuentas.eq(1).all():
        raise ValueError(f"Historial: {(cuentas == 0).sum()} horas sin vigencia y {(cuentas > 1).sum()} con solapes.")
    g["conexiones"] = coincidencias.set_index("_fila")["conexiones"].reindex(g.index)
    g = incorporar_exposiciones(g)
    metas = metas_largas(ctx)[["sector_id", "mes", "meta_pct"]]
    g = g.merge(metas, on=["sector_id", "mes"], how="left", validate="many_to_one")
    if g["meta_pct"].isna().any():
        raise ValueError("Hay horas del calendario sin meta docente.")
    return g


def resumir_cobertura(grilla, por):
    t = grilla.groupby(por, observed=True, sort=True).agg(
        horas_esperadas=("observada", "size"), horas_observadas=("observada", "sum"),
    ).reset_index()
    t["horas_ausentes"] = t["horas_esperadas"] - t["horas_observadas"]
    t["cobertura_pct"] = 100.0 * t["horas_observadas"] / t["horas_esperadas"]
    return t


def resumir_continuidad(grilla, por):
    grupos = grilla.groupby(por, observed=True, sort=True)
    if grupos["meta_pct"].nunique().ne(1).any():
        raise ValueError("Hay metas diferentes en un mismo agregado; se requiere revisar el criterio de comparación.")
    t = grupos.agg(
        horas_esperadas=("observada", "size"), horas_observadas=("observada", "sum"),
        horas_interrupcion_conocida=("interrupcion_conocida", "sum"),
        lecturas_sin_interrupcion_valida=("lectura_sin_interrupcion_valida", "sum"),
        minutos_conexion_esperados=("E", "sum"), minutos_conexion_observados=("O", "sum"),
        minutos_conexion_interrumpidos=("I", "sum"), minutos_conexion_desconocidos=("U", "sum"),
        meta_pct=("meta_pct", "first"),
    ).reset_index()
    t["horas_ausentes"] = t["horas_esperadas"] - t["horas_observadas"]
    t["horas_desconocidas"] = t["horas_esperadas"] - t["horas_interrupcion_conocida"]
    t["cobertura_pct"] = 100.0 * t["horas_observadas"] / t["horas_esperadas"]
    e, o, i, u = (t["minutos_conexion_" + c] for c in ["esperados", "observados", "interrumpidos", "desconocidos"])
    t["continuidad_obs_pct"] = 100 * (1 - i / o.where(o.gt(0)))
    t["continuidad_min_pct"] = 100 * (1 - (i + u) / e)
    t["continuidad_max_pct"] = 100 * (1 - i / e)
    t["estado_meta"] = np.select(
        [t["continuidad_max_pct"] < t["meta_pct"], t["continuidad_min_pct"] >= t["meta_pct"]],
        ["bajo la meta", "cumplimiento asegurado"], default="incierto",
    )
    return t


def auditar_uniones(df, ctx, grilla):
    """Cuenta matches por fila original, sin ocultar duplicación de dimensiones."""
    filas = []

    def registrar(nombre, cuentas, universo, no_evaluables=0, fuera_alcance=0):
        filas.append(dict(union=nombre, universo=universo, hechos_evaluados=len(cuentas),
                          coincidencias_0=int(cuentas.eq(0).sum()), coincidencias_1=int(cuentas.eq(1).sum()),
                          coincidencias_multiples=int(cuentas.gt(1).sum()),
                          no_evaluables=int(no_evaluables), fuera_alcance=int(fuera_alcance)))

    frec = ctx["sectores"].groupby("sector_id").size()
    registrar("lectura_catalogo", df["sector_id"].map(frec).fillna(0), len(df))
    fechadas = df[df["fecha"].notna()]
    _, cuentas = _matches_historial(fechadas, ctx["historial"])
    registrar("lectura_historial", cuentas, len(df), no_evaluables=df["fecha"].isna().sum())
    _, cuentas = _matches_historial(grilla, ctx["historial"])
    registrar("grilla_historial", cuentas, len(grilla))
    ini, fin = pd.Timestamp("2025-08-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
    en = df["fecha"].ge(ini) & df["fecha"].lt(fin)
    keys = df.loc[en, ["sector_id", "fecha"]].assign(mes=df.loc[en, "fecha"].dt.strftime("%Y-%m"))
    tarifas = ctx["tarifas"].groupby(["sector_id", "mes"]).size().rename("n").reset_index()
    cuentas = keys.merge(tarifas, on=["sector_id", "mes"], how="left", validate="many_to_one")["n"].fillna(0)
    registrar("lectura_tarifas_ago_dic", cuentas, len(df), no_evaluables=df["fecha"].isna().sum(),
              fuera_alcance=(df["fecha"].notna() & ~en).sum())
    metas = metas_largas(ctx)
    frecuencias = metas.groupby(["sector_id", "mes"]).size().rename("n").reset_index()
    cuentas = grilla[["sector_id", "mes"]].merge(frecuencias, on=["sector_id", "mes"], how="left", validate="many_to_one")["n"].fillna(0)
    registrar("grilla_metas_anuales", cuentas, len(grilla))
    return pd.DataFrame(filas)


def comparar_metas(ctx):
    claves = ["sector_id", "indicador", "mes"]
    a, b = metas_largas(ctx, "metas_ancho"), metas_largas(ctx)
    t = a.merge(b, on=claves, how="outer", suffixes=("_original", "_anual"),
                validate="one_to_one", indicator=True)
    t = t[t["mes"].le("2025-07")].copy()
    t["coincide"] = (t["_merge"].eq("both") & t["meta_pct_original"].eq(t["meta_pct_anual"])
                     & t["unidad_original"].eq(t["unidad_anual"]) & t["sentido_original"].eq(t["sentido_anual"]))
    return t.drop(columns="_merge")


def generar_tablas(df, ctx, ev, grilla):
    """Productos T3: CSV requeridos y evidencia auxiliar de denominadores."""
    tablas = {}
    for nombre, por in {
        "cobertura_sector_semana": ["sector_id", "semana_inicio"],
        "cobertura_sector_mes": ["sector_id", "mes"],
        "cobertura_sector_hora": ["sector_id", "hora_utc"],
    }.items():
        tablas[nombre] = resumir_cobertura(grilla, por)
    semanal = resumir_continuidad(grilla, ["sector_id", "semana_inicio"])
    tablas["continuidad_sector_semana"] = semanal
    ranking = grilla[grilla["lote"].eq("ampliacion")]
    resumen = resumir_continuidad(ranking, ["sector_id"])
    tablas["por_sector"] = resumen[CONTRATO].copy()
    tablas["continuidad_sector_ago_dic"] = resumen
    diario = resumir_continuidad(ranking, ["sector_id", "dia"])
    parejas = ranking.groupby(["sector_id", "dia"], observed=True).agg(
        horas_pareadas=("par_valido", "sum"), presion_mediana_bar=("presion_pareada", "median"),
        interrupcion_media_min_h=("minutos_pareados", "mean"),
    ).reset_index()
    conocido = ranking.groupby(["sector_id", "dia"], observed=True).agg(
        interrupcion_media_conocida_min_h=("minutos_interrupcion", lambda s: s[s.between(0, 60)].mean()),
    ).reset_index()
    tablas["resumen_sector_dia"] = diario.merge(parejas, on=["sector_id", "dia"], validate="one_to_one").merge(
        conocido, on=["sector_id", "dia"], validate="one_to_one")
    por_lote = resumir_cobertura(grilla, ["lote"])
    por_lote["filas_recibidas"] = por_lote["lote"].map(df.groupby("lote").size())
    reglas = {"copias_exactas": "RQ-UNI-01", "sector_horas_repetidas": "RQ-UNI-03",
              "fechas_imposibles": "RQ-VAL-01", "fechas_fuera_periodo": "RQ-VAL-03",
              "sectores_desconocidos": "RQ-VAL-10"}
    for col, regla in reglas.items():
        por_lote[col] = por_lote["lote"].map(ev[regla][0].groupby(df["lote"]).sum())
    conocidas = grilla.groupby("lote")["lectura_sin_interrupcion_valida"].sum()
    por_lote["lecturas_sin_interrupcion_valida"] = por_lote["lote"].map(conocidas)
    # Las máscaras de problemas pueden solaparse; no se suman como exclusiones disjuntas.
    por_lote["filas_no_utilizadas"] = por_lote["filas_recibidas"] - por_lote["horas_observadas"]
    por_lote["diferencia_recepcion_calendario"] = por_lote["horas_esperadas"] - por_lote["filas_recibidas"]
    tablas["comparacion_lotes"] = por_lote
    tablas["uniones"] = auditar_uniones(df, ctx, grilla)
    tablas["comparacion_metas"] = comparar_metas(ctx)
    return tablas


def validar_resultados(df, ctx, ev, grilla, tablas):
    """Comprueba invariantes y cifras de este paquete docente, sin escribir."""
    comun.verificar_hashes()
    assert len(grilla) == 262800 and not grilla.duplicated(CLAVE).any()
    esperado = {"base": (130320, 129929), "actualizacion": (22320, 22253), "ampliacion": (110160, 99500)}
    t2 = rq.cobertura(df, ev, ctx).set_index("lote")
    for _, r in tablas["comparacion_lotes"].iterrows():
        assert (r.horas_esperadas, r.horas_observadas) == esperado[r.lote]
        assert r.horas_observadas == t2.loc[r.lote, "sector_horas_con_lectura_valida"]
    assert int(grilla["lectura_sin_interrupcion_valida"].sum()) == 350
    assert len(tablas["por_sector"]) == 30 and tablas["por_sector"]["sector_id"].is_unique
    assert list(tablas["por_sector"].columns) == CONTRATO
    for t in tablas.values():
        if "cobertura_pct" in t:
            assert t["cobertura_pct"].between(0, 100).all()
            assert (t["horas_observadas"] <= t["horas_esperadas"]).all()
        if "horas_ausentes" in t:
            assert t["horas_observadas"].add(t["horas_ausentes"]).eq(t["horas_esperadas"]).all()
        if "continuidad_min_pct" in t:
            lo, ob, hi = (t[c] for c in ["continuidad_min_pct", "continuidad_obs_pct", "continuidad_max_pct"])
            assert lo.ge(-1e-9).all() and hi.le(100 + 1e-9).all()
            assert lo.le(hi + 1e-9).all()
            known = ob.notna()
            assert (lo[known] <= ob[known] + 1e-9).all() and (ob[known] <= hi[known] + 1e-9).all()
            if "minutos_conexion_esperados" in t:
                assert np.allclose(t["minutos_conexion_esperados"], t["minutos_conexion_observados"] + t["minutos_conexion_desconocidos"])
    for _, r in tablas["uniones"].iterrows():
        assert r.hechos_evaluados == r.coincidencias_0 + r.coincidencias_1 + r.coincidencias_multiples
        assert r.universo == r.hechos_evaluados + r.no_evaluables + r.fuera_alcance
    assert tablas["comparacion_metas"]["coincide"].all()
    assert grilla["meta_pct"].eq(99.5).all()
    horas = tablas["cobertura_sector_hora"].groupby("sector_id")["horas_esperadas"].sum()
    assert horas.eq(8760).all()
    semanas = tablas["cobertura_sector_semana"]
    assert semanas["semana_inicio"].dt.dayofweek.eq(0).all()
    assert semanas.groupby("sector_id")["horas_esperadas"].sum().eq(8760).all()
    hist = ctx["historial"]
    for fecha in ["2025-09-30T23:00:00Z", "2025-10-01T00:00:00Z"]:
        ts = pd.Timestamp(fecha)
        vigentes = hist[hist["vigente_desde"].le(ts) & hist["vigente_hasta"].gt(ts)].set_index("sector_id")
        real = grilla[grilla["fecha"].eq(ts)].set_index("sector_id")
        assert real.index.sort_values().tolist() == vigentes.index.sort_values().tolist()
        np.testing.assert_allclose(real["conexiones"].sort_index().to_numpy(dtype=float),
                                   vigentes["conexiones"].sort_index().to_numpy(dtype=float))
    return "OK: hashes, grilla, T2, exposiciones, semanas, vigencias y contrato del ranking."


def probar_casos():
    """Ejemplos independientes, con resultados calculables manualmente."""
    def ejemplo(minutos, observadas, pesos):
        n = len(minutos)
        g = pd.DataFrame(dict(sector_id=["prueba"] * n,
                             fecha=pd.date_range("2025-09-30T23:00:00Z", periods=n, freq="h"),
                             minutos_interrupcion=minutos, observada=observadas,
                             conexiones=pesos, presion_bar=[3.0] * n, meta_pct=[99.5] * n))
        return resumir_continuidad(incorporar_exposiciones(g), ["sector_id"]).iloc[0]
    cols = ["continuidad_obs_pct", "continuidad_min_pct", "continuidad_max_pct"]
    a = ejemplo([0, 30], [True, True], [100, 100])
    np.testing.assert_allclose(a[cols].astype(float), [75, 75, 75])
    b = ejemplo([0] * 80 + [np.nan] * 20, [True] * 80 + [False] * 20, [100] * 100)
    np.testing.assert_allclose(b[cols].astype(float), [100, 80, 100])
    c = ejemplo([np.nan, np.nan], [False, False], [100, 200])
    assert pd.isna(c.continuidad_obs_pct)
    np.testing.assert_allclose(c[[cols[1], cols[2]]].astype(float), [0, 100])
    d = ejemplo([60, 0], [True, True], [100, 200])
    np.testing.assert_allclose(d[cols].astype(float), [200 / 3] * 3)
    e = ejemplo([0, 90], [True, True], [100, 100])
    assert e.horas_observadas == 2 and e.horas_interrupcion_conocida == 1
    np.testing.assert_allclose(e[cols].astype(float), [100, 50, 100])
    return "OK: completo, parcial, sin observaciones, pesos cambiantes e interrupción inválida."


def probar_copia_adicional(df, ctx, ev, grilla):
    """Una copia exacta adicional debe producir exactamente la misma grilla."""
    indice = rq.lecturas_validas(df, ev)[lambda s: s].index[0]
    duplicado = pd.concat([df, df.loc[[indice]]], ignore_index=True)
    ev2 = rq.evaluar_reglas(duplicado, ctx)
    g2 = construir_grilla(duplicado, ctx, ev2)
    pd.testing.assert_frame_equal(grilla, g2)
    return "OK: una copia adicional no cambia cobertura, pesos ni continuidad."


def _numero(n, decimales=0):
    return f"{n:,.{decimales}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def estadisticas_figuras(tablas):
    diario = tablas["resumen_sector_dia"]
    s = tablas["continuidad_sector_ago_dic"]
    lot = tablas["comparacion_lotes"].set_index("lote").loc["ampliacion"]
    pares = diario[diario["horas_pareadas"].gt(0)]
    return dict(horas_esperadas=int(lot.horas_esperadas), horas_observadas=int(lot.horas_observadas),
                horas_ausentes=int(lot.horas_ausentes), cobertura_pct=float(lot.cobertura_pct),
                dias_sector=len(diario), dias_sin_lectura=int(diario.horas_observadas.eq(0).sum()),
                dias_parciales=int((diario.cobertura_pct.gt(0) & diario.cobertura_pct.lt(100)).sum()),
                sectores_inciertos=int(s.estado_meta.eq("incierto").sum()),
                sectores_bajo_meta=int(s.estado_meta.eq("bajo la meta").sum()),
                sectores_cumplimiento=int(s.estado_meta.eq("cumplimiento asegurado").sum()),
                sectores=len(s), dias_pareados=len(pares), horas_pareadas=int(pares.horas_pareadas.sum()),
                horas_excluidas_pares=int(lot.horas_esperadas - pares.horas_pareadas.sum()),
                correlacion_diaria=float(pares.presion_mediana_bar.corr(pares.interrupcion_media_min_h)),
                correlacion_presion_cobertura=float(pares.presion_mediana_bar.corr(pares.cobertura_pct)))


def generar_figuras(tablas):
    """Devuelve tres figuras sin guardarlas. Usar exportar para escribir PNG."""
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap, Normalize
    s = estadisticas_figuras(tablas)
    diario = tablas["resumen_sector_dia"]
    pal = comun.PALETA
    cmap = LinearSegmentedColormap.from_list("t3_acento", ["#F7FAFC", pal["acento"]])
    cmap.set_bad(pal["ausente"])
    nota = comun.NOTA_FUENTE + " · Corte ampliación: 2026-01-08 UTC"
    figuras = {}
    fig, axes = plt.subplots(2, 1, figsize=(17, 11), sharex=True, sharey=True)
    campos = [("cobertura_pct", "Cobertura de lecturas (%)", 100),
              ("interrupcion_media_conocida_min_h", "Interrupción media conocida (min/h)", None)]
    for ax, (campo, titulo, maximo) in zip(axes, campos):
        matriz = diario.pivot(index="sector_id", columns="dia", values=campo).sort_index()
        if campo == "cobertura_pct":
            matriz = matriz.mask(matriz.eq(0))  # 0% recepción se muestra como ausencia, no 0 min.
        im = ax.imshow(np.ma.masked_invalid(matriz.to_numpy(dtype=float)), aspect="auto", interpolation="nearest",
                       cmap=cmap, vmin=0, vmax=maximo)
        ax.set_yticks(range(len(matriz)), matriz.index, fontsize=8)
        ax.set_ylabel("Sector")
        ax.set_title(titulo, loc="left", fontsize=11)
        desconocidas = "horas_ausentes" if campo == "cobertura_pct" else "horas_desconocidas"
        parcial = diario.pivot(index="sector_id", columns="dia", values=desconocidas).reindex(index=matriz.index, columns=matriz.columns)
        ys, xs = np.where(parcial.gt(0).to_numpy() & matriz.notna().to_numpy())
        ax.scatter(xs, ys, marker=".", s=3, c=pal["alerta"], alpha=.65)
        fig.colorbar(im, ax=ax, fraction=.018, pad=.01)
    ticks = [j for j, d in enumerate(matriz.columns) if d.day in (1, 15)]
    axes[-1].set_xticks(ticks, [matriz.columns[j].strftime("%d-%m") for j in ticks], rotation=45, ha="right")
    axes[-1].set_xlabel("Día de 2025 (UTC)")
    fig.suptitle(f"La ampliación tiene {_numero(s['horas_ausentes'])} de {_numero(s['horas_esperadas'])} sector-horas sin lectura válida", fontsize=15, y=.98)
    fig.text(.08, .93, f"Ago–dic 2025 UTC · {_numero(s['cobertura_pct'], 2)}% de cobertura · Gris: sin dato; rojo: faltan lecturas (arriba) o interrupciones válidas (abajo)", fontsize=10)
    fig.text(.08, .02, nota, fontsize=9)
    fig.subplots_adjust(top=.89, bottom=.11, hspace=.18)
    figuras["cobertura_interrupciones"] = fig

    t = tablas["continuidad_sector_ago_dic"].sort_values("continuidad_min_pct").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(12, 9))
    y = np.arange(len(t))
    ax.hlines(y, t.continuidad_min_pct, t.continuidad_max_pct, color=pal["neutro"], lw=3, label="Límites 60/0 min desconocidos")
    ax.scatter(t.continuidad_min_pct, y, color=pal["alerta"], s=15, label="Mínima")
    ax.scatter(t.continuidad_obs_pct, y, color=pal["acento"], s=24, label="Observada")
    ax.axvline(99.5, color="#323232", ls="--", lw=1, label="Meta docente 99,5%")
    ax.set_yticks(y, t.sector_id)
    ax.set_xlim(max(0, float(t.continuidad_min_pct.min()) - 2), 100.1)
    ax.set_xlabel("Continuidad ponderada por conexiones (%)")
    ax.set_ylabel("Sector")
    ax.set_title(f"Aun en el mejor caso, {s['sectores_bajo_meta']} de {s['sectores']} sectores quedan bajo 99,5%", loc="left", fontsize=14, pad=32)
    ax.text(0, 1.025, "Ago–dic 2025 UTC · 110.160 sector-horas esperadas · Observada solo con interrupción válida", transform=ax.transAxes, fontsize=10)
    ax.grid(axis="x", alpha=.2)
    ax.legend(loc="upper left", fontsize=9)
    fig.text(.10, .025, nota, fontsize=9)
    fig.subplots_adjust(left=.12, right=.97, top=.88, bottom=.10)
    figuras["continuidad_limites"] = fig

    pares = diario[diario.horas_pareadas.gt(0)]
    fig, ax = plt.subplots(figsize=(12, 7))
    im = ax.scatter(pares.presion_mediana_bar, pares.interrupcion_media_min_h,
                    c=pares.cobertura_pct, cmap=cmap, norm=Normalize(0, 100), s=16, alpha=.35)
    fig.colorbar(im, ax=ax, label="Cobertura diaria de lecturas (%)")
    ax.set_xlabel("Mediana de presión sobre horas pareadas (bar)")
    ax.set_ylabel("Interrupción media sobre las mismas horas (min/h)")
    ax.set_ylim(bottom=0)
    ax.set_title(f"Presión e interrupciones tienen asociación diaria r = {_numero(s['correlacion_diaria'], 3)}", loc="left", fontsize=14, pad=32)
    ax.text(0, 1.025, f"Ago–dic 2025 UTC · {_numero(s['dias_pareados'])} de {_numero(s['dias_sector'])} sector-días · {_numero(s['horas_pareadas'])} de {_numero(s['horas_esperadas'])} pares horarios", transform=ax.transAxes, fontsize=10)
    ax.grid(alpha=.15)
    fig.text(.10, .02, nota + " · Asociación descriptiva; no implica causalidad.", fontsize=9)
    fig.subplots_adjust(top=.84, bottom=.13)
    figuras["presion_interrupciones"] = fig
    return figuras


def exportar(tablas, figuras, destino=E1):
    """Único punto de escritura: sobrescribe únicamente salidas con prefijo T3_."""
    destino = Path(destino)
    carpeta_tablas, carpeta_figuras = destino / "salidas/tablas", destino / "salidas/figuras"
    carpeta_tablas.mkdir(parents=True, exist_ok=True)
    carpeta_figuras.mkdir(parents=True, exist_ok=True)
    rutas = []
    for nombre, tabla in tablas.items():
        ruta = carpeta_tablas / f"T3_{nombre}.csv"
        tabla.to_csv(ruta, index=False, encoding="utf-8", float_format="%.10f")
        rutas.append(ruta)
    for nombre, figura in figuras.items():
        ruta = carpeta_figuras / f"T3_{nombre}.png"
        figura.savefig(ruta, dpi=150, bbox_inches="tight")
        rutas.append(ruta)
    return rutas
