"""Etapa 4: reporte HTML autocontenido (sin internet, listo para proyectar)."""
from collections import Counter
from html import escape

COLORES = {"positivo": "#16a34a", "negativo": "#dc2626", "neutro": "#64748b"}
SENTIMIENTOS = ["positivo", "neutro", "negativo"]

CSS = """
:root{--bg:#f8fafc;--card:#fff;--txt:#0f172a;--sub:#64748b;--line:#e2e8f0;--acc:#4f46e5}
*{box-sizing:border-box}body{margin:0;font-family:Segoe UI,system-ui,Arial,sans-serif;background:var(--bg);color:var(--txt);line-height:1.5}
header{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:36px 24px}
header h1{margin:0 0 6px;font-size:28px}header p{margin:0;opacity:.9}
main{max-width:1050px;margin:0 auto;padding:24px}
section{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin-bottom:20px}
h2{margin:0 0 4px;font-size:20px}.etapa{color:var(--acc);font-weight:700;font-size:12px;letter-spacing:.08em;text-transform:uppercase}
.sub{color:var(--sub);margin:0 0 16px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.kpi{border:1px solid var(--line);border-radius:12px;padding:14px}.kpi b{display:block;font-size:28px}.kpi span{color:var(--sub);font-size:13px}
.fila{display:flex;gap:28px;align-items:center;flex-wrap:wrap}
.donut{width:170px;height:170px;border-radius:50%;position:relative;flex:none}
.donut::after{content:"";position:absolute;inset:34px;background:#fff;border-radius:50%}
.leyenda div{margin:6px 0}.dot{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:8px}
.barra{display:flex;align-items:center;gap:10px;margin:8px 0}.barra .n{width:90px;font-weight:600;text-transform:capitalize}
.barra .t{flex:1;background:#eef2ff;border-radius:6px;height:22px;overflow:hidden}.barra .t i{display:block;height:100%;background:var(--acc)}
.barra .v{width:36px;text-align:right;color:var(--sub)}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left}
th{color:var(--sub);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em}
td.c{text-align:center}.tag{padding:2px 9px;border-radius:99px;color:#fff;font-size:12px;font-weight:600}
.chips span{display:inline-block;background:#eef2ff;color:#3730a3;border-radius:99px;padding:3px 11px;margin:3px 4px 3px 0;font-size:13px}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.graficas{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
.grafica{border:1px solid var(--line);border-radius:12px;padding:12px;min-width:0}
.grafica h3{margin:0 0 8px;font-size:15px}.grafica svg{display:block;width:100%;height:auto}
footer{text-align:center;color:var(--sub);font-size:12px;padding:10px 0 30px}
@media print{header{background:#4f46e5!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}section{break-inside:avoid}}
"""

MAPA = [
    ("Sentiment Analysis (sentimiento)", "Etapa 1: clasificador de sentimiento entrenado con ejemplos"),
    ("Topic Classifier (clasificar por tema)", "Etapa 2: clasificador de temas entrenado con ejemplos"),
    ("Keyword Extractor (palabras clave)", "Etapa 3: conteo de palabras relevantes por sentimiento"),
    ("Entrenar modelos propios con clics (No-Code)", "Aquí: se edita un CSV con ejemplos y se vuelve a ejecutar"),
    ("Dashboards y gráficas", "Etapa 4: este reporte HTML"),
    ("API para conectar con otras apps", "Aquí: las funciones de la carpeta mldemo/ se importan desde cualquier script"),
]


def _donut(conteo: Counter, total: int) -> str:
    partes, ini = [], 0.0
    for s in SENTIMIENTOS:
        pct = 100 * conteo.get(s, 0) / total if total else 0
        partes.append(f"{COLORES[s]} {ini:.2f}% {ini + pct:.2f}%")
        ini += pct
    leyenda = "".join(
        f'<div><span class="dot" style="background:{COLORES[s]}"></span>'
        f'<b>{s.capitalize()}</b>: {conteo.get(s, 0)} ({100 * conteo.get(s, 0) / total:.0f}%)</div>'
        for s in SENTIMIENTOS
    )
    return (
        f'<div class="fila"><div class="donut" style="background:conic-gradient({", ".join(partes)})"></div>'
        f'<div class="leyenda">{leyenda}</div></div>'
    )


def _barras(conteo: Counter) -> str:
    mx = max(conteo.values()) if conteo else 1
    return "".join(
        f'<div class="barra"><span class="n">{escape(k)}</span>'
        f'<span class="t"><i style="width:{100 * v / mx:.0f}%"></i></span><span class="v">{v}</span></div>'
        for k, v in conteo.most_common()
    )


