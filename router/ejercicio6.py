# Ejercicio 6: Analizador de texto (estadísticas + filtros)
# Contexto
# API que recibe texto y devuelve estadísticas (sin guardar), útil para practicar body + query params.

import re
from collections import Counter
from typing import Optional, Literal
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="",
    tags=["Ejercicio6"]
)

# =========================
# MODELOS (REQUEST / RESPONSE)
# =========================

class TextAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: Literal["es", "en"]

class WordCount(BaseModel):
    word: str
    count: int

class TextAnalyzeResponse(BaseModel):
    words: int
    characters: int
    top_words: list[WordCount]

class FrequencyResponse(BaseModel):
    word: str
    frequency: int
    case_sensitive: bool

class CensorRequest(BaseModel):
    text: str = Field(..., min_length=1)
    banned: list[str] = Field(default_factory=list)
    mask: str = Field(default="*", min_length=1)

class CensorResponse(BaseModel):
    censored_text: str


# =========================
# HELPERS
# =========================

STOPWORDS_ES = {
    "de","la","que","el","en","y","a","los","del","se","las","por","un","para","con",
    "no","una","su","al","lo","como","mas","más","pero","sus","le","ya","o","este",
    "si","sí","porque","esta","entre","cuando","muy","sin","sobre","tambien","también",
    "me","hasta","hay","donde","quien","quién","desde","todo","nos","durante","todos",
    "uno","les","ni","contra","otros","ese","eso","ante","ellos","e","esto","mi","mí",
    "antes","algunos","que","qué","unos","yo","otro","otras","otra","el","él"
}

STOPWORDS_EN = {
    "the","and","a","an","to","of","in","is","it","you","that","he","was","for","on",
    "are","with","as","i","his","they","be","at","one","have","this","from","or","had",
    "by","not","but","what","some","we","can","out","other","were","all","there","when",
    "up","your","how","said","each","she"
}

def tokenize(text: str):
    # Palabras "normales", ignorando signos; soporta tildes por Unicode
    # Ej: "Hola, Perú!" -> ["Hola", "Perú"]
    return re.findall(r"\b\w+\b", text, flags=re.UNICODE)

def get_stopwords(language: str):
    if language == "es":
        return STOPWORDS_ES
    if language == "en":
        return STOPWORDS_EN
    return set()


# =========================
# ENDPOINTS
# =========================

# 1) POST /text/analyze
# Body: { "text": str, "language": "es|en" }
# Devuelve:
# - número de palabras
# - número de caracteres
# - top 5 palabras más repetidas
# Reto extra: ignore_stopwords=true (query param)
@router.post("/text/analyze", response_model=TextAnalyzeResponse)
async def analyze_text(
    payload: TextAnalyzeRequest,
    ignore_stopwords: bool = Query(default=False)
):
    words = tokenize(payload.text)
    total_words = len(words)
    total_chars = len(payload.text)

    # Conteo base (case-insensitive para que sea “de examen” y consistente)
    normalized = [w.lower() for w in words]

    # Aplicar stopwords solo para el TOP (más útil y más estándar)
    if ignore_stopwords:
        sw = get_stopwords(payload.language)
        normalized_for_top = [w for w in normalized if w not in sw]
    else:
        normalized_for_top = normalized

    counter = Counter(normalized_for_top)

    # top 5 por frecuencia desc; si empatan, por orden alfabético para estabilidad
    top = sorted(counter.items(), key=lambda x: (-x[1], x[0]))[:5]
    top_words = [WordCount(word=w, count=c) for w, c in top]

    return TextAnalyzeResponse(
        words=total_words,
        characters=total_chars,
        top_words=top_words
    )


# 2) GET /text/{word}/frequency
# Path: word
# Query:
# - text: str (obligatorio)
# - case_sensitive: bool (default false)
@router.get("/text/{word}/frequency", response_model=FrequencyResponse)
async def word_frequency(
    word: str,
    text: str = Query(..., min_length=1),
    case_sensitive: bool = Query(default=False)
):
    tokens = tokenize(text)

    if case_sensitive:
        target = word
        freq = sum(1 for t in tokens if t == target)
    else:
        target = word.lower()
        freq = sum(1 for t in tokens if t.lower() == target)

    return FrequencyResponse(
        word=word,
        frequency=freq,
        case_sensitive=case_sensitive
    )


# 3) POST /text/censor
# Body: { "text": str, "banned": [str], "mask": "*" }
# Devuelve texto censurado.
@router.post("/text/censor", response_model=CensorResponse)
async def censor_text(payload: CensorRequest):
    # Si no hay palabras prohibidas, retorna el texto tal cual
    banned_clean = [b.strip() for b in payload.banned if b.strip()]
    if not banned_clean:
        return CensorResponse(censored_text=payload.text)

    # Construir regex: \b(word1|word2|...)\b
    # Escapamos para evitar problemas con caracteres especiales
    pattern = r"\b(" + "|".join(re.escape(w) for w in banned_clean) + r")\b"

    def repl(match):
        original = match.group(0)
        return payload.mask * len(original)

    censored = re.sub(pattern, repl, payload.text, flags=re.IGNORECASE)

    return CensorResponse(censored_text=censored)
