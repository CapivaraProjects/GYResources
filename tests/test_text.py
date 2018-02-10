import json
import pytest
from flask import Flask
from app import initialize_app
from collections import namedtuple
import models.Text


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_text_id = 0
generic_text = models.Text.Text(
        language='test',
        tag='test',
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
def test_create(generic_text=generic_text):
    data = generic_text.__dict__
    resp = client().post('/api/gyresources/texts/', data=str(
        json.dumps(data)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
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
def test_update(generic_text=generic_text):
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
    resp = client().put('/api/gyresources/texts/', data=str(
        json.dumps(text)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})

    assert resp.status_code == 200
    text = json.loads(resp.get_data(as_text=True))
    text = namedtuple("Text", text.keys())(*text.values())
    assert "update" in text.response['tag']


@pytest.mark.order6
def test_delete(generic_text=generic_text):
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
    resp = client().delete('/api/gyresources/texts/', data=str(
        json.dumps(text)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
