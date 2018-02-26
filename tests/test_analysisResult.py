import json
import pytest
import base64
import models.AnalysisResult
from flask import Flask
from app import initialize_app
from collections import namedtuple
from tools.Cryptography import Crypto


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_analysisResult = models.AnalysisResult.AnalysisResult(
        id=1,
        idAnalysis=1,
        idDisease=1,
        score=0.000000)

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
            '/api/gyresources/analysisResult',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 500


@pytest.mark.order2
def test_create(generic_analysisResult=generic_analysisResult, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysisResult.__dict__
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/analysisResult/', data=str(
        json.dumps(data)), headers=headers)
    analysisResult = json.loads(resp.get_data(as_text=True))['response']
    analysisResult = namedtuple("AnalysisResult", analysisResult.keys())(*analysisResult.values())
    generic_analysisResult = analysisResult
    assert resp.status_code == 200
    # se o json estiver vazio a condicao eh aceita...
    assert "'id': 0" not in json.loads(
            resp.get_data(as_text=True))['response']


@pytest.mark.order3
def test_search_by_id():
    data = {
            "action": "searchByID",
            "id": 1
            }
    resp = client().get(
            '/api/gyresources/analysisResult',
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
            "idAnalysis": generic_analysisResult.idAnalysis,
            "idDisease": 1,
            "score": generic_analysisResult.score,
            "pageSize": 10,
            "offset": 0	
            }
    resp = client().get(
            '/api/gyresources/analysisResult',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert response['idDisease'] == 1


@pytest.mark.order5
def test_update(generic_analysisResult=generic_analysisResult, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysisResult.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/analysisResult',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    analysisResult = object()
    for response in pagedResponse['response']:
        analysisResult = namedtuple("AnalysisResult", response.keys())(*response.values())
        analysisResult = {
                "id": analysisResult.id,
                "idAnalysis": 9999,
                "idDisease": analysisResult.idDisease,
                "score": 0.9999
                }
    generic_analysisResult.idAnalysis = 9999
    generic_analysisResult.score = 0.9999
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().put('/api/gyresources/analysisResult/', data=str(
        json.dumps(analysisResult)), headers=headers)
    assert resp.status_code == 200
    analysisResult = json.loads(
                resp.get_data(as_text=True))
    analysisResult = namedtuple("AnalysisResult", analysisResult.keys())(*analysisResult.values())
    assert 9999 == analysisResult.response['idAnalysis']


@pytest.mark.order6
def test_update_wrong_id(generic_analysisResult=generic_analysisResult, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysisResult.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/analysisResult',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    analysisResult = object()
    for response in pagedResponse['response']:
        analysisResult = namedtuple("AnalysisResult", response.keys())(*response.values())
        analysisResult = {
                "id": 1000,
                "idAnalysis": analysisResult.idAnalysis, 
                "idDisease": analysisResult.idDisease,
                "score": analysisResult.score
                }

    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().put('/api/gyresources/analysisResult/', data=str(
        json.dumps(analysisResult)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']


@pytest.mark.order7
def test_delete_non_existent(generic_analysisResult=generic_analysisResult, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysisResult.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/analysisResult',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    analysisResult = object()
    for response in pagedResponse['response']:
        analysisResult = namedtuple("AnalysisResult", response.keys())(*response.values())
        analysisResult = {
                "id": 1000,
                "idAnalysis": analysisResult.idAnalysis,
                "idDisease": analysisResult.idDisease,
                "score": analysisResult.score
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    print(str(json.dumps(analysisResult)))
    resp = client().delete('/api/gyresources/analysisResult/', data=str(json.dumps(analysisResult)), headers=headers)
    resp = json.loads(resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']


@pytest.mark.order8
def test_delete(generic_analysisResult=generic_analysisResult, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysisResult.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/analysisResult',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    analysisResult = object()
    for response in pagedResponse['response']:
        analysisResult = namedtuple("AnalysisResult", response.keys())(*response.values())
        analysisResult = {
                "id": analysisResult.id,
                "idAnalysis": analysisResult.idAnalysis,
                "idDisease": analysisResult.idDisease,
                "score": analysisResult.score
                }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().delete('/api/gyresources/analysisResult/', data=str(
        json.dumps(analysisResult)), headers=headers)
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']


@pytest.mark.order9
def test_create_empty(generic_analysisResult=generic_analysisResult, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    analysisResult = generic_analysisResult
    analysisResult.idAnalysis = 0
    analysisResult.idDisease = 0
    analysisResult.score = 0.000000
    data = analysisResult.__dict__
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/analysisResult/', data=str(
        json.dumps(data)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500
