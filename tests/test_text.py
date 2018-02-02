import json
import pytest
from flask import Flask
from app import initialize_app
from collections import namedtuple
import models.Text


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_text = models.Text.Text(language='test language', tag='test tag', value='test value', description='test description')

@pytest.mark.order1
def test_create(generic_text=generic_text):
    resp = client().post('/api/gyresources/texts/', data=str(
        json.dumps(generic_text.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    text = json.loads(resp.get_data(as_text=True))['response']
    text = namedtuple("Text", text.keys())(*text.values())
    generic_text = text
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(resp.get_data(as_text=True))['response']

@pytest.mark.order2
def test_search():
    data = {
                "action": "search",
                "language": "test language",
                "tag": "test tag",
                "value": "test value",
                "description": "test description"
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
        assert 'test value' in response['value']

@pytest.mark.order3
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

    text = models.Text.Text(
                id=text.id,
                language=text.language,
                tag=text.tag,
                value=text.value,
                description=text.description)
    text.tag = 'test tag update'
    resp = client().put('/api/gyresources/texts/', data=str(
        json.dumps(text.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    text = json.loads(
                resp.get_data(as_text=True))
    text = namedtuple("Text", text.keys())(*text.values())
    assert "test tag update" in text.response['tag']

@pytest.mark.order4
def test_delete():
    print(str(generic_text.__dict__))
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

    text = models.Text.Text(
                id=text.id,
                language=text.language,
                tag=text.tag,
                value=text.value,
                description=text.description)
    print('delete' + str(text.__dict__))
    resp = client().delete('/api/gyresources/texts/', data=str(
        json.dumps(text.__dict__)), headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']
