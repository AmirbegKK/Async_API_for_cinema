from http import HTTPStatus
from typing import Optional

from api.v1.queries import get_query_film_by_genre, get_query_film_search
from core.decorators import cache
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel
from services.common import RetrivalService
from services.films import get_film_service, get_short_film_service

router = APIRouter()


class FilmAPI(BaseModel):

    uuid: str
    title: str
    imdb_rating: float
    description: Optional[str]
    genre: Optional[list[dict[str, str]]]
    actors: Optional[list[dict[str, str]]]
    writers: Optional[list[dict[str, str]]]
    directors: Optional[list[dict[str, str]]]


class ShortFilmAPI(BaseModel):

    uuid: str
    title: str
    imdb_rating: str


@router.get('/', response_model=list[ShortFilmAPI])
@cache()
async def popular_films(
    sort: str = '-imdb_rating',
    page_num: int = 1,
    page_size: int = 50,
    genre: Optional[str] = None,
    film_service: RetrivalService = Depends(get_short_film_service),
) -> list[ShortFilmAPI]:
    starting_doc = (page_num - 1) * page_size
    films = await film_service.get_by_query(
        sort=sort, size=page_size, from_=starting_doc, **get_query_film_by_genre(genre),
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return [ShortFilmAPI(**film.get_api_fields()) for film in films]


@router.get('/{uuid}', response_model=FilmAPI)
@cache()
async def film_details(
    uuid: str,
    film_service: RetrivalService = Depends(get_film_service),
) -> FilmAPI:
    film = await film_service.get_by_id(uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return FilmAPI(**film.get_api_fields())


@router.get('/search/', response_model=list[ShortFilmAPI])
@cache()
async def films_search(
    query: str,
    page_num: int = 1,
    page_size: int = 50,
    film_service: RetrivalService = Depends(get_short_film_service),
) -> list[ShortFilmAPI]:
    starting_doc = (page_num - 1) * page_size
    films = await film_service.get_by_query(
        size=page_size, from_=starting_doc, **get_query_film_search(query),
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return [ShortFilmAPI(**film.get_api_fields()) for film in films]
