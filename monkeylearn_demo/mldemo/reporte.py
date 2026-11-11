"""Etapa 4: reporte HTML autocontenido (sin internet, listo para proyectar)."""
from collections import Counter
from html import escape

COLORES = {"positivo": "#16a34a", "negativo": "#dc2626", "neutro": "#64748b"}
SENTIMIENTOS = ["positivo", "neutro", "negativo"]

CSS = """
:root{
  --bg:#f3f6f8;--surface:#fff;--surface-soft:#f7f9fa;--ink:#17212b;--muted:#667482;
  --line:#d8e0e6;--line-strong:#bdc9d2;--accent:#155e75;--accent-strong:#0e7490;
  --accent-soft:#e2f1f5;--positive:#16805a;--positive-soft:#e5f4ed;
  --negative:#b43b46;--negative-soft:#f9e8ea;--neutral:#64748b;--neutral-soft:#edf1f4;
  --shadow:0 8px 24px rgba(23,33,43,.06);--radius:10px
}
*{box-sizing:border-box}
html{background:var(--bg);scroll-behavior:smooth}
body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.5;font-size:15px}
header{background:var(--ink);color:#fff;border-bottom:4px solid var(--accent-strong);padding:38px max(24px,calc((100vw - 1180px)/2))}
header h1{margin:0 0 8px;font-size:clamp(25px,3vw,36px);line-height:1.1;letter-spacing:-.03em}
header p{margin:0;color:#cbd5dc;max-width:720px}
main{max-width:1180px;margin:0 auto;padding:28px 24px 48px}
section{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  box-shadow:var(--shadow);padding:24px;margin-bottom:18px}
h2{margin:0 0 5px;font-size:21px;line-height:1.25;letter-spacing:-.015em}
h3{color:var(--ink)}.etapa{color:var(--accent-strong);font-weight:750;font-size:11px;
  letter-spacing:.11em;text-transform:uppercase;margin-bottom:7px}.sub{color:var(--muted);margin:0 0 18px}
.cards{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}
.kpi{background:var(--surface-soft);border:1px solid var(--line);border-radius:8px;padding:15px 14px;min-height:94px}
.kpi b{display:block;font-size:30px;line-height:1.05;letter-spacing:-.04em;margin-bottom:9px;color:var(--ink)}
.kpi span{display:block;color:var(--muted);font-size:12px;line-height:1.35}
.fila{display:flex;gap:34px;align-items:center;flex-wrap:wrap}.donut{width:176px;height:176px;border-radius:50%;
  position:relative;flex:none;box-shadow:inset 0 0 0 1px rgba(23,33,43,.06)}
.donut::after{content:"";position:absolute;inset:37px;background:var(--surface);border-radius:50%;
  box-shadow:0 0 0 1px var(--line)}
.leyenda{min-width:190px}.leyenda div{margin:10px 0;color:var(--muted);font-size:14px}
.leyenda b{color:var(--ink)}.dot{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:8px}
.barra{display:flex;align-items:center;gap:12px;margin:12px 0}.barra .n{width:92px;font-weight:650;text-transform:capitalize}
.barra .t{flex:1;background:var(--neutral-soft);border-radius:4px;height:12px;overflow:hidden}
.barra .t i{display:block;height:100%;background:var(--accent-strong);border-radius:4px;transition:width .35s ease}
.barra .v{width:32px;text-align:right;color:var(--muted);font-variant-numeric:tabular-nums}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:14px}
th,td{padding:12px 13px;border-bottom:1px solid var(--line);text-align:left}
th{color:var(--muted);font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:.07em;background:var(--surface-soft)}
th:first-child{border-radius:6px 0 0 0}th:last-child{border-radius:0 6px 0 0}tr:last-child td{border-bottom:0}
tbody tr:hover td{background:#fbfcfc}td.c{text-align:center;font-weight:700;font-variant-numeric:tabular-nums}
.tag{display:inline-block;padding:3px 9px;border-radius:4px;color:#fff;font-size:11px;font-weight:750;letter-spacing:.02em}
.chips span{display:inline-block;background:var(--accent-soft);color:#164e63;border:1px solid #c8e3ea;
  border-radius:4px;padding:5px 10px;margin:3px 4px 3px 0;font-size:13px}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.graficas{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.grafica{border:1px solid var(--line);background:var(--surface-soft);border-radius:8px;padding:14px;min-width:0}
.grafica h3{margin:0 0 10px;font-size:14px}.grafica svg{display:block;width:100%;height:auto}
textarea{width:100%;min-height:175px;border:1px solid var(--line-strong);border-radius:8px;padding:15px;
  font:inherit;font-size:15px;line-height:1.55;background:#fbfcfc;color:var(--ink);resize:vertical}
textarea::placeholder{color:#8a98a4}textarea:focus,select:focus,button:focus-visible{outline:3px solid #8bd1df;outline-offset:2px}
.acciones{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-top:13px}
button{background:var(--accent);color:#fff;border:1px solid var(--accent);border-radius:6px;padding:10px 17px;
  font:inherit;font-size:14px;font-weight:700;cursor:pointer;transition:background .15s,transform .15s,box-shadow .15s}
button:hover{background:var(--accent-strong);box-shadow:0 3px 8px rgba(14,116,144,.2);transform:translateY(-1px)}
button:active{transform:translateY(0)}button.sec{background:var(--surface);color:var(--accent);border-color:var(--line-strong)}
button.sec:hover{background:var(--accent-soft);border-color:#9fcbd5;box-shadow:none}
button.mini{padding:6px 10px;font-size:12px}button:disabled{opacity:.55;cursor:wait;transform:none;box-shadow:none}
label.vivo{font-size:13px;color:var(--muted);display:flex;gap:7px;align-items:center;cursor:pointer;margin-left:4px}
label.vivo input{accent-color:var(--accent)}#estado{margin:12px 0 0;min-height:22px;font-size:13px}
select{border:1px solid var(--line-strong);border-radius:5px;padding:7px 8px;font:inherit;font-size:12px;
  background:var(--surface);color:var(--ink);max-width:100%}.vacio{color:var(--muted);padding:22px 0}
#toast{position:fixed;bottom:24px;left:50%;z-index:10;transform:translate(-50%,10px);background:var(--ink);
  color:#fff;padding:12px 17px;border-radius:6px;font-size:14px;box-shadow:0 8px 20px rgba(23,33,43,.22);
  opacity:0;pointer-events:none;transition:opacity .2s,transform .2s}#toast.on{opacity:1;transform:translate(-50%,0)}
.barra .t i{transition:width .35s}.tabla-scroll{overflow-x:auto}td small{color:var(--muted)}
footer{text-align:center;color:var(--muted);font-size:12px;padding:8px 0 30px}
@media (max-width:900px){.cards{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:640px){header{padding:28px 18px}main{padding:18px 14px 34px}section{padding:18px;margin-bottom:14px}
  .cards,.graficas{grid-template-columns:1fr 1fr}.kpi{min-height:84px}.kpi b{font-size:25px}
  .graficas .grafica:last-child{grid-column:1/-1}.acciones button{flex:1 1 auto}.acciones label{width:100%;margin:5px 0 0}
  .fila{gap:20px}.donut{width:145px;height:145px}.donut::after{inset:31px}}
@media print{body{background:#fff}header{background:#17212b!important;padding:24px;-webkit-print-color-adjust:exact;print-color-adjust:exact}
  main{padding:18px 0}section{box-shadow:none;break-inside:avoid}.acciones,textarea,#toast{display:none!important}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition-duration:.01ms!important}}
@media (prefers-color-scheme:dark){:root{--bg:#101820;--surface:#17232c;--surface-soft:#1d2b35;--ink:#edf3f5;--muted:#a8b7c0;
  --line:#30434f;--line-strong:#46606e;--accent-soft:#173d49;--neutral-soft:#263640;--shadow:0 8px 24px rgba(0,0,0,.18)}
  textarea{background:#142029;color:var(--ink)}.donut::after{background:var(--surface)}tbody tr:hover td{background:#1b2b35}
  .chips span{color:#bce5ef;border-color:#2d6472}select{background:var(--surface);color:var(--ink)}}
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
