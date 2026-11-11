# Demo estilo MonkeyLearn (análisis de texto en español)

## 1. ¿Qué era MonkeyLearn?

MonkeyLearn fue una **plataforma web** (no una librería) para analizar texto **sin programar**.
Pegabas o subías textos (reseñas, encuestas, tickets de soporte) y te devolvía:

| Función de MonkeyLearn | Qué hacía | Dónde está en este proyecto |
|---|---|---|
| Sentiment Analysis | Decir si un texto es positivo, neutro o negativo | Etapa 1 (`mldemo/clasificador.py`) |
| Topic Classifier | Asignar cada texto a un tema (precio, envío, etc.) | Etapa 2 (`mldemo/clasificador.py`) |
| Keyword Extractor | Sacar las palabras más importantes | Etapa 3 (`mldemo/palabras.py`) |
| Entrenar modelos propios con clics | Subir ejemplos etiquetados y crear tu propio clasificador | Editar los CSV `data/entrenamiento*.csv` |
| Dashboards | Gráficas con los resultados | Etapa 4 (`mldemo/reporte.py`) |
| API | Conectar con otras apps | Importar las funciones de `mldemo/` |

**Estado actual:** Medallia la adquirió en 2022, el servicio independiente se cerró en 2023 y
`monkeylearn.com` hoy redirige a Medallia. Por eso esta demo reproduce sus funciones con
herramientas libres (Python + scikit-learn).

## 2. Cómo ejecutarlo (Windows)

Necesitas [uv](https://docs.astral.sh/uv/). Abre PowerShell dentro de esta carpeta y ejecuta:

```powershell
.\run.ps1
```

Eso instala uv si falta, instala las dependencias (`uv sync`) y abre la **página interactiva**
en tu navegador (http://127.0.0.1:8000). Para detenerla, `Ctrl + C` en la terminal.
Si PowerShell bloquea scripts, usa los comandos manuales:

```powershell
uv sync
uv run python web.py
```

### Página interactiva (lo principal para la demo)

- Escribes o pegas comentarios (uno por línea) y las gráficas se recalculan solas mientras escribes.
- **Cargar ejemplos** trae 16 comentarios de muestra; **Limpiar** vacía la caja; **Descargar CSV** guarda los resultados.
- En la tabla de detalle puedes corregir la etiqueta de un comentario y pulsar **Enseñar**: el ejemplo se guarda en
  `data/entrenamiento_usuario.csv` y el modelo se reentrena (tarda unos segundos). Es la función de MonkeyLearn de
  "entrenar con clics". Para volver al modelo original, borra ese archivo.
- Todo corre en tu computador: el servidor solo escucha en `127.0.0.1` y no envía tus textos a ningún servicio externo.

### Reporte estático (opcional)

`.\run.ps1 -Reporte` (o `uv run python main.py --abrir`) genera `output/reporte.html`, un archivo único que puedes enviar o abrir sin servidor.

Paquetes que se instalan: solo `scikit-learn` (y lo que él necesita, como numpy y scipy).
Todo está declarado en `pyproject.toml`.

## 3. Opciones útiles (línea de comandos)

`uv run python web.py --puerto 9000` cambia el puerto y `--no-abrir` evita que se abra el navegador.
Los demás comandos usan `main.py`:

```powershell
uv run python main.py --etapa 1                  # solo sentimiento
uv run python main.py --etapa 2                  # hasta temas
uv run python main.py --etapa 3                  # hasta palabras clave
uv run python main.py                            # todo + reporte en output/reporte.html
uv run python main.py --texto "El envío llegó tarde y roto"   # un solo texto (ideal para la demo en vivo)
uv run python main.py --archivo mis_comentarios.csv --abrir   # tus propios datos
```

Tu CSV propio debe tener una columna llamada `texto`.

## 4. Cómo funciona por dentro (para explicarlo)

1. **Ejemplos etiquetados:** `data/entrenamiento.csv` y `data/entrenamiento_extra.csv` suman 156 comentarios con su sentimiento y su tema.
2. **Entrenamiento:** el texto se convierte en números (TF-IDF: da más peso a las palabras que distinguen un comentario de otro, y se usan palabras y también fragmentos de letras para tolerar variantes como caro/carísimo) y una regresión logística aprende qué se asocia a cada etiqueta.
3. **Predicción:** para un comentario nuevo, el modelo calcula la probabilidad de cada etiqueta y elige la más alta (esa es la "confianza").
4. **Validación:** la "exactitud" se mide con validación cruzada: se entrena con una parte de los ejemplos y se prueba con la parte que el modelo no vio.

Resultados de la validación cruzada con los datos incluidos: aprox. **79% en sentimiento** y **83% en temas**.
Limitación honesta: con 156 ejemplos el modelo es una demostración, no un producto. Se equivoca con frases
ambiguas (por ejemplo "el domiciliario fue amable pero se demoró mucho" mezcla algo bueno y algo malo) y con palabras
que nunca vio. Mientras más ejemplos agregues a los CSV de `data/`, mejor funciona.

## 5. Cómo implementarlo en tu propio proyecto

```python
from mldemo.datos import cargar_entrenamiento
from mldemo.clasificador import entrenar, predecir

datos = cargar_entrenamiento()
modelo, exactitud = entrenar([d["texto"] for d in datos], [d["sentimiento"] for d in datos])
print(predecir(modelo, ["Me encantó la atención"]))   # [('positivo', 0.7...)]
```

Para usar otras categorías, cambia las etiquetas del CSV (por ejemplo `urgente / no urgente`)
y vuelve a ejecutar.

## 6. Guion sugerido para la exposición (5 minutos)

1. **Qué es MonkeyLearn** (1 min): plataforma no-code de análisis de texto; se vendió a Medallia y se cerró en 2023.
2. **Para qué sirve** (1 min): una empresa con miles de comentarios no los puede leer todos; esto los clasifica solo.
3. **Demo en vivo** (2 min): con la página interactiva abierta, pide comentarios al público y escríbelos en la caja; las gráficas cambian al instante. Si el modelo se equivoca, corrígelo con **Enseñar** y muestra que aprende.
4. **Cómo se implementa hoy** (1 min): mismas funciones con Python y scikit-learn, o con alternativas como Google Cloud Natural Language, Amazon Comprehend o MeaningCloud.

## Estructura

```
web.py                   página interactiva (servidor local)
main.py                  versión por consola + reporte estático
run.ps1                  atajo para PowerShell
pyproject.toml           dependencias (uv)
data/entrenamiento*.csv  ejemplos etiquetados (se leen todos los que empiecen así)
data/comentarios_nuevos.csv   comentarios a analizar
mldemo/                  código de cada etapa (servidor.py y pagina.html son la web)
output/                  reporte.html, resultados.csv, resultados.json (se crea al ejecutar)
```