def _cruce(resultados: list[dict], temas: list[str]) -> str:
    cab = "".join(f"<th>{s.capitalize()}</th>" for s in SENTIMIENTOS)
    filas = ""
    for t in temas:
        celdas = ""
        for s in SENTIMIENTOS:
            n = sum(1 for r in resultados if r["tema"] == t and r["sentimiento"] == s)
            alfa = min(0.12 + 0.22 * n, 0.9) if n else 0
            fondo = f"background:{COLORES[s]}{int(alfa * 255):02x}" if n else ""
            celdas += f'<td class="c" style="{fondo}">{n}</td>'
        filas += f"<tr><td><b>{escape(t.capitalize())}</b></td>{celdas}</tr>"
    return f"<table><tr><th>Tema</th>{cab}</tr>{filas}</table>"


def _chips(pares: list[tuple[str, int]]) -> str:
    if not pares:
        return '<span class="sub">Sin datos</span>'
    return "".join(f"<span>{escape(p)} · {n}</span>" for p, n in pares)


def _svg_confianza(resultados: list[dict]) -> str:
    ancho, alto, izq, arriba, abajo = 560, 220, 48, 18, 34
    ancho_g, alto_g = ancho - izq - 12, alto - arriba - abajo
    puntos_sent = []
    puntos_tema = []
    for i, r in enumerate(resultados):
        x = izq + (ancho_g * i / max(1, len(resultados) - 1))
        puntos_sent.append(f"{x:.1f},{arriba + alto_g * (1 - r['conf_sent']):.1f}")
        puntos_tema.append(f"{x:.1f},{arriba + alto_g * (1 - r['conf_tema']):.1f}")
    lineas = "".join(
        f'<line x1="{izq}" y1="{arriba + alto_g * (1 - p):.1f}" x2="{ancho - 12}" '
        f'y2="{arriba + alto_g * (1 - p):.1f}" stroke="#e2e8f0"/><text x="4" '
        f'y="{arriba + alto_g * (1 - p) + 4:.1f}" font-size="11" fill="#64748b">{int(p * 100)}%</text>'
        for p in (0, .5, 1)
    )
    return (
        f'<svg viewBox="0 0 {ancho} {alto}" role="img" aria-label="Confianza por comentario">'
        f'{lineas}<polyline points="{" ".join(puntos_sent)}" fill="none" stroke="{COLORES["positivo"]}" stroke-width="3"/>'
        f'<polyline points="{" ".join(puntos_tema)}" fill="none" stroke="{COLORES["acc"] if "acc" in COLORES else "#4f46e5"}" stroke-width="3"/>'
        f'<text x="{izq}" y="{alto - 8}" font-size="11" fill="#64748b">Comentario</text>'
        f'<circle cx="{ancho - 150}" cy="14" r="4" fill="{COLORES["positivo"]}"/><text x="{ancho - 142}" y="18" font-size="11">Sentimiento</text>'
        f'<circle cx="{ancho - 62}" cy="14" r="4" fill="#4f46e5"/><text x="{ancho - 54}" y="18" font-size="11">Tema</text></svg>'
    )


def _svg_temas(resultados: list[dict], temas: list[str]) -> str:
    ancho, alto, izq, arriba = 560, 240, 110, 22
    alto_barra = 28
    maximo = max((sum(1 for r in resultados if r["tema"] == t) for t in temas), default=1)
    barras = []
    for i, tema in enumerate(temas):
        y = arriba + i * (alto_barra + 12)
        cursor = izq
        barras.append(f'<text x="0" y="{y + 19}" font-size="12" fill="#0f172a">{escape(tema.capitalize())}</text>')
        for sent in SENTIMIENTOS:
            n = sum(1 for r in resultados if r["tema"] == tema and r["sentimiento"] == sent)
            w = (ancho - izq - 12) * n / maximo
            if n:
                barras.append(f'<rect x="{cursor:.1f}" y="{y}" width="{w:.1f}" height="{alto_barra}" rx="4" fill="{COLORES[sent]}"/>')
                cursor += w
    leyenda = "".join(
        f'<circle cx="{ancho - 155 + i * 58}" cy="14" r="4" fill="{COLORES[s]}"/>'
        f'<text x="{ancho - 148 + i * 58}" y="18" font-size="10">{s[:4]}</text>'
        for i, s in enumerate(SENTIMIENTOS)
    )
    return f'<svg viewBox="0 0 {ancho} {max(alto, arriba + len(temas) * 40)}" role="img" aria-label="Temas divididos por sentimiento">{leyenda}{"".join(barras)}</svg>'


