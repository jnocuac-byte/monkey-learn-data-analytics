"""Etapa 3: extracción de palabras clave (conteo simple, sin modelo).

Equivale al "Keyword Extractor" de MonkeyLearn en su versión más básica.
"""
import re
import unicodedata
from collections import Counter

_STOP_TXT = """
de la el en y a los las un una unos unas que por con para es fue ser muy se lo del al me mi su sus
no pero mas como o le les ya hay esta este esto son si todo toda todos porque tambien sin sobre
estaba estaban llego llegaron he hice fui era tan solo cada nada nadie nunca siempre bien
"""


def _sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


_STOP = set(_STOP_TXT.split())


def palabras_clave(textos: list[str], n: int = 8) -> list[tuple[str, int]]:
    """Las n palabras más frecuentes (sin palabras vacías como 'de', 'la')."""
    conteo: Counter = Counter()
    for t in textos:
        for p in re.findall(r"[a-záéíóúüñ]+", t.lower()):
            if len(p) >= 4 and _sin_tildes(p) not in _STOP:
                conteo[p] += 1
    return conteo.most_common(n)
