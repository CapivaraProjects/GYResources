import json
import pytest
from flask import Flask
from app import initialize_app
from collections import namedtuple
import models.User


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_user = models.User.User(idType=1, email='test@hotmail.com',
                                username='username test', password='password test',
                                salt='salt test', dateInsertion='03/02/2018',
                                dateUpdate='04/02/2018')

@pytest.mark.order1
def test_create(generic_user=generic_user):
    resp = client().post('/api/gyresources/users/', data=str(
        json.dumps(generic_user.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    user = json.loads(resp.get_data(as_text=True))['response']
    user = namedtuple("User", user.keys())(*user.values())
    generic_user = user
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']

@pytest.mark.order2
def test_search():
    data = {
                "action": "search",
                "idType": "1",
                "email": "test@hotmail.com",
                "username": "username test",
                "password": "password test",
                "salt": "salt test",
                "dateInsertion": "03/02/2018",
                "dateUpdate": "04/02/2018"
            }
    resp = client().get(
            '/api/gyresources/users',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert 'test@hotmail.com' in response['email']

@pytest.mark.order3
def test_update(generic_user=generic_user):
    data = generic_user.__dict__
    data['action'] = 'search'
    resp = client().get(
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
                password=user.password,
                salt=user.salt,
                dateInsertion=user.dateInsertion,
                dateUpdate=user.dateUpdate)
    user.username = 'username update'
    resp = client().put('/api/gyresources/users/', data=str(
        json.dumps(user.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    user = json.loads(
                resp.get_data(as_text=True))
    user = namedtuple("User", user.keys())(*user.values())
    assert "username update" in user.response['username']

@pytest.mark.order4
def test_delete():
    print(str(generic_user.__dict__))
    data = generic_user.__dict__
    data['action'] = 'search'
    resp = client().get(
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
                password=user.password,
                salt=user.salt,
                dateInsertion=user.dateInsertion,
                dateUpdate=user.dateUpdate)
    print('delete' + str(user.__dict__))
    resp = client().delete('/api/gyresources/users/', data=str(
        json.dumps(user.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
