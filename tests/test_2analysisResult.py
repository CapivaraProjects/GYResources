import json
import pytest
import base64
import models.AnalysisResult
import models.Analysis
import models.Classifier
import models.Image
import models.Disease
import models.Plant
from flask import Flask
from app import initialize_app
from collections import namedtuple
from tools.Cryptography import Crypto


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_analysisResult = models.AnalysisResult.AnalysisResult(
        id=1,
        analysis=models.Analysis.Analysis(id=1),
        disease=models.Disease.Disease(id=1),
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
    data = {}
    data["id"] = generic_analysisResult.id
    data["idDisease"] = generic_analysisResult.disease.id
    data["idAnalysis"] = generic_analysisResult.analysis.id
    data["score"] = generic_analysisResult.score
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/analysisResult/', data=str(
        json.dumps(data)), headers=headers)
    print("resp {}".format(resp))
    analysisResult = json.loads(resp.get_data(as_text=True))['response']
    analysisResult = namedtuple("AnalysisResult", analysisResult.keys())(*analysisResult.values())
    generic_analysisResult = analysisResult
    assert resp.status_code == 200
    assert "'id': 0" not in json.loads(
            resp.get_data(as_text=True))['response']

@pytest.mark.order3
def test_search_by_id():
    data = {
            "action": "searchByID",
            "id": 1,
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
            "idAnalysis": 1,
            "idDisease": 1,
            "score": 0.00,
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
        assert response['disease']['id'] == 1


@pytest.mark.order5
def test_update(generic_analysisResult=generic_analysisResult, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysisResult.__dict__
    data['action'] = 'searchByID'
    resp = client().get(
            '/api/gyresources/analysisResult',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    response = json.loads(resp.get_data(as_text=True))
    analysisResult = namedtuple("AnalysisResult", response.keys())(*response.values())
    analysisResult = {
                "id": analysisResult.response['id'],
                "idAnalysis": analysisResult.response['analysis']['id'],
                "idDisease": analysisResult.response['disease']['id'],
                "score": 0.9999
                }
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
    assert 0.9999 == analysisResult.response['score']


@pytest.mark.order6
def test_update_wrong_id(generic_analysisResult=generic_analysisResult, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysisResult.__dict__
    data['action'] = 'searchByID'
    resp = client().get(
            '/api/gyresources/analysisResult',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    response = json.loads(resp.get_data(as_text=True))
    analysisResult = namedtuple("AnalysisResult", response.keys())(*response.values())
    analysisResult = {
                "id": 1000,
                "idAnalysis": analysisResult.response['analysis']['id'],
                "idDisease": analysisResult.response['disease']['id'],
                "score": 0.9999
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
    data['action'] = 'searchByID'
    resp = client().get(
            '/api/gyresources/analysisResult',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    response = json.loads(resp.get_data(as_text=True))
    analysisResult = namedtuple("AnalysisResult", response.keys())(*response.values())
    analysisResult = {
                "id": 1000,
                "idAnalysis": analysisResult.response['analysis']['id'],
                "idDisease": analysisResult.response['disease']['id'],
                "score": 0.9999
                }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().delete('/api/gyresources/analysisResult/', data=str(json.dumps(analysisResult)), headers=headers)
    resp = json.loads(resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']

@pytest.mark.order8
def test_delete(generic_analysisResult=generic_analysisResult, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_analysisResult.__dict__
    data['action'] = 'searchByID'
    resp = client().get(
            '/api/gyresources/analysisResult',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)

    response = json.loads(resp.get_data(as_text=True))
    analysisResult = namedtuple("AnalysisResult", response.keys())(*response.values())
    analysisResult = {
                "id": analysisResult.response['id'],
                "idAnalysis": analysisResult.response['analysis']['id'],
                "idDisease": analysisResult.response['disease']['id'],
                "score": analysisResult.response['score']
                }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().delete('/api/gyresources/analysisResult/', data=str(
        json.dumps(analysisResult)), headers=headers)
    assert resp.status_code == 200
    assert 204 == json.loads(resp.get_data(as_text=True))['status_code']


@pytest.mark.order9
def test_create_empty(generic_analysisResult=generic_analysisResult, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = {}
    data["id"] = 0
    data["idAnalysis"] = 0
    data["idDisease"] = 0
    data["score"] = 0.000
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/analysisResult/', data=str(
        json.dumps(data)), headers=headers)
    resp = json.loads(resp.get_data(as_text=True))
    assert resp['status_code'] == 500
