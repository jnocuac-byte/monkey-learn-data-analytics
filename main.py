"""Punto de entrada. Ejecutar con:  uv run python main.py

Opciones:
  --etapa N         ejecuta hasta la etapa N (1 sentimiento, 2 temas, 3 palabras clave, 4 reporte). Por defecto 4.
  --texto "..."     clasifica un solo texto (útil para la demo en vivo)
  --archivo ruta    analiza tu propio CSV (debe tener una columna 'texto')
  --abrir           abre el reporte HTML en el navegador al terminar
"""
import argparse
import csv
import json
import sys
import webbrowser

from mldemo.clasificador import entrenar, predecir
from mldemo.datos import SALIDA, cargar_entrenamiento, cargar_nuevos
from mldemo.palabras import palabras_clave
from mldemo.reporte import generar_html


def titulo(txt: str) -> None:
    print("\n" + "=" * 64 + f"\n{txt}\n" + "=" * 64)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="Demo estilo MonkeyLearn en español")
    ap.add_argument("--etapa", type=int, choices=[1, 2, 3, 4], default=4)
    ap.add_argument("--texto", help="clasifica un solo texto")
    ap.add_argument("--archivo", help="CSV propio con columna 'texto'")
    ap.add_argument("--abrir", action="store_true", help="abre el reporte en el navegador")
    a = ap.parse_args()

    # ---- Datos de entrenamiento ----
    entrena = cargar_entrenamiento()
    textos = [f["texto"] for f in entrena]

    titulo("ETAPA 1 · Clasificador de SENTIMIENTO")
    print("Qué hace: aprende de ejemplos etiquetados (positivo/neutro/negativo)")
    print("y luego clasifica comentarios nuevos. Es lo que MonkeyLearn llamaba")
    print("'Sentiment Analysis' o un 'Classifier' propio.")
    m_sent, acc_sent = entrenar(textos, [f["sentimiento"] for f in entrena])
    print(f"Entrenado con {len(entrena)} ejemplos. Exactitud (validación cruzada): {acc_sent:.0%}")

    # ---- Modo un solo texto ----
    if a.texto:
        r = predecir(m_sent, [a.texto])[0]
        m_tema, _ = entrenar(textos, [f["tema"] for f in entrena])
        t = predecir(m_tema, [a.texto])[0]
        print(f"\nTexto: {a.texto}")
        print(f"Sentimiento: {r[0]} ({r[1]:.0%})")
        print(f"Tema:        {t[0]} ({t[1]:.0%})")
        return

    nuevos = cargar_nuevos(a.archivo)
    ps = predecir(m_sent, nuevos)
    print("\nEjemplos de resultado:")
    for txt, (s, c) in list(zip(nuevos, ps))[:5]:
        print(f"  [{s:8}] {c:4.0%}  {txt}")
    if a.etapa == 1:
        return

    titulo("ETAPA 2 · Clasificador de TEMAS")
    print("Qué hace: el mismo método, pero con otra etiqueta (servicio, envío,")
    print("precio, producto). Es el 'Topic Classifier' de MonkeyLearn.")
    m_tema, acc_tema = entrenar(textos, [f["tema"] for f in entrena])
    pt = predecir(m_tema, nuevos)
    print(f"Exactitud (validación cruzada): {acc_tema:.0%}")
    print("\nEjemplos de resultado:")
    for txt, (t, c) in list(zip(nuevos, pt))[:5]:
        print(f"  [{t:8}] {c:4.0%}  {txt}")
    if a.etapa == 2:
        return

    titulo("ETAPA 3 · PALABRAS CLAVE")
    print("Qué hace: cuenta qué palabras importantes se repiten más.")
    print("Es la versión simple del 'Keyword Extractor' de MonkeyLearn.")
    resultados = [
        {"texto": t, "sentimiento": s, "conf_sent": cs, "tema": tm, "conf_tema": ct}
        for t, (s, cs), (tm, ct) in zip(nuevos, ps, pt)
    ]
    claves = {"general": palabras_clave(nuevos)}
    for s in ("positivo", "negativo", "neutro"):
        claves[s] = palabras_clave([r["texto"] for r in resultados if r["sentimiento"] == s], 6)
    for k, v in claves.items():
        print(f"  {k:9}: " + ", ".join(f"{p}({n})" for p, n in v))
    if a.etapa == 3:
        return

    titulo("ETAPA 4 · REPORTE")
    SALIDA.mkdir(exist_ok=True)
    ruta_html = SALIDA / "reporte.html"
    ruta_html.write_text(generar_html(resultados, acc_sent, acc_tema, len(entrena), claves), encoding="utf-8")
    with open(SALIDA / "resultados.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(resultados[0].keys()))
        w.writeheader()
        w.writerows(resultados)
    (SALIDA / "resultados.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Reporte listo:  {ruta_html}")
    print(f"Datos:          {SALIDA / 'resultados.csv'} y resultados.json")
    if a.abrir:
        webbrowser.open(ruta_html.as_uri())


if __name__ == "__main__":
    main()
