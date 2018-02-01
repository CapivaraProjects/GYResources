from flask import Flask
from app import initialize_app
import models.Plant
import json


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client


def test_search_by_id():
    resp = client().get(
            '/api/gyresources/plants/searchById/2',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 5})
    print(json.loads(resp.get_data(as_text=True)))
    assert resp.status_code == 200


def test_create():
    plant = models.Plant.Plant(scientificName='test3', commonName='test3')
    resp = client().post('/api/gyresources/plants/', data=str(
        json.dumps(plant.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']