def _svg_palabras(claves: list[tuple[str, int]]) -> str:
    ancho, alto, izq, arriba, barra = 560, 240, 120, 10, 22
    maximo = max((n for _, n in claves), default=1)
    filas = []
    for i, (palabra, n) in enumerate(claves[:8]):
        y = arriba + i * 28
        w = (ancho - izq - 20) * n / maximo
        filas.append(
            f'<text x="0" y="{y + 16}" font-size="12">{escape(palabra)}</text>'
            f'<rect x="{izq}" y="{y}" width="{w:.1f}" height="{barra}" rx="4" fill="#4f46e5"/>'
            f'<text x="{izq + w + 7:.1f}" y="{y + 16}" font-size="12" fill="#64748b">{n}</text>'
        )
    return f'<svg viewBox="0 0 {ancho} {max(alto, arriba + len(claves[:8]) * 28)}" role="img" aria-label="Palabras clave más frecuentes">{"".join(filas)}</svg>'


def _svg_sentimientos(conteo: Counter, total: int) -> str:
    filas = []
    for i, sentimiento in enumerate(SENTIMIENTOS):
        porcentaje = 100 * conteo.get(sentimiento, 0) / total if total else 0
        y = 16 + i * 42
        filas.append(
            f'<text x="0" y="{y + 17}" font-size="12">{sentimiento.capitalize()}</text>'
            f'<rect x="95" y="{y}" width="390" height="24" rx="5" fill="#eef2ff"/>'
            f'<rect x="95" y="{y}" width="{3.9 * porcentaje:.1f}" height="24" rx="5" fill="{COLORES[sentimiento]}"/>'
            f'<text x="{100 + 3.9 * porcentaje:.1f}" y="{y + 17}" font-size="12" fill="#0f172a">{porcentaje:.0f}%</text>'
        )
    return f'<svg viewBox="0 0 560 150" role="img" aria-label="Porcentaje por sentimiento">{"".join(filas)}</svg>'


def _svg_histograma(resultados: list[dict]) -> str:
    valores = [r["conf_sent"] for r in resultados]
    grupos = [sum(1 for v in valores if i / 5 <= v < (i + 1) / 5) for i in range(5)]
    if valores and valores[-1] == 1:
        grupos[-1] += 1
    maximo = max(grupos, default=1)
    barras = []
    for i, cantidad in enumerate(grupos):
        alto = 125 * cantidad / maximo
        x = 35 + i * 100
        barras.append(
            f'<rect x="{x}" y="{145 - alto:.1f}" width="62" height="{alto:.1f}" rx="5" fill="#4f46e5"/>'
            f'<text x="{x + 31}" y="163" text-anchor="middle" font-size="11">{i * 20}-{(i + 1) * 20}%</text>'
            f'<text x="{x + 31}" y="{138 - alto:.1f}" text-anchor="middle" font-size="11">{cantidad}</text>'
        )
    return f'<svg viewBox="0 0 560 180" role="img" aria-label="Histograma de confianza"><line x1="25" y1="145" x2="540" y2="145" stroke="#cbd5e1"/>{"".join(barras)}</svg>'


