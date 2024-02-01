from fastapi import FastAPI, Body, status, Path, Query, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, Response
import json
from dataclasses import dataclass, asdict
from typing import Any, Coroutine, Optional, List
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from datetime import datetime

from starlette.requests import Request
from .jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer


app = FastAPI()
app.title = "My first app with FastAPI"
app.version = "0.0.1"

movie_file = "movies.json"


def get_all_movies():
    with open(movie_file, 'r') as file:
        # Load the JSON data
        movies = json.load(file)
    return movies


class User(BaseModel):
    email: str = "admin"
    password: str = "admin"


class Movie(BaseModel):
    id: Optional[int]
    title: str = Field(max_length=20)
    genre: str = Field(max_length=20, min_length=1)
    director: str = Field(min_length=1)
    release_year: int = Field(ge=2000, le=datetime.now().year)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 0,
                "title": "NoName",
                "genre": "Unclasified",
                "director": "NoOne",
                "release_year": datetime.now().year
            }
            }

    def asdict(self) -> dict:
        return dict(self)

    def set_id(self, id: int) -> None:
        self.id = id


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Coroutine[Any,
                                                            Any,
                                                            HTTPAuthorizationCredentials | None]:
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if not data or data['email'] != 'admin':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Credenciales incorrectas')



@dataclass
class MovieWebSites:
    id: Optional[int] = None
    name: str = None
    url: str = None
    ip: str = None


@app.post('/login', tags=["auth"], status_code=status.HTTP_200_OK)
def login(user: User):
    if user.email == "admin" and user.password == "admin":
        token: str = create_token(user.model_dump())
        return JSONResponse(content=token)
    return JSONResponse(content=[""], status_code=status.HTTP_204_NO_CONTENT)



@app.get('/', tags=["Home"])
def main():
    return {"valor":1}


@app.get('/main2', tags=["Home"])
def main2():
    return HTMLResponse("<h1>Hola mundo</h1>")


@app.get('/movies', tags=["movies"], response_model=List[Movie],
         dependencies=[Depends(JWTBearer())])
def get_movies():
    return JSONResponse(content=get_all_movies())


@app.get('/movies/{id}', tags=["movies"], response_model=Movie,
         status_code=status.HTTP_200_OK,
         dependencies=[Depends(JWTBearer())])
def get_movie(id: int = Path(ge=1, le=1000)):
    data = get_all_movies()
    movie = list(filter(lambda movie: movie['id'] == id, data))
    if movie:
        return JSONResponse(content=movie)

    return JSONResponse(content=[], status_code=status.HTTP_404_NOT_FOUND)


@app.get('/movies/', tags=["movies"], status_code=status.HTTP_200_OK)
def get_movie_by_genre(genre: str = Query(min_length=1, max_length=20)):
    data = get_all_movies()
    if data:
        return JSONResponse(content=list(
                            filter(lambda movie: movie['genre'] == genre, data)))
    return JSONResponse(content=[])

@app.post('/movies', tags=["movies"], status_code=status.HTTP_201_CREATED)
def create_movie(movie: Movie = Body()):
    movies = get_all_movies()
    newid = max([movie["id"] for movie in movies], default=0) + 1
    movie.set_id(newid)
    movies.append(movie.asdict())
    with open(movie_file, 'w') as file:
        json.dump(movies, file, indent=2)
    return JSONResponse(content={"message": "The creation was succesfull"})


@app.delete('/movies/{id}', tags=["movies"],
            status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(id: int):
    data = get_all_movies()
    data = list(filter(lambda movie: movie['id'] != id, data))
    with open(movie_file, 'w') as file:
        json.dump(data, file, indent=2)
    return JSONResponse(content={"message":"The element was deleted"})

@app.put('/movies', tags=["movies"],
         status_code=status.HTTP_200_OK)
def update_movie(movie: Movie):
    data = get_all_movies()
    # temporary deleting
    idupdate = movie.id
    data = list(filter(lambda movie: movie['id'] != idupdate, data))
    # ----------
    data.append(movie.asdict())
    with open(movie_file, 'w') as file:
        data.sort(key= lambda movie: movie["id"])
        json.dump(data, file, indent=2)
    return JSONResponse(content={"message":"The update was succesfull"})

# uvicorn main:app --reload