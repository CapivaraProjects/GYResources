import json
import pytest
import base64
import models.Classifier
import models.Plant
from flask import Flask
from app import initialize_app
from collections import namedtuple
from tools.Cryptography import Crypto


app = Flask(__name__)
app = initialize_app(app)
client = app.test_client
generic_classifier = models.Classifier.Classifier(
        plant=models.Plant.Plant(id=1),
        tag="test1",
        path="test1")

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


generic_user = models.User.User(
    id=generic_user.id,
    idType=generic_user.idType,
    email=generic_user.email,
    username=generic_user.username,
    password='test',
    salt=generic_user.salt,
    dateInsertion=generic_user.dateInsertion,
    dateUpdate=generic_user.dateUpdate)


@pytest.mark.order1
def test_search_by_unexistent_id():
    data = {
            "action": "searchByID",
            "id": "1000",
            }
    resp = client().get(
            '/api/gyresources/classifiers',
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
            '/api/gyresources/classifiers',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json',
                'timeout': 240},
            query_string=data, follow_redirects=True)
    assert json.loads(resp.get_data(as_text=True))['status_code'] == 200


@pytest.mark.order3
def test_search():
    data = {
                "action": "search",
                "idPlant": 24,
                "tag": "1",
                "path": "gykernel/savedmodels",
                "pageSize": 10,
                "offset": 0
            }
    resp = client().get(
            '/api/gyresources/classifiers',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    assert pagedResponse['status_code'] == 200
    for response in pagedResponse['response']:
        assert 'gykernel' in response['path']



@pytest.mark.order4
def test_create(generic_classifier=generic_classifier, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    aux = generic_classifier.plant
    generic_classifier.plant = generic_classifier.plant.__dict__
    data = generic_classifier.__dict__
    data["idPlant"] = aux.id
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/classifiers/', data=str(
        json.dumps(data)), headers=headers)
    classifier = json.loads(resp.get_data(as_text=True))['response']
    classifier = namedtuple("Classifier", classifier.keys())(*classifier.values())
    generic_classifier = classifier
    assert resp.status_code == 200


@pytest.mark.order5
def test_update(generic_classifier=generic_classifier, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_classifier.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/classifiers',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    classifier = object()
    for response in pagedResponse['response']:
        classifier = namedtuple("Classifier", response.keys())(*response.values())

    classifier = {
                "id": classifier.id,
                "idPlant": classifier.plant["id"],
                "tag": "2",
                "path": classifier.path,
            }
    generic_classifier.tag = '2'
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().put('/api/gyresources/classifiers/', data=str(
        json.dumps(classifier)), headers=headers)
    assert resp.status_code == 200
    classifier = json.loads(
                resp.get_data(as_text=True))
    classifier = namedtuple("Classifier", classifier .keys())(*classifier .values())
    assert "2" in classifier.response['tag']


@pytest.mark.order6
def test_delete(generic_classifier=generic_classifier, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_classifier.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/classifiers',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    classifier = object()
    for response in pagedResponse['response']:
        classifier = namedtuple("Classifier", response.keys())(*response.values())

    classifier = {
                "id": classifier.id,
                "idPlant": classifier.plant["id"],
                "tag": classifier.tag,
                "path": classifier.path
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().delete('/api/gyresources/classifiers/', data=str(
        json.dumps(classifier)), headers=headers)
    assert resp.status_code == 200
    assert 204 == json.loads(
            resp.get_data(as_text=True))['status_code']



@pytest.mark.order7
def test_create_empty(generic_classifier=generic_classifier, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    classifier = generic_classifier
    classifier.tag = ''
    classifier.path = ''
    data = classifier.__dict__
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().post('/api/gyresources/classifiers/', data=str(
        json.dumps(data)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500


@pytest.mark.order9
def test_update_wrong_id(generic_classifier=generic_classifier, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_classifier.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/classifiers',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    classifier = object()
    for response in pagedResponse['response']:
        classifier = namedtuple("Disease", response.keys())(*response.values())

        classifier = {

                "id": 1000,
                "idPlant": classifier.plant["id"],
                "tag": '2',
                "path": classifier.path
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().put('/api/gyresources/classifiers/', data=str(
        json.dumps(classifier)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']


@pytest.mark.order10
def test_delete_non_existent(generic_classifier=generic_classifier, generic_user=generic_user):
    (generic_user, token) = auth(generic_user)
    data = generic_classifier.__dict__
    data['action'] = 'search'
    resp = client().get(
            '/api/gyresources/classifiers',
            content_type='application/json',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'dataType': 'json'},
            query_string=data, follow_redirects=True)
    pagedResponse = json.loads(resp.get_data(as_text=True))
    classifier = object()
    for response in pagedResponse['response']:
        classifier = namedtuple("Disease", response.keys())(*response.values())

        classifier = {
                "id": 1000,
                "idPlant": classifier.plant["id"],
                "tag": classifier.tag,
                "path": classifier.path
            }
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token['token']
            }
    resp = client().delete('/api/gyresources/classifiers/', data=str(
        json.dumps(classifier)), headers=headers)
    resp = json.loads(
                resp.get_data(as_text=True))
    assert resp['status_code'] == 500
    assert 'Internal server error' in resp['message']
