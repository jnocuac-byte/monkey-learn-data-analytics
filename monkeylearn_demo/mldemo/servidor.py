"""Servidor web local: página interactiva + API.

Se ejecuta con:  uv run python web.py
Solo escucha en tu computador (127.0.0.1), nadie más en la red puede entrar.
"""
import argparse
import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from mldemo.clasificador import entrenar, predecir
from mldemo.datos import agregar_ejemplo, cargar_entrenamiento, cargar_nuevos
from mldemo.palabras import palabras_clave
from mldemo.reporte import CSS

PAGINA = Path(__file__).resolve().parent / "pagina.html"
SENTIMIENTOS = {"positivo", "neutro", "negativo"}
TEMAS = {"servicio", "envio", "precio", "producto"}
MAX_CUERPO = 1_000_000
MAX_TEXTOS = 500
MAX_LARGO = 1000


class Motor:
    """Guarda los modelos entrenados y los vuelve a entrenar cuando aprenden algo nuevo."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self._entrenar_todo()

    def _entrenar_todo(self) -> None:
        datos = cargar_entrenamiento()
        textos = [d["texto"] for d in datos]
        self.m_sent, self.acc_sent = entrenar(textos, [d["sentimiento"] for d in datos])
        self.m_tema, self.acc_tema = entrenar(textos, [d["tema"] for d in datos])
        self.n = len(datos)

    def estado(self) -> dict:
        return {"n_entrena": self.n, "acc_sent": self.acc_sent, "acc_tema": self.acc_tema}

    def analizar(self, textos: list[str]) -> dict:
        with self.lock:
            ps = predecir(self.m_sent, textos)
            pt = predecir(self.m_tema, textos)
            estado = self.estado()
        resultados = [
            {"texto": t, "sentimiento": s, "conf_sent": cs, "tema": tm, "conf_tema": ct}
            for t, (s, cs), (tm, ct) in zip(textos, ps, pt)
        ]
        claves = {"general": palabras_clave(textos, 8)}
        for s in SENTIMIENTOS:
            claves[s] = palabras_clave([r["texto"] for r in resultados if r["sentimiento"] == s], 6)
        return {"resultados": resultados, "claves": claves, **estado}

    def aprender(self, texto: str, sentimiento: str, tema: str) -> dict:
        with self.lock:
            agregar_ejemplo(texto, sentimiento, tema)
            self._entrenar_todo()
            return self.estado()


def _validar_textos(cuerpo: dict) -> list[str]:
    textos = cuerpo.get("textos")
    if not isinstance(textos, list) or not all(isinstance(t, str) for t in textos):
        raise ValueError("'textos' debe ser una lista de textos")
    textos = [t.strip() for t in textos if t.strip()]
    if len(textos) > MAX_TEXTOS:
        raise ValueError(f"Máximo {MAX_TEXTOS} comentarios a la vez")
    return [t[:MAX_LARGO] for t in textos]


def crear_manejador(motor: Motor):
    class Manejador(BaseHTTPRequestHandler):
        def log_message(self, *args):  # silencia el log de cada petición
            pass

        def _enviar(self, codigo: int, cuerpo: bytes, tipo: str) -> None:
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(cuerpo)

        def _json(self, datos, codigo: int = 200) -> None:
            self._enviar(codigo, json.dumps(datos, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                html = PAGINA.read_text(encoding="utf-8").replace("/*CSS*/", CSS)
                self._enviar(200, html.encode("utf-8"), "text/html; charset=utf-8")
            elif self.path == "/api/ejemplos":
                self._json({"textos": cargar_nuevos()})
            elif self.path == "/api/estado":
                self._json(motor.estado())
            else:
                self._json({"error": "No encontrado"}, 404)

        def do_POST(self):
            try:
                largo = int(self.headers.get("Content-Length", 0))
                if largo > MAX_CUERPO:
                    return self._json({"error": "Cuerpo demasiado grande"}, 413)
                cuerpo = json.loads(self.rfile.read(largo) or b"{}")
                if not isinstance(cuerpo, dict):
                    raise ValueError("Se esperaba un objeto JSON")
                if self.path == "/api/analizar":
                    return self._json(motor.analizar(_validar_textos(cuerpo)))
                if self.path == "/api/aprender":
                    texto = str(cuerpo.get("texto", "")).strip()[:MAX_LARGO]
                    sent, tema = cuerpo.get("sentimiento"), cuerpo.get("tema")
                    if not texto or sent not in SENTIMIENTOS or tema not in TEMAS:
                        raise ValueError("Falta el texto o la etiqueta no es válida")
                    return self._json({"ok": True, **motor.aprender(texto, sent, tema)})
                return self._json({"error": "No encontrado"}, 404)
            except (ValueError, json.JSONDecodeError) as e:
                self._json({"error": str(e)}, 400)
            except Exception as e:  # noqa: BLE001 - no tumbar el servidor por un error puntual
                self._json({"error": f"Error interno: {e}"}, 500)

    return Manejador


def iniciar() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Página interactiva estilo MonkeyLearn")
    ap.add_argument("--puerto", type=int, default=8000)
    ap.add_argument("--no-abrir", action="store_true", help="no abrir el navegador automáticamente")
    a = ap.parse_args()

    print("Entrenando modelos...")
    motor = Motor()
    print(f"Listo: {motor.n} ejemplos. Sentimiento {motor.acc_sent:.0%}, temas {motor.acc_tema:.0%}.")

    servidor = None
    for puerto in range(a.puerto, a.puerto + 11):
        try:
            servidor = ThreadingHTTPServer(("127.0.0.1", puerto), crear_manejador(motor))
            break
        except OSError:
            continue
    if servidor is None:
        raise SystemExit(f"No pude abrir ningún puerto entre {a.puerto} y {a.puerto + 10}.")

    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    print(f"\nAbre esta dirección en tu navegador:  {url}")
    print("Para detener el servidor: Ctrl + C\n")
    if not a.no_abrir:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()
