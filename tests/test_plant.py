import json
import pytest
from flask import Flask
from app import initialize_app
from collections import namedtuple
import models.Plant


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_plant = models.Plant.Plant(
        scientificName='test',
        commonName='test')


@pytest.mark.order1
def test_search_by_unexistent_id():
    data = {
                "action": "searchByID",
                "id": "1000",
            }
    resp = client().get(
            '/api/gyresources/plants',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 500


@pytest.mark.order2
def test_search_by_id():
    data = {
                "action": "searchByID",
                "id": "1",
            }
    resp = client().get(
            '/api/gyresources/plants',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 200
    assert 'Apple' in json.loads(
            resp.get_data(as_text=True))['response']['commonName']


@pytest.mark.order3
def test_search():
    data = {
                "action": "search",
                "scientificName": "Malus domestica",
                "commonName": "Apple"
            }
    resp = client().get(
            '/api/gyresources/plants',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert 'Malus domestica' in response['scientificName']


@pytest.mark.order4
def test_create(generic_plant=generic_plant):
    data = generic_plant.__dict__
    resp = client().post('/api/gyresources/plants/', data=str(
        json.dumps(generic_plant.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    plant = json.loads(
                resp.get_data(as_text=True))['response']
    plant = namedtuple("Plant", plant.keys())(*plant.values())
    generic_plant = plant
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']


@pytest.mark.order5
def test_update(generic_plant=generic_plant):
    data = generic_plant.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/plants',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    plant = object()
    for response in pagedResponse['response']:
        plant = namedtuple("Plant", response.keys())(*response.values())

    plant = {
                "action": "string",
                "id": plant.id,
                "scientificName": 'update',
                "commonName": plant.commonName
            }
    generic_plant.scientificName = 'update'
    resp = client().put('/api/gyresources/plants/', data=str(
        json.dumps(plant)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    plant = json.loads(
                resp.get_data(as_text=True))
    plant = namedtuple("Plant", plant.keys())(*plant.values())
    assert "update" in plant.response['scientificName']


@pytest.mark.order6
def test_delete(generic_plant=generic_plant):
    data = generic_plant.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/plants',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    plant = object()
    for response in pagedResponse['response']:
        plant = namedtuple("Plant", response.keys())(*response.values())

    plant = {
                "action": "string",
                "id": plant.id,
                "scientificName": plant.scientificName,
                "commonName": plant.commonName
            }
    resp = client().delete('/api/gyresources/plants/', data=str(
        json.dumps(plant)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
