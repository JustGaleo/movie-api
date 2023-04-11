from fastapi import FastAPI, HTTPException,Path, Query, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from middleware.jwt_manager import create_token
from fastapi.security import HTTPBearer
from config.database import Session, engine, Base 
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder
from middleware.error_handler import ErrorHandler
from middleware.jwt_bearer import JWTBearer

app = FastAPI()
app.title = 'My app with FastAPI'
app.version = '0.0.1'

app.add_middleware(ErrorHandler)

Base.metadata.create_all(bind=engine)

class User(BaseModel):
    email: str
    password: str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5, max_length=100)
    overview: str = Field(min_length=5, max_length=100)
    year: int = Field(le=2023)
    rating: float = Field(ge=1, le=10)
    category: str = Field(min_length=5, max_length=15)

@app.get('/info', tags=['home'])
def message():
    return {"name": "movie-api"}

@app.post('/login', tags=['auth'])
def login(user: User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())
    return JSONResponse(content=token, status_code=200)

@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def getMovies() -> List[Movie]:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        result = db.query(MovieModel).all()
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        else: 
            return JSONResponse(content=jsonable_encoder(result), status_code=200)

@app.get('/movies/{id}', tags=['movies'], response_model=Movie, status_code=200)
def getMoviesById(id: int = Path(ge=1, le=2000)) -> Movie:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        result = db.query(MovieModel).filter(MovieModel.id == id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        else: 
            return JSONResponse(content=jsonable_encoder(result), status_code=200)

#get request with query params
@app.get('/movies/', tags=['movies'], response_model=List[Movie], status_code=200)
def getMoviesByCategory(category: str = Query(min_length=10, max_length=15)) -> List[Movie]:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        result = db.query(MovieModel).filter(MovieModel.category == category).all()
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        else: 
            return JSONResponse(content=jsonable_encoder(result), status_code=200)

@app.post('/movie', tags =['movies'], response_model=dict, status_code=201)
async def addMovie(movie: Movie) -> dict:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        new_movie = MovieModel(**movie.dict())
        db.add(new_movie)
        db.commit()
        return JSONResponse(status_code=201, 
                            content={"message": "Upload Successful",
                                     "details": movie.dict()})

@app.put('/movie/{id}', tags=['movies'], response_model=List[Movie], status_code=200)
def modifyMovie(movie: Movie, id: int = Path(ge=1, le=2000)) -> List[Movie]:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        result = db.query(MovieModel).filter(MovieModel.id == id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        else: 
            result.title = movie.title
            result.category = movie.overview
            result.overview = movie.overview
            result.rating = movie.rating
            result.year = movie.year  
            db.commit()
            return JSONResponse(status_code=201, content={"message": "Updated done"})


@app.delete('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def deleteMovie(id: int = Path(ge=1, le=2000)) -> dict:
    try:
        db = Session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        result = db.query(MovieModel).filter(MovieModel.id == id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        else: 
            db.delete(result)
            db.commit()
            return JSONResponse(status_code=201, content={"message": "Delete successful"})