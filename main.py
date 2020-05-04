import secrets
import sqlite3
from hashlib import sha256
from typing import Dict

from fastapi import FastAPI, HTTPException, Depends, Response, status, Cookie, Request
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from pydantic import BaseModel

app = FastAPI()
app.patients={}
app.counter=0

@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


class HelloResp(BaseModel):
    msg: str


@app.get("/hello/{name}", response_model=HelloResp)
def read_item(name: str):
    return HelloResp(msg=f"Hello {name}")


class GiveMeSomethingRq(BaseModel):
    first_key: str


class GiveMeSomethingResp(BaseModel):
    received: Dict
    constant_data: str = "python jest super"


@app.post("/whatever", response_model=GiveMeSomethingResp)
def receive_something(rq: GiveMeSomethingRq):
    return GiveMeSomethingResp(received=rq.dict())


@app.get("/method")
def method_get():
    return {"method":"GET"}


@app.post("/method")
def method_post():
    return {"method":"POST"}


@app.put("/method")
def method_put():
    return {"method":"PUT"}


@app.delete("/method")
def method_delete():
    return {"method":"DELETE"}


# class PatientResponse(BaseModel):
#     name: str
#     surename: str


#app.counter = 0
# app.patients = dict()

#@app.post("/patient")
# def patient_with_saving(patient: PatientResponse):
#     app.counter += 1
#     app.patients.append(patient)
#     return {"id": app.counter, "patient": patient}

#@app.get("/patient/{pk}")
# def get_patient_by_id(pk: int):
#     if pk > app.counter or pk < 0:
#         raise HTTPException(status_code=204, detail="No content")
#     else:
#         return app.patients[pk-1]

### FICZUR

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
security = HTTPBasic()
app.session_tokens = []
app.secret_key = "very constatn and random secret, best 64 characters, here it is."

@app.get("/welcome")
def welcome(request: Request, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=401, detail="Login required")
    return templates.TemplateResponse("greeting.html", {"request": request, "user": "trudnY"})

    # return {"message": "Welcome! Bienvenido! Benvenuto! Willkommen!"}

@app.post("/login")
def login_auth(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "trudnY")
    correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401,  detail="Incorrect email or password", headers={"WWW-Authenticate": "Basic"})
    session_token = sha256(
        bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding='utf8')).hexdigest()
    app.session_tokens.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    response.headers["Location"] = "/welcome"
    response.status_code = status.HTTP_302_FOUND


@app.post("/logout")
def logout_check(*, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=401, detail="Login required")
    app.session_tokens.remove(session_token)
    response.headers["Location"] = "/"
    response.status_code = status.HTTP_302_FOUND

class PatientRq(BaseModel):
    name: str
    surname: str

@app.post("/patient")
def add_patient(response: Response, rq: PatientRq, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Login required"
    pk=f"id_{app.counter}"
    app.patients[pk]=rq.dict()
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = f"/patient/{pk}"
    app.counter+=1

@app.get("/patient")
def get_patients_all(response: Response, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Login required"
    if len(app.patients) != 0:
        return app.patients
    response.status_code = status.HTTP_204_NO_CONTENT

@app.get("/patient/{pk}")
def get_patient(pk: str, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Login required"
    if pk in app.patients:
        return app.patients[pk]
    response.status_code = status.HTTP_204_NO_CONTENT

@app.delete("/patient/{pk}")
def remove_patient(pk: str, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Login required"
    app.patients.pop(pk, None)
    response.status_code = status.HTTP_204_NO_CONTENT

################## wyklad 4 ###########################

@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')

@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()

# 1
@app.get("/tracks")
async def get_tracks(page: int = 0, per_page: int = 10):
    app.db_connection.row_factory = sqlite3.Row
    tracks = app.db_connection.execute(
        f"SELECT * FROM tracksORDER BY TrackId LIMIT {per_page} OFFSET {per_page * (page)}"
        ).fetchall()
    return tracks

# 2
@app.get("/tracks/composers")
async def show_titles(composer_name: str):
    app.db_connection.row_factory = lambda cursor, x : x[0]
    tracks = app.db_connection.execute(
        f'SELECT name FROM tracks WHERE composer = "{composer_name}" ORDER BY name').fetchall()
    if len(tracks) <= 0:
        raise HTTPException(status_code=404, detail={"error": "Item not found"})
    return tracks

# 3
class AlbumRequest(BaseModel):
    title: str
    artist_id: int


class AlbumResponse(BaseModel):
    AlbumId: int
    Title: str
    ArtistId: int

@app.post("/albums", response_model=AlbumResponse)
async def insert_album(response: Response, request: AlbumRequest):
    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.cursor()
    artist = cursor.execute("SELECT * FROM artists WHERE artistId = ?",
                                        (request.artist_id,)).fetchall()
    if len(artist) <= 0:
        raise HTTPException(status_code=404, detail={"error": "No artist with this id"})
    cursor.execute("INSERT INTO albums(title, artistId) VALUES (?,?)",
                                        (request.title,request.artist_id))
    app.db_connection.commit()
    response.status_code = 201
    return AlbumResponse(AlbumId=cursor.lastrowid, Title=request.title, ArtistId=request.artist_id)


@app.get("/albums/{album_id}", response_model=AlbumResponse)
async def get_album(album_id: int):
    app.db_connection.row_factory = sqlite3.Row
    album = app.db_connection.execute("SELECT * FROM albums WHERE albumId = ?",
                                        (album_id,)).fetchall()
    if len(album) <= 0:
        raise HTTPException(status_code=404, detail={"error": "Item not found"})
    return AlbumResponse(AlbumId=album_id, Title=album[0]["title"], ArtistId=album[0]["artistId"])

# 4

class CustomerRequest(BaseModel):
	company: str =''
	address: str =''
	city: str =''
	state: str =''
	country: str =''
	postalcode: str =''
	fax: str =''

@app.put("/customers/{customer_id}")
async def customer_edit(customer_id: int, request: CustomerRequest):
    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.cursor()
    name = cursor.execute(f'SELECT CustomerId FROM customers WHERE CustomerId = {customer_id}').fetchone()
    if not name:
        raise HTTPException(status_code=404, detail= {'error': "Customer not found"})
    for x, y in request.__dict__.items():
        if y:
            cursor.execute(f'UPDATE customers SET {x} = "{y}" WHERE CustomerId = {customer_id}')
            app.db_connection.commit()
    return cursor.execute(f'SELECT * FROM customers WHERE CustomerId={customer_id}').fetchone()

# 5,6
@app.get("/sales")
async def statistics(category: str):
    app.db_connection.row_factory = sqlite3.Row
    if category == "customers":
        stats = app.db_connection.execute('''
            SELECT c.customerId, email, phone, ROUND(SUM(total),2) AS Sum
            FROM customers c 
                JOIN invoices i ON c.customerId = i.customerId
            GROUP BY c.customerId
            ORDER BY Sum DESC, c.customerId;
            ''').fetchall()
    elif category == "genres":
        stats = app.db_connection.execute('''
            SELECT g.name, SUM(quantity) AS Sum
            FROM genres g 
                JOIN tracks t ON t.genreId = g.genreId
                JOIN invoice_items ii ON ii.trackId = t.trackId
            GROUP BY g.name
            ORDER BY Sum DESC, g.name
            ''').fetchall()
    else:
        raise HTTPException(status_code=404, detail={"error": "Category not found"})
    return stats

