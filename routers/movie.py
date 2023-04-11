from fastapi import APIRouter, HTTPException
from fastapi import Depends, Path, Query
from fastapi.responses import JSONResponse
from typing import List
from config.database import Session
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder
from middleware.jwt_bearer import JWTBearer
from services.movie import MovieService
from schemas.movie import Movie

movie_router = APIRouter()

@movie_router.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200)
async def getMovies() -> List[Movie]:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        result = MovieService(db).get_movies()
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        else: 
            return JSONResponse(content=jsonable_encoder(result), status_code=200)

@movie_router.get('/movies/{id}', tags=['movies'], response_model=Movie, status_code=200)
async def getMoviesById(id: int = Path(ge=1, le=2000)) -> Movie:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        result = MovieService(db).get_movie(id)
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        else: 
            return JSONResponse(content=jsonable_encoder(result), status_code=200)

#get request with query params
@movie_router.get('/movies/', tags=['movies'], response_model=List[Movie], status_code=200)
async def getMoviesByCategory(category: str = Query(min_length=10, max_length=15)) -> List[Movie]:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        result = MovieService(db).get_movie_by_category(category)
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        else: 
            return JSONResponse(content=jsonable_encoder(result), status_code=200)

@movie_router.post('/movie', tags =['movies'], response_model=dict, status_code=201)
async def addMovie(movie: Movie) -> dict:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        MovieService(db).create_movie(movie)
        return JSONResponse(status_code=201, 
                            content={"message": "Upload Successful",
                                     "details": movie.dict()})

@movie_router.put('/movie/{id}', tags=['movies'], response_model=List[Movie], status_code=200)
async def modifyMovie(movie: Movie, id: int = Path(ge=1, le=2000)) -> List[Movie]:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        result = MovieService(db).get_movie(id)
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        else: 
            MovieService(db).update_movie(id, movie)
            return JSONResponse(status_code=201, content={"message": "Updated done"})

@movie_router.delete('/movies/{id}', tags=['movies'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
async def deleteMovie(id: int = Path(ge=1, le=2000)) -> dict:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        result = MovieService(db).get_movie(id)
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        else: 
            MovieService(db).delete_movie(id)
            return JSONResponse(status_code=201, content={"message": "Delete successful"})