import json
import pytest
from flask import Flask
from app import initialize_app
from collections import namedtuple
import models.Disease
import models.Plant


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_disease = models.Disease.Disease(
        plant=models.Plant.Plant(),
        scientificName="test1",
        commonName="test1",
        images=[])


@pytest.mark.order1
def test_create(generic_disease=generic_disease):
    aux = generic_disease.plant
    generic_disease.plant = generic_disease.plant.__dict__
    data = generic_disease.__dict__
    data["idPlant"] = aux.id
    resp = client().post('/api/gyresources/diseases/', data=str(
        json.dumps(data)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    disease = json.loads(resp.get_data(as_text=True))['response']
    disease = namedtuple("Disease", disease.keys())(*disease.values())
    generic_disease = disease
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(
            resp.get_data(as_text=True))['response']


@pytest.mark.order2
def test_search():
    data = {
                "action": "search",
                "scientificName": "Venturia",
                "commonName": "Apple",
            }
    resp = client().get(
            '/api/gyresources/diseases',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert 'inaequalis' in response['scientificName']


@pytest.mark.order3
def test_update(generic_disease=generic_disease):
    data = generic_disease.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/diseases',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    disease = object()
    for response in pagedResponse['response']:
        disease = namedtuple("Disease", response.keys())(*response.values())

    disease = models.Disease.Disease(
            id=disease.id,
            plant=disease.plant,
            scientificName=disease.scientificName,
            commonName=disease.commonName,
            images=disease.images)
    disease.commonName = 'test update'
    data = disease.__dict__
    data['idPlant'] = disease.plant['id']
    resp = client().put('/api/gyresources/diseases/', data=str(
        json.dumps(data)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    disease = json.loads(
                resp.get_data(as_text=True))
    disease = namedtuple("Disease", disease.keys())(*disease.values())
    assert "test update" in disease.response['commonName']


@pytest.mark.order4
def test_delete():
    print(str(generic_disease.__dict__))
    data = generic_disease.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/diseases',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    disease = object()
    for response in pagedResponse['response']:
        disease = namedtuple("Disease", response.keys())(*response.values())

    disease = models.Disease.Disease(
            id=disease.id,
            plant=disease.plant,
            scientificName=disease.scientificName,
            commonName=disease.commonName,
            images=disease.images)
    data = disease.__dict__
    data['idPlant'] = disease.plant['id']
    resp = client().delete('/api/gyresources/diseases/', data=str(
        json.dumps(data)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']


@pytest.mark.order5
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
