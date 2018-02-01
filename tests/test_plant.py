from flask import Flask
from app import initialize_app
import models.Plant
import json


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client


def test_search_by_unexistent_id():
    resp = client().get(
            '/api/gyresources/plants/searchByID/1000',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240})
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 500


def test_search_by_id():
    resp = client().get(
            '/api/gyresources/plants/searchByID/23',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240})
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 200
    assert 'Strawberry' in json.loads(
            resp.get_data(as_text=True))['response']['commonName']


def test_search():
    data = {
                "commonName": "Apple",
                "scientificName": "Malus"
            }
    resp = client().get(
            '/api/gyresources/plants/search/0',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert 'Apple' in response['commonName']


def test_create():
    plant = models.Plant.Plant(scientificName='test3', commonName='test3')
    resp = client().post('/api/gyresources/plants/', data=str(
        json.dumps(plant.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']


def test_update():
    plant = models.Plant.Plant(
            id=24,
            scientificName='test4',
            commonName='test3')
    resp = client().put('/api/gyresources/plants/', data=str(
        json.dumps(plant.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert "test4" in json.loads(
            resp.get_data(as_text=True))['response']['scientificName']


def test_delete():
    plant = models.Plant.Plant(
            id=24,
            scientificName='test3',
            commonName='test3')
    resp = client().delete('/api/gyresources/plants/', data=str(
        json.dumps(plant.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
