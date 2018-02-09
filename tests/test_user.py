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
        idType=1, email='test@hotmail.com',
        username='username', password='password',
        salt='salt', dateInsertion='03/02/2018',
        dateUpdate='04/02/2018')


@pytest.mark.order1
def test_create(generic_user=generic_user):
    crypto = Crypto()
    generic_user.salt = crypto.generateRandomSalt()
    generic_user.password = crypto.encrypt(
            generic_user.salt,
            generic_user.password)
    resp = client.post('/api/gyresources/users/', data=str(
        json.dumps(generic_user.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})

    user = json.loads(resp.get_data(as_text=True))['response']
    user = namedtuple("User", user.keys())(*user.values())
    generic_user = user
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']


@pytest.mark.order2
def test_search(generic_user=generic_user, client=client):
    data = {
            "action": "search",
            "idType": generic_user.idType,
            "email": generic_user.email,
            "username": generic_user.username,
            "password": generic_user.password,
            "salt": generic_user.salt,
            "dateInsertion": generic_user.dateInsertion,
            "dateUpdate": generic_user.dateUpdate
            }
    creds = base64.b64encode(
                bytes(
                    generic_user.username + ":" + generic_user.password,
                    'utf-8')).decode('utf-8')
    headers = {
       'Content-Type': 'application/json',
       'Accept': 'application/json',
       'Authorization': 'Basic %s' % creds
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
        assert 'test@hotmail.com' in response['email']


@pytest.mark.order3
def test_update(generic_user=generic_user):
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
    creds = base64.b64encode(
                bytes(
                    user.username + ":" + user.password,
                    'utf-8')).decode('utf-8')
    user.username = 'username2'
    headers = {
       'Content-Type': 'application/json',
       'Accept': 'application/json',
       'Authorization': 'Basic %s' % creds
    }
    resp = client.put('/api/gyresources/users/', data=str(
        json.dumps(user.__dict__)), headers=headers)
    assert resp.status_code == 200
    user = json.loads(
            resp.get_data(as_text=True))
    user = namedtuple("User", user.keys())(*user.values())
    assert "username2" in user.response['username']


@pytest.mark.order4
def test_delete():
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
            salt=user.salt,
            dateInsertion=user.dateInsertion,
            dateUpdate=user.dateUpdate)
    user.salt = crypto.generateRandomSalt()
    user.password = crypto.encrypt(
            user.salt,
            user.password)
    creds = base64.b64encode(
                bytes(
                    user.username + ":" + user.password,
                    'utf-8')).decode('utf-8')
    headers = {
       'Content-Type': 'application/json',
       'Accept': 'application/json',
       'Authorization': 'Basic %s' % creds
    }
    resp = client.delete('/api/gyresources/users/', data=str(
        json.dumps(user.__dict__)), headers=headers)
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
