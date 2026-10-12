"""T5: revisa qué falta para entregar la E1, une fichas, corre el ranking y arma el entregable.

Uso (desde E1/, con el venv del caso):

    python T5_consolidar.py                  # revisar: estado ✅/🟡/❌ de insumos y productos (solo lectura)
    python T5_consolidar.py --unir-fichas    # T4_fichas_kpi.csv + T2_fichas_calidad.csv -> fichas_indicadores.csv
    python T5_consolidar.py --ranking        # T2/T3/T4_por_sector.csv -> T2_ranking.csv (con y sin filtro)
    python T5_consolidar.py --versiones      # versiones_probadas.txt (Python + pip freeze)
    python T5_consolidar.py --empaquetar     # carpeta entregable/ + .zip (solo si todo está ✅; --forzar para probar)
    python T5_consolidar.py --probar         # descomprime el .zip en una carpeta temporal y ejecuta el notebook ahí

--notebook X.ipynb cambia el notebook a revisar/empaquetar (por defecto E1_diagnostico.ipynb).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd

import comun
import T2_reglas as rq

E1 = Path(__file__).resolve().parent
RAIZ = comun.RAIZ
TABLAS = E1 / "salidas" / "tablas"
FIGURAS = E1 / "salidas" / "figuras"
SALIDA = E1 / "entregable"
NOMBRE = "Entrega_E1_AguasAndinas"
MAX_PAGINAS = 5
OK, PARCIAL, FALTA = "✅", "🟡", "❌"


def _columnas_plantilla(nombre):
    return pd.read_csv(RAIZ / nombre, nrows=0).columns.tolist()


def _paginas_pdf(ruta):
    """Cuenta páginas con PDFKit (macOS); si no está disponible, cuenta objetos /Type /Page."""
    try:
        js = (f"ObjC.import('PDFKit'); $.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath('{ruta}')).pageCount")
        r = subprocess.run(["osascript", "-l", "JavaScript", "-e", js], capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip().isdigit():
            return int(r.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return len(re.findall(rb"/Type\s*/Page(?!s)", ruta.read_bytes()))


def _estado_notebook(ruta):
    if not ruta.exists():
        return FALTA, "no existe"
    nb = json.loads(ruta.read_text(encoding="utf-8"))
    codigo = [c for c in nb["cells"] if c["cell_type"] == "code" and "".join(c["source"]).strip()]
    sin_ejecutar = sum(1 for c in codigo if not c.get("execution_count"))
    errores = sum(1 for c in codigo for o in c.get("outputs", []) if o.get("output_type") == "error")
    if errores:
        return FALTA, f"{errores} celda(s) con error"
    if sin_ejecutar:
        return PARCIAL, f"{sin_ejecutar} de {len(codigo)} celdas de código sin ejecutar"
    return OK, f"{len(codigo)} celdas ejecutadas, sin errores"


def _estado_tabla_sector(nombre, clave):
    ruta = TABLAS / nombre
    if not ruta.exists():
        return FALTA, "no existe (contrato en README: 'Contrato de tablas por sector')"
    t = pd.read_csv(ruta)
    faltan = sorted(set(rq.COLUMNAS_CONTRATO[clave]) - set(t.columns))
    if faltan:
        return FALTA, f"faltan columnas {faltan}"
    if len(t) != 30 or not t["sector_id"].is_unique:
        return FALTA, f"{len(t)} filas; se esperan 30 sectores únicos"
    return OK, "30 sectores, columnas del contrato"


def revisar(notebook):
    """Lista de (grupo, elemento, estado, detalle)."""
    filas = []

    def add(grupo, elemento, estado, detalle):
        filas.append((grupo, elemento, estado, detalle))

    try:
        comun.verificar_hashes()
        add("Datos", "Hashes de datos/ vs metadatos.json", OK, "8 archivos intactos")
    except AssertionError as e:
        add("Datos", "Hashes de datos/ vs metadatos.json", FALTA, str(e))

    for nombre, clave in [("T2_por_sector.csv", "t2"), ("T3_por_sector.csv", "t3"), ("T4_por_sector.csv", "t4")]:
        add("Insumos del ranking", nombre, *_estado_tabla_sector(nombre, clave))

    ruta = TABLAS / "diccionario_revisado.csv"
    add("Producto 3", "diccionario_revisado.csv", *((OK, f"{len(pd.read_csv(ruta))} campos") if ruta.exists() else (FALTA, "no existe")))
    ruta = TABLAS / "perfil_calidad.csv"
    add("Producto 3", "perfil_calidad.csv", *((OK, f"{len(pd.read_csv(ruta))} filas") if ruta.exists() else (FALTA, "no existe")))
    ruta = TABLAS / "matriz_reglas.csv"
    if ruta.exists():
        cols = pd.read_csv(ruta, nrows=0).columns.tolist()
        ok = cols[:len(rq.COLUMNAS_PLANTILLA)] == _columnas_plantilla("plantilla_reglas_calidad.csv")
        add("Producto 3", "matriz_reglas.csv", OK if ok else FALTA, "columnas de la plantilla" if ok else "columnas distintas a la plantilla")
    else:
        add("Producto 3", "matriz_reglas.csv", FALTA, "no existe")

    for nombre in ["T2_fichas_calidad.csv", "T4_fichas_kpi.csv"]:
        ruta = TABLAS / nombre
        add("Producto 4 (insumos)", nombre, *((OK, f"{len(pd.read_csv(ruta))} fichas") if ruta.exists() else (FALTA, "no existe")))
    ruta = TABLAS / "fichas_indicadores.csv"
    if ruta.exists():
        f = pd.read_csv(ruta)
        n_kpi, n_kri = int((f.tipo_KPI_KRI_visual == "KPI").sum()), int((f.tipo_KPI_KRI_visual == "KRI").sum())
        ok = list(f.columns) == _columnas_plantilla("plantilla_fichas_indicadores.csv") and n_kpi >= 6 and n_kri >= 6
        add("Producto 4", "fichas_indicadores.csv", OK if ok else PARCIAL, f"{n_kpi} KPI + {n_kri} KRI")
    else:
        add("Producto 4", "fichas_indicadores.csv", FALTA, "no existe; correr --unir-fichas")

    ruta = TABLAS / "T2_ranking.csv"
    add("Ranking (P4)", "T2_ranking.csv", *((OK, "generado") if ruta.exists() else (FALTA, "no existe; correr --ranking")))

    add("Producto 1", notebook, *_estado_notebook(E1 / notebook))

    ruta = E1 / "Diagnostico.pdf"
    if ruta.exists():
        p = _paginas_pdf(ruta)
        add("Producto 2", "Diagnostico.pdf", OK if p <= MAX_PAGINAS else FALTA, f"{p} páginas (máx. {MAX_PAGINAS})")
    else:
        add("Producto 2", "Diagnostico.pdf", FALTA, "no existe; exportar desde diagnostico.md")

    ruta = E1 / "uso_ia.md"
    filas_ia = sum(1 for l in ruta.read_text(encoding="utf-8").splitlines() if l.startswith("| 20")) if ruta.exists() else 0
    add("Declaraciones", "uso_ia.md", OK if filas_ia else FALTA, f"{filas_ia} registro(s)")
    ruta = E1 / "versiones_probadas.txt"
    add("Declaraciones", "versiones_probadas.txt", *((OK, "generado") if ruta.exists() else (FALTA, "correr --versiones")))
    return filas


def imprimir(filas):
    grupo_actual = None
    for grupo, elemento, estado, detalle in filas:
        if grupo != grupo_actual:
            print(f"\n{grupo}")
            grupo_actual = grupo
        print(f"  {estado} {elemento:<38} {detalle}")
    listos = sum(1 for f in filas if f[2] == OK)
    print(f"\n{listos} de {len(filas)} listos.")
    return listos == len(filas)


def unir_fichas():
    kpi, kri = TABLAS / "T4_fichas_kpi.csv", TABLAS / "T2_fichas_calidad.csv"
    faltan = [p.name for p in (kpi, kri) if not p.exists()]
    if faltan:
        sys.exit(f"No se pueden unir las fichas: falta {', '.join(faltan)}.")
    columnas = _columnas_plantilla("plantilla_fichas_indicadores.csv")
    a, b = pd.read_csv(kpi), pd.read_csv(kri)
    for nombre, t in [(kpi.name, a), (kri.name, b)]:
        if list(t.columns) != columnas:
            sys.exit(f"{nombre} no tiene las columnas de plantilla_fichas_indicadores.csv.")
    f = pd.concat([a, b], ignore_index=True)
    if not f["id"].is_unique:
        sys.exit(f"Hay ids repetidos: {f.loc[f['id'].duplicated(), 'id'].tolist()}")
    if (a.tipo_KPI_KRI_visual == "KPI").sum() < 6 or (b.tipo_KPI_KRI_visual == "KRI").sum() < 6:
        sys.exit("Se esperan al menos 6 KPI (T4) y 6 KRI (T2).")
    f.to_csv(TABLAS / "fichas_indicadores.csv", index=False)
    print(f"fichas_indicadores.csv: {len(f)} fichas ({len(a)} de T4 + {len(b)} de T2).")


def ranking():
    tablas = {k: TABLAS / f"{k.upper()}_por_sector.csv" for k in ("t2", "t3", "t4")}
    faltan = [p.name for p in tablas.values() if not p.exists()]
    if faltan:
        sys.exit(f"No se puede correr el ranking real: falta {', '.join(faltan)} (D-03: no se usan datos de prueba).")
    t2, t3, t4 = (pd.read_csv(p) for p in tablas.values())
    r = rq.comparar_rankings(t2, t3, t4)
    r.to_csv(TABLAS / "T2_ranking.csv", index=False)
    top = r[r.filtro_cobertura.eq("sin filtro")].head(3)
    print("T2_ranking.csv generado. Top 3 sin filtro:")
    print(top[["posicion", "sector_id", "puntaje", "tipo_inspeccion", "continuidad_vs_meta"]].to_string(index=False))


def versiones():
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True).stdout
    (E1 / "versiones_probadas.txt").write_text(f"Python {sys.version.split()[0]}\n\n{freeze}", encoding="utf-8")
    print(f"versiones_probadas.txt: Python {sys.version.split()[0]}, {len(freeze.splitlines())} paquetes.")


def _modulos_locales(notebook):
    """Módulos .py de E1/ que importa el notebook, y los que importan esos módulos."""
    nb = json.loads((E1 / notebook).read_text(encoding="utf-8"))
    fuente = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    pendientes, encontrados = [fuente], set()
    while pendientes:
        texto = pendientes.pop()
        for nombre in re.findall(r"^\s*(?:import|from)\s+(\w+)", texto, flags=re.M):
            ruta = E1 / f"{nombre}.py"
            if ruta.exists() and nombre not in encontrados:
                encontrados.add(nombre)
                pendientes.append(ruta.read_text(encoding="utf-8"))
    return sorted(encontrados)


LEEME = """# Entrega E1 · Diagnóstico y necesidades · Grupo Aguas Andinas

