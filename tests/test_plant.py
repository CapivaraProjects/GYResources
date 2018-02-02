import json
import pytest
from flask import Flask
from app import initialize_app
from collections import namedtuple
import models.Plant


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_plant = models.Plant.Plant(scientificName='test3', commonName='test3')


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
                "id": "23",
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
    assert 'Strawberry' in json.loads(
            resp.get_data(as_text=True))['response']['commonName']


@pytest.mark.order3
def test_search():
    data = {
                "action": "search",
                "commonName": "Apple",
                "scientificName": "Malus"
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
        assert 'Apple' in response['commonName']


@pytest.mark.order4
def test_create(generic_plant=generic_plant):
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

    plant = models.Plant.Plant(
                id=plant.id,
                scientificName=plant.scientificName,
                commonName=plant.commonName)
    plant.scientificName = 'test4'
    resp = client().put('/api/gyresources/plants/', data=str(
        json.dumps(plant.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    plant = json.loads(
                resp.get_data(as_text=True))
    plant = namedtuple("Plant", plant.keys())(*plant.values())
    assert "test4" in plant.response['scientificName']


@pytest.mark.order6
def test_delete():
    print(str(generic_plant.__dict__))
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

    plant = models.Plant.Plant(
                id=plant.id,
                scientificName=plant.scientificName,
                commonName=plant.commonName)
    print('delete' + str(plant.__dict__))
    resp = client().delete('/api/gyresources/plants/', data=str(
        json.dumps(plant.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
