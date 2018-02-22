import json
import pytest
import base64
import models.User
from flask import Flask
from app import initialize_app
from collections import namedtuple
from tools.Cryptography import Crypto


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client()
generic_user = models.User.User(
        idType=1,
        email='test@test.com',
        username='test',
        password='test',
        salt='test',
        dateInsertion='03/02/2018',
        dateUpdate='10/02/2018')


@pytest.mark.order1
def test_search_by_unexistent_id():
    data = {
            "action": "searchByID",
            "id": "1000000",
            }
    resp = client.get(
            '/api/gyresources/users',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 500


@pytest.mark.order2
def test_create(generic_user=generic_user):
    crypto = Crypto()
    generic_user.salt = crypto.generateRandomSalt()
    generic_user.password = crypto.encrypt(
            generic_user.salt,
            generic_user.password)
    data = generic_user.__dict__
    resp = client.post('/api/gyresources/users/', data=str(
        json.dumps(data)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})

    user = json.loads(resp.get_data(as_text=True))['response']
    user['password'] = generic_user.password
    user['salt'] = generic_user.salt
    user = namedtuple("User", user.keys())(*user.values())
    generic_user = user
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']
    return generic_user


@pytest.mark.order3
def test_auth(generic_user=generic_user):
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
    resp = client.post(
        '/api/gyresources/token/',
        headers=headers,
        data=str(
            json.dumps(data)),
        follow_redirects=True)
    resp = json.loads(resp.get_data(as_text=True))
    token = resp['response']
    generic_user.password = 'password'
    assert token
    return (generic_user, token)


aux = models.User.User(
        idType=1,
        email='test@test.com',
        username='username',
        password='test',
        salt='test',
        dateInsertion='03/02/2018',
        dateUpdate='10/02/2018')
generic_user = test_create(generic_user=aux)
generic_user = models.User.User(
    id=generic_user.id,
    idType=generic_user.idType,
    email=generic_user.email,
    username=generic_user.username,
    password='test',
    salt=generic_user.salt,
    dateInsertion=generic_user.dateInsertion,
    dateUpdate=generic_user.dateUpdate)
(generic_user, token) = test_auth(generic_user)


@pytest.mark.order4
def test_search(generic_user=generic_user, client=client, token=token):
    data = {
            "action": "search",
            "idType": generic_user.idType,
            "email": generic_user.email,
            "username": generic_user.username,
            "password": generic_user.password,
            "salt": generic_user.salt,
            "dateInsertion": generic_user.dateInsertion,
            "dateUpdate": generic_user.dateUpdate,
            "pageSize": 10,
            "offset": 0
            }
    headers = {
       'Content-Type': 'application/json',
       'Accept': 'application/json',
       'Authorization': 'Basic %s' % token
    }
    resp = client.get(
         '/api/gyresources/users',
         headers=headers,
         content_type='application/json',
         query_string=data,
         follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert 'test@test.com' in response['email']


@pytest.mark.order5
def test_update(generic_user=generic_user, token=token):
    data = generic_user.__dict__
    data['action'] = 'search'
    resp = client.get(
            '/api/gyresources/users',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    user = object()
    for response in pagedResponse['response']:
        user = namedtuple("User", response.keys())(*response.values())

    crypto = Crypto()
    user = models.User.User(
            id=user.id,
            idType=user.idType,
            email=user.email,
            username=user.username,
            password='password',
            salt=crypto.generateRandomSalt(),
            dateInsertion=user.dateInsertion,
            dateUpdate=user.dateUpdate)
    user.password = crypto.encrypt(
            user.salt,
            user.password)
    user.username = 'username2'
    headers = {
       'Content-Type': 'application/json',
       'Accept': 'application/json',
       'Authorization': 'Bearer %s' % token['token']
    }
    resp = client.put('/api/gyresources/users/', data=str(
        json.dumps(user.__dict__)), headers=headers)
    assert resp.status_code == 200
    user = json.loads(
            resp.get_data(as_text=True))
    user = namedtuple("User", user.keys())(*user.values())
    assert "username2" in user.response['username']


@pytest.mark.order6
def test_search_by_id(generic_user=generic_user, client=client, token=token):
    data = {
            "action": "searchByID",
            "id": generic_user.id
            }
    headers = {
       'Content-Type': 'application/json',
       'Accept': 'application/json',
       'Authorization': 'Basic %s' % token
    }
    resp = client.get(
         '/api/gyresources/users',
         headers=headers,
         content_type='application/json',
         query_string=data,
         follow_redirects=True)
    baseResponse = json.loads(resp.get_data(as_text=True))
    assert baseResponse['status_code'] == 200


@pytest.mark.order7
def test_create_empty():
    user = models.User.User()
    user.email = ''
    user.username = ''
    data = user.__dict__
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            }
    resp = client.post('/api/gyresources/users/', data=str(
        json.dumps(data)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500


@pytest.mark.order8
def test_update_wrong_id(
        generic_user=generic_user, token=token):
    data = generic_user.__dict__
    data['action'] = 'search'
    resp = client.get(
            '/api/gyresources/users',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    user = object()
    for response in pagedResponse['response']:
        user = namedtuple("User", response.keys())(*response.values())

    user = {
                "action": "string",
                "id": 1000,
                'idType': user.idType,
                'email': user.email,
                'username': user.username,
                'password': user.password,
                'salt': user.salt,
                'dateInsertion': user.dateInsertion,
                'dateUpdate': user.dateUpdate
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client.put('/api/gyresources/users/', data=str(
        json.dumps(user)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']


@pytest.mark.order9
def test_delete_non_existent(
        user=generic_user, token=token):
    user = {
                "action": "string",
                "id": 1000,
                'idType': user.idType,
                'email': user.email,
                'username': user.username,
                'password': user.password,
                'salt': user.salt,
                'dateInsertion': user.dateInsertion,
                'dateUpdate': user.dateUpdate
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client.delete('/api/gyresources/users/', data=str(
        json.dumps(user)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    print(str(resp))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']


@pytest.mark.order10
def test_delete(token=token):
    data = generic_user.__dict__
    data['action'] = 'search'
    resp = client.get(
            '/api/gyresources/users',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    user = object()
    for response in pagedResponse['response']:
        user = namedtuple("User", response.keys())(*response.values())

    user = models.User.User(
            id=user.id,
            idType=user.idType,
            email=user.email,
            username=user.username,
            password='password',
            salt=user.salt,
            dateInsertion=user.dateInsertion,
            dateUpdate=user.dateUpdate)
    headers = {
       'Content-Type': 'application/json',
       'Accept': 'application/json',
       'Authorization': 'Bearer %s' % token['token']
    }
    resp = client.delete('/api/gyresources/users/', data=str(
        json.dumps(user.__dict__)), headers=headers)
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']


@pytest.mark.order11
def test_wrong_auth(generic_user=generic_user):
    crypto = Crypto()
    generic_user.salt = crypto.generateRandomSalt()
    generic_user.password = crypto.encrypt(
        generic_user.salt,
        'test')

    data = {'salt': generic_user.salt}
    creds = base64.b64encode(
        bytes(
            "wrong:"+generic_user.password,
            'utf-8')).decode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Basic %s' % creds
    }
    resp = client.post(
        '/api/gyresources/token/',
        headers=headers,
        data=str(
            json.dumps(data)),
        follow_redirects=True)
    resp = json.loads(resp.get_data(as_text=True))
    assert resp['status_code'] == 401


@pytest.mark.order12
def test_wrong_token(
        user=generic_user, token=token):
    user = {
                "action": "string",
                "id": 1000,
                'idType': user.idType,
                'email': user.email,
                'username': user.username,
                'password': user.password,
                'salt': user.salt,
                'dateInsertion': user.dateInsertion,
                'dateUpdate': user.dateUpdate
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer wrongToken'
            }
    resp = client.delete('/api/gyresources/users/', data=str(
        json.dumps(user)), headers=headers)
    assert 'UNAUTHORIZED' in str(resp)


@pytest.mark.order13
def test_unhandled_exception():
    resp = client.get('/api/gyresources/token/')
    assert 'unhandled exception' in str(resp)