Integrantes: Byron, Bastian, Sepu, Jose · Visualización de Datos 2026 S2 · Prof. Viktor Tapia
Datos 100% simulados con fines docentes.

## Contenido
- `Diagnostico.pdf`: diagnóstico (máx. 5 páginas).
- `E1/{notebook}`: notebook ejecutado desde cero con los 3 lotes y las tablas complementarias.
- `E1/salidas/tablas/`: diccionario_revisado.csv, perfil_calidad.csv, matriz_reglas.csv, fichas_indicadores.csv y tablas de apoyo.
- `E1/salidas/figuras/`: figuras del notebook.
- `versiones_probadas.txt`: versiones de Python y paquetes con que se probó.

## Cómo ejecutar el notebook
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd E1 && jupyter lab {notebook}     # o: jupyter nbconvert --to notebook --execute {notebook}
```
El notebook verifica al inicio que los CSV de `datos/` no fueron modificados (SHA-256 vs `metadatos.json`).
"""


def empaquetar(notebook, forzar):
    if not forzar and not imprimir(revisar(notebook)):
        sys.exit("\nHay elementos sin ✅: no se empaqueta. Usa --forzar solo para probar el empaquetado.")
    if not (E1 / notebook).exists():
        sys.exit(f"No existe {notebook}.")
    destino = SALIDA / NOMBRE
    if destino.exists():
        shutil.rmtree(destino)
    (destino / "E1").mkdir(parents=True)
    for nombre in ["metadatos.json", "diccionario_datos.csv", "requirements.txt"] + [p.name for p in RAIZ.glob("plantilla_*.csv")]:
        shutil.copy2(RAIZ / nombre, destino / nombre)
    shutil.copytree(RAIZ / "datos", destino / "datos", ignore=shutil.ignore_patterns(".DS_Store"))
    for nombre in ["Diagnostico.pdf", "versiones_probadas.txt"]:
        if (E1 / nombre).exists():
            shutil.copy2(E1 / nombre, destino / nombre)
    shutil.copy2(E1 / notebook, destino / "E1" / notebook)
    modulos = _modulos_locales(notebook)
    for m in modulos:
        shutil.copy2(E1 / f"{m}.py", destino / "E1" / f"{m}.py")
    shutil.copytree(E1 / "salidas", destino / "E1" / "salidas", ignore=shutil.ignore_patterns(".gitkeep", ".DS_Store"))
    (destino / "LEEME.md").write_text(LEEME.format(notebook=notebook), encoding="utf-8")
    zip_path = shutil.make_archive(str(SALIDA / NOMBRE), "zip", root_dir=SALIDA, base_dir=NOMBRE)
    print(f"\nEntregable armado en {destino.relative_to(RAIZ.parent)} (módulos: {', '.join(modulos)})")
    print(f"Zip: {Path(zip_path).relative_to(RAIZ.parent)} ({Path(zip_path).stat().st_size / 1e6:.1f} MB)")


def probar(notebook):
    zip_path = SALIDA / f"{NOMBRE}.zip"
    if not zip_path.exists():
        sys.exit("No existe el .zip; correr --empaquetar primero.")
    tmp = Path(tempfile.mkdtemp(prefix="prueba_E1_"))
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(tmp)
    e1 = tmp / NOMBRE / "E1"
    subprocess.run([sys.executable, "-c", "import comun; comun.verificar_hashes()"], cwd=e1, check=True)
    r = subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", notebook,
                        "--output-dir", str(tmp / "ejecutado")], cwd=e1, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        sys.exit(f"❌ El notebook falló al ejecutarse desde el .zip (carpeta de prueba: {tmp}).")
    estado, detalle = _estado_notebook(tmp / "ejecutado" / notebook)
    print(f"{estado} El notebook corre desde el .zip descomprimido en una carpeta nueva: {detalle}.")
    shutil.rmtree(tmp)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--notebook", default="E1_diagnostico.ipynb")
    p.add_argument("--unir-fichas", action="store_true")
    p.add_argument("--ranking", action="store_true")
    p.add_argument("--versiones", action="store_true")
    p.add_argument("--empaquetar", action="store_true")
    p.add_argument("--forzar", action="store_true", help="empaquetar aunque falten elementos (solo para pruebas)")
    p.add_argument("--probar", action="store_true")
    a = p.parse_args()
    if a.unir_fichas:
        unir_fichas()
    if a.ranking:
        ranking()
    if a.versiones:
        versiones()
    if a.empaquetar:
        empaquetar(a.notebook, a.forzar)
    if a.probar:
        probar(a.notebook)
    if not any([a.unir_fichas, a.ranking, a.versiones, a.empaquetar, a.probar]):
        imprimir(revisar(a.notebook))


if __name__ == "__main__":
    main()
