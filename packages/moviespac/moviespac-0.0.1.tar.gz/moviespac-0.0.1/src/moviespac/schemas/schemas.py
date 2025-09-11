from pydantic import BaseModel
from typing import Optional, List


# --- Schémas secondaires ---

class RatingBase(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int

    class Config:
        orm_mode = True # Active la compatibilité avec SQLAlchemy ORM


class TagBase(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int

    class Config:
        orm_mode = True


class LinkBase(BaseModel):
    imdbId: Optional[str]
    tmdbId: Optional[int]

    class Config:
        orm_mode = True


# --- Schéma principal pour Movie ---
class MovieBase(BaseModel):
    movieId: int
    title: str
    genres: Optional[str] = None

    class Config:
        orm_mode = True


class MovieDetailed(MovieBase):
    ratings: List[RatingBase] = []
    tags: List[TagBase] = []
    link: Optional[LinkBase] = None


# --- Schéma pour liste de films (sans détails imbriqués) ---
class MovieSimple(BaseModel):
    movieId: int
    title: str
    genres: Optional[str]

    class Config:
        orm_mode = True


# --- Pour les endpoints de /ratings et /tags si appelés seuls ---
class RatingSimple(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int

    class Config:
        orm_mode = True


class TagSimple(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int

    class Config:
        orm_mode = True


class LinkSimple(BaseModel):
    movieId: int
    imdbId: Optional[str]
    tmdbId: Optional[int]

    class Config:
        orm_mode = True

class AnalyticsResponse(BaseModel):
    movie_count: int
    rating_count: int
    tag_count: int
    link_count: int

    class Config:
        orm_mode = True

class MovieScore(BaseModel):
    movieId: int                    # identifiant du film
    title: str                      # titre
    genres: Optional[str] = None    # genres du film
    average_rating: float           # moyenne calculée
    rating_count: int               # nombre de votes pris en compte

    class Config:
        orm_mode = True

class GenreStat(BaseModel):
    genre: str                      # nom du genre (ex: Comedy)
    count: int                      # combien de films de ce genre existent

    class Config:
        orm_mode = True
