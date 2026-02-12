# Ejercicio 4: Catálogo de películas + recomendador simple
# Contexto
# API que maneja un catálogo en memoria y recomienda películas por criterios.

from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field


router = APIRouter(
    prefix = "",
    tags = ["Ejercicio4"]
)

class Pelicula(BaseModel):
    id : str
    title : str
    genres : str
    year : int
    rating : float = Field(..., ge=0, le=10)

class PeliculaCreate(BaseModel):
    title : str
    genres : str
    year : int
    rating : float = Field(..., ge=0, le=10)
    

class Solicitud(BaseModel):
    preferred_genres: list[str]
    min_year: Optional[int] = None
    max_results: int
    
movies_history: dict[str,Pelicula] = {}

# 1. POST /movies
@router.post("/movies")
async def createMovies(movies: PeliculaCreate):
    movie_id = str(uuid4())
    
    movie = Pelicula(
        id = movie_id,
        title = movies.title,
        genres = movies.genres,
        year = movies.year,
        rating = movies.rating
    )
    
    movies_history[movie_id] = movie
    return {
        "msg" : "película creada",
        "data" : movie
    }
# 2. GET /movies/{movie_id}
# - Path param: movie_id
@router.get("/movies/{movie_id}")
async def movieXID(movie_id: str):
    movie = movies_history.get(movie_id)
    
    if not movie:
        raise HTTPException(
            status_code = 404,
            detail = "Movie not found in this reposotory"
        )
    
    return {
        "msg": "",
        "data" : movie
    }
# 3. GET /movies
# - Query params:
# - genre: str | null
# - min_rating: float | null
# - year: int | null
@router.get("/movies")
async def filtraMovies(
    genre: Optional[str] = Query(default = None),
    min_rating: Optional[float] = Query(default = None),
    year: Optional[int] = Query(default = None)
):
    filtrado: list[Pelicula] = []
    for movie in movies_history.values():
        if genre is not None and movie.genres != genre:
            continue
        if min_rating is not None and movie.rating < min_rating:
            continue
        if year is not None and movie.year != year:
            continue
        filtrado.append(movie)
    
    return {
        "msg" : "",
        "data" : filtrado
    }
# 4. POST /movies/recommend
# - Body (JSON):
# { "preferred_genres": [str], "min_year": int | null, "max_results": int }
# - Devuelve lista ordenada (por rating desc).
@router.post("/movies/recommend")
async def recommend_movies(req: Solicitud):
    if req.max_results <= 0:
        raise HTTPException(
            status_code=400, detail="max_results debe ser mayor que 0"
        )
    
    candidatos: list[Pelicula] = []
    
    for movie in movies_history.values():
        # Si no es None ni es menor al año mínimo, entonces
        if req.min_year is not None and movie.year < req.min_year:
            continue
        # “Si el usuario sí mandó una lista de géneros preferidos (no está vacía) y el género de esta película NO está dentro de esa lista, entonces descarto esta película.”
        if req.preferred_genres and movie.genres not in req.preferred_genres:
            continue
        candidatos.append(movie)

    candidatos.sort(key=lambda m: m.rating, reverse=True) # Ordenado por rating de forma descendente 
    
    recommend = candidatos[:req.max_results]
    
    return{
        "msg" : "",
        "data" : recommend
    }