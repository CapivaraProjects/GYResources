import json
import pytest
from flask import Flask
from app import initialize_app
from collections import namedtuple
import models.User


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
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
    resp = client().get(
            '/api/gyresources/users',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 500


@pytest.mark.order3
def test_search_by_id():
    data = {
            "action": "searchByID",
            "id": "1",
            }
    resp = client().get(
            '/api/gyresources/users',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 200
    assert 'thumb' in json.loads(
            resp.get_data(as_text=True))['response']['value']


@pytest.mark.order4
def test_search():
    data = {
                "action": "search",
                "idType": 1,
                "email": "test@test.com",
                "username": "test",
                "password": "test",
                "salt": "test",
                "dateInsertion": "03/02/2018",
                "dateUpdate": "10/02/2018",
                "pageSize": 10,
                "offset": 0
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
        assert 'test' in response['password']

@pytest.mark.order2
def test_create(generic_user=generic_user):
    data = generic_user.__dict__
    resp = client().post('/api/gyresources/users/', data=str(
        json.dumps(data)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    user = json.loads(resp.get_data(as_text=True))['response']
    user = namedtuple("User", user.keys())(*user.values())
    generic_user = user
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']


@pytest.mark.order5
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

    user = {
                "id": user.id,
                "idType": user.idType,
                "email": user.email,
                "username": 'update',
                "password": user.password,
                "salt": user.salt,
                "dateInsertion": user.dateInsertion,
                "dateUpdate": user.dateUpdate
            }
    generic_user.username = 'update'
    resp = client().put('/api/gyresources/users/', data=str(
        json.dumps(user)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    user = json.loads(
                resp.get_data(as_text=True))
    user = namedtuple("User", user.keys())(*user.values())
    assert "update" in user.response['username']

@pytest.mark.order6
def test_delete(generic_user=generic_user):
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

    user = {
                "id": user.id,
                "idType": user.idType,
                "email": user.email,
                "username": user.username,
                "password": user.password,
                "salt": user.salt,
                "dateInsertion": user.dateInsertion,
                "dateUpdate": user.dateUpdate
            }

    resp = client().delete('/api/gyresources/users/', data=str(
        json.dumps(user)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
