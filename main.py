from fastapi import FastAPI, HTTPException,Path, Query, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer

app = FastAPI()
app.title = 'My app with FastAPI'
app.version = '0.0.1'

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "admin@gmail.com":
            raise HTTPException(status_code=403, detail="Invalid credentials")
        
class User(BaseModel):
    email: str
    password: str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5, max_length=100)
    overview: str = Field(min_length=5, max_length=100)
    year: str = Field(min_length=5)
    rating: float = Field(ge=1, le=10)
    category: str = Field(min_length=5, max_length=15)

movies = [
   {
		"id": 1,
		"title": "Avatar",
		"overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
		"year": "2009",
		"rating": 7.8,
		"category": "Accion"
	}
]

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
    if len(movies) == 0:
        raise HTTPException(status_code=404, detail="There aren't movies")
    else:
        return JSONResponse(content=movies, status_code=200)

@app.get('/movies/{id}', tags=['movies'], response_model=Movie, status_code=200)
def getMoviesById(id: int = Path(ge=1, le=2000)) -> Movie:
    data = [movie for movie in movies if movie['id'] == id]
    if len(data) == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    else:
        return JSONResponse(content=data, status_code=200)

#get request with query params
@app.get('/movies/', tags=['movies'], response_model=List[Movie], status_code=200)
def getMoviesByCategory(category: str = Query(min_length=10, max_length=15)) -> List[Movie]:
    data = [movie for movie in movies if movie['category'] == category]
    if len(data) == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    else:
        return JSONResponse(content=data, status_code=200)

@app.post('/movie', tags =['movies'], response_model=List[Movie], status_code=201)
def addMovie(movie: Movie) -> List[Movie]:
    movies.append(movie)
    return JSONResponse(content=movies, status_code=201)

@app.put('/movie/{id}', tags=['movies'], response_model=List[Movie], status_code=200)
def modifyMovie(movie: Movie, id: int = Path(ge=1, le=2000)) -> List[Movie]:
    for item in movies:
        if item["id"] == id:
            item.update(movie)
    return JSONResponse(content=movies, status_code=200)

@app.delete('/movies/{id}', tags=['movies'], response_model=List[Movie], status_code=200)
def deleteMovie(id: int = Path(ge=1, le=2000)) -> List[Movie]:
    movies_by_id = list(filter(lambda x: x['id'] == id , movies))
    if(len(movies_by_id) > 0):
        movies.remove(movies_by_id[-1])
        return JSONResponse(content=movies, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Movie not found")