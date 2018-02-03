import json
import pytest
from flask import Flask
from app import initialize_app
from collections import namedtuple
import models.Image


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_image = models.Image.Image(
        disease=models.Disease.Disease(
            id=1,
            plant=models.Plant.Plant().__dict__,
            scientificName='<i>Venturia inaequalis </i>',
            commonName='Apple scab').__dict__,
        url='test',
        description='services',
        source='',
        size=1)


@pytest.mark.order1
def test_search_by_unexistent_id():
    data = {
            "action": "searchByID",
            "id": "1000000",
            }
    resp = client().get(
            '/api/gyresources/images',
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
            '/api/gyresources/images',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 200
    assert 'JPG' in json.loads(
            resp.get_data(as_text=True))['response']['url']


@pytest.mark.order3
def test_search():
    data = {
            "action": "search",
            "url": "DSC04057_resized.JPG",
            "description": "Healthy leaf, photographed in field/outside, " +
            "Rock Springs Research Center, Penn State, PA",
            "source": "PlantVillage",
            "pageSize": 10,
            "offset": 0
            }
    resp = client().get(
            '/api/gyresources/images',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert 'JPG' in response['url']


@pytest.mark.order4
def test_create(generic_image=generic_image):
    data = generic_image.__dict__
    data["idDisease"] = generic_image.disease['id']
    data["action"] = 'create'
    resp = client().post('/api/gyresources/images/', data=str(
        json.dumps(data)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    img = json.loads(
                resp.get_data(as_text=True))['response']
    img = namedtuple("Image", img.keys())(*img.values())
    generic_image = img
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']


@pytest.mark.order5
def test_update(generic_image=generic_image):
    data = generic_image.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/images',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    image = object()
    for response in pagedResponse['response']:
        image = namedtuple("Image", response.keys())(*response.values())

    image = {
                "id": image.id,
                "description": image.description,
                "idDisease": image.disease["id"],
                "size": image.size,
                "source": 'test',
                "url": 'test4'
            }

    resp = client().put('/api/gyresources/images/', data=str(
        json.dumps(image)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    img = json.loads(
                resp.get_data(as_text=True))
    img = namedtuple("Image", img.keys())(*img.values())
    assert "test4" in img.response['url']


@pytest.mark.order6
def test_delete():
    data = generic_image.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/images',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    image = object()
    for response in pagedResponse['response']:
        image = namedtuple("Image", response.keys())(*response.values())

    image = {
                "action": "string",
                "description": "string",
                "id": image.id,
                "idDisease": image.disease["id"],
                "size": 0,
                "source": "string",
                "url": "string"
            }
    resp = client().delete('/api/gyresources/images/', data=str(
        json.dumps(image)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
