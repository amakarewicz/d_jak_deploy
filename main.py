import secrets
from hashlib import sha256
from typing import Dict

from fastapi import FastAPI, HTTPException, Depends, Response, status, Cookie, Request
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from pydantic import BaseModel

app = FastAPI()
app.patients={}
app.next_patient_id=0
#app.sessions={}

MESSAGE_UNAUTHORIZED = "Log in to access this page."

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


class PatientResponse(BaseModel):
    name: str
    surename: str


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

# @app.post("/patient")
# def add_patient(request: PatientResponse, response: Response ,session_token: str = Cookie(None)):
#     if session_token not in app.session_tokens:
#         raise HTTPException(status_code=401, detail="Login required")
#     app.patients[app.counter] = request.dict()
#     app.counter = app.counter+1
#     response.headers["Location"] = f"/patient/{app.counter-1}"
#     response.status_code = status.HTTP_302_FOUND
#     return response
#
# @app.get("/patient")
# def display_patients(response: Response, session_token: str = Cookie(None)):
#     if session_token not in app.session_tokens:
#        raise HTTPException(status_code=401, detail="Login required")
#     if len(app.patients) != 0:
#         return app.patients
#     response.status_code = status.HTTP_204_NO_CONTENT
#
# @app.get("/patient/{pk}")
# def get_patient_by_id(response: Response, pk: int, session_token: str = Cookie(None)):
#     if session_token not in app.session_tokens:
#         raise HTTPException(status_code=401, detail="Login required")
#     if pk in app.patients:
#         return app.patients[pk]
#     else:
#         raise HTTPException(204, "Such patient doesn't exist")
#
#
# @app.delete("/patient/{pk}")
# def delete_patient(response: Response, pk: int, session_token: str = Cookie(None)):
#     if session_token not in app.session_tokens:
#         raise HTTPException(status_code=401, detail="Login required")
#     if pk in app.patients:
#         app.patients.pop(pk)
#         response.headers["Location"]="/patient"
#         response.status_code = status.HTTP_302_FOUND
#         return response
#     else:
#         raise HTTPException(204)


class PatientRq(BaseModel):
    name: str
    surname: str

@app.post("/patient")
def add_patient(response: Response, rq: PatientRq, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    pid=f"id_{app.next_patient_id}"
    app.patients[pid]=rq.dict()
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = f"/patient/{pid}"
    app.next_patient_id+=1

@app.get("/patient")
def get_all_patients(response: Response, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    if len(app.patients) != 0:
        return app.patients
    response.status_code = status.HTTP_204_NO_CONTENT

@app.get("/patient/{pid}")
def get_patient(pid: str, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    if pid in app.patients:
        return app.patients[pid]
    response.status_code = status.HTTP_204_NO_CONTENT

@app.delete("/patient/{pid}")
def remove_patient(pid: str, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    app.patients.pop(pid, None)
    response.status_code = status.HTTP_204_NO_CONTENT