"""Carga compartida para los notebooks de la E1.

Uso desde un notebook ubicado en E1/:

    import comun
    comun.verificar_hashes()
    crudo = comun.cargar_lotes()                 # strings, tal como vienen
    df = comun.parse_exploratorio(crudo)         # tipado mínimo para explorar
    sectores = comun.cargar_tabla("dimensiones/sectores.csv")

parse_exploratorio es solo para el EDA de la E1: no elimina, no deduplica y no
imputa nada. La limpieza oficial y su bitácora corresponden a la E2.
"""
from pathlib import Path
import hashlib
import json

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]  # 04_Aguas_Andinas_alumnos/
DATOS = RAIZ / "datos"
META = json.loads((RAIZ / "metadatos.json").read_text(encoding="utf-8"))
LOTES = ["base", "actualizacion", "ampliacion"]

COLS_NUMERICAS = ["volumen_entrada", "volumen_salida", "presion_bar", "energia_kwh", "minutos_interrupcion"]
COLS_FECHA = ["fecha", "cargado_en"]
FORMATO_ISO = "%Y-%m-%dT%H:%M:%SZ"
FORMATO_ALT = "%d/%m/%Y %H:%M:%S"  # aparece en ampliación; se interpreta como UTC

# Paleta común del equipo (ver skill grafico-diagnostico)
PALETA = {
    "neutro": "#9AA0A6",   # todo lo que no se destaca
    "acento": "#1F6FB2",   # lo que el título afirma
    "alerta": "#C8553D",   # problema de calidad o fuera de meta
    "ausente": "#E6E6E6",  # horas sin lectura (nunca 0)
    "base": "#4C78A8",
    "actualizacion": "#72B7B2",
    "ampliacion": "#F58518",
}
NOTA_FUENTE = "Datos simulados docentes · Caso Aguas Andinas v2 · Fechas UTC"


def verificar_hashes():
    """Falla si algún archivo de datos/ difiere de metadatos.json (no deben editarse)."""
    for f in META["files"]:
        contenido = (RAIZ / f["archivo"]).read_bytes()
        # Git puede materializar LF como CRLF en Windows (core.autocrlf).
        # Comparar el contenido canónico LF declarado por metadatos.json sin
        # cambiar el archivo del usuario ni ocultar diferencias de contenido.
        contenido = contenido.replace(b"\r\n", b"\n")
        real = hashlib.sha256(contenido).hexdigest()
        assert real == f["sha256"], f"{f['archivo']} fue modificado"


def cargar_lotes(concatenar=True):
    """Lee los 3 lotes de telemetría como strings y agrega la columna `lote`."""
    lotes = {
        lote: pd.read_csv(DATOS / lote / f"{META['main']}.csv", dtype="string").assign(lote=lote)
        for lote in LOTES
    }
    return pd.concat(lotes.values(), ignore_index=True) if concatenar else lotes


def cargar_tabla(ruta_relativa):
    """Lee una tabla de datos/ (dimensiones o complementarios) como strings."""
    return pd.read_csv(DATOS / ruta_relativa, dtype="string")


def _a_numero(s):
    return pd.to_numeric(s.str.replace(",", ".", regex=False), errors="coerce")


def _a_fecha_utc(s):
    alt = s.str.match(r"^\d{2}/\d{2}/\d{4} ", na=False)
    iso = pd.to_datetime(s.where(~alt), format=FORMATO_ISO, utc=True, errors="coerce")
    otra = pd.to_datetime(s.where(alt), format=FORMATO_ALT, utc=True, errors="coerce")
    return iso.fillna(otra), alt


def parse_exploratorio(crudo):
    """Copia tipada de la telemetría con flags de los formatos excepcionales.

    - Numéricos: coma decimal -> punto (no hay separador de miles); texto -> NA.
    - fecha y cargado_en: ISO 8601 o dd/mm/YYYY HH:MM:SS, ambos UTC; fechas
      imposibles (p. ej. 30 de febrero) -> NaT.
    - volumen_*_m3: litros divididos por 1000; m3 sin cambio; otra unidad -> NA.
    - modo_operacion: strip + minúsculas.
    - Flags: _decimal_coma, _fecha_formato_alt, _cargado_en_formato_alt,
      _fecha_invalida, _numero_no_parseable, _unidad_L, _unidad_desconocida,
      _dup_medicion_id (todas las filas cuya clave se repite).
    Las columnas originales se conservan con sufijo _raw para poder contrastar.
    """
    df = crudo.copy()
    df["_decimal_coma"] = df[COLS_NUMERICAS].apply(lambda c: c.str.contains(",", regex=False, na=False)).any(axis=1)
    for col in COLS_NUMERICAS:
        df[f"{col}_raw"] = df[col]
        df[col] = _a_numero(df[col])
    for col in COLS_FECHA:
        df[f"{col}_raw"] = df[col]
        df[col], df[f"_{col}_formato_alt"] = _a_fecha_utc(df[col])

    df["_fecha_invalida"] = df["fecha"].isna() & df["fecha_raw"].notna()
    df["_numero_no_parseable"] = pd.concat(
        [df[c].isna() & df[f"{c}_raw"].notna() for c in COLS_NUMERICAS], axis=1
    ).any(axis=1)

    unidad = df["unidad_volumen"].str.strip()
    df["_unidad_L"] = unidad.eq("L").fillna(False)
    df["_unidad_desconocida"] = ~unidad.isin(["m3", "L"]).fillna(False)
    factor = unidad.map({"m3": 1.0, "L": 1 / 1000}).astype("Float64")  # otra unidad -> NA
    df["volumen_entrada_m3"] = df["volumen_entrada"] * factor
    df["volumen_salida_m3"] = df["volumen_salida"] * factor

    df["modo_operacion_raw"] = df["modo_operacion"]
    df["modo_operacion"] = df["modo_operacion"].str.strip().str.lower()
    df["_dup_medicion_id"] = df["medicion_id"].duplicated(keep=False)
    return df