def _svg_longitudes(resultados: list[dict]) -> str:
    grupos = [0, 0, 0, 0]
    for r in resultados:
        largo = len(r["texto"].split())
        grupos[min(largo // 10, 3)] += 1
    maximo = max(grupos, default=1)
    etiquetas = ["0-9", "10-19", "20-29", "30+"]
    barras = []
    for i, cantidad in enumerate(grupos):
        alto = 125 * cantidad / maximo
        x = 55 + i * 115
        barras.append(
            f'<rect x="{x}" y="{145 - alto:.1f}" width="70" height="{alto:.1f}" rx="5" fill="#16a34a"/>'
            f'<text x="{x + 35}" y="163" text-anchor="middle" font-size="11">{etiquetas[i]} palabras</text>'
            f'<text x="{x + 35}" y="{138 - alto:.1f}" text-anchor="middle" font-size="11">{cantidad}</text>'
        )
    return f'<svg viewBox="0 0 560 180" role="img" aria-label="Longitud de los comentarios"><line x1="35" y1="145" x2="540" y2="145" stroke="#cbd5e1"/>{"".join(barras)}</svg>'


def generar_html(resultados, acc_sent, acc_tema, n_entrena, claves) -> str:
    total = len(resultados)
    sent = Counter(r["sentimiento"] for r in resultados)
    temas = Counter(r["tema"] for r in resultados)
    pct_pos = 100 * sent.get("positivo", 0) / total if total else 0
    pct_neg = 100 * sent.get("negativo", 0) / total if total else 0

    filas = "".join(
        f"<tr><td>{escape(r['texto'])}</td>"
        f'<td><span class="tag" style="background:{COLORES[r["sentimiento"]]}">{r["sentimiento"]}</span> '
        f'<small>{r["conf_sent"]:.0%}</small></td>'
        f"<td>{escape(r['tema'])} <small>{r['conf_tema']:.0%}</small></td></tr>"
        for r in resultados
    )
    bloques_claves = "".join(
        f"<div><h3 style='margin:0 0 6px;font-size:15px'>{titulo}</h3><div class='chips'>{_chips(claves.get(k, []))}</div></div>"
        for k, titulo in [("general", "Todos los comentarios"), ("positivo", "Positivos"), ("negativo", "Negativos")]
    )
    mapa = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in MAPA)

    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Análisis de texto estilo MonkeyLearn</title><style>{CSS}</style></head><body>
<header><h1>Análisis de texto estilo MonkeyLearn</h1>
<p>Sentimiento · Temas · Palabras clave, con {total} comentarios de clientes</p></header>
<main>
<section><div class="etapa">Resumen</div><h2>Lo más importante</h2><p class="sub">Resultado de analizar los comentarios nuevos con modelos entrenados en {n_entrena} ejemplos.</p>
<div class="cards">
<div class="kpi"><b>{total}</b><span>comentarios analizados</span></div>
<div class="kpi"><b style="color:{COLORES['positivo']}">{pct_pos:.0f}%</b><span>positivos</span></div>
<div class="kpi"><b style="color:{COLORES['negativo']}">{pct_neg:.0f}%</b><span>negativos</span></div>
<div class="kpi"><b>{acc_sent:.0%}</b><span>exactitud del modelo de sentimiento (validación cruzada)</span></div>
<div class="kpi"><b>{acc_tema:.0%}</b><span>exactitud del modelo de temas (validación cruzada)</span></div>
</div></section>

<section><div class="etapa">Etapa 1</div><h2>¿Cómo se sienten los clientes?</h2>
<p class="sub">El modelo lee cada comentario y lo clasifica como positivo, neutro o negativo.</p>{_donut(sent, total)}</section>

<section><div class="etapa">Etapa 2</div><h2>¿De qué hablan?</h2>
<p class="sub">Cada comentario se asigna a un tema. Abajo se cruza el tema con el sentimiento: los números más altos tienen el color más fuerte.</p>
<div class="grid3" style="grid-template-columns:1fr 1.4fr"><div>{_barras(temas)}</div><div>{_cruce(resultados, [t for t, _ in temas.most_common()])}</div></div></section>

<section><div class="etapa">Visualizaciones</div><h2>Lectura visual del análisis</h2>
<p class="sub">Tres formas de ver la misma información: confianza del modelo, composición de temas y palabras frecuentes.</p>
<div class="graficas"><div class="grafica"><h3>Confianza por comentario</h3>{_svg_confianza(resultados)}</div>
<div class="grafica"><h3>Sentimiento dentro de cada tema</h3>{_svg_temas(resultados, [t for t, _ in temas.most_common()])}</div>
<div class="grafica"><h3>Palabras clave principales</h3>{_svg_palabras(claves.get("general", []))}</div>
<div class="grafica"><h3>Porcentaje por sentimiento</h3>{_svg_sentimientos(sent, total)}</div>
<div class="grafica"><h3>Histograma de confianza</h3>{_svg_histograma(resultados)}</div>
<div class="grafica"><h3>Longitud de los comentarios</h3>{_svg_longitudes(resultados)}</div></div></section>

<section><div class="etapa">Etapa 3</div><h2>Palabras que más se repiten</h2>
<p class="sub">El número es cuántas veces aparece la palabra.</p><div class="grid3">{bloques_claves}</div></section>

<section><div class="etapa">Detalle</div><h2>Cada comentario clasificado</h2>
<p class="sub">El porcentaje pequeño es la confianza del modelo en su respuesta.</p>
<table><tr><th>Comentario</th><th>Sentimiento</th><th>Tema</th></tr>{filas}</table></section>

<section><div class="etapa">Contexto</div><h2>¿Qué era MonkeyLearn y cómo se relaciona con esta demo?</h2>
<p class="sub">MonkeyLearn fue una plataforma web de análisis de texto sin programar. Medallia la adquirió en 2022 y el servicio independiente se cerró en 2023. Esta demo reproduce sus funciones principales con herramientas libres.</p>
<table><tr><th>Lo que hacía MonkeyLearn</th><th>Equivalente en esta demo</th></tr>{mapa}</table></section>
</main><footer>Generado con Python y scikit-learn</footer></body></html>"""
