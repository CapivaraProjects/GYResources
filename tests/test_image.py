import json
import pytest
import base64
import models.Image
from flask import Flask
from app import initialize_app
from collections import namedtuple
from tools.Cryptography import Crypto


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
(generic_user, token) = auth(generic_user)


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
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/images/', data=str(
        json.dumps(data)), headers=headers)
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
                "description": 'update',
                "idDisease": image.disease["id"],
                "size": image.size,
                "source": image.source,
                "url": image.url
            }
    generic_image.description = 'update'
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().put('/api/gyresources/images/', data=str(
        json.dumps(image)), headers=headers)
    assert resp.status_code == 200
    img = json.loads(
                resp.get_data(as_text=True))
    img = namedtuple("Image", img.keys())(*img.values())
    assert "update" in img.response['description']


@pytest.mark.order6
def test_delete(generic_image=generic_image):
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
                "source": image.source,
                "url": image.url
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().delete('/api/gyresources/images/', data=str(
        json.dumps(image)), headers=headers)
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
