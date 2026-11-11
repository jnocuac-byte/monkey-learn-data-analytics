"""Carga de datos (CSV con codificación UTF-8)."""
import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"
SALIDA = RAIZ / "output"


def _leer(ruta: Path) -> list[dict]:
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def cargar_entrenamiento() -> list[dict]:
    """Comentarios ya etiquetados (texto, sentimiento, tema).

    Lee todos los archivos data/entrenamiento*.csv: para dar más ejemplos
    al modelo, agrega filas a uno de ellos o crea otro archivo con ese nombre.
    """
    filas: list[dict] = []
    for ruta in sorted(DATOS.glob("entrenamiento*.csv")):
        filas.extend(_leer(ruta))
    return filas


def agregar_ejemplo(texto: str, sentimiento: str, tema: str) -> None:
    """Guarda un ejemplo corregido por el usuario en data/entrenamiento_usuario.csv."""
    ruta = DATOS / "entrenamiento_usuario.csv"
    nuevo = not ruta.exists()
    with open(ruta, "a", newline="", encoding="utf-8-sig" if nuevo else "utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["texto", "sentimiento", "tema"])
        w.writerow([texto, sentimiento, tema])


def cargar_nuevos(ruta: str | None = None) -> list[str]:
    """Comentarios sin etiquetar. El CSV debe tener una columna 'texto'."""
    archivo = Path(ruta) if ruta else DATOS / "comentarios_nuevos.csv"
    filas = _leer(archivo)
    if filas and "texto" not in filas[0]:
        raise SystemExit(f"El archivo {archivo} debe tener una columna llamada 'texto'.")
    return [f["texto"].strip() for f in filas if f["texto"].strip()]
