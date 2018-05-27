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
def test_create(generic_image=generic_image, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
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
def test_update(generic_image=generic_image, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
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
def test_delete(generic_image=generic_image, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
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
    print(image)
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().delete('/api/gyresources/images/', data=str(
        json.dumps(image)), headers=headers)
    print(resp)
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']


@pytest.mark.order7
def test_read():
    data = {
            "action": "read",
            "id": 3264,
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
    jsonResp = json.loads(resp.get_data(as_text=True))
    assert jsonResp['status_code'] == 200
    assert jsonResp['response']['url'].strip()[-1] == '='


@pytest.mark.order8
def test_save(generic_image=generic_image, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_image.__dict__
    data["idDisease"] = 3
    data["url"] = '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\n3Uobn1EYmDgbSvwJ/9k=\n'
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
    assert "JPG" in json.loads(resp.get_data(as_text=True))['response']['url']


@pytest.mark.order9
def test_search_with_page_size_and_offset():
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
        assert 'PlantVillage' in response['source']


@pytest.mark.order10
def test_create_empty(generic_image=generic_image, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    image = generic_image
    image.url = ''
    image.description = ''
    image.source = ''
    data = image.__dict__
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/images/', data=str(
        json.dumps(data)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500


@pytest.mark.order11
def test_update_wrong_id(generic_image=generic_image, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
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
                "id": 1000000,
                "description": image.description,
                "idDisease": image.disease["id"],
                "size": image.size,
                "source": image.source,
                "url": 'update'
        }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
    }
    resp = client().put('/api/gyresources/images/', data=str(
        json.dumps(image)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']


@pytest.mark.order12
def test_delete_non_existent(generic_image=generic_image, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
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
                "id": 1000,
                "description": image.url,
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
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']
