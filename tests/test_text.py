import json
import pytest
import base64
import models.Text
from flask import Flask
from app import initialize_app
from collections import namedtuple
from tools.Cryptography import Crypto


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_text_id = 0
generic_text = models.Text.Text(
        language='test',
        tag='test',
        value='test',
        description='test')

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
            '/api/gyresources/texts',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 500


@pytest.mark.order2
def test_create(generic_text=generic_text, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_text.__dict__
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/texts/', data=str(
        json.dumps(data)), headers=headers)
    text = json.loads(resp.get_data(as_text=True))['response']
    text = namedtuple("Text", text.keys())(*text.values())
    generic_text = text
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']


@pytest.mark.order3
def test_search_by_id():
    data = {
            "action": "searchByID",
            "id": "1"
            }
    resp = client().get(
            '/api/gyresources/texts',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 200
    assert 'test' in json.loads(
            resp.get_data(as_text=True))['response']['language']


@pytest.mark.order4
def test_search():
    data = {
            "action": "search",
            "language": "test",
            "tag": "test",
            "value": "test",
            "description": "test",
            "pageSize": 10,
            "offset": 0
            }
    resp = client().get(
            '/api/gyresources/texts',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert 'test' in response['value']


@pytest.mark.order5
def test_update(generic_text=generic_text, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_text.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/texts',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    text = object()

    for response in pagedResponse['response']:
        text = namedtuple("Text", response.keys())(*response.values())

    text = {
                "id": text.id,
                "language": text.language,
                "tag": 'update',
                "value": text.value,
                "description": text.description
            }
    generic_text.tag = 'update'
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().put('/api/gyresources/texts/', data=str(
        json.dumps(text)), headers=headers)

    assert resp.status_code == 200
    text = json.loads(resp.get_data(as_text=True))
    text = namedtuple("Text", text.keys())(*text.values())
    assert "update" in text.response['tag']


@pytest.mark.order6
def test_search_with_page_size_and_offset():
    data = {
                "action": "search",
                "language": "test",
                "tag": "test",
                "value": "test",
                "description": "test",
                "pageSize": 10,
                "offset": 0
            }
    resp = client().get(
            '/api/gyresources/texts',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert 'test' in response['description']


@pytest.mark.order7
def test_delete(generic_text=generic_text, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_text.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/texts',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    text = object()

    for response in pagedResponse['response']:
        text = namedtuple("Text", response.keys())(*response.values())

    text = {
                "id": text.id,
                "language": text.language,
                "tag": text.tag,
                "value": text.value,
                "description": text.description
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().delete('/api/gyresources/texts/', data=str(
        json.dumps(text)), headers=headers)
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']


@pytest.mark.order8
def test_create_empty(generic_text=generic_text, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    text = generic_text
    text.value = ''
    text.description = ''
    data = text.__dict__
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token['token']
        }
    resp = client().post('/api/gyresources/texts/', data=str(
        json.dumps(data)), headers=headers)
    resp = json.loads(
        resp.get_data(as_text=True))
    assert resp['status_code'] == 500


@pytest.mark.order9
def test_update_wrong_id(generic_text=generic_text, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_text.__dict__
    data['action'] = 'search'
    resp = client().get(
        '/api/gyresources/texts',
        content_type='application/json',
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'dataType': 'json'},
        query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    text = object()
    for response in pagedResponse['response']:
        text = namedtuple("Text", response.keys())(*response.values())

    text = {
        "id": 1000,
        "language": text.language,
        "tag": text.tag,
        "value": text.value,
        "description": 'update'
    }
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token['token']
    }
    resp = client().put('/api/gyresources/texts/', data=str(
        json.dumps(text)), headers=headers)
    resp = json.loads(
        resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']


@pytest.mark.order10
def test_delete_non_existent(generic_text=generic_text, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_text.__dict__
    data['action'] = 'search'
    resp = client().get(
        '/api/gyresources/texts',
        content_type='application/json',
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'dataType': 'json'},
        query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    text = object()
    for response in pagedResponse['response']:
        text = namedtuple("Text", response.keys())(*response.values())

    text = {
        "id": 1000,
        "language": text.language,
        "tag": text.tag,
        "value": text.value,
        "description": text.description
    }
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token['token']
    }
    resp = client().delete('/api/gyresources/texts/', data=str(
        json.dumps(text)), headers=headers)
    resp = json.loads(
        resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']
