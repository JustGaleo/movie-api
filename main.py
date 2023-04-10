from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
app.title = 'My app with FastAPI'
app.version = '0.0.1'

class Movie(BaseModel):
    id: int
    title: str
    overview: str
    year: str 
    rating: float
    category: str

movies = [
    {
		"id": 1,
		"title": "Avatar",
		"overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
		"year": "2009",
		"rating": 7.8,
		"category": "Accion"
	},
        {
		"id": 2,
		"title": "Avatar 2",
		"overview": "Los Na'vi han vuelto...",
		"year": "2022",
		"rating": 9,
		"category": "Accion"
	}
]

@app.get('/info', tags=['home'])
def message():
    return {"name": "movie-api"}

@app.get('/movies', tags=['movies'])
def getMovies():
    return movies

@app.get('/movies/{id}', tags=['movies'])
def getMoviesById(id: int):
    return [movie for movie in movies if movie['id'] == id]

#get request with query params
@app.get('/movies/', tags=['movies'])
def getMoviesByCategory(category: str):
    return [movie for movie in movies if movie['category'] == category]

@app.post('/movie', tags =['movies'])
def addMovie(movie: Movie):
    movies.append(movie)
    return movies

@app.put('/movie/{id}', tags=['movies'])
def modifyMovie(id: int, movie: Movie):
    for item in movies:
        if item["id"] == id:
            item.update(movie)
    return movies

@app.delete('/movies/{id}', tags=['movies'])
def deleteMovie(id: int):
    movies_by_id = list(filter(lambda x: x['id'] == id , movies))
    if(len(movies_by_id) > 0):
        movies.remove(movies_by_id[-1])
        return movies
    else:
        raise HTTPException(status_code=404, detail="Movie not found")