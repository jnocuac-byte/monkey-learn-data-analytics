"""Etapas 1 y 2: clasificadores de texto (sentimiento y temas).

Es la misma idea que el "Classifier" de MonkeyLearn: se le dan ejemplos
etiquetados, el modelo aprende, y luego clasifica textos nuevos.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline, make_union


def entrenar(textos: list[str], etiquetas: list[str]):
    """Entrena un clasificador y devuelve (modelo, exactitud_validada).

    El texto se convierte en números de dos formas a la vez:
    - palabras sueltas y pares de palabras ("no funciona")
    - fragmentos de letras (ayuda con variantes: caro / carísimo, dañado / dañó)
    """
    comun = dict(strip_accents="unicode", lowercase=True, sublinear_tf=True)
    modelo = make_pipeline(
        make_union(
            TfidfVectorizer(ngram_range=(1, 2), **comun),
            TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), **comun),
        ),
        LogisticRegression(C=10, max_iter=3000),
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    exactitud = float(cross_val_score(modelo, textos, etiquetas, cv=cv).mean())
    modelo.fit(textos, etiquetas)
    return modelo, exactitud


def predecir(modelo, textos: list[str]) -> list[tuple[str, float]]:
    """Devuelve [(etiqueta, confianza)] por cada texto."""
    proba = modelo.predict_proba(textos)
    clases = modelo.classes_
    return [(str(clases[fila.argmax()]), float(fila.max())) for fila in proba]
