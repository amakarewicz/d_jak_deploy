from fastapi.testclient import TestClient
import pytest
from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World during the coronavirus pandemic!"}


@pytest.mark.parametrize("name", ['Kasia', 'Ola', 'Jacek'])
def test_hello_name(name):
    response = client.get(f"/hello/{name}")
    assert response.status_code == 200
    assert response.json() == {'msg': f"Hello {name}"}


def test_receive_something():
    response = client.post("/whatever", json={'first_key': 'some_value'})
    assert response.json() == {"received": {'first_key': 'some_value'},
                             "constant_data": "python jest super"}


def test_method_get():
	response = client.get("/method")
	assert response.status_code == 200
	assert response.json() == {"method":"GET"}

def test_method_post():
	response = client.post("/method")
	assert response.status_code == 200
	assert response.json() == {"method":"POST"}

def test_method_put():
	response = client.put("/method")
	assert response.status_code == 200
	assert response.json() == {"method":"PUT"}

def test_method_delete():
	response = client.delete("/method")
	assert response.status_code == 200
	assert response.json() == {"method":"DELETE"}
	