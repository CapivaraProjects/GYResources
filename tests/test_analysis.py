import json
import pytest
import base64
import models.Analysis
import models.Image
import models.Classifier
from flask import Flask
from app import initialize_app
from collections import namedtuple
from tools.Cryptography import Crypto


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_analysis = models.Analysis.Analysis(
        id=1,
        image = models.Image.Image(id=3264),
        classifier = models.Classifier.Classifier(id=1))

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

@pytest.mark.order1
def test_search_by_unexistent_id():
    data = {
            "action": "searchByID",
            "id": 1000
            }
    resp = client().get(
            '/api/gyresources/analysis',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 500

@pytest.mark.order2
def test_create(generic_analysis=generic_analysis, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = {}
    data["id"] = generic_analysis.id
    data["idImage"] = generic_analysis.image.id
    data["idClassifier"] = generic_analysis.classifier.id
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/analysis/', data=str(
        json.dumps(data)), headers=headers)
    analysis = json.loads(resp.get_data(as_text=True))['response']
    analysis = namedtuple("Analysis", analysis.keys())(*analysis.values())
    generic_analysis = analysis
    assert resp.status_code == 200
    assert "'id': 1" not in json.loads(
            resp.get_data(as_text=True))['response']


@pytest.mark.order3
def test_search_by_id():
    data = {
                "action": "searchByID",
                "id": 1
            }
    resp = client().get(
            '/api/gyresources/analysis',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 200


@pytest.mark.order4
def test_search():
    data = {
                "action": "search",
                "idImage": 1,
                "idClassifier": 1,
                "pageSize": 10,
                "offset": 0
            }
    resp = client().get(
            '/api/gyresources/analysis',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert response['image']['id'] == 1


@pytest.mark.order5
def test_update(generic_analysis=generic_analysis, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysis.__dict__
    data['action'] = 'searchByID'
    resp = client().get(
            '/api/gyresources/analysis',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    get_response = json.loads(resp.get_data(as_text=True))
    get_response = namedtuple("Analysis", get_response.keys())(*get_response.values())
    analysis = {
            "id": get_response.response["id"],
            "idImage": 2,
            "idClassifier": get_response.response["classifier"]["id"]
            }
    generic_analysis.image.id = 2
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().put('/api/gyresources/analysis/', data=str(
        json.dumps(analysis)), headers=headers)
    assert resp.status_code == 200
    analysis = json.loads(
                resp.get_data(as_text=True))
    analysis = namedtuple("Analysis", analysis.keys())(*analysis.values())
    assert 2 == analysis.response["image"]['id']

@pytest.mark.order6
def test_update_wrong_id(generic_analysis=generic_analysis, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysis.__dict__
    data['action'] = 'searchByID'
    resp = client().get(
            '/api/gyresources/analysis',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    get_response = json.loads(resp.get_data(as_text=True))
    get_response = namedtuple("Analysis", get_response.keys())(*get_response.values())
    analysis = {
            "id": 1000,
            "idImage": get_response.response['image']['id'],
            "idClassifier": get_response.response["classifier"]["id"]
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().put('/api/gyresources/analysis/', data=str(
        json.dumps(analysis)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']


@pytest.mark.order7
def test_search_with_page_size_and_offset():
    data = {
                "action": "search",
                "idImage": 2,
                "idClassifier": 1,
                "pageSize": 10,
                "offset": 0
            }
    resp = client().get(
            '/api/gyresources/analysis',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert response['image']['id'] == 2

@pytest.mark.order8
def test_delete_non_existent(generic_analysis=generic_analysis, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysis.__dict__
    data['action'] = 'searchByID'
    resp = client().get(
            '/api/gyresources/analysis',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    get_response = json.loads(resp.get_data(as_text=True))
    get_response = namedtuple("Analysis", get_response.keys())(*get_response.values())
    analysis = {
            "id": 1000,
            "idImage": get_response.response['image']['id'],
            "idClassifier": get_response.response['classifier']['id']
        }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().delete('/api/gyresources/analysis/', data=str(json.dumps(analysis)), headers=headers)
    resp = json.loads(resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']


@pytest.mark.order9
def test_delete(generic_analysis=generic_analysis, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysis.__dict__
    data['action'] = 'searchByID'
    resp = client().get(
            '/api/gyresources/analysis',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    get_response = json.loads(resp.get_data(as_text=True))
    get_response = namedtuple("Analysis", get_response.keys())(*get_response.values())
    analysis = {
            "id": get_response.response['id'],
            "idImage": get_response.response['image']['id'],
            "idClassifier": get_response.response['classifier']['id']
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().delete('/api/gyresources/analysis/', data=str(
        json.dumps(analysis)), headers=headers)

    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']


@pytest.mark.order10
def test_create_empty(generic_analysis=generic_analysis, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = {}
    data["id"] = 0
    data["idImage"] = 0
    data["idClassifier"] = 0
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/analysis/', data=str(
        json.dumps(data)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500
