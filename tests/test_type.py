import json
import pytest
from flask import Flask
from app import initialize_app
from collections import namedtuple
import models.Type


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_type = models.Type.Type(
        value='test',
        description='test')


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
def test_search_by_id():
    data = {
            "action": "searchByID",
            "id": "1",
            }
    resp = client().get(
            '/api/gyresources/types',
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


@pytest.mark.order3
def test_search():
    data = {
                "action": "search",
                "value": "test",
                "description": "test",
                "pageSize": 10,
                "offset": 0
            }
    resp = client().get(
            '/api/gyresources/types',
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


@pytest.mark.order4
def test_create(generic_type=generic_type):
    data = generic_type.__dict__
    resp = client().post('/api/gyresources/types/', data=str(
        json.dumps(data)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    type = json.loads(resp.get_data(as_text=True))['response']
    type = namedtuple("Type", type.keys())(*type.values())
    generic_type = type
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']


@pytest.mark.order5
def test_update(generic_type=generic_type):
    data = generic_type.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/types',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    type = object()
    for response in pagedResponse['response']:
        type = namedtuple("Type", response.keys())(*response.values())

    type = {
                "id": type.id,
                "value": type.value,
                "description": 'update'
            }
    generic_type.description = 'update'
    resp = client().put('/api/gyresources/types/', data=str(
        json.dumps(type)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    type = json.loads(
                resp.get_data(as_text=True))
    type = namedtuple("Type", type.keys())(*type.values())
    assert "update" in type.response['description']

@pytest.mark.order6
def test_delete(generic_type=generic_type):
    data = generic_type.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/types',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    type = object()
    for response in pagedResponse['response']:
        type = namedtuple("Type", response.keys())(*response.values())

    type = {
                "id": type.id,
                "value": type.value,
                "description": type.description
            }

    resp = client().delete('/api/gyresources/types/', data=str(
        json.dumps(type)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
