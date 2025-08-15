from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil
from sqlalchemy import func

from database import get_db, MovieModel

from schemas.movies import MovieListResponseSchema, MovieDetailResponseSchema

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def read_movies(
        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=1),
        db: AsyncSession = Depends(get_db)
):
    if not isinstance(page, int):
        raise HTTPException(
            status_code=422,
            detail=[{"msg": "Page must be an integer"}]
        )
    if not isinstance(per_page, int):
        raise HTTPException(
            status_code=422,
            detail=[{"msg": "Page must be an integer"}]
        )
    if not (1 <= per_page <= 20):
        raise HTTPException(
            status_code=422, detail="<UNK>"
        )

    if not (page >= 1):
        raise HTTPException(
            status_code=422, detail="<UNK>"
        )
    total_items = await db.execute(select(func.count()).select_from(MovieModel))
    total_items = total_items.scalar_one()
    total_pages = ceil(total_items / per_page)

    result = await db.execute(
        select(MovieModel)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    movies = result.scalars().all()

    if not movies:
        raise HTTPException(
            status_code=404, detail="No movies found."
        )

    return MovieListResponseSchema(
        movies=movies,
        prev_page=f"http://localhost:8000/api/v1/theater/movies?page={page - 1}"
                  f"&per_page={per_page}" if page > 1 else None,
        next_page=f"http://localhost:8000/api/v1/theater/movies?page={page + 1}"
                  f"&per_page={per_page}" if page < total_pages else None,
        total_pages=total_pages,
        total_items=total_items
    )


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")
    return movie
