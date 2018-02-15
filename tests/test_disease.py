import json
import pytest
import base64
import models.Disease
import models.Plant
from flask import Flask
from app import initialize_app
from collections import namedtuple
from tools.Cryptography import Crypto


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_disease = models.Disease.Disease(
        plant=models.Plant.Plant(id=1),
        scientificName="test1",
        commonName="test1",
        images=[])

generic_user = models.User.User(
        idType=1,
        email='test@test.com',
        username='test',
        password='test',
        salt='test',
        dateInsertion='03/02/2018',
        dateUpdate='10/02/2018')


def auth(generic_user=generic_user):
    crypto = Crypto()
    generic_user.salt = crypto.generateRandomSalt()
    generic_user.password = crypto.encrypt(
        generic_user.salt,
        'test')

    data = {'salt': generic_user.salt}
    creds = base64.b64encode(
        bytes(
            generic_user.username+":"+generic_user.password,
            'utf-8')).decode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Basic %s' % creds
    }
    resp = client().post(
        '/api/gyresources/token/',
        headers=headers,
        data=str(
            json.dumps(data)),
        follow_redirects=True)
    resp = json.loads(resp.get_data(as_text=True))
    token = resp['response']
    generic_user.password = 'password'
    return (generic_user, token)


generic_user = models.User.User(
    id=generic_user.id,
    idType=generic_user.idType,
    email=generic_user.email,
    username=generic_user.username,
    password='test',
    salt=generic_user.salt,
    dateInsertion=generic_user.dateInsertion,
    dateUpdate=generic_user.dateUpdate)


@pytest.mark.order1
def test_search_by_unexistent_id():
    data = {
            "action": "searchByID",
            "id": "1000000",
            }
    resp = client().get(
            '/api/gyresources/diseases',
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


@pytest.mark.order3
def test_search():
    data = {
                "action": "search",
                "scientificName": "Venturia",
                "commonName": "Apple",
                "pageSize": 10,
                "offset": 0
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
        assert 'Venturia' in response['scientificName']


@pytest.mark.order4
def test_create(generic_disease=generic_disease, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    aux = generic_disease.plant
    generic_disease.plant = generic_disease.plant.__dict__
    data = generic_disease.__dict__
    data["idPlant"] = aux.id
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/diseases/', data=str(
        json.dumps(data)), headers=headers)
    disease = json.loads(resp.get_data(as_text=True))['response']
    disease = namedtuple("Disease", disease.keys())(*disease.values())
    generic_disease = disease
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(
            resp.get_data(as_text=True))['response']


@pytest.mark.order5
def test_update(generic_disease=generic_disease, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
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
        disease = namedtuple("Text", response.keys())(*response.values())

    disease = {
                "id": disease.id,
                "idPlant": disease.plant["id"],
                "scientificName": disease.scientificName,
                "commonName": 'update',
                "images": disease.images
            }
    generic_disease.commonName = 'update'
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().put('/api/gyresources/diseases/', data=str(
        json.dumps(disease)), headers=headers)
    assert resp.status_code == 200
    disease  = json.loads(
                resp.get_data(as_text=True))
    disease = namedtuple("Text", disease .keys())(*disease .values())
    assert "update" in disease.response['commonName']


@pytest.mark.order6
def test_delete(generic_disease=generic_disease, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
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

    disease = {
                "id": disease.id,
                "idPlant": disease.plant["id"],
                "scientificName": disease.scientificName,
                "commonName": disease.commonName,
                "images": disease.images
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().delete('/api/gyresources/diseases/', data=str(
        json.dumps(disease)), headers=headers)
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
