from typing import Dict

from fastapi import FastAPI

from pydantic import BaseModel
from requests import Response
from starlette.status import HTTP_204_NO_CONTENT

app = FastAPI()


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


app.counter = 0


#@app.post("/patient")
#def receive_patient(patient: PatientResponse):
#    app.counter += 1
#    return {"id": app.counter, "patient": patient}

app.patients = []

@app.post("/patient")
def patient_with_saving(patient: PatientResponse):
    app.counter += 1
    app.patients.append(patient)
    return {"id": app.counter, "patient": patient}

@app.get("/patient/{pk}")
def get_patient_by_id(pk: int):
    if pk > app.counter or pk < 0:
        return Response(status_code=HTTP_204_NO_CONTENT)
    else:
        return app.patients[pk-1]